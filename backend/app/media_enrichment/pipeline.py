from app.media_enrichment.models import (
    ContentAnalysis,
    ContentPage,
    MediaLinkCandidate,
    RankedYouTubeVideo,
    YouTubeVideo,
    dedupe_preserving_order,
)
from app.media_enrichment.ranking import VideoRanker
from app.media_enrichment.services import (
    AuxiliaryProvider,
    ContentAnalyzer,
    YouTubeSearchService,
)


class ContentRecommendationPipeline:
    def __init__(self, analyzer: ContentAnalyzer) -> None:
        self.analyzer = analyzer

    def analyze_and_build_queries(
        self,
        content_page: ContentPage,
        *,
        fallback_query: str = "",
        query_limit: int = 3,
    ) -> tuple[ContentAnalysis, list[str]]:
        analysis = self.analyzer.analyze(content_page)
        base_queries = analysis.search_queries or ([fallback_query] if fallback_query else [])
        queries = dedupe_preserving_order(base_queries)
        return analysis, queries[:query_limit]


class YouTubeRecommendationPipeline:
    def __init__(
        self,
        analyzer: ContentAnalyzer,
        youtube_search_service: YouTubeSearchService,
        ranker: VideoRanker,
    ) -> None:
        self.analyzer = analyzer
        self.youtube_search_service = youtube_search_service
        self.ranker = ranker

    def recommend(
        self,
        content_page: ContentPage,
        *,
        analysis: ContentAnalysis | None = None,
        queries: list[str] | None = None,
        query_limit: int = 3,
        results_per_query: int = 5,
    ) -> tuple[ContentAnalysis, list[RankedYouTubeVideo]]:
        analysis = analysis or self.analyzer.analyze(content_page)
        search_queries = dedupe_preserving_order(
            queries if queries is not None else analysis.search_queries,
        )
        collected_videos: list[YouTubeVideo] = []
        for query in search_queries[:query_limit]:
            for video in self.youtube_search_service.search(query, results_per_query):
                if not video.matched_query:
                    video.matched_query = query
                collected_videos.append(video)
        deduped_videos = dedupe_youtube_videos(collected_videos)
        return analysis, self.ranker.rank(content_page, analysis, deduped_videos)


def dedupe_youtube_videos(videos: list[YouTubeVideo]) -> list[YouTubeVideo]:
    videos_by_key: dict[str, YouTubeVideo] = {}
    for video in videos:
        key = video.video_id or video.url
        if key not in videos_by_key:
            videos_by_key[key] = video
    return list(videos_by_key.values())


def collect_provider_candidates(
    provider: AuxiliaryProvider,
    queries: list[str],
    *,
    results_per_query: int,
    total_limit: int,
) -> list[MediaLinkCandidate]:
    collected_candidates: list[MediaLinkCandidate] = []
    for query in queries:
        collected_candidates.extend(provider.search(query)[:results_per_query])
    deduped_candidates = dedupe_media_link_candidates(collected_candidates)
    ranked_candidates = sorted(
        deduped_candidates,
        key=lambda candidate: (
            -float(candidate.confidence),
            candidate.provider,
            candidate.media_type,
            candidate.title.casefold(),
        ),
    )
    return ranked_candidates[:total_limit]


def dedupe_media_link_candidates(
    candidates: list[MediaLinkCandidate],
) -> list[MediaLinkCandidate]:
    candidates_by_url: dict[str, MediaLinkCandidate] = {}
    for candidate in candidates:
        if candidate.url not in candidates_by_url:
            candidates_by_url[candidate.url] = candidate
    return list(candidates_by_url.values())


def ranked_videos_to_media_links(
    ranked_videos: list[RankedYouTubeVideo],
) -> list[MediaLinkCandidate]:
    return [
        MediaLinkCandidate(
            provider="youtube",
            media_type="video",
            title=item.video.title,
            url=item.video.url,
            query=item.video.matched_query,
            confidence=item.score,
            video_id=item.video.video_id,
            channel_title=item.video.channel_title,
            description=item.video.description,
            published_at=item.video.published_at,
            reason=item.reason,
        )
        for item in ranked_videos
    ]
