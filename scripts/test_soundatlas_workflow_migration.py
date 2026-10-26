from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

from scripts.check_soundatlas_workflow_migration import (
    MANIFEST_PATH,
    REQUIRED_MARKERS,
    REQUIRED_SKILL_SECTIONS,
    SKILL_PATH,
    SUPPORTED_THEME_ROWS,
    UX_PROMPT_PATH,
    UX_PROMPT_ROUTES,
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
                    *SUPPORTED_THEME_ROWS.values(),
                )
            ),
            encoding="utf-8",
        )
        registry = root / "docs/workflow-registry.md"
        registry.parent.mkdir(parents=True, exist_ok=True)
        registry.write_text("## Decision and planning composition\n", encoding="utf-8")
        manifest = root / MANIFEST_PATH
        manifest.parent.mkdir(parents=True, exist_ok=True)
        manifest.write_text(
            'interface:\n  default_prompt: "Use $soundatlas-workflow-migration; sunset #203"\n',
            encoding="utf-8",
        )
        prompt = root / UX_PROMPT_PATH
        prompt.parent.mkdir(parents=True, exist_ok=True)
        prompt.write_text("\n".join(UX_PROMPT_ROUTES) + "\n", encoding="utf-8")
        return root

    def test_valid_contract_and_theme(self) -> None:
        root = self.make_root()
        for theme in (247, 248, 249, 250, 251):
            with self.subTest(theme=theme):
                self.assertEqual(find_errors(root, theme), [])

    def test_unsupported_theme_is_rejected(self) -> None:
        for theme in (246, 252, 281):
            with self.subTest(theme=theme):
                self.assertTrue(validate_supported_theme(theme))
        self.assertEqual(validate_supported_theme(251), [])

    def test_missing_output_marker_is_reported(self) -> None:
        root = self.make_root()
        skill = root / SKILL_PATH
        skill.write_text(
            skill.read_text(encoding="utf-8").replace(REQUIRED_MARKERS[2], ""),
            encoding="utf-8",
        )
        errors = find_errors(root)
        self.assertTrue(any("#202 representative-evaluation handoff" in error for error in errors))

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

    def test_stale_migration_theme_row_is_reported(self) -> None:
        root = self.make_root()
        skill = root / SKILL_PATH
        skill.write_text(
            skill.read_text(encoding="utf-8").replace(SUPPORTED_THEME_ROWS[248], ""),
            encoding="utf-8",
        )

        errors = find_errors(root)

        self.assertTrue(any("supported theme row for #248" in error for error in errors))

    def test_universal_pane_default_is_reported(self) -> None:
        root = self.make_root()
        skill = root / SKILL_PATH
        skill.write_text(
            skill.read_text(encoding="utf-8") + "\nPane is the default provider.\n",
            encoding="utf-8",
        )

        errors = find_errors(root)

        self.assertTrue(any("universal provider default" in error for error in errors))

    def test_missing_registry_fragment_is_reported(self) -> None:
        root = self.make_root()
        registry = root / "docs/workflow-registry.md"
        registry.write_text("## Other section\n", encoding="utf-8")

        errors = find_errors(root)

        self.assertTrue(any("authority fragment is missing" in error for error in errors))

    def test_missing_registry_target_is_reported(self) -> None:
        root = self.make_root()
        (root / "docs/workflow-registry.md").unlink()

        errors = find_errors(root)

        self.assertTrue(any("authority route does not resolve" in error for error in errors))

    def test_manifest_must_invoke_the_migration_skill(self) -> None:
        root = self.make_root()
        manifest = root / MANIFEST_PATH
        manifest.write_text(
            'interface:\n  default_prompt: "Use $soundatlas-other"\n  # sunset #203\n',
            encoding="utf-8",
        )

        errors = find_errors(root)

        self.assertTrue(
            any("does not invoke its same-directory skill" in error for error in errors)
        )

    def test_all_manifests_must_resolve_to_their_same_directory_skill(self) -> None:
        root = self.make_root()
        manifest = root / ".codex/skills/soundatlas-extra/agents/openai.yaml"
        manifest.parent.mkdir(parents=True, exist_ok=True)
        manifest.write_text(
            'interface:\n  default_prompt: "Use $soundatlas-other"\n',
            encoding="utf-8",
        )
        (manifest.parents[1] / "SKILL.md").write_text("skill\n", encoding="utf-8")

        errors = find_errors(root)

        self.assertTrue(
            any(
                "default prompt does not invoke its same-directory skill" in error
                for error in errors
            )
        )

    def test_manifest_comment_cannot_stand_in_for_default_prompt(self) -> None:
        root = self.make_root()
        manifest = root / MANIFEST_PATH
        manifest.write_text(
            "interface:\n  # use $soundatlas-workflow-migration\n"
            '  default_prompt: "Use $soundatlas-other"\n'
            "  # sunset #203\n",
            encoding="utf-8",
        )

        errors = find_errors(root)

        self.assertTrue(
            any("does not invoke its same-directory skill" in error for error in errors)
        )

    def test_ux_prompt_must_keep_its_canonical_authority_routes(self) -> None:
        root = self.make_root()
        prompt = root / UX_PROMPT_PATH
        prompt.write_text("\n".join(UX_PROMPT_ROUTES[:-1]) + "\n", encoding="utf-8")

        errors = find_errors(root)

        self.assertTrue(any("missing canonical authority route" in error for error in errors))


if __name__ == "__main__":
    unittest.main()
