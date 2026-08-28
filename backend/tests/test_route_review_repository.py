import json
import os
from pathlib import Path

import pytest
from fastapi.testclient import TestClient

from app.main import create_app
from app.route_review import (
    RouteReviewConflictError,
    RouteReviewError,
    RouteReviewPlaceUpdate,
    RouteReviewRepository,
    RouteReviewStateUpdate,
)
from app.seed_repository import SeedRepository

ROUTE_ID = "review-route"


def test_refresh_defaults_to_draft_and_preserves_agent_recommendation(tmp_path: Path) -> None:
    repository = write_review_fixture(tmp_path)
    draft_path = tmp_path / ROUTE_ID / "complete-draft.json"
    payload = json.loads(draft_path.read_text(encoding="utf-8"))
    payload["warnings"] = ["Route chronology needs review."]
    draft_path.write_text(json.dumps(payload), encoding="utf-8")

    result = repository.refresh(ROUTE_ID)

    assert result.proposals[0].editorial_state == "draft"
    assert result.proposals[0].included is True
    assert result.proposals[0].agent_recommendation == "exclude"
    assert result.proposals[0].warnings == ["Check the date."]
    assert result.warnings == ["Route chronology needs review."]
    assert result.technical_ready is True
    assert (tmp_path / ROUTE_ID / "route-review.json").exists()


def test_review_binds_exact_reader_facing_event_and_place(tmp_path: Path) -> None:
    repository = write_review_fixture(tmp_path)
    draft_path = tmp_path / ROUTE_ID / "complete-draft.json"
    payload = json.loads(draft_path.read_text(encoding="utf-8"))
    payload["events"][0].pop("summary")
    payload["events"][0].pop("significance")
    payload["events"][0]["story_sections"] = [
        {"heading": "The room opens", "body": "The generated story begins."},
        {"heading": "A practice travels", "body": "The route meaning follows."},
    ]
    draft_path.write_text(json.dumps(payload), encoding="utf-8")

    result = repository.refresh(ROUTE_ID)

    proposal = result.proposals[0]
    assert result.source == "complete-draft.json"
    assert proposal.event is not None
    assert proposal.event.title == "Reader-facing event"
    assert [section.heading for section in proposal.event.story_sections] == [
        "The room opens",
        "A practice travels",
    ]
    assert proposal.event.source_urls == ["https://example.org/source"]
    assert result.places[0].place.name == "Review Place"


def test_review_bundle_resolves_new_places_media_relationships_and_connections(
    tmp_path: Path,
) -> None:
    repository = write_review_fixture(tmp_path, include_second=True)
    draft_path = tmp_path / ROUTE_ID / "complete-draft.json"
    payload = json.loads(draft_path.read_text(encoding="utf-8"))
    second = payload["events"][1]
    second["place_id"] = "new-place"
    second["place_ids"] = ["new-place", "place-one"]
    second["default_place_id"] = "new-place"
    second["place_relationships"] = [
        {
            "from_place_id": "place-one",
            "to_place_id": "new-place",
            "directionality": "forward",
            "context_label": "The practice moved between these places.",
            "source_urls": ["https://example.org/relationship"],
        }
    ]
    second["media_links"] = [
        {
            "provider": "youtube",
            "type": "video",
            "title": "Documentary excerpt",
            "url": "https://www.youtube.com/watch?v=example",
            "query": "review route documentary",
            "confidence": 0.8,
            "review_status": "draft",
        }
    ]
    payload["places"].append(
        {
            "decision": "new",
            "place_id": "new-place",
            "place": place("new-place") | {"name": "New Route Place"},
        }
    )
    payload["connections"] = [
        {
            "id": "event-one-to-event-two",
            "from_event_id": "event-one",
            "to_event_id": "event-two",
            "type": "influence",
            "summary": "The first event informs the second.",
            "review_status": "draft",
        }
    ]
    draft_path.write_text(json.dumps(payload), encoding="utf-8")

    result = repository.refresh(ROUTE_ID)

    assert [item.place.id for item in result.places] == ["new-place", "place-one"]
    assert result.places[0].decision == "new"
    assert result.proposals[1].event is not None
    assert result.proposals[1].event.media_links[0].title == "Documentary excerpt"
    assert result.proposals[1].event.place_relationships[0].to_place_id == "new-place"
    assert result.connections[0].id == "event-one-to-event-two"


@pytest.mark.parametrize(
    "geometry",
    [
        {
            "type": "Polygon",
            "coordinates": [
                [[-73.91, 40.8], [-73.9, 40.8], [-73.9, 40.81], [-73.91, 40.8]]
            ],
        },
        {
            "type": "MultiPolygon",
            "coordinates": [
                [
                    [
                        [-73.91, 40.8],
                        [-73.9, 40.8],
                        [-73.9, 40.81],
                        [-73.91, 40.8],
                    ]
                ]
            ],
        },
    ],
)
def test_review_accepts_new_area_places_with_complete_provenance(
    tmp_path: Path,
    geometry: dict[str, object],
) -> None:
    repository = write_review_fixture(tmp_path)
    draft_path = tmp_path / ROUTE_ID / "complete-draft.json"
    payload = json.loads(draft_path.read_text(encoding="utf-8"))
    payload["events"][0].update(
        {
            "place_id": "new-area",
            "place_ids": ["new-area"],
            "default_place_id": "new-area",
        }
    )
    payload["places"] = [
        {
            "decision": "new",
            "place_id": "new-area",
            "place": place("new-area")
            | {
                "geometry": geometry,
                "geometry_precision": "interpretive",
                "geometry_source_type": "external",
                "geometry_source_url": "https://example.org/geodata",
                "geometry_source_note": "Reviewed external boundary.",
                "geometry_license": "ODbL-1.0",
            },
        }
    ]
    draft_path.write_text(json.dumps(payload), encoding="utf-8")

    review = repository.refresh(ROUTE_ID)

    assert review.technical_ready is True
    assert review.places[0].place.geometry is not None
    assert review.places[0].place.geometry.type == geometry["type"]


def test_reader_facing_change_resets_approved_state_and_revision(tmp_path: Path) -> None:
    repository = write_review_fixture(tmp_path)
    first = repository.refresh(ROUTE_ID)
    approved = repository.update_state(
        ROUTE_ID,
        "event-one",
        RouteReviewStateUpdate(
            revision_id=first.revision_id,
            editorial_state="approved",
        ),
    )
    draft_path = tmp_path / ROUTE_ID / "complete-draft.json"
    payload = json.loads(draft_path.read_text(encoding="utf-8"))
    payload["events"][0]["summary"] = "Materially changed reader-facing story."
    draft_path.write_text(json.dumps(payload), encoding="utf-8")

    refreshed = repository.refresh(ROUTE_ID)

    assert refreshed.proposals[0].editorial_state == "draft"
    assert refreshed.proposals[0].event is not None
    assert refreshed.proposals[0].event.summary == "Materially changed reader-facing story."
    assert refreshed.revision_id != approved.revision_id


def test_invalid_reader_facing_event_is_an_explicit_technical_error(tmp_path: Path) -> None:
    repository = write_review_fixture(tmp_path)
    draft_path = tmp_path / ROUTE_ID / "complete-draft.json"
    payload = json.loads(draft_path.read_text(encoding="utf-8"))
    payload["events"][0].pop("summary")
    draft_path.write_text(json.dumps(payload), encoding="utf-8")

    result = repository.refresh(ROUTE_ID)

    assert result.proposals[0].event is None
    assert result.proposals[0].renderable is False
    assert result.technical_ready is False
    assert "event story requires story_sections" in result.proposals[0].technical_errors[0]


def test_missing_source_is_owned_blocks_publication_but_preserves_preview(
    tmp_path: Path,
) -> None:
    repository = write_review_fixture(tmp_path)
    draft_path = tmp_path / ROUTE_ID / "complete-draft.json"
    payload = json.loads(draft_path.read_text(encoding="utf-8"))
    payload["events"][0]["source_urls"] = []
    draft_path.write_text(json.dumps(payload), encoding="utf-8")

    result = repository.refresh(ROUTE_ID)

    assert result.technical_ready is False
    assert result.proposals[0].event is not None
    assert result.proposals[0].renderable is True
    assert result.proposals[0].technical_errors == ["Reader-facing event has no source URL."]
    assert any(
        finding.owner == "source_media"
        and finding.candidate_id == "event-one"
        and finding.blocking
        for finding in result.findings
    )


def test_state_updates_change_revision_and_reject_stale_writes(tmp_path: Path) -> None:
    repository = write_review_fixture(tmp_path)
    result = repository.refresh(ROUTE_ID)

    approved = repository.update_state(
        ROUTE_ID,
        "event-one",
        RouteReviewStateUpdate(
            revision_id=result.revision_id,
            editorial_state="approved",
        ),
    )
    assert approved.proposals[0].editorial_state == "approved"
    assert approved.revision_id != result.revision_id

    excluded = repository.update_state(
        ROUTE_ID,
        "event-one",
        RouteReviewStateUpdate(
            revision_id=approved.revision_id,
            editorial_state="dont_use",
        ),
    )
    assert excluded.proposals[0].included is False

    with pytest.raises(RouteReviewConflictError, match="reload before saving"):
        repository.update_state(
            ROUTE_ID,
            "event-one",
            RouteReviewStateUpdate(
                revision_id=approved.revision_id,
                editorial_state="draft",
            ),
        )


def test_spatial_update_requires_explicit_approval_and_resets_when_changed(
    tmp_path: Path,
) -> None:
    repository = write_review_fixture(tmp_path)
    draft_path = tmp_path / ROUTE_ID / "complete-draft.json"
    payload = json.loads(draft_path.read_text(encoding="utf-8"))
    payload["places"] = [
        {
            "decision": "update",
            "place_id": "place-one",
            "source_place_text": "Review Place",
            "spatial_update": {"latitude": 40.81, "longitude": -73.91},
        }
    ]
    draft_path.write_text(json.dumps(payload), encoding="utf-8")

    review = repository.refresh(ROUTE_ID)

    assert review.places[0].decision == "update"
    assert review.places[0].canonical_place is not None
    assert review.places[0].place.name == "Review Place"
    assert review.places[0].place.latitude == 40.81
    assert review.places[0].spatial_update_approved is False
    assert review.technical_ready is False

    approved = repository.update_place_review(
        ROUTE_ID,
        "place-one",
        RouteReviewPlaceUpdate(
            revision_id=review.revision_id,
            spatial_update_approved=True,
        ),
    )
    assert approved.places[0].spatial_update_approved is True
    assert approved.technical_ready is True

    payload["places"][0]["spatial_update"]["latitude"] = 40.82
    draft_path.write_text(json.dumps(payload), encoding="utf-8")
    refreshed = repository.refresh(ROUTE_ID)

    assert refreshed.places[0].spatial_update_approved is False
    assert refreshed.technical_ready is False


def test_spatial_update_rejects_non_spatial_fields_and_new_place_collisions(
    tmp_path: Path,
) -> None:
    repository = write_review_fixture(tmp_path)
    draft_path = tmp_path / ROUTE_ID / "complete-draft.json"
    payload = json.loads(draft_path.read_text(encoding="utf-8"))
    payload["places"] = [
        {
            "decision": "update",
            "place_id": "place-one",
            "spatial_update": {"name": "Rewritten place"},
        }
    ]
    draft_path.write_text(json.dumps(payload), encoding="utf-8")

    invalid_update = repository.refresh(ROUTE_ID)
    assert any("unsupported fields: name" in error for error in invalid_update.technical_errors)

    payload["places"] = [
        {
            "decision": "new",
            "place_id": "place-one",
            "place": place("place-one"),
        }
    ]
    draft_path.write_text(json.dumps(payload), encoding="utf-8")
    collision = repository.refresh(ROUTE_ID)

    assert any("already exists in canonical seeds" in error for error in collision.technical_errors)

    payload["events"][0].update(
        {
            "place_id": "new-place",
            "place_ids": ["new-place"],
            "default_place_id": "new-place",
        }
    )
    payload["places"] = [
        {
            "decision": "new",
            "place_id": "new-place",
            "place": place("new-place") | {"latitude": 0.0, "longitude": 0.0},
        }
    ]
    draft_path.write_text(json.dumps(payload), encoding="utf-8")
    placeholder = repository.refresh(ROUTE_ID)

    assert any("unresolved placeholder coordinates" in error for error in placeholder.technical_errors)


def test_regeneration_applies_selective_carryover_and_dormant_records(tmp_path: Path) -> None:
    repository = write_review_fixture(tmp_path, include_second=True)
    first = repository.refresh(ROUTE_ID)
    approved = repository.update_state(
        ROUTE_ID,
        "event-one",
        RouteReviewStateUpdate(
            revision_id=first.revision_id,
            editorial_state="approved",
        ),
    )
    rejected = repository.update_state(
        ROUTE_ID,
        "event-two",
        RouteReviewStateUpdate(
            revision_id=approved.revision_id,
            editorial_state="dont_use",
        ),
    )

    supporting_change = candidate("event-one", status="keep")
    supporting_change["decision_rationale"] = "Updated agent-only rationale."
    supporting_change["risk_notes"] = ["Updated warning."]
    write_event_list(tmp_path, [supporting_change, candidate("event-two", status="reject")])
    support_refreshed = repository.refresh(ROUTE_ID)
    support_states = {
        proposal.candidate_id: proposal.editorial_state
        for proposal in support_refreshed.proposals
    }
    assert support_states == {"event-one": "approved", "event-two": "dont_use"}

    write_event_list(
        tmp_path,
        [
            candidate("event-one", title="Materially changed title"),
            candidate("event-two", title="Also materially changed"),
            candidate("event-three"),
        ],
    )
    refreshed = repository.refresh(ROUTE_ID)
    states = {proposal.candidate_id: proposal.editorial_state for proposal in refreshed.proposals}
    assert states == {
        "event-one": "draft",
        "event-two": "dont_use",
        "event-three": "draft",
    }
    assert refreshed.revision_id != rejected.revision_id

    write_event_list(tmp_path, [candidate("event-one", title="Materially changed title")])
    removed = repository.refresh(ROUTE_ID)
    dormant = {proposal.candidate_id: proposal for proposal in removed.dormant_proposals}
    assert dormant["event-two"].editorial_state == "dont_use"
    assert dormant["event-two"].active is False
    assert dormant["event-three"].editorial_state == "draft"


def test_invalid_identifiable_proposal_remains_reviewable_and_can_be_excluded(
    tmp_path: Path,
) -> None:
    repository = write_review_fixture(tmp_path)
    invalid = candidate("event-one")
    invalid.pop("place")
    write_event_list(tmp_path, [invalid])

    result = repository.refresh(ROUTE_ID)

    assert result.proposals[0].renderable is False
    assert result.proposals[0].technical_errors == [
        "Missing place ('place')",
        "Context route entries require next_evidence_task with missing_evidence, "
        "target_claim, target_place, and expected_output.",
    ]
    assert result.technical_ready is False

    excluded = repository.update_state(
        ROUTE_ID,
        "event-one",
        RouteReviewStateUpdate(
            revision_id=result.revision_id,
            editorial_state="dont_use",
        ),
    )
    assert excluded.proposals[0].renderable is False
    assert excluded.technical_ready is True


def test_invalid_route_result_does_not_replace_existing_review(tmp_path: Path) -> None:
    repository = write_review_fixture(tmp_path)
    repository.refresh(ROUTE_ID)
    review_path = tmp_path / ROUTE_ID / "route-review.json"
    original = review_path.read_bytes()
    (tmp_path / ROUTE_ID / "complete-draft.json").write_text(
        "not json",
        encoding="utf-8",
    )

    with pytest.raises(RouteReviewError, match="not valid JSON"):
        repository.refresh(ROUTE_ID)

    assert review_path.read_bytes() == original


def test_failed_atomic_state_write_leaves_existing_review_usable(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    repository = write_review_fixture(tmp_path)
    result = repository.refresh(ROUTE_ID)
    review_path = tmp_path / ROUTE_ID / "route-review.json"
    original = review_path.read_bytes()

    def fail_replace(source: Path, destination: Path) -> None:
        raise OSError("simulated replace failure")

    monkeypatch.setattr(os, "replace", fail_replace)
    with pytest.raises(OSError, match="simulated replace failure"):
        repository.update_state(
            ROUTE_ID,
            "event-one",
            RouteReviewStateUpdate(
                revision_id=result.revision_id,
                editorial_state="approved",
            ),
        )

    assert review_path.read_bytes() == original


def test_editorial_api_rejects_invalid_route_ids(tmp_path: Path) -> None:
    repository = RouteReviewRepository(tmp_path)
    client = TestClient(
        create_app(
            SeedRepository([], [], [], []),
            route_review_repository=repository,
        )
    )

    response = client.get("/editorial/routes/Outside/review")

    assert response.status_code == 400


def test_editorial_review_openapi_keeps_compatibility_schema_name(tmp_path: Path) -> None:
    repository = write_review_fixture(tmp_path)
    repository.refresh(ROUTE_ID)
    client = TestClient(
        create_app(
            SeedRepository([], [], [], []),
            route_review_repository=repository,
        )
    )

    schema = client.get("/openapi.json").json()
    response_schema = schema["paths"]["/editorial/routes/{route_id}/review"]["get"][
        "responses"
    ]["200"]["content"]["application/json"]["schema"]

    assert response_schema == {"$ref": "#/components/schemas/RouteReviewResult"}
    assert "RouteEditorialReview" not in schema["components"]["schemas"]


def test_legacy_migration_is_explicit_and_does_not_use_agent_decisions(tmp_path: Path) -> None:
    repository = write_review_fixture(tmp_path, include_second=True)
    event_list_path = tmp_path / ROUTE_ID / "event-list.json"
    payload = json.loads(event_list_path.read_text(encoding="utf-8"))
    payload["candidates"][0]["review_state"] = "approved"
    payload["candidates"][1]["review_state"] = "rejected"
    event_list_path.write_text(json.dumps(payload), encoding="utf-8")

    report = repository.migrate_legacy(ROUTE_ID)
    result = repository.get(ROUTE_ID)

    assert report.migrated == {"pending": 0, "approved": 1, "rejected": 1}
    assert result.proposals[0].editorial_state == "approved"
    assert result.proposals[0].agent_recommendation == "exclude"
    assert result.proposals[1].editorial_state == "dont_use"
    with pytest.raises(RouteReviewConflictError, match="one-time"):
        repository.migrate_legacy(ROUTE_ID)


def test_editorial_api_reads_and_updates_private_state_without_public_leak(
    tmp_path: Path,
) -> None:
    repository = write_review_fixture(tmp_path)
    result = repository.refresh(ROUTE_ID)
    client = TestClient(
        create_app(
            SeedRepository([], [], [], []),
            route_review_repository=repository,
        )
    )

    response = client.get(f"/editorial/routes/{ROUTE_ID}/review")
    assert response.status_code == 200
    assert response.json()["revision_id"] == result.revision_id

    update = client.patch(
        f"/editorial/routes/{ROUTE_ID}/review/events/event-one",
        json={"revision_id": result.revision_id, "editorial_state": "approved"},
    )
    assert update.status_code == 200
    assert update.json()["proposals"][0]["editorial_state"] == "approved"

    stale = client.patch(
        f"/editorial/routes/{ROUTE_ID}/review/events/event-one",
        json={"revision_id": result.revision_id, "editorial_state": "draft"},
    )
    assert stale.status_code == 409
    assert client.get("/routes").json() == []
    assert client.get("/events").json() == []


def test_editorial_api_approves_only_revision_bound_existing_place_updates(
    tmp_path: Path,
) -> None:
    repository = write_review_fixture(tmp_path)
    draft_path = tmp_path / ROUTE_ID / "complete-draft.json"
    payload = json.loads(draft_path.read_text(encoding="utf-8"))
    payload["places"] = [
        {
            "decision": "update",
            "place_id": "place-one",
            "spatial_update": {"latitude": 40.81},
        }
    ]
    draft_path.write_text(json.dumps(payload), encoding="utf-8")
    review = repository.refresh(ROUTE_ID)
    client = TestClient(
        create_app(
            SeedRepository([], [], [], []),
            route_review_repository=repository,
        )
    )

    response = client.patch(
        f"/editorial/routes/{ROUTE_ID}/review/places/place-one",
        json={
            "revision_id": review.revision_id,
            "spatial_update_approved": True,
        },
    )

    assert response.status_code == 200
    assert response.json()["places"][0]["spatial_update_approved"] is True
    stale = client.patch(
        f"/editorial/routes/{ROUTE_ID}/review/places/place-one",
        json={
            "revision_id": review.revision_id,
            "spatial_update_approved": False,
        },
    )
    assert stale.status_code == 409


def write_review_fixture(
    content_root: Path,
    *,
    include_second: bool = False,
) -> RouteReviewRepository:
    candidates = [candidate("event-one", status="reject")]
    if include_second:
        candidates.append(candidate("event-two", status="keep"))
    write_event_list(content_root, candidates)
    seed_dir = content_root / "seed"
    seed_dir.mkdir(exist_ok=True)
    (seed_dir / "places.json").write_text(
        json.dumps({"places": [place("place-one")]}) + "\n",
        encoding="utf-8",
    )
    return RouteReviewRepository(content_root, seed_dir=seed_dir)


def write_event_list(content_root: Path, candidates: list[dict[str, object]]) -> None:
    route_dir = content_root / ROUTE_ID
    route_dir.mkdir(parents=True, exist_ok=True)
    (route_dir / "event-list.json").write_text(
        json.dumps(
            {
                "_meta": {"route_id": ROUTE_ID},
                "candidates": candidates,
            },
            indent=2,
        )
        + "\n",
        encoding="utf-8",
    )
    (route_dir / "complete-draft.json").write_text(
        json.dumps(
            {
                "_meta": {"route_id": ROUTE_ID},
                "candidates": candidates,
                "events": [event(str(item["candidate_id"])) for item in candidates],
                "places": [{"decision": "reuse", "place_id": "place-one"}],
                "connections": [],
                "warnings": [],
            },
            indent=2,
        )
        + "\n",
        encoding="utf-8",
    )


def candidate(
    candidate_id: str,
    *,
    title: str = "Review event",
    status: str = "maybe",
) -> dict[str, object]:
    return {
        "candidate_id": candidate_id,
        "status": status,
        "review_state": "pending",
        "years": "1973",
        "place": "Bronx",
        "working_title": title,
        "route_function": "Explain the route.",
        "decision_rationale": "Agent rationale.",
        "risk_notes": ["Check the date."],
    }


def event(event_id: str) -> dict[str, object]:
    return {
        "id": event_id,
        "route_id": ROUTE_ID,
        "place_id": "place-one",
        "place_ids": ["place-one"],
        "default_place_id": "place-one",
        "place_relationships": [],
        "title": "Reader-facing event",
        "year_start": 1973,
        "year_end": 1973,
        "summary": "What happened in the generated story.",
        "significance": "Why the generated story matters.",
        "tags": [],
        "review_status": "draft",
        "source_urls": ["https://example.org/source"],
        "media_links": [],
        "image_links": [],
    }


def place(place_id: str) -> dict[str, object]:
    return {
        "id": place_id,
        "name": "Review Place",
        "borough": "Bronx",
        "place_type": "venue",
        "latitude": 40.8,
        "longitude": -73.9,
        "summary": "Review place summary.",
        "review_status": "draft",
        "source_urls": [],
    }
