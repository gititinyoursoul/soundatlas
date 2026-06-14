from scripts.run_youtube_search_requests import (
    build_dry_run_summary,
    normalize_youtube_search_items,
    run_request_plan,
)


def test_run_request_plan_injects_key_and_writes_redacted_results() -> None:
    captured_params = []

    def fake_requester(url: str, params: dict[str, str]) -> dict:
        captured_params.append(params)
        return {
            "items": [
                {
                    "id": {"kind": "youtube#video", "videoId": "abc123"},
                    "snippet": {
                        "title": "Grandmaster Flash Interview",
                        "channelTitle": "Archive Channel",
                        "channelId": "channel-1",
                        "description": "Interview clip.",
                        "publishedAt": "2010-01-01T00:00:00Z",
                    },
                },
            ],
        }

    result = run_request_plan(
        {
            "event_id": "grandmaster-flash-dj-techniques",
            "query_candidates": [
                {
                    "intent": "interview",
                    "media_goal": "Find interview material.",
                    "confidence_hint": "high",
                    "review_priority": 1,
                    "reason": "Direct artist query.",
                    "q": "Grandmaster Flash 1975 1977 interview",
                    "request_params": {
                        "part": "snippet",
                        "type": "video",
                        "maxResults": 8,
                        "order": "relevance",
                        "safeSearch": "moderate",
                        "relevanceLanguage": "en",
                        "regionCode": "US",
                        "q": "Grandmaster Flash 1975 1977 interview",
                        "key": "YOUTUBE_API_KEY",
                    },
                },
            ],
        },
        api_key="real-youtube-key",
        requester=fake_requester,
    )

    assert captured_params[0]["key"] == "real-youtube-key"
    assert result["results"][0]["request"]["params"]["key"] == "YOUTUBE_API_KEY"
    assert "real-youtube-key" not in result["results"][0]["request"]["url"]
    assert result["results"][0]["items"][0]["url"] == (
        "https://www.youtube.com/watch?v=abc123"
    )


def test_normalize_youtube_search_items_supports_playlists() -> None:
    items = normalize_youtube_search_items(
        {
            "items": [
                {
                    "id": {"kind": "youtube#playlist", "playlistId": "playlist-1"},
                    "snippet": {
                        "title": "Early Hip-Hop Breaks",
                        "channelTitle": "Curator",
                    },
                },
            ],
        },
        {
            "intent": "playlist_of_songs",
            "youtube_type": "playlist",
            "q": "early hip hop breaks playlist 1973",
        },
    )

    assert items[0]["type"] == "playlist"
    assert items[0]["playlist_id"] == "playlist-1"
    assert items[0]["url"] == "https://www.youtube.com/playlist?list=playlist-1"
    assert items[0]["matched_query"] == "early hip hop breaks playlist 1973"


def test_build_dry_run_summary_uses_request_plan_without_secrets() -> None:
    summary = build_dry_run_summary(
        {
            "event_id": "kool-herc-back-to-school-jam",
            "query_candidates": [
                {
                    "intent": "documentary",
                    "youtube_type": "video",
                    "q": "DJ Kool Herc 1973 documentary",
                    "get_request": "https://example.test?key=YOUTUBE_API_KEY",
                },
            ],
        },
    )

    assert summary == {
        "event_id": "kool-herc-back-to-school-jam",
        "requests": [
            {
                "intent": "documentary",
                "youtube_type": "video",
                "q": "DJ Kool Herc 1973 documentary",
                "get_request": "https://example.test?key=YOUTUBE_API_KEY",
            },
        ],
    }
