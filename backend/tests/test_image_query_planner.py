from app.media_enrichment.image_query_planner import plan_image_queries
from app.media_enrichment.retrieval_brief import build_retrieval_brief


def test_plan_image_queries_for_concrete_venue_and_artist() -> None:
    plans = plan_image_queries(
        build_retrieval_brief(
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
        ),
    )

    assert ("venue_photo", "1520 Sedgwick Avenue") in plan_pairs(plans)
    assert ("artist_photo", "DJ Kool Herc") in plan_pairs(plans)
    assert "bronx" not in planned_queries(plans)


def test_plan_image_queries_for_artist_event_avoids_broad_place_query() -> None:
    plans = plan_image_queries(
        build_retrieval_brief(
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
        ),
    )

    assert ("artist_photo", "Grandmaster Flash") in plan_pairs(plans)
    assert ("archive_photo", "Grandmaster Flash Refines DJ Techniques") in plan_pairs(plans)
    assert "South Bronx" not in planned_queries(plans)


def test_plan_image_queries_for_context_event_does_not_use_region_only_query() -> None:
    plans = plan_image_queries(
        build_retrieval_brief(
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
        ),
    )

    assert ("archive_photo", "Caribbean Sound System Influences Reach the Bronx") in plan_pairs(plans)
    assert "South Bronx" not in planned_queries(plans)
    assert "bronx" not in planned_queries(plans)


def test_plan_image_queries_for_quoted_release() -> None:
    plans = plan_image_queries(
        build_retrieval_brief(
            event={
                "id": "rappers-delight-mainstream-breakthrough",
                "route_id": "birth-of-hip-hop",
                "place_id": "englewood-sugar-hill-records",
                "title": "Rapper's Delight Brings Rap into the Charts",
                "year_start": 1979,
                "year_end": 1979,
                "summary": "The Sugarhill Gang's 'Rapper's Delight' makes rap visible to a broad audience.",
                "significance": "The event marks the transition to records, industry, and mass media.",
                "tags": ["rappers-delight", "sugarhill-gang", "industry", "mainstream"],
            },
            route={"id": "birth-of-hip-hop", "title": "Birth of Hip-Hop"},
            place={
                "id": "englewood-sugar-hill-records",
                "name": "Sugar Hill Records",
                "place_type": "label",
            },
        ),
    )

    assert ("album_cover", "Rapper") not in plan_pairs(plans)
    assert ("album_cover", "Rapper's Delight") in plan_pairs(plans)


def plan_pairs(plans):
    return {(plan.target_type, plan.query) for plan in plans}


def planned_queries(plans):
    return {plan.query for plan in plans}
