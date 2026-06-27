#!/usr/bin/env bash
set -euo pipefail

BACKEND_PORT=8000
FRONTEND_PORT=5173

usage() {
  cat <<'EOF'
Usage: scripts/start-dev.sh [--backend-port PORT] [--frontend-port PORT]

Starts the SoundAtlas backend and frontend dev servers.

Options:
  --backend-port PORT   Backend port, default 8000
  --frontend-port PORT  Frontend port, default 5173
  -h, --help            Show this help text
EOF
}

while [[ $# -gt 0 ]]; do
  case "$1" in
    --backend-port)
      BACKEND_PORT="${2:-}"
      shift 2
      ;;
    --frontend-port)
      FRONTEND_PORT="${2:-}"
      shift 2
      ;;
    -h|--help)
      usage
      exit 0
      ;;
    *)
      echo "Unknown argument: $1" >&2
      usage >&2
      exit 2
      ;;
  esac
done

if [[ ! "$BACKEND_PORT" =~ ^[0-9]+$ ]]; then
  echo "Backend port must be a number." >&2
  exit 2
fi

if [[ ! "$FRONTEND_PORT" =~ ^[0-9]+$ ]]; then
  echo "Frontend port must be a number." >&2
  exit 2
fi

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

BACKEND_PID=""
FRONTEND_PID=""

cleanup() {
  local exit_code=$?

  trap - INT TERM EXIT

  if [[ -n "$FRONTEND_PID" ]] && kill -0 "$FRONTEND_PID" 2>/dev/null; then
    kill "$FRONTEND_PID" 2>/dev/null || true
  fi

  if [[ -n "$BACKEND_PID" ]] && kill -0 "$BACKEND_PID" 2>/dev/null; then
    kill "$BACKEND_PID" 2>/dev/null || true
  fi

  wait "$FRONTEND_PID" 2>/dev/null || true
  wait "$BACKEND_PID" 2>/dev/null || true

  exit "$exit_code"
}

trap cleanup INT TERM EXIT

echo "SoundAtlas dev servers are starting..."
echo "Backend:  http://127.0.0.1:$BACKEND_PORT"
echo "Frontend: http://127.0.0.1:$FRONTEND_PORT"
echo "Press Ctrl+C to stop both servers."

(
  cd "$BACKEND_DIR"
  uv run uvicorn app.main:app --reload --host 127.0.0.1 --port "$BACKEND_PORT"
) &
BACKEND_PID=$!

(
  cd "$FRONTEND_DIR"
  CHOKIDAR_USEPOLLING=true VITE_API_BASE_URL="http://127.0.0.1:$BACKEND_PORT" npm run dev -- --host 127.0.0.1 --port "$FRONTEND_PORT"
) &
FRONTEND_PID=$!

wait -n "$BACKEND_PID" "$FRONTEND_PID"
