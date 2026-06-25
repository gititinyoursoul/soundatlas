#!/usr/bin/env sh
set -eu

CODEX_HOME="${CODEX_HOME:-/home/soundatlas/.codex}"
HOST_CODEX_HOME="/mnt/host-codex"
CODEX_CONFIG="$CODEX_HOME/config.toml"

mkdir -p "$CODEX_HOME"

if [ -d "$HOST_CODEX_HOME" ]; then
  if [ -f "$HOST_CODEX_HOME/auth.json" ]; then
    cp "$HOST_CODEX_HOME/auth.json" "$CODEX_HOME/auth.json"
    chmod 0600 "$CODEX_HOME/auth.json"
  fi

  if [ -f "$HOST_CODEX_HOME/config.toml" ] && [ ! -f "$CODEX_CONFIG" ]; then
    cp "$HOST_CODEX_HOME/config.toml" "$CODEX_CONFIG"
    chmod 0600 "$CODEX_CONFIG"
  fi
fi

if [ ! -f "$CODEX_CONFIG" ]; then
  : > "$CODEX_CONFIG"
  chmod 0600 "$CODEX_CONFIG"
fi

python3 - "$CODEX_CONFIG" <<'PY'
from pathlib import Path
import re
import sys

path = Path(sys.argv[1])
text = path.read_text(encoding="utf-8") if path.exists() else ""
lines = text.splitlines()

root_keys = {"approval_policy", "sandbox_mode", "web_search"}
managed_tables = {"sandbox_workspace_write", 'projects."/workspace"'}
generated_defaults_comment = (
    "# SoundAtlas dev container defaults. These are applied only inside CODEX_HOME."
)
table_re = re.compile(r"^\s*\[([^\[\]]+)\]\s*(?:#.*)?$")
key_re = re.compile(r"^\s*([A-Za-z0-9_.-]+)\s*=")

kept = []
current_table = ""
skip_table = False
skip_generated_defaults = False

for line in lines:
    stripped = line.strip()
    table_match = table_re.match(line)
    if table_match:
        current_table = table_match.group(1).strip()
        skip_table = current_table in managed_tables
        skip_generated_defaults = False
        if skip_table:
            continue

    if skip_table:
        continue

    key_match = key_re.match(line)

    if stripped == generated_defaults_comment:
        skip_generated_defaults = True
        continue

    if skip_generated_defaults:
        if stripped == "":
            continue
        if key_match and key_match.group(1) in root_keys:
            continue
        skip_generated_defaults = False

    if key_match and key_match.group(1) in root_keys:
        if current_table == "":
            continue
        if current_table == "tui.model_availability_nux":
            continue

    kept.append(line)

root_block = """
# SoundAtlas dev container defaults. These are applied only inside CODEX_HOME.
approval_policy = "on-request"
sandbox_mode = "workspace-write"
web_search = "cached"
""".strip()

table_block = """
[sandbox_workspace_write]
network_access = true
exclude_tmpdir_env_var = false
exclude_slash_tmp = false
writable_roots = [
  "/workspace",
  "/home/soundatlas/.cache/uv",
  "/home/soundatlas/.npm",
  "/home/soundatlas/.codex",
]

[projects."/workspace"]
trust_level = "trusted"
""".strip()

while kept and kept[-1] == "":
    kept.pop()

first_table_index = next(
    (index for index, line in enumerate(kept) if table_re.match(line)),
    len(kept),
)

before_tables = kept[:first_table_index]
after_tables = kept[first_table_index:]

while before_tables and before_tables[-1] == "":
    before_tables.pop()
while after_tables and after_tables[0] == "":
    after_tables.pop(0)

parts = []
if before_tables:
    parts.append("\n".join(before_tables))
parts.append(root_block)
if after_tables:
    parts.append("\n".join(after_tables))
parts.append(table_block)

new_text = "\n\n".join(parts) + "\n"
path.write_text(new_text, encoding="utf-8")
PY

git config --global --replace-all safe.directory /workspace
git config --global credential.useHttpPath true
git config --global core.autocrlf true
git config --global core.filemode false
