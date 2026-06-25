#!/usr/bin/env sh
set -eu

CODEX_HOME="${CODEX_HOME:-/home/soundatlas/.codex}"
HOST_CODEX_HOME="/mnt/host-codex"

mkdir -p "$CODEX_HOME"

if [ -d "$HOST_CODEX_HOME" ]; then
  if [ -f "$HOST_CODEX_HOME/auth.json" ]; then
    cp "$HOST_CODEX_HOME/auth.json" "$CODEX_HOME/auth.json"
    chmod 0600 "$CODEX_HOME/auth.json"
  fi

  if [ -f "$HOST_CODEX_HOME/config.toml" ] && [ ! -f "$CODEX_HOME/config.toml" ]; then
    cp "$HOST_CODEX_HOME/config.toml" "$CODEX_HOME/config.toml"
    chmod 0600 "$CODEX_HOME/config.toml"
  fi
fi

git config --global --replace-all safe.directory /workspace
git config --global credential.useHttpPath true
git config --global core.autocrlf true
git config --global core.filemode false
