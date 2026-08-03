from copy import deepcopy

import pytest
from pydantic import ValidationError

from app.schemas import Event, Place, Route
from app.seed_repository import SeedRepository, SeedValidationError


def event_payload() -> dict:
    return {
        "id": "spatial-event",
        "route_id": "route",
        "place_id": "place-a",
        "place_ids": ["place-a", "place-b"],
        "default_place_id": "place-a",
        "place_relationships": [
            {
                "from_place_id": "place-a",
                "to_place_id": "place-b",
                "directionality": "forward",
                "context_label": "Practice circulates toward another site.",
                "source_urls": ["https://example.org/relationship"],
            }
        ],
        "title": "Spatial event",
        "year_start": 1973,
        "year_end": 1974,
        "summary": "Summary",
        "significance": "Significance",
        "tags": [],
        "review_status": "draft",
        "source_urls": [],
        "media_links": [],
        "image_links": [],
    }


def place_payload(place_id: str = "place-a") -> dict:
    return {
        "id": place_id,
        "name": place_id,
        "borough": "Bronx",
        "place_type": "site",
        "latitude": 40.82,
        "longitude": -73.93,
        "summary": "Summary",
        "review_status": "draft",
        "source_urls": [],
    }


def route() -> Route:
    return Route.model_validate(
        {
            "id": "route",
            "title": "Route",
            "creator": "test",
            "color": "#000000",
            "year_start": 1970,
            "year_end": 1980,
            "summary": "Summary",
            "thesis": "Thesis",
            "tags": [],
            "review_status": "draft",
            "source_urls": [],
        }
    )


def test_legacy_event_normalizes_to_canonical_places() -> None:
    payload = event_payload()
    payload.pop("place_ids")
    payload.pop("default_place_id")
    payload.pop("place_relationships")

    event = Event.model_validate(payload)

    assert event.place_ids == ["place-a"]
    assert event.default_place_id == "place-a"
    assert event.place_id == "place-a"
    assert event.place_relationships == []


def test_canonical_event_supplies_legacy_alias() -> None:
    payload = event_payload()
    payload.pop("place_id")

    event = Event.model_validate(payload)

    assert event.place_id == "place-a"


@pytest.mark.parametrize(
    ("field", "value"),
    [
        ("place_ids", []),
        ("place_ids", ["place-a", "place-a"]),
        ("default_place_id", "place-c"),
        ("place_id", "place-b"),
    ],
)
def test_event_rejects_invalid_place_composition(field: str, value: object) -> None:
    payload = event_payload()
    payload[field] = value

    with pytest.raises(ValidationError):
        Event.model_validate(payload)


@pytest.mark.parametrize("directionality", ["undirected", "forward", "reciprocal"])
def test_event_accepts_each_relationship_direction(directionality: str) -> None:
    payload = event_payload()
    payload["place_relationships"][0]["directionality"] = directionality

    assert (
        Event.model_validate(payload).place_relationships[0].directionality
        == directionality
    )


@pytest.mark.parametrize(
    ("field", "value"),
    [
        ("directionality", "grouped"),
        ("context_label", "  "),
        ("source_urls", []),
        ("source_urls", [""]),
        ("to_place_id", "place-a"),
    ],
)
def test_event_rejects_invalid_place_relationship(field: str, value: object) -> None:
    payload = event_payload()
    payload["place_relationships"][0][field] = value

    with pytest.raises(ValidationError):
        Event.model_validate(payload)


def test_place_accepts_curated_polygon_without_external_source() -> None:
    payload = place_payload()
    payload.update(
        {
            "geometry": {
                "type": "Polygon",
                "coordinates": [
                    [
                        [-73.94, 40.81],
                        [-73.93, 40.81],
                        [-73.93, 40.82],
                        [-73.94, 40.81],
                    ]
                ],
            },
            "geometry_precision": "interpretive",
            "geometry_source_type": "curated",
            "geometry_source_note": "SoundAtlas-curated interpretive outline.",
        }
    )

    assert Place.model_validate(payload).geometry is not None


def test_place_accepts_external_multipolygon_with_provenance() -> None:
    payload = place_payload()
    payload.update(
        {
            "geometry": {
                "type": "MultiPolygon",
                "coordinates": [
                    [
                        [
                            [-73.94, 40.81],
                            [-73.93, 40.81],
                            [-73.93, 40.82],
                            [-73.94, 40.81],
                        ]
                    ]
                ],
            },
            "geometry_precision": "site",
            "geometry_source_type": "external",
            "geometry_source_url": "https://example.org/geometry",
            "geometry_source_note": "Published site boundary.",
            "geometry_license": "ODbL 1.0",
        }
    )

    assert Place.model_validate(payload).geometry is not None


@pytest.mark.parametrize(
    ("field", "value"),
    [
        ("geometry_source_url", None),
        ("geometry_license", None),
        ("geometry_source_note", ""),
    ],
)
def test_external_geometry_rejects_incomplete_provenance(
    field: str,
    value: object,
) -> None:
    payload = place_payload()
    payload.update(
        {
            "geometry": {
                "type": "Polygon",
                "coordinates": [
                    [
                        [-73.94, 40.81],
                        [-73.93, 40.81],
                        [-73.93, 40.82],
                        [-73.94, 40.81],
                    ]
                ],
            },
            "geometry_precision": "site",
            "geometry_source_type": "external",
            "geometry_source_url": "https://example.org/geometry",
            "geometry_source_note": "Published site boundary.",
            "geometry_license": "ODbL 1.0",
        }
    )
    payload[field] = value

    with pytest.raises(ValidationError):
        Place.model_validate(payload)


@pytest.mark.parametrize(
    "coordinates",
    [
        [],
        [[[-73.94, 40.81], [-73.93, 40.81], [-73.94, 40.81]]],
        [[[-73.94, 40.81], [-73.93, 40.81], [-73.93, 40.82], [-73.92, 40.81]]],
        [[[-181, 40.81], [-73.93, 40.81], [-73.93, 40.82], [-181, 40.81]]],
    ],
)
def test_place_rejects_malformed_polygon(coordinates: list) -> None:
    payload = place_payload()
    payload.update(
        {
            "geometry": {"type": "Polygon", "coordinates": coordinates},
            "geometry_precision": "interpretive",
            "geometry_source_type": "curated",
            "geometry_source_note": "Interpretive outline.",
        }
    )

    with pytest.raises(ValidationError):
        Place.model_validate(payload)


def test_repository_rejects_relationship_endpoint_outside_event_places() -> None:
    payload = event_payload()
    payload["place_ids"] = ["place-a"]
    event = Event.model_validate(payload)
    repository = SeedRepository(
        [route()],
        [Place.model_validate(place_payload("place-a")), Place.model_validate(place_payload("place-b"))],
        [event],
        [],
    )

    with pytest.raises(SeedValidationError, match="must appear in event place_ids"):
        repository.validate_references()


def test_repository_rejects_unknown_event_place() -> None:
    payload = deepcopy(event_payload())
    payload["place_ids"] = ["place-a", "missing-place"]
    payload["place_relationships"] = []
    event = Event.model_validate(payload)
    repository = SeedRepository(
        [route()],
        [Place.model_validate(place_payload("place-a"))],
        [event],
        [],
    )

    with pytest.raises(SeedValidationError, match="unknown place 'missing-place'"):
        repository.validate_references()


@pytest.mark.parametrize(
    "place_kinds",
    [
        ["point"],
        ["area"],
        ["point", "point"],
        ["area", "area"],
        ["point", "area"],
    ],
    ids=["one-point", "one-area", "multiple-points", "multiple-areas", "mixed"],
)
def test_repository_accepts_supported_spatial_footprints(
    place_kinds: list[str],
) -> None:
    places = []
    place_ids = []
    for index, place_kind in enumerate(place_kinds):
        place_id = f"place-{index}"
        payload = place_payload(place_id)
        if place_kind == "area":
            payload.update(
                {
                    "geometry": {
                        "type": "Polygon",
                        "coordinates": [
                            [
                                [-73.94 + index * 0.01, 40.81],
                                [-73.93 + index * 0.01, 40.81],
                                [-73.93 + index * 0.01, 40.82],
                                [-73.94 + index * 0.01, 40.81],
                            ]
                        ],
                    },
                    "geometry_precision": "interpretive",
                    "geometry_source_type": "curated",
                    "geometry_source_note": "Deterministic test fixture.",
                }
            )
        places.append(Place.model_validate(payload))
        place_ids.append(place_id)

    payload = event_payload()
    payload.update(
        {
            "place_id": place_ids[0],
            "place_ids": place_ids,
            "default_place_id": place_ids[0],
            "place_relationships": [],
        }
    )
    repository = SeedRepository(
        [route()],
        places,
        [Event.model_validate(payload)],
        [],
    )

    repository.validate_references()
