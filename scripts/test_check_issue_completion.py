import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


SCRIPT = Path(__file__).with_name("check_issue_completion.py")
VALID_REPORT = """## Summary

Completed.

## Verification

- check - Pass

## Acceptance Criteria Result

- [x] Criterion - evidence

## Review Result

- Verdict: Accepted
- Evidence coverage: checks
- Findings and routing: None
- Documentation impact: Current

## Remaining Risks

- None
"""


class CheckIssueCompletionTests(unittest.TestCase):
    def run_cli(self, *args: str, input_text: str | None = None) -> subprocess.CompletedProcess[str]:
        return subprocess.run(
            [sys.executable, str(SCRIPT), *args],
            input=input_text,
            capture_output=True,
            text=True,
            check=False,
        )

    def report_path(self, text: str) -> tuple[tempfile.TemporaryDirectory[str], Path]:
        directory = tempfile.TemporaryDirectory()
        path = Path(directory.name) / "report.md"
        path.write_text(text, encoding="utf-8")
        return directory, path

    def test_accepts_complete_report(self) -> None:
        directory, path = self.report_path(VALID_REPORT)
        self.addCleanup(directory.cleanup)
        result = self.run_cli("completion", "--report", str(path), "--commit", "1700cef", "--completion-comments", "1", "--working-tree-verified")
        self.assertEqual(result.returncode, 0, result.stderr)

    def test_rejects_unchecked_criteria(self) -> None:
        directory, path = self.report_path(VALID_REPORT.replace("- [x]", "- [ ]"))
        self.addCleanup(directory.cleanup)
        result = self.run_cli("report", "--file", str(path))
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("all acceptance criteria", result.stderr)

    def test_rejects_non_accepted_review(self) -> None:
        directory, path = self.report_path(VALID_REPORT.replace("Accepted", "Correction required"))
        self.addCleanup(directory.cleanup)
        result = self.run_cli("report", "--file", str(path))
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("Accepted review verdict", result.stderr)

    def test_rejects_duplicate_completion_comments(self) -> None:
        directory, path = self.report_path(VALID_REPORT)
        self.addCleanup(directory.cleanup)
        result = self.run_cli("completion", "--report", str(path), "--commit", "1700cef", "--completion-comments", "2", "--working-tree-verified")
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("exactly one", result.stderr)

    def test_generic_payload_preserves_newlines_and_shell_sensitive_markdown(self) -> None:
        body = "Header\n\nLiteral \\n text, `backticks`, $(substitution), $value, \"quotes\", and café 🎵.\n"
        directory, path = self.report_path(body)
        self.addCleanup(directory.cleanup)
        result = subprocess.run(
            [sys.executable, str(Path(__file__).with_name("gh_markdown_payload.py")), "--file", str(path)],
            capture_output=True,
            text=True,
            check=False,
        )
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(json.loads(result.stdout)["body"], body)


if __name__ == "__main__":
    unittest.main()
