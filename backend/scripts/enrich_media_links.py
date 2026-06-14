import argparse
import json
import sys
from pathlib import Path
from typing import Any

BACKEND_ROOT = Path(__file__).resolve().parents[1]
if str(BACKEND_ROOT) not in sys.path:
    sys.path.insert(0, str(BACKEND_ROOT))

from app.media_enrichment.models import ContentPage, MediaLinkCandidate
from app.media_enrichment.pipeline import (
    ContentRecommendationPipeline,
    collect_provider_candidates,
    YouTubeRecommendationPipeline,
    ranked_videos_to_media_links,
)
from app.media_enrichment.ranking import HeuristicVideoRanker
from app.media_enrichment.services import (
    AuxiliaryProvider,
    HeuristicContentAnalyzer,
    MediaProviderError,
    YouTubeDataApiSearchService,
    build_auxiliary_providers,
)
from app.media_enrichment.settings import MediaEnrichmentSettings


REPO_ROOT = Path(__file__).resolve().parents[2]
SEED_DIR = REPO_ROOT / "data" / "seed"
EVENTS_PATH = SEED_DIR / "events.json"
ROUTES_PATH = SEED_DIR / "routes.json"


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Enrich SoundAtlas events with provider media links.",
    )
    parser.add_argument("--event-id", help="Only enrich one event.")
    parser.add_argument("--limit", type=int, default=3, help="Candidates per provider.")
    parser.add_argument("--dry-run", action="store_true", help="Print changes without writing.")
    args = parser.parse_args()

    try:
        settings = MediaEnrichmentSettings.from_env()
    except ValueError as exc:
        print(str(exc), file=sys.stderr)
        return 2

    routes_payload = read_json(ROUTES_PATH)
    events_payload = read_json(EVENTS_PATH)
    route_title_by_id = {
        route["id"]: route["title"] for route in routes_payload.get("routes", [])
    }
    content_pipeline = build_content_pipeline()
    youtube_pipeline = build_youtube_pipeline(settings, content_pipeline)
    providers = build_auxiliary_providers(settings, args.limit)

    if not youtube_pipeline and not providers:
        print(
            "No live provider credentials found. Set SOUNDATLAS_ENV_FILE or use mocks in tests.",
            file=sys.stderr,
        )
        return 2

    changed_events = enrich_events_payload(
        events_payload=events_payload,
        route_title_by_id=route_title_by_id,
        event_id=args.event_id,
        content_pipeline=content_pipeline,
        youtube_pipeline=youtube_pipeline,
        providers=providers,
        provider_limit=args.limit,
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


def build_query(event: dict[str, Any], route_title: str) -> str:
    years = (
        str(event["year_start"])
        if event["year_start"] == event["year_end"]
        else f'{event["year_start"]} {event["year_end"]}'
    )
    terms = [
        event["title"],
        route_title,
        years,
        " ".join(event.get("tags", [])[:5]),
        "music",
    ]
    return " ".join(term for term in terms if term).strip()


def build_event_content_page(
    event: dict[str, Any],
    route_title: str,
) -> ContentPage:
    text_fragments = [
        event.get("title", ""),
        route_title,
        event.get("summary", ""),
        event.get("significance", ""),
        " ".join(event.get("tags", [])),
    ]
    return ContentPage(
        identifier=event["id"],
        title=event["title"],
        text=" ".join(fragment for fragment in text_fragments if fragment).strip(),
        route_title=route_title,
        summary=event.get("summary", ""),
        tags=tuple(event.get("tags", [])),
        year_start=event.get("year_start"),
        year_end=event.get("year_end"),
    )


def enrich_events_payload(
    events_payload: dict[str, Any],
    route_title_by_id: dict[str, str],
    event_id: str | None,
    content_pipeline: ContentRecommendationPipeline,
    youtube_pipeline: YouTubeRecommendationPipeline | None,
    providers: list[AuxiliaryProvider],
    provider_limit: int,
) -> int:
    changed_events = 0
    for event in events_payload.get("events", []):
        if event_id and event["id"] != event_id:
            continue

        route_title = route_title_by_id.get(event["route_id"], "")
        candidates: list[MediaLinkCandidate] = []
        base_query = build_query(event, route_title)
        content_page = build_event_content_page(event, route_title)
        analysis, queries = content_pipeline.analyze_and_build_queries(
            content_page,
            fallback_query=base_query,
            query_limit=max(3, min(provider_limit, 5)),
        )

        if youtube_pipeline:
            try:
                _, ranked_videos = youtube_pipeline.recommend(
                    content_page,
                    analysis=analysis,
                    queries=queries,
                    query_limit=len(queries),
                    results_per_query=provider_limit,
                )
                candidates.extend(ranked_videos_to_media_links(ranked_videos[:provider_limit]))
            except MediaProviderError as exc:
                print(f"youtube: {exc}", file=sys.stderr)

        for provider in providers:
            try:
                candidates.extend(
                    collect_provider_candidates(
                        provider,
                        queries,
                        results_per_query=provider_limit,
                        total_limit=provider_limit,
                    ),
                )
            except MediaProviderError as exc:
                print(f"{provider.name}: {exc}", file=sys.stderr)

        if not candidates:
            continue

        existing_links = event.get("media_links", [])
        merged_links = merge_media_links(existing_links, candidates)
        if merged_links != existing_links:
            event["media_links"] = merged_links
            changed_events += 1
    return changed_events


def merge_media_links(
    existing_links: list[dict[str, Any]],
    candidates: list[MediaLinkCandidate],
) -> list[dict[str, Any]]:
    links_by_url = {
        link["url"]: link
        for link in existing_links
        if isinstance(link, dict) and isinstance(link.get("url"), str)
    }

    for candidate in candidates:
        payload = candidate.to_payload()
        links_by_url.setdefault(payload["url"], payload)

    return sorted(
        links_by_url.values(),
        key=lambda link: (link["provider"], link["type"], -float(link["confidence"])),
    )


def build_content_pipeline() -> ContentRecommendationPipeline:
    return ContentRecommendationPipeline(analyzer=HeuristicContentAnalyzer())


def build_youtube_pipeline(
    settings: MediaEnrichmentSettings,
    content_pipeline: ContentRecommendationPipeline,
) -> YouTubeRecommendationPipeline | None:
    if not settings.has_live_youtube_credentials:
        return None
    return YouTubeRecommendationPipeline(
        analyzer=content_pipeline.analyzer,
        youtube_search_service=YouTubeDataApiSearchService(settings.youtube_api_key or ""),
        ranker=HeuristicVideoRanker(),
    )


if __name__ == "__main__":
    raise SystemExit(main())
