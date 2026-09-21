"""Check the tracked Pane–SoundAtlas composition routing contract."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

CONTRACT_HEADING = "## Pane–SoundAtlas Composition Contract"

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
    ),
    Path("docs/github-issue-workflow.md"): (
        "`docs/workflow-registry.md` owns the Pane–SoundAtlas composition contract.",
        "Local or temporary Pane planning artifacts are non-authoritative.",
        "Only the latest valid GitHub Issue Plan and its later matching",
    ),
}


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
        heading_count = sum(
            line.strip() == CONTRACT_HEADING for line in registry.splitlines()
        )
        if heading_count != 1:
            errors.append(
                f"{registry_path}: expected exactly one {CONTRACT_HEADING!r} "
                f"heading, found {heading_count}"
            )

    for relative_path, markers in EXPECTED_MARKERS.items():
        text = contents.get(relative_path)
        if text is None:
            continue
        for marker in markers:
            if marker not in text:
                errors.append(
                    f"{relative_path}: missing composition routing marker {marker!r}"
                )

    return errors


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--root", type=Path, default=Path(__file__).resolve().parents[1]
    )
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
