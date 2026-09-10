import subprocess
import unittest

from pane_execution_context import ContextError, build_execution_context


def completed(root: str = "/runtime/repos/example/worktrees/issue-232") -> subprocess.CompletedProcess[str]:
    return subprocess.CompletedProcess(["git"], 0, stdout=root + "\n", stderr="")


class PaneExecutionContextTests(unittest.TestCase):
    def test_describes_the_container_boundary_and_fail_closed_actions(self):
        context = build_execution_context(
            environment={"PANE_DIR": "/runtime/pane"},
            path_exists=lambda path: path == "/.dockerenv",
            run=lambda *_args, **_kwargs: completed(),
        )

        self.assertIn("WORKSPACE: available", context)
        self.assertNotIn("/runtime/repos", context)
        self.assertIn("SERVICE: unknown", context)
        self.assertIn("HOST: unavailable", context)
        self.assertIn("GUI: unavailable", context)
        self.assertIn("Docker socket: unavailable", context)
        self.assertIn("unknown, unreachable, or unsupported capabilities are unavailable", context)

    def test_requires_a_pane_container_and_git_worktree(self):
        with self.assertRaisesRegex(ContextError, "Pane workspace container"):
            build_execution_context(
                environment={}, path_exists=lambda _path: True, run=lambda *_args, **_kwargs: completed()
            )
        with self.assertRaisesRegex(ContextError, "Git worktree"):
            build_execution_context(
                environment={"PANE_DIR": "/runtime/pane"},
                path_exists=lambda path: path == "/.dockerenv",
                run=lambda *_args, **_kwargs: subprocess.CompletedProcess(["git"], 1, stdout="", stderr=""),
            )

    def test_does_not_promote_display_or_docker_socket_to_host_access(self):
        context = build_execution_context(
            environment={"PANE_DIR": "/runtime/pane", "DISPLAY": ":0"},
            path_exists=lambda path: path in {"/.dockerenv", "/var/run/docker.sock"},
            run=lambda *_args, **_kwargs: completed(),
        )

        self.assertIn("GUI: configured in this container", context)
        self.assertIn("Docker socket: unknown", context)
        self.assertIn("HOST: unavailable", context)


if __name__ == "__main__":
    unittest.main()
