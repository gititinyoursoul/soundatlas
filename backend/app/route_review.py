import hashlib
import json
import os
import re
from pathlib import Path
from typing import Any, Literal

from pydantic import BaseModel, Field

from app.config import DEFAULT_CONTENT_ROOT

ROUTE_REVIEW_FILENAME = "route-review.json"
EVENT_LIST_FILENAME = "event-list.json"

EditorialState = Literal["draft", "approved", "dont_use"]

LEGACY_STATE_MAP: dict[str, EditorialState] = {
    "pending": "draft",
    "approved": "approved",
    "rejected": "dont_use",
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


class RouteReviewProposal(BaseModel):
    candidate_id: str
    editorial_state: EditorialState
    active: bool = True
    included: bool = True
    renderable: bool = True
    agent_recommendation: str | None = None
    warnings: list[str] = Field(default_factory=list)
    technical_errors: list[str] = Field(default_factory=list)
    material_signature: str
    proposal: dict[str, Any]


class RouteReviewResult(BaseModel):
    route_id: str
    revision_id: str
    source: str = EVENT_LIST_FILENAME
    proposals: list[RouteReviewProposal]
    dormant_proposals: list[RouteReviewProposal] = Field(default_factory=list)
    warnings: list[str] = Field(default_factory=list)
    technical_ready: bool


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
    def __init__(self, content_root: Path = DEFAULT_CONTENT_ROOT) -> None:
        self._content_root = content_root

    def get(self, route_id: str) -> RouteReviewResult:
        path = self._review_path(route_id)
        if not path.exists():
            raise RouteReviewNotFoundError(f"Route review '{route_id}' not found")
        try:
            return RouteReviewResult.model_validate_json(path.read_text(encoding="utf-8"))
        except (OSError, ValueError) as exc:
            raise RouteReviewError(f"Route review '{route_id}' is invalid") from exc

    def refresh(self, route_id: str) -> RouteReviewResult:
        event_list = self._read_event_list(route_id)
        previous = self._optional_review(route_id)
        result = build_route_review(route_id=route_id, event_list=event_list, previous=previous)
        self._write(result)
        return result

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
            if not isinstance(legacy_state, str) or legacy_state not in LEGACY_STATE_MAP:
                raise RouteReviewError(
                    f"Candidate '{candidate_id}' has unsupported legacy review_state "
                    f"'{legacy_state}'"
                )
            legacy_states[candidate_id] = LEGACY_STATE_MAP[legacy_state]
            counts[legacy_state] += 1

        result = build_route_review(
            route_id=route_id,
            event_list=event_list,
            previous=None,
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
    ) -> RouteReviewResult:
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
        result.technical_ready = _technical_ready(result.proposals)
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

    def _optional_review(self, route_id: str) -> RouteReviewResult | None:
        try:
            return self.get(route_id)
        except RouteReviewNotFoundError:
            return None

    def _write(self, result: RouteReviewResult) -> None:
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
    previous: RouteReviewResult | None,
    initial_states: dict[str, EditorialState] | None = None,
) -> RouteReviewResult:
    candidates = _candidate_objects(event_list)
    initial_states = initial_states or {}
    previous_proposals = previous.proposals if previous else []
    previous_dormant = previous.dormant_proposals if previous else []
    prior_by_id = {
        item.candidate_id: item for item in [*previous_proposals, *previous_dormant]
    }
    seen: set[str] = set()
    proposals: list[RouteReviewProposal] = []

    for candidate in candidates:
        candidate_id = _candidate_id(candidate)
        if candidate_id in seen:
            raise RouteReviewError(f"Duplicate candidate_id '{candidate_id}'")
        seen.add(candidate_id)
        signature = material_signature(candidate)
        prior = prior_by_id.get(candidate_id)
        state = initial_states.get(candidate_id, "draft")
        if prior is not None:
            state = _carry_state(prior, signature)
        errors = proposal_errors(candidate)
        proposals.append(
            RouteReviewProposal(
                candidate_id=candidate_id,
                editorial_state=state,
                included=state != "dont_use",
                renderable=not errors,
                agent_recommendation=_optional_string(candidate.get("status")),
                warnings=_unique_strings(
                    candidate.get("risk_notes"),
                    candidate.get("warnings"),
                ),
                technical_errors=errors,
                material_signature=signature,
                proposal=candidate,
            )
        )

    dormant = []
    for candidate_id, prior in prior_by_id.items():
        if candidate_id in seen:
            continue
        dormant.append(prior.model_copy(update={"active": False, "included": False}))

    result = RouteReviewResult(
        route_id=route_id,
        revision_id="",
        proposals=proposals,
        dormant_proposals=sorted(dormant, key=lambda item: item.candidate_id),
        warnings=_route_warnings(event_list),
        technical_ready=_technical_ready(proposals),
    )
    result.revision_id = _revision_id(result)
    return result


def material_signature(candidate: dict[str, Any]) -> str:
    material = {field: candidate.get(field) for field in MATERIAL_FIELDS if field in candidate}
    return hashlib.sha256(_canonical_json(material).encode("utf-8")).hexdigest()


def proposal_errors(candidate: dict[str, Any]) -> list[str]:
    errors = []
    for field, label in RENDER_FIELDS.items():
        value = candidate.get(field)
        if not isinstance(value, str) or not value.strip():
            errors.append(f"Missing {label} ('{field}')")
    return errors


def _candidate_objects(event_list: dict[str, Any]) -> list[dict[str, Any]]:
    candidates = event_list.get("candidates")
    if not isinstance(candidates, list):
        raise RouteReviewError("Generated event list must contain a candidates list")
    if any(not isinstance(candidate, dict) for candidate in candidates):
        raise RouteReviewError("Generated event list contains a non-object candidate")
    return candidates


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


def _technical_ready(proposals: list[RouteReviewProposal]) -> bool:
    return all(proposal.renderable or not proposal.included for proposal in proposals)


def _revision_id(result: RouteReviewResult) -> str:
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
