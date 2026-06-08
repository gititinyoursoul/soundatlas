from fastapi.testclient import TestClient

from app.main import app


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
