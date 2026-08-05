import json
import os
from pathlib import Path

import pytest
from fastapi.testclient import TestClient

from app.main import create_app
from app.route_review import (
    RouteReviewConflictError,
    RouteReviewError,
    RouteReviewRepository,
    RouteReviewStateUpdate,
)
from app.seed_repository import SeedRepository

ROUTE_ID = "review-route"


def test_refresh_defaults_to_draft_and_preserves_agent_recommendation(tmp_path: Path) -> None:
    repository = write_review_fixture(tmp_path)
    event_list_path = tmp_path / ROUTE_ID / "event-list.json"
    payload = json.loads(event_list_path.read_text(encoding="utf-8"))
    payload["warnings"] = ["Route chronology needs review."]
    event_list_path.write_text(json.dumps(payload), encoding="utf-8")

    result = repository.refresh(ROUTE_ID)

    assert result.proposals[0].editorial_state == "draft"
    assert result.proposals[0].included is True
    assert result.proposals[0].agent_recommendation == "reject"
    assert result.proposals[0].warnings == ["Check the date."]
    assert result.warnings == ["Route chronology needs review."]
    assert result.technical_ready is True
    assert (tmp_path / ROUTE_ID / "route-review.json").exists()


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
    assert result.proposals[0].technical_errors == ["Missing place ('place')"]
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
    (tmp_path / ROUTE_ID / "event-list.json").write_text("not json", encoding="utf-8")

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
    assert result.proposals[0].agent_recommendation == "reject"
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


def write_review_fixture(
    content_root: Path,
    *,
    include_second: bool = False,
) -> RouteReviewRepository:
    candidates = [candidate("event-one", status="reject")]
    if include_second:
        candidates.append(candidate("event-two", status="keep"))
    write_event_list(content_root, candidates)
    return RouteReviewRepository(content_root)


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
