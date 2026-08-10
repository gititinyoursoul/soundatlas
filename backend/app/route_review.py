import hashlib
import json
import os
import re
from pathlib import Path
from typing import Any, Literal

from pydantic import BaseModel, Field, ValidationError

from app.config import DEFAULT_CONTENT_ROOT, DEFAULT_SEED_DIR
from app.schemas import Connection, Event, Place

ROUTE_REVIEW_FILENAME = "route-review.json"
EVENT_LIST_FILENAME = "event-list.json"
COMPLETE_DRAFT_FILENAME = "complete-draft.json"

EditorialState = Literal["draft", "approved", "dont_use"]
RouteEntryRole = Literal["active", "context", "exclude"]
CompositionOutcome = Literal["active", "omitted", "merged_into", "split_into", "added"]
FindingOwner = Literal[
    "candidate_composition",
    "active_event",
    "active_route",
    "source_media",
    "technical",
]

LEGACY_STATE_MAP: dict[str, EditorialState] = {
    "pending": "draft",
    "approved": "approved",
    "rejected": "dont_use",
}
LEGACY_RECOMMENDATION_MAP = {
    "keep": "include",
    "maybe": "context",
    "merge": "merge",
    "reject": "exclude",
}

MATERIAL_FIELDS = (
    "working_title",
    "title",
    "years",
    "year_start",
    "year_end",
    "place",
    "route_function",
    "summary",
    "significance",
    "claims",
)

RENDER_FIELDS = {
    "working_title": "working title",
    "years": "time range",
    "place": "place",
    "route_function": "route function",
}

MISSING_SOURCE_URL_ERROR = "Reader-facing event has no source URL."


def _canonical_recommendation(candidate: dict[str, Any]) -> str | None:
    recommendation = candidate.get("agent_recommendation")
    if isinstance(recommendation, str):
        return LEGACY_RECOMMENDATION_MAP.get(recommendation, recommendation)
    status = candidate.get("status")
    return LEGACY_RECOMMENDATION_MAP.get(status) if isinstance(status, str) else None


def _route_entry_role(candidate: dict[str, Any]) -> RouteEntryRole:
    explicit = candidate.get("route_entry_role") or candidate.get("editorial_role")
    if explicit in {"active", "context", "exclude"}:
        return explicit
    recommendation = _canonical_recommendation(candidate)
    if recommendation == "context":
        return "context"
    if recommendation == "exclude":
        return "exclude"
    return "active"


class RouteReviewProposal(BaseModel):
    candidate_id: str
    editorial_state: EditorialState
    active: bool = True
    included: bool = True
    renderable: bool = True
    agent_recommendation: str | None = None
    route_entry_role: RouteEntryRole = "active"
    next_evidence_task: dict[str, Any] | None = None
    warnings: list[str] = Field(default_factory=list)
    technical_errors: list[str] = Field(default_factory=list)
    material_signature: str
    proposal: dict[str, Any]
    event: Event | None = None


class RouteReviewFinding(BaseModel):
    owner: FindingOwner
    message: str
    candidate_id: str | None = None
    blocking: bool = False


class RouteReviewCandidateAccount(BaseModel):
    candidate_id: str
    outcome: CompositionOutcome
    reason: str
    related_candidate_ids: list[str] = Field(default_factory=list)
    active: bool
    preview: dict[str, Any] = Field(default_factory=dict)
    context: dict[str, Any] = Field(default_factory=dict)
    findings: list[RouteReviewFinding] = Field(default_factory=list)


class RouteReviewPlace(BaseModel):
    decision: Literal["reuse", "new"]
    place: Place


class RouteEditorialReview(BaseModel):
    route_id: str
    revision_id: str
    source: str = EVENT_LIST_FILENAME
    proposals: list[RouteReviewProposal]
    dormant_proposals: list[RouteReviewProposal] = Field(default_factory=list)
    places: list[RouteReviewPlace] = Field(default_factory=list)
    connections: list[Connection] = Field(default_factory=list)
    candidate_accounts: list[RouteReviewCandidateAccount] = Field(default_factory=list)
    phase_coverage: list[dict[str, Any]] = Field(default_factory=list)
    findings: list[RouteReviewFinding] = Field(default_factory=list)
    warnings: list[str] = Field(default_factory=list)
    technical_errors: list[str] = Field(default_factory=list)
    technical_ready: bool


class RouteReviewResult(RouteEditorialReview):
    """Compatibility response model retaining the established OpenAPI schema name."""


class RouteReviewStateUpdate(BaseModel):
    revision_id: str
    editorial_state: EditorialState


class RouteReviewError(ValueError):
    pass


class RouteReviewNotFoundError(RouteReviewError):
    pass


class RouteReviewConflictError(RouteReviewError):
    pass


class RouteReviewValidationError(RouteReviewError):
    pass


class RouteReviewMigrationReport(BaseModel):
    route_id: str
    revision_id: str
    migrated: dict[str, int]
    proposals: int


class RouteReviewRepository:
    def __init__(
        self,
        content_root: Path = DEFAULT_CONTENT_ROOT,
        seed_dir: Path = DEFAULT_SEED_DIR,
    ) -> None:
        self._content_root = content_root
        self._seed_dir = seed_dir

    def get(self, route_id: str) -> RouteEditorialReview:
        path = self._review_path(route_id)
        if not path.exists():
            raise RouteReviewNotFoundError(f"Route review '{route_id}' not found")
        try:
            result = RouteEditorialReview.model_validate_json(path.read_text(encoding="utf-8"))
        except (OSError, ValueError) as exc:
            raise RouteReviewError(f"Route review '{route_id}' is invalid") from exc
        complete_draft = self._optional_complete_draft(route_id)
        if complete_draft is not None and (
            result.source != COMPLETE_DRAFT_FILENAME
            or any(proposal.event is None for proposal in result.proposals)
            or not result.candidate_accounts
            or any(not account.context for account in result.candidate_accounts)
        ):
            return self._build_current(route_id, result, complete_draft)
        if any(not account.context for account in result.candidate_accounts):
            return self._build_current(route_id, result)
        return result

    def refresh(self, route_id: str) -> RouteEditorialReview:
        previous = self._optional_review(route_id)
        result = self._build_current(route_id, previous)
        self._write(result)
        return result

    def build_from_complete_draft(
        self,
        route_id: str,
        complete_draft: dict[str, Any],
    ) -> RouteEditorialReview:
        """Build, but do not write, the review bound to an exact complete draft."""
        return self._build_current(
            route_id,
            self._optional_review(route_id),
            complete_draft=complete_draft,
        )

    def migrate_legacy(self, route_id: str) -> RouteReviewMigrationReport:
        if self._review_path(route_id).exists():
            raise RouteReviewConflictError(
                f"Route review '{route_id}' already exists; legacy migration is one-time"
            )
        event_list = self._read_event_list(route_id)
        legacy_states: dict[str, EditorialState] = {}
        counts = {state: 0 for state in LEGACY_STATE_MAP}
        for candidate in _candidate_objects(event_list):
            candidate_id = _candidate_id(candidate)
            legacy_state = candidate.get("review_state")
            if legacy_state is None:
                canonical_state = candidate.get("editorial_state")
                if isinstance(canonical_state, str):
                    legacy_state = {
                        "draft": "pending",
                        "approved": "approved",
                        "dont_use": "rejected",
                    }.get(canonical_state)
            if not isinstance(legacy_state, str) or legacy_state not in LEGACY_STATE_MAP:
                raise RouteReviewError(
                    f"Candidate '{candidate_id}' has unsupported legacy review_state "
                    f"'{legacy_state}'"
                )
            legacy_states[candidate_id] = LEGACY_STATE_MAP[legacy_state]
            counts[legacy_state] += 1

        result = self._build_current(
            route_id,
            None,
            initial_states=legacy_states,
        )
        self._write(result)
        return RouteReviewMigrationReport(
            route_id=route_id,
            revision_id=result.revision_id,
            migrated=counts,
            proposals=len(result.proposals),
        )

    def update_state(
        self,
        route_id: str,
        candidate_id: str,
        update: RouteReviewStateUpdate,
    ) -> RouteEditorialReview:
        result = self.get(route_id)
        if result.revision_id != update.revision_id:
            raise RouteReviewConflictError(
                f"Route review '{route_id}' changed; reload before saving"
            )
        proposal = next(
            (item for item in result.proposals if item.candidate_id == candidate_id),
            None,
        )
        if proposal is None:
            raise RouteReviewNotFoundError(
                f"Proposal '{candidate_id}' not found in route review '{route_id}'"
            )
        proposal.editorial_state = update.editorial_state
        proposal.included = update.editorial_state != "dont_use"
        result.technical_ready = _technical_ready(
            result.proposals,
            result.technical_errors,
        )
        result.revision_id = _revision_id(result)
        self._write(result)
        return result

    def _read_event_list(self, route_id: str) -> dict[str, Any]:
        path = self._route_dir(route_id) / EVENT_LIST_FILENAME
        try:
            payload = json.loads(path.read_text(encoding="utf-8"))
        except FileNotFoundError as exc:
            raise RouteReviewNotFoundError(
                f"Generated event list for route '{route_id}' not found"
            ) from exc
        except json.JSONDecodeError as exc:
            raise RouteReviewError(
                f"Generated event list for route '{route_id}' is not valid JSON"
            ) from exc
        if not isinstance(payload, dict):
            raise RouteReviewError("Generated event list must be a JSON object")
        meta = payload.get("_meta")
        source_route_id = meta.get("route_id") if isinstance(meta, dict) else None
        if source_route_id is not None and source_route_id != route_id:
            raise RouteReviewError(
                f"Generated event list route '{source_route_id}' does not match '{route_id}'"
            )
        _candidate_objects(payload)
        return payload

    def _optional_complete_draft(self, route_id: str) -> dict[str, Any] | None:
        path = self._route_dir(route_id) / COMPLETE_DRAFT_FILENAME
        if not path.exists():
            return None
        try:
            payload = json.loads(path.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError) as exc:
            raise RouteReviewError(
                f"Complete draft for route '{route_id}' is not valid JSON"
            ) from exc
        if not isinstance(payload, dict):
            raise RouteReviewError("Complete draft must be a JSON object")
        meta = payload.get("_meta")
        source_route_id = meta.get("route_id") if isinstance(meta, dict) else None
        if source_route_id != route_id:
            raise RouteReviewError(
                f"Complete draft route '{source_route_id}' does not match '{route_id}'"
            )
        _candidate_objects(payload)
        return payload

    def _build_current(
        self,
        route_id: str,
        previous: RouteEditorialReview | None,
        complete_draft: dict[str, Any] | None = None,
        initial_states: dict[str, EditorialState] | None = None,
    ) -> RouteEditorialReview:
        complete_draft = complete_draft or self._optional_complete_draft(route_id)
        source = complete_draft or self._read_event_list(route_id)
        return build_route_review(
            route_id=route_id,
            event_list=source,
            previous=previous,
            initial_states=initial_states,
            complete_draft=complete_draft,
            seed_places=self._read_seed_places(),
        )

    def _read_seed_places(self) -> dict[str, dict[str, Any]]:
        path = self._seed_dir / "places.json"
        if not path.exists():
            return {}
        try:
            payload = json.loads(path.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError) as exc:
            raise RouteReviewError("Seed places are not valid JSON") from exc
        places = payload.get("places") if isinstance(payload, dict) else None
        if not isinstance(places, list):
            raise RouteReviewError("Seed places must contain a places list")
        return {
            item["id"]: item
            for item in places
            if isinstance(item, dict) and isinstance(item.get("id"), str)
        }

    def _optional_review(self, route_id: str) -> RouteEditorialReview | None:
        try:
            return self.get(route_id)
        except RouteReviewNotFoundError:
            return None

    def _write(self, result: RouteEditorialReview) -> None:
        path = self._review_path(result.route_id)
        path.parent.mkdir(parents=True, exist_ok=True)
        temporary_path = path.with_name(f".{path.name}.tmp")
        temporary_path.write_text(
            json.dumps(result.model_dump(), indent=2, ensure_ascii=False) + "\n",
            encoding="utf-8",
        )
        os.replace(temporary_path, path)

    def _route_dir(self, route_id: str) -> Path:
        if not re.fullmatch(r"[a-z0-9][a-z0-9-]*", route_id):
            raise RouteReviewValidationError(
                "Route IDs must use lowercase letters, numbers, and hyphens"
            )
        return self._content_root / route_id

    def _review_path(self, route_id: str) -> Path:
        return self._route_dir(route_id) / ROUTE_REVIEW_FILENAME


def build_route_review(
    *,
    route_id: str,
    event_list: dict[str, Any],
    previous: RouteEditorialReview | None,
    initial_states: dict[str, EditorialState] | None = None,
    complete_draft: dict[str, Any] | None = None,
    seed_places: dict[str, dict[str, Any]] | None = None,
) -> RouteEditorialReview:
    candidates = _candidate_objects(event_list)
    candidate_accounts = _candidate_accounts(candidates)
    active_accounts = [account for account in candidate_accounts if account.active]
    active_candidate_ids = {account.candidate_id for account in active_accounts}
    candidates_by_id = {_candidate_id(candidate): candidate for candidate in candidates}
    event_payloads, event_collection_errors = _objects_by_id(
        complete_draft,
        "events",
    )
    places, place_errors = _review_places(
        complete_draft,
        seed_places or {},
        event_payloads,
    )
    resolved_place_ids = {item.place.id for item in places}
    connections, connection_errors = _review_connections(
        complete_draft,
        active_candidate_ids,
    )
    unexpected_event_ids = sorted(set(event_payloads) - active_candidate_ids)
    route_errors = [
        *event_collection_errors,
        *(
            f"Reader-facing event '{event_id}' has no active proposal."
            for event_id in unexpected_event_ids
        ),
        *place_errors,
        *connection_errors,
    ]
    initial_states = initial_states or {}
    previous_proposals = previous.proposals if previous else []
    previous_dormant = previous.dormant_proposals if previous else []
    prior_by_id = {
        item.candidate_id: item for item in [*previous_proposals, *previous_dormant]
    }
    seen: set[str] = set()
    proposals: list[RouteReviewProposal] = []

    findings = _review_findings(event_list, candidate_accounts)
    route_errors.extend(
        finding.message
        for finding in findings
        if finding.owner == "technical" and finding.blocking
    )
    for account in active_accounts:
        candidate = candidates_by_id[account.candidate_id]
        candidate_id = _candidate_id(candidate)
        if candidate_id in seen:
            raise RouteReviewError(f"Duplicate candidate_id '{candidate_id}'")
        seen.add(candidate_id)
        event, event_errors = _review_event(
            event_payloads.get(candidate_id),
            route_id,
            candidate_id,
            resolved_place_ids,
        )
        errors = [*proposal_errors(candidate), *event_errors]
        renderability_errors = [
            error for error in errors if error != MISSING_SOURCE_URL_ERROR
        ]
        signature = material_signature(candidate, event)
        prior = prior_by_id.get(candidate_id)
        state = initial_states.get(candidate_id, "draft")
        if prior is not None:
            state = _carry_state(prior, signature)
        proposals.append(
            RouteReviewProposal(
                candidate_id=candidate_id,
                editorial_state=state,
                included=state != "dont_use",
                renderable=not renderability_errors,
                agent_recommendation=_canonical_recommendation(candidate),
                route_entry_role=_route_entry_role(candidate),
                next_evidence_task=(
                    candidate.get("next_evidence_task")
                    if isinstance(candidate.get("next_evidence_task"), dict)
                    else None
                ),
                warnings=_unique_strings(
                    candidate.get("risk_notes"),
                    candidate.get("warnings"),
                ),
                technical_errors=errors,
                material_signature=signature,
                proposal=candidate,
                event=event,
            )
        )
        findings.extend(
            RouteReviewFinding(
                owner=(
                    "source_media"
                    if "source URL" in error
                    else "technical"
                ),
                message=error,
                candidate_id=candidate_id,
                blocking=True,
            )
            for error in errors
        )

    dormant = []
    for candidate_id, prior in prior_by_id.items():
        if candidate_id in seen:
            continue
        dormant.append(prior.model_copy(update={"active": False, "included": False}))

    result = RouteEditorialReview(
        route_id=route_id,
        revision_id="",
        source=(
            COMPLETE_DRAFT_FILENAME
            if complete_draft is not None
            else EVENT_LIST_FILENAME
        ),
        proposals=proposals,
        dormant_proposals=sorted(dormant, key=lambda item: item.candidate_id),
        places=places,
        connections=connections,
        candidate_accounts=candidate_accounts,
        phase_coverage=_phase_coverage(event_list),
        findings=_unique_findings(findings),
        warnings=[
            finding.message
            for finding in _unique_findings(findings)
            if finding.owner == "active_route"
        ],
        technical_errors=route_errors,
        technical_ready=_technical_ready(proposals, route_errors),
    )
    result.revision_id = _revision_id(result)
    return result


def material_signature(candidate: dict[str, Any], event: Event | None = None) -> str:
    material = {field: candidate.get(field) for field in MATERIAL_FIELDS if field in candidate}
    material["event"] = event.model_dump(mode="json") if event is not None else None
    return hashlib.sha256(_canonical_json(material).encode("utf-8")).hexdigest()


def proposal_errors(candidate: dict[str, Any]) -> list[str]:
    errors = []
    for field, label in RENDER_FIELDS.items():
        value = candidate.get(field)
        if not isinstance(value, str) or not value.strip():
            errors.append(f"Missing {label} ('{field}')")
    if _route_entry_role(candidate) == "context":
        task = candidate.get("next_evidence_task")
        required = ("missing_evidence", "target_claim", "target_place", "expected_output")
        if not isinstance(task, dict) or any(
            not isinstance(task.get(field), str) or not task[field].strip()
            for field in required
        ):
            errors.append(
                "Context route entries require next_evidence_task with "
                "missing_evidence, target_claim, target_place, and expected_output."
            )
    return errors


def _objects_by_id(
    payload: dict[str, Any] | None,
    field: str,
) -> tuple[dict[str, dict[str, Any]], list[str]]:
    if payload is None:
        return {}, []
    values = payload.get(field)
    if not isinstance(values, list):
        return {}, [f"Complete draft `{field}` must be a list."]
    objects: dict[str, dict[str, Any]] = {}
    errors: list[str] = []
    for index, value in enumerate(values):
        if not isinstance(value, dict):
            errors.append(f"Complete draft `{field}[{index}]` must be an object.")
            continue
        value_id = value.get("id")
        if not isinstance(value_id, str) or not value_id:
            errors.append(f"Complete draft `{field}[{index}]` is missing `id`.")
            continue
        if value_id in objects:
            errors.append(f"Complete draft `{field}` contains duplicate ID '{value_id}'.")
            continue
        objects[value_id] = value
    return objects, errors


def _review_event(
    payload: dict[str, Any] | None,
    route_id: str,
    candidate_id: str,
    resolved_place_ids: set[str],
) -> tuple[Event | None, list[str]]:
    if payload is None:
        return None, ["Missing reader-facing event content in `complete-draft.json`."]
    try:
        event = Event.model_validate(payload)
    except ValidationError as exc:
        return None, _validation_messages("Reader-facing event", exc)

    errors: list[str] = []
    if event.id != candidate_id:
        errors.append(
            f"Reader-facing event ID '{event.id}' does not match proposal '{candidate_id}'."
        )
    if event.route_id != route_id:
        errors.append(
            f"Reader-facing event route '{event.route_id}' does not match '{route_id}'."
        )
    for field, label in (
        ("title", "title"),
        ("summary", "What happened"),
        ("significance", "Why it matters"),
    ):
        value = getattr(event, field)
        if not value.strip():
            errors.append(f"Reader-facing event is missing {label} ('{field}').")
    if not event.source_urls:
        errors.append(MISSING_SOURCE_URL_ERROR)
    for place_id in event.place_ids:
        if place_id not in resolved_place_ids:
            errors.append(
                f"Reader-facing event references unresolved place '{place_id}'."
            )
    return event, errors


def _review_places(
    complete_draft: dict[str, Any] | None,
    seed_places: dict[str, dict[str, Any]],
    event_payloads: dict[str, dict[str, Any]],
) -> tuple[list[RouteReviewPlace], list[str]]:
    if complete_draft is None:
        return [], []
    place_values = complete_draft.get("places")
    if not isinstance(place_values, list):
        return [], ["Complete draft `places` must be a list."]

    decisions: dict[str, dict[str, Any]] = {}
    errors: list[str] = []
    for index, value in enumerate(place_values):
        if not isinstance(value, dict):
            errors.append(f"Complete draft `places[{index}]` must be an object.")
            continue
        place_id = value.get("place_id")
        if not isinstance(place_id, str) or not place_id:
            errors.append(f"Complete draft `places[{index}]` is missing `place_id`.")
            continue
        if place_id in decisions:
            errors.append(f"Complete draft places contain duplicate ID '{place_id}'.")
            continue
        decisions[place_id] = value

    referenced_place_ids: set[str] = set()
    for event in event_payloads.values():
        place_ids = event.get("place_ids")
        if isinstance(place_ids, list):
            referenced_place_ids.update(
                item for item in place_ids if isinstance(item, str) and item
            )
        elif isinstance(event.get("place_id"), str):
            referenced_place_ids.add(event["place_id"])

    places: list[RouteReviewPlace] = []
    for place_id in sorted(referenced_place_ids):
        decision = decisions.get(place_id)
        if decision is None:
            errors.append(f"Complete draft has no place decision for '{place_id}'.")
            continue
        decision_name = decision.get("decision")
        if decision_name == "reuse":
            raw_place = seed_places.get(place_id)
            if raw_place is None:
                errors.append(f"Reused place '{place_id}' is missing from canonical seeds.")
                continue
        elif decision_name == "new":
            raw_place = decision.get("place")
            if not isinstance(raw_place, dict):
                errors.append(f"New place '{place_id}' is missing its place record.")
                continue
        else:
            errors.append(
                f"Place '{place_id}' has unsupported decision '{decision_name}'."
            )
            continue
        try:
            place = Place.model_validate(raw_place)
        except ValidationError as exc:
            errors.extend(_validation_messages(f"Place '{place_id}'", exc))
            continue
        if place.id != place_id:
            errors.append(
                f"Place decision '{place_id}' resolves to mismatched place '{place.id}'."
            )
            continue
        places.append(RouteReviewPlace(decision=decision_name, place=place))
    return places, errors


def _review_connections(
    complete_draft: dict[str, Any] | None,
    active_candidate_ids: set[str],
) -> tuple[list[Connection], list[str]]:
    if complete_draft is None:
        return [], []
    values = complete_draft.get("connections")
    if values is None:
        return [], []
    if not isinstance(values, list):
        return [], ["Complete draft `connections` must be a list."]
    connections: list[Connection] = []
    errors: list[str] = []
    seen: set[str] = set()
    for index, value in enumerate(values):
        try:
            connection = Connection.model_validate(value)
        except ValidationError as exc:
            errors.extend(
                _validation_messages(f"Connection at index {index}", exc)
            )
            continue
        if connection.id in seen:
            errors.append(f"Complete draft contains duplicate connection '{connection.id}'.")
            continue
        seen.add(connection.id)
        missing_endpoints = {
            connection.from_event_id,
            connection.to_event_id,
        } - active_candidate_ids
        if missing_endpoints:
            errors.append(
                f"Connection '{connection.id}' references inactive or missing events: "
                + ", ".join(sorted(missing_endpoints))
                + "."
            )
            continue
        connections.append(connection)
    return connections, errors


def _validation_messages(label: str, error: ValidationError) -> list[str]:
    messages = []
    for item in error.errors(include_url=False):
        location = ".".join(str(part) for part in item["loc"])
        messages.append(f"{label} has invalid `{location}`: {item['msg']}.")
    return messages


def _candidate_objects(event_list: dict[str, Any]) -> list[dict[str, Any]]:
    candidates = event_list.get("candidates")
    if not isinstance(candidates, list):
        raise RouteReviewError("Generated event list must contain a candidates list")
    if any(not isinstance(candidate, dict) for candidate in candidates):
        raise RouteReviewError("Generated event list contains a non-object candidate")
    return candidates


def _candidate_accounts(
    candidates: list[dict[str, Any]],
) -> list[RouteReviewCandidateAccount]:
    accounts: list[RouteReviewCandidateAccount] = []
    for candidate in candidates:
        candidate_id = _candidate_id(candidate)
        composition = candidate.get("composition")
        if not isinstance(composition, dict):
            composition = {}
        outcome = composition.get("outcome", "active")
        if outcome not in {"active", "omitted", "merged_into", "split_into", "added"}:
            outcome = "omitted"
        reason = composition.get("reason")
        if not isinstance(reason, str) or not reason.strip():
            reason = _optional_string(candidate.get("decision_rationale")) or "Generated composition decision."
        related = composition.get("related_candidate_ids", [])
        if not isinstance(related, list):
            related = []
        preview = candidate.get("preview")
        if not isinstance(preview, dict):
            preview = {
                key: candidate[key]
                for key in (
                    "working_title",
                    "years",
                    "place",
                    "route_function",
                    "decision_rationale",
                    "review_question",
                    "source_leads",
                    "risk_notes",
                    "next_action",
                )
                if key in candidate
            }
        accounts.append(
            RouteReviewCandidateAccount(
                candidate_id=candidate_id,
                outcome=outcome,
                reason=reason,
                related_candidate_ids=[item for item in related if isinstance(item, str)],
                active=outcome in {"active", "added"},
                preview=preview,
                context={
                    key: value
                    for key, value in candidate.items()
                    if key not in {"composition", "preview", "editorial_state"}
                },
                findings=_candidate_findings(candidate, candidate_id, outcome),
            )
        )
    return accounts


def _candidate_findings(
    candidate: dict[str, Any],
    candidate_id: str,
    outcome: str,
) -> list[RouteReviewFinding]:
    raw_findings = candidate.get("findings")
    findings: list[RouteReviewFinding] = []
    if isinstance(raw_findings, list):
        for raw in raw_findings:
            try:
                findings.append(RouteReviewFinding.model_validate(raw))
            except ValidationError:
                continue
    if findings:
        return findings
    owner: FindingOwner = "active_event" if outcome in {"active", "added"} else "candidate_composition"
    return [
        RouteReviewFinding(owner=owner, message=message, candidate_id=candidate_id)
        for message in _unique_strings(candidate.get("risk_notes"), candidate.get("warnings"))
    ]


def _review_findings(
    event_list: dict[str, Any],
    accounts: list[RouteReviewCandidateAccount],
) -> list[RouteReviewFinding]:
    values: list[RouteReviewFinding] = [
        finding
        for account in accounts
        for finding in account.findings
    ]
    raw_findings = event_list.get("findings")
    if isinstance(raw_findings, list):
        for raw in raw_findings:
            try:
                values.append(RouteReviewFinding.model_validate(raw))
            except ValidationError:
                continue
    if not any(finding.owner == "active_route" for finding in values):
        values.extend(
            RouteReviewFinding(owner="active_route", message=message)
            for message in _route_warnings(event_list)
        )
    return values


def _phase_coverage(event_list: dict[str, Any]) -> list[dict[str, Any]]:
    values = event_list.get("phase_coverage")
    return [item for item in values if isinstance(item, dict)] if isinstance(values, list) else []


def _unique_findings(values: list[RouteReviewFinding]) -> list[RouteReviewFinding]:
    unique: dict[tuple[str, str | None, bool, str], RouteReviewFinding] = {}
    for value in values:
        key = (value.owner, value.candidate_id, value.blocking, value.message)
        unique.setdefault(key, value)
    return list(unique.values())


def _candidate_id(candidate: dict[str, Any]) -> str:
    candidate_id = candidate.get("candidate_id")
    if not isinstance(candidate_id, str) or not candidate_id.strip():
        raise RouteReviewError("Generated proposal is missing an identifiable candidate_id")
    return candidate_id


def _carry_state(prior: RouteReviewProposal, signature: str) -> EditorialState:
    if prior.editorial_state == "dont_use":
        return "dont_use"
    if prior.editorial_state == "approved" and prior.material_signature != signature:
        return "draft"
    return prior.editorial_state


def _technical_ready(
    proposals: list[RouteReviewProposal],
    route_errors: list[str],
) -> bool:
    return not route_errors and all(
        not proposal.included
        or (proposal.renderable and not proposal.technical_errors)
        for proposal in proposals
    )


def _revision_id(result: RouteEditorialReview) -> str:
    payload = result.model_dump(exclude={"revision_id"})
    return hashlib.sha256(_canonical_json(payload).encode("utf-8")).hexdigest()


def _canonical_json(payload: Any) -> str:
    return json.dumps(payload, sort_keys=True, separators=(",", ":"), ensure_ascii=False)


def _optional_string(value: Any) -> str | None:
    return value if isinstance(value, str) else None


def _string_list(value: Any) -> list[str]:
    if isinstance(value, list):
        return [str(item) for item in value if str(item).strip()]
    if isinstance(value, str) and value.strip():
        return [value]
    return []


def _unique_strings(*values: Any) -> list[str]:
    return list(dict.fromkeys(item for value in values for item in _string_list(value)))


def _route_warnings(event_list: dict[str, Any]) -> list[str]:
    meta = event_list.get("_meta")
    meta_warnings = meta.get("warnings") if isinstance(meta, dict) else None
    return _unique_strings(event_list.get("warnings"), meta_warnings)
