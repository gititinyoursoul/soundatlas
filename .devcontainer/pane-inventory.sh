#!/usr/bin/env bash
set -euo pipefail

readonly PANE_REPOSITORY="soundatlas"
readonly PANE_RUNTIME_DIR="/runtime/pane"

fail() {
  printf 'Pane inventory: %s\n' "$*" >&2
  exit 1
}

usage() {
  cat >&2 <<'EOF'
Usage: soundatlas-pane-inventory --pane <pane-name-or-id>
EOF
  exit 2
}

selector=""
while [ "$#" -gt 0 ]; do
  case "$1" in
    --pane)
      [ "$#" -ge 2 ] || usage
      selector="$2"
      shift 2
      ;;
    --help|-h)
      usage
      ;;
    *)
      usage
      ;;
  esac
done

[ -n "$selector" ] || usage
command -v runpane >/dev/null 2>&1 || fail "runpane is unavailable in pane-workspace."
command -v python3 >/dev/null 2>&1 || fail "Python 3 is unavailable in pane-workspace."

if ! pane_json="$(PANE_DIR="$PANE_RUNTIME_DIR" runpane panes list --repo "$PANE_REPOSITORY" --json 2>/dev/null)"; then
  fail "Pane inventory is unavailable. Confirm that the Pane profile is running and retry over its authenticated loopback SSH endpoint."
fi

python3 -c '
import json
import sys

selector = sys.argv[1]
try:
    payload = json.load(sys.stdin)
except json.JSONDecodeError:
    print("Pane inventory: Pane returned malformed inventory data.", file=sys.stderr)
    raise SystemExit(1)

if not isinstance(payload, dict) or payload.get("ok") is not True:
    print("Pane inventory: Pane inventory response was unsuccessful.", file=sys.stderr)
    raise SystemExit(1)

panes = payload.get("panes")
if not isinstance(panes, list):
    print("Pane inventory: Pane inventory response did not contain a Pane list.", file=sys.stderr)
    raise SystemExit(1)

matches = [
    pane
    for pane in panes
    if isinstance(pane, dict)
    and selector in {str(pane.get("id", "")), str(pane.get("paneId", "")), str(pane.get("name", ""))}
]
if not matches:
    print(f"Pane inventory: No Pane matched {selector!r} in repository soundatlas.", file=sys.stderr)
    raise SystemExit(1)
if len(matches) != 1:
    print(f"Pane inventory: Pane selector {selector!r} is ambiguous in repository soundatlas.", file=sys.stderr)
    raise SystemExit(1)

pane = matches[0]
pane_id = pane.get("paneId") or pane.get("id")
pane_name = pane.get("name")
repo_name = pane.get("repoName")
worktree_path = pane.get("worktreePath")
if not all(isinstance(value, str) and value for value in (pane_id, pane_name, repo_name, worktree_path)):
    print("Pane inventory: Selected Pane is missing required identity fields.", file=sys.stderr)
    raise SystemExit(1)
if repo_name != "soundatlas":
    print("Pane inventory: Selected Pane does not belong to repository soundatlas.", file=sys.stderr)
    raise SystemExit(1)

json.dump(
    {
        "pane_id": pane_id,
        "pane_name": pane_name,
        "repo_name": repo_name,
        "worktree_path": worktree_path,
    },
    sys.stdout,
    separators=(",", ":"),
)
sys.stdout.write("\n")
' "$selector" <<<"$pane_json"
