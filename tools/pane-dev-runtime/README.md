# Pane Runtime Phase 1 candidate

This isolated directory is the complete Docker build context for Issue #243
Phase 1. It provides pinned Pane, RunPane, Codex, Git, SSH transport, candidate
state, and a default-deny/public-HTTPS egress fixture. It deliberately excludes
Python, uv, DBT, PostgreSQL, browser tooling, GitHub CLI, provider clients, and
project credentials.

Create a fresh disposable proof root with one clean clone at a recorded commit.
Do not point the following values at a user checkout or existing Pane state:

```sh
export PANE_PROOF_ROOT=/absolute/path/to/disposable-proof-root
export PANE_REPOSITORY_NAME=independent-proof
export PANE_AUTHORIZED_KEYS_FILE=/absolute/path/to/test-authorized-keys
export PANE_CODEX_AUTH_FILE=/absolute/path/to/synthetic-auth.json
# Optional for a Windows-host checkout whose line-ending policy must be honored.
export PANE_GIT_AUTOCRLF=true
```

From this directory, use the one supported candidate lifecycle:

```sh
docker compose --project-name pane-runtime-phase1 -f compose.yaml config --quiet
docker compose --project-name pane-runtime-phase1 -f compose.yaml build
docker compose --project-name pane-runtime-phase1 -f compose.yaml up -d
```

`tests/smoke.sh` collects the candidate smoke. It never stops an existing
runtime. Candidate deletion, `down -v`, worktree/ref removal, and production
cutover are outside Phase 1. The egress companion is a regression fixture, not
the selected generic networking contract.
