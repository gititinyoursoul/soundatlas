from app.seed_repository import SeedRepository


def test_seed_repository_loads_routes_places_events_and_connections() -> None:
    repository = SeedRepository.from_seed_dir()

    assert len(repository.list_routes()) == 1
    assert len(repository.list_places()) == 8
    assert len(repository.list_events()) == 12
    assert len(repository.list_connections()) == 12


def test_seed_repository_filters_connections_by_route() -> None:
    repository = SeedRepository.from_seed_dir()

    connections = repository.list_connections(route_id="birth-of-hip-hop")

    assert len(connections) == 12
    assert {connection.review_status for connection in connections} == {"draft"}
