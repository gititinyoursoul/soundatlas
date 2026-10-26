"""Check the tracked Pane–SoundAtlas composition routing contract."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

CONTRACT_HEADING = "## Pane–SoundAtlas Composition Contract"

DECISION_ROUTE = "../../../docs/workflow-registry.md#decision-and-planning-composition"
DECISION_ENTRIES = (
    "exploration",
    "defect investigation",
    "independent critique",
    "retained critique",
    "retained synthesis",
    "canonical composer",
    "planning",
    "drafting and review",
    "canonical records",
    "capability availability",
    "execution evidence",
)
DECISION_OWNERS = (
    Path(".codex/skills/soundatlas-grill-me/SKILL.md"),
    Path(".codex/skills/soundatlas-concept-work/SKILL.md"),
    Path(".codex/skills/soundatlas-issue-planning/SKILL.md"),
)
DECISION_SOURCES = (
    *DECISION_OWNERS,
    Path(".codex/skills/soundatlas-workflow-migration/SKILL.md"),
)

EXPECTED_MARKERS: dict[Path, tuple[str, ...]] = {
    Path("AGENTS.md"): (
        "For Pane-composed work, apply the Pane–SoundAtlas composition contract",
        "`docs/workflow-registry.md`",
        "Local Pane artifacts are not",
    ),
    Path("docs/workflow-registry.md"): (
        "`docs/github-issue-workflow.md` owns the lifecycle and canonical record shapes.",
        "The latest valid GitHub Issue Plan and its later matching",
        "Local or temporary Pane planning artifacts are non-authoritative.",
        "A contributor without Pane starts at `AGENTS.md`",
        "SoundAtlas defines the capabilities and evidence needed for correct work.",
        "runtime discovers available capabilities and chooses tools, skills, agents,",
        "These requirements apply independently of",
        "Ordinary repository/GitHub tools can fulfil",
        "Frontend, backend and documentation implementation use their retained skills",
        "the active environment selects suitable implementation procedure, tools,",
        "Ordinary repository/GitHub tools may fulfil the same",
        "When Pane is selected, apply the existing envelope, exact provenance, drift,",
        "without copying provider procedure. Without Pane,",
        "GAP-1..3 remain open for #202's representative evidence; textual requirements",
        "PR creation, rebase/integration, push, merge, publication, deployment, release,",
    ),
    Path("docs/github-issue-workflow.md"): (
        "`docs/workflow-registry.md` owns the Pane–SoundAtlas composition contract.",
        "Local or temporary Pane planning artifacts are non-authoritative.",
        "Only the latest valid GitHub Issue Plan and its later matching",
        "GitHub Issues are the source of truth for planned agent work.",
        "For non-trivial Issue work, one explicit human implementation request after the",
    ),
}

for owner in DECISION_SOURCES:
    EXPECTED_MARKERS[owner] = (DECISION_ROUTE,)


def find_contract_errors(root: Path) -> list[str]:
    """Return actionable structural routing errors under *root*."""

    errors: list[str] = []
    contents: dict[Path, str] = {}
    for relative_path in EXPECTED_MARKERS:
        source = root / relative_path
        if not source.is_file():
            errors.append(f"{relative_path}: required composition authority is missing")
            continue
        contents[relative_path] = source.read_text(encoding="utf-8")

    registry_path = Path("docs/workflow-registry.md")
    registry = contents.get(registry_path)
    if registry is not None:
        heading_count = sum(line.strip() == CONTRACT_HEADING for line in registry.splitlines())
        if heading_count != 1:
            errors.append(
                f"{registry_path}: expected exactly one {CONTRACT_HEADING!r} "
                f"heading, found {heading_count}"
            )

        for entry in DECISION_ENTRIES:
            if f"| {entry} |" not in registry:
                errors.append(f"{registry_path}: missing decision/planning entry {entry!r}")
        for owner in DECISION_OWNERS:
            if f"`{owner}`" not in registry:
                errors.append(f"{registry_path}: missing decision/planning owner {owner}")
        heading = "## Decision and planning composition"
        if registry.splitlines().count(heading) != 1:
            errors.append(f"{registry_path}: expected one {heading!r} heading")

    # Wiring only: no claim about semantics, Human authority or runtime equivalence.
    for relative_path in DECISION_SOURCES:
        text = contents.get(relative_path, "")
        if text.count(DECISION_ROUTE) > 1:
            errors.append(f"{relative_path}: duplicate decision/planning route")

    for relative_path, markers in EXPECTED_MARKERS.items():
        text = contents.get(relative_path)
        if text is None:
            continue
        for marker in markers:
            if marker not in text:
                errors.append(f"{relative_path}: missing composition routing marker {marker!r}")

    return errors


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=Path(__file__).resolve().parents[1])
    args = parser.parse_args()
    errors = find_contract_errors(args.root.resolve())
    if errors:
        for error in errors:
            print(error)
        return 1
    print("Pane–SoundAtlas composition routing is valid.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
