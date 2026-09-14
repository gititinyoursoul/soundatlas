#!/usr/bin/env bash
set -euo pipefail

name="${PANE_REPOSITORY_NAME:-unknown}"
[[ "$name" =~ ^[A-Za-z0-9][A-Za-z0-9._-]*$ ]] || name=unknown
pane_dir="${PANE_DIR:-/runtime/pane}"
printf '{"repository":"%s","pane_directory_ready":%s,"ssh_ready":%s,"codex_available":%s}\n' \
  "$name" \
  "$(test -f "$pane_dir/config.json" && printf true || printf false)" \
  "$(test -f /runtime/ssh/sshd.pid && printf true || printf false)" \
  "$(command -v codex >/dev/null 2>&1 && printf true || printf false)"
