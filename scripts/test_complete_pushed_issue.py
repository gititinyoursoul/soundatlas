import contextlib
import importlib.util
import io
import json
import unittest
from pathlib import Path

SCRIPT = Path(__file__).with_name("complete_pushed_issue.py")
SPEC = importlib.util.spec_from_file_location("complete_pushed_issue", SCRIPT)
assert SPEC and SPEC.loader
MODULE = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(MODULE)

VALID_REPORT = """## Implementation Report

## Summary

Completed.

Commit: `abcdef0`

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


class FakeRunner:
    def __init__(self, responses):
        self.responses = responses
        self.calls = []

    def __call__(self, command, input_text=None):
        self.calls.append((command, input_text))
        key = tuple(command)
        response = self.responses.get(key)
        if isinstance(response, Exception):
            raise response
        if response is None:
            raise AssertionError(f"unexpected command: {command}")
        return response


def output(value):
    return json.dumps(value)


def project_command(*arguments):
    return tuple(MODULE.project_command(*arguments))


class CompletePushedIssueTests(unittest.TestCase):
    def pr_responses(self):
        responses = self.completion_responses()
        issue_key = ("gh", "issue", "view", "178", "--repo", "owner/repo", "--json", "number,title,state,comments,url")
        responses[issue_key] = self.issue().replace('"OPEN"', '"CLOSED"')
        responses[("gh", "pr", "view", "42", "--repo", "owner/repo", "--json", "state,baseRefName,headRefOid,mergeCommit,closingIssuesReferences")] = output({"state": "MERGED", "baseRefName": "main", "headRefOid": "abcdef0123456789", "mergeCommit": {"oid": "merge123"}, "closingIssuesReferences": [{"number": 178, "repository": {"name": "repo", "owner": {"login": "owner"}}}]})
        responses[("git", "merge-base", "--is-ancestor", "merge123", "fedcba9876543210")] = ""
        return responses

    def pr_args(self):
        return ("--repo", "owner/repo", "--owner", "owner", "complete", "--issue", "178", "--commit", "abcdef0", "--merged-pr", "42", "--merge-authorized", "--post-merge-verified", "--working-tree-verified")

    def test_merged_pr_completion_does_not_close_again(self):
        runner = FakeRunner(self.pr_responses())
        self.assertEqual(self.run_main(runner, *self.pr_args()), 0)
        self.assertFalse(any(call[0][:3] == ["gh", "issue", "close"] for call in runner.calls))
        self.assertTrue(any(call[0][:3] == MODULE.project_command("item-edit") for call in runner.calls))

    def test_merged_pr_handles_each_linked_issue_separately(self):
        responses = self.pr_responses()
        key = ("gh", "pr", "view", "42", "--repo", "owner/repo", "--json", "state,baseRefName,headRefOid,mergeCommit,closingIssuesReferences")
        pr = json.loads(responses[key])
        pr["closingIssuesReferences"].append({"number": 179, "repository": {"name": "repo", "owner": {"login": "owner"}}})
        responses[key] = output(pr)
        runner = FakeRunner(responses)
        self.assertEqual(self.run_main(runner, *self.pr_args()), 0)
        payload = next(json.loads(data)["body"] for cmd, data in runner.calls if cmd[:3] == ["gh", "api", "--method"])
        self.assertIn("Issue: #178", payload)
        self.assertNotIn("Issue: #179", payload)

    def test_merged_pr_requires_verification_before_mutation(self):
        runner = FakeRunner(self.pr_responses())
        args = tuple(arg for arg in self.pr_args() if arg != "--post-merge-verified")
        self.assertEqual(self.run_main(runner, *args), 1)
        self.assertFalse(any(call[0][:2] == ["gh", "api"] for call in runner.calls))

    def test_merged_pr_requires_authorization_before_inspection(self):
        runner = FakeRunner({})
        args = tuple(arg for arg in self.pr_args() if arg != "--merge-authorized")
        self.assertEqual(self.run_main(runner, *args), 1)
        self.assertEqual(runner.calls, [])

    def test_merged_pr_rejects_same_issue_number_in_another_repository(self):
        responses = self.pr_responses()
        key = ("gh", "pr", "view", "42", "--repo", "owner/repo", "--json", "state,baseRefName,headRefOid,mergeCommit,closingIssuesReferences")
        pr = json.loads(responses[key])
        pr["closingIssuesReferences"][0]["repository"]["owner"]["login"] = "other"
        responses[key] = output(pr)
        runner = FakeRunner(responses)
        self.assertEqual(self.run_main(runner, *self.pr_args()), 1)
        self.assertFalse(any(call[0][:2] == ["gh", "api"] for call in runner.calls))

    def test_merged_pr_recovery_does_not_repeat_completion_comment(self):
        runner = FakeRunner(self.pr_responses())
        self.assertEqual(self.run_main(runner, *self.pr_args()), 0)
        posted = next(json.loads(data)["body"] for cmd, data in runner.calls if cmd[:3] == ["gh", "api", "--method"])
        responses = self.pr_responses()
        key = ("gh", "issue", "view", "178", "--repo", "owner/repo", "--json", "number,title,state,comments,url")
        issue = json.loads(responses[key])
        issue["comments"].append({"body": posted})
        responses[key] = output(issue)
        runner = FakeRunner(responses)
        self.assertEqual(self.run_main(runner, *self.pr_args()), 0)
        self.assertFalse(any(call[0][:2] == ["gh", "api"] for call in runner.calls))

    def test_verification_failure_reopens_and_records_only_affected_issue(self):
        responses = self.pr_responses()
        pr_key = ("gh", "pr", "view", "42", "--repo", "owner/repo", "--json", "state,baseRefName,headRefOid,mergeCommit,closingIssuesReferences")
        failure_pr_key = ("gh", "pr", "view", "42", "--repo", "owner/repo", "--json", "state,baseRefName,closingIssuesReferences")
        responses[failure_pr_key] = responses[pr_key]
        responses[("gh", "issue", "reopen", "178", "--repo", "owner/repo")] = ""
        runner = FakeRunner(responses)
        args = ("--repo", "owner/repo", "record-pr-failure", "--issue", "178", "--merged-pr", "42", "--failure", "CI failed", "--merge-authorized")
        self.assertEqual(self.run_main(runner, *args), 0)
        self.assertEqual(runner.calls[-2][0][:3], ["gh", "issue", "reopen"])
        self.assertIn("CI failed", json.loads(runner.calls[-1][1])["body"])
        self.assertFalse(any(call[0][:3] == MODULE.project_command("item-edit") for call in runner.calls))

    def test_verification_failure_stops_if_reopen_fails(self):
        responses = self.pr_responses()
        pr_key = ("gh", "pr", "view", "42", "--repo", "owner/repo", "--json", "state,baseRefName,headRefOid,mergeCommit,closingIssuesReferences")
        failure_pr_key = ("gh", "pr", "view", "42", "--repo", "owner/repo", "--json", "state,baseRefName,closingIssuesReferences")
        responses[failure_pr_key] = responses[pr_key]
        responses[("gh", "issue", "reopen", "178", "--repo", "owner/repo")] = MODULE.ReconciliationError("reopen failed")
        runner = FakeRunner(responses)
        self.assertEqual(self.run_main(runner, "--repo", "owner/repo", "record-pr-failure", "--issue", "178", "--merged-pr", "42", "--failure", "CI failed", "--merge-authorized"), 1)
        self.assertFalse(any(call[0][:2] == ["gh", "api"] for call in runner.calls))

    def test_verification_failure_recovery_does_not_repeat_evidence(self):
        responses = self.pr_responses()
        pr_key = ("gh", "pr", "view", "42", "--repo", "owner/repo", "--json", "state,baseRefName,headRefOid,mergeCommit,closingIssuesReferences")
        failure_pr_key = ("gh", "pr", "view", "42", "--repo", "owner/repo", "--json", "state,baseRefName,closingIssuesReferences")
        responses[failure_pr_key] = responses[pr_key]
        key = ("gh", "issue", "view", "178", "--repo", "owner/repo", "--json", "number,title,state,comments,url")
        issue = json.loads(responses[key])
        issue["state"] = "OPEN"
        issue["comments"].append({"body": "## Post-merge verification failure\n\n- PR: #42\n- Issue: #178\n- Failure: CI failed\n"})
        responses[key] = output(issue)
        runner = FakeRunner(responses)
        self.assertEqual(self.run_main(runner, "--repo", "owner/repo", "record-pr-failure", "--issue", "178", "--merged-pr", "42", "--failure", "CI failed", "--merge-authorized"), 0)
        self.assertFalse(any(call[0][:2] == ["gh", "api"] or call[0][:3] == ["gh", "issue", "reopen"] for call in runner.calls))

    def issue(self, report=VALID_REPORT, completed=False):
        comments = [{"body": report}]
        if completed:
            comments.append({"body": "## Completed\n\n- Commit: `abcdef0`"})
        return output(
            {"number": 178, "title": "Example", "state": "OPEN", "comments": comments}
        )

    def completion_responses(self, report=VALID_REPORT):
        return {
            (
                "gh",
                "issue",
                "view",
                "178",
                "--repo",
                "owner/repo",
                "--json",
                "number,title,state,comments,url",
            ): self.issue(report),
            ("git", "rev-parse", "abcdef0"): "abcdef0123456789\n",
            ("git", "rev-parse", "origin/main"): "fedcba9876543210\n",
            (
                "git",
                "merge-base",
                "--is-ancestor",
                "abcdef0123456789",
                "fedcba9876543210",
            ): "",
            project_command(
                "item-list",
                "1",
                "--owner",
                "owner",
                "--limit",
                "500",
                "--format",
                "json",
            ): output({"items": [{"id": "item", "content": {"number": 178}}]}),
            project_command("list", "--owner", "owner", "--format", "json"): output(
                {"projects": [{"number": 1, "id": "project"}]}
            ),
            project_command(
                "field-list", "1", "--owner", "owner", "--format", "json"
            ): output(
                {
                    "fields": [
                        {
                            "name": "Status",
                            "id": "status",
                            "options": [{"name": "Done", "id": "done"}],
                        }
                    ]
                }
            ),
            (
                "gh",
                "api",
                "--method",
                "POST",
                "repos/owner/repo/issues/178/comments",
                "--input",
                "-",
            ): "{}",
            project_command(
                "item-edit",
                "--id",
                "item",
                "--project-id",
                "project",
                "--field-id",
                "status",
                "--single-select-option-id",
                "done",
            ): "",
            ("gh", "issue", "close", "178", "--repo", "owner/repo"): "",
        }

    def run_main(self, runner, *arguments):
        with (
            contextlib.redirect_stdout(io.StringIO()),
            contextlib.redirect_stderr(io.StringIO()),
        ):
            return MODULE.main(list(arguments), runner)

    def test_complete_posts_comment_then_updates_project_then_closes(self):
        runner = FakeRunner(self.completion_responses())
        result = self.run_main(
            runner,
            "--repo",
            "owner/repo",
            "--owner",
            "owner",
            "complete",
            "--issue",
            "178",
            "--commit",
            "abcdef0",
            "--push-authorized",
            "--working-tree-verified",
        )
        self.assertEqual(result, 0)
        actions = [call[0][:3] for call in runner.calls[-3:]]
        self.assertEqual(
            actions,
            [
                ["gh", "api", "--method"],
                [MODULE.sys.executable, MODULE.PROJECT_HELPER, "item-edit"],
                ["gh", "issue", "close"],
            ],
        )
        comment_payload = json.loads(runner.calls[-3][1])
        self.assertIn("## Completed", comment_payload["body"])
        self.assertIn("abcdef0123456789", comment_payload["body"])

    def test_complete_requires_explicit_attestations(self):
        runner = FakeRunner({})
        result = self.run_main(
            runner, "complete", "--issue", "178", "--commit", "abcdef0"
        )
        self.assertEqual(result, 1)
        self.assertEqual(runner.calls, [])

    def test_complete_rejects_unpublished_commit_before_mutation(self):
        responses = self.completion_responses()
        responses[
            (
                "git",
                "merge-base",
                "--is-ancestor",
                "abcdef0123456789",
                "fedcba9876543210",
            )
        ] = MODULE.ReconciliationError("not ancestor")
        runner = FakeRunner(responses)
        result = self.run_main(
            runner,
            "--repo",
            "owner/repo",
            "--owner",
            "owner",
            "complete",
            "--issue",
            "178",
            "--commit",
            "abcdef0",
            "--push-authorized",
            "--working-tree-verified",
        )
        self.assertEqual(result, 1)
        self.assertFalse(any(call[0][:2] == ["gh", "api"] for call in runner.calls))

    def test_complete_rejects_existing_completion_comment(self):
        runner = FakeRunner(
            {
                (
                    "gh",
                    "issue",
                    "view",
                    "178",
                    "--repo",
                    "owner/repo",
                    "--json",
                    "number,title,state,comments,url",
                ): self.issue(completed=True)
            }
        )
        result = self.run_main(
            runner,
            "--repo",
            "owner/repo",
            "--owner",
            "owner",
            "complete",
            "--issue",
            "178",
            "--commit",
            "abcdef0",
            "--push-authorized",
            "--working-tree-verified",
        )
        self.assertEqual(result, 1)
        self.assertEqual(len(runner.calls), 1)

    def test_complete_rejects_missing_implementation_report(self):
        issue = output(
            {"number": 178, "title": "Example", "state": "OPEN", "comments": []}
        )
        runner = FakeRunner(
            {
                (
                    "gh",
                    "issue",
                    "view",
                    "178",
                    "--repo",
                    "owner/repo",
                    "--json",
                    "number,title,state,comments,url",
                ): issue
            }
        )
        result = self.run_main(
            runner,
            "--repo",
            "owner/repo",
            "--owner",
            "owner",
            "complete",
            "--issue",
            "178",
            "--commit",
            "abcdef0",
            "--push-authorized",
            "--working-tree-verified",
        )
        self.assertEqual(result, 1)
        self.assertEqual(len(runner.calls), 1)

    def test_complete_rejects_non_accepted_report_before_git_or_github_mutation(self):
        report = VALID_REPORT.replace(
            "- Verdict: Accepted", "- Verdict: Correction required"
        )
        runner = FakeRunner(
            {
                (
                    "gh",
                    "issue",
                    "view",
                    "178",
                    "--repo",
                    "owner/repo",
                    "--json",
                    "number,title,state,comments,url",
                ): self.issue(report)
            }
        )
        result = self.run_main(
            runner,
            "--repo",
            "owner/repo",
            "--owner",
            "owner",
            "complete",
            "--issue",
            "178",
            "--commit",
            "abcdef0",
            "--push-authorized",
            "--working-tree-verified",
        )
        self.assertEqual(result, 1)
        self.assertEqual(len(runner.calls), 1)

    def test_complete_accepts_an_ordered_reviewed_range(self):
        responses = self.completion_responses()
        responses.pop(("git", "rev-parse", "abcdef0"))
        responses[("git", "merge-base", "--is-ancestor", "base", "head")] = ""
        responses[("git", "rev-parse", "head")] = "abcdef0123456789\n"
        responses[
            (
                "gh",
                "issue",
                "view",
                "178",
                "--repo",
                "owner/repo",
                "--json",
                "number,title,state,comments,url",
            )
        ] = self.issue(
            VALID_REPORT.replace("Commit: `abcdef0`", "Commit range: base..head")
        )
        runner = FakeRunner(responses)
        result = self.run_main(
            runner,
            "--repo",
            "owner/repo",
            "--owner",
            "owner",
            "complete",
            "--issue",
            "178",
            "--range",
            "base..head",
            "--push-authorized",
            "--working-tree-verified",
        )
        self.assertEqual(result, 0)
        comment_payload = json.loads(runner.calls[-3][1])
        self.assertIn("base..head", comment_payload["body"])

    def test_complete_rejects_a_commit_that_does_not_match_the_report(self):
        responses = self.completion_responses()
        responses[
            (
                "gh",
                "issue",
                "view",
                "178",
                "--repo",
                "owner/repo",
                "--json",
                "number,title,state,comments,url",
            )
        ] = self.issue(VALID_REPORT.replace("abcdef0", "deadbee"))
        responses[("git", "rev-parse", "deadbee")] = "1111111111111111\n"
        runner = FakeRunner(responses)
        result = self.run_main(
            runner,
            "--repo",
            "owner/repo",
            "--owner",
            "owner",
            "complete",
            "--issue",
            "178",
            "--commit",
            "abcdef0",
            "--push-authorized",
            "--working-tree-verified",
        )
        self.assertEqual(result, 1)
        self.assertFalse(any(call[0][:2] == ["gh", "api"] for call in runner.calls))

    def test_status_failure_does_not_close_the_issue(self):
        responses = self.completion_responses()
        status_command = project_command(
            "item-edit",
            "--id",
            "item",
            "--project-id",
            "project",
            "--field-id",
            "status",
            "--single-select-option-id",
            "done",
        )
        responses[status_command] = MODULE.ReconciliationError("status update failed")
        runner = FakeRunner(responses)
        result = self.run_main(
            runner,
            "--repo",
            "owner/repo",
            "--owner",
            "owner",
            "complete",
            "--issue",
            "178",
            "--commit",
            "abcdef0",
            "--push-authorized",
            "--working-tree-verified",
        )
        self.assertEqual(result, 1)
        self.assertFalse(
            any(call[0][:3] == ["gh", "issue", "close"] for call in runner.calls)
        )

    def test_frontend_ci_failure_stops_before_github_mutation(self):
        responses = self.completion_responses()
        responses[
            (
                "gh",
                "run",
                "view",
                "123",
                "--repo",
                "owner/repo",
                "--json",
                "conclusion,url",
            )
        ] = output({"conclusion": "failure", "url": "https://example.test/run/123"})
        runner = FakeRunner(responses)
        result = self.run_main(
            runner,
            "--repo",
            "owner/repo",
            "--owner",
            "owner",
            "complete",
            "--issue",
            "178",
            "--commit",
            "abcdef0",
            "--push-authorized",
            "--working-tree-verified",
            "--frontend-ci-run",
            "123",
        )
        self.assertEqual(result, 1)
        self.assertFalse(any(call[0][:2] == ["gh", "api"] for call in runner.calls))

    def test_comment_failure_does_not_change_status_or_close(self):
        responses = self.completion_responses()
        responses[
            (
                "gh",
                "api",
                "--method",
                "POST",
                "repos/owner/repo/issues/178/comments",
                "--input",
                "-",
            )
        ] = MODULE.ReconciliationError("comment failed")
        runner = FakeRunner(responses)
        result = self.run_main(
            runner,
            "--repo",
            "owner/repo",
            "--owner",
            "owner",
            "complete",
            "--issue",
            "178",
            "--commit",
            "abcdef0",
            "--push-authorized",
            "--working-tree-verified",
        )
        self.assertEqual(result, 1)
        self.assertFalse(
            any(
                call[0][:3] == MODULE.project_command("item-edit")
                for call in runner.calls
            )
        )
        self.assertFalse(
            any(call[0][:3] == ["gh", "issue", "close"] for call in runner.calls)
        )

    def test_close_failure_leaves_prior_completion_evidence_intact(self):
        responses = self.completion_responses()
        responses[("gh", "issue", "close", "178", "--repo", "owner/repo")] = (
            MODULE.ReconciliationError("close failed")
        )
        runner = FakeRunner(responses)
        result = self.run_main(
            runner,
            "--repo",
            "owner/repo",
            "--owner",
            "owner",
            "complete",
            "--issue",
            "178",
            "--commit",
            "abcdef0",
            "--push-authorized",
            "--working-tree-verified",
        )
        self.assertEqual(result, 1)
        self.assertTrue(
            any(
                call[0][:3] == MODULE.project_command("item-edit")
                for call in runner.calls
            )
        )

    def test_audit_is_read_only_and_reports_published_candidate(self):
        responses = {
            project_command(
                "item-list",
                "1",
                "--owner",
                "owner",
                "--limit",
                "500",
                "--format",
                "json",
            ): output(
                {
                    "items": [
                        {
                            "status": "Locally Implemented",
                            "content": {"number": 178, "title": "Example"},
                        }
                    ]
                }
            ),
            (
                "gh",
                "issue",
                "view",
                "178",
                "--repo",
                "owner/repo",
                "--json",
                "number,title,state,comments,url",
            ): self.issue(
                VALID_REPORT.replace("Completed.", "Completed.\n\nCommit: `abcdef0`")
            ),
            ("git", "rev-parse", "origin/main"): "fedcba9876543210\n",
            ("git", "merge-base", "--is-ancestor", "abcdef0", "fedcba9876543210"): "",
        }
        runner = FakeRunner(responses)
        result = self.run_main(
            runner, "--repo", "owner/repo", "--owner", "owner", "audit"
        )
        self.assertEqual(result, 0)
        self.assertFalse(
            any(
                call[0][0] == "gh"
                and call[0][1] in {"api", "project", "issue"}
                and "POST" in call[0]
                for call in runner.calls
            )
        )


if __name__ == "__main__":
    unittest.main()
