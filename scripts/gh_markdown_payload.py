#!/usr/bin/env python3
"""Encode a Markdown body as a shell-safe GitHub API JSON payload."""

from __future__ import annotations

import argparse
import json
from pathlib import Path


def read_body(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def emit_payload(path: Path) -> None:
    print(json.dumps({"body": read_body(path)}, ensure_ascii=False))


def parser() -> argparse.ArgumentParser:
    command_parser = argparse.ArgumentParser(description=__doc__)
    command_parser.add_argument(
        "--file",
        type=Path,
        required=True,
        help="UTF-8 Markdown body file containing real newlines",
    )
    return command_parser


def main() -> int:
    args = parser().parse_args()
    emit_payload(args.file)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
