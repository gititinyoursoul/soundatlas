import json
import os
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

from pydantic import BaseModel, Field

from app.config import DEFAULT_CONTENT_ROOT, DEFAULT_SEED_DIR
from app.route_review import (
    RouteEditorialReview,
    RouteReviewError,
    RouteReviewNotFoundError,
    RouteReviewProposal,
    RouteReviewRepository,
)
from app.schemas import Connection, Event, Place, Route
from app.seed_repository import SeedRepository

PUBLICATION_STATE_FILENAME = "route-publication.json"


class PublicationEventSummary(BaseModel):
    candidate_id: str
    title: str
    editorial_state: str
    included: bool


class RoutePublicationSummary(BaseModel):
    route_id: str
    revision_id: str
    source: str
    included_events: list[PublicationEventSummary]
    excluded_event_ids: list[str]
    warnings: list[str] = Field(default_factory=list)
    technical_errors: list[str] = Field(default_factory=list)
    route_warnings: list[str] = Field(default_factory=list)
    route_technical_errors: list[str] = Field(default_factory=list)
    included_event_warning_count: int = 0
    included_event_technical_error_count: int = 0
    technical_ready: bool
    published_revision_id: str | None = None


class RoutePublicationRequest(BaseModel):
    revision_id: str


class RoutePublicationResult(RoutePublicationSummary):
    published: bool


class RoutePublicationError(ValueError):
    pass


class RoutePublicationNotFoundError(RoutePublicationError):
    pass


class RoutePublicationConflictError(RoutePublicationError):
    pass


class RoutePublicationValidationError(RoutePublicationError):
    pass


@dataclass
class PublicationFindings:
    route_warnings: list[str] = field(default_factory=list)
    route_technical_errors: list[str] = field(default_factory=list)
    included_event_warnings: list[str] = field(default_factory=list)
    included_event_technical_errors: list[str] = field(default_factory=list)

    @property
    def warnings(self) -> list[str]:
        return _unique([*self.route_warnings, *self.included_event_warnings])

    @property
    def technical_errors(self) -> list[str]:
        return _unique([*self.route_technical_errors, *self.included_event_technical_errors])


class RoutePublicationRepository:
    def __init__(
        self,
        review_repository: RouteReviewRepository,
        content_root: Path = DEFAULT_CONTENT_ROOT,
        seed_dir: Path = DEFAULT_SEED_DIR,
    ) -> None:
        self._review_repository = review_repository
        self._content_root = content_root
        self._seed_dir = seed_dir

    def summary(self, route_id: str) -> RoutePublicationSummary:
        review = self._get_review(route_id)
        payload, findings = self._build_payload(review)
        del payload
        return self._summary(review, findings)

    def publish(self, route_id: str, revision_id: str) -> RoutePublicationResult:
        review = self._get_review(route_id)
        if review.revision_id != revision_id:
            raise RoutePublicationConflictError(
                f"Route review '{route_id}' changed; reload before publishing"
            )

        payload, findings = self._build_payload(review)
        summary = self._summary(review, findings)
        if not summary.technical_ready:
            raise RoutePublicationValidationError(
                "Publication is not technically ready: " + "; ".join(summary.technical_errors)
            )

        self._write_payloads(payload, route_id, review)
        return RoutePublicationResult(**summary.model_dump(), published=True)

    def _build_payload(
        self, review: RouteEditorialReview
    ) -> tuple[dict[str, dict[str, Any]], PublicationFindings]:
        findings = PublicationFindings(
            route_warnings=list(review.warnings),
            route_technical_errors=list(review.technical_errors),
        )
        try:
            seed = self._read_seed()
        except (FileNotFoundError, json.JSONDecodeError, RoutePublicationError) as exc:
            findings.route_technical_errors.append(str(exc))
            return self._empty_payload(), findings

        proposals_by_id = {proposal.candidate_id: proposal for proposal in review.proposals}
        candidate_ids = set(proposals_by_id)
        included_ids = {
            proposal.candidate_id
            for proposal in review.proposals
            if proposal.active and proposal.included
        }
        selected_events: list[dict[str, Any]] = []
        for proposal in review.proposals:
            candidate_id = proposal.candidate_id
            if candidate_id not in included_ids:
                continue
            findings.included_event_warnings.extend(proposal.warnings)
            findings.included_event_technical_errors.extend(
                f"{candidate_id}: {error}" for error in proposal.technical_errors
            )
            if proposal.event is None:
                if not proposal.technical_errors:
                    findings.included_event_technical_errors.append(
                        f"Included proposal '{candidate_id}' has no reader-facing event content."
                    )
                continue
            selected_events.append(proposal.event.model_dump(mode="json"))

        selected_place_ids = {
            place_id for event in selected_events for place_id in event.get("place_ids", [])
        }
        new_places = [
            item.place.model_dump(mode="json")
            for item in review.places
            if item.decision == "new" and item.place.id in selected_place_ids
        ]
        # Connections are deferred from the MVP. Keep legacy seed records
        # readable, but do not select or publish new relationship records.
        previous = self._read_publication_state(review.route_id)
        published_event_ids = set(previous.get("event_ids", []))
        events = [
            event
            for event in seed["events"].get("events", [])
            if not (
                event.get("route_id") == review.route_id
                and event.get("id") in (published_event_ids | candidate_ids)
            )
        ]
        events.extend(selected_events)
        places = [
            place
            for place in seed["places"].get("places", [])
            if place.get("id") not in {item.get("id") for item in new_places}
        ]
        places.extend(new_places)
        # Preserve legacy Connection data unchanged while it is deferred from
        # the MVP publication path.
        connections = list(seed["connections"].get("connections", []))
        payload = {
            "routes": seed["routes"],
            "places": {**seed["places"], "places": places},
            "events": {**seed["events"], "events": events},
            "connections": {**seed["connections"], "connections": connections},
        }
        findings.route_technical_errors.extend(self._validate_payload(payload))
        return payload, findings

    def _get_review(self, route_id: str) -> RouteEditorialReview:
        try:
            return self._review_repository.get(route_id)
        except RouteReviewNotFoundError as exc:
            raise RoutePublicationNotFoundError(str(exc)) from exc
        except RouteReviewError as exc:
            raise RoutePublicationError(str(exc)) from exc

    def _summary(
        self,
        review: RouteEditorialReview,
        findings: PublicationFindings,
    ) -> RoutePublicationSummary:
        included = [
            PublicationEventSummary(
                candidate_id=proposal.candidate_id,
                title=_proposal_title(proposal),
                editorial_state=proposal.editorial_state,
                included=proposal.included,
            )
            for proposal in review.proposals
            if proposal.active and proposal.included
        ]
        excluded = [
            proposal.candidate_id
            for proposal in review.proposals
            if proposal.active and not proposal.included
        ]
        state = self._read_publication_state(review.route_id)
        return RoutePublicationSummary(
            route_id=review.route_id,
            revision_id=review.revision_id,
            source=review.source,
            included_events=included,
            excluded_event_ids=excluded,
            warnings=findings.warnings,
            technical_errors=findings.technical_errors,
            route_warnings=_unique(findings.route_warnings),
            route_technical_errors=_unique(findings.route_technical_errors),
            included_event_warning_count=len(findings.included_event_warnings),
            included_event_technical_error_count=len(findings.included_event_technical_errors),
            technical_ready=not findings.technical_errors,
            published_revision_id=state.get("revision_id"),
        )

    def _write_payloads(
        self,
        payload: dict[str, dict[str, Any]],
        route_id: str,
        review: RouteEditorialReview,
    ) -> None:
        files = {
            "places.json": payload["places"],
            "events.json": payload["events"],
            "connections.json": payload["connections"],
        }
        state_path = self._route_dir(route_id) / PUBLICATION_STATE_FILENAME
        state = {
            "route_id": route_id,
            "revision_id": review.revision_id,
            "event_ids": [
                item.candidate_id for item in review.proposals if item.active and item.included
            ],
            "connection_ids": [
                item.get("id")
                for item in payload["connections"].get("connections", [])
                if item.get("from_event_id") in {p.candidate_id for p in review.proposals}
            ],
        }
        files[str(state_path)] = state
        old = {
            str(self._seed_dir / name): self._read_bytes(self._seed_dir / name)
            for name in files
            if not name.startswith("/")
        }
        old[str(state_path)] = self._read_bytes(state_path)
        temp_paths: list[Path] = []
        replaced: list[Path] = []
        try:
            for name, value in files.items():
                path = Path(name) if name.startswith("/") else self._seed_dir / name
                path.parent.mkdir(parents=True, exist_ok=True)
                temp = path.with_name(f".{path.name}.publication.tmp")
                temp.write_text(
                    json.dumps(value, indent=2, ensure_ascii=False) + "\n", encoding="utf-8"
                )
                temp_paths.append(temp)
                os.replace(temp, path)
                replaced.append(path)
        except OSError as exc:
            for path in replaced:
                previous = old.get(str(path))
                if previous is None:
                    path.unlink(missing_ok=True)
                else:
                    path.write_bytes(previous)
            raise RoutePublicationError(
                f"Publication failed; previous route was preserved: {exc}"
            ) from exc
        finally:
            for temp in temp_paths:
                temp.unlink(missing_ok=True)

    def _validate_payload(self, payload: dict[str, dict[str, Any]]) -> list[str]:
        errors: list[str] = []
        try:
            routes = [Route.model_validate(item) for item in payload["routes"].get("routes", [])]
            places = [Place.model_validate(item) for item in payload["places"].get("places", [])]
            events = [Event.model_validate(item) for item in payload["events"].get("events", [])]
            connections = [
                Connection.model_validate(item)
                for item in payload["connections"].get("connections", [])
            ]
            SeedRepository(routes, places, events, connections).validate_references()
        except Exception as exc:
            errors.append(str(exc))
        return errors

    def _read_seed(self) -> dict[str, dict[str, Any]]:
        return {
            name: self._read_json(self._seed_dir / f"{name}.json")
            for name in ("routes", "places", "events", "connections")
        }

    def _read_publication_state(self, route_id: str) -> dict[str, Any]:
        path = self._route_dir(route_id) / PUBLICATION_STATE_FILENAME
        if not path.exists():
            return {}
        return self._read_json(path)

    def _route_dir(self, route_id: str) -> Path:
        return self._content_root / route_id

    @staticmethod
    def _read_json(path: Path) -> dict[str, Any]:
        try:
            value = json.loads(path.read_text(encoding="utf-8"))
        except FileNotFoundError as exc:
            raise RoutePublicationNotFoundError(
                f"Publication input '{path.name}' not found"
            ) from exc
        if not isinstance(value, dict):
            raise RoutePublicationValidationError(
                f"Publication input '{path.name}' must be an object"
            )
        return value

    @staticmethod
    def _read_bytes(path: Path) -> bytes | None:
        try:
            return path.read_bytes()
        except FileNotFoundError:
            return None

    @staticmethod
    def _empty_payload() -> dict[str, dict[str, Any]]:
        return {
            "routes": {"routes": []},
            "places": {"places": []},
            "events": {"events": []},
            "connections": {"connections": []},
        }


def _proposal_title(proposal: RouteReviewProposal) -> str:
    for key in ("working_title", "title"):
        value = proposal.proposal.get(key)
        if isinstance(value, str) and value.strip():
            return value
    return proposal.candidate_id


def _unique(values: list[str]) -> list[str]:
    return list(dict.fromkeys(value for value in values if value))
