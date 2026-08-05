#!/usr/bin/env python3
"""Validate SoundAtlas Issue completion artifacts without mutating GitHub."""

from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path


REPORT_SECTIONS = (
    "## Summary",
    "## Verification",
    "## Acceptance Criteria Result",
    "## Review Result",
    "## Remaining Risks",
)
REVIEW_FIELDS = (
    "- Evidence coverage:",
    "- Findings and routing:",
    "- Documentation impact:",
)


class ValidationError(ValueError):
    """Raised when a completion artifact does not satisfy the local contract."""


def read_text(path: Path) -> str:
    try:
        return path.read_text(encoding="utf-8")
    except OSError as exc:
        raise ValidationError(f"cannot read {path}: {exc}") from exc


def section(text: str, heading: str) -> str:
    start = text.find(heading)
    if start < 0:
        raise ValidationError(f"missing required section: {heading}")
    remainder = text[start + len(heading) :]
    next_heading = remainder.find("\n## ")
    return remainder if next_heading < 0 else remainder[:next_heading]


def validate_report(text: str) -> None:
    missing = [heading for heading in REPORT_SECTIONS if heading not in text]
    if missing:
        raise ValidationError("missing required section(s): " + ", ".join(missing))

    acceptance = section(text, "## Acceptance Criteria Result")
    criteria = re.findall(r"^\s*- \[([ xX])\]", acceptance, re.MULTILINE)
    if not criteria:
        raise ValidationError("acceptance criteria result contains no checklist items")
    if any(mark.lower() != "x" for mark in criteria):
        raise ValidationError("all acceptance criteria must be checked for completion")

    review = section(text, "## Review Result")
    missing_review_fields = [field for field in REVIEW_FIELDS if field not in review]
    if missing_review_fields:
        raise ValidationError(
            "review result is missing field(s): " + ", ".join(missing_review_fields)
        )
    verdict = re.search(r"^\s*- Verdict:\s*(.+?)\s*$", review, re.MULTILINE)
    if not verdict:
        raise ValidationError("review result has no verdict")
    if verdict.group(1) != "Accepted":
        raise ValidationError(
            f"completion requires an Accepted review verdict, got {verdict.group(1)!r}"
        )


def validate_completion(
    report_path: Path,
    commit: str,
    completion_comments: int,
    working_tree_verified: bool,
) -> None:
    validate_report(read_text(report_path))
    if not re.fullmatch(r"[0-9a-fA-F]{7,40}", commit):
        raise ValidationError("commit must be a 7-40 character hexadecimal hash")
    if completion_comments != 1:
        raise ValidationError("exactly one standard completion comment is required")
    if not working_tree_verified:
        raise ValidationError("Issue-relevant working-tree verification is required")


def parser() -> argparse.ArgumentParser:
    command_parser = argparse.ArgumentParser(description=__doc__)
    subparsers = command_parser.add_subparsers(dest="command", required=True)

    report_parser = subparsers.add_parser("report", help="validate a report")
    report_parser.add_argument("--file", type=Path, required=True)

    completion_parser = subparsers.add_parser(
        "completion", help="validate all local completion prerequisites"
    )
    completion_parser.add_argument("--report", type=Path, required=True)
    completion_parser.add_argument("--commit", required=True)
    completion_parser.add_argument("--completion-comments", type=int, required=True)
    completion_parser.add_argument("--working-tree-verified", action="store_true")

    return command_parser


def main(argv: list[str] | None = None) -> int:
    args = parser().parse_args(argv)
    try:
        if args.command == "report":
            validate_report(read_text(args.file))
        else:
            validate_completion(
                args.report,
                args.commit,
                args.completion_comments,
                args.working_tree_verified,
            )
    except ValidationError as exc:
        print(f"Validation failed: {exc}", file=sys.stderr)
        return 1

    print("Validation passed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
