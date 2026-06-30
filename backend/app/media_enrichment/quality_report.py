from __future__ import annotations

from collections import Counter
from statistics import mean
import re
from typing import Any

from app.link_ignores import link_is_ignored


GENERIC_QUERY_TOKENS = {
    "archive",
    "bronx",
    "club",
    "dj",
    "hip",
    "hop",
    "image",
    "music",
    "new",
    "nyc",
    "photo",
    "picture",
    "sound",
    "york",
}

STOP_WORDS = {
    "a",
    "an",
    "and",
    "at",
    "by",
    "for",
    "from",
    "in",
    "into",
    "of",
    "on",
    "the",
    "to",
    "with",
}


def build_quality_report(
    *,
    kind: str,
    events: list[dict[str, Any]],
    routes_by_id: dict[str, dict[str, Any]],
    places_by_id: dict[str, dict[str, Any]],
    raw_candidates_by_event_id: dict[str, list[dict[str, Any]]],
    planned_query_counts_by_event_id: dict[str, int] | None = None,
    query_counts_with_candidates_by_event_id: dict[str, int] | None = None,
    ignored_link_index: dict[tuple[str, str], set[str]] | None = None,
    limit: int | None = None,
    source: str = "dry_run",
    workflow: dict[str, Any] | None = None,
) -> dict[str, Any]:
    event_reports = []
    for event in events:
        event_id = event.get("id")
        if not isinstance(event_id, str):
            continue
        route = routes_by_id.get(event.get("route_id"), {})
        place = places_by_id.get(event.get("place_id"), {})
        event_reports.append(
            build_event_quality_report(
                kind=kind,
                event=event,
                route=route,
                place=place,
                raw_candidates=raw_candidates_by_event_id.get(event_id, []),
                existing_links=event.get(link_field_for_kind(kind), []),
                ignored_link_index=ignored_link_index,
                limit=limit,
                planned_query_count=(planned_query_counts_by_event_id or {}).get(event_id, 0),
                query_count_with_candidates=(query_counts_with_candidates_by_event_id or {}).get(
                    event_id,
                    0,
                ),
            ),
        )

    return {
        "kind": kind,
        "source": source,
        "workflow": workflow or {},
        "events": event_reports,
        "aggregate": aggregate_event_reports(event_reports),
    }


def build_seed_baseline_report(
    *,
    kind: str,
    events: list[dict[str, Any]],
    routes_by_id: dict[str, dict[str, Any]],
    places_by_id: dict[str, dict[str, Any]],
) -> dict[str, Any]:
    event_reports = []
    link_field = link_field_for_kind(kind)
    for event in events:
        event_id = event.get("id")
        if not isinstance(event_id, str):
            continue
        route = routes_by_id.get(event.get("route_id"), {})
        place = places_by_id.get(event.get("place_id"), {})
        links = [link for link in event.get(link_field, []) if isinstance(link, dict)]
        event_reports.append(
            build_event_quality_report(
                kind=kind,
                event=event,
                route=route,
                place=place,
                raw_candidates=links,
                existing_links=[],
                ignored_link_index=None,
                limit=None,
                planned_query_count=0,
                query_count_with_candidates=count_distinct_queries(links),
            ),
        )
    return {
        "kind": kind,
        "source": "seed_links",
        "workflow": {},
        "events": event_reports,
        "aggregate": aggregate_event_reports(event_reports),
    }


def build_event_quality_report(
    *,
    kind: str,
    event: dict[str, Any],
    route: dict[str, Any],
    place: dict[str, Any],
    raw_candidates: list[dict[str, Any]],
    existing_links: list[dict[str, Any]],
    ignored_link_index: dict[tuple[str, str], set[str]] | None,
    limit: int | None,
    planned_query_count: int,
    query_count_with_candidates: int,
) -> dict[str, Any]:
    event_id = str(event.get("id") or "")
    valid_raw_candidates = [
        candidate for candidate in raw_candidates if candidate_identity_values(kind, candidate)
    ]
    deduped_candidates, duplicate_count = dedupe_candidates(kind, valid_raw_candidates)

    ignored_candidates: list[dict[str, Any]] = []
    not_ignored_candidates: list[dict[str, Any]] = []
    for candidate in deduped_candidates:
        if ignored_link_index and link_is_ignored(ignored_link_index, event_id, kind, candidate):
            ignored_candidates.append(candidate)
        else:
            not_ignored_candidates.append(candidate)

    if limit is None:
        selected_candidates = not_ignored_candidates
        limit_dropped_count = 0
    else:
        selected_candidates = not_ignored_candidates[:limit]
        limit_dropped_count = max(len(not_ignored_candidates) - len(selected_candidates), 0)

    existing_values = identity_values_for_links(kind, existing_links)
    existing_duplicate_count = sum(
        1
        for candidate in selected_candidates
        if candidate_identity_values(kind, candidate) & existing_values
    )
    added_candidates = [
        candidate
        for candidate in selected_candidates
        if not candidate_identity_values(kind, candidate) & existing_values
    ]

    candidate_summaries = [
        summarize_candidate(
            kind=kind,
            candidate=candidate,
            event=event,
            route=route,
            place=place,
            would_add=not bool(candidate_identity_values(kind, candidate) & existing_values),
        )
        for candidate in selected_candidates
    ]
    specificity_values = [
        candidate["specificity"]
        for candidate in candidate_summaries
        if isinstance(candidate.get("specificity"), float)
    ]
    confidence_values = [
        candidate["confidence"]
        for candidate in candidate_summaries
        if isinstance(candidate.get("confidence"), (int, float))
    ]

    type_counts = Counter(
        candidate.get("type") or "unknown"
        for candidate in candidate_summaries
        if isinstance(candidate, dict)
    )
    provider_counts = Counter(
        candidate.get("provider") or "unknown"
        for candidate in candidate_summaries
        if isinstance(candidate, dict)
    )
    rights_status_counts = Counter(
        candidate.get("rights_status") or "unknown"
        for candidate in candidate_summaries
        if kind == "image" and isinstance(candidate, dict)
    )

    report = {
        "event_id": event_id,
        "event_title": event.get("title") or "",
        "route_id": event.get("route_id") or "",
        "raw_candidate_count": len(valid_raw_candidates),
        "deduped_candidate_count": len(deduped_candidates),
        "duplicate_count": duplicate_count,
        "ignored_match_count": len(ignored_candidates),
        "existing_duplicate_count": existing_duplicate_count,
        "added_count": len(added_candidates),
        "final_candidate_count": len(selected_candidates),
        "limit_dropped_count": limit_dropped_count,
        "planned_query_count": planned_query_count,
        "query_count_with_candidates": query_count_with_candidates,
        "candidate_query_coverage": safe_ratio(query_count_with_candidates, planned_query_count),
        "average_specificity": round(mean(specificity_values), 3) if specificity_values else None,
        "low_specificity_count": sum(1 for value in specificity_values if value < 0.45),
        "high_specificity_count": sum(1 for value in specificity_values if value >= 0.7),
        "average_confidence": round(mean(confidence_values), 3) if confidence_values else None,
        "low_confidence_count": sum(1 for value in confidence_values if value < 0.45),
        "high_confidence_count": sum(1 for value in confidence_values if value >= 0.7),
        "missing_confidence_count": len(candidate_summaries) - len(confidence_values),
        "type_counts": dict(sorted(type_counts.items())),
        "provider_counts": dict(sorted(provider_counts.items())),
        "rights_status_counts": dict(sorted(rights_status_counts.items())),
        "candidates": candidate_summaries,
    }
    report["warnings"] = build_event_warnings(kind, report)
    return report


def compare_quality_reports(
    baseline: dict[str, Any],
    candidate: dict[str, Any],
    *,
    baseline_source: str = "baseline",
) -> dict[str, Any]:
    baseline_events = {
        event["event_id"]: event
        for event in baseline.get("events", [])
        if isinstance(event, dict) and isinstance(event.get("event_id"), str)
    }
    candidate_events = {
        event["event_id"]: event
        for event in candidate.get("events", [])
        if isinstance(event, dict) and isinstance(event.get("event_id"), str)
    }
    event_comparisons = []
    for event_id in sorted(set(baseline_events) | set(candidate_events)):
        baseline_event = baseline_events.get(event_id, empty_event_report(event_id))
        candidate_event = candidate_events.get(event_id, empty_event_report(event_id))
        event_comparisons.append(
            compare_event_reports(
                event_id=event_id,
                baseline_event=baseline_event,
                candidate_event=candidate_event,
            ),
        )

    return {
        "baseline_source": baseline_source,
        "events": event_comparisons,
        "aggregate": aggregate_comparisons(event_comparisons),
    }


def compare_event_reports(
    *,
    event_id: str,
    baseline_event: dict[str, Any],
    candidate_event: dict[str, Any],
) -> dict[str, Any]:
    baseline_candidates = [
        candidate
        for candidate in baseline_event.get("candidates", [])
        if isinstance(candidate, dict)
    ]
    candidate_candidates = [
        candidate
        for candidate in candidate_event.get("candidates", [])
        if isinstance(candidate, dict)
    ]
    baseline_values = summary_identity_values(baseline_candidates)
    candidate_values = summary_identity_values(candidate_candidates)
    new_candidates = [
        candidate
        for candidate in candidate_candidates
        if not summary_identity_values([candidate]) & baseline_values
    ]
    lost_candidates = [
        candidate
        for candidate in baseline_candidates
        if not summary_identity_values([candidate]) & candidate_values
    ]
    comparison = {
        "event_id": event_id,
        "baseline_candidate_count": baseline_event.get(
            "final_candidate_count",
            baseline_event.get("added_count", 0),
        ),
        "candidate_candidate_count": candidate_event.get(
            "final_candidate_count",
            candidate_event.get("added_count", 0),
        ),
        "delta_candidate_count": numeric_delta(
            baseline_event.get("final_candidate_count", baseline_event.get("added_count")),
            candidate_event.get("final_candidate_count", candidate_event.get("added_count")),
        ),
        "baseline_added_count": baseline_event.get("added_count", 0),
        "candidate_added_count": candidate_event.get("added_count", 0),
        "delta_added_count": numeric_delta(
            baseline_event.get("added_count"),
            candidate_event.get("added_count"),
        ),
        "delta_average_specificity": numeric_delta(
            baseline_event.get("average_specificity"),
            candidate_event.get("average_specificity"),
        ),
        "delta_average_confidence": numeric_delta(
            baseline_event.get("average_confidence"),
            candidate_event.get("average_confidence"),
        ),
        "delta_ignored_match_count": numeric_delta(
            baseline_event.get("ignored_match_count"),
            candidate_event.get("ignored_match_count"),
        ),
        "delta_duplicate_count": numeric_delta(
            baseline_event.get("duplicate_count"),
            candidate_event.get("duplicate_count"),
        ),
        "new_candidate_identity_count": len(new_candidates),
        "lost_candidate_identity_count": len(lost_candidates),
        "type_count_deltas": count_deltas(
            baseline_event.get("type_counts", {}),
            candidate_event.get("type_counts", {}),
        ),
        "provider_count_deltas": count_deltas(
            baseline_event.get("provider_counts", {}),
            candidate_event.get("provider_counts", {}),
        ),
        "rights_status_count_deltas": count_deltas(
            baseline_event.get("rights_status_counts", {}),
            candidate_event.get("rights_status_counts", {}),
        ),
        "type_quality_deltas": compare_quality_by_field(
            baseline_candidates,
            candidate_candidates,
            "type",
        ),
        "new_candidates": compact_candidate_list(new_candidates),
        "lost_candidates": compact_candidate_list(lost_candidates),
        "warnings": sorted(
            set(candidate_event.get("warnings", []))
            | comparison_warnings(baseline_event, candidate_event),
        ),
    }
    comparison["quality_direction"] = quality_direction(comparison)
    return comparison


def summarize_candidate(
    *,
    kind: str,
    candidate: dict[str, Any],
    event: dict[str, Any],
    route: dict[str, Any],
    place: dict[str, Any],
    would_add: bool = True,
) -> dict[str, Any]:
    specificity = score_specificity(candidate=candidate, event=event, route=route, place=place)
    summary = {
        "identity": primary_identity(kind, candidate),
        "provider": candidate.get("provider") or "unknown",
        "type": candidate.get("type") or "unknown",
        "title": candidate.get("title") or "",
        "query": candidate.get("query") or "",
        "confidence": normalized_confidence(candidate.get("confidence")),
        "specificity": specificity,
        "review_status": candidate.get("review_status") or "",
        "would_add": would_add,
    }
    if kind == "image":
        summary["rights_status"] = candidate.get("rights_status") or "unknown"
        summary["source_url"] = candidate.get("source_url") or ""
        summary["image_url"] = candidate.get("image_url") or ""
    else:
        summary["url"] = candidate.get("url") or ""
    return summary


def score_specificity(
    *,
    candidate: dict[str, Any],
    event: dict[str, Any],
    route: dict[str, Any],
    place: dict[str, Any],
) -> float:
    text_blob = " ".join(
        str(value)
        for value in [
            candidate.get("title"),
            candidate.get("query"),
            candidate.get("url"),
            candidate.get("source_url"),
        ]
        if value
    )
    query = str(candidate.get("query") or "")
    score = 0.0
    if token_overlap_count(event.get("title"), text_blob) >= 2:
        score += 0.25
    elif token_overlap(event.get("title"), text_blob):
        score += 0.15
    if token_overlap(place.get("name"), text_blob):
        score += 0.2
    if token_overlap_count(route.get("title"), text_blob) >= 2:
        score += 0.1
    if tag_overlap(event.get("tags", []), text_blob):
        score += 0.15
    if year_overlap(event.get("year_start"), event.get("year_end"), text_blob):
        score += 0.1
    if token_overlap(event.get("summary"), text_blob) or token_overlap(
        event.get("significance"),
        text_blob,
    ):
        score += 0.1
    if has_identifying_query(query):
        score += 0.1
    if is_generic_query(query):
        score -= 0.15
    return round(min(max(score, 0.0), 1.0), 3)


def aggregate_event_reports(event_reports: list[dict[str, Any]]) -> dict[str, Any]:
    additive_fields = [
        "raw_candidate_count",
        "deduped_candidate_count",
        "duplicate_count",
        "ignored_match_count",
        "existing_duplicate_count",
        "added_count",
        "final_candidate_count",
        "limit_dropped_count",
        "planned_query_count",
        "query_count_with_candidates",
        "low_specificity_count",
        "high_specificity_count",
        "low_confidence_count",
        "high_confidence_count",
        "missing_confidence_count",
    ]
    aggregate = {
        "event_count": len(event_reports),
        "events_with_no_candidates": sum(
            1 for report in event_reports if report.get("final_candidate_count") == 0
        ),
        "events_with_added_candidates": sum(
            1 for report in event_reports if report.get("added_count", 0) > 0
        ),
    }
    for field in additive_fields:
        aggregate[field] = sum(int(report.get(field) or 0) for report in event_reports)

    specificity_values = [
        report["average_specificity"]
        for report in event_reports
        if isinstance(report.get("average_specificity"), (int, float))
    ]
    confidence_values = [
        report["average_confidence"]
        for report in event_reports
        if isinstance(report.get("average_confidence"), (int, float))
    ]
    aggregate["average_specificity"] = (
        round(mean(specificity_values), 3) if specificity_values else None
    )
    aggregate["average_confidence"] = (
        round(mean(confidence_values), 3) if confidence_values else None
    )
    aggregate["candidate_query_coverage"] = safe_ratio(
        aggregate["query_count_with_candidates"],
        aggregate["planned_query_count"],
    )
    aggregate["type_counts"] = merge_count_maps(
        [report.get("type_counts", {}) for report in event_reports],
    )
    aggregate["provider_counts"] = merge_count_maps(
        [report.get("provider_counts", {}) for report in event_reports],
    )
    aggregate["rights_status_counts"] = merge_count_maps(
        [report.get("rights_status_counts", {}) for report in event_reports],
    )
    aggregate["warnings"] = sorted(
        {
            warning
            for report in event_reports
            for warning in report.get("warnings", [])
            if isinstance(warning, str)
        },
    )
    return aggregate


def aggregate_comparisons(comparisons: list[dict[str, Any]]) -> dict[str, Any]:
    additive_fields = [
        "delta_candidate_count",
        "delta_added_count",
        "delta_ignored_match_count",
        "delta_duplicate_count",
        "new_candidate_identity_count",
        "lost_candidate_identity_count",
    ]
    aggregate = {"event_count": len(comparisons)}
    for field in additive_fields:
        aggregate[field] = sum(int(comparison.get(field) or 0) for comparison in comparisons)
    aggregate["type_count_deltas"] = merge_count_maps(
        [comparison.get("type_count_deltas", {}) for comparison in comparisons],
    )
    aggregate["provider_count_deltas"] = merge_count_maps(
        [comparison.get("provider_count_deltas", {}) for comparison in comparisons],
    )
    aggregate["rights_status_count_deltas"] = merge_count_maps(
        [comparison.get("rights_status_count_deltas", {}) for comparison in comparisons],
    )
    aggregate["direction_counts"] = dict(
        sorted(Counter(comparison.get("quality_direction") for comparison in comparisons).items()),
    )
    aggregate["warnings"] = sorted(
        {
            warning
            for comparison in comparisons
            for warning in comparison.get("warnings", [])
            if isinstance(warning, str)
        },
    )
    return aggregate


def build_event_warnings(kind: str, report: dict[str, Any]) -> list[str]:
    warnings = []
    if report["final_candidate_count"] == 0:
        warnings.append("no_candidates")
    if report["raw_candidate_count"] > 0 and report["ignored_match_count"] == report["deduped_candidate_count"]:
        warnings.append("all_candidates_ignored")
    if report["limit_dropped_count"] > 0:
        warnings.append("limit_reached")
    if report["final_candidate_count"] > 0 and report["low_specificity_count"] == report["final_candidate_count"]:
        warnings.append("only_low_specificity_candidates")
    if report["final_candidate_count"] > 0 and report["low_confidence_count"] == report["final_candidate_count"]:
        warnings.append("only_low_confidence_candidates")
    if any(not candidate.get("query") for candidate in report.get("candidates", [])):
        warnings.append("missing_query")
    if any(not candidate.get("title") for candidate in report.get("candidates", [])):
        warnings.append("missing_title")
    if kind == "media":
        type_counts = report.get("type_counts", {})
        if type_counts.get("playlist", 0) > 0 and type_counts.get("video", 0) == 0:
            warnings.append("playlist_only")
        if report["final_candidate_count"] > 0 and type_counts.get("video", 0) == 0:
            warnings.append("no_videos")
    if kind == "image":
        rights_counts = report.get("rights_status_counts", {})
        if rights_counts.get("unknown", 0) > 0:
            warnings.append("unknown_rights_status")
        if any(not candidate.get("source_url") for candidate in report.get("candidates", [])):
            warnings.append("missing_source_url")
    return sorted(set(warnings))


def comparison_warnings(
    baseline_event: dict[str, Any],
    candidate_event: dict[str, Any],
) -> set[str]:
    warnings = set()
    baseline_types = baseline_event.get("type_counts", {})
    candidate_types = candidate_event.get("type_counts", {})
    if baseline_types.get("venue_photo", 0) > 0 and candidate_types.get("venue_photo", 0) == 0:
        warnings.add("lost_all_venue_photos")
    if baseline_types.get("video", 0) > candidate_types.get("video", 0):
        warnings.add("fewer_reviewable_videos")
    baseline_unknown_rights = baseline_event.get("rights_status_counts", {}).get("unknown", 0)
    candidate_unknown_rights = candidate_event.get("rights_status_counts", {}).get("unknown", 0)
    if candidate_unknown_rights > baseline_unknown_rights:
        warnings.add("more_unknown_rights_images")
    if (
        candidate_types.get("archive_photo", 0) > baseline_types.get("archive_photo", 0)
        and candidate_types.get("venue_photo", 0) < baseline_types.get("venue_photo", 0)
    ):
        warnings.add("candidate_mix_shifted_to_generic_archive_photos")
    return warnings


def quality_direction(comparison: dict[str, Any]) -> str:
    score = 0
    if (comparison.get("delta_candidate_count") or 0) > 0:
        score += 1
    elif (comparison.get("delta_candidate_count") or 0) < 0:
        score -= 1
    if (comparison.get("delta_average_specificity") or 0) > 0.05:
        score += 1
    elif (comparison.get("delta_average_specificity") or 0) < -0.05:
        score -= 1
    if (comparison.get("delta_average_confidence") or 0) > 0.05:
        score += 1
    elif (comparison.get("delta_average_confidence") or 0) < -0.05:
        score -= 1
    if (comparison.get("lost_candidate_identity_count") or 0) > (
        comparison.get("new_candidate_identity_count") or 0
    ):
        score -= 1
    if score > 0 and comparison.get("warnings"):
        return "mixed"
    if score > 0:
        return "improved"
    if score < 0:
        return "regressed"
    return "unchanged"


def dedupe_candidates(
    kind: str,
    candidates: list[dict[str, Any]],
) -> tuple[list[dict[str, Any]], int]:
    deduped = []
    seen_values: set[str] = set()
    duplicate_count = 0
    for candidate in candidates:
        values = candidate_identity_values(kind, candidate)
        if not values:
            continue
        if seen_values & values:
            duplicate_count += 1
            continue
        deduped.append(candidate)
        seen_values.update(values)
    return deduped, duplicate_count


def candidate_identity_values(kind: str, candidate: dict[str, Any]) -> set[str]:
    if kind == "media":
        value = candidate.get("url")
        return {value} if isinstance(value, str) and value else set()
    if kind == "image":
        values = set()
        for field in ("source_url", "image_url", "thumbnail_url"):
            value = candidate.get(field)
            if isinstance(value, str) and value:
                values.add(value)
        return values
    raise ValueError(f"Unsupported report kind: {kind}")


def primary_identity(kind: str, candidate: dict[str, Any]) -> str:
    fields = ("url",) if kind == "media" else ("source_url", "image_url", "thumbnail_url")
    for field in fields:
        value = candidate.get(field)
        if isinstance(value, str) and value:
            return value
    return ""


def identity_values_for_links(kind: str, links: list[dict[str, Any]]) -> set[str]:
    values = set()
    for link in links:
        if isinstance(link, dict):
            values.update(candidate_identity_values(kind, link))
    return values


def summary_identity_values(candidates: list[dict[str, Any]]) -> set[str]:
    values = set()
    for candidate in candidates:
        for field in ("identity", "url", "source_url", "image_url"):
            value = candidate.get(field)
            if isinstance(value, str) and value:
                values.add(value)
    return values


def link_field_for_kind(kind: str) -> str:
    if kind == "media":
        return "media_links"
    if kind == "image":
        return "image_links"
    raise ValueError(f"Unsupported report kind: {kind}")


def normalized_confidence(value: Any) -> float | None:
    if isinstance(value, (int, float)):
        return round(float(value), 3)
    return None


def count_distinct_queries(candidates: list[dict[str, Any]]) -> int:
    return len(
        {
            candidate.get("query")
            for candidate in candidates
            if isinstance(candidate, dict)
            and isinstance(candidate.get("query"), str)
            and candidate.get("query")
        },
    )


def safe_ratio(numerator: int, denominator: int) -> float | None:
    if denominator <= 0:
        return None
    return round(numerator / denominator, 3)


def numeric_delta(baseline: Any, candidate: Any) -> float | int | None:
    if not isinstance(baseline, (int, float)) or not isinstance(candidate, (int, float)):
        return None
    delta = candidate - baseline
    if isinstance(baseline, int) and isinstance(candidate, int):
        return int(delta)
    return round(delta, 3)


def count_deltas(
    baseline_counts: dict[str, Any],
    candidate_counts: dict[str, Any],
) -> dict[str, int]:
    keys = sorted(set(baseline_counts) | set(candidate_counts))
    return {
        key: int(candidate_counts.get(key, 0) or 0) - int(baseline_counts.get(key, 0) or 0)
        for key in keys
    }


def compare_quality_by_field(
    baseline_candidates: list[dict[str, Any]],
    candidate_candidates: list[dict[str, Any]],
    field: str,
) -> dict[str, dict[str, Any]]:
    values = sorted(
        {
            str(candidate.get(field) or "unknown")
            for candidate in baseline_candidates + candidate_candidates
        },
    )
    comparisons = {}
    for value in values:
        baseline_group = [candidate for candidate in baseline_candidates if (candidate.get(field) or "unknown") == value]
        candidate_group = [candidate for candidate in candidate_candidates if (candidate.get(field) or "unknown") == value]
        comparisons[value] = {
            "baseline_count": len(baseline_group),
            "candidate_count": len(candidate_group),
            "delta_count": len(candidate_group) - len(baseline_group),
            "delta_average_specificity": numeric_delta(
                average_field(baseline_group, "specificity"),
                average_field(candidate_group, "specificity"),
            ),
            "delta_average_confidence": numeric_delta(
                average_field(baseline_group, "confidence"),
                average_field(candidate_group, "confidence"),
            ),
        }
    return comparisons


def average_field(candidates: list[dict[str, Any]], field: str) -> float | None:
    values = [
        candidate[field]
        for candidate in candidates
        if isinstance(candidate.get(field), (int, float))
    ]
    return round(mean(values), 3) if values else None


def merge_count_maps(count_maps: list[dict[str, Any]]) -> dict[str, int]:
    merged: Counter[str] = Counter()
    for count_map in count_maps:
        for key, value in count_map.items():
            if isinstance(key, str) and isinstance(value, (int, float)):
                merged[key] += int(value)
    return dict(sorted(merged.items()))


def compact_candidate_list(candidates: list[dict[str, Any]]) -> list[dict[str, Any]]:
    return [
        {
            "identity": candidate.get("identity") or "",
            "type": candidate.get("type") or "unknown",
            "title": candidate.get("title") or "",
            "specificity": candidate.get("specificity"),
            "confidence": candidate.get("confidence"),
        }
        for candidate in candidates
    ]


def empty_event_report(event_id: str) -> dict[str, Any]:
    return {
        "event_id": event_id,
        "added_count": 0,
        "average_specificity": None,
        "average_confidence": None,
        "ignored_match_count": 0,
        "duplicate_count": 0,
        "type_counts": {},
        "provider_counts": {},
        "rights_status_counts": {},
        "candidates": [],
        "warnings": [],
    }


def token_overlap(value: Any, text_blob: str) -> bool:
    return token_overlap_count(value, text_blob) > 0


def token_overlap_count(value: Any, text_blob: str) -> int:
    if not isinstance(value, str) or not value:
        return 0
    return len(meaningful_tokens(value) & meaningful_tokens(text_blob))


def tag_overlap(tags: Any, text_blob: str) -> bool:
    if not isinstance(tags, list):
        return False
    tag_tokens = set()
    for tag in tags:
        if isinstance(tag, str):
            tag_tokens.update(meaningful_tokens(tag.replace("-", " ")))
    return bool(tag_tokens & meaningful_tokens(text_blob))


def year_overlap(year_start: Any, year_end: Any, text_blob: str) -> bool:
    years = {str(year_start)}
    if isinstance(year_end, int):
        years.add(str(year_end))
    return any(year in text_blob for year in years if year and year != "None")


def has_identifying_query(query: str) -> bool:
    tokens = meaningful_tokens(query)
    specific_tokens = tokens - GENERIC_QUERY_TOKENS
    return len(specific_tokens) >= 2


def is_generic_query(query: str) -> bool:
    tokens = meaningful_tokens(query)
    if not tokens:
        return False
    return tokens <= GENERIC_QUERY_TOKENS or len(tokens - GENERIC_QUERY_TOKENS) <= 1


def meaningful_tokens(value: str) -> set[str]:
    return {
        token
        for token in re.findall(r"[a-z0-9]+", value.casefold())
        if len(token) >= 2 and token not in STOP_WORDS
    }
