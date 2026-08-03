# SoundAtlas

![SoundAtlas screenshot](docs/design/screenshots/drawer-closed-desktop.png)

SoundAtlas is an MVP for an interactive music history app. It makes scenes
explorable across place, time, and cultural connection with a map-first UI,
timeline navigation, and a synchronized story panel.

The current product frame is **New York 1965-1985**. The seed data currently
covers five curated routes:

- `Birth of Hip-Hop`
- `Disco To Dance Music`
- `Punk & New Wave Downtown`
- `Salsa & Latin New York`
- `Downtown Experiment / No Wave / Loft Jazz`

The first vertical slice remains **Birth of Hip-Hop: Bronx 1970-1985**.

Deployed page: [gititinyoursoul.github.io/soundatlas](https://gititinyoursoul.github.io/soundatlas/)

## Stack

- Frontend: SvelteKit, TypeScript, Leaflet
- Backend: FastAPI, Python 3.13, `uv`
- Data: curated JSON seed files under `data/seed/`

## Quick Start

Requirements:

- Python `>=3.13`
- `uv`
- Node.js and npm
- PowerShell for `scripts/start-dev.ps1`, or Bash for `scripts/start-dev.sh`

### Local

PowerShell:

```powershell
.\scripts\start-dev.ps1
```

Bash:

```sh
./scripts/start-dev.sh
```

Default URLs:

- Frontend: `http://127.0.0.1:5173`
- Backend: `http://127.0.0.1:8000`
- Health: `http://127.0.0.1:8000/health`

### Docker Compose

```sh
docker compose up --build
```

This starts the app stack only:

- `backend`
- `frontend`

It does not start the dev-container `workspace` service.

Default URLs:

- Frontend: `http://localhost:5173`
- Backend: `http://localhost:8000`
- Health: `http://localhost:8000/health`

Stop the stack:

```sh
docker compose down
```

### Workspace Dev Container

To start the long-running `workspace` container used by VS Code Dev Containers
or Codex CLI, include the dev-container Compose overlay:

```sh
docker compose -f docker-compose.yml -f .devcontainer/docker-compose.devcontainer.yml up -d --build workspace
docker compose -f docker-compose.yml -f .devcontainer/docker-compose.devcontainer.yml exec --user soundatlas workspace sh .devcontainer/post-create.sh
docker compose -f docker-compose.yml -f .devcontainer/docker-compose.devcontainer.yml exec --user soundatlas workspace bash
```

To start the same workspace through VS Code:

1. Open the repository folder in VS Code.
2. Install the Dev Containers extension if it is not already installed.
3. Run `Dev Containers: Reopen in Container` from the Command Palette.

VS Code uses `.devcontainer/devcontainer.json` and starts the `workspace`
service with the root `docker-compose.yml` plus
`.devcontainer/docker-compose.devcontainer.yml`.

The dev container config also owns container-specific VS Code settings such as
the Linux backend Python interpreter path. Local Windows VS Code users should
select their own backend interpreter locally after running the `uv` workflow;
`.vscode/` remains ignored so machine-specific editor paths are not committed.

The workspace also seeds Codex login state from the host `.codex` directory by
default. If your host uses a different path, set
`SOUNDATLAS_HOST_CODEX_HOME` before starting the container.

### Manual Development

Backend:

```sh
cd backend
uv run uvicorn app.main:app --reload --host 127.0.0.1 --port 8000
```

Frontend:

```sh
cd frontend
VITE_API_BASE_URL=http://127.0.0.1:8000 npm run dev -- --host 127.0.0.1 --port 5173
```

### Public Static Mode

The public GitHub Pages deployment is a read-only static frontend. It loads
generated JSON assets from the curated seed files instead of calling the local
FastAPI backend.

```sh
cd frontend
VITE_DATA_MODE=static VITE_BASE_PATH=/soundatlas npm run build
```

Local/editorial mode remains API-backed:

```sh
cd frontend
VITE_DATA_MODE=api VITE_API_BASE_URL=http://127.0.0.1:8000 npm run dev
```

`npm run build` regenerates `frontend/static/soundatlas-data/` from
`data/seed/`. The generated static data is build input and should not replace
the seed files as the editorial source of truth.

### Release Organization

Deployment work is grouped in the GitHub milestone
`v0.1 Public Static MVP`. Issues in that milestone track the public static
frontend, generated seed-data assets, Pages deployment workflow, and docs.

Use GitHub Milestones for release planning and GitHub Releases only after a
validated deployment is tagged, for example `v0.1.0`.

## Checks

Backend:

```sh
cd backend
uv run ruff check .
uv run pyright
uv run pytest
```

Frontend:

```sh
cd frontend
npm run lint
npm run check
npm run test
```

Optional coverage reports:

```sh
cd backend
uv run pytest --cov

cd ../frontend
npm run test:coverage
```

## Architecture and data

The system architecture, component boundaries, API overview, and runtime data
flow are documented in [`docs/architecture/`](docs/architecture/README.md).
Seed files remain under `data/seed/`; their contracts and validation rules live
in [`docs/data/`](docs/data/seed-data-structure.md).

The current seed authoring workflow is prompt-guided curation, followed by JSON
validation and backend schema loading. See the [editorial workflow](docs/content/editorial-workflow.md)
and [enrichment documentation](docs/enrichment/workflow.md) for those domain
workflows.

## Enrichment

The repository includes media and image enrichment workflows that generate draft
external links for review. No audio, video, or image assets are stored in the
repository.

Useful docs:

- `docs/enrichment/media/overview.md`
- `docs/enrichment/media/youtube-mvp-workflow.md`
- `docs/enrichment/media/workflow-commands.md`
- `docs/enrichment/image/overview.md`
- `docs/enrichment/image/workflow-commands.md`
- `docs/enrichment/upstream/event-search-components.md`

Example dry run:

```sh
cd backend
uv run python scripts/run_youtube_search_requests.py --dry-run
```

Real provider credentials should stay outside the repo. See `.env.example` for
the expected environment variables.

## Project Structure

The [system overview](docs/architecture/system-overview.md) documents the
repository components and their boundaries. The top-level areas are:

- `backend/`: FastAPI application and backend tooling
- `frontend/`: SvelteKit application
- `data/`: curated seed data and enrichment artifacts
- `docs/`: product, architecture, design, data, and workflow documentation
- `prompts/`: reusable project prompts
- `scripts/`: local developer startup helpers

## Documentation

- MVP concept: `docs/mvp-concept.md`
- Architecture: `docs/architecture/README.md`
- Planned agent work: GitHub Issues
- Legacy backlog: `TODO.md`
- Completed work archive: `docs/done.md`
- Dev container workflow: `docs/dev-container.md`
- Implementation plan workflow: `docs/implementation-plan-workflow.md`

## Working Rules

- Keep changes small and aligned with the MVP scope.
- Prefer curated, traceable data over automated aggregation.
- Always include source fields in the data model.
- Do not commit secrets, tokens, or local machine paths.
- Do not add audio files to the repository; use external media links only.
