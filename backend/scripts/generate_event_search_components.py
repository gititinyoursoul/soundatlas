import argparse
import json
import sys
from pathlib import Path
from typing import Any

BACKEND_ROOT = Path(__file__).resolve().parents[1]
if str(BACKEND_ROOT) not in sys.path:
    sys.path.insert(0, str(BACKEND_ROOT))

from app.media_enrichment.event_search_components import (
    EventSearchComponent,
    build_event_search_component,
    component_path_for_event,
    validate_component_for_seed,
)
from scripts.enrich_image_links import (
    EVENTS_PATH,
    PLACES_PATH,
    ROUTES_PATH,
    build_places_by_id,
    build_routes_by_id,
    read_json,
    select_events,
)


REPO_ROOT = Path(__file__).resolve().parents[2]
DEFAULT_COMPONENT_DIR = REPO_ROOT / "data" / "enrichment" / "event-search-components"


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Generate SoundAtlas event-search-components from existing seed data.",
    )
    parser.add_argument("--event-id", help="Only generate one event component.")
    parser.add_argument("--route-id", help="Only generate components for events in one route.")
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=DEFAULT_COMPONENT_DIR,
        help="Directory for event-search-component JSON files.",
    )
    parser.add_argument("--dry-run", action="store_true", help="Print changes without writing.")
    parser.add_argument(
        "--json",
        action="store_true",
        help="With --dry-run, print generated components and validation reports as JSON.",
    )
    args = parser.parse_args(argv)

    if args.json and not args.dry_run:
        print("--json can only be used with --dry-run.", file=sys.stderr)
        return 2

    try:
        events_payload = read_json(EVENTS_PATH)
        routes_payload = read_json(ROUTES_PATH)
        places_payload = read_json(PLACES_PATH)
        components = generate_components(
            events_payload=events_payload,
            routes_payload=routes_payload,
            places_payload=places_payload,
            event_id=args.event_id,
            route_id=args.route_id,
        )
    except ValueError as exc:
        print(str(exc), file=sys.stderr)
        return 2

    if args.dry_run:
        if args.json:
            print(
                json.dumps(
                    build_json_preview(components),
                    indent=2,
                    ensure_ascii=False,
                ),
            )
        else:
            print(
                format_generation_summary(
                    components=components,
                    output_dir=args.output_dir,
                    event_id=args.event_id,
                    route_id=args.route_id,
                    dry_run=True,
                    written_paths=[],
                ),
            )
        return 0

    args.output_dir.mkdir(parents=True, exist_ok=True)
    written_paths = []
    for record in components:
        path = component_path_for_event(args.output_dir, record["component"].event_id)
        path.write_text(
            json.dumps(
                record["component"].model_dump(),
                indent=2,
                ensure_ascii=False,
            )
            + "\n",
            encoding="utf-8",
        )
        written_paths.append(path)

    print(
        format_generation_summary(
            components=components,
            output_dir=args.output_dir,
            event_id=args.event_id,
            route_id=args.route_id,
            dry_run=False,
            written_paths=written_paths,
        ),
    )
    return 0


def generate_components(
    *,
    events_payload: dict[str, Any],
    routes_payload: dict[str, Any],
    places_payload: dict[str, Any],
    event_id: str | None,
    route_id: str | None,
) -> list[dict[str, Any]]:
    routes_by_id = build_routes_by_id(routes_payload)
    places_by_id = build_places_by_id(places_payload)
    events_by_id = {
        event["id"]: event
        for event in events_payload.get("events", [])
        if isinstance(event, dict) and isinstance(event.get("id"), str)
    }
    events = select_events(
        events_payload=events_payload,
        routes_payload=routes_payload,
        event_id=event_id,
        route_id=route_id,
    )

    records = []
    for event in events:
        route = routes_by_id.get(event.get("route_id"), {})
        place = places_by_id.get(event.get("place_id"), {})
        component = build_event_search_component(event=event, route=route, place=place)
        report = validate_component_for_seed(
            component=component,
            event=events_by_id.get(component.event_id),
            place=place,
        )
        records.append({"component": component, "validation": report})
    return records


def build_json_preview(records: list[dict[str, Any]]) -> dict[str, Any]:
    return {
        "components": [
            {
                "component": record["component"].model_dump(),
                "validation": record["validation"].model_dump(),
            }
            for record in records
        ],
    }


def format_generation_summary(
    *,
    components: list[dict[str, Any]],
    output_dir: Path,
    event_id: str | None,
    route_id: str | None,
    dry_run: bool,
    written_paths: list[Path],
) -> str:
    warning_count = sum(len(record["validation"].warnings) for record in components)
    error_count = sum(len(record["validation"].errors) for record in components)
    lines = [
        "Event search component generation",
        f"Mode: {'dry-run (no files written)' if dry_run else 'write'}",
        f"Scope: {format_scope(event_id=event_id, route_id=route_id)}",
        f"Output dir: {relative_repo_path(output_dir)}",
        f"Components: {len(components)}",
        f"Validation warnings: {warning_count}",
        f"Validation errors: {error_count}",
    ]
    if written_paths:
        lines.extend(["", "Files"])
        for path in written_paths:
            lines.append(f"  {relative_repo_path(path)}")
    if components:
        lines.extend(["", "Events"])
        for record in components:
            component: EventSearchComponent = record["component"]
            warnings = record["validation"].warnings
            errors = record["validation"].errors
            status = "ok"
            if errors:
                status = f"{len(errors)} error(s)"
            elif warnings:
                status = f"{len(warnings)} warning(s)"
            lines.append(f"  {component.event_id}: {status}")
    if dry_run:
        lines.extend(["", "Use --dry-run --json to inspect generated components."])
    return "\n".join(lines)


def format_scope(event_id: str | None, route_id: str | None) -> str:
    if event_id:
        return f"event {event_id}"
    if route_id:
        return f"route {route_id}"
    return "all events"


def relative_repo_path(path: Path) -> str:
    try:
        return str(path.relative_to(REPO_ROOT))
    except ValueError:
        return str(path)


if __name__ == "__main__":
    raise SystemExit(main())
