"""Check the temporary SoundAtlas workflow-migration skill contract."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

SUPPORTED_MIGRATION_ISSUES = (247, 248, 249, 250, 251)
SKILL_PATH = Path(".codex/skills/soundatlas-workflow-migration/SKILL.md")
MANIFEST_PATH = Path(".codex/skills/soundatlas-workflow-migration/agents/openai.yaml")

REQUIRED_SKILL_SECTIONS = (
    "## Required context",
    "## Supported migration themes",
    "## Composition procedure",
    "## Per-slice migration record",
    "## Fail-closed stops and destinations",
    "## Non-Pane path",
    "## Sunset",
)
REQUIRED_MARKERS = (
    "#200 Inventory and Migration Map",
    "#246 composition contract",
    "#202 representative-evaluation handoff",
    "Issue #203 owns removal",
    "Local Pane plans",
    "separate Pane capability ticket",
    "cannot authorize",
)
FORBIDDEN_PROCEDURE_HEADINGS = (
    "## Pane Procedure",
    "### Pane Procedure",
    "## Generic Pane Procedure",
)


def validate_supported_theme(issue_number: int) -> list[str]:
    if issue_number not in SUPPORTED_MIGRATION_ISSUES:
        return [
            f"unsupported migration Issue #{issue_number}; expected one of "
            + ", ".join(f"#{number}" for number in SUPPORTED_MIGRATION_ISSUES)
        ]
    return []


def find_errors(root: Path, issue_number: int | None = None) -> list[str]:
    errors: list[str] = []
    if issue_number is not None:
        errors.extend(validate_supported_theme(issue_number))

    skill_path = root / SKILL_PATH
    manifest_path = root / MANIFEST_PATH
    if not skill_path.is_file():
        errors.append(f"{SKILL_PATH}: required temporary skill is missing")
        return errors
    if not manifest_path.is_file():
        errors.append(f"{MANIFEST_PATH}: discovery manifest is missing")
        return errors

    skill = skill_path.read_text(encoding="utf-8")
    manifest = manifest_path.read_text(encoding="utf-8")
    for section in REQUIRED_SKILL_SECTIONS:
        if section not in skill:
            errors.append(f"{SKILL_PATH}: missing required section {section!r}")
    for marker in REQUIRED_MARKERS:
        if marker not in skill:
            errors.append(f"{SKILL_PATH}: missing required marker {marker!r}")
    for issue in SUPPORTED_MIGRATION_ISSUES:
        if f"#{issue}" not in skill:
            errors.append(f"{SKILL_PATH}: missing supported theme #{issue}")
    for heading in FORBIDDEN_PROCEDURE_HEADINGS:
        if heading in skill:
            errors.append(f"{SKILL_PATH}: copied Pane procedure heading {heading!r}")
    if "#203" not in manifest or "sunset" not in manifest.lower():
        errors.append(f"{MANIFEST_PATH}: missing explicit #203 sunset marker")
    return errors


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--root", type=Path, default=Path(__file__).resolve().parents[1]
    )
    parser.add_argument("--theme", type=int, help="validate one supported child Issue")
    args = parser.parse_args()
    errors = find_errors(args.root.resolve(), args.theme)
    if errors:
        print("\n".join(errors))
        return 1
    print("SoundAtlas workflow-migration skill contract is valid.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
