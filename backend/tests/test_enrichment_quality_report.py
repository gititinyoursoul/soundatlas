import json
from pathlib import Path
from typing import Any

from app.media_enrichment.quality_report import (
    build_quality_report,
    compare_quality_reports,
)
from scripts import report_enrichment_quality


def test_media_quality_report_counts_filters_and_compares_to_seed(
    tmp_path: Path,
    monkeypatch,
    capsys,
) -> None:
    events_path, routes_path, places_path = write_seed_files(
        tmp_path,
        events_payload={
            "events": [
                build_event(
                    {
                        "media_links": [
                            build_media_candidate(
                                "https://www.youtube.com/watch?v=existing",
                                "Existing clip",
                                "video",
                            ),
                        ],
                    },
                ),
            ],
            "ignored_links": [
                {
                    "event_id": "kool-herc-back-to-school-jam",
                    "kind": "media",
                    "values": ["https://www.youtube.com/watch?v=ignored"],
                },
            ],
        },
    )
    results_dir = tmp_path / "youtube-results"
    results_dir.mkdir()
    (results_dir / "kool-herc-back-to-school-jam.json").write_text(
        json.dumps(build_youtube_result_payload()),
        encoding="utf-8",
    )
    original_seed_text = events_path.read_text(encoding="utf-8")

    monkeypatch.setattr(report_enrichment_quality, "EVENTS_PATH", events_path)
    monkeypatch.setattr(report_enrichment_quality, "ROUTES_PATH", routes_path)
    monkeypatch.setattr(report_enrichment_quality, "PLACES_PATH", places_path)

    exit_code = report_enrichment_quality.main(
        [
            "--kind",
            "media",
            "--event-id",
            "kool-herc-back-to-school-jam",
            "--results-dir",
            str(results_dir),
            "--baseline-from-seed",
            "--json",
        ],
    )

    output = json.loads(capsys.readouterr().out)
    event_report = output["events"][0]
    comparison = output["comparison"]["events"][0]

    assert exit_code == 0
    assert events_path.read_text(encoding="utf-8") == original_seed_text
    assert event_report["raw_candidate_count"] == 5
    assert event_report["deduped_candidate_count"] == 4
    assert event_report["duplicate_count"] == 1
    assert event_report["ignored_match_count"] == 1
    assert event_report["existing_duplicate_count"] == 1
    assert event_report["added_count"] == 2
    assert event_report["final_candidate_count"] == 3
    assert event_report["type_counts"] == {"playlist": 1, "video": 2}
    assert comparison["baseline_candidate_count"] == 1
    assert comparison["candidate_candidate_count"] == 3
    assert comparison["delta_candidate_count"] == 2
    assert comparison["baseline_added_count"] == 1
    assert comparison["candidate_added_count"] == 2
    assert comparison["delta_added_count"] == 1
    assert comparison["type_count_deltas"] == {"playlist": 1, "video": 1}
    assert comparison["new_candidate_identity_count"] == 2
    assert comparison["lost_candidate_identity_count"] == 0


def test_image_quality_report_counts_types_rights_and_compares_to_seed(
    tmp_path: Path,
    monkeypatch,
    capsys,
) -> None:
    existing_image = build_image_candidate(
        "https://commons.wikimedia.org/wiki/File:Existing.jpg",
        "https://upload.wikimedia.org/existing.jpg",
        image_type="venue_photo",
        rights_status="open_license",
    )
    events_path, routes_path, places_path = write_seed_files(
        tmp_path,
        events_payload={
            "events": [
                build_event({"image_links": [existing_image]}),
            ],
        },
    )
    original_seed_text = events_path.read_text(encoding="utf-8")

    monkeypatch.setattr(report_enrichment_quality, "EVENTS_PATH", events_path)
    monkeypatch.setattr(report_enrichment_quality, "ROUTES_PATH", routes_path)
    monkeypatch.setattr(report_enrichment_quality, "PLACES_PATH", places_path)
    monkeypatch.setattr(report_enrichment_quality, "request_wikimedia_json", fake_wikimedia_request)

    exit_code = report_enrichment_quality.main(
        [
            "--kind",
            "image",
            "--event-id",
            "kool-herc-back-to-school-jam",
            "--baseline-from-seed",
            "--json",
        ],
    )

    output = json.loads(capsys.readouterr().out)
    event_report = output["events"][0]
    comparison = output["comparison"]["events"][0]

    assert exit_code == 0
    assert events_path.read_text(encoding="utf-8") == original_seed_text
    assert event_report["raw_candidate_count"] > 2
    assert event_report["deduped_candidate_count"] == 2
    assert event_report["duplicate_count"] == event_report["raw_candidate_count"] - 2
    assert event_report["added_count"] == 2
    assert event_report["type_counts"] == {"archive_photo": 1, "venue_photo": 1}
    assert event_report["rights_status_counts"] == {
        "open_license": 1,
        "unknown": 1,
    }
    assert "unknown_rights_status" in event_report["warnings"]
    assert comparison["type_count_deltas"] == {
        "archive_photo": 1,
        "venue_photo": 0,
    }
    assert comparison["rights_status_count_deltas"] == {
        "open_license": 0,
        "unknown": 1,
    }


def test_compare_quality_reports_highlights_type_quality_deltas() -> None:
    event = build_event({"media_links": []})
    route = build_route()
    place = build_place()
    baseline = build_quality_report(
        kind="media",
        events=[event],
        routes_by_id={route["id"]: route},
        places_by_id={place["id"]: place},
        raw_candidates_by_event_id={
            event["id"]: [
                build_media_candidate(
                    "https://www.youtube.com/watch?v=baseline",
                    "Bronx hip hop playlist",
                    "playlist",
                    confidence=0.35,
                    query="Bronx hip hop",
                ),
            ],
        },
        limit=3,
    )
    candidate = build_quality_report(
        kind="media",
        events=[event],
        routes_by_id={route["id"]: route},
        places_by_id={place["id"]: place},
        raw_candidates_by_event_id={
            event["id"]: [
                build_media_candidate(
                    "https://www.youtube.com/watch?v=candidate",
                    "DJ Kool Herc 1973 interview at 1520 Sedgwick Avenue",
                    "video",
                    confidence=0.75,
                    query="DJ Kool Herc 1973 interview",
                ),
            ],
        },
        limit=3,
    )

    comparison = compare_quality_reports(baseline, candidate)
    event_comparison = comparison["events"][0]

    assert event_comparison["type_count_deltas"] == {"playlist": -1, "video": 1}
    assert event_comparison["type_quality_deltas"]["video"]["candidate_count"] == 1
    assert event_comparison["type_quality_deltas"]["playlist"]["baseline_count"] == 1
    assert event_comparison["delta_average_confidence"] > 0
    assert event_comparison["quality_direction"] in {"improved", "mixed"}


def write_seed_files(
    tmp_path: Path,
    *,
    events_payload: dict[str, Any],
) -> tuple[Path, Path, Path]:
    events_path = tmp_path / "events.json"
    routes_path = tmp_path / "routes.json"
    places_path = tmp_path / "places.json"
    events_path.write_text(json.dumps(events_payload, indent=2), encoding="utf-8")
    routes_path.write_text(json.dumps({"routes": [build_route()]}, indent=2), encoding="utf-8")
    places_path.write_text(json.dumps({"places": [build_place()]}, indent=2), encoding="utf-8")
    return events_path, routes_path, places_path


def build_event(overrides: dict[str, Any] | None = None) -> dict[str, Any]:
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
        "source_urls": [],
        "review_status": "draft",
        "media_links": [],
        "image_links": [],
    }
    if overrides:
        event.update(overrides)
    return event


def build_route() -> dict[str, Any]:
    return {
        "id": "birth-of-hip-hop",
        "title": "Birth of Hip-Hop",
        "tags": ["hip-hop", "bronx"],
    }


def build_place() -> dict[str, Any]:
    return {
        "id": "1520-sedgwick-avenue",
        "name": "1520 Sedgwick Avenue",
        "place_type": "building",
    }


def build_media_candidate(
    url: str,
    title: str,
    media_type: str,
    *,
    confidence: float = 0.75,
    query: str = "DJ Kool Herc 1973 interview",
) -> dict[str, Any]:
    return {
        "provider": "youtube",
        "type": media_type,
        "title": title,
        "url": url,
        "query": query,
        "confidence": confidence,
        "review_status": "draft",
    }


def build_youtube_result_payload() -> dict[str, Any]:
    return {
        "provider": "youtube",
        "event_id": "kool-herc-back-to-school-jam",
        "results": [
            {
                "intent": "interview",
                "confidence_hint": "high",
                "review_priority": 1,
                "request": {"params": {"q": "DJ Kool Herc 1973 interview"}},
                "items": [
                    {
                        "provider": "youtube",
                        "type": "video",
                        "url": "https://www.youtube.com/watch?v=existing",
                        "title": "Existing clip",
                        "matched_query": "DJ Kool Herc 1973 interview",
                    },
                    {
                        "provider": "youtube",
                        "type": "video",
                        "url": "https://www.youtube.com/watch?v=ignored",
                        "title": "Ignored clip",
                        "matched_query": "DJ Kool Herc 1973 interview",
                    },
                    {
                        "provider": "youtube",
                        "type": "video",
                        "url": "https://www.youtube.com/watch?v=new-video",
                        "title": "DJ Kool Herc 1973 interview",
                        "matched_query": "DJ Kool Herc 1973 interview",
                    },
                    {
                        "provider": "youtube",
                        "type": "video",
                        "url": "https://www.youtube.com/watch?v=new-video",
                        "title": "Duplicate video",
                        "matched_query": "DJ Kool Herc 1973 interview",
                    },
                    {
                        "provider": "youtube",
                        "type": "playlist",
                        "url": "https://www.youtube.com/playlist?list=breaks",
                        "title": "Early hip-hop breaks",
                        "matched_query": "early hip hop breaks playlist 1973",
                    },
                ],
            },
        ],
    }


def build_image_candidate(
    source_url: str,
    image_url: str,
    *,
    image_type: str,
    rights_status: str,
    title: str = "1520 Sedgwick Avenue",
    query: str = "1520 Sedgwick Avenue",
) -> dict[str, Any]:
    return {
        "provider": "wikimedia",
        "type": image_type,
        "title": title,
        "image_url": image_url,
        "thumbnail_url": image_url.replace(".jpg", "-thumb.jpg"),
        "source_url": source_url,
        "rights_status": rights_status,
        "alt_text": title,
        "query": query,
        "confidence": 0.65,
        "review_status": "draft",
    }


def fake_wikimedia_request(url: str, params: dict[str, str] | None = None) -> dict[str, Any]:
    assert params is not None
    if params.get("list") == "search":
        query = params.get("srsearch", "")
        if "1520" in query:
            results = [{"title": "File:1520 Sedgwick Avenue.jpg"}]
        elif "Kool Herc" in query:
            results = [{"title": "File:Bronx block party.jpg"}]
        else:
            results = []
        return {
            "query": {
                "search": results,
            },
        }
    requested_titles = set((params.get("titles") or "").split("|"))
    pages = {}
    if "File:1520 Sedgwick Avenue.jpg" in requested_titles:
        pages["1"] = build_imageinfo_page(
            title="File:1520 Sedgwick Avenue.jpg",
            object_name="1520 Sedgwick Avenue",
            description="1520 Sedgwick Avenue in the Bronx.",
            license_name="CC BY-SA 4.0",
        )
    if "File:Bronx block party.jpg" in requested_titles:
        pages["2"] = build_imageinfo_page(
            title="File:Bronx block party.jpg",
            object_name="Bronx block party",
            description="Bronx hip hop block party crowd in 1973.",
            license_name="",
        )
    return {
        "query": {
            "pages": pages,
        },
    }


def build_imageinfo_page(
    *,
    title: str,
    object_name: str,
    description: str,
    license_name: str,
) -> dict[str, Any]:
    slug = title.removeprefix("File:").replace(" ", "_")
    extmetadata = {
        "ObjectName": {"value": object_name},
        "ImageDescription": {"value": description},
        "Artist": {"value": "Example photographer"},
    }
    if license_name:
        extmetadata["LicenseShortName"] = {"value": license_name}
        extmetadata["LicenseUrl"] = {"value": "https://creativecommons.org/licenses/by-sa/4.0/"}
    return {
        "title": title,
        "imageinfo": [
            {
                "url": f"https://upload.wikimedia.org/{slug}",
                "thumburl": f"https://upload.wikimedia.org/thumb/{slug}",
                "descriptionurl": f"https://commons.wikimedia.org/wiki/{slug}",
                "mime": "image/jpeg",
                "mediatype": "BITMAP",
                "extmetadata": extmetadata,
            },
        ],
    }
