import json
import subprocess
import sys
import tempfile
import unittest
from copy import deepcopy
from pathlib import Path
from typing import Any

SCRIPT = Path(__file__).with_name("check_issue_readiness.py")
ISSUE_NUMBER = 101
BASE_URL = "https://github.com/example/soundatlas/issues/101"
CONCEPT_URL = f"{BASE_URL}#issuecomment-2"
PLAN_URL = f"{BASE_URL}#issuecomment-3"


def comment(number: int, body: str) -> dict[str, str]:
    return {
        "body": body,
        "url": f"{BASE_URL}#issuecomment-{number}",
        "createdAt": f"2026-08-07T00:{number:02d}:00Z",
    }


def intake_body() -> str:
    return """## Task

Add a readiness gate.

## Context

Prevent premature implementation.

## Acceptance Criteria

- [ ] Readiness is validated.
"""


def grill_review() -> str:
    return """## Grill-Me Review

**Stage:** Intake

### Findings and decisions

1. **Finding:** The gate needs a durable authorization record.
   **Decision:** Confirmed by human — record the implementation go-ahead.

**Next step:** Concept Work
"""


def concept() -> str:
    return """## Concept

### Target behavior

Validate readiness.
"""


def detailed_plan(*, concept_basis: str | None = None, open_questions: str = "None.") -> str:
    basis = concept_basis or f"Target Concept: [#101 Concept]({CONCEPT_URL})"
    return f"""## Detailed Plan Update

{basis}

## Plan

Add the gate.

## Assumptions

- Inputs are canonical Issue artifacts.

## Non-Goals

- No workflow service.

## Acceptance Criteria Changes

None.

## Implementation Steps

1. Add the validator.

## Validation

- Run unit tests.

## Open Questions

{open_questions}
"""


def simple_plan() -> str:
    return """## Plan Update

Grill-Me check: clean — no material findings; proceeding.

Concept Work: Not required — the change is local and decision-complete.

## Plan

Make the local change.

## Non-Goals

- No cross-cutting behavior.

## Open Questions

None.
"""


def go_ahead(*, plan_url: str = PLAN_URL, issue_number: int = ISSUE_NUMBER) -> str:
    return f"""## Proceed to Implementation

- Plan: [#101 Detailed Plan Update]({plan_url})
- Human decision: Proceed with this plan.
- Authorized scope: Issue #{issue_number}'s accepted plan.
"""


def valid_issue() -> dict[str, Any]:
    return {
        "number": ISSUE_NUMBER,
        "body": intake_body(),
        "comments": [
            comment(1, grill_review()),
            comment(2, concept()),
            comment(3, detailed_plan()),
            comment(4, go_ahead()),
        ],
    }


class CheckIssueReadinessTests(unittest.TestCase):
    def run_cli(
        self, issue: dict[str, Any], *extra_args: str
    ) -> subprocess.CompletedProcess[str]:
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "issue.json"
            path.write_text(json.dumps(issue), encoding="utf-8")
            return subprocess.run(
                [sys.executable, str(SCRIPT), "--file", str(path), *extra_args],
                capture_output=True,
                text=True,
                check=False,
            )

    def assert_invalid(self, issue: dict[str, Any], message: str) -> None:
        result = self.run_cli(issue)
        self.assertNotEqual(result.returncode, 0)
        self.assertIn(message, result.stderr)

    def assert_invalid_with_args(
        self, issue: dict[str, Any], message: str, *extra_args: str
    ) -> None:
        result = self.run_cli(issue, *extra_args)
        self.assertNotEqual(result.returncode, 0)
        self.assertIn(message, result.stderr)

    def test_accepts_confirmed_detailed_plan(self) -> None:
        result = self.run_cli(valid_issue())
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn(PLAN_URL, result.stdout)

    def test_accepts_json_from_standard_input(self) -> None:
        result = subprocess.run(
            [sys.executable, str(SCRIPT), "--file", "-"],
            input=json.dumps(valid_issue()),
            capture_output=True,
            text=True,
            check=False,
        )
        self.assertEqual(result.returncode, 0, result.stderr)

    def test_accepts_simple_plan_with_inline_clean_check(self) -> None:
        issue = valid_issue()
        issue["comments"] = [
            comment(3, simple_plan()),
            comment(4, go_ahead()),
        ]
        result = self.run_cli(issue)
        self.assertEqual(result.returncode, 0, result.stderr)

    def test_requires_grill_evidence_only_when_selected_for_risk(self) -> None:
        issue = valid_issue()
        plan = simple_plan().replace(
            "Grill-Me check: clean — no material findings; proceeding.\n\n", ""
        )
        issue["comments"] = [comment(3, plan), comment(4, go_ahead())]
        self.assertEqual(self.run_cli(issue).returncode, 0)
        self.assert_invalid_with_args(
            issue,
            "no completed Grill-Me Review or inline clean check",
            "--require-grill-review",
        )

    def test_rejects_incomplete_grill_review(self) -> None:
        issue = valid_issue()
        issue["comments"][0]["body"] = grill_review().replace(
            "   **Decision:** Confirmed by human — record the implementation go-ahead.\n", ""
        )
        self.assert_invalid(issue, "1 finding(s) and 0 decision(s)")

    def test_rejects_pending_grill_decision(self) -> None:
        issue = valid_issue()
        issue["comments"][0]["body"] = grill_review().replace(
            "Confirmed by human — record", "Pending human confirmation — record"
        )
        self.assert_invalid(issue, "unconfirmed or malformed Decision")

    def test_rejects_missing_go_ahead(self) -> None:
        issue = valid_issue()
        issue["comments"].pop()
        self.assert_invalid(issue, "no Proceed to Implementation")

    def test_rejects_missing_human_decision(self) -> None:
        issue = valid_issue()
        issue["comments"][-1]["body"] = go_ahead().replace(
            "- Human decision: Proceed with this plan.\n", ""
        )
        self.assert_invalid(issue, "missing the confirmed human decision")

    def test_rejects_wrong_plan_link(self) -> None:
        issue = valid_issue()
        issue["comments"][-1]["body"] = go_ahead(plan_url=f"{BASE_URL}#issuecomment-99")
        self.assert_invalid(issue, "does not link the latest Plan Update")

    def test_rejects_go_ahead_before_latest_plan(self) -> None:
        issue = valid_issue()
        issue["comments"].append(comment(5, detailed_plan()))
        self.assert_invalid(issue, "must follow the latest Plan Update")

    def test_rejects_incomplete_detailed_plan(self) -> None:
        issue = valid_issue()
        issue["comments"][2]["body"] = detailed_plan().replace(
            "## Validation\n\n- Run unit tests.\n\n", ""
        )
        self.assert_invalid(issue, "missing required section: ## Validation")

    def test_rejects_later_intake_revision(self) -> None:
        issue = valid_issue()
        issue["comments"].append(comment(5, "## Intake Revision\n\n- Revised scope: changed"))
        self.assert_invalid(issue, "superseded by ## Intake Revision")

    def test_rejects_later_concept(self) -> None:
        issue = valid_issue()
        issue["comments"].append(comment(5, concept()))
        self.assert_invalid(issue, "superseded by ## Concept")

    def test_rejects_later_blocking_review(self) -> None:
        issue = valid_issue()
        blocked = grill_review().replace("**Next step:** Concept Work", "**Next step:** Blocked")
        issue["comments"].append(comment(5, blocked))
        self.assert_invalid(issue, "routes the Issue away from implementation")

    def test_rejects_unresolved_pre_plan_blocker(self) -> None:
        issue = valid_issue()
        issue["comments"][0]["body"] = grill_review().replace(
            "**Next step:** Concept Work", "**Next step:** Blocked"
        )
        self.assert_invalid(issue, "latest pre-Plan Grill-Me Review remains blocked")

    def test_rejects_missing_concept_required_by_latest_review(self) -> None:
        issue = valid_issue()
        issue["comments"].pop(1)
        issue["comments"][1]["body"] = detailed_plan(
            concept_basis="Concept Work: Not required — the change appears local."
        )
        self.assert_invalid(issue, "requires a later Concept")

    def test_rejects_blocking_open_questions(self) -> None:
        issue = valid_issue()
        issue["comments"][2]["body"] = detailed_plan(open_questions="- Which format?")
        self.assert_invalid(issue, "Open Questions must be None")

    def test_accepts_human_deferred_non_blocking_question(self) -> None:
        issue = valid_issue()
        issue["comments"][2]["body"] = detailed_plan(
            open_questions="- Deferred by human — non-blocking: exact error wording."
        )
        result = self.run_cli(issue)
        self.assertEqual(result.returncode, 0, result.stderr)

    def test_rejects_missing_concept_basis(self) -> None:
        issue = valid_issue()
        issue["comments"][2]["body"] = detailed_plan(concept_basis="Plan basis: unknown")
        self.assert_invalid(issue, "reference its Target Concept")

    def test_rejects_target_link_to_non_concept_comment(self) -> None:
        issue = valid_issue()
        wrong_url = f"{BASE_URL}#issuecomment-1"
        issue["comments"][2]["body"] = detailed_plan(
            concept_basis=f"Target Concept: [wrong]({wrong_url})"
        )
        self.assert_invalid(issue, "does not link an earlier Concept comment")

    def test_rejects_wrong_issue_scope(self) -> None:
        issue = valid_issue()
        issue["comments"][-1]["body"] = go_ahead(issue_number=102)
        self.assert_invalid(issue, "does not authorize Issue #101")

    def test_uses_comment_timestamps_not_export_order(self) -> None:
        issue = valid_issue()
        issue["comments"] = list(reversed(deepcopy(issue["comments"])))
        result = self.run_cli(issue)
        self.assertEqual(result.returncode, 0, result.stderr)

    def test_uses_export_order_when_comment_timestamps_match(self) -> None:
        issue = valid_issue()
        issue["comments"][2]["createdAt"] = "2026-08-07T00:03:00Z"
        issue["comments"][3]["createdAt"] = "2026-08-07T00:03:00Z"
        result = self.run_cli(issue)
        self.assertEqual(result.returncode, 0, result.stderr)


if __name__ == "__main__":
    unittest.main()
