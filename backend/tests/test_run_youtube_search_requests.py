import json
from pathlib import Path

import pytest

from scripts import run_youtube_search_requests
from scripts.run_youtube_search_requests import (
    build_dry_run_summary,
    main,
    normalize_youtube_search_items,
    run_request_plan,
    validate_request_plan,
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
                    "priority": 1,
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
            "intent": "playlist",
            "priority": 2,
            "youtube_type": "playlist",
            "confidence_hint": "medium",
            "review_priority": 2,
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
                    "priority": 1,
                    "youtube_type": "video",
                    "confidence_hint": "high",
                    "review_priority": 1,
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


def test_dry_run_prints_youtube_request_summary(
    tmp_path: Path,
    monkeypatch,
    capsys,
) -> None:
    request_dir = write_request_plan_files(tmp_path)
    monkeypatch.setattr(
        run_youtube_search_requests.MediaEnrichmentSettings,
        "from_env",
        lambda: build_dummy_settings(),
    )

    exit_code = main(
        [
            "--event-id",
            "grandmaster-flash-dj-techniques",
            "--request-dir",
            str(request_dir),
            "--dry-run",
        ],
    )

    output = capsys.readouterr().out
    assert exit_code == 0
    assert "YouTube request run" in output
    assert "Mode: dry-run (no API calls, no files written)" in output
    assert "Request plans: 1" in output
    assert "grandmaster-flash-dj-techniques: 1 request(s) (video=1)" in output
    assert "Use --dry-run --json" in output


def test_dry_run_json_preserves_youtube_request_summary_shape(
    tmp_path: Path,
    monkeypatch,
    capsys,
) -> None:
    request_dir = write_request_plan_files(tmp_path)
    monkeypatch.setattr(
        run_youtube_search_requests.MediaEnrichmentSettings,
        "from_env",
        lambda: build_dummy_settings(),
    )

    exit_code = main(
        [
            "--event-id",
            "grandmaster-flash-dj-techniques",
            "--request-dir",
            str(request_dir),
            "--dry-run",
            "--json",
        ],
    )

    payload = json.loads(capsys.readouterr().out)
    assert exit_code == 0
    assert payload == [build_dry_run_summary(build_valid_request_plan())]


def test_live_run_prints_written_result_summary(
    tmp_path: Path,
    monkeypatch,
    capsys,
) -> None:
    request_dir = write_request_plan_files(tmp_path)
    output_dir = tmp_path / "youtube-search-results"
    monkeypatch.setattr(
        run_youtube_search_requests.MediaEnrichmentSettings,
        "from_env",
        lambda: build_live_settings(),
    )

    def fake_run_request_plan(request_plan, api_key):
        assert api_key == "real-youtube-key"
        return {
            "provider": "youtube",
            "api_method": "search.list",
            "event_id": request_plan["event_id"],
            "results": [
                {
                    "intent": "interview",
                    "items": [],
                }
            ],
        }

    monkeypatch.setattr(run_youtube_search_requests, "run_request_plan", fake_run_request_plan)

    exit_code = main(
        [
            "--event-id",
            "grandmaster-flash-dj-techniques",
            "--request-dir",
            str(request_dir),
            "--output-dir",
            str(output_dir),
        ],
    )

    output = capsys.readouterr().out
    result_path = output_dir / "grandmaster-flash-dj-techniques.json"
    assert exit_code == 0
    assert result_path.exists()
    assert "Mode: write" in output
    assert "Written result files: 1" in output
    assert "grandmaster-flash-dj-techniques.json" in output
    assert "real-youtube-key" not in output


def test_validate_request_plan_rejects_unsupported_intent(tmp_path) -> None:
    request_plan = build_valid_request_plan()
    request_plan["query_candidates"][0]["intent"] = "unsupported_legacy_intent"

    with pytest.raises(ValueError, match="unsupported intent"):
        validate_request_plan(request_plan, tmp_path / "request.json")


def test_validate_request_plan_rejects_mismatched_query(tmp_path) -> None:
    request_plan = build_valid_request_plan()
    request_plan["query_candidates"][0]["request_params"]["q"] = "different query"

    with pytest.raises(ValueError, match="request_params.q"):
        validate_request_plan(request_plan, tmp_path / "request.json")


def build_valid_request_plan() -> dict:
    return {
        "event_id": "grandmaster-flash-dj-techniques",
        "query_candidates": [
            {
                "intent": "interview",
                "media_goal": "Find interview material.",
                "priority": 1,
                "youtube_type": "video",
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
    }


def write_request_plan_files(tmp_path: Path) -> Path:
    request_dir = tmp_path / "youtube-search-requests"
    request_dir.mkdir()
    (request_dir / "grandmaster-flash-dj-techniques.json").write_text(
        json.dumps(build_valid_request_plan()),
        encoding="utf-8",
    )
    return request_dir


def build_dummy_settings():
    return run_youtube_search_requests.MediaEnrichmentSettings(
        env_source="test",
        env_file=None,
        use_dummy_services=True,
        youtube_api_key=None,
    )


def build_live_settings():
    return run_youtube_search_requests.MediaEnrichmentSettings(
        env_source="test",
        env_file=None,
        use_dummy_services=False,
        youtube_api_key="real-youtube-key",
    )
