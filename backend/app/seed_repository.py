import json
from pathlib import Path
from typing import Any

from pydantic import ValidationError

from app.config import DEFAULT_SEED_DIR
from app.schemas import Connection, Event, Place, Route


class SeedValidationError(ValueError):
    pass


class SeedRepository:
    def __init__(
        self,
        routes: list[Route],
        places: list[Place],
        events: list[Event],
        connections: list[Connection],
        seed_dir: Path | None = None,
    ) -> None:
        self._routes = routes
        self._places = places
        self._events = events
        self._connections = connections
        self._seed_dir = seed_dir
        self._route_ids = {route.id for route in routes}
        self._place_ids = {place.id for place in places}
        self._event_ids = {event.id for event in events}
        self._events_by_id = {event.id: event for event in events}

    @classmethod
    def from_seed_dir(cls, seed_dir: Path = DEFAULT_SEED_DIR) -> "SeedRepository":
        routes = _read_collection(seed_dir / "routes.json", "routes", Route)
        places = _read_collection(seed_dir / "places.json", "places", Place)
        events = _read_collection(seed_dir / "events.json", "events", Event)
        connections = _read_collection(
            seed_dir / "connections.json",
            "connections",
            Connection,
        )
        repository = cls(routes, places, events, connections, seed_dir=seed_dir)
        repository.validate_references()
        return repository

    def validate_references(self) -> None:
        for event in self._events:
            if event.route_id not in self._route_ids:
                raise SeedValidationError(
                    f"Event '{event.id}' references unknown route '{event.route_id}'",
                )
            if event.place_id not in self._place_ids:
                raise SeedValidationError(
                    f"Event '{event.id}' references unknown place '{event.place_id}'",
                )

        for connection in self._connections:
            if connection.from_event_id not in self._event_ids:
                raise SeedValidationError(
                    "Connection "
                    f"'{connection.id}' references unknown source event "
                    f"'{connection.from_event_id}'",
                )
            if connection.to_event_id not in self._event_ids:
                raise SeedValidationError(
                    "Connection "
                    f"'{connection.id}' references unknown target event "
                    f"'{connection.to_event_id}'",
                )

    def list_routes(self) -> list[Route]:
        return self._routes

    def has_route(self, route_id: str) -> bool:
        return route_id in self._route_ids

    def list_places(self) -> list[Place]:
        return self._places

    def list_events(
        self,
        from_year: int | None = None,
        to_year: int | None = None,
        route_id: str | None = None,
    ) -> list[Event]:
        events = self._events
        if route_id is not None:
            events = [event for event in events if event.route_id == route_id]
        if from_year is not None:
            events = [event for event in events if event.year_end >= from_year]
        if to_year is not None:
            events = [event for event in events if event.year_start <= to_year]
        return events

    def get_event(self, event_id: str) -> Event | None:
        return self._events_by_id.get(event_id)

    def mark_media_link_reviewed(self, event_id: str, media_url: str) -> Event | None:
        return self.mark_event_link_reviewed(event_id, "media", media_url)

    def reject_media_link(self, event_id: str, media_url: str) -> Event | None:
        return self.reject_event_link(event_id, "media", media_url)

    def mark_event_link_reviewed(
        self,
        event_id: str,
        link_kind: str,
        url: str,
    ) -> Event | None:
        event = self.get_event(event_id)
        if event is None:
            return None

        link_collection = event.media_links if link_kind == "media" else event.image_links
        link = next((link for link in link_collection if link_matches_url(link, url)), None)
        if link is None:
            return None

        link.review_status = "reviewed"
        self._write_link_review_status(event_id, link_kind, url, "reviewed")
        return event

    def reject_event_link(
        self,
        event_id: str,
        link_kind: str,
        url: str,
    ) -> Event | None:
        event = self.get_event(event_id)
        if event is None:
            return None

        if link_kind == "media":
            next_links = [
                media_link
                for media_link in event.media_links
                if not link_matches_url(media_link, url)
            ]
            if len(next_links) == len(event.media_links):
                return None
            event.media_links = next_links
        else:
            next_links = [
                image_link
                for image_link in event.image_links
                if not link_matches_url(image_link, url)
            ]
            if len(next_links) == len(event.image_links):
                return None
            event.image_links = next_links

        self._remove_link(event_id, link_kind, url)
        return event

    def mark_image_link_reviewed(self, event_id: str, image_url: str) -> Event | None:
        return self.mark_event_link_reviewed(event_id, "image", image_url)

    def reject_image_link(self, event_id: str, image_url: str) -> Event | None:
        return self.reject_event_link(event_id, "image", image_url)

    def list_connections(self, route_id: str | None = None) -> list[Connection]:
        if route_id is None:
            return self._connections

        route_event_ids = {
            event.id for event in self._events if event.route_id == route_id
        }
        return [
            connection
            for connection in self._connections
            if connection.from_event_id in route_event_ids
            and connection.to_event_id in route_event_ids
        ]

    def _write_media_link_review_status(
        self,
        event_id: str,
        media_url: str,
        review_status: str,
    ) -> None:
        self._write_link_review_status(event_id, "media", media_url, review_status)

    def _remove_media_link(self, event_id: str, media_url: str) -> None:
        self._remove_link(event_id, "media", media_url)

    def _write_link_review_status(
        self,
        event_id: str,
        link_kind: str,
        url: str,
        review_status: str,
    ) -> None:
        if self._seed_dir is None:
            return

        events_path = self._seed_dir / "events.json"
        payload = read_json_payload(events_path)
        collection_key = get_link_collection_key(link_kind)
        for event in payload.get("events", []):
            if event.get("id") != event_id:
                continue
            for link in event.get(collection_key, []):
                if raw_link_matches_url(link, url):
                    link["review_status"] = review_status
                    write_json_payload(events_path, payload)
                    return

    def _remove_link(self, event_id: str, link_kind: str, url: str) -> None:
        if self._seed_dir is None:
            return

        events_path = self._seed_dir / "events.json"
        payload = read_json_payload(events_path)
        collection_key = get_link_collection_key(link_kind)
        for event in payload.get("events", []):
            if event.get("id") != event_id:
                continue
            event[collection_key] = [
                link
                for link in event.get(collection_key, [])
                if not raw_link_matches_url(link, url)
            ]
            write_json_payload(events_path, payload)
            return

def _read_collection(
    path: Path,
    collection_key: str,
    model: type[Route] | type[Place] | type[Event] | type[Connection],
) -> list[Any]:
    payload = read_json_payload(path)

    collection = payload.get(collection_key)
    if not isinstance(collection, list):
        raise SeedValidationError(
            f"Seed file '{path}' must contain a '{collection_key}' list",
        )

    try:
        return [model.model_validate(item) for item in collection]
    except ValidationError as exc:
        raise SeedValidationError(
            f"Seed file '{path}' failed schema validation",
        ) from exc


def read_json_payload(path: Path) -> dict[str, Any]:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except FileNotFoundError as exc:
        raise SeedValidationError(f"Missing seed file: {path}") from exc
    except json.JSONDecodeError as exc:
        raise SeedValidationError(f"Invalid JSON in seed file: {path}") from exc


def write_json_payload(path: Path, payload: dict[str, Any]) -> None:
    path.write_text(
        json.dumps(payload, indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )


def get_link_collection_key(link_kind: str) -> str:
    return "media_links" if link_kind == "media" else "image_links"


def link_matches_url(link: Any, url: str) -> bool:
    return any(
        getattr(link, attribute, None) == url
        for attribute in ("url", "image_url", "source_url", "thumbnail_url")
    )


def raw_link_matches_url(link: dict[str, Any], url: str) -> bool:
    return any(
        link.get(attribute) == url
        for attribute in ("url", "image_url", "source_url", "thumbnail_url")
    )
