"""Deterministic checks for Pane launch-time Git credential provisioning."""

from __future__ import annotations

import os
import subprocess
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
ENTRYPOINT = ROOT / ".devcontainer" / "pane-entrypoint.sh"
DUMMY_TOKEN = "dummy-pane-agent-token"


class PaneEntrypointTests(unittest.TestCase):
    def credential_file(self, directory: str, content: str) -> Path:
        path = Path(directory) / "github-agent.env"
        path.write_text(content, encoding="utf-8")
        return path

    def run_loader(
        self, credential_path: Path | None, *, extra_env: dict[str, str] | None = None
    ) -> subprocess.CompletedProcess[str]:
        with tempfile.TemporaryDirectory() as home:
            environment = {
                "HOME": home,
                "PATH": os.environ["PATH"],
            }
            if credential_path is not None:
                environment["SOUNDATLAS_GITHUB_AGENT_ENV_FILE"] = str(credential_path)
            if extra_env:
                environment.update(extra_env)
            git_config_count = environment.get("GIT_CONFIG_COUNT", "0")
            expected_count = (
                str(int(git_config_count) + 1) if git_config_count.isdigit() else ""
            )
            probe = r'''
source "$1"
load_repository_git_credentials || exit $?
test "${GH_TOKEN:-}" = "$EXPECTED_TOKEN"
test "${GITHUB_TOKEN+x}" != x
test "$GIT_CONFIG_COUNT" = "$EXPECTED_CONFIG_COUNT"
test "${!EXPECTED_CONFIG_KEY}" = credential.helper
test "${!EXPECTED_CONFIG_VALUE}" = '!gh auth git-credential'
if [ -n "${ORIGINAL_CONFIG_KEY:-}" ]; then
  test "${!ORIGINAL_CONFIG_KEY}" = "$ORIGINAL_CONFIG_VALUE"
fi
bash -c 'test "$GH_TOKEN" = "$EXPECTED_TOKEN"; test "$GIT_CONFIG_COUNT" = "$EXPECTED_CONFIG_COUNT"'
env -u GIT_CONFIG_COUNT -u "${EXPECTED_CONFIG_KEY}" -u "${EXPECTED_CONFIG_VALUE}" \
  git config --global --get-all credential.helper >/dev/null && exit 1 || true
'''
            environment.update(
                {
                    "EXPECTED_TOKEN": DUMMY_TOKEN,
                    "EXPECTED_CONFIG_COUNT": expected_count,
                    "EXPECTED_CONFIG_KEY": f"GIT_CONFIG_KEY_{git_config_count}",
                    "EXPECTED_CONFIG_VALUE": f"GIT_CONFIG_VALUE_{git_config_count}",
                }
            )
            return subprocess.run(
                ["bash", "-c", probe, "pane-entrypoint-test", str(ENTRYPOINT)],
                env=environment,
                capture_output=True,
                text=True,
                check=False,
            )

    def test_loads_repository_credential_and_process_scoped_helper(self):
        with tempfile.TemporaryDirectory() as directory:
            result = self.run_loader(
                self.credential_file(directory, f"GH_TOKEN={DUMMY_TOKEN}\n")
            )

        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertNotIn(DUMMY_TOKEN, result.stdout + result.stderr)

    def test_preserves_existing_environment_backed_git_configuration(self):
        with tempfile.TemporaryDirectory() as directory:
            result = self.run_loader(
                self.credential_file(directory, f"GH_TOKEN={DUMMY_TOKEN}\n"),
                extra_env={
                    "GIT_CONFIG_COUNT": "1",
                    "GIT_CONFIG_KEY_0": "core.filemode",
                    "GIT_CONFIG_VALUE_0": "false",
                    "ORIGINAL_CONFIG_KEY": "GIT_CONFIG_KEY_0",
                    "ORIGINAL_CONFIG_VALUE": "core.filemode",
                },
            )

        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertNotIn(DUMMY_TOKEN, result.stdout + result.stderr)

    def test_rejects_missing_malformed_empty_and_duplicate_inputs_without_echoing(self):
        cases = [
            (None, ""),
            ("OTHER_TOKEN=" + DUMMY_TOKEN + "\n", ""),
            ("GH_TOKEN=\n", ""),
            (f"GH_TOKEN={DUMMY_TOKEN}\nGH_TOKEN=second\n", ""),
        ]
        for content, _ in cases:
            with self.subTest(content=content), tempfile.TemporaryDirectory() as directory:
                credential_path = (
                    None if content is None else self.credential_file(directory, content)
                )
                result = self.run_loader(credential_path)

            self.assertNotEqual(result.returncode, 0)
            self.assertNotIn(DUMMY_TOKEN, result.stdout + result.stderr)

    def test_rejects_invalid_existing_git_config_count(self):
        with tempfile.TemporaryDirectory() as directory:
            result = self.run_loader(
                self.credential_file(directory, f"GH_TOKEN={DUMMY_TOKEN}\n"),
                extra_env={"GIT_CONFIG_COUNT": "invalid"},
            )

        self.assertNotEqual(result.returncode, 0)
        self.assertNotIn(DUMMY_TOKEN, result.stdout + result.stderr)


if __name__ == "__main__":
    unittest.main()
