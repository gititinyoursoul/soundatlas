import json
from pathlib import Path
from typing import Any

from app.media_enrichment.services import MediaProviderError
from app.schemas import ImageLink
from scripts import enrich_image_links
from scripts.enrich_image_links import (
    build_event_image_queries,
    build_wikimedia_search_queries,
    build_wikimedia_image_link,
    dedupe_image_links,
    enrich_events_payload,
    fetch_wikimedia_image_candidates,
    infer_image_type,
    main,
    merge_image_links,
    score_image_candidate,
    request_wikimedia_json,
)


def test_wikimedia_search_result_normalizes_to_valid_image_link() -> None:
    candidates = fetch_wikimedia_image_candidates(
        event=build_event(),
        route=build_route(),
        place=build_place(),
        limit=5,
        request_fn=build_wikimedia_request_fn(),
    )

    assert len(candidates) == 1

    image_link = ImageLink.model_validate(candidates[0])

    assert image_link.provider == "wikimedia"
    assert image_link.type == "venue_photo"
    assert image_link.title == "1520 Sedgwick Avenue"
    assert image_link.rights_status == "open_license"
    assert image_link.review_status == "draft"
    assert image_link.creator == "Example photographer"
    assert image_link.confidence >= 0.45


def test_query_builder_includes_concise_place_and_notable_term_queries() -> None:
    queries = build_event_image_queries(
        event=build_event(),
        route=build_route(),
        place=build_place(),
    )

    assert "1520 Sedgwick Avenue" in queries
    assert any(query == "DJ Kool Herc" for query in queries)
    assert all("'" not in query for query in queries)


def test_legacy_query_planner_uses_legacy_queries() -> None:
    queries = build_wikimedia_search_queries(
        event=build_event(),
        route=build_route(),
        place=build_place(),
        query_planner="legacy",
    )

    assert queries[:2] == [
        "Kool Herc Back to School Jam 1520 Sedgwick Avenue 1973",
        "Kool Herc Back to School Jam",
    ]


def test_v2_query_planner_uses_planned_queries() -> None:
    queries = build_wikimedia_search_queries(
        event=build_event(),
        route=build_route(),
        place=build_place(),
        query_planner="v2",
    )

    assert queries[:3] == [
        "1520 Sedgwick Avenue Bronx 1973",
        "1520 Sedgwick Avenue Bronx 1970s",
        "DJ Kool Herc 1973",
    ]


def test_wikimedia_request_wrapper_adds_maxlag_caches_and_retries(
    monkeypatch,
) -> None:
    enrich_image_links.WIKIMEDIA_REQUEST_CACHE.clear()
    calls: list[dict[str, str]] = []
    sleeps: list[float] = []
    attempts = {"count": 0}

    def fake_request(url: str, params: dict[str, str] | None = None, headers=None) -> dict[str, Any]:
        assert url == enrich_image_links.WIKIMEDIA_API_URL
        assert headers is not None
        calls.append(dict(params or {}))
        attempts["count"] += 1
        if attempts["count"] == 1:
            raise MediaProviderError("HTTP 429: too many requests")
        return {"ok": True}

    monkeypatch.setattr(enrich_image_links, "request_json", fake_request)
    monkeypatch.setattr(enrich_image_links.time, "sleep", lambda seconds: sleeps.append(seconds))

    first = request_wikimedia_json(
        enrich_image_links.WIKIMEDIA_API_URL,
        {"action": "query", "format": "json"},
    )
    second = request_wikimedia_json(
        enrich_image_links.WIKIMEDIA_API_URL,
        {"action": "query", "format": "json"},
    )

    assert first == {"ok": True}
    assert second == {"ok": True}
    assert calls[0]["maxlag"] == "1"
    assert len(calls) == 2
    assert sleeps == [1.0]


def test_confidence_scoring_and_image_type_fallback() -> None:
    event = build_event(
        tags=["bronx", "block-party"],
        title="Breakbeat DJing Spreads Across Parties",
    )
    route = build_route()
    place = build_place({"name": "Cedar Park", "place_type": "park"})
    text_blob = "Bronx hip hop block party crowd in Cedar Park 1974"

    assert score_image_candidate(text_blob, event=event, route=route, place=place) == 0.8
    assert infer_image_type(text_blob=text_blob, event=event, place=place) == "venue_photo"
    assert (
        infer_image_type(
            text_blob="Bronx hip hop block party crowd 1974",
            event=event,
            place=place,
        )
        == "archive_photo"
    )


def test_build_wikimedia_image_link_defaults_to_archive_photo() -> None:
    candidate = build_wikimedia_image_link(
        page=build_imageinfo_page(
            title="File:Bronx block party 1974.jpg",
            object_name="Bronx block party",
            description="Bronx hip hop block party crowd in 1974.",
        ),
        query="Bronx hip hop block party 1974",
        event=build_event(tags=["bronx", "block-party"]),
        route=build_route(),
        place=build_place({"name": "South Bronx", "place_type": "region"}),
    )

    assert candidate is not None
    assert candidate["type"] == "archive_photo"
    assert candidate["review_status"] == "draft"


def test_build_wikimedia_image_link_rejects_generic_broad_place_matches() -> None:
    candidate = build_wikimedia_image_link(
        page=build_imageinfo_page(
            title="File:South Bronx street scene.jpg",
            object_name="South Bronx street scene",
            description="A street scene in the South Bronx.",
        ),
        query="South Bronx",
        event=build_event({"title": "Caribbean Sound System Influences Reach the Bronx"}),
        route=build_route(),
        place=build_place({"name": "South Bronx", "place_type": "region"}),
    )

    assert candidate is None


def test_deduplication_uses_image_thumbnail_and_source_urls() -> None:
    image_links = [
        build_candidate("https://img.example/1.jpg", "https://thumb.example/a.jpg", "https://src.example/1"),
        build_candidate("https://img.example/2.jpg", "https://thumb.example/a.jpg", "https://src.example/2"),
        build_candidate("https://img.example/3.jpg", "https://thumb.example/c.jpg", "https://src.example/1"),
        build_candidate("https://img.example/4.jpg", "https://thumb.example/d.jpg", "https://src.example/4"),
    ]

    deduped_links = dedupe_image_links(image_links)

    assert [link["image_url"] for link in deduped_links] == [
        "https://img.example/1.jpg",
        "https://img.example/4.jpg",
    ]


def test_merge_preserves_existing_links_and_skips_duplicates() -> None:
    existing_link = build_candidate(
        "https://img.example/existing.jpg",
        "https://thumb.example/existing.jpg",
        "https://src.example/existing",
        provider="manual",
        review_status="reviewed",
    )
    duplicate_candidate = build_candidate(
        "https://img.example/new.jpg",
        "https://thumb.example/new.jpg",
        "https://src.example/existing",
    )
    new_candidate = build_candidate(
        "https://img.example/newer.jpg",
        "https://thumb.example/newer.jpg",
        "https://src.example/newer",
    )

    merged_links = merge_image_links(
        [existing_link],
        [duplicate_candidate, new_candidate],
        limit=5,
    )

    assert merged_links == [existing_link, new_candidate]


def test_enrich_events_payload_filters_event_route_and_limit() -> None:
    events_payload = {
        "events": [
            build_event({"id": "target", "route_id": "birth-of-hip-hop", "image_links": []}),
            build_event({"id": "other", "route_id": "birth-of-hip-hop", "image_links": []}),
            build_event({"id": "other-route", "route_id": "disco-to-dance-music", "image_links": []}),
        ],
    }
    changed_events = enrich_events_payload(
        events_payload=events_payload,
        routes_payload={"routes": [build_route(), build_route({"id": "disco-to-dance-music"})]},
        places_payload={"places": [build_place()]},
        event_id="target",
        route_id="birth-of-hip-hop",
        limit=1,
        providers=["wikimedia"],
        request_fn=build_wikimedia_request_fn(),
    )

    assert changed_events == 1
    assert len(events_payload["events"][0]["image_links"]) == 1
    assert events_payload["events"][1]["image_links"] == []
    assert events_payload["events"][2]["image_links"] == []


def test_enrich_events_payload_uses_v2_query_planner_by_default() -> None:
    searched_queries: list[str] = []

    def fake_request(url: str, params: dict[str, str] | None = None) -> dict[str, Any]:
        assert params is not None
        if params.get("list") == "search":
            searched_queries.append(params["srsearch"])
            return {
                "query": {
                    "search": [
                        {"title": "File:1520 Sedgwick Avenue.jpg"},
                    ],
                },
            }
        return {
            "query": {
                "pages": {
                    "1": build_imageinfo_page(
                        title="File:1520 Sedgwick Avenue.jpg",
                        object_name="1520 Sedgwick Avenue",
                        description="1520 Sedgwick Avenue in the Bronx.",
                    ),
                },
            },
        }

    events_payload = {"events": [build_event({"image_links": []})]}
    changed_events = enrich_events_payload(
        events_payload=events_payload,
        routes_payload={"routes": [build_route()]},
        places_payload={"places": [build_place()]},
        event_id="kool-herc-back-to-school-jam",
        route_id=None,
        limit=1,
        providers=["wikimedia"],
        request_fn=fake_request,
    )

    assert changed_events == 1
    assert searched_queries[0] == "1520 Sedgwick Avenue Bronx 1973"
    assert events_payload["events"][0]["image_links"][0]["query"] == "1520 Sedgwick Avenue Bronx 1973"


def test_enrich_events_payload_can_use_legacy_query_planner() -> None:
    searched_queries: list[str] = []

    def fake_request(url: str, params: dict[str, str] | None = None) -> dict[str, Any]:
        assert params is not None
        if params.get("list") == "search":
            searched_queries.append(params["srsearch"])
            return {
                "query": {
                    "search": [
                        {"title": "File:1520 Sedgwick Avenue.jpg"},
                    ],
                },
            }
        return {
            "query": {
                "pages": {
                    "1": build_imageinfo_page(
                        title="File:1520 Sedgwick Avenue.jpg",
                        object_name="1520 Sedgwick Avenue",
                        description="1520 Sedgwick Avenue in the Bronx.",
                    ),
                },
            },
        }

    events_payload = {"events": [build_event({"image_links": []})]}
    changed_events = enrich_events_payload(
        events_payload=events_payload,
        routes_payload={"routes": [build_route()]},
        places_payload={"places": [build_place()]},
        event_id="kool-herc-back-to-school-jam",
        route_id=None,
        limit=1,
        providers=["wikimedia"],
        query_planner="legacy",
        request_fn=fake_request,
    )

    assert changed_events == 1
    assert searched_queries[0] == "Kool Herc Back to School Jam 1520 Sedgwick Avenue 1973"


def test_enrich_events_payload_skips_ignored_image_links() -> None:
    events_payload = {
        "events": [
            build_event(
                {
                    "image_links": [],
                },
            )
        ],
        "ignored_links": [
            {
                "event_id": "kool-herc-back-to-school-jam",
                "kind": "image",
                "values": [
                    "https://upload.wikimedia.org/example.jpg",
                    "https://commons.wikimedia.org/wiki/File:1520_Sedgwick_Avenue.jpg",
                ],
            }
        ],
    }

    changed_events = enrich_events_payload(
        events_payload=events_payload,
        routes_payload={"routes": [build_route()]},
        places_payload={"places": [build_place()]},
        event_id="kool-herc-back-to-school-jam",
        route_id="birth-of-hip-hop",
        limit=5,
        providers=["wikimedia"],
        ignored_link_index=enrich_image_links.build_ignored_link_index(events_payload),
        request_fn=build_wikimedia_request_fn(),
    )

    assert changed_events == 0
    assert events_payload["events"][0]["image_links"] == []


def test_dry_run_does_not_write_seed_data_with_default_v2_planner(
    tmp_path: Path,
    monkeypatch,
    capsys,
) -> None:
    events_path = tmp_path / "events.json"
    routes_path = tmp_path / "routes.json"
    places_path = tmp_path / "places.json"
    original_payload = {"events": [build_event({"image_links": []})]}
    events_path.write_text(json.dumps(original_payload, indent=2), encoding="utf-8")
    routes_path.write_text(json.dumps({"routes": [build_route()]}), encoding="utf-8")
    places_path.write_text(json.dumps({"places": [build_place()]}), encoding="utf-8")
    original_text = events_path.read_text(encoding="utf-8")

    monkeypatch.setattr(enrich_image_links, "EVENTS_PATH", events_path)
    monkeypatch.setattr(enrich_image_links, "ROUTES_PATH", routes_path)
    monkeypatch.setattr(enrich_image_links, "PLACES_PATH", places_path)
    monkeypatch.setattr(enrich_image_links, "request_wikimedia_json", build_wikimedia_request_fn())

    exit_code = main(
        [
            "--event-id",
            "kool-herc-back-to-school-jam",
            "--dry-run",
        ],
    )

    output = capsys.readouterr().out
    assert exit_code == 0
    assert events_path.read_text(encoding="utf-8") == original_text
    assert "Image enrichment" in output
    assert "Mode: dry-run (no files written)" in output
    assert "Changed events: 1" in output
    assert "kool-herc-back-to-school-jam: +1 image link(s) (0 -> 1)" in output
    assert "Use --dry-run --json" in output


def test_legacy_dry_run_does_not_write_seed_data(
    tmp_path: Path,
    monkeypatch,
    capsys,
) -> None:
    events_path = tmp_path / "events.json"
    routes_path = tmp_path / "routes.json"
    places_path = tmp_path / "places.json"
    original_payload = {"events": [build_event({"image_links": []})]}
    events_path.write_text(json.dumps(original_payload, indent=2), encoding="utf-8")
    routes_path.write_text(json.dumps({"routes": [build_route()]}), encoding="utf-8")
    places_path.write_text(json.dumps({"places": [build_place()]}), encoding="utf-8")
    original_text = events_path.read_text(encoding="utf-8")

    monkeypatch.setattr(enrich_image_links, "EVENTS_PATH", events_path)
    monkeypatch.setattr(enrich_image_links, "ROUTES_PATH", routes_path)
    monkeypatch.setattr(enrich_image_links, "PLACES_PATH", places_path)
    monkeypatch.setattr(enrich_image_links, "request_wikimedia_json", build_wikimedia_request_fn())

    exit_code = main(
        [
            "--event-id",
            "kool-herc-back-to-school-jam",
            "--query-planner",
            "legacy",
            "--dry-run",
        ],
    )

    output = capsys.readouterr().out
    assert exit_code == 0
    assert events_path.read_text(encoding="utf-8") == original_text
    assert "Image enrichment" in output
    assert "Query planner: legacy" in output
    assert "Changed events: 1" in output


def test_dry_run_json_prints_changed_seed_payload(
    tmp_path: Path,
    monkeypatch,
    capsys,
) -> None:
    events_path = tmp_path / "events.json"
    routes_path = tmp_path / "routes.json"
    places_path = tmp_path / "places.json"
    original_payload = {"events": [build_event({"image_links": []})]}
    events_path.write_text(json.dumps(original_payload, indent=2), encoding="utf-8")
    routes_path.write_text(json.dumps({"routes": [build_route()]}), encoding="utf-8")
    places_path.write_text(json.dumps({"places": [build_place()]}), encoding="utf-8")
    original_text = events_path.read_text(encoding="utf-8")

    monkeypatch.setattr(enrich_image_links, "EVENTS_PATH", events_path)
    monkeypatch.setattr(enrich_image_links, "ROUTES_PATH", routes_path)
    monkeypatch.setattr(enrich_image_links, "PLACES_PATH", places_path)
    monkeypatch.setattr(enrich_image_links, "request_wikimedia_json", build_wikimedia_request_fn())

    exit_code = main(
        [
            "--event-id",
            "kool-herc-back-to-school-jam",
            "--dry-run",
            "--json",
        ],
    )

    payload = json.loads(capsys.readouterr().out)
    assert exit_code == 0
    assert events_path.read_text(encoding="utf-8") == original_text
    assert payload["events"][0]["image_links"][0]["query"] == "1520 Sedgwick Avenue Bronx 1973"


def test_preview_queries_prints_default_v2_plan_without_provider_calls(
    tmp_path: Path,
    monkeypatch,
    capsys,
) -> None:
    events_path, routes_path, places_path = write_preview_seed_files(tmp_path)
    original_text = events_path.read_text(encoding="utf-8")

    def fail_request(*args, **kwargs):
        raise AssertionError("preview should not call Wikimedia")

    monkeypatch.setattr(enrich_image_links, "EVENTS_PATH", events_path)
    monkeypatch.setattr(enrich_image_links, "ROUTES_PATH", routes_path)
    monkeypatch.setattr(enrich_image_links, "PLACES_PATH", places_path)
    monkeypatch.setattr(enrich_image_links, "request_wikimedia_json", fail_request)

    exit_code = main(
        [
            "--event-id",
            "kool-herc-back-to-school-jam",
            "--preview-queries",
        ],
    )

    output = capsys.readouterr().out
    assert exit_code == 0
    assert events_path.read_text(encoding="utf-8") == original_text
    assert "Event: kool-herc-back-to-school-jam" in output
    assert "venue_photo" in output
    assert "[1/high] 1520 Sedgwick Avenue Bronx 1973" in output
    assert "[2/high] DJ Kool Herc 1973" in output


def test_preview_queries_can_print_legacy_queries(
    tmp_path: Path,
    monkeypatch,
    capsys,
) -> None:
    events_path, routes_path, places_path = write_preview_seed_files(tmp_path)
    monkeypatch.setattr(enrich_image_links, "EVENTS_PATH", events_path)
    monkeypatch.setattr(enrich_image_links, "ROUTES_PATH", routes_path)
    monkeypatch.setattr(enrich_image_links, "PLACES_PATH", places_path)

    exit_code = main(
        [
            "--event-id",
            "kool-herc-back-to-school-jam",
            "--preview-queries",
            "--query-planner",
            "legacy",
        ],
    )

    output = capsys.readouterr().out
    assert exit_code == 0
    assert "Event: kool-herc-back-to-school-jam" in output
    assert "legacy" in output
    assert "[1] Kool Herc Back to School Jam 1520 Sedgwick Avenue 1973" in output


def test_preview_queries_respects_route_filter(
    tmp_path: Path,
    monkeypatch,
    capsys,
) -> None:
    events_path, routes_path, places_path = write_preview_seed_files(tmp_path)
    monkeypatch.setattr(enrich_image_links, "EVENTS_PATH", events_path)
    monkeypatch.setattr(enrich_image_links, "ROUTES_PATH", routes_path)
    monkeypatch.setattr(enrich_image_links, "PLACES_PATH", places_path)

    exit_code = main(
        [
            "--route-id",
            "birth-of-hip-hop",
            "--preview-queries",
        ],
    )

    output = capsys.readouterr().out
    assert exit_code == 0
    assert "Event: kool-herc-back-to-school-jam" in output
    assert "Event: other-route-event" not in output


def test_preview_queries_reports_unknown_filters(
    tmp_path: Path,
    monkeypatch,
    capsys,
) -> None:
    events_path, routes_path, places_path = write_preview_seed_files(tmp_path)
    monkeypatch.setattr(enrich_image_links, "EVENTS_PATH", events_path)
    monkeypatch.setattr(enrich_image_links, "ROUTES_PATH", routes_path)
    monkeypatch.setattr(enrich_image_links, "PLACES_PATH", places_path)

    exit_code = main(
        [
            "--event-id",
            "missing-event",
            "--preview-queries",
        ],
    )

    captured = capsys.readouterr()
    assert exit_code == 2
    assert "No event found for --event-id 'missing-event'." in captured.err


def build_wikimedia_request_fn():
    def fake_request(url: str, params: dict[str, str] | None = None) -> dict[str, Any]:
        assert url == enrich_image_links.WIKIMEDIA_API_URL
        assert params is not None
        if params.get("list") == "search":
            return {
                "query": {
                    "search": [
                        {"title": "File:1520 Sedgwick Avenue.jpg"},
                        {"title": "Category:Not a file"},
                    ],
                },
            }
        return {
            "query": {
                "pages": {
                    "1": build_imageinfo_page(
                        title="File:1520 Sedgwick Avenue.jpg",
                        object_name="1520 Sedgwick Avenue",
                        description="1520 Sedgwick Avenue in the Bronx.",
                    ),
                },
            },
        }

    return fake_request


def build_imageinfo_page(
    title: str,
    object_name: str,
    description: str,
) -> dict[str, Any]:
    return {
        "title": title,
        "imageinfo": [
            {
                "url": "https://upload.wikimedia.org/example.jpg",
                "thumburl": "https://upload.wikimedia.org/example-thumb.jpg",
                "descriptionurl": "https://commons.wikimedia.org/wiki/File:1520_Sedgwick_Avenue.jpg",
                "mime": "image/jpeg",
                "mediatype": "BITMAP",
                "extmetadata": {
                    "ObjectName": {"value": object_name},
                    "ImageDescription": {"value": description},
                    "Artist": {"value": "Example photographer"},
                    "LicenseShortName": {"value": "CC BY-SA 4.0"},
                    "LicenseUrl": {"value": "https://creativecommons.org/licenses/by-sa/4.0/"},
                },
            },
        ],
    }


def build_event(overrides: dict[str, Any] | None = None, **keyword_overrides: Any) -> dict[str, Any]:
    event = {
        "id": "kool-herc-back-to-school-jam",
        "route_id": "birth-of-hip-hop",
        "place_id": "1520-sedgwick-avenue",
        "title": "Kool Herc's Back-to-School Jam",
        "year_start": 1973,
        "year_end": 1973,
        "summary": "DJ Kool Herc plays in the community room at 1520 Sedgwick Avenue.",
        "significance": "A symbolic origin point for Bronx hip hop party culture.",
        "tags": ["kool-herc", "block-party", "bronx", "origin-story"],
        "review_status": "draft",
        "source_urls": [],
        "media_links": [],
        "image_links": [],
    }
    if overrides:
        event.update(overrides)
    event.update(keyword_overrides)
    return event


def write_preview_seed_files(tmp_path: Path) -> tuple[Path, Path, Path]:
    events_path = tmp_path / "events.json"
    routes_path = tmp_path / "routes.json"
    places_path = tmp_path / "places.json"
    events_path.write_text(
        json.dumps(
            {
                "events": [
                    build_event(),
                    build_event(
                        {
                            "id": "other-route-event",
                            "route_id": "other-route",
                            "place_id": "other-place",
                            "title": "Other Event",
                        },
                    ),
                ],
            },
            indent=2,
        ),
        encoding="utf-8",
    )
    routes_path.write_text(
        json.dumps(
            {
                "routes": [
                    build_route(),
                    build_route({"id": "other-route", "title": "Other Route"}),
                ],
            },
        ),
        encoding="utf-8",
    )
    places_path.write_text(
        json.dumps(
            {
                "places": [
                    build_place(),
                    build_place({"id": "other-place", "name": "Other Place"}),
                ],
            },
        ),
        encoding="utf-8",
    )
    return events_path, routes_path, places_path


def build_route(overrides: dict[str, Any] | None = None) -> dict[str, Any]:
    route = {
        "id": "birth-of-hip-hop",
        "title": "Birth of Hip-Hop",
        "tags": ["hip-hop", "bronx"],
    }
    if overrides:
        route.update(overrides)
    return route


def build_place(overrides: dict[str, Any] | None = None) -> dict[str, Any]:
    place = {
        "id": "1520-sedgwick-avenue",
        "name": "1520 Sedgwick Avenue",
        "place_type": "building",
    }
    if overrides:
        place.update(overrides)
    return place


def build_candidate(
    image_url: str,
    thumbnail_url: str,
    source_url: str,
    provider: str = "wikimedia",
    review_status: str = "draft",
) -> dict[str, Any]:
    return {
        "provider": provider,
        "type": "archive_photo",
        "title": "Example image",
        "image_url": image_url,
        "thumbnail_url": thumbnail_url,
        "source_url": source_url,
        "rights_status": "open_license",
        "alt_text": "Example image.",
        "query": "example",
        "confidence": 0.6,
        "review_status": review_status,
    }
