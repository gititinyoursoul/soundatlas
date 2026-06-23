# Dev Container Setup

This document describes the current VS Code Dev Containers setup for SoundAtlas.
It is based on `.devcontainer/devcontainer.json`,
`.devcontainer/docker-compose.devcontainer.yml`, the root `docker-compose.yml`,
and the related Dockerfiles.

## Purpose

The dev container provides a reproducible workspace for editing, running, and
checking the MVP stack without installing all project tooling directly on the
host machine.

It is intentionally suitable for agent-assisted development: the agent runs
inside the `workspace` container, sees only the repository and named Docker
volumes, and does not receive host home-directory, SSH, cloud, or private
dotfile mounts.

It starts three Compose services:

- `workspace`: interactive VS Code/Codex workspace
- `backend`: FastAPI development server on port `8000`
- `frontend`: SvelteKit/Vite development server on port `5173`

The repository is mounted in the workspace container at `/workspace`.

## Entry Point

Open the repository with the VS Code Dev Containers extension and run:

```text
Dev Containers: Reopen in Container
```

The dev container uses these Compose files, in order:

```sh
docker-compose.yml
.devcontainer/docker-compose.devcontainer.yml
```

The selected VS Code service is:

```sh
workspace
```

The container user is:

```sh
soundatlas
```

## Workspace Image

The `workspace` service is built from `.devcontainer/Dockerfile`.

Installed runtime tools:

- Python 3.13 through the `ghcr.io/astral-sh/uv:python3.13-bookworm-slim` base
  image
- `uv`
- Node.js `24.11.1`
- npm
- Git
- basic shell/process tools: `curl`, `less`, `procps`

The workspace image uses `/workspace` as its working directory and runs
`sleep infinity` by default so VS Code can attach to it.

## Services

### `workspace`

Defined in `.devcontainer/docker-compose.devcontainer.yml`.

Responsibilities:

- host the interactive editor and Codex session
- provide Python, `uv`, Node.js, npm, and Git in one container
- mount the full repository at `/workspace`
- share dependency/cache volumes with the project workflow

Important environment variables:

```sh
CODEX_HOME=/home/soundatlas/.codex
UV_PROJECT_ENVIRONMENT=/home/soundatlas/.cache/uv/venvs/backend
SOUNDATLAS_EGRESS_GUARD=enabled
SOUNDATLAS_ALLOWED_INBOUND_PORTS=
SOUNDATLAS_ALLOWED_OUTBOUND_PORTS=8000 5173
SOUNDATLAS_WRITABLE_PATHS=/workspace/frontend/node_modules /home/soundatlas/.cache/uv /home/soundatlas/.npm /home/soundatlas/.codex
```

The workspace waits for the `backend` and `frontend` services to start.

### `backend`

Defined in the root `docker-compose.yml` and extended by the dev container
Compose override.

Responsibilities:

- run the FastAPI app with reload enabled
- expose the API at `http://localhost:8000`
- expose the health endpoint at `http://localhost:8000/health`
- read curated seed data from `/workspace/data`

Default command from `backend/Dockerfile`:

```sh
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

The backend uses the root Compose egress guard settings in the dev container.

### `frontend`

Defined in the root `docker-compose.yml`.

Responsibilities:

- run the SvelteKit/Vite development server
- expose the frontend at `http://localhost:5173`
- call the backend through `VITE_API_BASE_URL=http://localhost:8000`

Default command from `frontend/Dockerfile`:

```sh
sh -c "if [ ! -x node_modules/.bin/vite ]; then npm ci; fi; npm run dev -- --host 0.0.0.0 --port 5173"
```

The frontend depends on the backend healthcheck before starting.

## Mounts And Volumes

The dev container setup intentionally avoids mounting host home directories,
SSH keys, private dotfiles, or cloud configuration directories.

The `workspace` service uses these mounts:

- repository bind mount: `.` to `/workspace`
- named volume: `workspace_codex_home` to `/home/soundatlas/.codex`
- named volume: `workspace_frontend_node_modules` to
  `/workspace/frontend/node_modules`
- named volume: `workspace_uv_cache` to `/home/soundatlas/.cache/uv`
- named volume: `workspace_npm_cache` to `/home/soundatlas/.npm`

Because `CODEX_HOME` points at a named Docker volume, Codex state persists
across container rebuilds but is not copied into the repository or image.

The app services use repo-local bind mounts and named dependency/cache volumes:

- `backend` mounts `backend`, `frontend`, `data`, `docs`, `scripts`,
  `README.md`, `TODO.md`, and `.env.example`
- `frontend` mounts `frontend`
- backend `uv` cache and frontend `node_modules`/npm cache are stored in named
  Docker volumes

## Post-Create Setup

After the container is created, `.devcontainer/post-create.sh` configures Git:

```sh
git config --global --replace-all safe.directory /workspace
git config --global credential.useHttpPath true
git config --global core.autocrlf true
git config --global core.filemode false
```

This makes the mounted workspace safe for Git inside the container and keeps
Windows-oriented line-ending and file-mode behavior predictable.

## VS Code Extensions

The dev container requests these VS Code extensions:

- Python and Pylance
- Docker
- Git Graph
- ChatGPT
- Svelte
- TOML, YAML, REST Client, and Markdown helpers

The extension list is defined in `.devcontainer/devcontainer.json`.

## Common Commands

Run backend tests from the workspace container:

```sh
cd /workspace/backend
uv run pytest
```

Run frontend checks from the workspace container:

```sh
cd /workspace/frontend
npm run check
```

Install frontend dependencies if needed:

```sh
cd /workspace/frontend
npm ci
```

Check service URLs from the host:

```text
Backend:  http://localhost:8000
Health:   http://localhost:8000/health
Frontend: http://localhost:5173
```

## Security Boundaries

All project containers run as the non-root `soundatlas` user after startup.
The root phase is used only by `docker/egress-guard.sh` to prepare writable
paths and, when enabled, apply `iptables` restrictions before dropping
privileges with `gosu`.

The egress guard:

- allows loopback and established connections
- allows Docker DNS
- allows responses from explicitly configured inbound service ports
- rejects common private/internal IPv4 ranges and metadata-style link-local
  ranges
- allows outbound TCP `443`
- applies similar restrictions for IPv6 when `ip6tables` is available

Current dev container behavior:

- `workspace`: egress guard enabled
- `backend`: egress guard enabled
- `frontend`: egress guard enabled from the root Compose file

This is a pragmatic agent-coding boundary, not a full sandbox. The agent can
edit the repository and use public HTTPS for package installation, Git remotes,
documentation lookup, and model/API access. The workspace may also call the
local dev service ports `8000` and `5173` for backend/frontend checks. It
should not receive direct mounts to host secrets or broader host directories.

Use `.env.codex.example` for dummy agent/test values. Keep any real
`.env.codex` file local and untracked. Do not add real tokens, SSH keys,
private dotfiles, or host-local paths to the repository, Docker images, or
checked-in environment files.

## Lifecycle Notes

VS Code controls the Compose lifecycle for the dev container. The configured
shutdown action is:

```sh
stopCompose
```

Stopping or closing the dev container stops the Compose services, but named
volumes remain available for later rebuilds unless they are explicitly removed
with Docker volume cleanup commands.
