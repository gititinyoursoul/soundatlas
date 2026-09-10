#!/usr/bin/env python3
"""Build the fail-closed execution-context notice for a Pane Codex session."""

from __future__ import annotations

import os
import subprocess
import sys
from collections.abc import Callable, Mapping


class ContextError(ValueError):
    """Raised when the Pane workspace boundary cannot be established."""


def git_workspace_root(run: Callable[..., subprocess.CompletedProcess[str]] = subprocess.run) -> str:
    try:
        result = run(
            ["git", "rev-parse", "--show-toplevel"],
            capture_output=True,
            check=False,
            text=True,
        )
    except OSError as error:
        raise ContextError("cannot determine the workspace root: git is unavailable") from error
    root = result.stdout.strip() if result.returncode == 0 else ""
    if not root:
        raise ContextError("cannot determine the workspace root: not inside a Git worktree")
    return root


def build_execution_context(
    *,
    environment: Mapping[str, str] | None = None,
    path_exists: Callable[[str], bool] = os.path.exists,
    run: Callable[..., subprocess.CompletedProcess[str]] = subprocess.run,
) -> str:
    """Return a non-secret notice based only on the running workspace."""
    environment = os.environ if environment is None else environment
    if not environment.get("PANE_DIR") or not path_exists("/.dockerenv"):
        raise ContextError("this launcher requires a Pane workspace container")

    git_workspace_root(run)
    display = "unavailable" if not (
        environment.get("DISPLAY") or environment.get("WAYLAND_DISPLAY")
    ) else "configured in this container"
    docker_socket = "unavailable" if not path_exists("/var/run/docker.sock") else "unknown"

    return "\n".join(
        (
            "Execution context (generated at this session start by a Pane-workspace self-probe):",
            "- WORKSPACE: available — current Linux container Git worktree.",
            "  Run workspace commands only from this worktree; do not infer host access from mounts or paths.",
            "- SERVICE: unknown until freshly probed from this container. localhost refers only to this network namespace; use a task-declared container service name when applicable.",
            "- HOST: unavailable — do not run or request host commands, Docker/Podman, host service control, GUI/browser opening, port forwarding, or filesystem access.",
            f"- GUI: {display}. Automated browser checks do not imply a host browser is available.",
            f"- Docker socket: {docker_socket}. Do not treat an installed command or a mounted file as authority.",
            "- Invariant: unknown, unreachable, or unsupported capabilities are unavailable. Preserve the existing sandbox, mounts, and network policy.",
        )
    )


def main() -> int:
    try:
        print(build_execution_context())
    except ContextError as error:
        print(f"execution context failed: {error}", file=sys.stderr)
        return 2
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
