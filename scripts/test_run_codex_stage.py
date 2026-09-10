import contextlib
import importlib.util
import io
import json
import sys
import tempfile
import unittest
from pathlib import Path
from unittest import mock

SCRIPT = Path(__file__).with_name("run_codex_stage.py")
SPEC = importlib.util.spec_from_file_location("run_codex_stage", SCRIPT)
assert SPEC and SPEC.loader
MODULE = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = MODULE
SPEC.loader.exec_module(MODULE)


def policy_text() -> str:
    return """[workflow]
discussion = "fast"
planning = "reasoning"
implementation = "coding"
review = "reasoning"

[roles]
fast = "gpt-5.6-luna"
reasoning = "gpt-5.6-sol"
coding = "gpt-5.6-terra"

[effort]
fast = "low"
reasoning = "high"
coding = "medium"
"""


class RunCodexStageTests(unittest.TestCase):
    def policy_file(self, directory: str, content: str | None = None) -> Path:
        path = Path(directory) / "model-routing.toml"
        path.write_text(content if content is not None else policy_text(), encoding="utf-8")
        return path

    def test_resolves_every_stage_to_the_selected_model_and_effort(self):
        expected = {
            "discussion": ("fast", "gpt-5.6-luna", "low"),
            "planning": ("reasoning", "gpt-5.6-sol", "high"),
            "implementation": ("coding", "gpt-5.6-terra", "medium"),
            "review": ("reasoning", "gpt-5.6-sol", "high"),
        }
        with tempfile.TemporaryDirectory() as directory:
            policy = MODULE.load_policy(self.policy_file(directory))
        for stage, values in expected.items():
            with self.subTest(stage=stage):
                resolved = MODULE.resolve_stage(stage, policy)
                self.assertEqual((resolved.role, resolved.model, resolved.effort), values)
                self.assertEqual(
                    MODULE.build_command(resolved, "execution context"),
                    [
                        "codex",
                        "--model",
                        values[1],
                        "--config",
                        f'model_reasoning_effort={json.dumps(values[2])}',
                        "execution context",
                    ],
                )

    def test_rejects_unknown_stage_before_command_building(self):
        with tempfile.TemporaryDirectory() as directory:
            policy = MODULE.load_policy(self.policy_file(directory))
        with self.assertRaisesRegex(MODULE.PolicyError, "unknown workflow stage"):
            MODULE.resolve_stage("release", policy)

    def test_rejects_missing_model_and_effort(self):
        for removed_line, message in (
            ('reasoning = "gpt-5.6-sol"\n', "model"),
            ('reasoning = "high"\n', "reasoning effort"),
        ):
            with self.subTest(removed_line=removed_line), tempfile.TemporaryDirectory() as directory:
                policy = MODULE.load_policy(self.policy_file(directory, policy_text().replace(removed_line, "")))
                with self.assertRaisesRegex(MODULE.PolicyError, message):
                    MODULE.resolve_stage("planning", policy)

    def test_rejects_missing_role_and_unsupported_effort(self):
        with tempfile.TemporaryDirectory() as directory:
            missing_role = MODULE.load_policy(
                self.policy_file(directory, policy_text().replace('planning = "reasoning"', 'planning = ""'))
            )
            with self.assertRaisesRegex(MODULE.PolicyError, "role"):
                MODULE.resolve_stage("planning", missing_role)

            unsupported_effort = MODULE.load_policy(
                self.policy_file(directory, policy_text().replace('reasoning = "high"', 'reasoning = "max"'))
            )
            with self.assertRaisesRegex(MODULE.PolicyError, "unsupported reasoning effort"):
                MODULE.resolve_stage("planning", unsupported_effort)

    def test_rejects_missing_stage_and_malformed_policy(self):
        with tempfile.TemporaryDirectory() as directory:
            missing_stage = MODULE.load_policy(
                self.policy_file(directory, policy_text().replace('review = "reasoning"\n', ""))
            )
            with self.assertRaisesRegex(MODULE.PolicyError, "must define exactly"):
                MODULE.resolve_stage("planning", missing_stage)
            malformed = self.policy_file(directory, "[workflow\n")
            with self.assertRaisesRegex(MODULE.PolicyError, "malformed"):
                MODULE.load_policy(malformed)

    def test_print_command_never_starts_codex(self):
        with tempfile.TemporaryDirectory() as directory, mock.patch.object(
            MODULE, "POLICY_PATH", self.policy_file(directory)
        ), mock.patch.object(MODULE, "build_execution_context", return_value="context") as context, mock.patch.object(MODULE.os, "execvp") as execvp, contextlib.redirect_stdout(
            io.StringIO()
        ) as output:
            result = MODULE.main(["--stage", "planning", "--print-command"])

        self.assertEqual(result, 0)
        self.assertEqual(
            json.loads(output.getvalue()),
            MODULE.build_command(
                MODULE.ResolvedStage(
                    stage="planning", role="reasoning", model="gpt-5.6-sol", effort="high"
                ),
                "context",
            ),
        )
        context.assert_called_once_with()
        execvp.assert_not_called()

    def test_missing_codex_fails_after_validation(self):
        with tempfile.TemporaryDirectory() as directory, mock.patch.object(
            MODULE, "POLICY_PATH", self.policy_file(directory)
        ), mock.patch.object(MODULE, "build_execution_context", return_value="context"), mock.patch.object(MODULE.os, "execvp", side_effect=FileNotFoundError), contextlib.redirect_stderr(
            io.StringIO()
        ) as error:
            result = MODULE.main(["--stage", "planning"])

        self.assertEqual(result, 127)
        self.assertIn("was not found", error.getvalue())

    def test_context_failure_stops_before_starting_codex(self):
        with tempfile.TemporaryDirectory() as directory, mock.patch.object(
            MODULE, "POLICY_PATH", self.policy_file(directory)
        ), mock.patch.object(MODULE, "build_execution_context", side_effect=MODULE.ContextError("not Pane")), mock.patch.object(
            MODULE.os, "execvp"
        ) as execvp, contextlib.redirect_stderr(io.StringIO()) as error:
            result = MODULE.main(["--stage", "planning"])

        self.assertEqual(result, 2)
        self.assertIn("not Pane", error.getvalue())
        execvp.assert_not_called()


if __name__ == "__main__":
    unittest.main()
