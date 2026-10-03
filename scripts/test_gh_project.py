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
SPEC = importlib.util.spec_from_file_location("gh_project", SCRIPT)
assert SPEC and SPEC.loader
MODULE = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(MODULE)


class GhProjectTests(unittest.TestCase):
    def credential_file(self, directory: str, content: str) -> Path:
        path = Path(directory) / "github-project-agent.env"
        path.write_text(content, encoding="utf-8")
        return path

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

    def test_project_graphql_preserves_numeric_looking_string_variables(self):
        with tempfile.TemporaryDirectory() as directory:
            path = self.credential_file(directory, "GH_TOKEN=project-token\n")
            environ = {MODULE.PROJECT_ENV_PATH: str(path)}
            completed = subprocess.CompletedProcess(
                [], 0, stdout='{"data": {}}', stderr=""
            )
            with mock.patch.object(
                MODULE.subprocess, "run", return_value=completed
            ) as run:
                MODULE.graphql(
                    "query($number: Int!, $option: String!) { viewer { login } }",
                    {"number": 1, "option": "12345678"},
                    environ,
                )

        command = run.call_args.args[0]
        pairs = [command[index : index + 2] for index in range(len(command) - 1)]
        self.assertIn(["-F", "number=1"], pairs)
        self.assertIn(["-f", "option=12345678"], pairs)

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

    def test_application_root_and_repository_token_cannot_select_project_auth(self):
        with tempfile.TemporaryDirectory() as directory:
            self.credential_file(directory, "GH_TOKEN=dummy-project-token\n")
            with self.assertRaisesRegex(MODULE.ProjectCredentialError, "not configured"):
                MODULE.project_environment({
                    "SOUNDATLAS_SECRETS_DIR": directory,
                    "GH_TOKEN": "dummy-repository-token",
                    "GITHUB_TOKEN": "dummy-fallback-token",
                })

    def test_explicit_project_path_is_independent_of_application_root(self):
        with tempfile.TemporaryDirectory() as directory:
            path = self.credential_file(directory, "GH_TOKEN=dummy-project-token\n")
            result = MODULE.project_environment({
                MODULE.PROJECT_ENV_PATH: str(path),
                "SOUNDATLAS_SECRETS_DIR": "nonexistent-application-store",
            })
            self.assertEqual(result["GH_TOKEN"], "dummy-project-token")

    def test_invalid_project_files_fail_before_gh_without_exposing_contents(self):
        for kind in ("missing", "directory", "invalid-text", "unreadable"):
            with self.subTest(kind=kind), tempfile.TemporaryDirectory() as directory:
                path = Path(directory) / "project.env"
                if kind == "directory":
                    path.mkdir()
                elif kind in ("invalid-text", "unreadable"):
                    path.write_bytes(b"GH_TOKEN=do-not-print\xff")
                with contextlib.ExitStack() as stack:
                    if kind == "unreadable":
                        stack.enter_context(mock.patch.object(
                            Path, "read_text", side_effect=PermissionError("do-not-print"),
                        ))
                    stack.enter_context(mock.patch.dict(MODULE.os.environ, {
                        MODULE.PROJECT_ENV_PATH: str(path),
                        "GH_TOKEN": "dummy-repository-token",
                    }, clear=True))
                    run = stack.enter_context(mock.patch.object(MODULE.subprocess, "run"))
                    error = stack.enter_context(contextlib.redirect_stderr(io.StringIO()))
                    result = MODULE.main(["list"])
                self.assertEqual(result, 1)
                self.assertIn("readable regular UTF-8 file", error.getvalue())
                self.assertNotIn("do-not-print", error.getvalue())
                run.assert_not_called()


if __name__ == "__main__":
    unittest.main()
