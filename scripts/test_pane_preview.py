"""Deterministic contract checks for the Pane-worktree browser preview helper."""

from __future__ import annotations

import json
import os
import subprocess
import tempfile
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

    def test_reads_the_single_bounded_inventory_result(self):
        pane = {
            "pane_id": "one",
            "pane_name": "alpha",
            "repo_name": "soundatlas",
            "worktree_path": "/runtime/repos/soundatlas/worktrees/alpha",
        }
        selected = self.source_function("select_pane", input_text=json.dumps(pane))
        self.assertEqual(selected.returncode, 0, selected.stderr)
        self.assertEqual(selected.stdout.strip().split("\t")[:2], ["one", "alpha"])

        invalid = self.source_function("select_pane", input_text=json.dumps([]))
        self.assertNotEqual(invalid.returncode, 0)
        self.assertIn("did not return an object", invalid.stderr)

    def test_falls_back_to_python_when_python3_is_unusable(self):
        with tempfile.TemporaryDirectory() as temporary_directory:
            temporary = Path(temporary_directory)
            unusable_python3 = temporary / "python3"
            unusable_python3.write_text("#!/usr/bin/env bash\nexit 1\n", encoding="utf-8")
            unusable_python3.chmod(0o755)

            environment = os.environ.copy()
            environment["PATH"] = str(temporary) + os.pathsep + environment["PATH"]
            result = subprocess.run(
                [
                    "bash",
                    "-c",
                    'source "$1"; resolve_python; printf "%s" "$PYTHON_COMMAND"',
                    "pane-preview-test",
                    str(SCRIPT),
                ],
                capture_output=True,
                text=True,
                check=False,
                env=environment,
            )

            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertEqual(result.stdout, "python")

    def test_uses_separate_diagnostics_logs_for_vite_and_tunnel(self):
        command = 'source "$1"; create_diagnostics_logs; printf "%s\\n%s\\n" "$VITE_LOG_FILE" "$TUNNEL_LOG_FILE"'
        result = subprocess.run(
            ["bash", "-c", command, "pane-preview-test", str(SCRIPT)],
            capture_output=True,
            text=True,
            check=False,
        )

        self.assertEqual(result.returncode, 0, result.stderr)
        vite_log, tunnel_log = result.stdout.splitlines()
        self.assertNotEqual(vite_log, tunnel_log)
        self.assertIn("pane-preview-vite", vite_log)
        self.assertIn("pane-preview-tunnel", tunnel_log)
        self.assertTrue(Path(vite_log).is_file())
        self.assertTrue(Path(tunnel_log).is_file())
        Path(vite_log).unlink()
        Path(tunnel_log).unlink()

    def test_queries_inventory_over_ssh_without_running_runpane_locally(self):
        with tempfile.TemporaryDirectory() as temporary_directory:
            temporary = Path(temporary_directory)
            key = temporary / "pane-key"
            ssh_log = temporary / "ssh.log"
            key.write_text("test-only\n", encoding="utf-8")

            pane_json = json.dumps({
                "pane_id": "pane-id",
                "pane_name": "preview-pane",
                "repo_name": "soundatlas",
                "worktree_path": "/runtime/repos/soundatlas/worktrees/preview-pane",
            })
            command = r'''
source "$1"
shift
ssh() {
  printf '%s\n' "$*" >>"$SSH_LOG"
  if [[ "$*" == *"soundatlas-pane-inventory --pane preview-pane"* ]]; then
    printf '%s\n' "$PANE_JSON"
    return 0
  fi
  if [[ "$*" == *"rev-parse --is-inside-work-tree"* ]]; then
    printf '%s\n' 'issue-220-worktree-browser-preview' '01a10e3' 'clean'
    return 0
  fi
  return 1
}
main --pane preview-pane --mode static --ssh-key "$TEST_KEY"
'''
            environment = os.environ.copy()
            environment.update({
                "PANE_JSON": pane_json,
                "SSH_LOG": str(ssh_log),
                "TEST_KEY": str(key),
            })
            result = subprocess.run(
                ["bash", "-c", command, "pane-preview-test", str(SCRIPT)],
                capture_output=True,
                text=True,
                check=False,
                env=environment,
            )

            self.assertNotEqual(result.returncode, 0)
            self.assertIn("Vite dependencies are unavailable", result.stderr)
            self.assertIn(
                "soundatlas-pane-inventory --pane preview-pane",
                ssh_log.read_text(encoding="utf-8"),
            )
            self.assertNotIn(
                "runpane panes list",
                ssh_log.read_text(encoding="utf-8"),
            )

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
