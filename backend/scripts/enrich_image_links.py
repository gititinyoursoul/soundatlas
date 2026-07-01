import argparse
import html
import json
import re
import sys
import time
from pathlib import Path
from typing import Any, Callable
from urllib.parse import quote

BACKEND_ROOT = Path(__file__).resolve().parents[1]
if str(BACKEND_ROOT) not in sys.path:
    sys.path.insert(0, str(BACKEND_ROOT))

from app.link_ignores import build_ignored_link_index, link_is_ignored
from app.media_enrichment.image_query_planner import ImageQueryPlan, plan_image_queries
from app.media_enrichment.retrieval_brief import build_retrieval_brief
from app.media_enrichment.services import MediaProviderError, request_json
from app.schemas import ImageLink


REPO_ROOT = Path(__file__).resolve().parents[2]
DATA_SEED_DIR = REPO_ROOT / "data" / "seed"
EVENTS_PATH = DATA_SEED_DIR / "events.json"
ROUTES_PATH = DATA_SEED_DIR / "routes.json"
PLACES_PATH = DATA_SEED_DIR / "places.json"
WIKIMEDIA_API_URL = "https://commons.wikimedia.org/w/api.php"
SUPPORTED_PROVIDERS = {"wikimedia"}
SUPPORTED_QUERY_PLANNERS = {"legacy", "v2"}
IMAGE_DEDUPE_FIELDS = ("image_url", "thumbnail_url", "source_url")
MIN_CONFIDENCE = 0.45
MAX_QUERIES_PER_EVENT = 6
SEARCH_RESULTS_PER_QUERY = 8

RequestJson = Callable[[str, dict[str, str] | None], dict[str, Any]]
WIKIMEDIA_USER_AGENT = (
    "SoundAtlas/0.1 (https://soundatlas.local; contact: local-development)"
)
WIKIMEDIA_MAXLAG_SECONDS = "1"
WIKIMEDIA_REQUEST_CACHE: dict[tuple[str, tuple[tuple[str, str], ...]], dict[str, Any]] = {}


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Add draft Wikimedia Commons image candidates to event image links.",
    )
    parser.add_argument("--event-id", help="Only enrich one event.")
    parser.add_argument("--route-id", help="Only enrich events in one route.")
    parser.add_argument(
        "--limit",
        type=int,
        default=5,
        help="Maximum image links to add per event.",
    )
    parser.add_argument(
        "--provider",
        action="append",
        choices=sorted(SUPPORTED_PROVIDERS),
        help="Image provider to query. May be repeated. Defaults to wikimedia.",
    )
    parser.add_argument("--dry-run", action="store_true", help="Print changes without writing.")
    parser.add_argument(
        "--json",
        action="store_true",
        help="With --dry-run, print the full changed seed payload as JSON.",
    )
    parser.add_argument(
        "--preview-queries",
        action="store_true",
        help="Print planned image queries without calling providers or writing seed data.",
    )
    parser.add_argument(
        "--query-planner",
        choices=sorted(SUPPORTED_QUERY_PLANNERS),
        default="v2",
        help="Query planner to use for provider searches. Defaults to v2.",
    )
    args = parser.parse_args(argv)

    providers = args.provider or ["wikimedia"]
    if args.limit < 1:
        print("--limit must be at least 1.", file=sys.stderr)
        return 2
    if args.json and not args.dry_run:
        print("--json can only be used with --dry-run.", file=sys.stderr)
        return 2

    events_payload = read_json(EVENTS_PATH)
    routes_payload = read_json(ROUTES_PATH)
    places_payload = read_json(PLACES_PATH)
    try:
        selected_event_ids = [
            event["id"]
            for event in select_events(
                events_payload=events_payload,
                routes_payload=routes_payload,
                event_id=args.event_id,
                route_id=args.route_id,
            )
            if isinstance(event.get("id"), str)
        ]
    except ValueError as exc:
        print(str(exc), file=sys.stderr)
        return 2
    before_counts = link_counts_by_event_id(events_payload, selected_event_ids, "image_links")

    if args.preview_queries:
        try:
            print_image_query_preview(
                events_payload=events_payload,
                routes_payload=routes_payload,
                places_payload=places_payload,
                event_id=args.event_id,
                route_id=args.route_id,
                query_planner=args.query_planner,
            )
        except ValueError as exc:
            print(str(exc), file=sys.stderr)
            return 2
        return 0

    ignored_link_index = build_ignored_link_index(events_payload)

    try:
        changed_events = enrich_events_payload(
            events_payload=events_payload,
            routes_payload=routes_payload,
            places_payload=places_payload,
            event_id=args.event_id,
            route_id=args.route_id,
            limit=args.limit,
            providers=providers,
            query_planner=args.query_planner,
            ignored_link_index=ignored_link_index,
            request_fn=request_wikimedia_json,
        )
    except ValueError as exc:
        print(str(exc), file=sys.stderr)
        return 2

    if args.dry_run:
        if args.json:
            print(json.dumps(events_payload, indent=2, ensure_ascii=False))
        else:
            print(
                format_image_enrichment_summary(
                    events_payload=events_payload,
                    selected_event_ids=selected_event_ids,
                    before_counts=before_counts,
                    changed_events=changed_events,
                    event_id=args.event_id,
                    route_id=args.route_id,
                    limit=args.limit,
                    providers=providers,
                    query_planner=args.query_planner,
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
            format_image_enrichment_summary(
                events_payload=events_payload,
                selected_event_ids=selected_event_ids,
                before_counts=before_counts,
                changed_events=changed_events,
                event_id=args.event_id,
                route_id=args.route_id,
                limit=args.limit,
                providers=providers,
                query_planner=args.query_planner,
                dry_run=False,
                wrote_seed=changed_events > 0,
            ),
        )
    return 0


def read_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


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


def format_image_enrichment_summary(
    *,
    events_payload: dict[str, Any],
    selected_event_ids: list[str],
    before_counts: dict[str, int],
    changed_events: int,
    event_id: str | None,
    route_id: str | None,
    limit: int,
    providers: list[str],
    query_planner: str,
    dry_run: bool,
    wrote_seed: bool,
) -> str:
    after_counts = link_counts_by_event_id(events_payload, selected_event_ids, "image_links")
    added_total = sum(
        max(after_counts.get(event_id, 0) - before_counts.get(event_id, 0), 0)
        for event_id in selected_event_ids
    )
    lines = [
        "Image enrichment",
        f"Mode: {'dry-run (no files written)' if dry_run else 'write'}",
        f"Scope: {format_scope(event_id=event_id, route_id=route_id)}",
        f"Providers: {', '.join(providers)}",
        f"Query planner: {query_planner}",
        f"Limit: {limit} image link(s) per event",
        f"Events considered: {len(selected_event_ids)}",
        f"Changed events: {changed_events}",
        f"Added image links: {added_total}",
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
                f"  {current_event_id}: +{max(after - before, 0)} image link(s) "
                f"({before} -> {after})",
            )
    if dry_run:
        lines.extend(["", "Use --dry-run --json to inspect the full changed seed payload."])
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


def print_image_query_preview(
    events_payload: dict[str, Any],
    routes_payload: dict[str, Any],
    places_payload: dict[str, Any],
    event_id: str | None,
    route_id: str | None,
    query_planner: str,
) -> None:
    routes_by_id = build_routes_by_id(routes_payload)
    places_by_id = build_places_by_id(places_payload)
    events = select_events(
        events_payload=events_payload,
        routes_payload=routes_payload,
        event_id=event_id,
        route_id=route_id,
    )

    output_blocks = []
    for event in events:
        route = routes_by_id.get(event.get("route_id"), {})
        place = places_by_id.get(event.get("place_id"), {})
        output_blocks.append(
            format_image_query_preview(
                event=event,
                route=route,
                place=place,
                query_planner=query_planner,
            ),
        )

    print("\n\n".join(output_blocks))


def build_routes_by_id(routes_payload: dict[str, Any]) -> dict[str, dict[str, Any]]:
    return {
        route["id"]: route
        for route in routes_payload.get("routes", [])
        if isinstance(route, dict) and isinstance(route.get("id"), str)
    }


def build_places_by_id(places_payload: dict[str, Any]) -> dict[str, dict[str, Any]]:
    return {
        place["id"]: place
        for place in places_payload.get("places", [])
        if isinstance(place, dict) and isinstance(place.get("id"), str)
    }


def select_events(
    events_payload: dict[str, Any],
    routes_payload: dict[str, Any],
    event_id: str | None,
    route_id: str | None,
) -> list[dict[str, Any]]:
    events = [
        event
        for event in events_payload.get("events", [])
        if isinstance(event, dict) and event_matches_filters(event, event_id=event_id, route_id=route_id)
    ]

    if event_id and not events:
        raise ValueError(f"No event found for --event-id '{event_id}'.")
    if route_id and not any(route.get("id") == route_id for route in routes_payload.get("routes", [])):
        raise ValueError(f"No route found for --route-id '{route_id}'.")
    return events


def format_image_query_preview(
    event: dict[str, Any],
    route: dict[str, Any],
    place: dict[str, Any],
    query_planner: str,
) -> str:
    event_id = event.get("id") or "(unknown event)"
    lines = [f"Event: {event_id}"]
    if query_planner == "legacy":
        queries = build_event_image_queries(event=event, route=route, place=place)
        if not queries:
            lines.append("  No image queries planned.")
            return "\n".join(lines)
        lines.append("  legacy")
        for index, query in enumerate(queries, start=1):
            lines.append(f"    [{index}] {query}")
        return "\n".join(lines)
    if query_planner != "v2":
        raise ValueError(f"Unsupported query planner: {query_planner}")

    brief = build_retrieval_brief(event=event, route=route, place=place)
    plans = plan_image_queries(brief)
    if not plans:
        lines.append("  No image queries planned.")
        return "\n".join(lines)

    current_target_type = ""
    for plan in plans:
        if plan.target_type != current_target_type:
            current_target_type = plan.target_type
            lines.append(f"  {current_target_type}")
        lines.append(f"    [{plan.priority}/{plan.confidence_hint}] {plan.query}")
    return "\n".join(lines)


def request_wikimedia_json(
    url: str,
    params: dict[str, str] | None = None,
) -> dict[str, Any]:
    request_params = dict(params or {})
    request_params.setdefault("maxlag", WIKIMEDIA_MAXLAG_SECONDS)
    cache_key = (url, tuple(sorted(request_params.items())))
    cached = WIKIMEDIA_REQUEST_CACHE.get(cache_key)
    if cached is not None:
        return cached

    headers = {
        "User-Agent": WIKIMEDIA_USER_AGENT,
        "Accept-Encoding": "gzip",
    }

    delay = 1.0
    for attempt in range(3):
        try:
            response = request_json(url, params=request_params, headers=headers)
            WIKIMEDIA_REQUEST_CACHE[cache_key] = response
            return response
        except MediaProviderError as exc:
            if not should_retry_wikimedia_request(exc) or attempt == 2:
                raise
            time.sleep(delay)
            delay *= 2


def should_retry_wikimedia_request(exc: MediaProviderError) -> bool:
    message = str(exc).casefold()
    return any(
        marker in message
        for marker in ("ratelimited", "too many requests", "retry-after", "maxlag")
    )


def enrich_events_payload(
    events_payload: dict[str, Any],
    routes_payload: dict[str, Any],
    places_payload: dict[str, Any],
    event_id: str | None,
    route_id: str | None,
    limit: int,
    providers: list[str],
    query_planner: str = "v2",
    ignored_link_index: dict[tuple[str, str], set[str]] | None = None,
    request_fn: RequestJson = request_json,
) -> int:
    unsupported_providers = sorted(set(providers) - SUPPORTED_PROVIDERS)
    if unsupported_providers:
        raise ValueError(f"Unsupported provider(s): {', '.join(unsupported_providers)}")
    if query_planner not in SUPPORTED_QUERY_PLANNERS:
        raise ValueError(f"Unsupported query planner: {query_planner}")

    routes_by_id = build_routes_by_id(routes_payload)
    places_by_id = build_places_by_id(places_payload)
    events = select_events(
        events_payload=events_payload,
        routes_payload=routes_payload,
        event_id=event_id,
        route_id=route_id,
    )

    changed_events = 0
    for event in events:
        candidates: list[dict[str, Any]] = []
        route = routes_by_id.get(event.get("route_id"), {})
        place = places_by_id.get(event.get("place_id"), {})

        if "wikimedia" in providers:
            try:
                candidates.extend(
                    fetch_wikimedia_image_candidates(
                        event=event,
                        route=route,
                        place=place,
                        limit=limit,
                        query_planner=query_planner,
                        ignored_link_index=ignored_link_index,
                        request_fn=request_fn,
                    ),
                )
            except MediaProviderError as exc:
                print(
                    f"Warning: Wikimedia enrichment failed for {event.get('id')}: {exc}",
                    file=sys.stderr,
                )

        candidates = dedupe_image_links(candidates)
        existing_links = event.get("image_links", [])
        merged_links = merge_image_links(existing_links, candidates, limit=limit)
        if merged_links != existing_links:
            event["image_links"] = merged_links
            changed_events += 1

    return changed_events


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


def fetch_wikimedia_image_candidates(
    event: dict[str, Any],
    route: dict[str, Any],
    place: dict[str, Any],
    limit: int,
    query_planner: str = "v2",
    ignored_link_index: dict[tuple[str, str], set[str]] | None = None,
    request_fn: RequestJson = request_json,
) -> list[dict[str, Any]]:
    candidates: list[dict[str, Any]] = []
    for query in build_wikimedia_search_queries(
        event=event,
        route=route,
        place=place,
        query_planner=query_planner,
    ):
        titles = search_wikimedia_file_titles(query, request_fn=request_fn)
        if not titles:
            continue

        pages = fetch_wikimedia_imageinfo(titles, request_fn=request_fn)
        for page in pages:
            candidate = build_wikimedia_image_link(
                page=page,
                query=query,
                event=event,
                route=route,
                place=place,
            )
            if candidate and not (
                ignored_link_index
                and link_is_ignored(ignored_link_index, event["id"], "image", candidate)
            ):
                candidates.append(candidate)

        if len(dedupe_image_links(candidates)) >= limit:
            break

    return dedupe_image_links(candidates)[:limit]


def build_wikimedia_search_queries(
    event: dict[str, Any],
    route: dict[str, Any],
    place: dict[str, Any],
    query_planner: str,
) -> list[str]:
    if query_planner == "legacy":
        return build_event_image_queries(event=event, route=route, place=place)
    if query_planner == "v2":
        brief = build_retrieval_brief(event=event, route=route, place=place)
        return [plan.query for plan in plan_image_queries(brief)]
    raise ValueError(f"Unsupported query planner: {query_planner}")


def build_event_image_queries(
    event: dict[str, Any],
    route: dict[str, Any],
    place: dict[str, Any],
) -> list[str]:
    event_title = clean_query_part(event.get("title"))
    route_title = clean_query_part(route.get("title"))
    place_name = clean_query_part(place.get("name"))
    years = format_years(event.get("year_start"), event.get("year_end"))
    tags = [clean_query_part(tag) for tag in event.get("tags", []) if clean_query_part(tag)]
    tag_text = " ".join(tags[:3])
    notable_terms = extract_notable_terms(event, max_terms=4)
    text_terms = " ".join(notable_terms)
    place_type = str(place.get("place_type") or "").casefold()
    allow_broad_place_only_queries = place_type in {
        "building",
        "club",
        "housing_complex",
        "venue",
    }

    query_parts = [
        [event_title, place_name, years],
        [event_title],
        *([[place_name, years], [place_name]] if allow_broad_place_only_queries else []),
        *[[term] for term in notable_terms[:2]],
        [event_title, route_title, years],
        [event_title, text_terms, tag_text],
        [place_name, route_title, tag_text],
    ]

    queries = []
    seen_queries = set()
    for parts in query_parts:
        query = " ".join(part for part in parts if part).strip()
        query = re.sub(r"\s+", " ", query)
        if not query or query.casefold() in seen_queries:
            continue
        queries.append(query)
        seen_queries.add(query.casefold())

    return queries[:MAX_QUERIES_PER_EVENT]


def clean_query_part(value: Any) -> str:
    if not isinstance(value, str):
        return ""
    value = value.replace("&", "and").replace("-", " ")
    value = re.sub(r"['’]s\b", "", value)
    value = re.sub(r"[^\w\s]", " ", value)
    return re.sub(r"\s+", " ", value).strip()


def format_years(year_start: Any, year_end: Any) -> str:
    if not isinstance(year_start, int):
        return ""
    if isinstance(year_end, int) and year_end != year_start:
        return f"{year_start} {year_end}"
    return str(year_start)


def extract_notable_terms(event: dict[str, Any], max_terms: int) -> list[str]:
    text = " ".join(
        value
        for value in (event.get("summary"), event.get("significance"))
        if isinstance(value, str)
    )
    phrases = re.findall(r"\b(?:[A-Z][A-Za-z0-9']+)(?:\s+[A-Z][A-Za-z0-9']+)*\b", text)
    terms = []
    seen_terms = set()
    for phrase in phrases:
        normalized = phrase.strip()
        if len(normalized) < 4 or normalized.casefold() in seen_terms:
            continue
        terms.append(normalized)
        seen_terms.add(normalized.casefold())
        if len(terms) >= max_terms:
            break
    return terms


def search_wikimedia_file_titles(
    query: str,
    request_fn: RequestJson = request_json,
) -> list[str]:
    payload = request_fn(
        WIKIMEDIA_API_URL,
        {
            "action": "query",
            "format": "json",
            "list": "search",
            "srnamespace": "6",
            "srlimit": str(SEARCH_RESULTS_PER_QUERY),
            "srsearch": query,
        },
    )
    results = payload.get("query", {}).get("search", [])
    return [
        result["title"]
        for result in results
        if isinstance(result, dict)
        and isinstance(result.get("title"), str)
        and result["title"].startswith("File:")
    ]


def fetch_wikimedia_imageinfo(
    titles: list[str],
    request_fn: RequestJson = request_json,
) -> list[dict[str, Any]]:
    if not titles:
        return []

    payload = request_fn(
        WIKIMEDIA_API_URL,
        {
            "action": "query",
            "format": "json",
            "prop": "imageinfo",
            "titles": "|".join(titles),
            "iiprop": "url|mime|mediatype|extmetadata",
            "iiurlwidth": "600",
        },
    )
    pages = payload.get("query", {}).get("pages", {})
    if not isinstance(pages, dict):
        return []
    return [page for page in pages.values() if isinstance(page, dict)]


def build_wikimedia_image_link(
    page: dict[str, Any],
    query: str,
    event: dict[str, Any],
    route: dict[str, Any],
    place: dict[str, Any],
) -> dict[str, Any] | None:
    imageinfo = page.get("imageinfo")
    if not isinstance(imageinfo, list) or not imageinfo:
        return None
    info = imageinfo[0]
    if not isinstance(info, dict):
        return None

    image_url = info.get("url")
    source_url = info.get("descriptionurl") or wikimedia_file_url(page.get("title"))
    title = metadata_value(info, "ObjectName") or file_title_to_label(page.get("title"))
    mime = info.get("mime")
    media_type = str(info.get("mediatype") or "").upper()

    if not isinstance(image_url, str) or not image_url:
        return None
    if not isinstance(source_url, str) or not source_url:
        return None
    if isinstance(mime, str) and not mime.startswith("image/"):
        return None
    if media_type and media_type not in {"BITMAP", "DRAWING", "UNKNOWN"}:
        return None
    if not title:
        return None

    place_type = str(place.get("place_type") or "").casefold()
    query_specificity = any(
        [
            token_overlap_count(event.get("title"), query) >= 2,
            token_overlap_count(route.get("title"), query) >= 2,
        ],
    )
    if place_type in {"city", "region", "neighborhood"} and not query_specificity:
        return None

    creator = metadata_value(info, "Artist")
    license_name = metadata_value(info, "LicenseShortName") or metadata_value(info, "UsageTerms")
    license_url = metadata_value(info, "LicenseUrl")
    description = metadata_value(info, "ImageDescription")
    alt_text = build_alt_text(title=title, description=description, place=place)
    text_blob = " ".join(
        value
        for value in [
            title,
            description,
            creator,
            license_name,
            metadata_value(info, "Categories"),
            query,
        ]
        if value
    )
    confidence = score_image_candidate(
        text_blob=text_blob,
        event=event,
        route=route,
        place=place,
    )
    if confidence < MIN_CONFIDENCE:
        return None

    candidate = {
        "provider": "wikimedia",
        "type": infer_image_type(text_blob=text_blob, event=event, place=place),
        "title": title,
        "image_url": image_url,
        "source_url": source_url,
        "rights_status": infer_rights_status(license_name=license_name, license_url=license_url),
        "alt_text": alt_text,
        "query": query,
        "confidence": confidence,
        "review_status": "draft",
    }
    thumbnail_url = info.get("thumburl")
    if isinstance(thumbnail_url, str) and thumbnail_url:
        candidate["thumbnail_url"] = thumbnail_url
    if creator:
        candidate["creator"] = creator
    if license_name:
        candidate["license"] = license_name
    if license_url:
        candidate["license_url"] = license_url

    try:
        return ImageLink.model_validate(candidate).model_dump(exclude_none=True)
    except ValueError:
        return None


def metadata_value(info: dict[str, Any], key: str) -> str:
    extmetadata = info.get("extmetadata")
    if not isinstance(extmetadata, dict):
        return ""
    metadata = extmetadata.get(key)
    if not isinstance(metadata, dict):
        return ""
    value = metadata.get("value")
    if not isinstance(value, str):
        return ""
    return strip_markup(value)


def strip_markup(value: str) -> str:
    without_tags = re.sub(r"<[^>]*>", " ", value)
    return re.sub(r"\s+", " ", html.unescape(without_tags)).strip()


def wikimedia_file_url(title: Any) -> str:
    if not isinstance(title, str) or not title:
        return ""
    return f"https://commons.wikimedia.org/wiki/{quote(title.replace(' ', '_'), safe=':/_()-,.')}"


def file_title_to_label(title: Any) -> str:
    if not isinstance(title, str):
        return ""
    label = title.removeprefix("File:")
    label = re.sub(r"\.[A-Za-z0-9]{2,5}$", "", label)
    return label.replace("_", " ").strip()


def build_alt_text(title: str, description: str, place: dict[str, Any]) -> str:
    if description:
        return truncate_text(description, 180)
    place_name = place.get("name")
    if isinstance(place_name, str) and place_name:
        return truncate_text(f"{title}, related to {place_name}.", 180)
    return truncate_text(title, 180)


def truncate_text(value: str, max_length: int) -> str:
    value = re.sub(r"\s+", " ", value).strip()
    if len(value) <= max_length:
        return value
    return value[: max_length - 1].rstrip() + "..."


def infer_rights_status(license_name: str, license_url: str) -> str:
    text = f"{license_name} {license_url}".casefold()
    if any(marker in text for marker in ("public domain", "pd-", "cc0", "pdm")):
        return "public_domain"
    if any(
        marker in text
        for marker in (
            "cc by",
            "creative commons",
            "gnu free",
            "gfdl",
            "free art license",
            "fal",
        )
    ):
        return "open_license"
    return "unknown"


def infer_image_type(
    text_blob: str,
    event: dict[str, Any],
    place: dict[str, Any],
) -> str:
    text = text_blob.casefold()
    if any(term in text for term in ("flyer", "poster", "handbill")):
        return "flyer_poster"
    if any(term in text for term in ("album cover", "record cover", "single cover")):
        return "album_cover"
    if "map" in text:
        return "map_image"
    if any(term in text for term in ("newspaper", "magazine", "press", "article")):
        return "press_scan"
    if place.get("place_type") in {"building", "club", "park", "venue", "housing_complex"}:
        place_name = place.get("name")
        if isinstance(place_name, str) and token_overlap(place_name, text_blob):
            return "venue_photo"
    if any(
        tag in {"dj-culture", "turntablism", "band", "artist"}
        for tag in event.get("tags", [])
        if isinstance(tag, str)
    ) and any(term in text for term in ("portrait", "performing", "dj ", "musician")):
        return "artist_photo"
    return "archive_photo"


def score_image_candidate(
    text_blob: str,
    event: dict[str, Any],
    route: dict[str, Any],
    place: dict[str, Any],
) -> float:
    place_type = str(place.get("place_type") or "").casefold()
    has_specificity = any(
        [
            token_overlap(event.get("title"), text_blob),
            token_overlap(route.get("title"), text_blob),
            tag_overlap(event.get("tags", []), text_blob),
            token_overlap(event.get("summary"), text_blob),
            token_overlap(event.get("significance"), text_blob),
        ],
    )
    if place_type in {"city", "region", "neighborhood"} and not has_specificity:
        return 0.0

    score = 0.3
    if token_overlap(event.get("title"), text_blob):
        score += 0.25
    if token_overlap(place.get("name"), text_blob):
        score += 0.2
    if token_overlap(route.get("title"), text_blob):
        score += 0.1
    if tag_overlap(event.get("tags", []), text_blob):
        score += 0.15
    if year_overlap(event.get("year_start"), event.get("year_end"), text_blob):
        score += 0.1
    if token_overlap(event.get("summary"), text_blob) or token_overlap(
        event.get("significance"),
        text_blob,
    ):
        score += 0.05
    return round(min(score, 1.0), 2)


def token_overlap(value: Any, text_blob: str) -> bool:
    if not isinstance(value, str) or not value:
        return False
    text_tokens = meaningful_tokens(text_blob)
    value_tokens = meaningful_tokens(value)
    return bool(text_tokens & value_tokens)


def token_overlap_count(value: Any, text_blob: str) -> int:
    if not isinstance(value, str) or not value:
        return 0
    text_tokens = meaningful_tokens(text_blob)
    value_tokens = meaningful_tokens(value)
    return len(text_tokens & value_tokens)


def tag_overlap(tags: Any, text_blob: str) -> bool:
    if not isinstance(tags, list):
        return False
    text_tokens = meaningful_tokens(text_blob)
    tag_tokens = set()
    for tag in tags:
        if isinstance(tag, str):
            tag_tokens.update(meaningful_tokens(tag))
    return bool(text_tokens & tag_tokens)


def year_overlap(year_start: Any, year_end: Any, text_blob: str) -> bool:
    years = {str(year_start)}
    if isinstance(year_end, int):
        years.add(str(year_end))
    return any(year in text_blob for year in years if year and year != "None")


def meaningful_tokens(value: str) -> set[str]:
    stop_words = {
        "and",
        "the",
        "for",
        "with",
        "from",
        "into",
        "new",
        "york",
        "city",
        "photo",
        "image",
        "commons",
        "wikimedia",
    }
    return {
        token
        for token in re.findall(r"[a-z0-9]+", value.casefold())
        if len(token) >= 3 and token not in stop_words
    }


def merge_image_links(
    existing_links: list[dict[str, Any]],
    candidates: list[dict[str, Any]],
    limit: int,
) -> list[dict[str, Any]]:
    links = [link for link in existing_links if isinstance(link, dict)]
    seen_values = image_link_values(links)
    added = 0
    for candidate in candidates:
        candidate_values = image_link_values([candidate])
        if seen_values & candidate_values:
            continue
        links.append(candidate)
        seen_values.update(candidate_values)
        added += 1
        if added >= limit:
            break
    return links


def dedupe_image_links(image_links: list[dict[str, Any]]) -> list[dict[str, Any]]:
    deduped_links = []
    seen_values: set[str] = set()
    for image_link in image_links:
        current_values = image_link_values([image_link])
        if not current_values or seen_values & current_values:
            continue
        deduped_links.append(image_link)
        seen_values.update(current_values)
    return deduped_links


def image_link_values(image_links: list[dict[str, Any]]) -> set[str]:
    values = set()
    for image_link in image_links:
        for field in IMAGE_DEDUPE_FIELDS:
            value = image_link.get(field)
            if isinstance(value, str) and value:
                values.add(value)
    return values


if __name__ == "__main__":
    raise SystemExit(main())
