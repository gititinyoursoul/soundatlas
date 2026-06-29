import argparse
import html
import json
import sys
from pathlib import Path
from typing import Any

BACKEND_ROOT = Path(__file__).resolve().parents[1]
if str(BACKEND_ROOT) not in sys.path:
    sys.path.insert(0, str(BACKEND_ROOT))

from scripts.run_youtube_search_requests import DEFAULT_OUTPUT_DIR
from app.link_ignores import build_ignored_link_index, link_is_ignored


REPO_ROOT = Path(__file__).resolve().parents[2]
EVENTS_PATH = REPO_ROOT / "data" / "seed" / "events.json"

YOUTUBE_CONFIDENCE_HINTS = {
    "high": 0.75,
    "medium": 0.55,
    "low": 0.35,
}
SUPPORTED_YOUTUBE_TYPES = {"video", "playlist"}


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Merge YouTube search result candidates into SoundAtlas event media links.",
    )
    parser.add_argument("--event-id", help="Only enrich one event.")
    parser.add_argument(
        "--results-dir",
        type=Path,
        default=DEFAULT_OUTPUT_DIR,
        help="Directory containing normalized YouTube search result JSON files.",
    )
    parser.add_argument(
        "--limit",
        type=int,
        default=3,
        help="Maximum YouTube links to add per event.",
    )
    parser.add_argument("--dry-run", action="store_true", help="Print changes without writing.")
    args = parser.parse_args()

    events_payload = read_json(EVENTS_PATH)
    ignored_link_index = build_ignored_link_index(events_payload)
    youtube_result_payloads = load_youtube_result_payloads(
        args.results_dir,
        event_id=args.event_id,
    )

    if not youtube_result_payloads:
        print("No YouTube search results found.", file=sys.stderr)
        return 2

    changed_events = enrich_events_payload(
        events_payload=events_payload,
        youtube_result_payloads=youtube_result_payloads,
        event_id=args.event_id,
        limit=args.limit,
        ignored_link_index=ignored_link_index,
    )

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


def load_youtube_result_payloads(
    results_dir: Path,
    event_id: str | None = None,
) -> list[dict[str, Any]]:
    if not results_dir.exists():
        return []

    result_payloads = []
    for result_path in sorted(results_dir.glob("*.json")):
        payload = read_json(result_path)
        if payload.get("provider") != "youtube":
            continue
        if event_id and payload.get("event_id") != event_id:
            continue
        result_payloads.append(payload)
    return result_payloads


def enrich_events_payload(
    events_payload: dict[str, Any],
    youtube_result_payloads: list[dict[str, Any]],
    event_id: str | None,
    limit: int,
    ignored_link_index: dict[tuple[str, str], set[str]] | None = None,
) -> int:
    result_payload_by_event_id = {
        payload["event_id"]: payload
        for payload in youtube_result_payloads
        if isinstance(payload.get("event_id"), str)
    }

    changed_events = 0
    for event in events_payload.get("events", []):
        if event_id and event["id"] != event_id:
            continue

        result_payload = result_payload_by_event_id.get(event["id"])
        if not result_payload:
            continue

        candidates = extract_media_links_from_youtube_results(
            result_payload,
            limit=limit,
            event_id=event["id"],
            ignored_link_index=ignored_link_index,
        )
        if not candidates:
            continue

        existing_links = event.get("media_links", [])
        merged_links = merge_media_links(existing_links, candidates)
        if merged_links != existing_links:
            event["media_links"] = merged_links
            changed_events += 1

    return changed_events


def extract_media_links_from_youtube_results(
    result_payload: dict[str, Any],
    limit: int,
    event_id: str | None = None,
    ignored_link_index: dict[tuple[str, str], set[str]] | None = None,
) -> list[dict[str, Any]]:
    candidates = []
    for result_group in sorted(
        result_payload.get("results", []),
        key=lambda result: int(result.get("review_priority") or 999),
    ):
        confidence = confidence_hint_to_score(result_group.get("confidence_hint"))
        for item in result_group.get("items", []):
            candidate = build_media_link_from_youtube_item(item, result_group, confidence)
            if candidate:
                candidates.append(candidate)

    candidates = dedupe_media_links(candidates)
    if event_id and ignored_link_index:
        candidates = [
            candidate
            for candidate in candidates
            if not link_is_ignored(ignored_link_index, event_id, "media", candidate)
        ]
    return candidates[:limit]


def build_media_link_from_youtube_item(
    item: dict[str, Any],
    result_group: dict[str, Any],
    confidence: float,
) -> dict[str, Any] | None:
    media_type = str(item.get("type") or "").replace("youtube#", "")
    if media_type not in SUPPORTED_YOUTUBE_TYPES:
        return None

    url = item.get("url")
    title = item.get("title")
    if not isinstance(url, str) or not url:
        return None
    if not isinstance(title, str) or not title:
        return None

    query = item.get("matched_query") or result_group.get("request", {}).get("params", {}).get("q")
    if not isinstance(query, str):
        query = ""

    return {
        "provider": "youtube",
        "type": media_type,
        "title": html.unescape(title),
        "url": url,
        "query": query,
        "confidence": confidence,
        "review_status": "draft",
    }


def confidence_hint_to_score(confidence_hint: Any) -> float:
    if not isinstance(confidence_hint, str):
        return 0.5
    return YOUTUBE_CONFIDENCE_HINTS.get(confidence_hint.casefold(), 0.5)


def merge_media_links(
    existing_links: list[dict[str, Any]],
    candidates: list[dict[str, Any]],
) -> list[dict[str, Any]]:
    links = [
        link
        for link in existing_links
        if isinstance(link, dict) and isinstance(link.get("url"), str)
    ]
    seen_urls = {link["url"] for link in links}

    for candidate in candidates:
        if candidate["url"] in seen_urls:
            continue
        links.append(candidate)
        seen_urls.add(candidate["url"])

    return links


def dedupe_media_links(media_links: list[dict[str, Any]]) -> list[dict[str, Any]]:
    deduped_links = []
    seen_urls = set()
    for media_link in media_links:
        if media_link["url"] in seen_urls:
            continue
        deduped_links.append(media_link)
        seen_urls.add(media_link["url"])
    return deduped_links


if __name__ == "__main__":
    raise SystemExit(main())
