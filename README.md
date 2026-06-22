# SoundAtlas

SoundAtlas is an MVP for an interactive music history app. The current scope is **New York 1965-1985** with curated routes, events, places, connections, and external media links.

## Requirements

- Python `>=3.13`
- `uv`
- Node.js and npm
- PowerShell for the optional startup script

## Local Development

Quick start:

```powershell
.\scripts\start-dev.ps1
```

After startup, the app runs locally at:

- Backend: `http://127.0.0.1:8000`
- Frontend: `http://127.0.0.1:5173`

Start the backend manually:

```powershell
cd backend
uv run uvicorn app.main:app --reload --host 127.0.0.1 --port 8000
```

Start the frontend manually:

```powershell
cd frontend
$env:VITE_API_BASE_URL='http://127.0.0.1:8000'
npm run dev -- --host 127.0.0.1 --port 5173
```

## Docker Compose Development

Start the containerized development environment:

```powershell
docker compose up --build
```

After startup, the app runs locally at:

- Backend: `http://localhost:8000`
- Backend health: `http://localhost:8000/health`
- Frontend: `http://localhost:5173`

Stop the environment:

```powershell
docker compose down
```

Run checks inside containers:

```powershell
docker compose run --rm backend uv run pytest
docker compose run --rm frontend npm run check
```

The Compose setup mounts only repo-local project paths, runs the app processes
as the `soundatlas` user, and keeps dependency folders in named volumes. Runtime
egress is restricted by `docker/egress-guard.sh`: general outbound HTTPS is
allowed, while common private/internal ranges and metadata IPs are rejected.
Image builds still use Docker's normal build network.

## VS Code Dev Containers

Open this repository with the VS Code Dev Containers extension and choose
`Reopen in Container`. The Dev Container uses the Docker Compose setup and
starts both backend and frontend services.

## Tests And Checks

Backend:

```powershell
cd backend
uv run pytest
```

Frontend:

```powershell
cd frontend
npm run check
```

## Data

The MVP seed data is stored in:

- `data/seed/routes.json`
- `data/seed/places.json`
- `data/seed/events.json`
- `data/seed/connections.json`

Validation rules: `docs/seed-validation.md`

## Media Retrieval

The current automated workflow is a YouTube-only MVP. It generates draft candidates for `media_links`; no audio or video files are stored.

Important docs:

- Workflow: `docs/media-retrieval/youtube-mvp-workflow.md`
- Workflow Commands: `docs/media-retrieval/workflow-commands.md`
- Event Search Components: `docs/media-retrieval/event-search-components.md`
- Query Planning: `docs/media-retrieval/query-planning.md`
- Codex Curation: `docs/media-retrieval/codex-query-curation.md`

Dry run for curated YouTube request plans:

```powershell
cd backend
uv run python scripts/run_youtube_search_requests.py --dry-run
```

Merge dry run for existing YouTube results:

```powershell
cd backend
uv run python scripts/enrich_media_links.py --dry-run
```

Live YouTube requests require a real `YOUTUBE_API_KEY` via `SOUNDATLAS_ENV_FILE`. See `.env.example`.

## Project Structure

- `backend/`: FastAPI app, Pydantic schemas, tests, and YouTube retrieval scripts
- `frontend/`: SvelteKit app with map, timeline, route filter, and story panel
- `data/seed/`: curated JSON data for the MVP
- `data/enrichment/`: curated query plans and generated retrieval results
- `docs/`: product, route, data validation, and media retrieval documentation
- `scripts/`: local helper scripts

## Working Rules

- Do not commit secrets or local paths.
- Do not store audio or video files in the repository.
- Keep data sources and media links as external URLs.
- Automatically generated media links remain `review_status: "draft"` until manually reviewed.
