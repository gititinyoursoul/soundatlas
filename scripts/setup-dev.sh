#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd -- "$SCRIPT_DIR/.." && pwd)"

if ! command -v uv >/dev/null 2>&1; then
  echo "uv is required but was not found in PATH." >&2
  exit 1
fi

if ! command -v npm >/dev/null 2>&1; then
  echo "npm is required but was not found in PATH." >&2
  exit 1
fi

if [[ ! -f "$REPO_ROOT/backend/pyproject.toml" ]]; then
  echo "Backend project not found at $REPO_ROOT/backend" >&2
  exit 1
fi

if [[ ! -f "$REPO_ROOT/frontend/package.json" ]]; then
  echo "Frontend project not found at $REPO_ROOT/frontend" >&2
  exit 1
fi

echo "Installing locked backend dependencies..."
(
  cd "$REPO_ROOT/backend"
  uv sync --locked --dev
)

echo "Installing locked frontend dependencies..."
(
  cd "$REPO_ROOT/frontend"
  npm ci
)

echo "SoundAtlas development dependencies are ready."
