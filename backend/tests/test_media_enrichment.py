from pathlib import Path

from app.media_enrichment.models import ContentAnalysis, ContentPage, YouTubeVideo
from app.media_enrichment.pipeline import (
    YouTubeRecommendationPipeline,
    ranked_videos_to_media_links,
)
from app.media_enrichment.ranking import HeuristicVideoRanker
from app.media_enrichment.services import (
    OpenAIContentAnalyzer,
    StaticYouTubeSearchService,
    YouTubeDataApiSearchService,
)
from app.media_enrichment.settings import MediaEnrichmentSettings


class FakeTransport:
    def __init__(self, payload: dict) -> None:
        self.payload = payload
        self.calls: list[dict] = []

    def complete_json(
        self,
        *,
        api_key: str,
        model: str,
        system_prompt: str,
        user_prompt: str,
    ) -> dict:
        self.calls.append(
            {
                "api_key": api_key,
                "model": model,
                "system_prompt": system_prompt,
                "user_prompt": user_prompt,
            },
        )
        return self.payload


class StaticAnalyzer:
    def analyze(self, content_page: ContentPage) -> ContentAnalysis:
        return ContentAnalysis(
            topic=content_page.title,
            mood="celebratory",
            audience="music history explorers",
            keywords=["bronx", "block party", "dj"],
            music_genres=["hip hop"],
            search_queries=["Bronx block party 1977", "DJ Kool Herc 1977"],
            notes="Static test analysis.",
        )


def test_settings_load_real_secrets_only_from_external_env_file(tmp_path: Path) -> None:
    secret_file = tmp_path / "soundatlas.env"
    secret_file.write_text(
        "\n".join(
            [
                "YOUTUBE_API_KEY=real-youtube-key",
                "SOUNDATLAS_OPENAI_API_KEY=real-openai-key",
                "SOUNDATLAS_USE_DUMMY_SERVICES=false",
            ],
        ),
        encoding="utf-8",
    )

    settings = MediaEnrichmentSettings.from_env(
        env={"SOUNDATLAS_ENV_FILE": str(secret_file)},
        codex_env_file=tmp_path / ".env.codex",
    )

    assert settings.env_source == "external"
    assert settings.env_file == secret_file
    assert settings.youtube_api_key == "real-youtube-key"
    assert settings.openai_api_key == "real-openai-key"
    assert settings.use_dummy_services is False


def test_settings_fall_back_to_dummy_codex_file(tmp_path: Path) -> None:
    codex_env_file = tmp_path / ".env.codex"
    codex_env_file.write_text(
        "\n".join(
            [
                "SOUNDATLAS_USE_DUMMY_SERVICES=true",
                "YOUTUBE_API_KEY=dummy-youtube-key",
            ],
        ),
        encoding="utf-8",
    )

    settings = MediaEnrichmentSettings.from_env(
        env={},
        codex_env_file=codex_env_file,
    )

    assert settings.env_source == "codex"
    assert settings.use_dummy_services is True
    assert settings.has_live_youtube_credentials is False


def test_openai_content_analyzer_only_receives_openai_key() -> None:
    transport = FakeTransport(
        {
            "topic": "Birth of Hip-Hop",
            "mood": "community-driven",
            "audience": "music history explorers",
            "keywords": ["bronx", "block party"],
            "music_genres": ["hip hop"],
            "search_queries": ["Bronx block party 1977"],
            "notes": "Structured test payload.",
        },
    )
    analyzer = OpenAIContentAnalyzer(
        api_key="openai-secret",
        model="gpt-4.1-mini",
        transport=transport,
    )

    analysis = analyzer.analyze(
        ContentPage(
            identifier="bronx-jam",
            title="Back to School Jam",
            route_title="Birth of Hip-Hop",
            summary="A foundational Bronx party.",
            text="DJ Kool Herc plays breakbeats for a Bronx crowd.",
            year_start=1973,
            year_end=1973,
        ),
    )

    assert analysis.search_queries == ["Bronx block party 1977"]
    assert transport.calls[0]["api_key"] == "openai-secret"
    assert "youtube-secret" not in transport.calls[0]["user_prompt"]


def test_youtube_data_api_service_normalizes_video_metadata() -> None:
    captured_request: dict = {}

    def fake_requester(url: str, params: dict[str, str], **_: object) -> dict:
        captured_request["url"] = url
        captured_request["params"] = params
        return {
            "items": [
                {
                    "id": {"videoId": "abc123"},
                    "snippet": {
                        "title": "Kool Herc live",
                        "channelTitle": "Archive TV",
                        "description": "Historic footage",
                        "publishedAt": "2009-04-01T00:00:00Z",
                    },
                },
            ],
        }

    service = YouTubeDataApiSearchService(
        api_key="youtube-secret",
        requester=fake_requester,
    )

    results = service.search("Bronx hip hop 1977", 3)

    assert captured_request["url"] == "https://www.googleapis.com/youtube/v3/search"
    assert captured_request["params"]["key"] == "youtube-secret"
    assert results[0].video_id == "abc123"
    assert results[0].channel_title == "Archive TV"
    assert results[0].matched_query == "Bronx hip hop 1977"


def test_pipeline_ranks_videos_and_converts_to_media_links() -> None:
    pipeline = YouTubeRecommendationPipeline(
        analyzer=StaticAnalyzer(),
        youtube_search_service=StaticYouTubeSearchService(
            {
                "Bronx block party 1977": [
                    YouTubeVideo(
                        title="Bronx Block Party 1977",
                        channel_title="Archive TV",
                        video_id="video-1",
                        url="https://www.youtube.com/watch?v=video-1",
                        description="Bronx party footage with DJs.",
                        published_at="2010-01-01T00:00:00Z",
                    ),
                ],
                "DJ Kool Herc 1977": [
                    YouTubeVideo(
                        title="DJ Kool Herc Interview",
                        channel_title="Hip Hop Archive",
                        video_id="video-2",
                        url="https://www.youtube.com/watch?v=video-2",
                        description="Interview about the early Bronx scene.",
                        published_at="2012-01-01T00:00:00Z",
                    ),
                ],
            },
        ),
        ranker=HeuristicVideoRanker(),
    )

    _, ranked = pipeline.recommend(
        ContentPage(
            identifier="bronx-jam",
            title="Bronx Block Party",
            route_title="Birth of Hip-Hop",
            summary="A Bronx DJ jam.",
            text="This page covers DJs, breakbeats and block party culture in the Bronx.",
            tags=("bronx", "dj", "block party"),
            year_start=1977,
            year_end=1977,
        ),
        query_limit=2,
        results_per_query=2,
    )
    media_links = ranked_videos_to_media_links(ranked)

    assert ranked[0].video.video_id == "video-1"
    assert media_links[0].provider == "youtube"
    assert media_links[0].channel_title == "Archive TV"
    assert media_links[0].reason
