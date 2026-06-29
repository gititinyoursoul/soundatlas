from app.media_enrichment.retrieval_brief import build_retrieval_brief


def test_build_retrieval_brief_marks_concrete_place_as_strong_term() -> None:
    brief = build_retrieval_brief(
        event={
            "id": "kool-herc-back-to-school-jam",
            "route_id": "birth-of-hip-hop",
            "place_id": "1520-sedgwick-avenue",
            "title": "Kool Herc's Back-to-School Jam",
            "year_start": 1973,
            "year_end": 1973,
            "summary": "DJ Kool Herc plays in the community room at 1520 Sedgwick Avenue.",
            "significance": "A symbolic origin point for Bronx hip hop party culture.",
            "tags": ["kool-herc", "block-party", "bronx", "origin-story"],
        },
        route={"id": "birth-of-hip-hop", "title": "Birth of Hip-Hop"},
        place={
            "id": "1520-sedgwick-avenue",
            "name": "1520 Sedgwick Avenue",
            "place_type": "building",
        },
    )

    assert brief.event_id == "kool-herc-back-to-school-jam"
    assert brief.year_phrase == "1973"
    assert "Kool Herc's Back-to-School Jam" in brief.strong_terms
    assert "1520 Sedgwick Avenue" in brief.strong_terms
    assert "DJ Kool Herc" in brief.strong_terms
    assert "Birth of Hip-Hop" in brief.supporting_terms
    assert "bronx" in brief.risky_terms


def test_build_retrieval_brief_marks_broad_place_as_supporting_term() -> None:
    brief = build_retrieval_brief(
        event={
            "id": "caribbean-soundsystem-influences",
            "route_id": "birth-of-hip-hop",
            "place_id": "south-bronx",
            "title": "Caribbean Sound System Influences Reach the Bronx",
            "year_start": 1967,
            "year_end": 1972,
            "summary": "Mobile sound-system practice reaches Bronx neighborhood parties.",
            "significance": "This context links Caribbean, African American, and Latino influences.",
            "tags": ["migration", "sound-system", "bronx", "dj-culture"],
        },
        route={"id": "birth-of-hip-hop", "title": "Birth of Hip-Hop"},
        place={"id": "south-bronx", "name": "South Bronx", "place_type": "region"},
    )

    assert brief.year_phrase == "1967 1972"
    assert "South Bronx" not in brief.strong_terms
    assert "South Bronx" in brief.supporting_terms
    assert "bronx" in brief.risky_terms


def test_build_retrieval_brief_extracts_named_artist_terms() -> None:
    brief = build_retrieval_brief(
        event={
            "id": "grandmaster-flash-dj-techniques",
            "route_id": "birth-of-hip-hop",
            "place_id": "south-bronx",
            "title": "Grandmaster Flash Refines DJ Techniques",
            "year_start": 1975,
            "year_end": 1977,
            "summary": "Grandmaster Flash develops backspin and punch phrasing.",
            "significance": "The turntables become a playable instrument.",
            "tags": ["grandmaster-flash", "dj-technique", "turntablism", "bronx"],
        },
        route={"id": "birth-of-hip-hop", "title": "Birth of Hip-Hop"},
        place={"id": "south-bronx", "name": "South Bronx", "place_type": "region"},
    )

    assert brief.year_phrase == "1975 1977"
    assert "Grandmaster Flash" in brief.strong_terms
    assert "turntablism" in brief.supporting_terms
    assert "South Bronx" in brief.supporting_terms


def test_build_retrieval_brief_handles_missing_route_and_place() -> None:
    brief = build_retrieval_brief(
        event={
            "id": "event-id",
            "route_id": "route-id",
            "place_id": "place-id",
            "title": "Minimal Event",
            "tags": [],
            "source_urls": [],
        },
        route={},
        place={},
    )

    assert brief.event_id == "event-id"
    assert brief.route_id == "route-id"
    assert brief.place_id == "place-id"
    assert brief.route_title == ""
    assert brief.place_name == ""
    assert brief.year_phrase == ""
    assert brief.supporting_terms == ()
    assert "reaction" in brief.avoid_terms
