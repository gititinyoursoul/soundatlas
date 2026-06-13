import pytest
from pydantic import ValidationError

from app.schemas import Event, ImageLink, MediaLink


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
            "video_id": "example",
            "channel_title": "Example Channel",
            "description": "Example description",
            "published_at": "1977-08-11T00:00:00Z",
            "reason": "references the event title directly",
        },
    )

    assert media_link.provider == "youtube"
    assert media_link.type == "video"
    assert media_link.video_id == "example"


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
                "image_links": [],
            },
        )


def test_image_link_accepts_structured_provider_link() -> None:
    image_link = ImageLink.model_validate(
        {
            "provider": "wikimedia",
            "type": "venue_photo",
            "title": "Example venue photo",
            "image_url": "https://commons.wikimedia.org/example.jpg",
            "thumbnail_url": "https://commons.wikimedia.org/example-thumb.jpg",
            "source_url": "https://commons.wikimedia.org/wiki/File:Example.jpg",
            "creator": "Example creator",
            "license": "CC BY-SA 4.0",
            "license_url": "https://creativecommons.org/licenses/by-sa/4.0/",
            "rights_status": "open_license",
            "alt_text": "Example venue exterior.",
            "query": "example venue New York 1977",
            "confidence": 0.8,
            "review_status": "draft",
        },
    )

    assert image_link.provider == "wikimedia"
    assert image_link.type == "venue_photo"


@pytest.mark.parametrize(
    ("field", "value"),
    [
        ("provider", "google_images"),
        ("type", "screenshot"),
        ("rights_status", "copyrighted"),
        ("confidence", -0.1),
    ],
)
def test_image_link_rejects_invalid_values(field: str, value: object) -> None:
    payload = {
        "provider": "manual",
        "type": "archive_photo",
        "title": "Example archive photo",
        "image_url": "https://example.org/image.jpg",
        "source_url": "https://example.org/source",
        "rights_status": "unknown",
        "alt_text": "Example archive photo.",
        "query": "example archive photo",
        "confidence": 0.5,
        "review_status": "draft",
    }
    payload[field] = value

    with pytest.raises(ValidationError):
        ImageLink.model_validate(payload)


def test_event_rejects_legacy_string_image_links() -> None:
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
                "media_links": [],
                "image_links": ["https://example.org/image.jpg"],
            },
        )
