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
    ) -> None:
        self._routes = routes
        self._places = places
        self._events = events
        self._connections = connections
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
        repository = cls(routes, places, events, connections)
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


def _read_collection(
    path: Path,
    collection_key: str,
    model: type[Route] | type[Place] | type[Event] | type[Connection],
) -> list[Any]:
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except FileNotFoundError as exc:
        raise SeedValidationError(f"Missing seed file: {path}") from exc
    except json.JSONDecodeError as exc:
        raise SeedValidationError(f"Invalid JSON in seed file: {path}") from exc

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
