from app.seed_repository import SeedRepository


def test_seed_repository_loads_routes_places_events_and_connections() -> None:
    repository = SeedRepository.from_seed_dir()

    route_ids = {route.id for route in repository.list_routes()}

    assert route_ids == {
        "birth-of-hip-hop",
        "disco-to-dance-music",
        "punk-new-wave-downtown",
    }
    assert len(repository.list_places()) == 24
    assert len(repository.list_events()) == 36
    assert len(repository.list_connections()) == 35


def test_seed_repository_filters_connections_by_route() -> None:
    repository = SeedRepository.from_seed_dir()

    hip_hop_connections = repository.list_connections(route_id="birth-of-hip-hop")
    disco_connections = repository.list_connections(route_id="disco-to-dance-music")
    punk_connections = repository.list_connections(route_id="punk-new-wave-downtown")

    assert len(hip_hop_connections) == 12
    assert len(disco_connections) == 11
    assert len(punk_connections) == 11
    assert {connection.review_status for connection in hip_hop_connections} == {"draft"}
    assert {connection.review_status for connection in disco_connections} == {"draft"}
    assert {connection.review_status for connection in punk_connections} == {"draft"}
