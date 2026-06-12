import argparse
import base64
import json
import os
import sys
import urllib.error
import urllib.parse
import urllib.request
from pathlib import Path
from typing import Any


REPO_ROOT = Path(__file__).resolve().parents[2]
SEED_DIR = REPO_ROOT / "data" / "seed"
EVENTS_PATH = SEED_DIR / "events.json"
ROUTES_PATH = SEED_DIR / "routes.json"
MEDIA_REVIEW_STATUS = "draft"


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Enrich SoundAtlas events with provider media links.",
    )
    parser.add_argument("--event-id", help="Only enrich one event.")
    parser.add_argument("--limit", type=int, default=3, help="Candidates per provider.")
    parser.add_argument("--dry-run", action="store_true", help="Print changes without writing.")
    args = parser.parse_args()

    routes_payload = read_json(ROUTES_PATH)
    events_payload = read_json(EVENTS_PATH)
    route_title_by_id = {
        route["id"]: route["title"] for route in routes_payload.get("routes", [])
    }
    providers = build_providers(args.limit)

    if not providers:
        print("No provider credentials found. Nothing to enrich.", file=sys.stderr)
        return 2

    changed_events = 0
    for event in events_payload.get("events", []):
        if args.event_id and event["id"] != args.event_id:
            continue

        route_title = route_title_by_id.get(event["route_id"], "")
        query = build_query(event, route_title)
        candidates = []

        for provider in providers:
            try:
                candidates.extend(provider.search(query))
            except MediaProviderError as exc:
                print(f"{provider.name}: {exc}", file=sys.stderr)

        if not candidates:
            continue

        existing_links = event.get("media_links", [])
        merged_links = merge_media_links(existing_links, candidates)
        if merged_links != existing_links:
            event["media_links"] = merged_links
            changed_events += 1

    if args.dry_run:
        print(json.dumps(events_payload, indent=2, ensure_ascii=False))
    elif changed_events:
        EVENTS_PATH.write_text(
            json.dumps(events_payload, indent=2, ensure_ascii=False) + "\n",
            encoding="utf-8",
        )

    print(f"Enriched {changed_events} event(s).")
    return 0


def read_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def build_query(event: dict[str, Any], route_title: str) -> str:
    years = (
        str(event["year_start"])
        if event["year_start"] == event["year_end"]
        else f'{event["year_start"]} {event["year_end"]}'
    )
    terms = [
        event["title"],
        route_title,
        years,
        " ".join(event.get("tags", [])[:5]),
        "music",
    ]
    return " ".join(term for term in terms if term).strip()


def merge_media_links(
    existing_links: list[dict[str, Any]],
    candidates: list[dict[str, Any]],
) -> list[dict[str, Any]]:
    links_by_url = {
        link["url"]: link
        for link in existing_links
        if isinstance(link, dict) and isinstance(link.get("url"), str)
    }

    for candidate in candidates:
        links_by_url.setdefault(candidate["url"], candidate)

    return sorted(
        links_by_url.values(),
        key=lambda link: (link["provider"], link["type"], -float(link["confidence"])),
    )


def build_providers(limit: int) -> list["Provider"]:
    providers: list[Provider] = []

    youtube_api_key = os.getenv("YOUTUBE_API_KEY")
    if youtube_api_key:
        providers.append(YouTubeProvider(youtube_api_key, limit))

    spotify_client_id = os.getenv("SPOTIFY_CLIENT_ID")
    spotify_client_secret = os.getenv("SPOTIFY_CLIENT_SECRET")
    if spotify_client_id and spotify_client_secret:
        providers.append(
            SpotifyProvider(spotify_client_id, spotify_client_secret, limit),
        )

    qobuz_app_id = os.getenv("QOBUZ_APP_ID")
    qobuz_user_auth_token = os.getenv("QOBUZ_USER_AUTH_TOKEN")
    if qobuz_app_id and qobuz_user_auth_token:
        providers.append(QobuzProvider(qobuz_app_id, qobuz_user_auth_token, limit))

    return providers


class MediaProviderError(RuntimeError):
    pass


class Provider:
    name: str

    def __init__(self, limit: int) -> None:
        self.limit = limit

    def search(self, query: str) -> list[dict[str, Any]]:
        raise NotImplementedError


class YouTubeProvider(Provider):
    name = "youtube"

    def __init__(self, api_key: str, limit: int) -> None:
        super().__init__(limit)
        self.api_key = api_key

    def search(self, query: str) -> list[dict[str, Any]]:
        payload = request_json(
            "https://www.googleapis.com/youtube/v3/search",
            {
                "part": "snippet",
                "type": "video",
                "maxResults": str(self.limit),
                "q": query,
                "key": self.api_key,
            },
        )
        links = []
        for item in payload.get("items", []):
            video_id = item.get("id", {}).get("videoId")
            title = item.get("snippet", {}).get("title")
            if not video_id or not title:
                continue
            links.append(
                make_media_link(
                    provider="youtube",
                    media_type="video",
                    title=title,
                    url=f"https://www.youtube.com/watch?v={video_id}",
                    query=query,
                ),
            )
        return links


class SpotifyProvider(Provider):
    name = "spotify"

    def __init__(self, client_id: str, client_secret: str, limit: int) -> None:
        super().__init__(limit)
        self.client_id = client_id
        self.client_secret = client_secret
        self.token: str | None = None

    def search(self, query: str) -> list[dict[str, Any]]:
        token = self.get_token()
        payload = request_json(
            "https://api.spotify.com/v1/search",
            {
                "q": query,
                "type": "track,album,playlist",
                "limit": str(self.limit),
            },
            headers={"Authorization": f"Bearer {token}"},
        )
        links = []
        for media_type, collection_key in [
            ("track", "tracks"),
            ("album", "albums"),
            ("playlist", "playlists"),
        ]:
            for item in payload.get(collection_key, {}).get("items", []):
                if not item:
                    continue
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
        payload = request_json(
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


class QobuzProvider(Provider):
    name = "qobuz"

    def __init__(self, app_id: str, user_auth_token: str, limit: int) -> None:
        super().__init__(limit)
        self.app_id = app_id
        self.user_auth_token = user_auth_token

    def search(self, query: str) -> list[dict[str, Any]]:
        payload = request_json(
            "https://www.qobuz.com/api.json/0.2/catalog/search",
            {
                "app_id": self.app_id,
                "user_auth_token": self.user_auth_token,
                "query": query,
                "limit": str(self.limit),
            },
        )
        links = []
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


def make_media_link(
    provider: str,
    media_type: str,
    title: str,
    url: str,
    query: str,
) -> dict[str, Any]:
    return {
        "provider": provider,
        "type": media_type,
        "title": title,
        "url": url,
        "query": query,
        "confidence": score_confidence(query, title),
        "review_status": MEDIA_REVIEW_STATUS,
    }


def score_confidence(query: str, title: str) -> float:
    query_terms = normalize_terms(query)
    title_terms = normalize_terms(title)
    if not query_terms or not title_terms:
        return 0.25
    overlap = len(query_terms & title_terms)
    score = 0.35 + min(overlap / max(len(title_terms), 1), 1) * 0.6
    return round(min(score, 0.95), 2)


def normalize_terms(value: str) -> set[str]:
    return {
        term
        for term in "".join(
            character.lower() if character.isalnum() else " " for character in value
        ).split()
        if len(term) > 2
    }


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


if __name__ == "__main__":
    raise SystemExit(main())
