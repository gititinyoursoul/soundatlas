# SoundAtlas

SoundAtlas is an MVP for an interactive music history app. It makes scenes
explorable across place, time, and cultural connection with a map-first UI,
timeline navigation, and a synchronized story panel.

The current product frame is **New York 1965-1985**. The first vertical slice
remains **Birth of Hip-Hop: Bronx 1970-1985**. Route availability is discovered
in the application's navigation; this README does not maintain a route
catalogue. For the status and replacement process of visual evidence, see the
[screenshot evidence policy](docs/design/screenshots/README.md).

Deployed page: [gititinyoursoul.github.io/soundatlas](https://gititinyoursoul.github.io/soundatlas/)

## Stack

- Frontend: SvelteKit, TypeScript, Leaflet
- Backend: FastAPI, Python 3.13, `uv`
- Data: curated JSON seed files under `data/seed/`

## Quick Start

Development targets are the host and Pane. Host commands are available below;
Pane integration still has the dependencies described in the
[development credential guide](docs/development-credentials.md).
Normal application startup and validation require no GitHub credentials.

### Local development

Use this path when Python, `uv`, Node.js, and npm are installed on the host.

For first-time setup, run the dependency installer from the repository root.

PowerShell:

```powershell
.\scripts\setup-dev.ps1
```

Bash:

```sh
./scripts/setup-dev.sh
```

Start both development servers:

PowerShell:

```powershell
.\scripts\start-dev.ps1
```

Bash:

```sh
./scripts/start-dev.sh
```

To start the same local stack in editorial review mode, set
`VITE_EDITORIAL_MODE=true` when launching the startup script.

PowerShell:

```powershell
$env:VITE_EDITORIAL_MODE = "true"
.\scripts\start-dev.ps1
```

Bash:

```sh
VITE_EDITORIAL_MODE=true ./scripts/start-dev.sh
```

Editorial mode requires the local FastAPI backend and API data path; it is not
available in the public static-data build. See the
[`editorial workflow`](docs/content/editorial-workflow.md) for the review and
publication process.

The default frontend URL is `http://127.0.0.1:5173`; the backend health check
is available at `http://127.0.0.1:8000/health`. See
[`docs/local-development.md`](docs/local-development.md) for checks and
troubleshooting.

### Pane

Pane owns agent repository authentication through its GitHub App. SoundAtlas
application credentials and the operator's Project Tracker PAT remain separate;
see the [credential guide](docs/development-credentials.md) for the individual-file
delivery contract and current integration limitations.

Container development uses the backend and frontend dev images in root Compose;
see [local development](docs/local-development.md).
The former workspace/devcontainer setup is retired. Pane integration is separate
from this SoundAtlas setup.

## Build and deployment

The public GitHub Pages deployment is a read-only static frontend. It loads
generated JSON assets from the curated seed files instead of calling the local
FastAPI backend. Build and deployment are handled by the Pages workflow.

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
external links for review. See the [enrichment documentation](docs/enrichment/workflow.md)
for their commands and provider requirements.

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
- Local development: `docs/local-development.md`
- Component-container workflow: `docs/local-development.md`
- GitHub Issue workflow: `docs/github-issue-workflow.md`
