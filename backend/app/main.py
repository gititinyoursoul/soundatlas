from fastapi import Depends, FastAPI, HTTPException, Query, status
from fastapi.middleware.cors import CORSMiddleware

from app.config import LOCAL_CORS_ORIGINS
from app.schemas import Connection, Event, HealthResponse, Place, Route
from app.seed_repository import SeedRepository


def create_app(repository: SeedRepository | None = None) -> FastAPI:
    active_repository = repository or SeedRepository.from_seed_dir()

    api = FastAPI(
        title="SoundAtlas API",
        version="0.1.0",
        description="Seed-backed API for the SoundAtlas MVP.",
    )

    api.add_middleware(
        CORSMiddleware,
        allow_origins=LOCAL_CORS_ORIGINS,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    def get_repository() -> SeedRepository:
        return active_repository

    @api.get("/health", response_model=HealthResponse)
    def health() -> HealthResponse:
        return HealthResponse(status="ok")

    @api.get("/routes", response_model=list[Route])
    def list_routes(
        seed_repository: SeedRepository = Depends(get_repository),
    ) -> list[Route]:
        return seed_repository.list_routes()

    @api.get("/events", response_model=list[Event])
    def list_events(
        from_year: int | None = Query(default=None),
        to_year: int | None = Query(default=None),
        route_id: str | None = Query(default=None),
        seed_repository: SeedRepository = Depends(get_repository),
    ) -> list[Event]:
        if from_year is not None and to_year is not None and from_year > to_year:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="from_year must be less than or equal to to_year",
            )
        if route_id is not None and not seed_repository.has_route(route_id):
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Route '{route_id}' not found",
            )
        return seed_repository.list_events(
            from_year=from_year,
            to_year=to_year,
            route_id=route_id,
        )

    @api.get("/events/{event_id}", response_model=Event)
    def get_event(
        event_id: str,
        seed_repository: SeedRepository = Depends(get_repository),
    ) -> Event:
        event = seed_repository.get_event(event_id)
        if event is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Event '{event_id}' not found",
            )
        return event

    @api.get("/places", response_model=list[Place])
    def list_places(
        seed_repository: SeedRepository = Depends(get_repository),
    ) -> list[Place]:
        return seed_repository.list_places()

    @api.get("/connections", response_model=list[Connection])
    def list_connections(
        route_id: str | None = Query(default=None),
        seed_repository: SeedRepository = Depends(get_repository),
    ) -> list[Connection]:
        if route_id is not None and not seed_repository.has_route(route_id):
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Route '{route_id}' not found",
            )
        return seed_repository.list_connections(route_id=route_id)

    return api


app = create_app()
