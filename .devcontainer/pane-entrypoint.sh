#!/usr/bin/env bash
set -euo pipefail

pane_dir="${PANE_DIR:-/runtime/pane}"
repo_dir="${SOUNDATLAS_PANE_REPO_DIR:-/runtime/repos}"
ssh_dir="${SOUNDATLAS_PANE_SSH_DIR:-/runtime/ssh}"
codex_dir="${CODEX_HOME:-/home/soundatlas/.codex}"
host_codex_dir="${HOST_CODEX_HOME:-/mnt/host-codex}"

umask 077
mkdir -p "$pane_dir" "$repo_dir" "$ssh_dir" "$codex_dir"

copy_seed() {
  source_path="$1"
  target_path="$2"
  if [ ! -e "$target_path" ] && [ -f "$source_path" ]; then
    cp "$source_path" "$target_path"
    chmod 0600 "$target_path"
  fi
}

copy_seed "$host_codex_dir/auth.json" "$codex_dir/auth.json"
copy_seed /run/secrets/pane_authorized_keys "$ssh_dir/authorized_keys"

if [ -n "${SOUNDATLAS_GIT_AUTHOR_NAME:-}" ] && [ -n "${SOUNDATLAS_GIT_AUTHOR_EMAIL:-}" ]; then
  git config --global user.name "$SOUNDATLAS_GIT_AUTHOR_NAME"
  git config --global user.email "$SOUNDATLAS_GIT_AUTHOR_EMAIL"
fi
git config --global credential.useHttpPath true
git config --global core.autocrlf true
git config --global core.filemode false

if [ ! -f "$ssh_dir/ssh_host_ed25519_key" ]; then
  ssh-keygen -q -t ed25519 -N "" -f "$ssh_dir/ssh_host_ed25519_key"
fi

if [ ! -s "$ssh_dir/authorized_keys" ]; then
  echo "pane-workspace requires a non-empty read-only SSH authorized-keys seed" >&2
  exit 1
fi

chmod 0700 "$ssh_dir"
chmod 0600 "$ssh_dir/authorized_keys" "$ssh_dir/ssh_host_ed25519_key"
chmod 0644 "$ssh_dir/ssh_host_ed25519_key.pub"

/usr/sbin/sshd -D -e -f "${SOUNDATLAS_PANE_SSHD_CONFIG:-/runtime-config/pane-sshd_config}" &
sshd_pid=$!

if ! node -e '
  const fs = require("fs");
  const config = JSON.parse(fs.readFileSync(process.argv[1], "utf8"));
  process.exit(config.remoteDaemon?.host?.config?.enabled === true ? 0 : 1);
' "$pane_dir/config.json" 2>/dev/null; then
  runpane install daemon \
    --pane-path /usr/bin/pane \
    --pane-dir "$pane_dir" \
    --prefer-tunnel ssh \
    --label "${SOUNDATLAS_PANE_REMOTE_LABEL:-SoundAtlas Pane}" \
    --no-install-service \
    --yes \
    >"$pane_dir/remote-setup.txt" \
    2>"$pane_dir/remote-setup.stderr"
  chmod 0600 "$pane_dir/remote-setup.txt" "$pane_dir/remote-setup.stderr"
fi

ELECTRON_OZONE_PLATFORM_HINT=headless \
PANE_DIR="$pane_dir" \
/opt/Pane/pane \
  --ozone-platform=headless \
  --disable-gpu \
  --daemon-headless \
  --pane-dir "$pane_dir" \
  >"$pane_dir/daemon.stdout" \
  2>"$pane_dir/daemon.stderr" &
pane_pid=$!

shutdown() {
  kill "$pane_pid" "$sshd_pid" 2>/dev/null || true
}
trap shutdown EXIT INT TERM

"$@" &
command_pid=$!
wait -n "$pane_pid" "$sshd_pid" "$command_pid"
