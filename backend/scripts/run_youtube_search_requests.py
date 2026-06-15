import argparse
import json
import sys
import urllib.parse
from pathlib import Path
from typing import Any

BACKEND_ROOT = Path(__file__).resolve().parents[1]
if str(BACKEND_ROOT) not in sys.path:
    sys.path.insert(0, str(BACKEND_ROOT))

from app.media_enrichment.services import MediaProviderError, request_json
from app.media_enrichment.settings import MediaEnrichmentSettings


REPO_ROOT = Path(__file__).resolve().parents[2]
DEFAULT_REQUEST_DIR = REPO_ROOT / "data" / "enrichment" / "youtube-search-requests"
DEFAULT_OUTPUT_DIR = REPO_ROOT / "data" / "enrichment" / "youtube-search-results"
YOUTUBE_SEARCH_URL = "https://www.googleapis.com/youtube/v3/search"
API_KEY_PLACEHOLDER = "YOUTUBE_API_KEY"
SUPPORTED_YOUTUBE_INTENTS = {
    "song",
    "interview",
    "documentary",
    "playlist",
    "dj_mix",
    "venue_context",
    "historical_context",
}
SUPPORTED_YOUTUBE_TYPES = {"video", "playlist"}
SUPPORTED_CONFIDENCE_HINTS = {"high", "medium", "low"}


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Run curated YouTube search.list request plans.",
    )
    parser.add_argument("--event-id", help="Only run request plans for one event.")
    parser.add_argument(
        "--request-dir",
        type=Path,
        default=DEFAULT_REQUEST_DIR,
        help="Directory containing YouTube request-plan JSON files.",
    )
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=DEFAULT_OUTPUT_DIR,
        help="Directory for normalized YouTube search results.",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Print planned requests without calling the YouTube API.",
    )
    args = parser.parse_args()

    try:
        settings = MediaEnrichmentSettings.from_env()
    except ValueError as exc:
        print(str(exc), file=sys.stderr)
        return 2

    if not args.dry_run and not settings.has_live_youtube_credentials:
        print(
            "No live YouTube credentials found. Set SOUNDATLAS_ENV_FILE with "
            "YOUTUBE_API_KEY and SOUNDATLAS_USE_DUMMY_SERVICES=false.",
            file=sys.stderr,
        )
        return 2

    request_plans = load_request_plans(args.request_dir, event_id=args.event_id)
    if not request_plans:
        print("No YouTube request plans found.", file=sys.stderr)
        return 2

    if args.dry_run:
        print(
            json.dumps(
                [
                    build_dry_run_summary(request_plan)
                    for request_plan in request_plans
                ],
                indent=2,
                ensure_ascii=False,
            ),
        )
        return 0

    args.output_dir.mkdir(parents=True, exist_ok=True)
    for request_plan in request_plans:
        result_payload = run_request_plan(
            request_plan,
            api_key=settings.youtube_api_key or "",
        )
        output_path = args.output_dir / f"{request_plan['event_id']}.json"
        output_path.write_text(
            json.dumps(result_payload, indent=2, ensure_ascii=False) + "\n",
            encoding="utf-8",
        )
        print(output_path.relative_to(REPO_ROOT))

    return 0


def load_request_plans(
    request_dir: Path,
    event_id: str | None = None,
) -> list[dict[str, Any]]:
    if not request_dir.exists():
        return []

    request_paths = sorted(request_dir.glob("*.json"))
    request_plans: list[dict[str, Any]] = []
    for request_path in request_paths:
        request_plan = read_json(request_path)
        if event_id and request_plan.get("event_id") != event_id:
            continue
        validate_request_plan(request_plan, request_path)
        request_plans.append(request_plan)
    return request_plans


def read_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def validate_request_plan(request_plan: dict[str, Any], path: Path) -> None:
    event_id = request_plan.get("event_id")
    candidates = request_plan.get("query_candidates")
    if not isinstance(event_id, str) or not event_id:
        raise ValueError(f"{path} must contain a non-empty event_id.")
    if not isinstance(candidates, list) or not candidates:
        raise ValueError(f"{path} must contain query_candidates.")

    for index, candidate in enumerate(candidates):
        intent = candidate.get("intent")
        if intent not in SUPPORTED_YOUTUBE_INTENTS:
            raise ValueError(f"{path} candidate {index} has unsupported intent.")

        youtube_type = candidate.get("youtube_type")
        if youtube_type not in SUPPORTED_YOUTUBE_TYPES:
            raise ValueError(f"{path} candidate {index} has unsupported youtube_type.")

        query = candidate.get("q")
        if not isinstance(query, str) or not query.strip():
            raise ValueError(f"{path} candidate {index} must contain a non-empty q.")

        confidence_hint = candidate.get("confidence_hint")
        if confidence_hint not in SUPPORTED_CONFIDENCE_HINTS:
            raise ValueError(f"{path} candidate {index} has unsupported confidence_hint.")

        for priority_field in ["priority", "review_priority"]:
            priority = candidate.get(priority_field)
            if not isinstance(priority, int) or priority < 1:
                raise ValueError(
                    f"{path} candidate {index} must contain a positive {priority_field}.",
                )

        params = candidate.get("request_params")
        if not isinstance(params, dict):
            raise ValueError(f"{path} candidate {index} must contain request_params.")
        if params.get("part") != "snippet":
            raise ValueError(f"{path} candidate {index} must use part=snippet.")
        if params.get("type") != youtube_type:
            raise ValueError(
                f"{path} candidate {index} request_params.type must match youtube_type.",
            )
        if params.get("q") != query:
            raise ValueError(
                f"{path} candidate {index} request_params.q must match q.",
            )
        if params.get("key") != API_KEY_PLACEHOLDER:
            raise ValueError(
                f"{path} candidate {index} must use {API_KEY_PLACEHOLDER} as key.",
            )


def build_dry_run_summary(request_plan: dict[str, Any]) -> dict[str, Any]:
    return {
        "event_id": request_plan["event_id"],
        "requests": [
            {
                "intent": candidate.get("intent"),
                "youtube_type": candidate.get("youtube_type"),
                "q": candidate.get("q"),
                "get_request": candidate.get("get_request"),
            }
            for candidate in request_plan.get("query_candidates", [])
        ],
    }


def run_request_plan(
    request_plan: dict[str, Any],
    api_key: str,
    requester: Any = request_json,
) -> dict[str, Any]:
    results = []
    for candidate in request_plan.get("query_candidates", []):
        request_params = prepare_request_params(candidate, api_key)
        try:
            raw_payload = requester(YOUTUBE_SEARCH_URL, request_params)
        except MediaProviderError:
            raise
        except Exception as exc:
            raise MediaProviderError(str(exc)) from exc

        results.append(
            {
                "intent": candidate.get("intent"),
                "media_goal": candidate.get("media_goal"),
                "confidence_hint": candidate.get("confidence_hint"),
                "review_priority": candidate.get("review_priority"),
                "reason": candidate.get("reason"),
                "request": {
                    "url": build_redacted_request_url(request_params),
                    "params": redact_request_params(request_params),
                },
                "items": normalize_youtube_search_items(raw_payload, candidate),
            },
        )

    return {
        "provider": "youtube",
        "api_method": "search.list",
        "event_id": request_plan["event_id"],
        "editorial_status": "draft",
        "source_request_plan": f"youtube-search-requests/{request_plan['event_id']}.json",
        "results": results,
        "review_notes": [
            "These are raw YouTube API candidates and must remain draft.",
            "Review historical relevance, source/channel quality, and availability before adding media_links.",
        ],
    }


def prepare_request_params(
    candidate: dict[str, Any],
    api_key: str,
) -> dict[str, str]:
    params = {
        str(key): str(value)
        for key, value in candidate["request_params"].items()
        if value is not None
    }
    params["key"] = api_key
    return params


def redact_request_params(params: dict[str, str]) -> dict[str, str]:
    return {**params, "key": API_KEY_PLACEHOLDER}


def build_redacted_request_url(params: dict[str, str]) -> str:
    return f"{YOUTUBE_SEARCH_URL}?{urllib.parse.urlencode(redact_request_params(params))}"


def normalize_youtube_search_items(
    payload: dict[str, Any],
    candidate: dict[str, Any],
) -> list[dict[str, Any]]:
    normalized_items = []
    for item in payload.get("items", []):
        item_id = item.get("id", {})
        snippet = item.get("snippet", {})
        media_type = item_id.get("kind", "").replace("youtube#", "")
        video_id = item_id.get("videoId")
        playlist_id = item_id.get("playlistId")
        normalized_items.append(
            {
                "provider": "youtube",
                "type": media_type or candidate.get("youtube_type"),
                "video_id": video_id,
                "playlist_id": playlist_id,
                "url": build_youtube_url(video_id=video_id, playlist_id=playlist_id),
                "title": snippet.get("title", ""),
                "channel_title": snippet.get("channelTitle", ""),
                "channel_id": snippet.get("channelId", ""),
                "description": snippet.get("description", ""),
                "published_at": snippet.get("publishedAt"),
                "matched_query": candidate.get("q", ""),
                "intent": candidate.get("intent"),
                "review_status": "draft",
            },
        )
    return normalized_items


def build_youtube_url(
    video_id: str | None,
    playlist_id: str | None,
) -> str | None:
    if video_id:
        return f"https://www.youtube.com/watch?v={video_id}"
    if playlist_id:
        return f"https://www.youtube.com/playlist?list={playlist_id}"
    return None


if __name__ == "__main__":
    raise SystemExit(main())
