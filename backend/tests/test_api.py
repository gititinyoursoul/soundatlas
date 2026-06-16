from fastapi.testclient import TestClient

from app.main import app, create_app
from app.seed_repository import SeedRepository


client = TestClient(app)


def test_health_returns_ok() -> None:
    response = client.get("/health")

    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_events_can_be_filtered_by_route_and_year_range() -> None:
    response = client.get(
        "/events",
        params={
            "route_id": "birth-of-hip-hop",
            "from_year": 1973,
            "to_year": 1977,
        },
    )

    assert response.status_code == 200
    event_ids = {event["id"] for event in response.json()}
    assert "kool-herc-back-to-school-jam" in event_ids
    assert "nyc-blackout-1977" in event_ids
    assert "wild-style-global-visibility" not in event_ids


def test_unknown_event_returns_404() -> None:
    response = client.get("/events/unknown-event")

    assert response.status_code == 404
    assert response.json() == {"detail": "Event 'unknown-event' not found"}


def test_unknown_route_filter_returns_404() -> None:
    response = client.get("/events", params={"route_id": "unknown-route"})

    assert response.status_code == 404
    assert response.json() == {"detail": "Route 'unknown-route' not found"}


def test_invalid_year_range_returns_400() -> None:
    response = client.get(
        "/events",
        params={
            "from_year": 1985,
            "to_year": 1970,
        },
    )

    assert response.status_code == 400
    assert response.json() == {
        "detail": "from_year must be less than or equal to to_year",
    }


def test_media_link_can_be_marked_reviewed(tmp_path) -> None:
    write_review_seed_files(tmp_path)
    review_client = TestClient(create_app(SeedRepository.from_seed_dir(tmp_path)))

    response = review_client.patch(
        "/events/review-event/media-links",
        json={
            "url": "https://www.youtube.com/watch?v=draft",
            "action": "reviewed",
        },
    )

    assert response.status_code == 200
    media_link = response.json()["media_links"][0]
    assert media_link["review_status"] == "reviewed"
    assert "reviewed" in (tmp_path / "events.json").read_text(encoding="utf-8")


def test_media_link_can_be_rejected(tmp_path) -> None:
    write_review_seed_files(tmp_path)
    review_client = TestClient(create_app(SeedRepository.from_seed_dir(tmp_path)))

    response = review_client.patch(
        "/events/review-event/media-links",
        json={
            "url": "https://www.youtube.com/watch?v=draft",
            "action": "reject",
        },
    )

    assert response.status_code == 200
    assert response.json()["media_links"] == []
    assert "watch?v=draft" not in (tmp_path / "events.json").read_text(
        encoding="utf-8",
    )


def write_review_seed_files(seed_dir) -> None:
    (seed_dir / "routes.json").write_text(
        """
{
  "routes": [
    {
      "id": "review-route",
      "title": "Review Route",
      "color": "#000000",
      "creator": "test",
      "year_start": 1970,
      "year_end": 1970,
      "summary": "Route summary",
      "thesis": "Route thesis",
      "tags": [],
      "review_status": "draft",
      "source_urls": []
    }
  ]
}
""",
        encoding="utf-8",
    )
    (seed_dir / "places.json").write_text(
        """
{
  "places": [
    {
      "id": "review-place",
      "name": "Review Place",
      "borough": "Bronx",
      "place_type": "venue",
      "latitude": 40.0,
      "longitude": -73.0,
      "summary": "Place summary",
      "review_status": "draft",
      "source_urls": []
    }
  ]
}
""",
        encoding="utf-8",
    )
    (seed_dir / "events.json").write_text(
        """
{
  "events": [
    {
      "id": "review-event",
      "route_id": "review-route",
      "place_id": "review-place",
      "title": "Review Event",
      "year_start": 1970,
      "year_end": 1970,
      "summary": "Event summary",
      "significance": "Event significance",
      "tags": [],
      "review_status": "draft",
      "source_urls": [],
      "media_links": [
        {
          "provider": "youtube",
          "type": "video",
          "title": "Draft Video",
          "url": "https://www.youtube.com/watch?v=draft",
          "query": "draft query",
          "confidence": 0.5,
          "review_status": "draft"
        }
      ],
      "image_links": []
    }
  ]
}
""",
        encoding="utf-8",
    )
    (seed_dir / "connections.json").write_text(
        """
{
  "connections": []
}
""",
        encoding="utf-8",
    )
