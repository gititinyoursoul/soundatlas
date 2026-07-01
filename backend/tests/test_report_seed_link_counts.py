import json
from pathlib import Path

from scripts import report_seed_link_counts
from scripts.report_seed_link_counts import main


def test_report_seed_link_counts_prints_summary_with_ignorelist(
    tmp_path: Path,
    monkeypatch,
    capsys,
) -> None:
    events_path, routes_path = write_seed_files(tmp_path)
    monkeypatch.setattr(report_seed_link_counts, "EVENTS_PATH", events_path)
    monkeypatch.setattr(report_seed_link_counts, "ROUTES_PATH", routes_path)

    exit_code = main([])

    output = capsys.readouterr().out
    assert exit_code == 0
    assert "Seed link counts" in output
    assert "Scope: all events" in output
    assert "events: 2" in output
    assert "media links: 1" in output
    assert "image links: 2" in output
    assert "ignored entries: 3" in output
    assert "kool-herc-back-to-school-jam: media=1 image=2 ignored=2 total=3" in output
    assert "Ignored links" in output
    assert "  kool-herc-back-to-school-jam" in output
    assert "    image: 1 entry(s), 2 value(s)" in output
    assert "    media: 1 entry(s), 1 value(s)" in output
    assert "  other-route-event" in output
    assert "    image: 1 entry(s), 1 value(s)" in output


def test_report_seed_link_counts_json_supports_route_filter(
    tmp_path: Path,
    monkeypatch,
    capsys,
) -> None:
    events_path, routes_path = write_seed_files(tmp_path)
    monkeypatch.setattr(report_seed_link_counts, "EVENTS_PATH", events_path)
    monkeypatch.setattr(report_seed_link_counts, "ROUTES_PATH", routes_path)

    exit_code = main(
        [
            "--route-id",
            "birth-of-hip-hop",
            "--json",
        ],
    )

    payload = json.loads(capsys.readouterr().out)
    assert exit_code == 0
    assert payload["aggregate"]["event_count"] == 1
    assert payload["aggregate"]["media_links"] == 1
    assert payload["aggregate"]["image_links"] == 2
    assert payload["aggregate"]["ignored_entries"] == 2
    assert payload["events"][0]["event_id"] == "kool-herc-back-to-school-jam"
    assert payload["events"][0]["ignored_entries"] == 2
    assert len(payload["ignored_links"]) == 2


def test_report_seed_link_counts_reports_unknown_filters(
    tmp_path: Path,
    monkeypatch,
    capsys,
) -> None:
    events_path, routes_path = write_seed_files(tmp_path)
    monkeypatch.setattr(report_seed_link_counts, "EVENTS_PATH", events_path)
    monkeypatch.setattr(report_seed_link_counts, "ROUTES_PATH", routes_path)

    exit_code = main(["--event-id", "missing-event"])

    captured = capsys.readouterr()
    assert exit_code == 2
    assert "No event found for --event-id 'missing-event'." in captured.err


def write_seed_files(tmp_path: Path) -> tuple[Path, Path]:
    events_path = tmp_path / "events.json"
    routes_path = tmp_path / "routes.json"
    events_path.write_text(
        json.dumps(
            {
                "events": [
                    build_event(
                        {
                            "id": "kool-herc-back-to-school-jam",
                            "route_id": "birth-of-hip-hop",
                            "media_links": [build_media_link()],
                            "image_links": [
                                build_image_link(),
                                build_image_link("https://example.com/image-2.jpg"),
                            ],
                        },
                    ),
                    build_event(
                        {
                            "id": "other-route-event",
                            "route_id": "disco-to-dance-music",
                            "media_links": [],
                            "image_links": [],
                        },
                    ),
                ],
                "ignored_links": [
                    {
                        "event_id": "kool-herc-back-to-school-jam",
                        "kind": "image",
                        "values": [
                            "https://example.com/image-2.jpg",
                            "https://example.com/thumb-2.jpg",
                        ],
                    },
                    {
                        "event_id": "kool-herc-back-to-school-jam",
                        "kind": "media",
                        "values": ["https://www.youtube.com/watch?v=ignored"],
                    },
                    {
                        "event_id": "other-route-event",
                        "kind": "image",
                        "values": ["https://example.com/other.jpg"],
                    },
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
                    {"id": "birth-of-hip-hop"},
                    {"id": "disco-to-dance-music"},
                ],
            },
            indent=2,
        ),
        encoding="utf-8",
    )
    return events_path, routes_path


def build_event(overrides: dict[str, object]) -> dict[str, object]:
    event = {
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
        "image_links": [],
    }
    event.update(overrides)
    return event


def build_media_link() -> dict[str, object]:
    return {
        "provider": "youtube",
        "type": "video",
        "title": "Existing clip",
        "url": "https://www.youtube.com/watch?v=existing",
        "query": "existing",
        "confidence": 0.5,
        "review_status": "draft",
    }


def build_image_link(url: str = "https://example.com/image-1.jpg") -> dict[str, object]:
    return {
        "provider": "wikimedia",
        "type": "archive_photo",
        "title": "Example image",
        "image_url": url,
        "source_url": "https://commons.wikimedia.org/wiki/File:Example.jpg",
        "rights_status": "open_license",
        "alt_text": "Example image.",
        "query": "example",
        "confidence": 0.6,
        "review_status": "draft",
    }
