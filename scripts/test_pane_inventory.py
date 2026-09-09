"""Deterministic contract tests for the read-only Pane inventory helper."""

from __future__ import annotations

import json
import os
import subprocess
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
HELPER = ROOT / ".devcontainer" / "pane-inventory.sh"


class PaneInventoryTests(unittest.TestCase):
    def run_helper(
        self, payload: object, *arguments: str, runpane_exit: int = 0
    ) -> tuple[subprocess.CompletedProcess[str], str]:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            bin_dir = root / "bin"
            bin_dir.mkdir()
            call_log = root / "runpane.log"
            payload_path = root / "payload.json"
            payload_path.write_text(json.dumps(payload), encoding="utf-8")
            runpane = bin_dir / "runpane"
            runpane.write_text(
                "#!/usr/bin/env bash\n"
                "printf '%s|%s\\n' \"${PANE_DIR:-}\" \"$*\" >> \"$CALL_LOG\"\n"
                "if [ \"${RUNPANE_EXIT:-0}\" -ne 0 ]; then exit \"$RUNPANE_EXIT\"; fi\n"
                "cat \"$RUNPANE_PAYLOAD\"\n",
                encoding="utf-8",
            )
            runpane.chmod(0o755)
            environment = {
                "PATH": f"{bin_dir}{os.pathsep}{os.environ['PATH']}",
                "CALL_LOG": str(call_log),
                "RUNPANE_EXIT": str(runpane_exit),
                "RUNPANE_PAYLOAD": str(payload_path),
            }
            result = subprocess.run(
                ["bash", str(HELPER), *arguments],
                env=environment,
                capture_output=True,
                text=True,
                check=False,
            )
            calls = call_log.read_text(encoding="utf-8") if call_log.exists() else ""
            return result, calls

    @staticmethod
    def payload(*panes: dict[str, object]) -> dict[str, object]:
        return {"ok": True, "panes": list(panes)}

    @staticmethod
    def pane(*, name: str = "issue-222", pane_id: str = "pane-222") -> dict[str, object]:
        return {
            "id": pane_id,
            "paneId": pane_id,
            "name": name,
            "repoName": "soundatlas",
            "worktreePath": f"/runtime/repos/soundatlas/worktrees/{name}",
            "status": "stopped",
            "agentStatus": "idle",
            "panelCount": 4,
        }

    def assert_read_only_list_call(self, calls: str) -> None:
        self.assertEqual(calls, "/runtime/pane|panes list --repo soundatlas --json\n")

    def test_resolves_exact_name_and_emits_only_bounded_identity(self):
        pane = self.pane()
        result, calls = self.run_helper(self.payload(pane), "--pane", "issue-222")

        self.assertEqual(result.returncode, 0, result.stderr)
        self.assert_read_only_list_call(calls)
        self.assertEqual(
            json.loads(result.stdout),
            {
                "pane_id": "pane-222",
                "pane_name": "issue-222",
                "repo_name": "soundatlas",
                "worktree_path": "/runtime/repos/soundatlas/worktrees/issue-222",
            },
        )
        self.assertNotIn("agentStatus", result.stdout)
        self.assertNotIn("panelCount", result.stdout)

    def test_resolves_exact_id(self):
        result, calls = self.run_helper(self.payload(self.pane()), "--pane", "pane-222")

        self.assertEqual(result.returncode, 0, result.stderr)
        self.assert_read_only_list_call(calls)
        self.assertEqual(json.loads(result.stdout)["pane_name"], "issue-222")

    def test_rejects_missing_ambiguous_and_malformed_inventory(self):
        cases = [
            (self.payload(), "No Pane matched"),
            (self.payload(self.pane(), self.pane()), "ambiguous"),
            ([], "response was unsuccessful"),
            ({"ok": True, "panes": "not-a-list"}, "did not contain a Pane list"),
        ]
        for payload, message in cases:
            with self.subTest(message=message):
                result, calls = self.run_helper(payload, "--pane", "issue-222")
                self.assertNotEqual(result.returncode, 0)
                self.assertEqual(result.stdout, "")
                self.assertIn(message, result.stderr)
                self.assert_read_only_list_call(calls)

    def test_rejects_unavailable_runpane_without_raw_diagnostics(self):
        result, calls = self.run_helper(
            self.payload(self.pane()), "--pane", "issue-222", runpane_exit=1
        )

        self.assertNotEqual(result.returncode, 0)
        self.assertEqual(result.stdout, "")
        self.assertIn("Pane inventory is unavailable", result.stderr)
        self.assert_read_only_list_call(calls)

    def test_requires_one_pane_selector(self):
        result, calls = self.run_helper(self.payload(self.pane()))

        self.assertEqual(result.returncode, 2)
        self.assertIn("Usage:", result.stderr)
        self.assertEqual(calls, "")


if __name__ == "__main__":
    unittest.main()
