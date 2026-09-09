#!/usr/bin/env bash
set -euo pipefail

pane_dir="${PANE_DIR:-/runtime/pane}"
repo_dir="${SOUNDATLAS_PANE_REPO_DIR:-/runtime/repos}"
ssh_dir="${SOUNDATLAS_PANE_SSH_DIR:-/runtime/ssh}"
codex_dir="${CODEX_HOME:-/home/soundatlas/.codex}"
host_codex_dir="${HOST_CODEX_HOME:-/mnt/host-codex}"

seed_playwright_browser_cache() {
  local staging_dir="${1:-/opt/soundatlas-playwright-browsers}"
  local cache_dir="${2:-/home/soundatlas/.cache/ms-playwright}"

  if [ ! -d "$staging_dir" ]; then
    echo "pane-workspace Playwright browser bundle is missing: $staging_dir" >&2
    return 1
  fi

  mkdir -p "$cache_dir"
  cp -a -n "$staging_dir"/. "$cache_dir"/
}

load_repository_git_credentials() {
  if [ -z "${GH_TOKEN:-}" ]; then
    if [ -z "${SOUNDATLAS_GITHUB_AGENT_ENV_FILE:-}" ] || [ ! -r "$SOUNDATLAS_GITHUB_AGENT_ENV_FILE" ]; then
      echo "pane-workspace requires a readable repository GitHub credential file" >&2
      return 1
    fi

    local github_token=""
    local github_token_lines=0
    local github_env_line
    while IFS= read -r github_env_line || [ -n "$github_env_line" ]; do
      case "$github_env_line" in
        ""|'#'*) continue ;;
        GH_TOKEN=*)
          github_token="${github_env_line#GH_TOKEN=}"
          github_token_lines=$((github_token_lines + 1))
          ;;
        *)
          echo "Repository GitHub credential file must contain only GH_TOKEN" >&2
          return 1
          ;;
      esac
    done < "$SOUNDATLAS_GITHUB_AGENT_ENV_FILE"

    if [ "$github_token_lines" -ne 1 ] || [ -z "$github_token" ]; then
      echo "Repository GitHub credential file must contain one non-empty GH_TOKEN" >&2
      return 1
    fi
    export GH_TOKEN="$github_token"
  fi

  local git_config_count="${GIT_CONFIG_COUNT:-0}"
  if ! [[ "$git_config_count" =~ ^[0-9]+$ ]]; then
    echo "GIT_CONFIG_COUNT must be a non-negative integer" >&2
    return 1
  fi
  git_config_count=$((10#$git_config_count))
  export GIT_CONFIG_COUNT=$((git_config_count + 1))
  export "GIT_CONFIG_KEY_${git_config_count}=credential.helper"
  export "GIT_CONFIG_VALUE_${git_config_count}=!gh auth git-credential"
}

main() {
  umask 077
  mkdir -p "$pane_dir" "$repo_dir" "$ssh_dir" "$codex_dir"
  seed_playwright_browser_cache

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

  load_repository_git_credentials

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
}

if [[ "${BASH_SOURCE[0]}" == "$0" ]]; then
  main "$@"
fi
