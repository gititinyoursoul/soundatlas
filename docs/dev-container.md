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
through Windows bind mounts. App/provider secrets are mounted as a single
read-only env file when present; GitHub agent credentials are kept separate
from app env files.

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
- Codex CLI `@openai/codex` `0.142.4`
- GitHub CLI `gh`
- Git
- Bash with programmable completion and Git prompt support
- basic shell/process tools: `bubblewrap`, `curl`, `less`, `procps`
- shared libraries needed to launch Playwright-managed Chromium for headless
  screenshots and browser checks

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
GH_CONFIG_DIR=/home/soundatlas/.config/gh
SOUNDATLAS_ENV_FILE=/run/secrets/soundatlas.env
SOUNDATLAS_GITHUB_AGENT_ENV_FILE=/run/secrets/github-agent.env
SOUNDATLAS_GIT_AUTHOR_NAME=
SOUNDATLAS_GIT_AUTHOR_EMAIL=
UV_PROJECT_ENVIRONMENT=/home/soundatlas/.cache/uv/venvs/backend
SOUNDATLAS_EGRESS_GUARD=enabled
SOUNDATLAS_ALLOWED_OUTBOUND_PORTS=8000 5173
SOUNDATLAS_WRITABLE_PATHS=/workspace/frontend/node_modules /home/soundatlas/.cache/ms-playwright /home/soundatlas/.cache/uv /home/soundatlas/.config/gh /home/soundatlas/.npm /home/soundatlas/.codex
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
- named volume: `playwright_cache` to `/home/soundatlas/.cache/ms-playwright`
- named volume: `backend_uv_cache` to `/home/soundatlas/.cache/uv`
- named volume: `frontend_npm_cache` to `/home/soundatlas/.npm`
- named volume: `codex_home` to `/home/soundatlas/.codex`
- named volume: `github_cli_config` to `/home/soundatlas/.config/gh`
- read-only host bind mount: `%USERPROFILE%/.codex` to `/mnt/host-codex`
- read-only host bind mount: `../secrets/soundatlas/.env` to
  `/run/secrets/soundatlas.env`
- read-only host bind mount: `../secrets/soundatlas/github-agent.env` to
  `/run/secrets/github-agent.env`

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

### App Secrets And Agent Tokens

The workspace dev container uses a narrow read-only mount for app/provider
secrets:

```text
host:      ../secrets/soundatlas/.env
container: /run/secrets/soundatlas.env
env var:   SOUNDATLAS_ENV_FILE=/run/secrets/soundatlas.env
```

This file is intended for SoundAtlas runtime and enrichment settings such as
`YOUTUBE_API_KEY`. The container receives the path through
`SOUNDATLAS_ENV_FILE`; the raw token values are not written into Compose
environment variables. Do not mount the whole `../secrets/soundatlas`
directory unless a specific task requires broader access.

GitHub agent credentials are separate from app/provider secrets. Use a
fine-grained GitHub token scoped to this repository only, and store it outside
the repo, for example:

```text
../secrets/soundatlas/github-agent.env
```

For issue management, the GitHub CLI can use `GH_TOKEN` from that file when it
is loaded into the shell. Interactive Bash shells in the workspace load
`SOUNDATLAS_GITHUB_AGENT_ENV_FILE` automatically when `GH_TOKEN` is not already
set, so `gh` can authenticate without `gh auth login` and without writing
GitHub credentials into the `github_cli_config` volume. For persistent
interactive `gh auth login` inside the container, GitHub CLI config is stored
in the `github_cli_config` Docker volume at `/home/soundatlas/.config/gh`. Do
not mount the host GitHub CLI config into the container.

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
# set git user.name and user.email when SOUNDATLAS_GIT_AUTHOR_* are present
cd /workspace/backend && uv sync --locked --dev
cd /workspace/frontend && npm ci
```

This seeds Codex auth/config into the writable Linux volume, makes the mounted
workspace safe for Git inside the container, and keeps Windows-oriented
line-ending and file-mode behavior predictable. Re-running the script updates
the container-local Codex defaults even when the `codex_home` volume already
existed from an older setup.

The script also syncs backend and frontend dependencies from lockfiles so a
fresh workspace has the Python and Node dependencies available without a
separate manual install step.

Git author configuration is intentionally opt-in. If both
`SOUNDATLAS_GIT_AUTHOR_NAME` and `SOUNDATLAS_GIT_AUTHOR_EMAIL` are provided to
the `workspace` service, `post-create.sh` writes them to the container user's
global Git config. If either value is empty, the script leaves `user.name` and
`user.email` untouched. This avoids mounting or copying the host `~/.gitconfig`
while still allowing repeatable commits inside the dev container.

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

Check GitHub CLI inside the workspace container:

```sh
cd /workspace
gh --version
gh auth status
gh issue list
```

## Browser Screenshot Checks

The workspace image includes the OS libraries required by Playwright-managed
Chromium. The browser binary itself is intentionally kept out of the image and
is downloaded into the `playwright_cache` Docker volume when needed.

After changing the browser runtime setup, rebuild the workspace image:

```powershell
docker compose -f docker-compose.yml -f .devcontainer/docker-compose.devcontainer.yml up -d --build workspace
```

From inside the workspace container, install Chromium into the cache volume and
start a workspace-local frontend server that points browser requests at the
Compose backend service:

```sh
cd /workspace/frontend
npx playwright install chromium
VITE_API_BASE_URL=http://backend:8000 npm run dev -- --host 127.0.0.1 --port 5173 --strictPort
```

In another workspace shell, capture a desktop screenshot:

```sh
cd /workspace/frontend
npx playwright screenshot --browser chromium --viewport-size=1440,1000 --wait-for-selector main.app-shell --wait-for-timeout 3000 http://127.0.0.1:5173 ../screenshots/desktop.png
```

Capture a mobile-sized screenshot with:

```sh
cd /workspace/frontend
npx playwright screenshot --browser chromium --viewport-size=390,844 --wait-for-selector main.app-shell --wait-for-timeout 3000 http://127.0.0.1:5173 ../screenshots/mobile.png
```

Generated screenshots belong in `/workspace/screenshots/`, which is ignored by
Git. Use them for local UX critique, then copy the approved files into
`docs/design/screenshots/` and remove any stale files from that tracked folder.
Use stable filenames so refreshed captures replace the previous version cleanly.
For the drawer states, run `cd /workspace/frontend && npm run capture:drawer`.
The `--strictPort` flag is intentional: if a previous dev server is still
running, Vite should fail loudly instead of moving to a different port while
Playwright captures the wrong page.

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
