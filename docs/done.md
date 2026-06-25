# SoundAtlas Done

Archive of completed work packages. The current work list lives in `TODO.md`.

## Product and Content

- [x] Finalize the guiding question for the MVP
- [x] Editorially develop the `Birth of Hip-Hop` route
- [x] Define 8-12 events for the hip-hop route
- [x] Capture 5-8 places with coordinates
- [x] Define 8-12 influence connections
- [x] Define the source structure for events
- [x] Clarify media-link rules: YouTube, Spotify, Internet Archive, or external links
- [x] Document the media enrichment concept
- [x] Mark open historical uncertainties

## Seed Data

- [x] Define the data format for routes, events, places, and connections
- [x] Create `data/seed/routes.json`
- [x] Create `data/seed/places.json`
- [x] Create `data/seed/events.json`
- [x] Create `data/seed/connections.json`
- [x] Add sample data for `Birth of Hip-Hop`
- [x] Define simple validation for required fields
- [x] Model source and media links as arrays

## Backend

- [x] Update the backend project description in `backend/pyproject.toml`
- [x] Create the FastAPI app structure under `backend/app/`
- [x] Define Pydantic schemas for API responses
- [x] Load JSON seed files in the backend
- [x] Validate seed data against `docs/seed-validation.md`
- [x] Implement `GET /health`
- [x] Implement `GET /routes`
- [x] Implement `GET /events` with `from_year`, `to_year`, and `route_id`
- [x] Implement `GET /events/{event_id}`
- [x] Implement `GET /places`
- [x] Implement `GET /connections` with `route_id`
- [x] Define error behavior for unknown IDs and empty filter results
- [x] Add local CORS configuration for the frontend
- [x] Add minimal backend tests for health and events
- [x] Introduce safe media enrichment settings with an external secret path
- [x] Implement a mockable YouTube analysis/search/ranking pipeline for content pages
- [x] Adjust the YouTube search prompt `prompts/generate-youtube-search-queries.md` to exclude Shorts
- [x] Check whether `backend/scripts/enrich_media_links.py` is compatible with the plus-only workflow

## Frontend

- [x] Migrate the existing `frontend/` to SvelteKit
- [x] Set up TypeScript configuration and SvelteKit scripts
- [x] Check frontend dependencies: SvelteKit, Vite, TypeScript, Leaflet
- [x] Define the API base URL for local development
- [x] Create TypeScript types for `Route`, `Place`, `Event`, and `Connection`
- [x] Build an API client for `/routes`, `/events`, `/places`, and `/connections`
- [x] Build the first page as an app shell with map, timeline, and side panel
- [x] Integrate Leaflet safely for browser use in Svelte
- [x] Create a `MapView` component with event markers
- [x] Create a `Timeline` component for the `1965-1985` period
- [x] Create a `RouteFilter` component for active routes
- [x] Create a `StoryPanel` component for the selected event
- [x] Define shared frontend state for route, time range, and selected event
- [x] Filter event markers by active time range and route
- [x] Render route colors consistently from API data
- [x] Show loading, error, and empty states
- [x] Define and run a frontend smoke check or build check

## UX and Design

- [x] Define the first screen layout: map, timeline, side panel
- [x] Define color coding per route
- [x] Define marker states: default, hover, selected
- [x] Make 1977 visible as a dramatic focus
- [x] Roughly check the mobile layout
- [x] Show sources and media links in the story panel
- [x] Show connections between events visually or textually
- [x] Check frontend acceptance criteria: map shows hip-hop events, timeline filters, story panel reacts to marker selection

## Image Material

- [x] Document the concept for event image material
- [x] Define `image_links` in the event schema
- [x] Document seed validation rules for image links
- [x] Initialize existing events with empty `image_links`
- [x] Extend the story panel for reviewed image material
- [x] Add tests for image-link schema and seed data
- [x] Plan an optional script for automatic image candidates

## Infrastructure

- [x] Create a root README for project start
- [x] Document the backend start command
- [x] Document the frontend start command
- [x] Define shared development commands
- [x] Define a containerized local development environment for backend and frontend with Docker Compose
- [x] Document Codex CLI in the dev container as the preferred agent workflow
- [x] Check `AGENTS.md` and translate it into English

## Docker Compose Run Checklist

- [x] Define the target mode: local development containers with hot reload for backend and frontend
- [x] Plan the backend container: Python `>=3.13`, `uv`, working directory `/workspace/backend`
- [x] Create the backend `Dockerfile` under `backend/Dockerfile`
- [x] Install backend dependencies reproducibly through `uv sync` or `uv run`
- [x] Define the backend start command in the container: `uv run uvicorn app.main:app --reload --host 0.0.0.0 --port 8000`
- [x] Ensure the backend container has access to `data/seed/` from the repo root
- [x] Plan the frontend container: Node.js LTS, npm, working directory `/workspace/frontend`
- [x] Create the frontend `Dockerfile` under `frontend/Dockerfile`
- [x] Install frontend dependencies through `npm ci` from `package-lock.json`
- [x] Define the frontend start command in the container: `npm run dev -- --host 0.0.0.0 --port 5173`
- [x] Set frontend env in Compose: `VITE_API_BASE_URL=http://localhost:8000`
- [x] Create root `docker-compose.yml` with `backend` and `frontend` services
- [x] Map ports: backend `8000:8000`, frontend `5173:5173`
- [x] Define bind mounts for development: `./backend`, `./frontend`, and `./data`
- [x] Limit bind mounts to repo paths; do not mount host home, SSH, cloud, or global config directories
- [x] Protect container-internal dependency directories from host conflicts, for example with separate volumes for `node_modules` and the Python environment
- [x] Run containers as a non-root user and check file permissions for mounted repo paths
- [x] Control secrets: do not copy secrets into the image; use only explicit env files or Docker secrets
- [x] Update `.env.example` for container variables without real tokens or local paths
- [x] Allow general outgoing HTTPS for dependency installation and API usage
- [x] Block access to private/internal networks and cloud metadata IPs, for example `169.254.169.254`, RFC1918 networks, and local host services where not needed by the app
- [x] Add `depends_on` from frontend to backend
- [x] Define an optional backend health check for `GET /health` in the Compose file
- [x] Configure VS Code Dev Containers, for example `.devcontainer/devcontainer.json` with Docker Compose integration
- [x] Limit the dev-container workspace to the repo and do not automatically mount extra host directories
- [x] Define only minimal dev-container extensions for Python, Svelte/TypeScript, and Docker
- [x] Check or create `.dockerignore` for root, backend, and frontend
- [x] Document Docker Compose start: `docker compose up --build`
- [x] Document Docker Compose stop: `docker compose down`
- [x] Document smoke test: check `http://localhost:8000/health` and `http://localhost:5173` in the browser
- [x] Document backend tests in the container: `docker compose run --rm backend uv run pytest`
- [x] Document frontend check in the container: `docker compose run --rm frontend npm run check`
- [x] Extend the README with the Docker Compose startup path once the containers are runnable

## Next Concrete Step

- [x] Create the seed data structure for `Birth of Hip-Hop` and fill it with the first events
- [x] Create the FastAPI app structure and load seed data
- [x] Migrate the frontend base structure to SvelteKit and connect the API client

## Frontend Acceptance Criteria for the Next Slice

- [x] App starts locally with SvelteKit
- [x] Backend data is loaded through the FastAPI endpoints
- [x] Map shows markers for `birth-of-hip-hop`
- [x] Timeline filters visible events by time range
- [x] Route filter can show and hide `Birth of Hip-Hop`
- [x] Clicking a marker opens event details in the story panel
- [x] Empty and failed API states are visibly handled
