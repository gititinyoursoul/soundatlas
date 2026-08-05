# Local Development

This document covers host-based development. For the reproducible VS Code or
Codex workspace, use the [Dev Container documentation](dev-container.md).

## Prerequisites

Install the following tools on the host:

- Python `>=3.13`
- `uv`
- Node.js and npm
- Bash for `scripts/setup-dev.sh` and `scripts/start-dev.sh`, or PowerShell
  for the `.ps1` scripts

## First-time setup

Run the setup script from the repository root. It installs the backend and
frontend dependencies from their lockfiles.

PowerShell:

```powershell
.\scripts\setup-dev.ps1
```

Bash:

```sh
./scripts/setup-dev.sh
```

Run the setup script again after changing either dependency lockfile.

## Start the application

PowerShell:

```powershell
.\scripts\start-dev.ps1
```

Bash:

```sh
./scripts/start-dev.sh
```

The scripts start both services and stop them together when the process ends.

Default URLs:

- Frontend: `http://127.0.0.1:5173`
- Backend: `http://127.0.0.1:8000`
- Health: `http://127.0.0.1:8000/health`

The Bash start script accepts `--backend-port` and `--frontend-port` when the
default ports are already in use.

## Checks

Run backend checks from `backend/`:

```sh
uv run ruff check .
uv run pyright
uv run pytest
```

Run frontend checks from `frontend/`:

```sh
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

## Troubleshooting

- If frontend installation fails with an npm lockfile synchronization error,
  resolve the dependency change intentionally and rerun the setup script.
- If a service port is already in use, pass alternate ports to the Bash start
  script or use the corresponding parameters of the PowerShell script.
- If the Dev Container is required, follow its separate prerequisite and
  secret-file instructions in `docs/dev-container.md`.
