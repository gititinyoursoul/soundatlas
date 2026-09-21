from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

from scripts.check_workflow_composition import (
    CONTRACT_HEADING,
    EXPECTED_MARKERS,
    find_contract_errors,
)


class WorkflowCompositionCheckTests(unittest.TestCase):
    def make_root(self) -> Path:
        temporary = tempfile.TemporaryDirectory()
        self.addCleanup(temporary.cleanup)
        root = Path(temporary.name)
        for relative_path, markers in EXPECTED_MARKERS.items():
            target = root / relative_path
            target.parent.mkdir(parents=True, exist_ok=True)
            lines = list(markers)
            if relative_path == Path("docs/workflow-registry.md"):
                lines.insert(0, CONTRACT_HEADING)
            target.write_text("\n".join(lines) + "\n", encoding="utf-8")
        return root

    def test_valid_contract(self) -> None:
        self.assertEqual(find_contract_errors(self.make_root()), [])

    def test_missing_authority_is_reported(self) -> None:
        root = self.make_root()
        (root / "AGENTS.md").unlink()

        errors = find_contract_errors(root)

        self.assertIn("AGENTS.md: required composition authority is missing", errors)

    def test_duplicate_contract_heading_is_reported(self) -> None:
        root = self.make_root()
        registry = root / "docs/workflow-registry.md"
        registry.write_text(
            registry.read_text(encoding="utf-8") + CONTRACT_HEADING + "\n",
            encoding="utf-8",
        )

        errors = find_contract_errors(root)

        self.assertTrue(any("found 2" in error for error in errors))

    def test_missing_route_marker_is_reported(self) -> None:
        root = self.make_root()
        relative_path = Path("docs/github-issue-workflow.md")
        lifecycle = root / relative_path
        missing = EXPECTED_MARKERS[relative_path][0]
        lifecycle.write_text(
            lifecycle.read_text(encoding="utf-8").replace(missing, ""),
            encoding="utf-8",
        )

        errors = find_contract_errors(root)

        self.assertTrue(any(repr(missing) in error for error in errors))

    def test_missing_canonical_boundary_is_reported(self) -> None:
        root = self.make_root()
        registry = root / "docs/workflow-registry.md"
        missing = "Local or temporary Pane planning artifacts are non-authoritative."
        registry.write_text(
            registry.read_text(encoding="utf-8").replace(missing, ""),
            encoding="utf-8",
        )

        errors = find_contract_errors(root)

        self.assertTrue(any(repr(missing) in error for error in errors))


if __name__ == "__main__":
    unittest.main()
