from app.schemas import ImageLink, MediaLink
from app.seed_repository import SeedRepository


def test_seed_repository_loads_routes_places_events_and_connections() -> None:
    repository = SeedRepository.from_seed_dir()

    route_ids = {route.id for route in repository.list_routes()}

    assert route_ids == {
        "birth-of-hip-hop",
        "disco-to-dance-music",
        "new-york-builds-the-dance-floor",
        "punk-new-wave-downtown",
        "salsa-latin-new-york",
        "downtown-experiment-no-wave-loft-jazz",
    }
    assert len(repository.list_places()) == 41

    expected_event_counts = {
        "birth-of-hip-hop": 12,
        "disco-to-dance-music": 12,
        "new-york-builds-the-dance-floor": 7,
        "punk-new-wave-downtown": 12,
        "salsa-latin-new-york": 12,
        "downtown-experiment-no-wave-loft-jazz": 12,
    }

    for route_id, expected_count in expected_event_counts.items():
        assert len(repository.list_events(route_id=route_id)) == expected_count
        
    assert len(repository.list_events()) == sum(expected_event_counts.values())

    assert len(repository.list_connections()) == 57
    assert {route.creator for route in repository.list_routes()} == {
        "SoundAtlas",
        "gpt-5.5",
    }
    for event in repository.list_events():
        assert event.place_ids
        assert event.default_place_id in event.place_ids
        assert event.place_id == event.default_place_id
        assert all(isinstance(media_link, MediaLink) for media_link in event.media_links)
        assert all(isinstance(image_link, ImageLink) for image_link in event.image_links)

    geometries = {
        place.id: place for place in repository.list_places() if place.geometry is not None
    }
    assert set(geometries) == {
        "south-bronx",
        "cedar-playground-bronx",
        "east-harlem-el-barrio",
    }
    assert geometries["cedar-playground-bronx"].geometry_source_type == "external"
    assert geometries["south-bronx"].geometry_source_type == "curated"


def test_seed_repository_filters_connections_by_route() -> None:
    repository = SeedRepository.from_seed_dir()

    hip_hop_connections = repository.list_connections(route_id="birth-of-hip-hop")
    disco_connections = repository.list_connections(route_id="disco-to-dance-music")
    punk_connections = repository.list_connections(route_id="punk-new-wave-downtown")
    salsa_connections = repository.list_connections(route_id="salsa-latin-new-york")
    downtown_experiment_connections = repository.list_connections(
        route_id="downtown-experiment-no-wave-loft-jazz",
    )

    assert len(hip_hop_connections) == 12
    assert len(disco_connections) == 11
    assert len(punk_connections) == 11
    assert len(salsa_connections) == 11
    assert len(downtown_experiment_connections) == 11
    assert {connection.review_status for connection in hip_hop_connections} == {"draft"}
    assert {connection.review_status for connection in disco_connections} == {"draft"}
    assert {connection.review_status for connection in punk_connections} == {"draft"}
    assert {connection.review_status for connection in salsa_connections} == {"draft"}
    assert {connection.review_status for connection in downtown_experiment_connections} == {
        "draft",
    }
