from app.seed_repository import SeedRepository


def test_seed_repository_loads_routes_places_events_and_connections() -> None:
    repository = SeedRepository.from_seed_dir()

    route_ids = {route.id for route in repository.list_routes()}

    assert route_ids == {"birth-of-hip-hop", "disco-to-dance-music"}
    assert len(repository.list_places()) == 16
    assert len(repository.list_events()) == 24
    assert len(repository.list_connections()) == 24


def test_seed_repository_filters_connections_by_route() -> None:
    repository = SeedRepository.from_seed_dir()

    hip_hop_connections = repository.list_connections(route_id="birth-of-hip-hop")
    disco_connections = repository.list_connections(route_id="disco-to-dance-music")

    assert len(hip_hop_connections) == 12
    assert len(disco_connections) == 11
    assert {connection.review_status for connection in hip_hop_connections} == {"draft"}
    assert {connection.review_status for connection in disco_connections} == {"draft"}
