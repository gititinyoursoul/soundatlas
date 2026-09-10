#!/usr/bin/env python3
"""Start Codex for one validated SoundAtlas workflow stage."""

from __future__ import annotations

import argparse
import json
import os
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Any

import tomllib

from pane_execution_context import ContextError, build_execution_context

SUPPORTED_STAGES = frozenset({"discussion", "planning", "implementation", "review"})
SUPPORTED_EFFORTS = frozenset({"low", "medium", "high", "xhigh"})
POLICY_PATH = Path(__file__).resolve().parents[1] / ".codex" / "model-routing.toml"


class PolicyError(ValueError):
    """Raised when a model-routing policy cannot be used safely."""


@dataclass(frozen=True)
class ResolvedStage:
    stage: str
    role: str
    model: str
    effort: str


def read_table(policy: dict[str, Any], name: str) -> dict[str, Any]:
    value = policy.get(name)
    if not isinstance(value, dict):
        raise PolicyError(f"model-routing policy requires a [{name}] table")
    return value


def read_non_empty_string(table: dict[str, Any], key: str, description: str) -> str:
    value = table.get(key)
    if not isinstance(value, str) or not value.strip():
        raise PolicyError(f"model-routing policy has no non-empty {description} for {key!r}")
    return value.strip()


def load_policy(path: Path = POLICY_PATH) -> dict[str, Any]:
    try:
        with path.open("rb") as policy_file:
            policy = tomllib.load(policy_file)
    except FileNotFoundError as error:
        raise PolicyError(f"model-routing policy was not found at {path}") from error
    except tomllib.TOMLDecodeError as error:
        raise PolicyError(f"model-routing policy is malformed: {error}") from error

    if not isinstance(policy, dict):
        raise PolicyError("model-routing policy must be a TOML table")
    return policy


def resolve_stage(stage: str, policy: dict[str, Any]) -> ResolvedStage:
    if stage not in SUPPORTED_STAGES:
        expected = ", ".join(sorted(SUPPORTED_STAGES))
        raise PolicyError(f"unknown workflow stage {stage!r}; expected one of: {expected}")

    workflow = read_table(policy, "workflow")
    roles = read_table(policy, "roles")
    efforts = read_table(policy, "effort")
    if set(workflow) != SUPPORTED_STAGES:
        expected = ", ".join(sorted(SUPPORTED_STAGES))
        raise PolicyError(f"[workflow] must define exactly: {expected}")

    role = read_non_empty_string(workflow, stage, "role")
    model = read_non_empty_string(roles, role, "model")
    effort = read_non_empty_string(efforts, role, "reasoning effort")
    if effort not in SUPPORTED_EFFORTS:
        expected = ", ".join(sorted(SUPPORTED_EFFORTS))
        raise PolicyError(f"unsupported reasoning effort {effort!r}; expected one of: {expected}")
    return ResolvedStage(stage=stage, role=role, model=model, effort=effort)


def build_command(resolved: ResolvedStage, execution_context: str) -> list[str]:
    return [
        "codex",
        "--model",
        resolved.model,
        "--config",
        f"model_reasoning_effort={json.dumps(resolved.effort)}",
        execution_context,
    ]


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--stage", required=True, help="SoundAtlas workflow stage to launch")
    parser.add_argument(
        "--print-command",
        action="store_true",
        help="print the validated command as JSON instead of starting Codex",
    )
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv)
    try:
        command = build_command(
            resolve_stage(args.stage, load_policy()), build_execution_context()
        )
    except (ContextError, PolicyError) as error:
        print(f"model routing failed: {error}", file=sys.stderr)
        return 2

    if args.print_command:
        print(json.dumps(command))
        return 0

    try:
        os.execvp(command[0], command)
    except FileNotFoundError:
        print("model routing failed: codex executable was not found on PATH", file=sys.stderr)
        return 127


if __name__ == "__main__":
    raise SystemExit(main())
