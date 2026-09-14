#!/usr/bin/env bash
set -euo pipefail
root=$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)
command -v docker >/dev/null 2>&1 || { printf '%s\n' 'Docker is required for the Phase 1 runtime smoke.' >&2; exit 2; }
: "${PANE_PROOF_ROOT:?set an absolute disposable proof-root path}"
: "${PANE_REPOSITORY_NAME:?set a disposable repository name}"
: "${PANE_AUTHORIZED_KEYS_FILE:?set a test-only authorized-keys file}"
: "${PANE_CODEX_AUTH_FILE:?set a synthetic Codex auth-shaped file}"
cd "$root"
docker compose --project-name "${PANE_COMPOSE_PROJECT:-pane-runtime-phase1}" -f compose.yaml config --quiet
docker compose --project-name "${PANE_COMPOSE_PROJECT:-pane-runtime-phase1}" -f compose.yaml build
docker compose --project-name "${PANE_COMPOSE_PROJECT:-pane-runtime-phase1}" -f compose.yaml up -d
docker compose --project-name "${PANE_COMPOSE_PROJECT:-pane-runtime-phase1}" -f compose.yaml exec -T runtime pane-runtime-status
docker compose --project-name "${PANE_COMPOSE_PROJECT:-pane-runtime-phase1}" -f compose.yaml exec -T runtime pane-runtime-attach-repository "$PANE_REPOSITORY_NAME"
docker compose --project-name "${PANE_COMPOSE_PROJECT:-pane-runtime-phase1}" -f compose.yaml exec -T runtime codex --version
docker compose --project-name "${PANE_COMPOSE_PROJECT:-pane-runtime-phase1}" -f compose.yaml exec -T runtime runpane panes create --repo "$PANE_REPOSITORY_NAME" --name "${PANE_REPOSITORY_NAME}-phase1" --tool-command 'bash -lc "git status --short"' --source agent --no-focus --yes --json
docker compose --project-name "${PANE_COMPOSE_PROJECT:-pane-runtime-phase1}" -f compose.yaml exec -T runtime runpane panes list --repo "$PANE_REPOSITORY_NAME" --json
