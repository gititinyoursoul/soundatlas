import contextlib
import importlib.util
import io
import os
import subprocess
import tempfile
import unittest
from pathlib import Path
from unittest import mock

SCRIPT = Path(__file__).with_name("gh_project.py")
BASHRC = SCRIPT.parent.parent / ".devcontainer" / "bashrc"
SPEC = importlib.util.spec_from_file_location("gh_project", SCRIPT)
assert SPEC and SPEC.loader
MODULE = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(MODULE)


class GhProjectTests(unittest.TestCase):
    def credential_file(self, directory: str, content: str) -> Path:
        path = Path(directory) / "github-project-agent.env"
        path.write_text(content, encoding="utf-8")
        return path

    def shell_token(self, path: Path, ambient_token: str | None = None) -> str:
        environ = {
            "HOME": os.environ.get("HOME", "/tmp"),
            "PATH": os.environ["PATH"],
            "SOUNDATLAS_GITHUB_AGENT_ENV_FILE": str(path),
        }
        if ambient_token is not None:
            environ["GH_TOKEN"] = ambient_token
        result = subprocess.run(
            [
                "bash",
                "--noprofile",
                "--rcfile",
                str(BASHRC),
                "-ic",
                'printf "%s" "$GH_TOKEN"',
            ],
            env=environ,
            capture_output=True,
            text=True,
            check=True,
        )
        return result.stdout

    def test_project_environment_replaces_ambient_github_tokens(self):
        with tempfile.TemporaryDirectory() as directory:
            path = self.credential_file(directory, "GH_TOKEN=project-token\n")
            result = MODULE.project_environment(
                {
                    "GH_TOKEN": "repository-token",
                    "GITHUB_TOKEN": "fallback-token",
                    MODULE.PROJECT_ENV_PATH: str(path),
                    "UNCHANGED": "value",
                }
            )

        self.assertEqual(result["GH_TOKEN"], "project-token")
        self.assertNotIn("GITHUB_TOKEN", result)
        self.assertEqual(result["UNCHANGED"], "value")

    def test_new_shell_reads_replacement_repository_credential(self):
        with tempfile.TemporaryDirectory() as directory:
            path = self.credential_file(directory, "GH_TOKEN=first-dummy-token\n")
            first = self.shell_token(path)
            path.write_text("GH_TOKEN=second-dummy-token\n", encoding="utf-8")
            second = self.shell_token(path)

        self.assertEqual(first, "first-dummy-token")
        self.assertEqual(second, "second-dummy-token")

    def test_explicit_repository_token_override_wins(self):
        with tempfile.TemporaryDirectory() as directory:
            path = self.credential_file(directory, "GH_TOKEN=mounted-dummy-token\n")
            result = self.shell_token(path, ambient_token="explicit-dummy-token")

        self.assertEqual(result, "explicit-dummy-token")

    def test_project_graphql_replaces_auth_and_redacts_failures(self):
        with tempfile.TemporaryDirectory() as directory:
            path = self.credential_file(directory, "GH_TOKEN=project-token\n")
            environ = {MODULE.PROJECT_ENV_PATH: str(path)}
            completed = subprocess.CompletedProcess(
                [], 1, stdout="project-token", stderr=""
            )
            with (
                mock.patch.object(
                    MODULE.subprocess, "run", return_value=completed
                ) as run,
                self.assertRaises(MODULE.ProjectCredentialError) as raised,
            ):
                MODULE.graphql("query { viewer { login } }", {}, environ)

        command = run.call_args.args[0]
        child_env = run.call_args.kwargs["env"]
        self.assertEqual(command[:3], ["gh", "api", "graphql"])
        self.assertEqual(child_env["GH_TOKEN"], "project-token")
        self.assertNotIn("project-token", str(raised.exception))

    def test_list_projects_emits_gh_compatible_shape(self):
        response = {
            "viewer": {
                "projectsV2": {
                    "totalCount": 1,
                    "nodes": [{"id": "project", "number": 1, "title": "Tracker"}],
                }
            }
        }
        with mock.patch.object(MODULE, "graphql", return_value=response):
            result = MODULE.list_projects({})

        self.assertEqual(result["totalCount"], 1)
        self.assertEqual(result["projects"][0]["id"], "project")

    def test_rejects_unapproved_project_owner_before_graphql(self):
        with (
            mock.patch.object(MODULE, "graphql") as graphql,
            self.assertRaises(MODULE.ProjectCredentialError),
        ):
            MODULE.run_project(["list", "--owner", "another-owner"], {})
        graphql.assert_not_called()

    def test_missing_configuration_fails_before_starting_gh(self):
        with (
            mock.patch.object(MODULE.os, "environ", {}),
            mock.patch.object(MODULE.subprocess, "run") as run,
            contextlib.redirect_stderr(io.StringIO()) as error,
        ):
            result = MODULE.main(["list"])

        self.assertEqual(result, 1)
        self.assertIn(MODULE.PROJECT_ENV_PATH, error.getvalue())
        run.assert_not_called()

    def test_malformed_file_does_not_echo_credential_content(self):
        secret = "do-not-print-this-value"
        with tempfile.TemporaryDirectory() as directory:
            path = self.credential_file(directory, f"OTHER_TOKEN={secret}\n")
            environ = os.environ.copy()
            environ[MODULE.PROJECT_ENV_PATH] = str(path)
            with (
                mock.patch.object(MODULE.os, "environ", environ),
                contextlib.redirect_stderr(io.StringIO()) as error,
            ):
                result = MODULE.main(["list"])

        self.assertEqual(result, 1)
        self.assertNotIn(secret, error.getvalue())

    def test_duplicate_or_empty_assignment_is_rejected(self):
        for content in ("GH_TOKEN=\n", "GH_TOKEN=first\nGH_TOKEN=second\n"):
            with (
                self.subTest(content=content),
                tempfile.TemporaryDirectory() as directory,
            ):
                path = self.credential_file(directory, content)
                with self.assertRaises(MODULE.ProjectCredentialError):
                    MODULE.read_project_token(path)


if __name__ == "__main__":
    unittest.main()
