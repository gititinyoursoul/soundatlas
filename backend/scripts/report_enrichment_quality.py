import argparse
import json
import sys
from pathlib import Path
from typing import Any

BACKEND_ROOT = Path(__file__).resolve().parents[1]
if str(BACKEND_ROOT) not in sys.path:
    sys.path.insert(0, str(BACKEND_ROOT))

from app.link_ignores import build_ignored_link_index
from app.media_enrichment.quality_report import (
    build_quality_report,
    build_seed_baseline_report,
    compare_quality_reports,
)
from app.media_enrichment.services import MediaProviderError
from scripts.enrich_image_links import (
    EVENTS_PATH,
    PLACES_PATH,
    ROUTES_PATH,
    build_places_by_id,
    build_routes_by_id,
    build_wikimedia_search_queries,
    build_wikimedia_image_link,
    dedupe_image_links,
    fetch_wikimedia_imageinfo,
    request_wikimedia_json,
    search_wikimedia_file_titles,
    select_events,
)
from scripts.enrich_media_links import (
    DEFAULT_OUTPUT_DIR,
    build_media_link_from_youtube_item,
    confidence_hint_to_score,
    load_youtube_result_payloads,
)


SUPPORTED_KINDS = {"media", "image"}


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Report dry-run quality metrics for SoundAtlas enrichment candidates.",
    )
    parser.add_argument("--kind", choices=sorted(SUPPORTED_KINDS), required=True)
    parser.add_argument("--event-id", help="Only report one event.")
    parser.add_argument("--route-id", help="Only report events in one route.")
    parser.add_argument(
        "--limit",
        type=int,
        help="Candidate limit per event. Defaults to 3 for media and 5 for image.",
    )
    parser.add_argument(
        "--results-dir",
        type=Path,
        default=DEFAULT_OUTPUT_DIR,
        help="Directory containing normalized YouTube result files for media reports.",
    )
    parser.add_argument(
        "--query-planner",
        choices=["legacy", "v2"],
        default="v2",
        help="Image query planner to evaluate. Ignored for media reports.",
    )
    parser.add_argument(
        "--compare-to",
        type=Path,
        help="Compare this report to a previously saved quality report JSON.",
    )
    parser.add_argument(
        "--baseline-from-seed",
        action="store_true",
        help="Compare this report to current seed media_links or image_links.",
    )
    parser.add_argument(
        "--json",
        action="store_true",
        help="Print full JSON instead of the default text summary.",
    )
    args = parser.parse_args(argv)

    if args.limit is not None and args.limit < 1:
        print("--limit must be at least 1.", file=sys.stderr)
        return 2

    limit = args.limit if args.limit is not None else default_limit(args.kind)

    try:
        events_payload = read_json(EVENTS_PATH)
        routes_payload = read_json(ROUTES_PATH)
        places_payload = read_json(PLACES_PATH)
        events = select_events(
            events_payload=events_payload,
            routes_payload=routes_payload,
            event_id=args.event_id,
            route_id=args.route_id,
        )
        routes_by_id = build_routes_by_id(routes_payload)
        places_by_id = build_places_by_id(places_payload)
        ignored_link_index = build_ignored_link_index(events_payload)

        if args.kind == "media":
            report = build_media_quality_report(
                events=events,
                routes_by_id=routes_by_id,
                places_by_id=places_by_id,
                ignored_link_index=ignored_link_index,
                results_dir=args.results_dir,
                event_id=args.event_id,
                limit=limit,
            )
        else:
            report = build_image_quality_report(
                events=events,
                routes_by_id=routes_by_id,
                places_by_id=places_by_id,
                ignored_link_index=ignored_link_index,
                query_planner=args.query_planner,
                limit=limit,
            )
    except ValueError as exc:
        print(str(exc), file=sys.stderr)
        return 2

    baseline = None
    baseline_source = ""
    if args.compare_to:
        baseline = read_json(args.compare_to)
        baseline_source = str(args.compare_to)
    elif args.baseline_from_seed:
        baseline = build_seed_baseline_report(
            kind=args.kind,
            events=events,
            routes_by_id=routes_by_id,
            places_by_id=places_by_id,
        )
        baseline_source = "seed_links"

    if baseline:
        report["comparison"] = compare_quality_reports(
            baseline,
            report,
            baseline_source=baseline_source,
        )

    if args.json:
        print(json.dumps(report, indent=2, ensure_ascii=False))
    else:
        print(format_quality_report(report))
    return 0


def build_media_quality_report(
    *,
    events: list[dict[str, Any]],
    routes_by_id: dict[str, dict[str, Any]],
    places_by_id: dict[str, dict[str, Any]],
    ignored_link_index: dict[tuple[str, str], set[str]],
    results_dir: Path,
    event_id: str | None,
    limit: int,
) -> dict[str, Any]:
    result_payloads = load_youtube_result_payloads(results_dir, event_id=event_id)
    raw_candidates_by_event_id: dict[str, list[dict[str, Any]]] = {}
    planned_query_counts_by_event_id: dict[str, int] = {}
    query_counts_with_candidates_by_event_id: dict[str, int] = {}

    for payload in result_payloads:
        current_event_id = payload.get("event_id")
        if not isinstance(current_event_id, str):
            continue
        candidates, planned_query_count, query_count_with_candidates = extract_media_report_inputs(payload)
        raw_candidates_by_event_id[current_event_id] = candidates
        planned_query_counts_by_event_id[current_event_id] = planned_query_count
        query_counts_with_candidates_by_event_id[current_event_id] = query_count_with_candidates

    return build_quality_report(
        kind="media",
        events=events,
        routes_by_id=routes_by_id,
        places_by_id=places_by_id,
        raw_candidates_by_event_id=raw_candidates_by_event_id,
        planned_query_counts_by_event_id=planned_query_counts_by_event_id,
        query_counts_with_candidates_by_event_id=query_counts_with_candidates_by_event_id,
        ignored_link_index=ignored_link_index,
        limit=limit,
        source="youtube_results",
        workflow={"results_dir": str(results_dir)},
    )


def extract_media_report_inputs(
    result_payload: dict[str, Any],
) -> tuple[list[dict[str, Any]], int, int]:
    candidates = []
    planned_query_count = 0
    queries_with_candidates: set[str] = set()
    for result_group in sorted(
        result_payload.get("results", []),
        key=lambda result: int(result.get("review_priority") or 999),
    ):
        planned_query_count += 1
        confidence = confidence_hint_to_score(result_group.get("confidence_hint"))
        group_candidates = []
        for item in result_group.get("items", []):
            candidate = build_media_link_from_youtube_item(item, result_group, confidence)
            if candidate:
                candidates.append(candidate)
                group_candidates.append(candidate)
        if group_candidates:
            query = result_group.get("request", {}).get("params", {}).get("q")
            if isinstance(query, str) and query:
                queries_with_candidates.add(query)
            else:
                queries_with_candidates.add(str(planned_query_count))
    return candidates, planned_query_count, len(queries_with_candidates)


def build_image_quality_report(
    *,
    events: list[dict[str, Any]],
    routes_by_id: dict[str, dict[str, Any]],
    places_by_id: dict[str, dict[str, Any]],
    ignored_link_index: dict[tuple[str, str], set[str]],
    query_planner: str,
    limit: int,
) -> dict[str, Any]:
    raw_candidates_by_event_id: dict[str, list[dict[str, Any]]] = {}
    planned_query_counts_by_event_id: dict[str, int] = {}
    query_counts_with_candidates_by_event_id: dict[str, int] = {}

    for event in events:
        event_id = event.get("id")
        if not isinstance(event_id, str):
            continue
        route = routes_by_id.get(event.get("route_id"), {})
        place = places_by_id.get(event.get("place_id"), {})
        try:
            candidates, planned_query_count, query_count_with_candidates = extract_image_report_inputs(
                event=event,
                route=route,
                place=place,
                query_planner=query_planner,
                limit=limit,
            )
        except MediaProviderError as exc:
            print(
                f"Warning: Wikimedia quality report failed for {event_id}: {exc}",
                file=sys.stderr,
            )
            candidates = []
            planned_query_count = 0
            query_count_with_candidates = 0
        raw_candidates_by_event_id[event_id] = candidates
        planned_query_counts_by_event_id[event_id] = planned_query_count
        query_counts_with_candidates_by_event_id[event_id] = query_count_with_candidates

    return build_quality_report(
        kind="image",
        events=events,
        routes_by_id=routes_by_id,
        places_by_id=places_by_id,
        raw_candidates_by_event_id=raw_candidates_by_event_id,
        planned_query_counts_by_event_id=planned_query_counts_by_event_id,
        query_counts_with_candidates_by_event_id=query_counts_with_candidates_by_event_id,
        ignored_link_index=ignored_link_index,
        limit=limit,
        source="wikimedia_dry_run",
        workflow={"query_planner": query_planner},
    )


def extract_image_report_inputs(
    *,
    event: dict[str, Any],
    route: dict[str, Any],
    place: dict[str, Any],
    query_planner: str,
    limit: int,
) -> tuple[list[dict[str, Any]], int, int]:
    queries = build_wikimedia_search_queries(
        event=event,
        route=route,
        place=place,
        query_planner=query_planner,
    )
    candidates = []
    queries_with_candidates = 0
    for query in queries:
        titles = search_wikimedia_file_titles(query, request_fn=request_wikimedia_json)
        if not titles:
            continue

        pages = fetch_wikimedia_imageinfo(titles, request_fn=request_wikimedia_json)
        query_candidates = []
        for page in pages:
            candidate = build_wikimedia_image_link(
                page=page,
                query=query,
                event=event,
                route=route,
                place=place,
            )
            if candidate:
                candidates.append(candidate)
                query_candidates.append(candidate)
        if query_candidates:
            queries_with_candidates += 1

        if len(dedupe_image_links(candidates)) >= limit:
            break

    return candidates, len(queries), queries_with_candidates


def format_quality_report(report: dict[str, Any]) -> str:
    lines = [
        f"Enrichment quality report: {report.get('kind')}",
        f"Source: {report.get('source')}",
        "",
    ]
    if report.get("kind") == "media" and report.get("source") == "youtube_results":
        lines.extend(
            [
                "Note: media reports read saved YouTube result files and do not call the YouTube API.",
                "To evaluate query-planning changes, run the new request plan first and point --results-dir at those results.",
                "",
            ],
        )
    aggregate = report.get("aggregate", {})
    lines.extend(
        [
            "Aggregate",
            f"  events: {aggregate.get('event_count', 0)}",
            f"  added candidates: {aggregate.get('added_count', 0)}",
            f"  raw candidates: {aggregate.get('raw_candidate_count', 0)}",
            f"  ignored matches: {aggregate.get('ignored_match_count', 0)}",
            f"  duplicates: {aggregate.get('duplicate_count', 0)}",
            f"  avg specificity: {format_optional(aggregate.get('average_specificity'))}",
            f"  avg confidence: {format_optional(aggregate.get('average_confidence'))}",
            f"  type counts: {format_counts(aggregate.get('type_counts', {}))}",
        ],
    )
    if report.get("kind") == "image":
        lines.append(
            f"  rights counts: {format_counts(aggregate.get('rights_status_counts', {}))}",
        )
    if aggregate.get("warnings"):
        lines.append(f"  warnings: {', '.join(aggregate['warnings'])}")

    lines.extend(["", "Events"])
    for event in report.get("events", []):
        lines.append(
            "  "
            + f"{event.get('event_id')}: added {event.get('added_count', 0)} "
            + f"(raw {event.get('raw_candidate_count', 0)}, ignored {event.get('ignored_match_count', 0)}, "
            + f"duplicates {event.get('duplicate_count', 0)}, specificity {format_optional(event.get('average_specificity'))}, "
            + f"confidence {format_optional(event.get('average_confidence'))})",
        )
        if event.get("type_counts"):
            lines.append(f"    types: {format_counts(event['type_counts'])}")
        if event.get("warnings"):
            lines.append(f"    warnings: {', '.join(event['warnings'])}")

    comparison = report.get("comparison")
    if comparison:
        lines.extend(["", f"Comparison baseline: {comparison.get('baseline_source')}", "Comparison aggregate"])
        comp_aggregate = comparison.get("aggregate", {})
        lines.extend(
            [
                f"  delta candidates: {comp_aggregate.get('delta_candidate_count', 0):+d}",
                f"  delta newly added: {comp_aggregate.get('delta_added_count', 0):+d}",
                f"  new identities: {comp_aggregate.get('new_candidate_identity_count', 0)}",
                f"  lost identities: {comp_aggregate.get('lost_candidate_identity_count', 0)}",
                f"  type deltas: {format_signed_counts(comp_aggregate.get('type_count_deltas', {}))}",
                f"  direction counts: {format_counts(comp_aggregate.get('direction_counts', {}))}",
            ],
        )
        if comp_aggregate.get("warnings"):
            lines.append(f"  warnings: {', '.join(comp_aggregate['warnings'])}")
        lines.extend(["", "Comparison events"])
        for comparison_event in comparison.get("events", []):
            lines.append(
                "  "
                + f"{comparison_event.get('event_id')}: "
                + f"{comparison_event.get('baseline_candidate_count', 0)} -> {comparison_event.get('candidate_candidate_count', 0)} "
                + f"({comparison_event.get('delta_candidate_count', 0):+d}), "
                + f"would add {comparison_event.get('candidate_added_count', 0)}, "
                + f"new {comparison_event.get('new_candidate_identity_count', 0)}, "
                + f"lost {comparison_event.get('lost_candidate_identity_count', 0)}, "
                + f"{comparison_event.get('quality_direction')}",
            )
            if comparison_event.get("type_count_deltas"):
                lines.append(
                    f"    type deltas: {format_signed_counts(comparison_event['type_count_deltas'])}",
                )
            if comparison_event.get("warnings"):
                lines.append(f"    warnings: {', '.join(comparison_event['warnings'])}")
    return "\n".join(lines)


def read_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def default_limit(kind: str) -> int:
    return 3 if kind == "media" else 5


def format_optional(value: Any) -> str:
    if value is None:
        return "n/a"
    return str(value)


def format_counts(counts: dict[str, Any]) -> str:
    if not counts:
        return "none"
    return ", ".join(f"{key}={value}" for key, value in sorted(counts.items()))


def format_signed_counts(counts: dict[str, Any]) -> str:
    if not counts:
        return "none"
    return ", ".join(f"{key}={int(value):+d}" for key, value in sorted(counts.items()))


if __name__ == "__main__":
    raise SystemExit(main())
