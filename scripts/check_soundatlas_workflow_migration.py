"""Check the temporary SoundAtlas workflow-migration skill contract."""

from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

SUPPORTED_MIGRATION_ISSUES = (247, 248, 249, 250, 251)
SKILL_PATH = Path(".codex/skills/soundatlas-workflow-migration/SKILL.md")
MANIFEST_PATH = Path(".codex/skills/soundatlas-workflow-migration/agents/openai.yaml")
WORKFLOW_REGISTRY_PATH = Path("docs/workflow-registry.md")
WORKFLOW_REGISTRY_ROUTE = "../../../docs/workflow-registry.md#decision-and-planning-composition"
UX_PROMPT_PATH = Path("prompts/design-ux.md")
UX_PROMPT_ROUTES = (
    "[UX workflow](../docs/design/ux-workflow.md)",
    "[workflow routing](../docs/workflow-registry.md)",
    "[Issue lifecycle](../docs/github-issue-workflow.md)",
)
SKILLS_ROOT = Path(".codex/skills")
DEFAULT_PROMPT_PATTERN = re.compile(r"(?m)^[ \t]*default_prompt:[ \t]*(['\"])(.*?)\1[ \t]*$")

SUPPORTED_THEME_ROWS = {
    247: "| #247 | bounded decision/planning consolidation |",
    248: "| #248 | implementation and review entrypoints |",
    249: "| #249 | deterministic test entrypoints |",
    250: "| #250 | [commit and delivery entrypoints](../../../docs/workflow-registry.md#commit-and-delivery-composition) |",
    251: "| #251 | domain and compatibility entrypoints |",
}

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
    "Local runtime plans",
    "cannot authorize",
    "SoundAtlas defines required capabilities, outcomes",
    "The active environment chooses suitable providers,",
    "Ordinary repository/GitHub tools may fulfil",
    "Different methods may",
    "without requiring fabricated Pane evidence for ordinary-tools execution",
    "Absence of a named Pane skill alone",
    WORKFLOW_REGISTRY_ROUTE,
)
FORBIDDEN_PROCEDURE_HEADINGS = (
    "## Pane Procedure",
    "### Pane Procedure",
    "## Generic Pane Procedure",
)
FORBIDDEN_PROVIDER_DEFAULTS = (
    "Pane is the default provider",
    "Pane is the preferred provider",
    "Pane is the canonical provider",
    "Pane owns generic workflow",
)


def validate_supported_theme(issue_number: int) -> list[str]:
    if issue_number not in SUPPORTED_MIGRATION_ISSUES:
        return [
            f"unsupported migration Issue #{issue_number}; expected one of "
            + ", ".join(f"#{number}" for number in SUPPORTED_MIGRATION_ISSUES)
        ]
    return []


def find_manifest_errors(root: Path) -> list[str]:
    """Check that each active discovery manifest resolves to its sibling skill."""

    errors: list[str] = []
    manifests = sorted((root / SKILLS_ROOT).glob("*/agents/openai.yaml"))
    if not manifests:
        return [f"{SKILLS_ROOT}: no skill discovery manifests were found"]

    for manifest in manifests:
        skill_dir = manifest.parents[1]
        skill_path = skill_dir / "SKILL.md"
        relative_manifest = manifest.relative_to(root)
        if not skill_path.is_file():
            errors.append(f"{relative_manifest}: same-directory SKILL.md is missing")
            continue
        text = manifest.read_text(encoding="utf-8")
        default_prompt = DEFAULT_PROMPT_PATTERN.search(text)
        if not default_prompt:
            errors.append(f"{relative_manifest}: default_prompt is missing or malformed")
        elif f"${skill_dir.name}" not in default_prompt.group(2):
            errors.append(
                f"{relative_manifest}: default prompt does not invoke its same-directory skill"
            )
    return errors


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
        row = SUPPORTED_THEME_ROWS[issue]
        if row not in skill:
            errors.append(f"{SKILL_PATH}: missing or stale supported theme row for #{issue}")
    for heading in FORBIDDEN_PROCEDURE_HEADINGS:
        if heading in skill:
            errors.append(f"{SKILL_PATH}: copied Pane procedure heading {heading!r}")
    for marker in FORBIDDEN_PROVIDER_DEFAULTS:
        if marker.casefold() in skill.casefold():
            errors.append(f"{SKILL_PATH}: universal provider default is forbidden: {marker!r}")

    errors.extend(find_manifest_errors(root))

    prompt_path = root / UX_PROMPT_PATH
    if not prompt_path.is_file():
        errors.append(f"{UX_PROMPT_PATH}: canonical UX compatibility prompt is missing")
    else:
        prompt = prompt_path.read_text(encoding="utf-8")
        for route in UX_PROMPT_ROUTES:
            if route not in prompt:
                errors.append(f"{UX_PROMPT_PATH}: missing canonical authority route {route!r}")

    route_target = (
        root / SKILL_PATH.parent / Path(WORKFLOW_REGISTRY_ROUTE.split("#", 1)[0])
    ).resolve()
    expected_target = (root / WORKFLOW_REGISTRY_PATH).resolve()
    if route_target != expected_target or not route_target.is_file():
        errors.append(f"{SKILL_PATH}: workflow-registry authority route does not resolve")
    else:
        registry = route_target.read_text(encoding="utf-8")
        if "## Decision and planning composition" not in registry:
            errors.append(f"{SKILL_PATH}: workflow-registry authority fragment is missing")

    if "#203" not in manifest or "sunset" not in manifest.lower():
        errors.append(f"{MANIFEST_PATH}: missing explicit #203 sunset marker")
    return errors


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=Path(__file__).resolve().parents[1])
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
