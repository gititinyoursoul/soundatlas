import base64
import json
import urllib.error
import urllib.parse
import urllib.request
from typing import Any, Protocol

from app.media_enrichment.models import (
    ContentAnalysis,
    ContentPage,
    MediaLinkCandidate,
    YouTubeVideo,
    dedupe_preserving_order,
    normalize_terms,
)
from app.media_enrichment.settings import MediaEnrichmentSettings


class MediaProviderError(RuntimeError):
    pass


class LLMTransport(Protocol):
    def complete_json(
        self,
        *,
        api_key: str,
        model: str,
        system_prompt: str,
        user_prompt: str,
    ) -> dict[str, Any]: ...


class ContentAnalyzer(Protocol):
    def analyze(self, content_page: ContentPage) -> ContentAnalysis: ...


class YouTubeSearchService(Protocol):
    def search(self, query: str, limit: int) -> list[YouTubeVideo]: ...


class AuxiliaryProvider(Protocol):
    name: str

    def search(self, query: str) -> list[MediaLinkCandidate]: ...


GENRE_HINTS = {
    "hip hop": {"hip", "hop", "bronx", "dj", "mc", "breakbeat", "b-boy", "b-girl"},
    "disco": {"disco", "dance", "club", "garage", "nightlife", "dj"},
    "punk": {"punk", "cbgb", "downtown", "guitar", "new", "wave"},
    "salsa": {"salsa", "latin", "fania", "barrio", "afro", "caribbean"},
    "jazz": {"jazz", "loft", "improv", "improvisation", "ensemble"},
}

MOOD_HINTS = {
    "urgent": {"protest", "raw", "rebellion", "punk", "blackout"},
    "celebratory": {"party", "dance", "celebration", "club", "jam"},
    "experimental": {"experimental", "avant", "no", "wave", "loft"},
    "community-driven": {"community", "youth", "block", "neighborhood", "bronx"},
}


class HeuristicContentAnalyzer:
    def analyze(self, content_page: ContentPage) -> ContentAnalysis:
        keyword_pool = dedupe_preserving_order(
            [
                *content_page.tags,
                *sorted(
                    normalize_terms(
                        " ".join(
                            [
                                content_page.title,
                                content_page.route_title,
                                content_page.summary,
                                content_page.text,
                            ],
                        ),
                    ),
                ),
            ],
        )
        keywords = keyword_pool[:8]
        genres = detect_music_genres(keyword_pool, content_page)
        years = build_year_phrase(content_page.year_start, content_page.year_end)
        search_queries = dedupe_preserving_order(
            [
                " ".join(
                    part
                    for part in [content_page.title, content_page.route_title, years]
                    if part
                ).strip(),
                " ".join(
                    part
                    for part in [
                        content_page.title,
                        genres[0] if genres else "",
                        years,
                        "song",
                    ]
                    if part
                ).strip(),
                " ".join(
                    part
                    for part in [
                        genres[0] if genres else "",
                        "New York",
                        years,
                        "documentary",
                    ]
                    if part
                ).strip(),
            ],
        )
        return ContentAnalysis(
            topic=content_page.title,
            mood=detect_mood(keyword_pool),
            audience="music history explorers",
            keywords=keywords,
            music_genres=genres,
            search_queries=search_queries[:3],
            notes=(
                "Heuristic fallback generated queries from title, route, years and"
                " stable content keywords."
            ),
        )


class OpenAIContentAnalyzer:
    def __init__(
        self,
        api_key: str,
        model: str,
        transport: LLMTransport,
    ) -> None:
        self.api_key = api_key
        self.model = model
        self.transport = transport

    def analyze(self, content_page: ContentPage) -> ContentAnalysis:
        payload = self.transport.complete_json(
            api_key=self.api_key,
            model=self.model,
            system_prompt=(
                "You analyze a music-history content page and respond with strict JSON."
                " Never include secrets or API keys."
            ),
            user_prompt=json.dumps(
                {
                    "content_page": {
                        "id": content_page.identifier,
                        "title": content_page.title,
                        "route_title": content_page.route_title,
                        "summary": content_page.summary,
                        "text": content_page.text,
                        "tags": list(content_page.tags),
                        "year_start": content_page.year_start,
                        "year_end": content_page.year_end,
                        "url": content_page.url,
                    },
                    "response_schema": {
                        "topic": "string",
                        "mood": "string",
                        "audience": "string",
                        "keywords": ["string"],
                        "music_genres": ["string"],
                        "search_queries": ["string"],
                        "notes": "string",
                    },
                },
                ensure_ascii=False,
            ),
        )
        return ContentAnalysis(
            topic=str(payload.get("topic") or content_page.title),
            mood=str(payload.get("mood") or "documentary"),
            audience=str(payload.get("audience") or "music history explorers"),
            keywords=_coerce_string_list(payload.get("keywords")),
            music_genres=_coerce_string_list(payload.get("music_genres")),
            search_queries=_coerce_string_list(payload.get("search_queries")),
            notes=str(payload.get("notes") or "Generated by OpenAI-compatible analyzer."),
        )


class YouTubeDataApiSearchService:
    def __init__(self, api_key: str, requester: Any | None = None) -> None:
        self.api_key = api_key
        self.requester = requester or request_json

    def search(self, query: str, limit: int) -> list[YouTubeVideo]:
        payload = self.requester(
            "https://www.googleapis.com/youtube/v3/search",
            {
                "part": "snippet",
                "type": "video",
                "maxResults": str(limit),
                "q": query,
                "key": self.api_key,
            },
        )
        videos: list[YouTubeVideo] = []
        for item in payload.get("items", []):
            video_id = item.get("id", {}).get("videoId")
            snippet = item.get("snippet", {})
            title = snippet.get("title")
            if not video_id or not title:
                continue
            videos.append(
                YouTubeVideo(
                    title=title,
                    channel_title=snippet.get("channelTitle", ""),
                    video_id=video_id,
                    url=f"https://www.youtube.com/watch?v={video_id}",
                    description=snippet.get("description", ""),
                    published_at=snippet.get("publishedAt"),
                    matched_query=query,
                ),
            )
        return videos


class StaticYouTubeSearchService:
    def __init__(self, results_by_query: dict[str, list[YouTubeVideo]] | None = None) -> None:
        self.results_by_query = results_by_query or {}

    def search(self, query: str, limit: int) -> list[YouTubeVideo]:
        return [
            YouTubeVideo(
                title=video.title,
                channel_title=video.channel_title,
                video_id=video.video_id,
                url=video.url,
                description=video.description,
                published_at=video.published_at,
                matched_query=video.matched_query or query,
            )
            for video in self.results_by_query.get(query, [])[:limit]
        ]


class SpotifyProvider:
    name = "spotify"

    def __init__(
        self,
        client_id: str,
        client_secret: str,
        limit: int,
        requester: Any | None = None,
    ) -> None:
        self.client_id = client_id
        self.client_secret = client_secret
        self.limit = limit
        self.requester = requester or request_json
        self.token: str | None = None

    def search(self, query: str) -> list[MediaLinkCandidate]:
        token = self.get_token()
        payload = self.requester(
            "https://api.spotify.com/v1/search",
            {
                "q": query,
                "type": "track,album,playlist",
                "limit": str(self.limit),
            },
            headers={"Authorization": f"Bearer {token}"},
        )
        links: list[MediaLinkCandidate] = []
        for media_type, collection_key in [
            ("track", "tracks"),
            ("album", "albums"),
            ("playlist", "playlists"),
        ]:
            for item in payload.get(collection_key, {}).get("items", []):
                title = item.get("name")
                url = item.get("external_urls", {}).get("spotify")
                if title and url:
                    links.append(
                        make_media_link(
                            provider="spotify",
                            media_type=media_type,
                            title=title,
                            url=url,
                            query=query,
                        ),
                    )
        return links[: self.limit]

    def get_token(self) -> str:
        if self.token:
            return self.token

        credentials = f"{self.client_id}:{self.client_secret}".encode("utf-8")
        auth = base64.b64encode(credentials).decode("ascii")
        payload = self.requester(
            "https://accounts.spotify.com/api/token",
            method="POST",
            body=urllib.parse.urlencode({"grant_type": "client_credentials"}).encode(
                "utf-8",
            ),
            headers={
                "Authorization": f"Basic {auth}",
                "Content-Type": "application/x-www-form-urlencoded",
            },
        )
        token = payload.get("access_token")
        if not token:
            raise MediaProviderError("Spotify did not return an access token.")
        self.token = token
        return token


class QobuzProvider:
    name = "qobuz"

    def __init__(
        self,
        app_id: str,
        user_auth_token: str,
        limit: int,
        requester: Any | None = None,
    ) -> None:
        self.app_id = app_id
        self.user_auth_token = user_auth_token
        self.limit = limit
        self.requester = requester or request_json

    def search(self, query: str) -> list[MediaLinkCandidate]:
        payload = self.requester(
            "https://www.qobuz.com/api.json/0.2/catalog/search",
            {
                "app_id": self.app_id,
                "user_auth_token": self.user_auth_token,
                "query": query,
                "limit": str(self.limit),
            },
        )
        links: list[MediaLinkCandidate] = []
        for media_type, collection_key in [
            ("track", "tracks"),
            ("album", "albums"),
            ("playlist", "playlists"),
        ]:
            for item in payload.get(collection_key, {}).get("items", []):
                title = item.get("title") or item.get("name")
                item_id = item.get("id")
                url = item.get("url") or build_qobuz_url(media_type, item_id)
                if title and url:
                    links.append(
                        make_media_link(
                            provider="qobuz",
                            media_type=media_type,
                            title=title,
                            url=url,
                            query=query,
                        ),
                    )
        return links[: self.limit]


def build_auxiliary_providers(
    settings: MediaEnrichmentSettings,
    limit: int,
    requester: Any | None = None,
) -> list[AuxiliaryProvider]:
    providers: list[AuxiliaryProvider] = []
    if settings.has_live_spotify_credentials:
        providers.append(
            SpotifyProvider(
                settings.spotify_client_id or "",
                settings.spotify_client_secret or "",
                limit,
                requester=requester,
            ),
        )
    if settings.has_live_qobuz_credentials:
        providers.append(
            QobuzProvider(
                settings.qobuz_app_id or "",
                settings.qobuz_user_auth_token or "",
                limit,
                requester=requester,
            ),
        )
    return providers


def make_media_link(
    provider: str,
    media_type: str,
    title: str,
    url: str,
    query: str,
) -> MediaLinkCandidate:
    return MediaLinkCandidate(
        provider=provider,
        media_type=media_type,
        title=title,
        url=url,
        query=query,
        confidence=score_confidence(query, title),
    )


def detect_music_genres(keyword_pool: list[str], content_page: ContentPage) -> list[str]:
    normalized_terms = {
        term.casefold() for term in keyword_pool if isinstance(term, str)
    } | normalize_terms(" ".join([content_page.title, content_page.route_title]))
    matches: list[str] = []
    for genre, hints in GENRE_HINTS.items():
        if normalized_terms & hints:
            matches.append(genre)
    if not matches:
        matches.append("music history")
    return matches


def detect_mood(keyword_pool: list[str]) -> str:
    normalized_terms = {term.casefold() for term in keyword_pool}
    for mood, hints in MOOD_HINTS.items():
        if normalized_terms & hints:
            return mood
    return "documentary"


def build_year_phrase(year_start: int | None, year_end: int | None) -> str:
    if year_start is None and year_end is None:
        return ""
    if year_start == year_end or year_end is None:
        return str(year_start)
    if year_start is None:
        return str(year_end)
    return f"{year_start} {year_end}"


def score_confidence(query: str, title: str) -> float:
    query_terms = normalize_terms(query)
    title_terms = normalize_terms(title)
    if not query_terms or not title_terms:
        return 0.25
    overlap = len(query_terms & title_terms)
    score = 0.35 + min(overlap / max(len(title_terms), 1), 1) * 0.6
    return round(min(score, 0.95), 2)


def build_qobuz_url(media_type: str, item_id: Any) -> str | None:
    if not item_id:
        return None
    if media_type == "track":
        return f"https://play.qobuz.com/track/{item_id}"
    if media_type == "album":
        return f"https://play.qobuz.com/album/{item_id}"
    if media_type == "playlist":
        return f"https://play.qobuz.com/playlist/{item_id}"
    return None


def _coerce_string_list(value: Any) -> list[str]:
    if not isinstance(value, list):
        return []
    return [str(item).strip() for item in value if str(item).strip()]


def request_json(
    url: str,
    params: dict[str, str] | None = None,
    method: str = "GET",
    body: bytes | None = None,
    headers: dict[str, str] | None = None,
) -> dict[str, Any]:
    if params:
        url = f"{url}?{urllib.parse.urlencode(params)}"
    request = urllib.request.Request(
        url,
        data=body,
        headers=headers or {},
        method=method,
    )
    try:
        with urllib.request.urlopen(request, timeout=30) as response:
            return json.loads(response.read().decode("utf-8"))
    except urllib.error.HTTPError as exc:
        detail = exc.read().decode("utf-8", errors="replace")
        raise MediaProviderError(f"HTTP {exc.code}: {detail}") from exc
    except urllib.error.URLError as exc:
        raise MediaProviderError(str(exc.reason)) from exc
