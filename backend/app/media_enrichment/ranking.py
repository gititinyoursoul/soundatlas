import json
from typing import Any, Protocol

from app.media_enrichment.models import (
    ContentAnalysis,
    ContentPage,
    RankedYouTubeVideo,
    YouTubeVideo,
    normalize_terms,
)
from app.media_enrichment.services import LLMTransport


class VideoRanker(Protocol):
    def rank(
        self,
        content_page: ContentPage,
        analysis: ContentAnalysis,
        videos: list[YouTubeVideo],
    ) -> list[RankedYouTubeVideo]: ...


class HeuristicVideoRanker:
    def rank(
        self,
        content_page: ContentPage,
        analysis: ContentAnalysis,
        videos: list[YouTubeVideo],
    ) -> list[RankedYouTubeVideo]:
        page_terms = normalize_terms(
            " ".join(
                [
                    content_page.title,
                    content_page.route_title,
                    content_page.summary,
                    content_page.text,
                    " ".join(analysis.keywords),
                    " ".join(analysis.music_genres),
                ],
            ),
        )
        ranked: list[RankedYouTubeVideo] = []
        for video in videos:
            searchable_text = " ".join(
                [video.title, video.channel_title, video.description, video.matched_query],
            )
            video_terms = normalize_terms(searchable_text)
            overlap = len(page_terms & video_terms)
            overlap_score = overlap / max(len(page_terms), 1)
            query_terms = normalize_terms(video.matched_query)
            query_overlap = len(query_terms & video_terms) / max(len(query_terms), 1)
            title_bonus = 0.12 if normalize_terms(content_page.title) & video_terms else 0
            year_bonus = score_year_alignment(content_page, video)
            score = round(
                min(0.2 + (overlap_score * 1.6) + (query_overlap * 0.4) + title_bonus + year_bonus, 0.99),
                2,
            )
            ranked.append(
                RankedYouTubeVideo(
                    video=video,
                    score=score,
                    reason=build_reason(content_page, analysis, video, overlap, year_bonus > 0),
                ),
            )
        return sorted(
            ranked,
            key=lambda item: (-item.score, item.video.title.casefold(), item.video.video_id),
        )


class OpenAIVideoRanker:
    def __init__(
        self,
        api_key: str,
        model: str,
        transport: LLMTransport,
    ) -> None:
        self.api_key = api_key
        self.model = model
        self.transport = transport

    def rank(
        self,
        content_page: ContentPage,
        analysis: ContentAnalysis,
        videos: list[YouTubeVideo],
    ) -> list[RankedYouTubeVideo]:
        payload = self.transport.complete_json(
            api_key=self.api_key,
            model=self.model,
            system_prompt=(
                "You rank YouTube videos for a content page. Respond with strict JSON and"
                " never include secrets or API keys."
            ),
            user_prompt=json.dumps(
                {
                    "content_page": {
                        "title": content_page.title,
                        "route_title": content_page.route_title,
                        "summary": content_page.summary,
                        "text": content_page.text,
                        "year_start": content_page.year_start,
                        "year_end": content_page.year_end,
                    },
                    "analysis": {
                        "topic": analysis.topic,
                        "mood": analysis.mood,
                        "audience": analysis.audience,
                        "keywords": analysis.keywords,
                        "music_genres": analysis.music_genres,
                        "search_queries": analysis.search_queries,
                    },
                    "videos": [
                        {
                            "video_id": video.video_id,
                            "title": video.title,
                            "channel_title": video.channel_title,
                            "description": video.description,
                            "published_at": video.published_at,
                            "matched_query": video.matched_query,
                        }
                        for video in videos
                    ],
                    "response_schema": {
                        "ranked_videos": [
                            {
                                "video_id": "string",
                                "score": "float from 0 to 1",
                                "reason": "string",
                            },
                        ],
                    },
                },
                ensure_ascii=False,
            ),
        )
        scores_by_video_id = {
            str(item.get("video_id")): (
                max(0.0, min(float(item.get("score", 0)), 1.0)),
                str(item.get("reason") or "Ranked by OpenAI-compatible video ranker."),
            )
            for item in payload.get("ranked_videos", [])
            if item.get("video_id")
        }
        ranked = [
            RankedYouTubeVideo(
                video=video,
                score=round(scores_by_video_id.get(video.video_id, (0.0, ""))[0], 2),
                reason=scores_by_video_id.get(
                    video.video_id,
                    (0.0, "Ranked by OpenAI-compatible video ranker."),
                )[1],
            )
            for video in videos
            if video.video_id in scores_by_video_id
        ]
        return sorted(ranked, key=lambda item: (-item.score, item.video.title.casefold()))


def score_year_alignment(content_page: ContentPage, video: YouTubeVideo) -> float:
    years = {
        str(year)
        for year in [content_page.year_start, content_page.year_end]
        if year is not None
    }
    if not years:
        return 0.0
    searchable_text = " ".join(
        filter(None, [video.title, video.description, video.published_at or ""]),
    )
    if any(year in searchable_text for year in years):
        return 0.08
    return 0.0


def build_reason(
    content_page: ContentPage,
    analysis: ContentAnalysis,
    video: YouTubeVideo,
    overlap: int,
    has_year_match: bool,
) -> str:
    reason_parts = []
    if overlap:
        reason_parts.append(f"shares {overlap} core content keyword(s)")
    if analysis.music_genres:
        reason_parts.append(f"matches the {analysis.music_genres[0]} context")
    if has_year_match:
        reason_parts.append("includes the event timeframe")
    if normalize_terms(content_page.title) & normalize_terms(video.title):
        reason_parts.append("references the event title directly")
    if not reason_parts:
        reason_parts.append("fits the broader scene context")
    return "; ".join(reason_parts)
