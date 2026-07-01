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


def main(argv: list[str] | None = None) -> int:
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
    parser.add_argument(
        "--json",
        action="store_true",
        help="With --dry-run, print the planned request summary as JSON.",
    )
    args = parser.parse_args(argv)

    if args.json and not args.dry_run:
        print("--json can only be used with --dry-run.", file=sys.stderr)
        return 2

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
        summaries = [build_dry_run_summary(request_plan) for request_plan in request_plans]
        if args.json:
            print(json.dumps(summaries, indent=2, ensure_ascii=False))
        else:
            print(
                format_youtube_request_run_summary(
                    request_plans=request_plans,
                    event_id=args.event_id,
                    request_dir=args.request_dir,
                    output_dir=args.output_dir,
                    dry_run=True,
                    written_paths=[],
                ),
            )
        return 0

    args.output_dir.mkdir(parents=True, exist_ok=True)
    written_paths = []
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
        written_paths.append(output_path)

    print(
        format_youtube_request_run_summary(
            request_plans=request_plans,
            event_id=args.event_id,
            request_dir=args.request_dir,
            output_dir=args.output_dir,
            dry_run=False,
            written_paths=written_paths,
        ),
    )

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


def format_youtube_request_run_summary(
    *,
    request_plans: list[dict[str, Any]],
    event_id: str | None,
    request_dir: Path,
    output_dir: Path,
    dry_run: bool,
    written_paths: list[Path],
) -> str:
    total_requests = sum(
        len(plan.get("query_candidates", []))
        for plan in request_plans
        if isinstance(plan.get("query_candidates"), list)
    )
    lines = [
        "YouTube request run",
        f"Mode: {'dry-run (no API calls, no files written)' if dry_run else 'write'}",
        f"Scope: {f'event {event_id}' if event_id else 'all request plans'}",
        f"Request dir: {relative_repo_path(request_dir)}",
        f"Output dir: {relative_repo_path(output_dir)}",
        f"Request plans: {len(request_plans)}",
        f"Planned requests: {total_requests}",
    ]
    if not dry_run:
        lines.append(f"Written result files: {len(written_paths)}")
    if request_plans:
        lines.extend(["", "Plans"])
        for request_plan in request_plans:
            candidates = [
                candidate
                for candidate in request_plan.get("query_candidates", [])
                if isinstance(candidate, dict)
            ]
            type_counts = count_values(candidates, "youtube_type")
            lines.append(
                f"  {request_plan.get('event_id')}: {len(candidates)} request(s) "
                f"({format_counts(type_counts)})",
            )
    if written_paths:
        lines.extend(["", "Files"])
        for path in written_paths:
            lines.append(f"  {relative_repo_path(path)}")
    if dry_run:
        lines.extend(["", "Use --dry-run --json to inspect the planned requests as JSON."])
    return "\n".join(lines)


def count_values(items: list[dict[str, Any]], field: str) -> dict[str, int]:
    counts: dict[str, int] = {}
    for item in items:
        value = item.get(field)
        if not isinstance(value, str) or not value:
            value = "unknown"
        counts[value] = counts.get(value, 0) + 1
    return dict(sorted(counts.items()))


def format_counts(counts: dict[str, int]) -> str:
    if not counts:
        return "none"
    return ", ".join(f"{key}={value}" for key, value in counts.items())


def relative_repo_path(path: Path) -> str:
    try:
        return str(path.relative_to(REPO_ROOT))
    except ValueError:
        return str(path)


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
