# Dev Container And Workspace Setup

This document describes SoundAtlas' normal containerized development setup. It
uses the root `docker-compose.yml` and `.devcontainer/docker-compose.devcontainer.yml`.
VS Code integration is optional; `.devcontainer/devcontainer.json` attaches VS
Code to the same workspace service.

## Purpose

The dev container provides a reproducible workspace for editing, running, and
checking the MVP stack without installing all project tooling on the host.

The default stack starts three services:

- `workspace`: interactive shell and Codex CLI workspace
- `backend`: FastAPI development server on port `8000`
- `frontend`: SvelteKit/Vite development server on port `5173`

The repository is mounted at `/workspace`. The workspace is a normal
SoundAtlas development environment; it has no dependency on a separate private
runtime or repository.

## Prerequisites

Install Docker with the Docker Compose plugin. The Compose override expects
these local, read-only files outside the repository:

```sh
mkdir -p ../secrets/soundatlas
$EDITOR ../secrets/soundatlas/.env
$EDITOR ../secrets/soundatlas/github-agent.env
$EDITOR ../secrets/soundatlas/github-project-agent.env
```

The app env file contains settings such as `YOUTUBE_API_KEY`. Each GitHub file
contains exactly one unquoted, non-empty `GH_TOKEN=<token>` assignment. Do not
commit any of these files.

Importing host Codex state is optional. When present, the host `.codex`
directory is mounted read-only at `/mnt/host-codex`; post-create setup seeds
the supported login and configuration files into the workspace-only
`codex_home` volume.

## Start the workspace

```powershell
docker compose -f docker-compose.yml -f .devcontainer/docker-compose.devcontainer.yml up -d --build workspace
docker compose -f docker-compose.yml -f .devcontainer/docker-compose.devcontainer.yml exec --user soundatlas workspace sh .devcontainer/post-create.sh
docker compose -f docker-compose.yml -f .devcontainer/docker-compose.devcontainer.yml exec --user soundatlas workspace bash
```

The manual `post-create.sh` step is needed only for CLI-only startup. VS Code
Dev Containers runs its configured post-create command automatically. To use
VS Code, open the repository and select **Dev Containers: Reopen in
Container**.

## Workspace image and services

The `workspace` service is built from the `workspace` target in
`.devcontainer/Dockerfile`. It includes Python 3.13 and `uv`, Node.js and npm,
Git, GitHub CLI, Codex CLI, Bash, and the libraries required by
Playwright-managed Chromium.

`workspace` mounts the repository, package/cache volumes, the optional
read-only host Codex state, and the three read-only secret files. It depends on
the backend and frontend services starting. `seccomp=unconfined` is retained
for Codex's Bubblewrap sandbox under Docker Desktop/WSL2.

The backend serves `http://localhost:8000` and its health endpoint at
`http://localhost:8000/health`. The frontend serves
`http://localhost:5173` and waits for the backend healthcheck.

## Post-create setup

`.devcontainer/post-create.sh` configures the container-local Git and Codex
state, then installs backend and frontend dependencies from their lockfiles.
It uses `/workspace` as Git's safe directory and only writes a Git author when
both `SOUNDATLAS_GIT_AUTHOR_NAME` and `SOUNDATLAS_GIT_AUTHOR_EMAIL` are set.

## Validation

Run the baseline validation from the workspace root:

```sh
cd /workspace
bash scripts/validate-dev.sh
```

Run focused checks when appropriate:

```sh
cd /workspace/backend
uv run ruff check .
uv run pyright
uv run pytest

cd /workspace/frontend
npm run validate
npm run validate:release
npm run validate:pages
```

`npm run validate:pages` uses the same static-data mode and `/soundatlas` base
path as Frontend CI.

## Browser checks

Browser screenshot checks are optional and are not part of the baseline path.
Install Chromium into the workspace cache when needed:

```sh
cd /workspace/frontend
npx playwright install chromium
VITE_API_BASE_URL=http://backend:8000 npm run dev -- --host 127.0.0.1 --port 5173 --strictPort
```

Capture screenshots from the checkout under review into its ignored
`screenshots/` directory. Copy only Human-approved evidence into
`docs/design/screenshots/`.

## Security boundaries

The workspace runs as the non-root `soundatlas` user after startup. The normal
egress guard prepares writable paths and applies the configured outbound policy
before dropping privileges. Secrets remain external, read-only inputs and are
not copied into the repository or image.

Do not use `docker compose down -v` as routine cleanup: it deletes normal
dependency and tool-cache volumes. Stop or recreate only the services needed
for the change being tested.