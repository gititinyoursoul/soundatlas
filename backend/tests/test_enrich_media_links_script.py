from app.media_enrichment.models import ContentAnalysis, ContentPage, MediaLinkCandidate
from app.media_enrichment.pipeline import YouTubeRecommendationPipeline
from app.media_enrichment.ranking import HeuristicVideoRanker
from app.media_enrichment.services import StaticYouTubeSearchService
from app.media_enrichment.models import YouTubeVideo
from scripts.enrich_media_links import enrich_events_payload


class StaticAnalyzer:
    def analyze(self, content_page: ContentPage) -> ContentAnalysis:
        return ContentAnalysis(
            topic=content_page.title,
            mood="community-driven",
            audience="music history explorers",
            keywords=["bronx", "dj"],
            music_genres=["hip hop"],
            search_queries=["Kool Herc Bronx 1973"],
            notes="Script test analysis.",
        )


class StaticProvider:
    name = "spotify"

    def __init__(self) -> None:
        self.seen_queries: list[str] = []

    def search(self, query: str) -> list[MediaLinkCandidate]:
        self.seen_queries.append(query)
        return [
            MediaLinkCandidate(
                provider="spotify",
                media_type="track",
                title="The Message",
                url="https://open.spotify.com/track/example",
                query=query,
                confidence=0.62,
            ),
        ]


def test_enrich_events_payload_merges_existing_youtube_and_auxiliary_links() -> None:
    events_payload = {
        "events": [
            {
                "id": "kool-herc-back-to-school-jam",
                "route_id": "birth-of-hip-hop",
                "place_id": "1520-sedgwick-avenue",
                "title": "Back to School Jam",
                "year_start": 1973,
                "year_end": 1973,
                "summary": "Bronx party",
                "significance": "Birth of a scene",
                "tags": ["bronx", "dj"],
                "source_urls": [],
                "review_status": "draft",
                "media_links": [
                    {
                        "provider": "youtube",
                        "type": "video",
                        "title": "Existing clip",
                        "url": "https://www.youtube.com/watch?v=existing",
                        "query": "existing",
                        "confidence": 0.5,
                        "review_status": "draft",
                    },
                ],
            },
        ],
    }
    pipeline = YouTubeRecommendationPipeline(
        analyzer=StaticAnalyzer(),
        youtube_search_service=StaticYouTubeSearchService(
            {
                "Kool Herc Bronx 1973": [
                    YouTubeVideo(
                        title="Kool Herc at 1520 Sedgwick",
                        channel_title="Archive TV",
                        video_id="fresh-video",
                        url="https://www.youtube.com/watch?v=fresh-video",
                        description="Historic footage.",
                        published_at="2011-01-01T00:00:00Z",
                    ),
                ],
            },
        ),
        ranker=HeuristicVideoRanker(),
    )

    provider = StaticProvider()

    changed_events = enrich_events_payload(
        events_payload=events_payload,
        route_title_by_id={"birth-of-hip-hop": "Birth of Hip-Hop"},
        event_id=None,
        content_pipeline=build_test_content_pipeline(),
        youtube_pipeline=pipeline,
        providers=[provider],
        provider_limit=2,
    )

    media_links = events_payload["events"][0]["media_links"]

    assert changed_events == 1
    assert len(media_links) == 3
    assert {link["provider"] for link in media_links} == {"spotify", "youtube"}
    assert any(link.get("video_id") == "fresh-video" for link in media_links)
    assert provider.seen_queries == ["Kool Herc Bronx 1973"]


def test_enrich_events_payload_uses_multiple_analyzed_queries_for_auxiliary_providers() -> None:
    class MultiQueryAnalyzer:
        def analyze(self, content_page: ContentPage) -> ContentAnalysis:
            return ContentAnalysis(
                topic=content_page.title,
                mood="community-driven",
                audience="music history explorers",
                keywords=["bronx", "block party", "dj"],
                music_genres=["hip hop"],
                search_queries=["Kool Herc Bronx 1973", "Bronx breakbeats song"],
                notes="Multi-query analysis.",
            )

    class RecordingProvider:
        name = "qobuz"

        def __init__(self) -> None:
            self.seen_queries: list[str] = []

        def search(self, query: str) -> list[MediaLinkCandidate]:
            self.seen_queries.append(query)
            return [
                MediaLinkCandidate(
                    provider="qobuz",
                    media_type="album",
                    title=f"Result for {query}",
                    url=f"https://play.qobuz.com/album/{len(self.seen_queries)}",
                    query=query,
                    confidence=0.55,
                ),
            ]

    provider = RecordingProvider()
    events_payload = {
        "events": [
            {
                "id": "kool-herc-back-to-school-jam",
                "route_id": "birth-of-hip-hop",
                "place_id": "1520-sedgwick-avenue",
                "title": "Back to School Jam",
                "year_start": 1973,
                "year_end": 1973,
                "summary": "Bronx party",
                "significance": "Birth of a scene",
                "tags": ["bronx", "dj"],
                "source_urls": [],
                "review_status": "draft",
                "media_links": [],
            },
        ],
    }

    changed_events = enrich_events_payload(
        events_payload=events_payload,
        route_title_by_id={"birth-of-hip-hop": "Birth of Hip-Hop"},
        event_id=None,
        content_pipeline=build_test_content_pipeline(analyzer=MultiQueryAnalyzer()),
        youtube_pipeline=None,
        providers=[provider],
        provider_limit=3,
    )

    assert changed_events == 1
    assert provider.seen_queries == ["Kool Herc Bronx 1973", "Bronx breakbeats song"]
    assert len(events_payload["events"][0]["media_links"]) == 2


def build_test_content_pipeline(
    analyzer: object | None = None,
):
    from app.media_enrichment.pipeline import ContentRecommendationPipeline

    return ContentRecommendationPipeline(analyzer=analyzer or StaticAnalyzer())
