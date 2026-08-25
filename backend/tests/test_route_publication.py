import json
from pathlib import Path

import pytest
from fastapi.testclient import TestClient

from app.main import create_app
from app.route_publication import RoutePublicationError, RoutePublicationRepository
from app.route_review import RouteReviewRepository, RouteReviewStateUpdate
from app.seed_repository import SeedRepository

ROUTE_ID = "review-route"


def test_publication_summary_and_publish_filter_exact_review_result(tmp_path: Path) -> None:
    content_root = tmp_path / "content"
    seed_dir = tmp_path / "seed"
    write_publication_fixture(content_root, seed_dir)
    review_repository = RouteReviewRepository(content_root, seed_dir=seed_dir)
    review = review_repository.refresh(ROUTE_ID)
    review = review_repository.update_state(
        ROUTE_ID,
        "event-two",
        RouteReviewStateUpdate(
            revision_id=review.revision_id,
            editorial_state="dont_use",
        ),
    )
    publication_repository = RoutePublicationRepository(
        review_repository,
        content_root=content_root,
        seed_dir=seed_dir,
    )
    client = TestClient(
        create_app(
            SeedRepository.from_seed_dir(seed_dir),
            route_review_repository=review_repository,
            route_publication_repository=publication_repository,
        )
    )

    summary = client.get(f"/editorial/routes/{ROUTE_ID}/publication")
    assert summary.status_code == 200
    assert [item["candidate_id"] for item in summary.json()["included_events"]] == ["event-one"]
    assert summary.json()["excluded_event_ids"] == ["event-two"]
    assert summary.json()["technical_ready"] is True

    published = client.post(
        f"/editorial/routes/{ROUTE_ID}/publication",
        json={"revision_id": review.revision_id},
    )
    assert published.status_code == 200
    assert published.json()["published"] is True
    places_payload = json.loads((seed_dir / "places.json").read_text(encoding="utf-8"))
    events_payload = json.loads((seed_dir / "events.json").read_text(encoding="utf-8"))
    connections_payload = json.loads(
        (seed_dir / "connections.json").read_text(encoding="utf-8")
    )
    assert [event["id"] for event in events_payload["events"]] == ["event-one"]
    assert places_payload["_meta"] == {"schema_version": 2}
    assert places_payload["place_notes"] == ["Keep place metadata."]
    assert events_payload["_meta"] == {"schema_version": 2}
    assert events_payload["ignored_links"] == [
        {
            "event_id": "event-two",
            "kind": "media",
            "values": ["https://example.org/ignored"],
        }
    ]
    assert connections_payload["_meta"] == {"schema_version": 1}
    assert connections_payload["connection_notes"] == {"status": "preserve"}
    assert (
        json.loads(
            (content_root / ROUTE_ID / "route-publication.json").read_text(encoding="utf-8")
        )["revision_id"]
        == review.revision_id
    )


def test_publication_summary_separates_route_and_included_event_findings(
    tmp_path: Path,
) -> None:
    content_root = tmp_path / "content"
    seed_dir = tmp_path / "seed"
    write_publication_fixture(content_root, seed_dir)
    draft_path = content_root / ROUTE_ID / "complete-draft.json"
    draft = json.loads(draft_path.read_text(encoding="utf-8"))
    draft["warnings"] = ["Review the route chronology."]
    draft["candidates"][0]["risk_notes"] = ["Verify the first event date."]
    draft["candidates"][1]["risk_notes"] = ["Verify the excluded event date."]
    draft["events"][1].pop("summary")
    draft_path.write_text(json.dumps(draft), encoding="utf-8")
    review_repository = RouteReviewRepository(content_root, seed_dir=seed_dir)
    review = review_repository.refresh(ROUTE_ID)
    review = review_repository.update_state(
        ROUTE_ID,
        "event-two",
        RouteReviewStateUpdate(
            revision_id=review.revision_id,
            editorial_state="dont_use",
        ),
    )
    repository = RoutePublicationRepository(
        review_repository,
        content_root=content_root,
        seed_dir=seed_dir,
    )

    summary = repository.summary(ROUTE_ID)

    assert summary.route_warnings == ["Review the route chronology."]
    assert summary.included_event_warning_count == 1
    assert summary.included_event_technical_error_count == 0
    assert summary.warnings == [
        "Review the route chronology.",
        "Verify the first event date.",
    ]
    assert "Verify the excluded event date." not in summary.warnings
    assert summary.technical_errors == []
    assert summary.technical_ready is True


def test_publication_summary_keeps_route_only_errors_distinct(tmp_path: Path) -> None:
    content_root = tmp_path / "content"
    seed_dir = tmp_path / "seed"
    write_publication_fixture(content_root, seed_dir)
    draft_path = content_root / ROUTE_ID / "complete-draft.json"
    draft = json.loads(draft_path.read_text(encoding="utf-8"))
    draft["connections"][0]["to_event_id"] = "missing-event"
    draft_path.write_text(json.dumps(draft), encoding="utf-8")
    review_repository = RouteReviewRepository(content_root, seed_dir=seed_dir)
    review_repository.refresh(ROUTE_ID)
    repository = RoutePublicationRepository(
        review_repository,
        content_root=content_root,
        seed_dir=seed_dir,
    )

    summary = repository.summary(ROUTE_ID)

    assert summary.included_event_technical_error_count == 0
    assert summary.route_technical_errors == [
        "Connection 'event-one-to-event-two' references inactive or missing events: missing-event."
    ]
    assert summary.technical_errors == summary.route_technical_errors
    assert summary.technical_ready is False


def test_publication_rejects_stale_revision_without_writing(tmp_path: Path) -> None:
    content_root = tmp_path / "content"
    seed_dir = tmp_path / "seed"
    write_publication_fixture(content_root, seed_dir)
    review_repository = RouteReviewRepository(content_root, seed_dir=seed_dir)
    first = review_repository.refresh(ROUTE_ID)
    second = review_repository.update_state(
        ROUTE_ID,
        "event-one",
        RouteReviewStateUpdate(
            revision_id=first.revision_id,
            editorial_state="approved",
        ),
    )
    publication_repository = RoutePublicationRepository(
        review_repository,
        content_root=content_root,
        seed_dir=seed_dir,
    )
    client = TestClient(
        create_app(
            SeedRepository.from_seed_dir(seed_dir),
            route_review_repository=review_repository,
            route_publication_repository=publication_repository,
        )
    )
    response = client.post(
        f"/editorial/routes/{ROUTE_ID}/publication",
        json={"revision_id": first.revision_id},
    )
    assert response.status_code == 409
    assert (
        json.loads((seed_dir / "events.json").read_text(encoding="utf-8"))["events"][0]["id"]
        == "event-two"
    )
    assert second.revision_id != first.revision_id


def test_publish_uses_the_bound_review_bundle_not_framing_files(tmp_path: Path) -> None:
    content_root = tmp_path / "content"
    seed_dir = tmp_path / "seed"
    write_publication_fixture(content_root, seed_dir)
    review_repository = RouteReviewRepository(content_root, seed_dir=seed_dir)
    review = review_repository.refresh(ROUTE_ID)
    route_dir = content_root / ROUTE_ID
    (route_dir / "event-framing.json").write_text(
        json.dumps({"events": [event("event-one", "place-one", "Wrong framing title")]}),
        encoding="utf-8",
    )
    (route_dir / "connection-framing.json").write_text(
        json.dumps({"connections": []}),
        encoding="utf-8",
    )
    publication_repository = RoutePublicationRepository(
        review_repository,
        content_root=content_root,
        seed_dir=seed_dir,
    )

    publication_repository.publish(ROUTE_ID, review.revision_id)

    events = json.loads((seed_dir / "events.json").read_text(encoding="utf-8"))["events"]
    connections = json.loads((seed_dir / "connections.json").read_text(encoding="utf-8"))[
        "connections"
    ]
    assert [item["title"] for item in events] == ["First event", "Second event"]
    assert connections == []


def test_publication_failure_restores_all_previous_files(tmp_path: Path, monkeypatch) -> None:
    content_root = tmp_path / "content"
    seed_dir = tmp_path / "seed"
    write_publication_fixture(content_root, seed_dir)
    review_repository = RouteReviewRepository(content_root, seed_dir=seed_dir)
    review = review_repository.refresh(ROUTE_ID)
    publication_repository = RoutePublicationRepository(
        review_repository,
        content_root=content_root,
        seed_dir=seed_dir,
    )
    paths = [seed_dir / name for name in ("places.json", "events.json", "connections.json")]
    original = {path: path.read_bytes() for path in paths}
    replace_calls = 0

    def fail_on_second_replace(source: Path, target: Path) -> None:
        nonlocal replace_calls
        replace_calls += 1
        if replace_calls == 2:
            raise OSError("simulated publication write failure")
        source.replace(target)

    monkeypatch.setattr("app.route_publication.os.replace", fail_on_second_replace)
    with pytest.raises(RoutePublicationError, match="previous route was preserved"):
        publication_repository.publish(ROUTE_ID, review.revision_id)

    assert {path: path.read_bytes() for path in paths} == original
    assert not (content_root / ROUTE_ID / "route-publication.json").exists()


def write_publication_fixture(content_root: Path, seed_dir: Path) -> None:
    route_dir = content_root / ROUTE_ID
    route_dir.mkdir(parents=True)
    seed_dir.mkdir()
    (route_dir / "pipeline.json").write_text(
        json.dumps(
            {
                "steps": {
                    "event_framing": {
                        "events": "event-framing.json",
                        "places": "place-framing.json",
                        "connections": "connection-framing.json",
                    }
                }
            }
        ),
        encoding="utf-8",
    )
    candidates = [candidate("event-one", "First event"), candidate("event-two", "Second event")]
    (route_dir / "event-list.json").write_text(
        json.dumps({"_meta": {"route_id": ROUTE_ID}, "candidates": candidates}),
        encoding="utf-8",
    )
    (route_dir / "complete-draft.json").write_text(
        json.dumps(
            {
                "_meta": {"route_id": ROUTE_ID},
                "candidates": candidates,
                "events": [
                    event("event-one", "place-one", "First event"),
                    event("event-two", "place-two", "Second event"),
                ],
                "places": [
                    {"decision": "reuse", "place_id": "place-one"},
                    {"decision": "reuse", "place_id": "place-two"},
                ],
                "connections": [connection()],
                "warnings": [],
            }
        ),
        encoding="utf-8",
    )
    (route_dir / "event-framing.json").write_text(
        json.dumps(
            {
                "events": [
                    event("event-one", "place-one", "First event"),
                    event("event-two", "place-two", "Second event"),
                ]
            }
        ),
        encoding="utf-8",
    )
    (route_dir / "place-framing.json").write_text(
        json.dumps(
            {
                "places": [
                    {"decision": "reuse", "place_id": "place-one"},
                    {"decision": "reuse", "place_id": "place-two"},
                ]
            }
        ),
        encoding="utf-8",
    )
    (route_dir / "connection-framing.json").write_text(
        json.dumps({"connections": []}), encoding="utf-8"
    )
    write_json(seed_dir / "routes.json", {"routes": [route()]})
    write_json(
        seed_dir / "places.json",
        {
            "_meta": {"schema_version": 2},
            "places": [place("place-one", "Place One"), place("place-two", "Place Two")],
            "place_notes": ["Keep place metadata."],
        },
    )
    write_json(
        seed_dir / "events.json",
        {
            "_meta": {"schema_version": 2},
            "events": [event("event-two", "place-two", "Old event")],
            "ignored_links": [
                {
                    "event_id": "event-two",
                    "kind": "media",
                    "values": ["https://example.org/ignored"],
                }
            ],
        },
    )
    write_json(
        seed_dir / "connections.json",
        {
            "_meta": {"schema_version": 1},
            "connections": [],
            "connection_notes": {"status": "preserve"},
        },
    )


def candidate(candidate_id: str, title: str) -> dict[str, object]:
    return {
        "candidate_id": candidate_id,
        "status": "keep",
        "review_state": "pending",
        "years": "1973",
        "place": "Place One",
        "working_title": title,
        "route_function": "Explain the route.",
    }


def event(event_id: str, place_id: str, title: str) -> dict[str, object]:
    return {
        "id": event_id,
        "route_id": ROUTE_ID,
        "place_id": place_id,
        "place_ids": [place_id],
        "default_place_id": place_id,
        "place_relationships": [],
        "title": title,
        "year_start": 1973,
        "year_end": 1973,
        "summary": "Summary",
        "significance": "Significance",
        "tags": [],
        "review_status": "draft",
        "source_urls": ["https://example.org/source"],
        "media_links": [],
        "image_links": [],
    }


def connection() -> dict[str, object]:
    return {
        "id": "event-one-to-event-two",
        "from_event_id": "event-one",
        "to_event_id": "event-two",
        "type": "influence",
        "summary": "The first event informs the second.",
        "review_status": "draft",
    }


def route() -> dict[str, object]:
    return {
        "id": ROUTE_ID,
        "title": "Review route",
        "color": "#000000",
        "creator": "SoundAtlas",
        "year_start": 1970,
        "year_end": 1980,
        "summary": "Summary",
        "thesis": "Thesis",
        "tags": [],
        "review_status": "draft",
        "source_urls": [],
    }


def place(place_id: str, name: str) -> dict[str, object]:
    return {
        "id": place_id,
        "name": name,
        "borough": "Bronx",
        "place_type": "venue",
        "latitude": 40.8,
        "longitude": -73.9,
        "summary": "Place",
        "review_status": "draft",
        "source_urls": [],
    }


def write_json(path: Path, value: object) -> None:
    path.write_text(json.dumps(value), encoding="utf-8")
