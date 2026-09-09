"""Deterministic contract checks for the Pane-worktree browser preview helper."""

from __future__ import annotations

import json
import subprocess
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SCRIPT = ROOT / "scripts" / "pane-preview.sh"
VITE_CONFIG = ROOT / "frontend" / "vite.config.ts"


class PanePreviewTests(unittest.TestCase):
    def run_script(self, *arguments: str, input_text: str = "") -> subprocess.CompletedProcess[str]:
        return subprocess.run(
            ["bash", str(SCRIPT), *arguments],
            input=input_text,
            capture_output=True,
            text=True,
            check=False,
        )

    def source_function(self, function: str, *arguments: str, input_text: str = "") -> subprocess.CompletedProcess[str]:
        command = "source \"$1\"; shift; " + function + ' "$@"'
        return subprocess.run(
            ["bash", "-c", command, "pane-preview-test", str(SCRIPT), *arguments],
            input=input_text,
            capture_output=True,
            text=True,
            check=False,
        )

    def test_help_and_mode_validation_are_actionable(self):
        help_result = self.run_script("--help")
        self.assertEqual(help_result.returncode, 0, help_result.stderr)
        self.assertIn("--pane NAME_OR_ID", help_result.stdout)

        invalid = self.run_script("--pane", "one", "--mode", "invalid")
        self.assertNotEqual(invalid.returncode, 0)
        self.assertIn("--mode must be api or static", invalid.stderr)

        incompatible = self.run_script("--pane", "one", "--mode", "static", "--editorial")
        self.assertNotEqual(incompatible.returncode, 0)
        self.assertIn("Editorial Mode requires --mode api", incompatible.stderr)

    def test_selects_an_exact_pane_and_rejects_ambiguous_or_missing_matches(self):
        panes = {
            "panes": [
                {"id": "one", "name": "alpha", "worktreePath": "/runtime/repos/soundatlas/worktrees/alpha"},
                {"id": "two", "name": "beta", "worktreePath": "/runtime/repos/soundatlas/worktrees/beta"},
            ]
        }
        selected = self.source_function("PANE_SELECTOR=one; select_pane", input_text=json.dumps(panes))
        self.assertEqual(selected.returncode, 0, selected.stderr)
        self.assertEqual(selected.stdout.strip().split("\t")[:2], ["one", "alpha"])

        ambiguous = self.source_function(
            "PANE_SELECTOR=shared; select_pane",
            input_text=json.dumps({"panes": [
                {"id": "one", "name": "shared", "worktreePath": "/one"},
                {"id": "two", "name": "shared", "worktreePath": "/two"},
            ]}),
        )
        self.assertNotEqual(ambiguous.returncode, 0)
        self.assertIn("ambiguous", ambiguous.stderr)

        missing = self.source_function("PANE_SELECTOR=missing; select_pane", input_text=json.dumps(panes))
        self.assertNotEqual(missing.returncode, 0)
        self.assertIn("No Pane matched", missing.stderr)

    def test_identity_snapshot_excludes_runtime_worktree_paths(self):
        result = self.source_function(
            "build_identity_json",
            "pane-id",
            "preview-pane",
            "issue-220",
            "abc1234",
            "dirty",
            "api",
            "true",
        )
        self.assertEqual(result.returncode, 0, result.stderr)
        snapshot = json.loads(result.stdout)
        self.assertEqual(snapshot["paneName"], "preview-pane")
        self.assertEqual(snapshot["worktreeState"], "dirty")
        self.assertNotIn("worktreePath", snapshot)

    def test_vite_identity_endpoint_is_explicitly_helper_gated(self):
        config = VITE_CONFIG.read_text(encoding="utf-8")
        self.assertIn("SOUNDATLAS_PANE_PREVIEW", config)
        self.assertIn("/__soundatlas/pane-preview", config)
        self.assertIn("configureServer", config)

    def test_api_mode_checks_the_browser_facing_backend_before_readiness(self):
        helper = SCRIPT.read_text(encoding="utf-8")
        self.assertIn("http://127.0.0.1:8000/health", helper)
        self.assertIn("Start the Compose backend", helper)


if __name__ == "__main__":
    unittest.main()
