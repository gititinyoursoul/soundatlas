import json

from scripts.enrich_media_links import (
    enrich_events_payload,
    extract_media_links_from_youtube_results,
    load_youtube_result_payloads,
)


def test_enrich_events_payload_merges_youtube_result_items() -> None:
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

    changed_events = enrich_events_payload(
        events_payload=events_payload,
        youtube_result_payloads=[build_youtube_result_payload()],
        event_id=None,
        limit=2,
    )

    media_links = events_payload["events"][0]["media_links"]

    assert changed_events == 1
    assert len(media_links) == 3
    assert media_links[0]["url"] == "https://www.youtube.com/watch?v=existing"
    assert media_links[1] == {
        "provider": "youtube",
        "type": "video",
        "title": "Kool Herc Interview",
        "url": "https://www.youtube.com/watch?v=interview",
        "query": "DJ Kool Herc 1973 interview",
        "confidence": 0.75,
        "review_status": "draft",
    }
    assert media_links[2]["type"] == "playlist"


def test_extract_media_links_sorts_by_review_priority_and_dedupes() -> None:
    media_links = extract_media_links_from_youtube_results(
        {
            "provider": "youtube",
            "event_id": "kool-herc-back-to-school-jam",
            "results": [
                {
                    "intent": "documentary",
                    "confidence_hint": "medium",
                    "review_priority": 2,
                    "items": [
                        {
                            "provider": "youtube",
                            "type": "video",
                            "url": "https://www.youtube.com/watch?v=documentary",
                            "title": "Documentary",
                            "matched_query": "DJ Kool Herc documentary",
                            "review_status": "draft",
                        },
                    ],
                },
                {
                    "intent": "interview",
                    "confidence_hint": "high",
                    "review_priority": 1,
                    "items": [
                        {
                            "provider": "youtube",
                            "type": "video",
                            "url": "https://www.youtube.com/watch?v=interview",
                            "title": "Kool Herc Interview",
                            "matched_query": "DJ Kool Herc interview",
                            "review_status": "draft",
                        },
                        {
                            "provider": "youtube",
                            "type": "video",
                            "url": "https://www.youtube.com/watch?v=interview",
                            "title": "Duplicate Interview",
                            "matched_query": "DJ Kool Herc interview",
                            "review_status": "draft",
                        },
                    ],
                },
            ],
        },
        limit=3,
    )

    assert [link["url"] for link in media_links] == [
        "https://www.youtube.com/watch?v=interview",
        "https://www.youtube.com/watch?v=documentary",
    ]


def test_load_youtube_result_payloads_filters_provider_and_event(tmp_path) -> None:
    youtube_result_path = tmp_path / "kool-herc-back-to-school-jam.json"
    youtube_result_path.write_text(
        json.dumps(build_youtube_result_payload()),
        encoding="utf-8",
    )
    spotify_result_path = tmp_path / "spotify-result.json"
    spotify_result_path.write_text(
        json.dumps({"provider": "spotify", "event_id": "kool-herc-back-to-school-jam"}),
        encoding="utf-8",
    )

    result_payloads = load_youtube_result_payloads(
        tmp_path,
        event_id="kool-herc-back-to-school-jam",
    )

    assert len(result_payloads) == 1
    assert result_payloads[0]["provider"] == "youtube"


def build_youtube_result_payload() -> dict:
    return {
        "provider": "youtube",
        "api_method": "search.list",
        "event_id": "kool-herc-back-to-school-jam",
        "editorial_status": "draft",
        "results": [
            {
                "intent": "interview",
                "confidence_hint": "high",
                "review_priority": 1,
                "request": {
                    "params": {
                        "q": "DJ Kool Herc 1973 interview",
                    },
                },
                "items": [
                    {
                        "provider": "youtube",
                        "type": "video",
                        "video_id": "interview",
                        "playlist_id": None,
                        "url": "https://www.youtube.com/watch?v=interview",
                        "title": "Kool Herc Interview",
                        "matched_query": "DJ Kool Herc 1973 interview",
                        "review_status": "draft",
                    },
                    {
                        "provider": "youtube",
                        "type": "playlist",
                        "video_id": None,
                        "playlist_id": "playlist",
                        "url": "https://www.youtube.com/playlist?list=playlist",
                        "title": "Early Hip-Hop Breaks",
                        "matched_query": "early hip hop breaks playlist 1973",
                        "review_status": "draft",
                    },
                ],
            },
        ],
    }
