#!/usr/bin/env bash
set -euo pipefail

BACKEND_PORT=8000
FRONTEND_PORT=5173

usage() {
  cat <<'EOF'
Usage: scripts/stop-dev.sh [--backend-port PORT] [--frontend-port PORT]

Stops SoundAtlas backend and frontend dev servers started on the given ports.

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

find_port_pids() {
  local port="$1"

  if command -v lsof >/dev/null 2>&1; then
    lsof -ti "tcp:$port" 2>/dev/null || true
    return
  fi

  if command -v fuser >/dev/null 2>&1; then
    fuser "${port}/tcp" 2>/dev/null || true
    return
  fi
}

find_matching_pids() {
  local pattern="$1"

  ps -eo pid=,args= |
    awk -v pattern="$pattern" '
      $0 ~ pattern && $0 !~ /awk -v pattern/ && $0 !~ /stop-dev\.sh/ {
        print $1
      }
    '
}

collect_pids() {
  {
    find_port_pids "$BACKEND_PORT"
    find_port_pids "$FRONTEND_PORT"
    find_matching_pids "uvicorn app\\.main:app.*--port[ =]?$BACKEND_PORT"
    find_matching_pids "vite dev.*--port[ =]?$FRONTEND_PORT"
    find_matching_pids "npm run dev.*--port[ =]?$FRONTEND_PORT"
  } | awk 'NF && !seen[$1]++ { print $1 }'
}

terminate_pids() {
  local pids=("$@")

  if [[ ${#pids[@]} -eq 0 ]]; then
    echo "No SoundAtlas dev servers found on backend port $BACKEND_PORT or frontend port $FRONTEND_PORT."
    return
  fi

  echo "Stopping SoundAtlas dev server processes: ${pids[*]}"
  kill "${pids[@]}" 2>/dev/null || true

  sleep 1

  local still_running=()
  local pid
  for pid in "${pids[@]}"; do
    if kill -0 "$pid" 2>/dev/null; then
      still_running+=("$pid")
    fi
  done

  if [[ ${#still_running[@]} -gt 0 ]]; then
    echo "Force stopping remaining processes: ${still_running[*]}"
    kill -9 "${still_running[@]}" 2>/dev/null || true
  fi
}

mapfile -t PIDS < <(collect_pids)
terminate_pids "${PIDS[@]}"
