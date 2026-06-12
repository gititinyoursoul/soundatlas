import pytest
from pydantic import ValidationError

from app.schemas import Event, MediaLink


def test_media_link_accepts_structured_provider_link() -> None:
    media_link = MediaLink.model_validate(
        {
            "provider": "youtube",
            "type": "video",
            "title": "Example video",
            "url": "https://www.youtube.com/watch?v=example",
            "query": "example query",
            "confidence": 0.8,
            "review_status": "draft",
        },
    )

    assert media_link.provider == "youtube"
    assert media_link.type == "video"


@pytest.mark.parametrize(
    ("field", "value"),
    [
        ("provider", "bandcamp"),
        ("type", "article"),
        ("confidence", 1.2),
    ],
)
def test_media_link_rejects_invalid_values(field: str, value: object) -> None:
    payload = {
        "provider": "spotify",
        "type": "track",
        "title": "Example track",
        "url": "https://open.spotify.com/track/example",
        "query": "example query",
        "confidence": 0.8,
        "review_status": "draft",
    }
    payload[field] = value

    with pytest.raises(ValidationError):
        MediaLink.model_validate(payload)


def test_event_rejects_legacy_string_media_links() -> None:
    with pytest.raises(ValidationError):
        Event.model_validate(
            {
                "id": "example-event",
                "route_id": "example-route",
                "place_id": "example-place",
                "title": "Example Event",
                "year_start": 1970,
                "year_end": 1970,
                "summary": "Example summary.",
                "significance": "Example significance.",
                "tags": [],
                "review_status": "draft",
                "source_urls": [],
                "media_links": ["https://www.youtube.com/watch?v=example"],
            },
        )
