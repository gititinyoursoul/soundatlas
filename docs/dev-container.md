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
inside the `workspace` container and sees only the repository plus the explicit
mounts listed below. Codex credentials and config are mounted from the host so
the VS Code/Codex extension can reuse the host login without baking credentials
into an image. Codex runtime state stays in a Docker volume so SQLite state
files are not written through the Windows bind mount.

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

Interactive terminals use Bash by default. The image installs
`bash-completion` and a small `.bashrc` that enables tab completion plus Git
branch/status information in the prompt.

## Workspace Image

The `workspace` service is built from `.devcontainer/Dockerfile`.

Installed runtime tools:

- Python 3.13 through the `ghcr.io/astral-sh/uv:python3.13-bookworm-slim` base
  image
- `uv`
- Node.js `24.11.1`
- npm
- Codex CLI `@openai/codex` `0.142.0`
- Git
- Bash with programmable completion and Git prompt support
- basic shell/process tools: `bubblewrap`, `curl`, `less`, `procps`

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
- named volume: `frontend_node_modules` to `/workspace/frontend/node_modules`
- named volume: `backend_uv_cache` to `/home/soundatlas/.cache/uv`
- named volume: `frontend_npm_cache` to `/home/soundatlas/.npm`
- named volume: `codex_home` to `/home/soundatlas/.codex`
- host bind mount: `%USERPROFILE%/.codex/auth.json` to
  `/home/soundatlas/.codex/auth.json`
- host bind mount: `%USERPROFILE%/.codex/config.toml` to
  `/home/soundatlas/.codex/config.toml`

Because `CODEX_HOME` points at the `codex_home` volume, Codex can keep its
container-local SQLite state on a Linux filesystem. The host `auth.json` and
`config.toml` are mounted into that directory after the user signs in on the
host. The credentials are not copied into the repository or Docker image.
The workspace image also installs the Codex CLI, so the VS Code Codex
extension and terminal sessions can use the same mounted login cache and
configuration.
The workspace intentionally shares dependency/cache volumes with the app
services so agent-run checks and running services see the same installed
frontend packages and uv cache.

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

Check Codex inside the workspace container:

```sh
codex --version
codex doctor
```

Check service URLs from the host:

```text
Backend:  http://localhost:8000
Health:   http://localhost:8000/health
Frontend: http://localhost:5173
```

## Codex Startup Troubleshooting

If the dev container starts but Codex does not appear in VS Code:

1. Open the Command Palette and run `Codex: Open Sidebar`.
2. In the workspace terminal, run `codex --version`.
3. Confirm the mounted login cache exists at `/home/soundatlas/.codex/auth.json`.
4. Run `codex doctor` and check the reported auth, config, runtime, and Git
   diagnostics.
5. Rebuild the dev container if `codex` is missing; the CLI is installed during
   the workspace image build.

`auth.json` is only the cached login state. It does not install or start Codex
by itself.
If `codex doctor` reports SQLite state errors under `/home/soundatlas/.codex`,
remove and recreate the `codex_home` Docker volume rather than bind-mounting
the whole host `%USERPROFILE%/.codex` directory.

## Security Boundaries

All project containers run as the non-root `soundatlas` user after startup.
The root phase is used only by `docker/egress-guard.sh` to prepare writable
paths and, when enabled, apply `iptables` restrictions before dropping
privileges with `gosu`.

The egress guard:

- allows loopback and established connections
- allows Docker DNS and configured DNS resolvers on port `53`
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
checked-in environment files. The host `%USERPROFILE%/.codex/auth.json` bind
mount is a runtime-only convenience for trusted local development; treat
`%USERPROFILE%/.codex/auth.json` like a password.

## Lifecycle Notes

VS Code controls the Compose lifecycle for the dev container. The configured
shutdown action is:

```sh
stopCompose
```

Stopping or closing the dev container stops the Compose services, but named
volumes remain available for later rebuilds unless they are explicitly removed
with Docker volume cleanup commands.
