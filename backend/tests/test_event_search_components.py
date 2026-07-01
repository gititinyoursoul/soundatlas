import json
from pathlib import Path

from app.media_enrichment.event_search_components import (
    EventSearchComponent,
    build_event_search_component,
    validate_component_for_seed,
)
from scripts import generate_event_search_components
from scripts.enrich_image_links import build_wikimedia_search_queries


def test_build_component_extracts_artist_place_and_time_context() -> None:
    component = build_event_search_component(
        event=build_event(),
        route=build_route(),
        place=build_place(),
    )
    report = validate_component_for_seed(
        component=component,
        event=build_event(),
        place=build_place(),
    )

    assert component.event_id == "kool-herc-back-to-school-jam"
    assert component.time_context.query_year_phrase == "1973"
    assert "DJ Kool Herc" in component.entities.artists
    assert "1520 Sedgwick Avenue" in component.entities.places
    assert "Bronx" in component.entities.places
    assert "New York" in component.entities.places
    assert report.errors == []


def test_build_component_types_quoted_release_and_film_works() -> None:
    release_component = build_event_search_component(
        event=build_event(
            {
                "id": "rappers-delight-mainstream-breakthrough",
                "title": "Rapper's Delight Brings Rap into the Charts",
                "year_start": 1979,
                "year_end": 1979,
                "summary": "The Sugarhill Gang's 'Rapper's Delight' makes rap visible.",
                "significance": "The event marks the transition to records and industry.",
                "tags": ["rappers-delight", "sugarhill-gang", "industry"],
            },
        ),
        route=build_route(),
        place=build_place({"name": "Sugar Hill Records", "place_type": "label"}),
    )
    film_component = build_event_search_component(
        event=build_event(
            {
                "id": "wild-style-global-visibility",
                "title": "Wild Style Documents the Four Elements",
                "year_start": 1983,
                "year_end": 1983,
                "summary": "Charlie Ahearn's film 'Wild Style' shows early hip-hop culture.",
                "significance": "The feature film makes the scene internationally legible.",
                "tags": ["wild-style", "film"],
            },
        ),
        route=build_route(),
        place=build_place({"name": "South Bronx", "place_type": "region"}),
    )

    assert [(work.title, work.type) for work in release_component.entities.works] == [
        ("Rapper's Delight", "release"),
    ]
    assert [(work.title, work.type) for work in film_component.entities.works] == [
        ("Wild Style", "film"),
    ]


def test_component_validation_reports_broad_only_terms_as_warning() -> None:
    component = EventSearchComponent.model_validate(
        {
            "event_id": "broad-event",
            "time_context": {
                "year_start": 1977,
                "year_end": 1977,
                "query_year_phrase": "1977",
            },
            "search_control": {
                "strong_terms": ["Bronx", "music"],
                "supporting_terms": [],
                "risky_terms": [],
                "avoid_terms": [],
            },
        },
    )

    report = validate_component_for_seed(
        component=component,
        event=build_event(
            {
                "id": "broad-event",
                "title": "Broad Event",
                "year_start": 1977,
                "year_end": 1977,
                "tags": ["bronx"],
            },
        ),
        place=build_place({"place_type": "region"}),
    )

    assert report.errors == []
    assert "strong_terms only contains broad terms." in report.warnings


def test_image_query_planner_prefers_component_file_when_present(tmp_path: Path) -> None:
    component_dir = tmp_path / "event-search-components"
    component_dir.mkdir()
    (component_dir / "generic-technique-event.json").write_text(
        json.dumps(
            {
                "event_id": "generic-technique-event",
                "event_type": "technique_development",
                "entities": {
                    "artists": ["Grandmaster Flash"],
                    "places": ["South Bronx", "New York"],
                    "works": [],
                    "organizations": [],
                    "techniques": ["backspin"],
                    "historical_events": [],
                },
                "context": {
                    "genres": ["hip hop"],
                    "scenes": ["Bronx hip-hop"],
                    "communities": [],
                    "practices": ["DJing"],
                    "industry_terms": [],
                    "route_terms": ["Birth of Hip-Hop"],
                },
                "time_context": {
                    "year_start": 1975,
                    "year_end": 1977,
                    "query_year_phrase": "1975 1977",
                },
                "search_control": {
                    "strong_terms": ["Grandmaster Flash"],
                    "supporting_terms": ["1975 1977", "Bronx hip-hop"],
                    "risky_terms": ["Bronx"],
                    "avoid_terms": ["reaction"],
                },
            },
        ),
        encoding="utf-8",
    )

    queries = build_wikimedia_search_queries(
        event=build_event(
            {
                "id": "generic-technique-event",
                "title": "DJ Technique Develops",
                "year_start": 1975,
                "year_end": 1977,
                "summary": "A DJ technique becomes more precise.",
                "significance": "The turntable becomes more playable.",
                "tags": ["dj-technique"],
            },
        ),
        route=build_route(),
        place=build_place({"name": "South Bronx", "place_type": "region"}),
        query_planner="v2",
        component_dir=component_dir,
    )

    assert queries[0] == "Grandmaster Flash 1975 1977"
    assert "Grandmaster Flash 1970s" in queries


def test_generator_dry_run_json_does_not_write_files(
    tmp_path: Path,
    monkeypatch,
    capsys,
) -> None:
    events_path, routes_path, places_path = write_seed_files(tmp_path)
    output_dir = tmp_path / "components"
    monkeypatch.setattr(generate_event_search_components, "EVENTS_PATH", events_path)
    monkeypatch.setattr(generate_event_search_components, "ROUTES_PATH", routes_path)
    monkeypatch.setattr(generate_event_search_components, "PLACES_PATH", places_path)

    exit_code = generate_event_search_components.main(
        [
            "--event-id",
            "kool-herc-back-to-school-jam",
            "--output-dir",
            str(output_dir),
            "--dry-run",
            "--json",
        ],
    )

    payload = json.loads(capsys.readouterr().out)
    assert exit_code == 0
    assert not output_dir.exists()
    assert payload["components"][0]["component"]["event_id"] == "kool-herc-back-to-school-jam"
    assert payload["components"][0]["validation"]["errors"] == []


def test_generator_write_creates_component_file(
    tmp_path: Path,
    monkeypatch,
    capsys,
) -> None:
    events_path, routes_path, places_path = write_seed_files(tmp_path)
    output_dir = tmp_path / "components"
    monkeypatch.setattr(generate_event_search_components, "EVENTS_PATH", events_path)
    monkeypatch.setattr(generate_event_search_components, "ROUTES_PATH", routes_path)
    monkeypatch.setattr(generate_event_search_components, "PLACES_PATH", places_path)

    exit_code = generate_event_search_components.main(
        [
            "--event-id",
            "kool-herc-back-to-school-jam",
            "--output-dir",
            str(output_dir),
        ],
    )

    output = capsys.readouterr().out
    component_path = output_dir / "kool-herc-back-to-school-jam.json"
    assert exit_code == 0
    assert component_path.exists()
    assert "Mode: write" in output
    assert "kool-herc-back-to-school-jam.json" in output


def write_seed_files(tmp_path: Path) -> tuple[Path, Path, Path]:
    events_path = tmp_path / "events.json"
    routes_path = tmp_path / "routes.json"
    places_path = tmp_path / "places.json"
    events_path.write_text(json.dumps({"events": [build_event()]}), encoding="utf-8")
    routes_path.write_text(json.dumps({"routes": [build_route()]}), encoding="utf-8")
    places_path.write_text(json.dumps({"places": [build_place()]}), encoding="utf-8")
    return events_path, routes_path, places_path


def build_event(overrides: dict | None = None) -> dict:
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
    return event


def build_route(overrides: dict | None = None) -> dict:
    route = {
        "id": "birth-of-hip-hop",
        "title": "Birth of Hip-Hop",
        "tags": ["hip-hop", "bronx"],
    }
    if overrides:
        route.update(overrides)
    return route


def build_place(overrides: dict | None = None) -> dict:
    place = {
        "id": "1520-sedgwick-avenue",
        "name": "1520 Sedgwick Avenue",
        "borough": "Bronx",
        "place_type": "building",
    }
    if overrides:
        place.update(overrides)
    return place
