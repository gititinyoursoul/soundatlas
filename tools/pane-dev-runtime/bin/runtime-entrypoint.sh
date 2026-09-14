#!/usr/bin/env bash
set -euo pipefail

pane_dir="${PANE_DIR:-/runtime/pane}"
repository_root="${PANE_REPOSITORY_ROOT:-/runtime/repos}"
ssh_dir="${PANE_SSH_DIR:-/runtime/ssh}"
codex_dir="${CODEX_HOME:-/runtime/codex}"

fail() { printf '%s\n' "$1" >&2; exit 1; }

main() {
  : "${PANE_REPOSITORY_NAME:?PANE_REPOSITORY_NAME is required}"
  [[ "$PANE_REPOSITORY_NAME" =~ ^[A-Za-z0-9][A-Za-z0-9._-]*$ ]] || fail "repository name is invalid"
  [[ -d "$repository_root/$PANE_REPOSITORY_NAME/.git" ]] || fail "attached repository is missing"
  [[ -f "$codex_dir/auth.json" ]] || fail "synthetic Codex auth file is missing"
  [[ -f "$ssh_dir/authorized_keys" ]] || fail "authorized-keys file is missing"
  mkdir -p "$pane_dir" "$ssh_dir"
  chmod 0700 "$ssh_dir"
  if [[ -n "${PANE_GIT_AUTHOR_NAME:-}" && -n "${PANE_GIT_AUTHOR_EMAIL:-}" ]]; then
    git config --global user.name "$PANE_GIT_AUTHOR_NAME"
    git config --global user.email "$PANE_GIT_AUTHOR_EMAIL"
  fi
  if [[ ! -f "$ssh_dir/ssh_host_ed25519_key" ]]; then
    ssh-keygen -q -t ed25519 -N '' -f "$ssh_dir/ssh_host_ed25519_key"
  fi
  /usr/sbin/sshd -D -e -f /etc/pane-runtime/sshd_config &
  sshd_pid=$!
  if ! node -e 'const fs=require("fs");try{const c=JSON.parse(fs.readFileSync(process.argv[1]));process.exit(c.remoteDaemon?.host?.config?.enabled?0:1)}catch{process.exit(1)}' "$pane_dir/config.json"; then
    runpane install daemon --pane-path /usr/bin/pane --pane-dir "$pane_dir" --prefer-tunnel ssh --label "Pane Runtime Phase 1" --no-install-service --yes >"$pane_dir/remote-setup.txt" 2>"$pane_dir/remote-setup.stderr"
    chmod 0600 "$pane_dir/remote-setup.txt" "$pane_dir/remote-setup.stderr"
  fi
  ELECTRON_OZONE_PLATFORM_HINT=headless PANE_DIR="$pane_dir" /opt/Pane/pane --ozone-platform=headless --disable-gpu --daemon-headless --pane-dir "$pane_dir" >"$pane_dir/daemon.stdout" 2>"$pane_dir/daemon.stderr" &
  pane_pid=$!
  shutdown() { kill "$pane_pid" "$sshd_pid" 2>/dev/null || true; }
  trap shutdown EXIT INT TERM
  "$@" &
  command_pid=$!
  wait -n "$pane_pid" "$sshd_pid" "$command_pid"
}

main "$@"
