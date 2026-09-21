from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

from scripts.check_soundatlas_workflow_migration import (
    MANIFEST_PATH,
    REQUIRED_MARKERS,
    REQUIRED_SKILL_SECTIONS,
    SKILL_PATH,
    find_errors,
    validate_supported_theme,
)


class WorkflowMigrationCheckTests(unittest.TestCase):
    def make_root(self) -> Path:
        temporary = tempfile.TemporaryDirectory()
        self.addCleanup(temporary.cleanup)
        root = Path(temporary.name)
        skill = root / SKILL_PATH
        skill.parent.mkdir(parents=True, exist_ok=True)
        skill.write_text(
            "\n".join(
                (
                    *REQUIRED_SKILL_SECTIONS,
                    *REQUIRED_MARKERS,
                    "#247 #248 #249 #250 #251",
                )
            ),
            encoding="utf-8",
        )
        manifest = root / MANIFEST_PATH
        manifest.parent.mkdir(parents=True, exist_ok=True)
        manifest.write_text("sunset #203\n", encoding="utf-8")
        return root

    def test_valid_contract_and_theme(self) -> None:
        self.assertEqual(find_errors(self.make_root(), 247), [])

    def test_unsupported_theme_is_rejected(self) -> None:
        self.assertTrue(validate_supported_theme(246))
        self.assertEqual(validate_supported_theme(251), [])

    def test_missing_output_marker_is_reported(self) -> None:
        root = self.make_root()
        skill = root / SKILL_PATH
        skill.write_text(
            skill.read_text(encoding="utf-8").replace(REQUIRED_MARKERS[2], ""),
            encoding="utf-8",
        )
        errors = find_errors(root)
        self.assertTrue(
            any("#202 representative-evaluation handoff" in error for error in errors)
        )

    def test_copied_pane_procedure_heading_is_rejected(self) -> None:
        root = self.make_root()
        skill = root / SKILL_PATH
        skill.write_text(
            skill.read_text(encoding="utf-8") + "\n## Pane Procedure\n",
            encoding="utf-8",
        )
        errors = find_errors(root)
        self.assertTrue(any("copied Pane procedure" in error for error in errors))

    def test_missing_sunset_manifest_is_reported(self) -> None:
        root = self.make_root()
        (root / MANIFEST_PATH).write_text("temporary skill\n", encoding="utf-8")
        errors = find_errors(root)
        self.assertTrue(any("sunset" in error for error in errors))


if __name__ == "__main__":
    unittest.main()
