#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd -- "$SCRIPT_DIR/.." && pwd)"
BACKEND_DIR="$REPO_ROOT/backend"
FRONTEND_DIR="$REPO_ROOT/frontend"

if [[ ! -f "$BACKEND_DIR/pyproject.toml" ]]; then
  echo "Backend project not found at $BACKEND_DIR" >&2
  exit 1
fi

if [[ ! -f "$FRONTEND_DIR/package.json" ]]; then
  echo "Frontend project not found at $FRONTEND_DIR" >&2
  exit 1
fi

run_section() {
  local name="$1"
  shift

  echo
  echo "=== $name ==="
  "$@"
}

run_section "Frontend validation" bash -c "cd \"$FRONTEND_DIR\" && npm run validate"
run_section "Backend lint" bash -c "cd \"$BACKEND_DIR\" && uv run ruff check ."
run_section "Backend tests" bash -c "cd \"$BACKEND_DIR\" && uv run pytest"

echo
echo "SoundAtlas development validation passed."
