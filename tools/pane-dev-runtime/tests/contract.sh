#!/usr/bin/env bash
set -euo pipefail
root=$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)
for script in "$root"/bin/*.sh; do bash -n "$script"; done
if rg -n -i 'soundatlas|postgres|dbt|openrouter|ollama|github-agent' \
  "$root/Dockerfile" "$root/egress.Dockerfile" "$root/compose.yaml" "$root/bin" "$root/config"; then
  printf '%s\n' 'generic runtime contains a project-specific reference' >&2
  exit 1
fi
rg -q '^  runtime:$' "$root/compose.yaml"
rg -q '^  egress:$' "$root/compose.yaml"
rg -q 'network_mode: service:egress' "$root/compose.yaml"
