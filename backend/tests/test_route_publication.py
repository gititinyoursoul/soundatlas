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
    review_repository = RouteReviewRepository(content_root)
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
    events = json.loads((seed_dir / "events.json").read_text(encoding="utf-8"))["events"]
    assert [event["id"] for event in events] == ["event-one"]
    assert json.loads(
        (content_root / ROUTE_ID / "route-publication.json").read_text(encoding="utf-8")
    )["revision_id"] == review.revision_id


def test_publication_rejects_stale_revision_without_writing(tmp_path: Path) -> None:
    content_root = tmp_path / "content"
    seed_dir = tmp_path / "seed"
    write_publication_fixture(content_root, seed_dir)
    review_repository = RouteReviewRepository(content_root)
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
    assert json.loads((seed_dir / "events.json").read_text(encoding="utf-8"))["events"][0]["id"] == "event-two"
    assert second.revision_id != first.revision_id


def test_publication_failure_restores_all_previous_files(tmp_path: Path, monkeypatch) -> None:
    content_root = tmp_path / "content"
    seed_dir = tmp_path / "seed"
    write_publication_fixture(content_root, seed_dir)
    review_repository = RouteReviewRepository(content_root)
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
    (route_dir / "connection-framing.json").write_text(json.dumps({"connections": []}), encoding="utf-8")
    write_json(seed_dir / "routes.json", {"routes": [route()]})
    write_json(
        seed_dir / "places.json",
        {"places": [place("place-one", "Place One"), place("place-two", "Place Two")]},
    )
    write_json(seed_dir / "events.json", {"events": [event("event-two", "place-two", "Old event")]})
    write_json(seed_dir / "connections.json", {"connections": []})


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
        "source_urls": [],
        "media_links": [],
        "image_links": [],
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
