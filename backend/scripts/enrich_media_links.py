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


def main(argv: list[str] | None = None) -> int:
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
    parser.add_argument(
        "--json",
        action="store_true",
        help="With --dry-run, print the full changed seed payload as JSON.",
    )
    args = parser.parse_args(argv)

    if args.limit < 1:
        print("--limit must be at least 1.", file=sys.stderr)
        return 2
    if args.json and not args.dry_run:
        print("--json can only be used with --dry-run.", file=sys.stderr)
        return 2

    events_payload = read_json(EVENTS_PATH)
    ignored_link_index = build_ignored_link_index(events_payload)
    youtube_result_payloads = load_youtube_result_payloads(
        args.results_dir,
        event_id=args.event_id,
    )

    if not youtube_result_payloads:
        print("No YouTube search results found.", file=sys.stderr)
        return 2
    selected_event_ids = selected_media_event_ids(
        events_payload=events_payload,
        youtube_result_payloads=youtube_result_payloads,
        event_id=args.event_id,
    )
    before_counts = link_counts_by_event_id(events_payload, selected_event_ids, "media_links")

    changed_events = enrich_events_payload(
        events_payload=events_payload,
        youtube_result_payloads=youtube_result_payloads,
        event_id=args.event_id,
        limit=args.limit,
        ignored_link_index=ignored_link_index,
    )

    if args.dry_run:
        if args.json:
            print(json.dumps(events_payload, indent=2, ensure_ascii=False))
        else:
            print(
                format_media_enrichment_summary(
                    events_payload=events_payload,
                    selected_event_ids=selected_event_ids,
                    before_counts=before_counts,
                    changed_events=changed_events,
                    event_id=args.event_id,
                    results_dir=args.results_dir,
                    result_payload_count=len(youtube_result_payloads),
                    limit=args.limit,
                    dry_run=True,
                    wrote_seed=False,
                ),
            )
    elif changed_events:
        EVENTS_PATH.write_text(
            json.dumps(events_payload, indent=2, ensure_ascii=False) + "\n",
            encoding="utf-8",
        )

    if not args.dry_run:
        print(
            format_media_enrichment_summary(
                events_payload=events_payload,
                selected_event_ids=selected_event_ids,
                before_counts=before_counts,
                changed_events=changed_events,
                event_id=args.event_id,
                results_dir=args.results_dir,
                result_payload_count=len(youtube_result_payloads),
                limit=args.limit,
                dry_run=False,
                wrote_seed=changed_events > 0,
            ),
        )
    return 0


def read_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def selected_media_event_ids(
    *,
    events_payload: dict[str, Any],
    youtube_result_payloads: list[dict[str, Any]],
    event_id: str | None,
) -> list[str]:
    result_event_ids = {
        payload["event_id"]
        for payload in youtube_result_payloads
        if isinstance(payload.get("event_id"), str)
    }
    return [
        event["id"]
        for event in events_payload.get("events", [])
        if isinstance(event, dict)
        and isinstance(event.get("id"), str)
        and event["id"] in result_event_ids
        and (event_id is None or event["id"] == event_id)
    ]


def link_counts_by_event_id(
    events_payload: dict[str, Any],
    event_ids: list[str],
    link_field: str,
) -> dict[str, int]:
    selected_ids = set(event_ids)
    return {
        event["id"]: len([link for link in event.get(link_field, []) if isinstance(link, dict)])
        for event in events_payload.get("events", [])
        if isinstance(event, dict) and event.get("id") in selected_ids
    }


def format_media_enrichment_summary(
    *,
    events_payload: dict[str, Any],
    selected_event_ids: list[str],
    before_counts: dict[str, int],
    changed_events: int,
    event_id: str | None,
    results_dir: Path,
    result_payload_count: int,
    limit: int,
    dry_run: bool,
    wrote_seed: bool,
) -> str:
    after_counts = link_counts_by_event_id(events_payload, selected_event_ids, "media_links")
    added_total = sum(
        max(after_counts.get(event_id, 0) - before_counts.get(event_id, 0), 0)
        for event_id in selected_event_ids
    )
    lines = [
        "Media enrichment",
        f"Mode: {'dry-run (no files written)' if dry_run else 'write'}",
        f"Scope: {f'event {event_id}' if event_id else 'all result events'}",
        f"Results dir: {relative_repo_path(results_dir)}",
        f"Result files: {result_payload_count}",
        f"Limit: {limit} media link(s) per event",
        f"Events considered: {len(selected_event_ids)}",
        f"Changed events: {changed_events}",
        f"Added media links: {added_total}",
    ]
    if not dry_run:
        lines.append(f"Wrote: {relative_repo_path(EVENTS_PATH) if wrote_seed else 'nothing'}")
        if not wrote_seed:
            lines.append("No candidates added.")
    if selected_event_ids:
        lines.extend(["", "Events"])
        for current_event_id in selected_event_ids:
            before = before_counts.get(current_event_id, 0)
            after = after_counts.get(current_event_id, 0)
            lines.append(
                f"  {current_event_id}: +{max(after - before, 0)} media link(s) "
                f"({before} -> {after})",
            )
    if dry_run:
        lines.extend(["", "Use --dry-run --json to inspect the full changed seed payload."])
    return "\n".join(lines)


def relative_repo_path(path: Path) -> str:
    try:
        return str(path.relative_to(REPO_ROOT))
    except ValueError:
        return str(path)


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
