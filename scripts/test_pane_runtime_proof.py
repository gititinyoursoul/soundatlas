"""Static contracts for the pinned isolated Pane runtime."""
from __future__ import annotations

import json
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
RUNTIME = ROOT / "vendor" / "pane-dev-runtime"


class PaneRuntimeProofTests(unittest.TestCase):
    def test_isolated_surface_is_complete(self) -> None:
        expected = {".dockerignore", "Dockerfile", "egress.Dockerfile", "compose.yaml", "bin/runtime-entrypoint.sh", "bin/runtime-status.sh", "bin/attach-repository.sh", "bin/egress-guard.sh", "config/pane-seccomp.json", "config/sshd_config", "tests/contract.sh", "tests/smoke.sh", "README.md"}
        actual = {
            path.relative_to(RUNTIME).as_posix()
            for path in RUNTIME.rglob("*")
            if path.is_file() and path.name != ".git"
        }
        self.assertEqual(actual, expected)

    def test_generic_sources_have_no_project_assumptions(self) -> None:
        prohibited = ("soundatlas", "postgres", "dbt", "openrouter", "ollama", "github-agent")
        for path in RUNTIME.rglob("*"):
            if not path.is_file() or path.name in {".git", "README.md", "contract.sh"}:
                continue
            with self.subTest(path=path):
                self.assertFalse(any(token in path.read_text(encoding="utf-8").lower() for token in prohibited))

    def test_compose_is_generic_and_isolated(self) -> None:
        compose = (RUNTIME / "compose.yaml").read_text(encoding="utf-8")
        self.assertIn("  runtime:\n", compose)
        self.assertIn("  egress:\n", compose)
        self.assertIn("network_mode: service:egress", compose)
        self.assertNotIn("backend:", compose)
        self.assertNotIn("frontend:", compose)

    def test_attachment_rejects_dirty_or_ambiguous_repositories(self) -> None:
        script = (RUNTIME / "bin/attach-repository.sh").read_text(encoding="utf-8")
        self.assertIn("status --porcelain=v1", script)
        self.assertIn("repository is dirty", script)
        self.assertIn("repository root is ambiguous", script)

    def test_smoke_creates_one_pane_owned_worktree(self) -> None:
        smoke = (RUNTIME / "tests/smoke.sh").read_text(encoding="utf-8")
        self.assertIn("runpane panes create", smoke)
        self.assertIn("--source agent", smoke)
        self.assertIn("runpane panes list", smoke)

    def test_soundatlas_extension_is_separate(self) -> None:
        extension = (ROOT / ".devcontainer/pane-soundatlas.Dockerfile").read_text(encoding="utf-8")
        overlay = (ROOT / ".devcontainer/docker-compose.pane-runtime-proof.yml").read_text(encoding="utf-8")
        self.assertIn("ARG PANE_RUNTIME_BASE_IMAGE", extension)
        self.assertIn("FROM ${PANE_RUNTIME_BASE_IMAGE}", extension)
        self.assertIn("soundatlas-pane-runtime-proof:phase1", overlay)
        self.assertNotIn("backend:", overlay)
        self.assertNotIn("/runtime/repos", overlay)

    def test_seccomp_profile_is_json(self) -> None:
        self.assertEqual(json.loads((RUNTIME / "config/pane-seccomp.json").read_text())["defaultAction"], "SCMP_ACT_ERRNO")


if __name__ == "__main__":
    unittest.main()
