import argparse
import json
import sys
from pathlib import Path
from typing import Any

BACKEND_ROOT = Path(__file__).resolve().parents[1]
if str(BACKEND_ROOT) not in sys.path:
    sys.path.insert(0, str(BACKEND_ROOT))

from app.link_ignores import iter_ignored_links


REPO_ROOT = Path(__file__).resolve().parents[2]
EVENTS_PATH = REPO_ROOT / "data" / "seed" / "events.json"
ROUTES_PATH = REPO_ROOT / "data" / "seed" / "routes.json"


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Report media, image, and ignored-link counts for seed events.",
    )
    parser.add_argument("--event-id", help="Only report one event.")
    parser.add_argument("--route-id", help="Only report events in one route.")
    parser.add_argument(
        "--json",
        action="store_true",
        help="Print the counts report as JSON instead of text.",
    )
    args = parser.parse_args(argv)

    try:
        events_payload = read_json(EVENTS_PATH)
        routes_payload = read_json(ROUTES_PATH)
        events = select_events(
            events_payload=events_payload,
            routes_payload=routes_payload,
            event_id=args.event_id,
            route_id=args.route_id,
        )
    except ValueError as exc:
        print(str(exc), file=sys.stderr)
        return 2

    report = build_seed_link_counts_report(
        events_payload=events_payload,
        events=events,
        event_id=args.event_id,
        route_id=args.route_id,
    )

    if args.json:
        print(json.dumps(report, indent=2, ensure_ascii=False))
    else:
        print(format_seed_link_counts_report(report))
    return 0


def read_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def select_events(
    *,
    events_payload: dict[str, Any],
    routes_payload: dict[str, Any],
    event_id: str | None,
    route_id: str | None,
) -> list[dict[str, Any]]:
    events = [
        event
        for event in events_payload.get("events", [])
        if isinstance(event, dict) and event_matches_filters(event, event_id, route_id)
    ]
    if event_id and not events:
        raise ValueError(f"No event found for --event-id '{event_id}'.")
    if route_id and not any(
        route.get("id") == route_id for route in routes_payload.get("routes", [])
    ):
        raise ValueError(f"No route found for --route-id '{route_id}'.")
    return events


def event_matches_filters(
    event: dict[str, Any],
    event_id: str | None,
    route_id: str | None,
) -> bool:
    if event_id and event.get("id") != event_id:
        return False
    if route_id and event.get("route_id") != route_id:
        return False
    return True


def build_seed_link_counts_report(
    *,
    events_payload: dict[str, Any],
    events: list[dict[str, Any]],
    event_id: str | None,
    route_id: str | None,
) -> dict[str, Any]:
    selected_event_ids = [event.get("id") for event in events if isinstance(event.get("id"), str)]
    ignored_entries = [
        entry
        for entry in iter_ignored_links(events_payload)
        if entry.get("event_id") in selected_event_ids
    ]
    event_rows = [summarize_event_links(event, ignored_entries) for event in events]
    aggregate = summarize_aggregate(event_rows, ignored_entries)
    return {
        "scope": {
            "event_id": event_id,
            "route_id": route_id,
        },
        "events": event_rows,
        "ignored_links": ignored_entries,
        "aggregate": aggregate,
    }


def summarize_event_links(
    event: dict[str, Any],
    ignored_entries: list[dict[str, Any]],
) -> dict[str, Any]:
    event_id = str(event.get("id") or "")
    media_count = count_link_collection(event.get("media_links", []))
    image_count = count_link_collection(event.get("image_links", []))
    ignored_for_event = [
        entry
        for entry in ignored_entries
        if entry.get("event_id") == event_id
    ]
    ignored_count = len(ignored_for_event)
    ignored_value_count = sum(
        len(entry.get("values", []))
        for entry in ignored_for_event
        if isinstance(entry.get("values"), list)
    )
    return {
        "event_id": event_id,
        "route_id": event.get("route_id") or "",
        "title": event.get("title") or "",
        "media_links": media_count,
        "image_links": image_count,
        "ignored_entries": ignored_count,
        "ignored_values": ignored_value_count,
        "total_links": media_count + image_count,
    }


def summarize_aggregate(
    events: list[dict[str, Any]],
    ignored_entries: list[dict[str, Any]],
) -> dict[str, Any]:
    return {
        "event_count": len(events),
        "media_links": sum(int(event.get("media_links") or 0) for event in events),
        "image_links": sum(int(event.get("image_links") or 0) for event in events),
        "ignored_entries": len(ignored_entries),
        "ignored_values": sum(
            len(entry.get("values", []))
            for entry in ignored_entries
            if isinstance(entry.get("values"), list)
        ),
        "total_links": sum(int(event.get("total_links") or 0) for event in events),
    }


def count_link_collection(links: Any) -> int:
    if not isinstance(links, list):
        return 0
    return sum(1 for link in links if isinstance(link, dict))


def format_seed_link_counts_report(report: dict[str, Any]) -> str:
    aggregate = report.get("aggregate", {})
    lines = [
        "Seed link counts",
        f"Scope: {format_scope(report.get('scope', {}))}",
        "",
        "Aggregate",
        f"  events: {aggregate.get('event_count', 0)}",
        f"  media links: {aggregate.get('media_links', 0)}",
        f"  image links: {aggregate.get('image_links', 0)}",
        f"  ignored entries: {aggregate.get('ignored_entries', 0)}",
        f"  ignored values: {aggregate.get('ignored_values', 0)}",
        f"  total links: {aggregate.get('total_links', 0)}",
    ]
    lines.extend(["", "Events"])
    for event in report.get("events", []):
        lines.append(
            "  "
            + f"{event.get('event_id')}: media={event.get('media_links', 0)} "
            + f"image={event.get('image_links', 0)} ignored={event.get('ignored_entries', 0)} "
            + f"total={event.get('total_links', 0)}",
        )
    ignored_groups = group_ignored_links(report.get("ignored_links", []))
    if ignored_groups:
        lines.extend(["", "Ignored links"])
        seen_event_ids = set()
        for event in report.get("events", []):
            event_id = str(event.get("event_id") or "")
            kind_rows = ignored_groups.get(event_id)
            if not kind_rows:
                continue
            seen_event_ids.add(event_id)
            lines.append(f"  {event_id}")
            for kind, summary in kind_rows.items():
                lines.append(
                    "    "
                    + f"{kind}: {summary['entries']} entry(s), {summary['values']} value(s)",
                )
        for event_id, kind_rows in ignored_groups.items():
            if event_id in seen_event_ids:
                continue
            lines.append(f"  {event_id}")
            for kind, summary in kind_rows.items():
                lines.append(
                    "    "
                    + f"{kind}: {summary['entries']} entry(s), {summary['values']} value(s)",
                )
    return "\n".join(lines)


def format_scope(scope: dict[str, Any]) -> str:
    event_id = scope.get("event_id")
    route_id = scope.get("route_id")
    if event_id:
        return f"event {event_id}"
    if route_id:
        return f"route {route_id}"
    return "all events"


def ignored_value_count(entry: dict[str, Any]) -> int:
    values = entry.get("values", [])
    if not isinstance(values, list):
        return 0
    return len(values)


def group_ignored_links(
    ignored_entries: list[dict[str, Any]],
) -> dict[str, dict[str, dict[str, int]]]:
    grouped: dict[str, dict[str, dict[str, int]]] = {}
    for entry in ignored_entries:
        event_id = str(entry.get("event_id") or "")
        kind = str(entry.get("kind") or "")
        event_group = grouped.setdefault(event_id, {})
        kind_group = event_group.setdefault(kind, {"entries": 0, "values": 0})
        kind_group["entries"] += 1
        kind_group["values"] += ignored_value_count(entry)
    return grouped


if __name__ == "__main__":
    raise SystemExit(main())
