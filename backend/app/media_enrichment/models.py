from dataclasses import dataclass, field
from typing import Any


@dataclass(slots=True)
class ContentPage:
    identifier: str
    title: str
    text: str
    route_title: str = ""
    summary: str = ""
    url: str | None = None
    tags: tuple[str, ...] = ()
    year_start: int | None = None
    year_end: int | None = None


@dataclass(slots=True)
class ContentAnalysis:
    topic: str
    mood: str
    audience: str
    keywords: list[str]
    music_genres: list[str]
    search_queries: list[str]
    notes: str


@dataclass(slots=True)
class YouTubeVideo:
    title: str
    channel_title: str
    video_id: str
    url: str
    description: str = ""
    published_at: str | None = None
    matched_query: str = ""


@dataclass(slots=True)
class RankedYouTubeVideo:
    video: YouTubeVideo
    score: float
    reason: str


@dataclass(slots=True)
class MediaLinkCandidate:
    provider: str
    media_type: str
    title: str
    url: str
    query: str
    confidence: float
    review_status: str = "draft"
    video_id: str | None = None
    channel_title: str | None = None
    description: str | None = None
    published_at: str | None = None
    reason: str | None = None

    def to_payload(self) -> dict[str, Any]:
        payload = {
            "provider": self.provider,
            "type": self.media_type,
            "title": self.title,
            "url": self.url,
            "query": self.query,
            "confidence": self.confidence,
            "review_status": self.review_status,
        }
        optional_fields = {
            "video_id": self.video_id,
            "channel_title": self.channel_title,
            "description": self.description,
            "published_at": self.published_at,
            "reason": self.reason,
        }
        payload.update(
            {
                key: value
                for key, value in optional_fields.items()
                if value not in (None, "")
            },
        )
        return payload


def normalize_terms(value: str) -> set[str]:
    return {
        term
        for term in "".join(
            character.lower() if character.isalnum() else " " for character in value
        ).split()
        if len(term) > 2
    }


def dedupe_preserving_order(values: list[str]) -> list[str]:
    seen: set[str] = set()
    deduped: list[str] = []
    for value in values:
        normalized = value.strip()
        if not normalized:
            continue
        key = normalized.casefold()
        if key in seen:
            continue
        seen.add(key)
        deduped.append(normalized)
    return deduped
