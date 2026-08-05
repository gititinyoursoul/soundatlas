import json
import os
from pathlib import Path
from typing import Any

from pydantic import BaseModel, Field

from app.config import DEFAULT_CONTENT_ROOT, DEFAULT_SEED_DIR
from app.route_review import (
    RouteReviewError,
    RouteReviewNotFoundError,
    RouteReviewProposal,
    RouteReviewRepository,
    RouteReviewResult,
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
        payload, warnings, technical_errors = self._build_payload(review)
        del payload
        return self._summary(review, warnings, technical_errors)

    def publish(self, route_id: str, revision_id: str) -> RoutePublicationResult:
        review = self._get_review(route_id)
        if review.revision_id != revision_id:
            raise RoutePublicationConflictError(
                f"Route review '{route_id}' changed; reload before publishing"
            )

        payload, warnings, technical_errors = self._build_payload(review)
        summary = self._summary(review, warnings, technical_errors)
        if not summary.technical_ready:
            raise RoutePublicationValidationError(
                "Publication is not technically ready: "
                + "; ".join(summary.technical_errors)
            )

        self._write_payloads(payload, route_id, review)
        return RoutePublicationResult(**summary.model_dump(), published=True)

    def _build_payload(
        self, review: RouteReviewResult
    ) -> tuple[dict[str, dict[str, Any]], list[str], list[str]]:
        route_dir = self._route_dir(review.route_id)
        manifest = self._read_json(route_dir / "pipeline.json")
        framing_name = (
            manifest.get("steps", {}).get("event_framing", {}).get("events")
        )
        places_name = (
            manifest.get("steps", {}).get("event_framing", {}).get("places")
        )
        connections_name = (
            manifest.get("steps", {}).get("event_framing", {}).get("connections")
        )
        technical_errors: list[str] = []
        if not all(isinstance(name, str) and name for name in (framing_name, places_name, connections_name)):
            technical_errors.append("Pipeline manifest is missing event framing outputs.")
            return self._empty_payload(), [], technical_errors

        try:
            event_framing = self._read_json(route_dir / framing_name)
            place_framing = self._read_json(route_dir / places_name)
            connection_framing = self._read_json(route_dir / connections_name)
            seed = self._read_seed()
        except (FileNotFoundError, json.JSONDecodeError, RoutePublicationError) as exc:
            technical_errors.append(str(exc))
            return self._empty_payload(), [], technical_errors

        proposals_by_id = {proposal.candidate_id: proposal for proposal in review.proposals}
        candidate_ids = set(proposals_by_id)
        included_ids = {
            proposal.candidate_id
            for proposal in review.proposals
            if proposal.active and proposal.included
        }
        framing_events = {
            item.get("id"): item
            for item in event_framing.get("events", [])
            if isinstance(item, dict) and isinstance(item.get("id"), str)
        }
        selected_events: list[dict[str, Any]] = []
        for candidate_id in sorted(included_ids):
            event = framing_events.get(candidate_id)
            if event is None:
                technical_errors.append(
                    f"Included proposal '{candidate_id}' has no event framing record."
                )
                continue
            selected_events.append(event)
            proposal = proposals_by_id[candidate_id]
            technical_errors.extend(
                f"{candidate_id}: {error}" for error in proposal.technical_errors
            )

        selected_event_ids = {event.get("id") for event in selected_events}
        selected_place_ids = {event.get("place_id") for event in selected_events}
        new_places = [
            item["place"]
            for item in place_framing.get("places", [])
            if isinstance(item, dict)
            and item.get("decision") == "new"
            and item.get("place_id") in selected_place_ids
            and isinstance(item.get("place"), dict)
        ]
        selected_connections = [
            item
            for item in connection_framing.get("connections", [])
            if isinstance(item, dict)
            and item.get("from_event_id") in selected_event_ids
            and item.get("to_event_id") in selected_event_ids
        ]

        previous = self._read_publication_state(review.route_id)
        published_event_ids = set(previous.get("event_ids", []))
        published_connection_ids = set(previous.get("connection_ids", []))
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
        connections = [
            connection
            for connection in seed["connections"].get("connections", [])
            if connection.get("id") not in published_connection_ids
            and not (
                connection.get("from_event_id") in candidate_ids
                or connection.get("to_event_id") in candidate_ids
            )
        ]
        connections.extend(selected_connections)
        payload = {
            "routes": seed["routes"],
            "places": {"places": places},
            "events": {"events": events},
            "connections": {"connections": connections},
        }
        technical_errors.extend(self._validate_payload(payload))
        warnings = list(review.warnings)
        for proposal in review.proposals:
            warnings.extend(proposal.warnings)
        return payload, _unique(warnings), _unique(technical_errors)

    def _get_review(self, route_id: str) -> RouteReviewResult:
        try:
            return self._review_repository.get(route_id)
        except RouteReviewNotFoundError as exc:
            raise RoutePublicationNotFoundError(str(exc)) from exc
        except RouteReviewError as exc:
            raise RoutePublicationError(str(exc)) from exc

    def _summary(
        self,
        review: RouteReviewResult,
        warnings: list[str],
        technical_errors: list[str],
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
            warnings=warnings,
            technical_errors=technical_errors,
            technical_ready=not technical_errors,
            published_revision_id=state.get("revision_id"),
        )

    def _write_payloads(
        self,
        payload: dict[str, dict[str, Any]],
        route_id: str,
        review: RouteReviewResult,
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
            "event_ids": [item.candidate_id for item in review.proposals if item.active and item.included],
            "connection_ids": [
                item.get("id")
                for item in payload["connections"].get("connections", [])
                if item.get("from_event_id") in {p.candidate_id for p in review.proposals}
            ],
        }
        files[str(state_path)] = state
        old = {str(self._seed_dir / name): self._read_bytes(self._seed_dir / name) for name in files if not name.startswith("/")}
        old[str(state_path)] = self._read_bytes(state_path)
        temp_paths: list[Path] = []
        replaced: list[Path] = []
        try:
            for name, value in files.items():
                path = Path(name) if name.startswith("/") else self._seed_dir / name
                path.parent.mkdir(parents=True, exist_ok=True)
                temp = path.with_name(f".{path.name}.publication.tmp")
                temp.write_text(json.dumps(value, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
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
            raise RoutePublicationError(f"Publication failed; previous route was preserved: {exc}") from exc
        finally:
            for temp in temp_paths:
                temp.unlink(missing_ok=True)

    def _validate_payload(self, payload: dict[str, dict[str, Any]]) -> list[str]:
        errors: list[str] = []
        try:
            routes = [Route.model_validate(item) for item in payload["routes"].get("routes", [])]
            places = [Place.model_validate(item) for item in payload["places"].get("places", [])]
            events = [Event.model_validate(item) for item in payload["events"].get("events", [])]
            connections = [Connection.model_validate(item) for item in payload["connections"].get("connections", [])]
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
            raise RoutePublicationNotFoundError(f"Publication input '{path.name}' not found") from exc
        if not isinstance(value, dict):
            raise RoutePublicationValidationError(f"Publication input '{path.name}' must be an object")
        return value

    @staticmethod
    def _read_bytes(path: Path) -> bytes | None:
        try:
            return path.read_bytes()
        except FileNotFoundError:
            return None

    @staticmethod
    def _empty_payload() -> dict[str, dict[str, Any]]:
        return {"routes": {"routes": []}, "places": {"places": []}, "events": {"events": []}, "connections": {"connections": []}}


def _proposal_title(proposal: RouteReviewProposal) -> str:
    for key in ("working_title", "title"):
        value = proposal.proposal.get(key)
        if isinstance(value, str) and value.strip():
            return value
    return proposal.candidate_id


def _unique(values: list[str]) -> list[str]:
    return list(dict.fromkeys(value for value in values if value))
