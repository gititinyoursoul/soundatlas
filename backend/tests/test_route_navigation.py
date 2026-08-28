from pathlib import Path

from fastapi.testclient import TestClient

from app.main import create_app
from app.route_navigation import RouteNavigationRepository
from app.route_publication import RoutePublicationRepository
from app.route_review import RouteReviewRepository
from app.seed_repository import SeedRepository
from tests.test_route_publication import ROUTE_ID, write_publication_fixture


def test_route_navigation_classifies_published_and_changed_review(tmp_path: Path) -> None:
    content_root = tmp_path / "content"
    seed_dir = tmp_path / "seed"
    write_publication_fixture(content_root, seed_dir)
    review_repository = RouteReviewRepository(content_root, seed_dir=seed_dir)
    review = review_repository.refresh(ROUTE_ID)
    publication_repository = RoutePublicationRepository(
        review_repository, content_root=content_root, seed_dir=seed_dir
    )
    repository = RouteNavigationRepository(review_repository, publication_repository)

    before = repository.summary(SeedRepository.from_seed_dir(seed_dir).list_routes())
    assert before.routes[0].appears_in_published_routes is False
    assert before.routes[0].appears_in_routes is True
    assert before.routes[0].appears_in_routes_to_review is True

    publication_repository.publish(ROUTE_ID, review.revision_id)
    after = repository.summary(SeedRepository.from_seed_dir(seed_dir).list_routes())
    assert after.routes[0].published_revision_id == review.revision_id
    assert after.routes[0].appears_in_published_routes is True
    assert after.routes[0].appears_in_routes is True
    assert after.routes[0].appears_in_routes_to_review is False

    client = TestClient(
        create_app(
            SeedRepository.from_seed_dir(seed_dir),
            route_review_repository=review_repository,
            route_publication_repository=publication_repository,
        )
    )
    response = client.get("/editorial/route-navigation")
    assert response.status_code == 200
    assert response.json()["routes"][0]["published_revision_id"] == review.revision_id
