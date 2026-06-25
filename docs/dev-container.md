# Dev Container And Workspace Setup

This document describes the current containerized development setup for
SoundAtlas. It is based on `.devcontainer/docker-compose.devcontainer.yml`,
the root `docker-compose.yml`, and the related Dockerfiles. The optional
`.devcontainer/devcontainer.json` file lets VS Code Dev Containers attach to
the same Compose workspace.

## Purpose

The dev container provides a reproducible workspace for editing, running, and
checking the MVP stack without installing all project tooling directly on the
host machine.

It is intentionally suitable for agent-assisted development: the agent runs
inside the `workspace` container and sees only the repository plus the explicit
mounts listed below. The `workspace` container does not require VS Code at
runtime; it is a long-running tools container that can be entered through plain
`docker compose exec` or, optionally, VS Code Dev Containers. Codex runs as a
CLI process inside that container. Codex credentials and config are seeded from
the host so the container CLI can reuse the host login without baking
credentials into an image. Codex runtime state and writable config stay in a
Docker volume so SQLite state files and `config.toml` updates are not written
through Windows bind mounts.

It starts three Compose services:

- `workspace`: interactive shell and Codex CLI workspace
- `backend`: FastAPI development server on port `8000`
- `frontend`: SvelteKit/Vite development server on port `5173`

The repository is mounted in the workspace container at `/workspace`.

## Entry Points

### Docker Compose CLI

The preferred agent workflow starts the workspace directly with Docker Compose:

```powershell
docker compose -f docker-compose.yml -f .devcontainer/docker-compose.devcontainer.yml up -d --build workspace
docker compose -f docker-compose.yml -f .devcontainer/docker-compose.devcontainer.yml exec --user soundatlas workspace sh .devcontainer/post-create.sh
docker compose -f docker-compose.yml -f .devcontainer/docker-compose.devcontainer.yml exec --user soundatlas workspace bash
```

The manual `post-create.sh` step is only needed for CLI-only startup. Use
`--user soundatlas` for manual `exec` commands so shell sessions match the
container user configured for the workspace.

### VS Code Dev Containers

VS Code is optional. To attach the editor to the same workspace container, open
the repository with the VS Code Dev Containers extension and run:

```text
Dev Containers: Reopen in Container
```

The dev container uses these Compose files, in order:

```sh
docker-compose.yml
.devcontainer/docker-compose.devcontainer.yml
```

When opened through VS Code, the selected service is:

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

VS Code Dev Containers runs the configured `postCreateCommand` automatically.

## Workspace Image

The `workspace` service is built from `.devcontainer/Dockerfile`.

Installed runtime tools:

- Python 3.13 through the `ghcr.io/astral-sh/uv:python3.13-bookworm-slim` base
  image
- `uv`
- Node.js `24.11.1`
- npm
- Codex CLI `@openai/codex` `0.142.2`
- Git
- Bash with programmable completion and Git prompt support
- basic shell/process tools: `bubblewrap`, `curl`, `less`, `procps`

The workspace image uses `/workspace` as its working directory and runs
`sleep infinity` by default so `docker compose exec` or VS Code can attach to
the already-running tools container.

## Services

### `workspace`

Defined in `.devcontainer/docker-compose.devcontainer.yml`.

Responsibilities:

- host an interactive shell and Codex CLI session
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

The `workspace` service also sets `seccomp=unconfined` so Codex's Linux
sandbox helper can create the user namespaces required by Bubblewrap inside
Docker Desktop/WSL2. Without that option, normal Codex tool calls and
`apply_patch` can fail before touching the workspace with a Bubblewrap
namespace error.

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
- read-only host bind mount: `%USERPROFILE%/.codex` to `/mnt/host-codex`

Because `CODEX_HOME` points at the `codex_home` volume, Codex can keep its
container-local SQLite state and writable `config.toml` on a Linux filesystem.
During post-create setup, host `auth.json` is copied into that volume and host
`config.toml` is copied only if the container does not already have one. The
post-create step then applies SoundAtlas dev-container defaults to the
container-local config: `/workspace` is trusted, Codex starts in
`workspace-write` with `on-request` approvals, cached web search is used, and
workspace shell commands can use network access. Network egress is still
bounded by the container firewall described below. The credentials are not
copied into the repository or Docker image. The workspace image installs the
Codex CLI, so terminal sessions inside the container use the seeded login cache
and configuration.
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
mkdir -p "$CODEX_HOME"
# copy /mnt/host-codex/auth.json into CODEX_HOME when present
# seed /mnt/host-codex/config.toml into CODEX_HOME only when missing
# apply container-local Codex defaults for /workspace
git config --global --replace-all safe.directory /workspace
git config --global credential.useHttpPath true
git config --global core.autocrlf true
git config --global core.filemode false
```

This seeds Codex auth/config into the writable Linux volume, makes the mounted
workspace safe for Git inside the container, and keeps Windows-oriented
line-ending and file-mode behavior predictable. Re-running the script updates
the container-local Codex defaults even when the `codex_home` volume already
existed from an older setup.

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
cd /workspace
codex --version
codex doctor
```

Start an interactive Codex session inside the workspace container:

```sh
cd /workspace
codex
```

Check service URLs from the host:

```text
Backend:  http://localhost:8000
Health:   http://localhost:8000/health
Frontend: http://localhost:5173
```

## Codex CLI Troubleshooting

If the dev container starts but Codex CLI does not work in the workspace
terminal:

1. In the workspace terminal, run `codex --version`.
2. Confirm `CODEX_HOME` is `/home/soundatlas/.codex`.
3. Confirm the copied login cache exists at `/home/soundatlas/.codex/auth.json`.
4. Confirm the writable config exists at `/home/soundatlas/.codex/config.toml`.
5. Confirm the config contains `[projects."/workspace"]` with
   `trust_level = "trusted"` and `[sandbox_workspace_write]` with
   `network_access = true`.
6. Run `codex doctor` and check the reported auth, config, runtime, and Git
   diagnostics.
7. Rebuild the dev container if `codex` is missing; the CLI is installed during
   the workspace image build.

`auth.json` is only the cached login state. It does not install or start Codex
by itself.
If `codex doctor` reports SQLite state errors under `/home/soundatlas/.codex`,
remove and recreate the `codex_home` Docker volume rather than bind-mounting
the whole host `%USERPROFILE%/.codex` directory.

If Codex asks whether `/workspace` is trusted and then fails with
`failed to persist config.toml`, rebuild the dev container so `config.toml` is
written inside the `codex_home` volume instead of being mounted as an
individual host file.

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
The only host credential mount is the read-only `%USERPROFILE%/.codex` seed
mount used by the workspace service.

Use `.env.codex.example` for dummy agent/test values. Keep any real
`.env.codex` file local and untracked. Do not add real tokens, SSH keys,
private dotfiles, or host-local paths to the repository, Docker images, or
checked-in environment files. The copied Codex `auth.json` gives the container
Codex login state, so treat the host and container copies of `auth.json` like a
password.

## Lifecycle Notes

When using Docker Compose directly, the lifecycle is controlled by normal
Compose commands such as `docker compose stop`, `docker compose down`, and
`docker compose up`. When using VS Code Dev Containers, VS Code attaches to the
same Compose service and manages the editor connection, but named volumes remain
available for later rebuilds unless they are explicitly removed with Docker
volume cleanup commands.
