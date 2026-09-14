#!/usr/bin/env bash
set -euo pipefail

repository_root="${PANE_REPOSITORY_ROOT:-/runtime/repos}"
name="${1:?repository name is required}"
fail() { printf '%s\n' "$1" >&2; exit 1; }
[[ "$name" =~ ^[A-Za-z0-9][A-Za-z0-9._-]*$ ]] || fail "repository name is invalid"
path="$repository_root/$name"
[[ -d "$path/.git" ]] || fail "repository is not a Git worktree"
[[ "$(git -C "$path" rev-parse --show-toplevel)" == "$path" ]] || fail "repository root is ambiguous"
[[ -z "$(git -C "$path" status --porcelain=v1)" ]] || fail "repository is dirty"
PANE_DIR="${PANE_DIR:-/runtime/pane}" runpane repos add --path "$path" --name "$name" --yes --json
