from pydantic import BaseModel

from app.route_publication import RoutePublicationRepository
from app.route_review import (
    RouteReviewError,
    RouteReviewNotFoundError,
    RouteReviewRepository,
)
from app.schemas import Route


class RouteNavigationEntry(BaseModel):
    route: Route
    review_revision_id: str | None = None
    published_revision_id: str | None = None
    appears_in_published_routes: bool
    appears_in_routes_to_review: bool


class RouteNavigationSummary(BaseModel):
    routes: list[RouteNavigationEntry]


class RouteNavigationRepository:
    """Derive route-navigation membership from review and publication artifacts."""

    def __init__(
        self,
        review_repository: RouteReviewRepository,
        publication_repository: RoutePublicationRepository,
    ) -> None:
        self._review_repository = review_repository
        self._publication_repository = publication_repository

    def summary(self, routes: list[Route]) -> RouteNavigationSummary:
        entries: list[RouteNavigationEntry] = []
        for route in routes:
            review_revision_id: str | None = None
            published_revision_id: str | None = None
            try:
                review = self._review_repository.get(route.id)
                review_revision_id = review.revision_id
                published_revision_id = self._publication_repository.summary(
                    route.id
                ).published_revision_id
            except RouteReviewNotFoundError:
                pass
            except RouteReviewError:
                # A malformed review cannot be classified as published or ready
                # for review. The route remains absent rather than being guessed
                # from its seed status.
                pass

            entries.append(
                RouteNavigationEntry(
                    route=route,
                    review_revision_id=review_revision_id,
                    published_revision_id=published_revision_id,
                    appears_in_published_routes=published_revision_id is not None,
                    appears_in_routes_to_review=(
                        review_revision_id is not None
                        and review_revision_id != published_revision_id
                    ),
                )
            )
        return RouteNavigationSummary(routes=entries)
