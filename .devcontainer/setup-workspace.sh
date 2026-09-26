#!/usr/bin/env sh
set -eu

WORKSPACE_ROOT="${SOUNDATLAS_WORKSPACE_ROOT:-$(git rev-parse --show-toplevel 2>/dev/null || pwd)}"

git config --global --replace-all safe.directory "$WORKSPACE_ROOT"
git config --global credential.useHttpPath true
git config --global core.autocrlf true
git config --global core.filemode false

if [ -n "${SOUNDATLAS_GIT_AUTHOR_NAME:-}" ] && [ -n "${SOUNDATLAS_GIT_AUTHOR_EMAIL:-}" ]; then
  git config --global user.name "$SOUNDATLAS_GIT_AUTHOR_NAME"
  git config --global user.email "$SOUNDATLAS_GIT_AUTHOR_EMAIL"
fi

echo "Syncing backend dependencies..."
cd "$WORKSPACE_ROOT/backend"
uv sync --locked --dev

echo "Installing frontend dependencies..."
cd "$WORKSPACE_ROOT/frontend"
npm ci
