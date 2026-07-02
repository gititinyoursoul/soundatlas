import argparse
import json
import re
import shutil
import sys
from pathlib import Path
from typing import Any

BACKEND_ROOT = Path(__file__).resolve().parents[1]
if str(BACKEND_ROOT) not in sys.path:
    sys.path.insert(0, str(BACKEND_ROOT))

from app.schemas import Connection, Event, Place, Route


REPO_ROOT = Path(__file__).resolve().parents[2]
DEFAULT_CONTENT_ROOT = REPO_ROOT / "docs" / "content" / "routes"
DEFAULT_SEED_DIR = REPO_ROOT / "data" / "seed"
SCRIPT_NAME = "route_content_pipeline.py"
PIPELINE_FILENAME = "pipeline.json"
PIPELINE_STEPS = (
    "event_list",
    "route_concept",
    "event_framing",
    "seed_preview",
    "validation",
)


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)

    try:
        if args.command == "init":
            route_dir = route_dir_for(args.content_root, args.route_id)
            manifest = init_pipeline(
                route_dir=route_dir,
                route_id=args.route_id,
                active_dossier=args.dossier,
                renew=args.renew,
            )
            print(format_init_summary(route_dir, manifest))
        elif args.command == "run":
            result = run_pipeline(
                content_root=args.content_root,
                seed_dir=args.seed_dir,
                route_id=args.route_id,
                step=args.step,
                renew=args.renew,
            )
            print(format_run_summary(result))
        elif args.command == "status":
            route_dir = route_dir_for(args.content_root, args.route_id)
            manifest = load_or_create_manifest(route_dir, args.route_id)
            print(format_status(route_dir, manifest))
        elif args.command == "promote":
            if not args.to_seed:
                raise ValueError("promote currently requires --to-seed.")
            result = promote_to_seed(
                content_root=args.content_root,
                seed_dir=args.seed_dir,
                route_id=args.route_id,
                write=args.write,
            )
            print(result)
        else:
            parser.print_help()
            return 2
    except ValueError as exc:
        print(str(exc), file=sys.stderr)
        return 2
    return 0


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Manage SoundAtlas route content from brief to seed-ready drafts.",
    )
    parser.add_argument(
        "--content-root",
        type=Path,
        default=DEFAULT_CONTENT_ROOT,
        help="Directory containing per-route content folders.",
    )
    parser.add_argument(
        "--seed-dir",
        type=Path,
        default=DEFAULT_SEED_DIR,
        help="Directory containing seed JSON files.",
    )
    subparsers = parser.add_subparsers(dest="command")

    init_parser = subparsers.add_parser("init", help="Create a route pipeline manifest.")
    init_parser.add_argument("--route-id", required=True)
    init_parser.add_argument("--dossier", help="Active dossier filename.")
    init_parser.add_argument(
        "--renew",
        action="store_true",
        help="Rewrite pipeline.json even when it already exists.",
    )

    run_parser = subparsers.add_parser("run", help="Run route pipeline steps.")
    run_parser.add_argument("--route-id", required=True)
    run_parser.add_argument("--step", choices=PIPELINE_STEPS)
    run_parser.add_argument(
        "--all",
        action="store_true",
        help="Run all steps. This is the default when --step is omitted.",
    )
    run_parser.add_argument(
        "--missing",
        action="store_true",
        help="Create only missing outputs. This is the default mode.",
    )
    run_parser.add_argument(
        "--renew",
        action="store_true",
        help="Regenerate selected outputs and save .bak copies of overwritten files.",
    )

    status_parser = subparsers.add_parser("status", help="Report route pipeline state.")
    status_parser.add_argument("--route-id", required=True)

    promote_parser = subparsers.add_parser(
        "promote",
        help="Preview or write reviewed route drafts into seed JSON.",
    )
    promote_parser.add_argument("--route-id", required=True)
    promote_parser.add_argument("--to-seed", action="store_true")
    promote_parser.add_argument(
        "--write",
        action="store_true",
        help="Write seed files. Omit for dry-run preview.",
    )
    return parser


def route_dir_for(content_root: Path, route_id: str) -> Path:
    return content_root / route_id


def init_pipeline(
    *,
    route_dir: Path,
    route_id: str,
    active_dossier: str | None,
    renew: bool = False,
) -> dict[str, Any]:
    route_dir.mkdir(parents=True, exist_ok=True)
    manifest_path = route_dir / PIPELINE_FILENAME
    if manifest_path.exists() and not renew:
        manifest = read_json(manifest_path)
        return merge_manifest_defaults(route_dir, route_id, manifest)

    manifest = default_manifest(route_dir, route_id, active_dossier)
    write_json(manifest_path, manifest)
    return manifest


def load_or_create_manifest(route_dir: Path, route_id: str) -> dict[str, Any]:
    manifest_path = route_dir / PIPELINE_FILENAME
    if manifest_path.exists():
        manifest = read_json(manifest_path)
        merged = merge_manifest_defaults(route_dir, route_id, manifest)
        if merged != manifest:
            write_json(manifest_path, merged)
        return merged
    return init_pipeline(route_dir=route_dir, route_id=route_id, active_dossier=None)


def default_manifest(
    route_dir: Path,
    route_id: str,
    active_dossier: str | None,
) -> dict[str, Any]:
    dossier = active_dossier or choose_active_dossier(route_dir)
    return {
        "route_id": route_id,
        "active_dossier": dossier,
        "steps": {
            "event_list": {
                "input": dossier,
                "markdown": "event-list.md",
                "json": "event-list.json",
                "review_status": "draft",
            },
            "route_concept": {
                "input": "event-list.json",
                "markdown": "route-concept.md",
                "review_status": "draft",
            },
            "event_framing": {
                "input": "route-concept.md",
                "markdown": "event-framing.md",
                "events": "event-framing.json",
                "places": "place-framing.json",
                "connections": "connection-framing.json",
                "review_status": "draft",
            },
            "seed_preview": {
                "input": "event-framing.json",
                "markdown": "seed-transfer-report.md",
                "review_status": "draft",
            },
            "validation": {
                "markdown": "validation-report.md",
                "review_status": "draft",
            },
        },
    }


def merge_manifest_defaults(
    route_dir: Path,
    route_id: str,
    manifest: dict[str, Any],
) -> dict[str, Any]:
    defaults = default_manifest(
        route_dir,
        route_id,
        manifest.get("active_dossier") if isinstance(manifest.get("active_dossier"), str) else None,
    )
    merged = {**defaults, **manifest}
    merged["steps"] = {
        step: {**defaults["steps"][step], **manifest.get("steps", {}).get(step, {})}
        for step in PIPELINE_STEPS
    }
    return merged


def choose_active_dossier(route_dir: Path) -> str:
    preferred = route_dir / "research-dossier-mvp-edit.md"
    if preferred.exists():
        return preferred.name
    dossiers = sorted(route_dir.glob("research-dossier*.md"))
    if dossiers:
        return dossiers[0].name
    return "research-dossier.md"


def run_pipeline(
    *,
    content_root: Path,
    seed_dir: Path,
    route_id: str,
    step: str | None,
    renew: bool,
) -> list[dict[str, Any]]:
    route_dir = route_dir_for(content_root, route_id)
    manifest = load_or_create_manifest(route_dir, route_id)
    selected_steps = [step] if step else list(PIPELINE_STEPS)
    results = []
    for selected_step in selected_steps:
        results.append(
            run_step(
                route_dir=route_dir,
                seed_dir=seed_dir,
                manifest=manifest,
                step=selected_step,
                renew=renew,
            ),
        )
    write_json(route_dir / PIPELINE_FILENAME, manifest)
    return results


def run_step(
    *,
    route_dir: Path,
    seed_dir: Path,
    manifest: dict[str, Any],
    step: str,
    renew: bool,
) -> dict[str, Any]:
    if step == "event_list":
        return generate_event_list(route_dir=route_dir, manifest=manifest, renew=renew)
    if step == "route_concept":
        return generate_route_concept(route_dir=route_dir, manifest=manifest, renew=renew)
    if step == "event_framing":
        return generate_event_framing(
            route_dir=route_dir,
            seed_dir=seed_dir,
            manifest=manifest,
            renew=renew,
        )
    if step == "seed_preview":
        return generate_seed_preview(
            route_dir=route_dir,
            seed_dir=seed_dir,
            manifest=manifest,
            renew=renew,
        )
    if step == "validation":
        return generate_validation_report(
            route_dir=route_dir,
            seed_dir=seed_dir,
            manifest=manifest,
            renew=renew,
        )
    raise ValueError(f"Unknown pipeline step '{step}'.")


def generate_event_list(
    *,
    route_dir: Path,
    manifest: dict[str, Any],
    renew: bool,
) -> dict[str, Any]:
    step = manifest["steps"]["event_list"]
    dossier_path = route_dir / step["input"]
    if not dossier_path.exists():
        raise ValueError(f"Missing active dossier: {dossier_path}")

    markdown_path = route_dir / step["markdown"]
    json_path = route_dir / step["json"]
    skipped = maybe_skip_outputs([markdown_path, json_path], renew)
    if skipped:
        return {"step": "event_list", "status": "skipped", "outputs": skipped}

    candidates = extract_candidate_events(dossier_path.read_text(encoding="utf-8"))
    payload = {
        "_meta": {
            "route_id": manifest["route_id"],
            "source": step["input"],
            "generated_by": SCRIPT_NAME,
            "review_status": "draft",
        },
        "candidates": [
            {
                **candidate,
                "status": "develop",
                "next_action": "review candidate",
            }
            for candidate in candidates
        ],
    }
    write_text(markdown_path, format_event_list_markdown(payload), renew=renew)
    write_json(json_path, payload, renew=renew)
    step["review_status"] = "draft"
    return {
        "step": "event_list",
        "status": "written",
        "outputs": [markdown_path.name, json_path.name],
        "candidates": len(candidates),
    }


def generate_route_concept(
    *,
    route_dir: Path,
    manifest: dict[str, Any],
    renew: bool,
) -> dict[str, Any]:
    step = manifest["steps"]["route_concept"]
    event_list_path = route_dir / step["input"]
    output_path = route_dir / step["markdown"]
    if not event_list_path.exists():
        raise ValueError(f"Missing event list JSON: {event_list_path}")
    skipped = maybe_skip_outputs([output_path], renew)
    if skipped:
        return {"step": "route_concept", "status": "skipped", "outputs": skipped}

    event_list = read_json(event_list_path)
    content = format_route_concept_markdown(manifest["route_id"], event_list)
    write_text(output_path, content, renew=renew)
    step["review_status"] = "draft"
    return {"step": "route_concept", "status": "written", "outputs": [output_path.name]}


def generate_event_framing(
    *,
    route_dir: Path,
    seed_dir: Path,
    manifest: dict[str, Any],
    renew: bool,
) -> dict[str, Any]:
    step = manifest["steps"]["event_framing"]
    event_list_path = route_dir / "event-list.json"
    dossier_path = route_dir / manifest["active_dossier"]
    outputs = [
        route_dir / step["markdown"],
        route_dir / step["events"],
        route_dir / step["places"],
        route_dir / step["connections"],
    ]
    if not event_list_path.exists():
        raise ValueError(f"Missing event list JSON: {event_list_path}")
    if not dossier_path.exists():
        raise ValueError(f"Missing active dossier: {dossier_path}")
    skipped = maybe_skip_outputs(outputs, renew)
    if skipped:
        return {"step": "event_framing", "status": "skipped", "outputs": skipped}

    event_list = read_json(event_list_path)
    seed_places = load_seed_collection(seed_dir, "places")
    seed_place_index = build_place_index(seed_places)
    events, places = build_event_and_place_drafts(
        route_id=manifest["route_id"],
        event_list=event_list,
        seed_place_index=seed_place_index,
    )
    connections = build_connection_drafts(
        manifest["route_id"],
        dossier_path.read_text(encoding="utf-8"),
        {event["id"] for event in events},
    )
    events_payload = {
        "_meta": {
            "route_id": manifest["route_id"],
            "source": "event-list.json",
            "generated_by": SCRIPT_NAME,
            "review_status": "draft",
        },
        "events": events,
    }
    places_payload = {
        "_meta": {
            "route_id": manifest["route_id"],
            "source": "event-list.json",
            "generated_by": SCRIPT_NAME,
            "review_status": "draft",
        },
        "places": places,
    }
    connections_payload = {
        "_meta": {
            "route_id": manifest["route_id"],
            "source": manifest["active_dossier"],
            "generated_by": SCRIPT_NAME,
            "review_status": "draft",
        },
        "connections": connections,
    }
    write_text(outputs[0], format_event_framing_markdown(events, places, connections), renew=renew)
    write_json(outputs[1], events_payload, renew=renew)
    write_json(outputs[2], places_payload, renew=renew)
    write_json(outputs[3], connections_payload, renew=renew)
    step["review_status"] = "draft"
    return {
        "step": "event_framing",
        "status": "written",
        "outputs": [path.name for path in outputs],
    }


def generate_seed_preview(
    *,
    route_dir: Path,
    seed_dir: Path,
    manifest: dict[str, Any],
    renew: bool,
) -> dict[str, Any]:
    step = manifest["steps"]["seed_preview"]
    output_path = route_dir / step["markdown"]
    skipped = maybe_skip_outputs([output_path], renew)
    if skipped:
        return {"step": "seed_preview", "status": "skipped", "outputs": skipped}

    report = build_seed_preview_report(route_dir=route_dir, seed_dir=seed_dir, manifest=manifest)
    write_text(output_path, report, renew=renew)
    step["review_status"] = "draft"
    return {"step": "seed_preview", "status": "written", "outputs": [output_path.name]}


def generate_validation_report(
    *,
    route_dir: Path,
    seed_dir: Path,
    manifest: dict[str, Any],
    renew: bool,
) -> dict[str, Any]:
    step = manifest["steps"]["validation"]
    output_path = route_dir / step["markdown"]
    skipped = maybe_skip_outputs([output_path], renew)
    if skipped:
        return {"step": "validation", "status": "skipped", "outputs": skipped}

    merged = build_merged_seed_payloads(route_dir=route_dir, seed_dir=seed_dir)
    errors = validate_seed_payloads(merged)
    report = format_validation_report(errors)
    write_text(output_path, report, renew=renew)
    step["review_status"] = "draft"
    return {"step": "validation", "status": "written", "outputs": [output_path.name]}


def maybe_skip_outputs(paths: list[Path], renew: bool) -> list[str]:
    if renew:
        return []
    existing = [path.name for path in paths if path.exists()]
    if len(existing) == len(paths):
        return existing
    return []


def extract_candidate_events(markdown: str) -> list[dict[str, str]]:
    rows = parse_section_table(markdown, "Candidate Events")
    candidates = []
    for row in rows:
        candidate_id = clean_id(row.get("candidate id", ""))
        if not candidate_id:
            continue
        candidates.append(
            {
                "candidate_id": candidate_id,
                "years": clean_cell(row.get("years", "")),
                "place": clean_cell(row.get("place", "")),
                "working_title": clean_cell(row.get("working title", "")),
                "inclusion_rationale": clean_cell(row.get("inclusion rationale", "")),
                "source_leads": clean_cell(row.get("source leads", "")),
                "risk_notes": clean_cell(row.get("risk notes", "")),
            },
        )
    return candidates


def extract_candidate_connections(markdown: str) -> list[dict[str, str]]:
    rows = parse_section_table(markdown, "Candidate Connections")
    connections = []
    for row in rows:
        from_event = clean_id(row.get("from event", ""))
        to_event = clean_id(row.get("to event", ""))
        relationship_type = slugify(clean_cell(row.get("relationship type", "")))
        if not from_event or not to_event or not relationship_type:
            continue
        connections.append(
            {
                "from_event_id": from_event,
                "to_event_id": to_event,
                "type": relationship_type,
                "summary": clean_cell(row.get("narrative purpose", "")),
                "source_leads": clean_cell(row.get("source leads", "")),
                "risk_notes": clean_cell(row.get("risk notes", "")),
            },
        )
    return connections


def parse_section_table(markdown: str, section_title: str) -> list[dict[str, str]]:
    lines = markdown.splitlines()
    section_lines: list[str] = []
    in_section = False
    for line in lines:
        if line.strip() == f"## {section_title}":
            in_section = True
            continue
        if in_section and line.startswith("## "):
            break
        if in_section:
            section_lines.append(line)

    table_lines = [line for line in section_lines if line.strip().startswith("|")]
    if len(table_lines) < 2:
        return []
    headers = [normalize_header(cell) for cell in split_markdown_row(table_lines[0])]
    rows = []
    for line in table_lines[2:]:
        cells = split_markdown_row(line)
        if len(cells) != len(headers):
            continue
        rows.append(dict(zip(headers, cells, strict=True)))
    return rows


def split_markdown_row(line: str) -> list[str]:
    return [cell.strip() for cell in line.strip().strip("|").split("|")]


def normalize_header(value: str) -> str:
    return clean_cell(value).lower()


def clean_cell(value: str) -> str:
    value = value.strip()
    if value.startswith("`") and value.endswith("`"):
        value = value[1:-1]
    return value.strip()


def clean_id(value: str) -> str:
    return slugify(clean_cell(value))


def slugify(value: str) -> str:
    value = value.lower().replace("&", " and ")
    value = re.sub(r"[^a-z0-9]+", "-", value)
    return value.strip("-")


def parse_year_range(value: str) -> tuple[int, int]:
    years = [int(year) for year in re.findall(r"(?<!\d)(1[6-9]\d{2}|20\d{2})(?!\d)", value)]
    if not years:
        decade_match = re.search(r"(1[6-9]\d0|20\d0)s", value)
        if decade_match:
            decade = int(decade_match.group(1))
            return decade, decade + 9
        return 0, 0
    return min(years), max(years)


def format_event_list_markdown(payload: dict[str, Any]) -> str:
    route_id = payload["_meta"]["route_id"]
    source = payload["_meta"]["source"]
    lines = [
        f"# {route_id} Event List",
        "",
        f"Source: `{source}`",
        "",
        "This is a review artifact. Candidate statuses are draft decisions and",
        "can be edited before route concept or seed-transfer work.",
        "",
        "| Candidate ID | Status | Years | Place | Working title | Route function | Source leads | Risk notes | Next action |",
        "| --- | --- | --- | --- | --- | --- | --- | --- | --- |",
    ]
    for candidate in payload["candidates"]:
        lines.append(
            "| "
            + " | ".join(
                [
                    f"`{candidate['candidate_id']}`",
                    candidate["status"],
                    candidate["years"],
                    candidate["place"],
                    candidate["working_title"],
                    candidate["inclusion_rationale"],
                    candidate["source_leads"],
                    candidate["risk_notes"],
                    candidate["next_action"],
                ],
            )
            + " |",
        )
    lines.append("")
    return "\n".join(lines)


def format_route_concept_markdown(route_id: str, event_list: dict[str, Any]) -> str:
    candidates = event_list.get("candidates", [])
    developed = [candidate for candidate in candidates if candidate.get("status") == "develop"]
    lines = [
        f"# {route_id} Route Concept Draft",
        "",
        "Source: `event-list.json`",
        "",
        "This scaffold turns reviewed event-list candidates into a route concept",
        "draft. Replace scaffold text with source-reviewed narrative before seed",
        "transfer.",
        "",
        "## Route Argument",
        "",
        "- Central question: TODO",
        "- Thesis: TODO",
        "",
        "## Candidate Sequence",
        "",
        "| Candidate ID | Years | Place | Working title | Route function |",
        "| --- | --- | --- | --- | --- |",
    ]
    for candidate in developed:
        lines.append(
            "| "
            + " | ".join(
                [
                    f"`{candidate.get('candidate_id', '')}`",
                    str(candidate.get("years", "")),
                    str(candidate.get("place", "")),
                    str(candidate.get("working_title", "")),
                    str(candidate.get("inclusion_rationale", "")),
                ],
            )
            + " |",
        )
    lines.extend(
        [
            "",
            "## Open Questions",
            "",
            "- Which candidates become seed events, route context, or later research?",
            "- Which places need exact coordinates or a justified regional strategy?",
            "- Which claims need source comparison before final wording?",
            "",
        ],
    )
    return "\n".join(lines)


def build_event_and_place_drafts(
    *,
    route_id: str,
    event_list: dict[str, Any],
    seed_place_index: dict[str, dict[str, Any]],
) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    events = []
    place_records_by_id: dict[str, dict[str, Any]] = {}
    for candidate in event_list.get("candidates", []):
        if candidate.get("status") not in {"develop", "context"}:
            continue
        place_text = str(candidate.get("place") or "review-place")
        place_decision = build_place_decision(place_text, seed_place_index)
        place_records_by_id[place_decision["place_id"]] = place_decision
        year_start, year_end = parse_year_range(str(candidate.get("years") or ""))
        events.append(
            {
                "id": candidate["candidate_id"],
                "route_id": route_id,
                "place_id": place_decision["place_id"],
                "title": candidate.get("working_title") or candidate["candidate_id"].replace("-", " ").title(),
                "year_start": year_start,
                "year_end": year_end,
                "summary": "Draft summary pending source-reviewed event framing.",
                "significance": candidate.get("inclusion_rationale") or "Draft significance pending review.",
                "tags": [],
                "review_status": "draft",
                "source_urls": [],
                "media_links": [],
                "image_links": [],
            },
        )
    return events, list(place_records_by_id.values())


def build_place_decision(
    place_text: str,
    seed_place_index: dict[str, dict[str, Any]],
) -> dict[str, Any]:
    place_id = slugify(place_text) or "review-place"
    existing = seed_place_index.get(place_id) or seed_place_index.get(slugify(place_text))
    if existing:
        return {
            "decision": "reuse",
            "source_place_text": place_text,
            "place_id": existing["id"],
        }
    return {
        "decision": "new",
        "source_place_text": place_text,
        "place_id": place_id,
        "place": {
            "id": place_id,
            "name": place_text,
            "borough": "review",
            "place_type": "review",
            "latitude": 0.0,
            "longitude": 0.0,
            "summary": "Draft place generated from route pipeline; review before seed promotion.",
            "review_status": "draft",
            "source_urls": [],
        },
    }


def build_place_index(seed_places: list[dict[str, Any]]) -> dict[str, dict[str, Any]]:
    index = {}
    for place in seed_places:
        if isinstance(place.get("id"), str):
            index[place["id"]] = place
        if isinstance(place.get("name"), str):
            index[slugify(place["name"])] = place
    return index


def build_connection_drafts(
    route_id: str,
    dossier_markdown: str,
    selected_event_ids: set[str],
) -> list[dict[str, Any]]:
    connections = []
    for candidate in extract_candidate_connections(dossier_markdown):
        if candidate["from_event_id"] not in selected_event_ids:
            continue
        if candidate["to_event_id"] not in selected_event_ids:
            continue
        connection_id = slugify(
            f"{candidate['from_event_id']}-to-{candidate['to_event_id']}-{candidate['type']}",
        )
        connections.append(
            {
                "id": connection_id,
                "from_event_id": candidate["from_event_id"],
                "to_event_id": candidate["to_event_id"],
                "type": candidate["type"],
                "summary": candidate["summary"] or f"Draft {route_id} connection pending review.",
                "review_status": "draft",
            },
        )
    return connections


def format_event_framing_markdown(
    events: list[dict[str, Any]],
    places: list[dict[str, Any]],
    connections: list[dict[str, Any]],
) -> str:
    lines = [
        "# Event Framing Draft",
        "",
        "This is a review artifact generated from the event list. Edit the JSON",
        "drafts before seed promotion.",
        "",
        "## Events",
        "",
        "| Event ID | Year range | Place ID | Title |",
        "| --- | --- | --- | --- |",
    ]
    for event in events:
        lines.append(
            f"| `{event['id']}` | {event['year_start']}-{event['year_end']} | "
            f"`{event['place_id']}` | {event['title']} |",
        )
    lines.extend(["", "## Places", "", "| Place ID | Decision | Source place |", "| --- | --- | --- |"])
    for place in places:
        lines.append(
            f"| `{place['place_id']}` | {place['decision']} | {place['source_place_text']} |",
        )
    lines.extend(
        [
            "",
            "## Connections",
            "",
            "| Connection ID | From | To | Type |",
            "| --- | --- | --- | --- |",
        ],
    )
    for connection in connections:
        lines.append(
            f"| `{connection['id']}` | `{connection['from_event_id']}` | "
            f"`{connection['to_event_id']}` | {connection['type']} |",
        )
    lines.append("")
    return "\n".join(lines)


def build_seed_preview_report(
    *,
    route_dir: Path,
    seed_dir: Path,
    manifest: dict[str, Any],
) -> str:
    merged = build_merged_seed_payloads(route_dir=route_dir, seed_dir=seed_dir)
    seed = load_seed_payloads(seed_dir)
    drafts = load_draft_payloads(route_dir)
    warnings = preview_warnings(manifest["route_id"], seed, drafts, merged)
    lines = [
        "# Seed Transfer Preview",
        "",
        f"Route: `{manifest['route_id']}`",
        "",
        "## Proposed Changes",
        "",
        f"- Routes: {count_new_records(seed['routes'], [], 'routes')}",
        f"- Places: {count_new_records(seed['places'], drafted_places(drafts), 'places')}",
        f"- Events: {count_new_records(seed['events'], drafts['events'].get('events', []), 'events')}",
        f"- Connections: {count_new_records(seed['connections'], drafts['connections'].get('connections', []), 'connections')}",
        "",
        "## Warnings",
        "",
    ]
    if warnings:
        lines.extend(f"- {warning}" for warning in warnings)
    else:
        lines.append("- None")
    lines.extend(["", "## Validation", ""])
    errors = validate_seed_payloads(merged)
    if errors:
        lines.extend(f"- {error}" for error in errors)
    else:
        lines.append("- Seed preview validates against current schemas and references.")
    lines.append("")
    return "\n".join(lines)


def preview_warnings(
    route_id: str,
    seed: dict[str, dict[str, Any]],
    drafts: dict[str, dict[str, Any]],
    merged: dict[str, dict[str, Any]],
) -> list[str]:
    warnings = []
    if not any(route.get("id") == route_id for route in seed["routes"].get("routes", [])):
        warnings.append(f"Route `{route_id}` does not exist in seed routes.")
    for event in drafts["events"].get("events", []):
        if not event.get("source_urls"):
            warnings.append(f"Event `{event.get('id')}` has no source URLs.")
        if event.get("year_start") == 0 or event.get("year_end") == 0:
            warnings.append(f"Event `{event.get('id')}` needs a reviewed year range.")
    for place in drafted_places(drafts):
        if place.get("latitude") == 0.0 and place.get("longitude") == 0.0:
            warnings.append(f"Place `{place.get('id')}` needs reviewed coordinates.")
        if place.get("place_type") == "review" or place.get("borough") == "review":
            warnings.append(f"Place `{place.get('id')}` needs reviewed place metadata.")
    warnings.extend(validate_seed_payloads(merged))
    return warnings


def count_new_records(
    seed_payload: dict[str, Any],
    draft_records: list[dict[str, Any]],
    collection_key: str,
) -> str:
    seed_ids = {
        item.get("id")
        for item in seed_payload.get(collection_key, [])
        if isinstance(item, dict)
    }
    new_count = sum(1 for item in draft_records if item.get("id") not in seed_ids)
    update_count = sum(1 for item in draft_records if item.get("id") in seed_ids)
    return f"{new_count} new, {update_count} update"


def promote_to_seed(
    *,
    content_root: Path,
    seed_dir: Path,
    route_id: str,
    write: bool,
) -> str:
    route_dir = route_dir_for(content_root, route_id)
    manifest = load_or_create_manifest(route_dir, route_id)
    report = build_seed_preview_report(route_dir=route_dir, seed_dir=seed_dir, manifest=manifest)
    if not write:
        return report

    framing_status = manifest["steps"]["event_framing"].get("review_status")
    if framing_status != "reviewed":
        raise ValueError(
            "Refusing to write seed files until event_framing review_status is 'reviewed' "
            "in pipeline.json.",
        )

    merged = build_merged_seed_payloads(route_dir=route_dir, seed_dir=seed_dir)
    errors = validate_seed_payloads(merged)
    if errors:
        raise ValueError("Refusing to write invalid seed data:\n" + "\n".join(errors))

    write_json(seed_dir / "places.json", merged["places"])
    write_json(seed_dir / "events.json", merged["events"])
    write_json(seed_dir / "connections.json", merged["connections"])
    return report + "\nSeed files written.\n"


def build_merged_seed_payloads(route_dir: Path, seed_dir: Path) -> dict[str, dict[str, Any]]:
    seed = load_seed_payloads(seed_dir)
    drafts = load_draft_payloads(route_dir)
    return {
        "routes": seed["routes"],
        "places": upsert_records(seed["places"], "places", drafted_places(drafts)),
        "events": upsert_records(seed["events"], "events", drafts["events"].get("events", [])),
        "connections": upsert_records(
            seed["connections"],
            "connections",
            drafts["connections"].get("connections", []),
        ),
    }


def load_seed_payloads(seed_dir: Path) -> dict[str, dict[str, Any]]:
    return {
        "routes": read_json(seed_dir / "routes.json"),
        "places": read_json(seed_dir / "places.json"),
        "events": read_json(seed_dir / "events.json"),
        "connections": read_json(seed_dir / "connections.json"),
    }


def load_draft_payloads(route_dir: Path) -> dict[str, dict[str, Any]]:
    return {
        "events": read_optional_json(route_dir / "event-framing.json", {"events": []}),
        "places": read_optional_json(route_dir / "place-framing.json", {"places": []}),
        "connections": read_optional_json(route_dir / "connection-framing.json", {"connections": []}),
    }


def drafted_places(drafts: dict[str, dict[str, Any]]) -> list[dict[str, Any]]:
    places = []
    for decision in drafts["places"].get("places", []):
        if decision.get("decision") == "new" and isinstance(decision.get("place"), dict):
            places.append(decision["place"])
    return places


def upsert_records(
    payload: dict[str, Any],
    collection_key: str,
    draft_records: list[dict[str, Any]],
) -> dict[str, Any]:
    next_payload = json.loads(json.dumps(payload))
    records = [
        record
        for record in next_payload.get(collection_key, [])
        if isinstance(record, dict)
    ]
    draft_by_id = {
        record["id"]: record
        for record in draft_records
        if isinstance(record, dict) and isinstance(record.get("id"), str)
    }
    next_records = []
    seen_ids = set()
    for record in records:
        record_id = record.get("id")
        if record_id in draft_by_id:
            next_records.append(draft_by_id[record_id])
            seen_ids.add(record_id)
        else:
            next_records.append(record)
    for record_id, draft in draft_by_id.items():
        if record_id not in seen_ids:
            next_records.append(draft)
    next_payload[collection_key] = next_records
    return next_payload


def validate_seed_payloads(payloads: dict[str, dict[str, Any]]) -> list[str]:
    errors = []
    routes = validate_collection(payloads["routes"], "routes", Route, errors)
    places = validate_collection(payloads["places"], "places", Place, errors)
    events = validate_collection(payloads["events"], "events", Event, errors)
    connections = validate_collection(payloads["connections"], "connections", Connection, errors)
    route_ids = {route.id for route in routes}
    place_ids = {place.id for place in places}
    event_ids = {event.id for event in events}
    for event in events:
        if event.route_id not in route_ids:
            errors.append(f"Event `{event.id}` references unknown route `{event.route_id}`.")
        if event.place_id not in place_ids:
            errors.append(f"Event `{event.id}` references unknown place `{event.place_id}`.")
    for connection in connections:
        if connection.from_event_id not in event_ids:
            errors.append(
                f"Connection `{connection.id}` references unknown source event "
                f"`{connection.from_event_id}`.",
            )
        if connection.to_event_id not in event_ids:
            errors.append(
                f"Connection `{connection.id}` references unknown target event "
                f"`{connection.to_event_id}`.",
            )
    return errors


def validate_collection(
    payload: dict[str, Any],
    collection_key: str,
    model: type[Route] | type[Place] | type[Event] | type[Connection],
    errors: list[str],
) -> list[Any]:
    valid = []
    for item in payload.get(collection_key, []):
        try:
            valid.append(model(**item))
        except Exception as exc:
            errors.append(f"{collection_key} `{item.get('id', '<missing>')}` failed schema validation: {exc}")
    return valid


def format_validation_report(errors: list[str]) -> str:
    lines = ["# Route Pipeline Validation", ""]
    if errors:
        lines.append("Validation failed:")
        lines.extend(f"- {error}" for error in errors)
    else:
        lines.append("Validation passed.")
    lines.append("")
    return "\n".join(lines)


def format_init_summary(route_dir: Path, manifest: dict[str, Any]) -> str:
    return "\n".join(
        [
            "Route content pipeline initialized",
            f"Route: {manifest['route_id']}",
            f"Directory: {relative_repo_path(route_dir)}",
            f"Active dossier: {manifest['active_dossier']}",
        ],
    )


def format_run_summary(results: list[dict[str, Any]]) -> str:
    lines = ["Route content pipeline run"]
    for result in results:
        outputs = ", ".join(result.get("outputs", [])) or "no outputs"
        detail = ""
        if "candidates" in result:
            detail = f" ({result['candidates']} candidate event(s))"
        lines.append(f"- {result['step']}: {result['status']} {outputs}{detail}")
    return "\n".join(lines)


def format_status(route_dir: Path, manifest: dict[str, Any]) -> str:
    lines = [
        "Route content pipeline status",
        f"Route: {manifest['route_id']}",
        f"Directory: {relative_repo_path(route_dir)}",
        f"Active dossier: {manifest['active_dossier']}",
        "",
        "Steps",
    ]
    for step_name, step in manifest["steps"].items():
        outputs = step_outputs(route_dir, step)
        output_status = ", ".join(
            f"{path.name}:{'present' if path.exists() else 'missing'}"
            for path in outputs
        )
        lines.append(
            f"- {step_name}: review={step.get('review_status', 'draft')} "
            f"outputs={output_status or 'none'}",
        )
    return "\n".join(lines)


def step_outputs(route_dir: Path, step: dict[str, Any]) -> list[Path]:
    outputs = []
    for key in ("markdown", "json", "events", "places", "connections"):
        if isinstance(step.get(key), str):
            outputs.append(route_dir / step[key])
    return outputs


def load_seed_collection(seed_dir: Path, collection_key: str) -> list[dict[str, Any]]:
    path = seed_dir / f"{collection_key}.json"
    if not path.exists():
        return []
    payload = read_json(path)
    return [
        item
        for item in payload.get(collection_key, [])
        if isinstance(item, dict)
    ]


def read_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def read_optional_json(path: Path, default: dict[str, Any]) -> dict[str, Any]:
    if not path.exists():
        return default
    return read_json(path)


def write_json(path: Path, payload: dict[str, Any], renew: bool = False) -> None:
    if path.exists() and renew:
        backup_file(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def write_text(path: Path, content: str, renew: bool = False) -> None:
    if path.exists() and renew:
        backup_file(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


def backup_file(path: Path) -> None:
    backup_path = path.with_name(path.name + ".bak")
    shutil.copy2(path, backup_path)


def relative_repo_path(path: Path) -> str:
    try:
        return str(path.relative_to(REPO_ROOT))
    except ValueError:
        return str(path)


if __name__ == "__main__":
    raise SystemExit(main())
