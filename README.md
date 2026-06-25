# SoundAtlas

SoundAtlas is an MVP for an interactive music history app. Current scope:
**New York 1965-1985**, starting with the vertical slice
**Birth of Hip-Hop: Bronx 1970-1985**.

## Quick Start

### Local

Requirements: Python `>=3.13`, `uv`, Node.js/npm, PowerShell.

```powershell
.\scripts\start-dev.ps1
```

App URLs:

- Backend: `http://127.0.0.1:8000`
- Frontend: `http://127.0.0.1:5173`

### Docker Compose

```powershell
docker compose up --build
```

App URLs:

- Backend: `http://localhost:8000`
- Backend health: `http://localhost:8000/health`
- Frontend: `http://localhost:5173`

Stop the containers:

```powershell
docker compose down
```

### Codex CLI Dev Container

Start the containerized Codex workspace:

```powershell
docker compose -f docker-compose.yml -f .devcontainer/docker-compose.devcontainer.yml up -d --build workspace
docker compose -f docker-compose.yml -f .devcontainer/docker-compose.devcontainer.yml exec --user soundatlas workspace sh .devcontainer/post-create.sh
docker compose -f docker-compose.yml -f .devcontainer/docker-compose.devcontainer.yml exec --user soundatlas workspace bash
```

The `post-create.sh` step is important for CLI-only startup: it seeds Codex
auth/config into the container volume, trusts `/workspace`, and applies the
dev-container Codex permission defaults.

Then start Codex inside the container:

```sh
cd /workspace
codex
```

This is the preferred setup for agent-assisted coding. Codex runs inside the
same isolated workspace as the app, so it sees the project filesystem,
dependencies, environment variables, test commands, linters, and build tools
used by the containers. VS Code can still attach to the same workspace through
the Dev Containers extension, but it is optional.

Details: `docs/dev-container.md`

## Manual Development

Backend:

```powershell
cd backend
uv run uvicorn app.main:app --reload --host 127.0.0.1 --port 8000
```

Frontend:

```powershell
cd frontend
$env:VITE_API_BASE_URL='http://127.0.0.1:8000'
npm run dev -- --host 127.0.0.1 --port 5173
```

## Checks

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

Inside Docker Compose:

```powershell
docker compose run --rm backend uv run pytest
docker compose run --rm frontend npm run check
```

## Data

Seed data lives in `data/seed/`:

- `routes.json`
- `places.json`
- `events.json`
- `connections.json`

Validation rules: `docs/seed-validation.md`

## Media Retrieval

The automated media workflow is a YouTube-only MVP. It creates draft
`media_links`; no audio or video files are stored in the repo.

Useful docs:

- `docs/media-retrieval/youtube-mvp-workflow.md`
- `docs/media-retrieval/workflow-commands.md`
- `docs/media-retrieval/codex-query-curation.md`

Dry run:

```powershell
cd backend
uv run python scripts/run_youtube_search_requests.py --dry-run
```

Live YouTube requests require `YOUTUBE_API_KEY` through `SOUNDATLAS_ENV_FILE`.
See `.env.example`.

## Project Structure

- `backend/`: FastAPI app, schemas, tests, and media retrieval scripts
- `frontend/`: SvelteKit app with map, timeline, route filter, and story panel
- `data/seed/`: curated MVP JSON data
- `data/enrichment/`: media retrieval plans and results
- `docs/`: product, data, route, infrastructure, and workflow docs
- `prompts/`: reusable project prompts for planning, implementation, review,
  and media retrieval
- `scripts/`: local helper scripts

## Rules

- Do not commit secrets, tokens, local paths, or private config.
- Do not store audio or video files in the repo.
- Keep sources and media as external links.
- Keep generated media links as `review_status: "draft"` until reviewed.
