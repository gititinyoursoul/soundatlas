# Dev Container And Workspace Setup

This document describes the current containerized development setup for
SoundAtlas. It is based on `.devcontainer/docker-compose.devcontainer.yml`,
the root `docker-compose.yml`, and the related Dockerfiles. VS Code
integration is optional; `.devcontainer/devcontainer.json` configures VS Code
Dev Containers to attach to the same Compose workspace.

## Purpose

The dev container provides a reproducible workspace for editing, running, and
checking the MVP stack without installing all project tooling directly on the
host machine.

It is intentionally suitable for agent-assisted development: the agent runs
inside the `workspace` container and sees only the repository plus the explicit
mounts listed below. The `workspace` container does not require VS Code at
runtime; it is a long-running tools container that can be entered through plain
`docker compose exec` or, optionally, VS Code Dev Containers. Codex runs as a
CLI process inside that container. Codex runtime state and writable config stay
in a Docker volume so SQLite state files and `config.toml` updates are not
written through host bind mounts. App/provider secrets are mounted as a single
read-only env file; GitHub agent credentials are kept separate from app env
files.

The default stack starts three Compose services:

- `workspace`: interactive shell and Codex CLI workspace
- `backend`: FastAPI development server on port `8000`
- `frontend`: SvelteKit/Vite development server on port `5173`

The repository is mounted in the workspace container at `/workspace`.
During the workspace-to-Pane migration, the explicit `pane` Compose profile
adds `pane-workspace` and its network companion, `pane-egress`. Pane uses the same backend and
frontend containers but owns its repository clones and Pane worktrees in Docker
volumes. It does not mount the host checkout.

## Prerequisites

Install Docker with the Docker Compose plugin before starting the stack. The
Compose override mounts two local secret files read-only, so both files must
exist and contain the required values before Compose startup:

```sh
mkdir -p ../secrets/soundatlas
$EDITOR ../secrets/soundatlas/.env
$EDITOR ../secrets/soundatlas/github-agent.env
```

The first file contains SoundAtlas app/provider settings such as
`YOUTUBE_API_KEY`; the second contains the repository-scoped GitHub agent
credential used by `gh`. Empty placeholder files are not a supported startup
configuration. Keep both files outside the repository and never commit their
contents.

Importing host Codex state is optional. When used, the host `.codex` directory
is mounted read-only at `/mnt/host-codex` only in the `workspace` service, and
post-create setup copies the supported login/config files into the
workspace-only `codex_home` volume.

The Pane profile requires an SSH public key for its host-loopback tunnel. Keep
the private key outside the repository and place only its public half at the
default seed path:

```powershell
ssh-keygen -t ed25519 -f ..\secrets\soundatlas\pane_ed25519
Copy-Item ..\secrets\soundatlas\pane_ed25519.pub ..\secrets\soundatlas\pane_authorized_keys
```

`pane-workspace` also reads the individual host Codex `auth.json` and
`config.toml` files and the existing `github-agent.env` file. Its entrypoint
copies those seeds into runtime-owned volumes; the image contains no
credential. Override the input paths with
`SOUNDATLAS_HOST_CODEX_AUTH_FILE`, `SOUNDATLAS_HOST_CODEX_CONFIG_FILE`, or
`SOUNDATLAS_PANE_AUTHORIZED_KEYS_FILE` when the defaults do not apply. A
nonstandard GitHub seed path can be supplied through
`SOUNDATLAS_GITHUB_AGENT_ENV_SEED_FILE`.

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

### Pane workspace migration profile

Build both retained development targets without changing the current default
Dev Container service:

```powershell
docker compose -f docker-compose.yml -f .devcontainer/docker-compose.devcontainer.yml --profile pane build workspace pane-workspace pane-egress
```

Start the one application stack and both workspace clients in parallel:

```powershell
docker compose -f docker-compose.yml -f .devcontainer/docker-compose.devcontainer.yml --profile pane up -d backend frontend workspace pane-workspace
```

The resulting local image tags are `soundatlas-workspace:local` and the
versioned `soundatlas-pane-workspace:2.4.95`. Set
`SOUNDATLAS_PANE_IMAGE_TAG` only when deliberately assigning another retained
local tag. Only backend and frontend publish application ports. Pane publishes
SSH through `pane-egress` at `127.0.0.1:53660` by default; set `SOUNDATLAS_PANE_SSH_PORT` before `up`
to choose another host-loopback port.

On first startup, the Pane entrypoint generates a runtime-owned SSH host key,
copies the scoped credential seeds, creates a pairing token, and starts Pane
headlessly with its Electron sandbox enabled. Retrieve the protected pairing
record explicitly, start the tunnel, and paste the `pane-remote://` line into
Pane's **Settings > Remote Pane** screen:

```powershell
docker compose -f docker-compose.yml -f .devcontainer/docker-compose.devcontainer.yml --profile pane exec pane-workspace sed -n '/^pane-remote:/p' /runtime/pane/remote-setup.txt
ssh -N -o IdentitiesOnly=yes -i ..\secrets\soundatlas\pane_ed25519 -p 53660 -L 42137:127.0.0.1:42137 soundatlas@127.0.0.1
```

The pairing URI is a bearer credential. Do not paste it into Issues, logs, or
tracked files. Regenerate the `pane_state` volume if the credential is exposed.

Pane owns the base clone and every Pane-managed worktree. Initialize the saved
repository once through the SSH shell; do not register the host checkout:

```sh
git clone https://github.com/gititinyoursoul/soundatlas.git /runtime/repos/soundatlas
cd /runtime/repos/soundatlas
sh .devcontainer/post-create.sh
runpane repos add --path /runtime/repos/soundatlas --name soundatlas --yes --json
runpane agents doctor --agent codex --repo soundatlas --json
```

With Pane/RunPane 2.4.95, `runpane panes create` can return
`input.items.0: did not match any allowed shape` after it has already created
the Pane, managed worktree, and initialized Codex panel. Check
`runpane panes list --repo soundatlas --json` and `runpane panels list` before
retrying. In the Issue #195 validation, the created Codex panel completed its
bounded read-only command after the one-time repository trust prompt; the
wrapper error did not represent daemon, worktree, or agent startup failure.

The derived repository root in `post-create.sh` lets the same bootstrap work at
`/workspace`, in the Pane-owned base clone, or in a Pane worktree. Git commits
and remotes are the transfer boundary between the host-mounted workspace and
Pane; they never share a writable checkout.

Use these equivalent smoke checks from each client shell. In the existing
workspace, the root is `/workspace`; in Pane, run them from the applicable
runtime-owned clone or worktree:

```sh
curl -fsS http://backend:8000/health
curl -fsS -H 'Host: localhost:5173' -o /dev/null -w '%{http_code}\n' http://frontend:5173
cd backend && uv run pytest
cd ../frontend && npm run validate
```

Vite rejects the Compose service name in the HTTP `Host` header, so the
frontend smoke check supplies the same allowed `localhost:5173` host used by a
developer browser. This does not change network routing: the request still
travels to the shared `frontend` service.

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

The dev container also provisions a focused set of VS Code extensions for the
project stack and applies container-only editor settings under
`.devcontainer/devcontainer.json`. Those settings include the Linux backend
Python interpreter path created by `UV_PROJECT_ENVIRONMENT`.

Local Windows VS Code workspaces should not reuse that Linux interpreter path.
Run the backend `uv` workflow locally and select the resulting interpreter in
VS Code user or workspace-local settings. The repo keeps `.vscode/` ignored so
host-specific interpreter paths stay out of source control.

## Workspace Image

The `workspace` service is built from `.devcontainer/Dockerfile`.

Installed runtime tools:

- Python 3.13 through the `ghcr.io/astral-sh/uv:python3.13-bookworm-slim` base
  image
- `uv`
- Node.js (version pinned in `.devcontainer/Dockerfile`)
- npm
- Codex CLI `@openai/codex` (version pinned in `.devcontainer/Dockerfile`)
- GitHub CLI `gh`
- Git
- Bash with programmable completion and Git prompt support
- basic shell/process tools: `bubblewrap`, `curl`, `less`, `procps`
- shared libraries needed to launch Playwright-managed Chromium for headless
  screenshots and browser checks

The workspace image uses `/workspace` as its working directory and runs
`sleep infinity` by default so `docker compose exec` or VS Code can attach to
the already-running tools container.

The Dockerfile's shared `soundatlas-tooling` stage supplies the same pinned
Python, uv, Node.js, npm, GitHub CLI, Git, shell tools, and browser libraries to
both final targets. `workspace` retains Codex CLI 0.147.0. The
`pane-workspace` target pins Codex CLI 0.153.4 for compatibility with Pane's
current built-in model selection, and adds checksum-verified Pane 2.4.95,
matching RunPane 2.4.95, plus the non-root SSH daemon.
The Pane Debian artifact SHA-256 is
`4de2274ecd9617e642bb06b430c210da28052151d090aa0ade94f19368482265`.
`workspace` retains its existing `/workspace` working directory and egress-
guard entrypoint; `pane-workspace` uses `/runtime/repos` and its dedicated
non-root Pane entrypoint.

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
SOUNDATLAS_ALLOWED_OUTBOUND_DESTINATIONS=backend:8000 frontend:5173
SOUNDATLAS_WRITABLE_PATHS=/workspace/frontend/node_modules /home/soundatlas/.cache/ms-playwright /home/soundatlas/.cache/uv /home/soundatlas/.config/gh /home/soundatlas/.npm /home/soundatlas/.codex
```

The workspace depends on the `backend` and `frontend` services with
`condition: service_started`. This means their containers have started; it
does not mean they are healthy or ready to accept requests. The `frontend`
service itself waits for the backend healthcheck before starting.

The `workspace` service also sets `seccomp=unconfined` so Codex's Linux
sandbox helper can create the user namespaces required by Bubblewrap inside
Docker Desktop/WSL2. Without that option, normal Codex tool calls and
`apply_patch` can fail before touching the workspace with a Bubblewrap
namespace error.

### `pane-workspace`

Defined in `.devcontainer/docker-compose.devcontainer.yml` and enabled only by
the `pane` profile.

Responsibilities:

- run the Pane daemon and its built-in agents as `soundatlas` (UID/GID 10001)
- own SoundAtlas base clones and Pane-managed worktrees under `/runtime/repos`
- reach, but never manage, the shared `backend` and `frontend` services
- expose only authenticated SSH on host loopback for the local Pane UI tunnel
- preserve Pane, repository, SSH, Codex, GitHub CLI, and tool-cache state in
  dedicated named volumes

The service shares `pane-egress`'s network namespace and starts only after its
firewall healthcheck passes. The companion depends on the Compose-owned backend
and frontend services being started. Pane has no
Docker socket and cannot start, stop, or reconfigure either application
service.

### `backend`

Defined in the root `docker-compose.yml` and started as a dependency of the
`workspace` service.

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

The dev container setup intentionally avoids broad host home directories,
private SSH keys, unrelated dotfiles, and cloud configuration directories.

The `workspace` service uses these mounts:

- repository bind mount: `.` to `/workspace`
- named volume: `frontend_node_modules` to `/workspace/frontend/node_modules`
- named volume: `playwright_cache` to `/home/soundatlas/.cache/ms-playwright`
- named volume: `backend_uv_cache` to `/home/soundatlas/.cache/uv`
- named volume: `frontend_npm_cache` to `/home/soundatlas/.npm`
- named volume: `codex_home` to `/home/soundatlas/.codex`
- named volume: `github_cli_config` to `/home/soundatlas/.config/gh`
- read-only host bind mount:
  `${SOUNDATLAS_HOST_CODEX_HOME:-${USERPROFILE:-${HOME}}/.codex}` to
  `/mnt/host-codex`
- read-only host bind mount: `../secrets/soundatlas/.env` to
  `/run/secrets/soundatlas.env`
- read-only host bind mount: `../secrets/soundatlas/github-agent.env` to
  `/run/secrets/github-agent.env`

Because `CODEX_HOME` points at the `codex_home` volume, Codex keeps its
container-local SQLite state and manually editable `config.toml` on a Linux
filesystem. The `.codex` directory is owned by `soundatlas` with mode `0700`;
present `config.toml` and `auth.json` files have mode `0600`.

Post-create performs a one-time bootstrap only when the corresponding
container-local file is absent: it may seed `auth.json` and `config.toml` from
the read-only host `.codex` mount, then establishes the SoundAtlas defaults for
the initial config. Later post-create runs preserve existing config contents;
they do not normalize, remove, or replace user settings. The initial defaults
trust `/workspace`, use `workspace-write` with `on-request` approvals, enable
workspace shell network access, and allow Codex writes only to `/workspace`,
`/home/soundatlas/.cache/uv`, and `/home/soundatlas/.npm`.

The root container entrypoint may still prepare `/home/soundatlas/.codex` so
that `soundatlas` owns the persistent Docker volume. That operating-system
permission is distinct from Codex's sandbox writable roots: Codex does not
receive normal workspace-sandbox write access to its own configuration
directory. Network egress remains bounded by the container firewall described
below. Credentials are not copied into the repository or Docker image. The
workspace image installs the Codex CLI, so terminal sessions inside the
container use the seeded login cache and configuration by default when the host
`.codex` directory exists. Override the host path with
`SOUNDATLAS_HOST_CODEX_HOME` when needed.
The workspace intentionally shares dependency/cache volumes with the app
services so agent-run checks and running services see the same installed
frontend packages and uv cache.

The `pane-workspace` service uses separate runtime-owned volumes for Pane
state, repositories/worktrees, SSH host state, Codex state, GitHub CLI state,
and uv/npm/Playwright caches. Its only host inputs are these read-only files:

- Pane entrypoint and SSH daemon configuration from `.devcontainer/`
- the public `pane_authorized_keys` seed
- host Codex `auth.json` and `config.toml` seeds
- the scoped `github-agent.env` seed

It does not mount `.`, `/workspace`, the host `.codex` directory, a private SSH
key, or a container-control socket. The public SSH key, Codex login state, and
GitHub agent environment are copied with mode `0600` into their respective
runtime volumes when absent. The host Codex configuration is copied and
adapted by `post-create.sh` after the Pane-owned clone exists.

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

### CI-parity validation

After dependencies have been installed by `.devcontainer/post-create.sh`, run
the complete baseline validation path from the workspace root:

```sh
cd /workspace
bash scripts/validate-dev.sh
```

The helper runs the same checks as the `test` job in
`.github/workflows/pages-deploy.yml`, from the directories expected by each tool:

```text
frontend/: npm run validate
backend/:  uv run ruff check .
backend/:  uv run pytest
```

It stops and exits non-zero when any check fails. It does not install
dependencies or run automatically during container creation, so post-create
setup remains fast and repeatable.

Run the commands individually when a focused check is more useful.

Run backend checks from the workspace container:

```sh
cd /workspace/backend
uv run ruff check .
uv run pyright
uv run pytest
```

Run frontend checks from the workspace container:

```sh
cd /workspace/frontend
npm run validate
```

For larger frontend changes that also need a production build, run
`npm run validate:release` instead.

To validate the GitHub Pages deployment mode locally, run:

```sh
npm run validate:pages
```

This uses the same static-data mode and `/soundatlas` base path as Frontend CI.

`uv run pyright` and the coverage commands below are useful additional local
quality checks, but they are not part of the default CI-parity validation path.

Generate optional coverage reports from the workspace container:

```sh
cd /workspace/backend
uv run pytest --cov

cd /workspace/frontend
npm run test:coverage
```

Coverage reports are informational only. They do not currently enforce minimum
thresholds in local validation or CI.

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

### Backend Script Completion

Interactive Bash shells in the workspace load completion for the backend
maintenance scripts. Completion is available for common invocation forms such
as:

```sh
cd /workspace/backend
uv run python scripts/report_seed_link_counts.py --event-id <Tab>
uv run python scripts/report_seed_link_counts.py --route-id <Tab>
```

`--event-id` values are read from `data/seed/events.json`; `--route-id` values
are read from `data/seed/routes.json`. Static choices such as `--kind`,
`--provider`, and `--query-planner` are completed from the script option
definitions.

## Browser Screenshot Checks

Browser and Playwright screenshot checks are optional and are not part of the
baseline validation path above. Run them only when validating browser rendering
or responsive UX.

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
remove and recreate the `codex_home` Docker volume rather than using the host
`.codex` directory itself as `CODEX_HOME`.

If Codex asks whether `/workspace` is trusted and then fails with
`failed to persist config.toml`, rebuild the dev container so `config.toml` is
written inside the `codex_home` volume instead of being mounted as an
individual host file.

## Security Boundaries

All workload containers run as the non-root `soundatlas` user after startup.
The inert `pane-egress` companion remains root with only `NET_ADMIN`.
The root phase is used only by `docker/egress-guard.sh` to prepare writable
paths and, when enabled, apply `iptables` restrictions before dropping
privileges with `gosu`.

The unchanged legacy `docker/egress-guard.sh`:

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
- `pane-workspace`: zero capabilities; firewall enforced by `pane-egress` in
  their shared network namespace

The Pane service deliberately preserves the Issue #194 least-privilege
boundary: UID/GID 10001, `cap_drop: ALL`, `no-new-privileges:true`, and the
versioned reduced Seccomp profile in `.devcontainer/pane-seccomp.json`. It does
not use privileged mode, `NET_ADMIN`, `--no-sandbox`, `seccomp=unconfined`,
host namespaces, a Docker/Podman socket, or a broad host mount. The Seccomp
profile is Docker/Moby v29.7.2's default plus only the four Chromium sandbox
allowances validated in Issue #194. The unmodified default profile's SHA-256
is `536529b665dd0972c37bfb569f5d4ac8a53592e7b00752bc39ff063ca9864c74`.

### Pane egress ownership and policy

`docker/pane-egress.Dockerfile` builds a minimal Debian companion with iptables
and the resolver tools used by `docker/pane-egress-guard.sh`. It has no volumes,
secrets, repository, Pane runtime, engine socket, host namespace, or published
application port. Its filesystem is read-only except for a private 1 MiB `/run`
tmpfs; limits are 32 processes, 64 MiB memory, and 0.25 CPU. It uses Docker's
default Seccomp profile and no-new-privileges. Only this companion receives
`NET_ADMIN`; it holds the namespace with an inert `sleep` after initialization.
Pane's existing SSH publication belongs to the companion's network endpoint.

The legacy guard allows arbitrary outbound DNS on TCP/UDP 53, rejects common
private IPv4 ranges, permits public TCP 443, and initializes IPv6 only when
available. Its configured application exceptions are resolved IPv4 IP/port
pairs. Pane preserves required public HTTPS and exact application reachability,
with stricter DNS and mandatory dual-family initialization:

1. Set both IPv4 and IPv6 OUTPUT policies to DROP before resolution or flushing.
2. Allow loopback (including Docker's embedded `127.0.0.11` resolver), then
   established/related replies. A missing or different resolver is fatal.
3. Resolve exactly `backend:8000 frontend:5173` and permit their usable IP/port
   pairs. Empty, malformed, changed, or unresolvable configuration is fatal.
4. Reject private, link-local, multicast, reserved and documentation IPv4
   ranges before allowing public TCP 443. IPv6 permits only native global
   unicast `2000::/3`, excluding special-use ranges including Teredo and 6to4;
   mapped IPv4, NAT64, ULA, and link-local cannot bypass private-address rules.
5. Drop every other outbound packet. Save and compare both installed OUTPUT
   chains before readiness; healthchecks compare them again for drift.

This is destination/port enforcement, not a hostname allowlist or HTTPS content
inspection. Loopback peers share the namespace. Public HTTPS and embedded DNS
remain available as required; they are not data-exfiltration prevention.

Host firewall/WSL enforcement would move policy into host administration;
a cooperative proxy would not stop direct-socket bypasses. The bounded companion
keeps enforcement outside Pane without those host changes or Pane privileges.

### Pane egress verification and failures

Run allowed probes in `pane-workspace`:

```sh
getent ahosts github.com
curl --noproxy '*' -fsS --max-time 10 -o /dev/null https://github.com
curl --noproxy '*' -fsS --max-time 5 http://backend:8000/health
curl --noproxy '*' -fsS --max-time 5 -H 'Host: localhost:5173' -o /dev/null http://frontend:5173
```

These denied probes must fail within their timeout:

```sh
curl --noproxy '*' --max-time 3 http://example.com
curl --noproxy '*' -k --max-time 3 https://169.254.169.254
```

Also use a disposable listener on the Compose network at an unapproved port:
prove it responds from an unfiltered control container, then fails from Pane.
Do not interpret a closed port as firewall evidence. Inspect both OUTPUT chains
from the companion and Pane's `/proc/self/status`: all capability masks must be
zero and `NoNewPrivs` must be 1. Inspect the helper's mounts, read-only root,
limits, and capability masks (only `NET_ADMIN`, bit `0x1000`).

Use disposable Compose projects for malformed configuration and missing-service
tests. They must leave the helper exited/unhealthy and Pane never started.
Do not change the running development stack's service aliases for these tests.
Remove every temporary listener, container, and network by its explicit probe
name after testing; do not prune unrelated Docker resources.

The pre-edit Docker Desktop/WSL lifecycle probe for #196 observed that killing
the namespace owner left the unprivileged Pane member running, but removed its
outbound route and Docker DNS. A previously reachable controlled listener stayed
unreachable by direct IP. Never flush firewall rules on exit. A failed startup
cannot release Pane through the health gate. A later unhealthy status does not
automatically stop an already-running Pane: rules stay installed, or namespace
endpoint loss stops connectivity. Treat either condition as requiring recovery.

Service IP changes and companion restarts require coordinated recreation;
restarting the helper alone can leave Pane in the old namespace. From the host:

```powershell
docker compose -f docker-compose.yml -f .devcontainer/docker-compose.devcontainer.yml --profile pane stop pane-workspace pane-egress
docker compose -f docker-compose.yml -f .devcontainer/docker-compose.devcontainer.yml --profile pane up -d --force-recreate pane-egress pane-workspace
```

Repeat one allowed and one controlled denied probe after recovery. Do not use
`--no-deps` to bypass the health gate for Pane. The legacy workspace remains a
rollback option; retirement stays blocked until Issue #196 evidence is accepted
or the Human explicitly changes that requirement.

This is a pragmatic agent-coding boundary, not a full sandbox. The agent can
edit the repository and use public HTTPS for package installation, Git remotes,
documentation lookup, and model/API access. The workspace may call only the
resolved Docker `backend:8000` and `frontend:5173` service destinations for
local backend/frontend checks. The egress guard resolves those service names at
startup and permits those exact destination IP/port pairs; it does not allow
arbitrary private addresses on ports `8000` or `5173`. If a configured service
cannot be resolved, workspace startup fails closed. It should not receive
direct mounts to host secrets or broader host directories.
The only host credential mount is the read-only
`${SOUNDATLAS_HOST_CODEX_HOME:-${USERPROFILE:-${HOME}}/.codex}` seed mount
used by the workspace service.

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

To roll back to workspace-only operation without touching backend, frontend,
or the current workspace, stop only the Pane client and its companion:

```powershell
docker compose -f docker-compose.yml -f .devcontainer/docker-compose.devcontainer.yml --profile pane stop pane-workspace pane-egress
docker compose -f docker-compose.yml -f .devcontainer/docker-compose.devcontainer.yml exec workspace curl -fsS http://backend:8000/health
```

Starting `pane-workspace` again reuses its named Pane, repository, SSH, Codex,
GitHub CLI, and tool-cache volumes. `docker compose down -v` is intentionally
not part of normal rollback because it destroys those volumes and may affect
the shared stack. Removal of `workspace`, changes to
`.devcontainer/devcontainer.json`, and final Pane promotion require separate
Human acceptance after the parallel smoke evidence; Issue #196 is also a
retirement dependency while equivalent egress enforcement remains required.
