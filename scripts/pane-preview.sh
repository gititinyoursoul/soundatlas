#!/usr/bin/env bash
# Run a browser preview from one exact Pane-managed worktree over the existing
# loopback-only Pane SSH boundary. This script intentionally never accepts a
# host checkout path.
set -euo pipefail

DEFAULT_PORT=5174
DEFAULT_SSH_PORT=53660
PREVIEW_PATH="/__soundatlas/pane-preview"

usage() {
  cat <<'EOF'
Usage: scripts/pane-preview.sh --pane NAME_OR_ID [options]

Start a local browser preview served from one exact Pane-managed worktree.

Options:
  --pane NAME_OR_ID  Exact Pane name or id (required).
  --mode MODE        api (default) or static.
  --editorial        Enable Editorial Mode (API mode only).
  --port PORT        Local and remote Vite port (default: 5174).
  --ssh-port PORT    Pane loopback SSH port (default: 53660).
  --ssh-key PATH     Private key (default: ../secrets/soundatlas/pane_ed25519).
  -h, --help         Show this help.

The script prints a URL only after the local preview identity page responds.
Press Ctrl+C to stop both the tunnel and its SSH-owned Vite process.
EOF
}

fail() {
  echo "Pane preview: $*" >&2
  exit 1
}

require_value() {
  [[ -n "${2:-}" ]] || fail "$1 requires a value."
}

validate_port() {
  [[ "$1" =~ ^[0-9]+$ ]] && (( $1 >= 1024 && $1 <= 65535 )) || fail "Port must be between 1024 and 65535."
}

build_identity_json() {
  local pane_id="$1" pane_name="$2" branch="$3" commit="$4" state="$5" mode="$6" editorial="$7"
  python3 - "$pane_id" "$pane_name" "$branch" "$commit" "$state" "$mode" "$editorial" <<'PY'
import json
import sys
keys = ("paneId", "paneName", "branch", "commit", "worktreeState", "mode", "editorial")
print(json.dumps(dict(zip(keys, sys.argv[1:])), separators=(",", ":")))
PY
}

select_pane() {
  python3 -c '
import json
import sys

selector = sys.argv[1]
try:
    panes = json.load(sys.stdin).get("panes", [])
except (json.JSONDecodeError, AttributeError) as error:
    raise SystemExit(f"Pane list was not valid JSON: {error}")
matches = [pane for pane in panes if selector in (pane.get("id"), pane.get("paneId"), pane.get("name"))]
if not matches:
    raise SystemExit(f"No Pane matched {selector!r}. Run runpane panes list --repo soundatlas --json and choose one exact name or id.")
if len(matches) != 1:
    raise SystemExit(f"Pane selector {selector!r} is ambiguous; use an exact Pane id.")
pane = matches[0]
worktree = pane.get("worktreePath")
if not isinstance(worktree, str) or not worktree:
    raise SystemExit("The selected Pane has no worktreePath.")
for value in (pane.get("id") or pane.get("paneId"), pane.get("name"), worktree):
    if not isinstance(value, str) or not value:
        raise SystemExit("The selected Pane is missing a stable id, name, or worktree path.")
print("\t".join((pane.get("id") or pane.get("paneId"), pane["name"], worktree)))
' "$PANE_SELECTOR"
}

PANE_SELECTOR=""
MODE="api"
EDITORIAL="false"
PREVIEW_PORT="$DEFAULT_PORT"
SSH_PORT="$DEFAULT_SSH_PORT"
SCRIPT_DIR="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"
SSH_KEY="${SOUNDATLAS_PANE_SSH_KEY:-$SCRIPT_DIR/../../secrets/soundatlas/pane_ed25519}"

parse_args() {
  while [[ $# -gt 0 ]]; do
    case "$1" in
      --pane)
        require_value "$1" "${2:-}"
        PANE_SELECTOR="$2"
        shift 2
        ;;
      --mode)
        require_value "$1" "${2:-}"
        MODE="$2"
        shift 2
        ;;
      --editorial)
        EDITORIAL="true"
        shift
        ;;
      --port)
        require_value "$1" "${2:-}"
        PREVIEW_PORT="$2"
        shift 2
        ;;
      --ssh-port)
        require_value "$1" "${2:-}"
        SSH_PORT="$2"
        shift 2
        ;;
      --ssh-key)
        require_value "$1" "${2:-}"
        SSH_KEY="$2"
        shift 2
        ;;
      -h|--help)
        usage
        exit 0
        ;;
      *)
        fail "Unknown option: $1"
        ;;
    esac
  done

  [[ -n "$PANE_SELECTOR" ]] || fail "--pane NAME_OR_ID is required."
  [[ "$MODE" == "api" || "$MODE" == "static" ]] || fail "--mode must be api or static."
  [[ "$MODE" != "static" || "$EDITORIAL" != "true" ]] || fail "Editorial Mode requires --mode api; static data has no editorial API."
  validate_port "$PREVIEW_PORT"
  validate_port "$SSH_PORT"
}

SSH_PID=""
VITE_PID=""
LOG_FILE=""

cleanup() {
  local code=$?
  trap - EXIT INT TERM
  [[ -z "$SSH_PID" ]] || kill "$SSH_PID" 2>/dev/null || true
  [[ -z "$VITE_PID" ]] || kill "$VITE_PID" 2>/dev/null || true
  [[ -z "$SSH_PID" ]] || wait "$SSH_PID" 2>/dev/null || true
  [[ -z "$VITE_PID" ]] || wait "$VITE_PID" 2>/dev/null || true
  if (( code != 0 )) && [[ -n "$LOG_FILE" ]]; then
    echo "Pane preview diagnostics: $LOG_FILE" >&2
  fi
  exit "$code"
}

main() {
  parse_args "$@"
  [[ -r "$SSH_KEY" ]] || fail "SSH key is unavailable at $SSH_KEY. Create the documented Pane SSH key or pass --ssh-key PATH."
  command -v ssh >/dev/null || fail "ssh is unavailable. Install an OpenSSH client before starting a Pane preview."
  command -v python3 >/dev/null || fail "python3 is unavailable; it is required to validate Pane identity."
  command -v curl >/dev/null || fail "curl is unavailable; it is required to verify preview readiness."
  if [[ "$MODE" == "api" ]] && ! curl --fail --silent --max-time 2 http://127.0.0.1:8000/health >/dev/null; then
    fail "The host API is unavailable at http://127.0.0.1:8000/health. Start the Compose backend before an API or Editorial preview."
  fi

  local -a ssh_base=(ssh -o BatchMode=yes -o IdentitiesOnly=yes -o ExitOnForwardFailure=yes -i "$SSH_KEY" -p "$SSH_PORT" soundatlas@127.0.0.1)
  local pane_json selected pane_id pane_name worktree remote_identity branch commit worktree_state identity_json
  if ! pane_json="$("${ssh_base[@]}" 'runpane panes list --repo soundatlas --json')"; then
    fail "Cannot query Pane over SSH on 127.0.0.1:$SSH_PORT. Start the Pane profile and verify its SSH/key prerequisite."
  fi
  if ! selected="$(printf '%s' "$pane_json" | select_pane)"; then
    fail "Could not resolve exactly one Pane: $selected"
  fi
  IFS=$'\t' read -r pane_id pane_name worktree <<<"$selected"

  local q_worktree
  printf -v q_worktree '%q' "$worktree"
  if ! remote_identity="$("${ssh_base[@]}" "bash -lc 'worktree=$q_worktree; test \"\$(git -C \"\$worktree\" rev-parse --is-inside-work-tree)\" = true || exit 21; branch=\$(git -C \"\$worktree\" branch --show-current); commit=\$(git -C \"\$worktree\" rev-parse --short HEAD); if git -C \"\$worktree\" diff --quiet && git -C \"\$worktree\" diff --cached --quiet; then state=clean; else state=dirty; fi; printf \"%s\\n%s\\n%s\\n\" \"\$branch\" \"\$commit\" \"\$state\"'")"; then
    fail "Selected Pane worktree is not an accessible Git worktree; no server was started."
  fi
  mapfile -t identity_lines <<<"$remote_identity"
  (( ${#identity_lines[@]} == 3 )) || fail "Could not read the selected worktree identity; no server was started."
  branch="${identity_lines[0]}"
  commit="${identity_lines[1]}"
  worktree_state="${identity_lines[2]}"
  identity_json="$(build_identity_json "$pane_id" "$pane_name" "$branch" "$commit" "$worktree_state" "$MODE" "$EDITORIAL")"

  if ! "${ssh_base[@]}" "test -x $q_worktree/frontend/node_modules/.bin/vite"; then
    fail "Vite dependencies are unavailable in the selected Pane worktree. Run npm ci in $pane_name before starting a preview."
  fi

  if [[ "$MODE" == "static" ]]; then
    if ! "${ssh_base[@]}" "bash -lc 'cd -- $q_worktree/frontend && npm run generate:static-data'"; then
      fail "Static data generation failed in the selected Pane worktree; no preview URL was opened."
    fi
  fi

  local q_frontend q_pane_id q_pane_name q_branch q_commit q_state q_mode q_editorial q_api_base q_identity start_command
  printf -v q_frontend '%q' "$worktree/frontend"
  printf -v q_pane_id '%q' "$pane_id"
  printf -v q_pane_name '%q' "$pane_name"
  printf -v q_branch '%q' "$branch"
  printf -v q_commit '%q' "$commit"
  printf -v q_state '%q' "$worktree_state"
  printf -v q_mode '%q' "$MODE"
  printf -v q_editorial '%q' "$EDITORIAL"
  printf -v q_api_base '%q' 'http://127.0.0.1:8000'
  printf -v q_identity '%q' "$identity_json"
  start_command="cd -- $q_frontend && exec env SOUNDATLAS_PANE_PREVIEW=1 SOUNDATLAS_PANE_PREVIEW_ID=$q_pane_id SOUNDATLAS_PANE_PREVIEW_NAME=$q_pane_name SOUNDATLAS_PANE_PREVIEW_BRANCH=$q_branch SOUNDATLAS_PANE_PREVIEW_COMMIT=$q_commit SOUNDATLAS_PANE_PREVIEW_STATE=$q_state SOUNDATLAS_PANE_PREVIEW_MODE=$q_mode VITE_EDITORIAL_MODE=$q_editorial VITE_API_BASE_URL=$q_api_base VITE_DATA_MODE=$q_mode npm run dev -- --host 127.0.0.1 --port $PREVIEW_PORT --strictPort"

  LOG_FILE="$(mktemp -t soundatlas-pane-preview.XXXXXX.log)"
  "${ssh_base[@]}" "bash -lc '$start_command'" >"$LOG_FILE" 2>&1 &
  VITE_PID=$!
  "${ssh_base[@]}" -N -L "$PREVIEW_PORT:127.0.0.1:$PREVIEW_PORT" >"$LOG_FILE" 2>&1 &
  SSH_PID=$!
  trap cleanup EXIT INT TERM

  local attempt
  for attempt in $(seq 1 30); do
    if curl --fail --silent --show-error --max-time 2 "http://127.0.0.1:$PREVIEW_PORT$PREVIEW_PATH" >/dev/null; then
      echo "Pane preview ready: http://127.0.0.1:$PREVIEW_PORT$PREVIEW_PATH"
      echo "Pane: $pane_name ($pane_id), $branch@$commit, $worktree_state, $MODE mode, editorial=$EDITORIAL"
      echo "Press Ctrl+C to stop the preview."
      wait "$VITE_PID"
      return
    fi
    if ! kill -0 "$VITE_PID" 2>/dev/null || ! kill -0 "$SSH_PID" 2>/dev/null; then
      fail "Vite or the SSH tunnel stopped before readiness. Check the diagnostics path below."
    fi
    sleep 1
  done
  fail "Preview did not answer at $PREVIEW_PATH within 30 seconds; no ready browser URL was emitted."
}

if [[ "${BASH_SOURCE[0]}" == "$0" ]]; then
  main "$@"
fi
