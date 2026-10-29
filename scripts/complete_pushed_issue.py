"""Audit or complete a published SoundAtlas Issue after explicit invocation.

This helper never reacts to a push on its own.  ``audit`` is read-only; the
``complete`` command requires explicit push and working-tree attestations and
performs the documented comment, Project status, and Issue-closure sequence.
"""

import argparse
import json
import re
import subprocess
import sys
from collections.abc import Callable
from pathlib import Path
from typing import Any

from check_issue_completion import ValidationError, validate_completion_text

DEFAULT_OWNER = "gititinyoursoul"
DEFAULT_PROJECT_NUMBER = 1
COMMIT_PATTERN = re.compile(r"(?i)\bcommit(?:\s+range)?\s*[:]?\s*`?([0-9a-f]{7,40})`?")
PROJECT_HELPER = str(Path(__file__).with_name("gh_project.py"))


class ReconciliationError(RuntimeError):
    """Raised when completion evidence or a required GitHub action is missing."""


Run = Callable[[list[str], str | None], str]


def project_command(*arguments: str) -> list[str]:
    """Route Project commands through the dedicated credential helper."""
    return [sys.executable, PROJECT_HELPER, *arguments]


def require_default_branch(run: Run, repo: str, branch: str) -> None:
    data = json_output(run, ["gh", "repo", "view", repo, "--json", "defaultBranchRef"])
    default = data.get("defaultBranchRef") if isinstance(data, dict) else None
    if not isinstance(default, dict) or default.get("name") != branch:
        raise ReconciliationError("PR target is not the repository default branch")


def run_command(command: list[str], input_text: str | None = None) -> str:
    result = subprocess.run(
        command,
        input=input_text,
        capture_output=True,
        text=True,
        check=False,
    )
    if result.returncode:
        details = result.stderr.strip() or result.stdout.strip() or "no command output"
        raise ReconciliationError(f"{' '.join(command[:3])} failed: {details}")
    return result.stdout


def json_output(run: Run, command: list[str]) -> Any:
    try:
        return json.loads(run(command, None))
    except json.JSONDecodeError as exc:
        raise ReconciliationError(
            f"{' '.join(command[:3])} returned invalid JSON"
        ) from exc


def first_heading(body: str) -> str | None:
    for line in body.splitlines():
        if line.strip():
            return line.strip()
    return None


def implementation_reports(comments: list[dict[str, Any]]) -> list[str]:
    return [
        str(comment.get("body", ""))
        for comment in comments
        if first_heading(str(comment.get("body", ""))) == "## Implementation Report"
    ]


def completion_comments(comments: list[dict[str, Any]]) -> int:
    return sum(
        first_heading(str(comment.get("body", ""))) == "## Completed"
        for comment in comments
    )


def accepted_report(comments: list[dict[str, Any]]) -> str:
    reports = implementation_reports(comments)
    if not reports:
        raise ReconciliationError("Issue has no Implementation Report")
    try:
        validate_completion_text(reports[-1], "abcdef0", 1, True)
    except ValidationError as exc:
        raise ReconciliationError(
            f"latest Implementation Report is not completion-ready: {exc}"
        ) from exc
    return reports[-1]


def report_commit(report: str) -> str | None:
    match = COMMIT_PATTERN.search(report)
    return match.group(1) if match else None


def remote_contains(
    run: Run, commit: str, remote: str, branch: str
) -> tuple[bool, str]:
    remote_ref = f"{remote}/{branch}"
    remote_head = run(["git", "rev-parse", remote_ref], None).strip()
    try:
        run(["git", "merge-base", "--is-ancestor", commit, remote_head], None)
    except ReconciliationError:
        return False, remote_head
    return True, remote_head


def reviewed_revision(
    run: Run, commit: str | None, commit_range: str | None
) -> tuple[str, str]:
    """Resolve one reviewed commit or a validated inclusive integration range."""
    if commit:
        return run(["git", "rev-parse", commit], None).strip(), commit
    if not commit_range or ".." not in commit_range:
        raise ReconciliationError(
            "complete requires --commit or --range <base>..<head>"
        )
    base, head = commit_range.split("..", 1)
    if not base or not head:
        raise ReconciliationError("range must use <base>..<head>")
    try:
        run(["git", "merge-base", "--is-ancestor", base, head], None)
    except ReconciliationError as exc:
        raise ReconciliationError(
            f"reviewed range is not ordered: {commit_range}"
        ) from exc
    return run(["git", "rev-parse", head], None).strip(), commit_range


def issue_data(run: Run, repo: str, issue: int) -> dict[str, Any]:
    result = json_output(
        run,
        [
            "gh",
            "issue",
            "view",
            str(issue),
            "--repo",
            repo,
            "--json",
            "number,title,state,comments,url",
        ],
    )
    if not isinstance(result, dict):
        raise ReconciliationError(f"Issue #{issue} response is not an object")
    return result


def project_items(run: Run, owner: str, project_number: int) -> list[dict[str, Any]]:
    result = json_output(
        run,
        project_command(
            "item-list",
            str(project_number),
            "--owner",
            owner,
            "--limit",
            "500",
            "--format",
            "json",
        ),
    )
    items = result.get("items") if isinstance(result, dict) else None
    if not isinstance(items, list):
        raise ReconciliationError("Project item list has no items array")
    return [item for item in items if isinstance(item, dict)]


def audit(
    run: Run, repo: str, owner: str, project_number: int, remote: str, branch: str
) -> int:
    candidates = 0
    for item in project_items(run, owner, project_number):
        if item.get("status") != "Locally Implemented":
            continue
        content = item.get("content")
        if not isinstance(content, dict) or not isinstance(content.get("number"), int):
            continue
        issue = int(content["number"])
        title = str(content.get("title", "Untitled"))
        try:
            report = accepted_report(issue_data(run, repo, issue).get("comments", []))
            commit = report_commit(report)
            if not commit:
                raise ReconciliationError("latest report does not name a commit")
            published, _ = remote_contains(run, commit, remote, branch)
            if not published:
                raise ReconciliationError(
                    f"{commit} is not reachable from {remote}/{branch}"
                )
        except ReconciliationError as exc:
            print(f"# {issue} not a completion candidate: {exc}")
            continue
        candidates += 1
        print(f"# {issue} candidate: {commit} — {title}")
    print(f"Audit complete: {candidates} candidate(s); no GitHub state was changed.")
    return 0


def project_ids(run: Run, owner: str, project_number: int) -> tuple[str, str, str]:
    projects = json_output(
        run, project_command("list", "--owner", owner, "--format", "json")
    )
    project = next(
        (
            value
            for value in projects.get("projects", [])
            if value.get("number") == project_number
        ),
        None,
    )
    if not isinstance(project, dict) or not isinstance(project.get("id"), str):
        raise ReconciliationError(
            f"Project #{project_number} was not found for {owner}"
        )
    fields = json_output(
        run,
        project_command(
            "field-list", str(project_number), "--owner", owner, "--format", "json"
        ),
    )
    status = next(
        (field for field in fields.get("fields", []) if field.get("name") == "Status"),
        None,
    )
    if not isinstance(status, dict) or not isinstance(status.get("id"), str):
        raise ReconciliationError("Project has no Status field")
    done = next(
        (
            option
            for option in status.get("options", [])
            if option.get("name") == "Done"
        ),
        None,
    )
    if not isinstance(done, dict) or not isinstance(done.get("id"), str):
        raise ReconciliationError("Project Status field has no Done option")
    return project["id"], status["id"], done["id"]


def complete(args: argparse.Namespace, run: Run) -> int:
    if args.merged_pr and not args.merge_authorized:
        raise ReconciliationError("PR completion requires --merge-authorized")
    if not args.merged_pr and not args.push_authorized:
        raise ReconciliationError("non-PR completion requires --push-authorized")
    if not args.working_tree_verified:
        raise ReconciliationError("complete requires --working-tree-verified")
    data = issue_data(run, args.repo, args.issue)
    expected_state = "CLOSED" if args.merged_pr else "OPEN"
    if data.get("state") != expected_state:
        raise ReconciliationError(f"Issue #{args.issue} is not {expected_state.lower()}")
    comments = data.get("comments", [])
    if not isinstance(comments, list):
        raise ReconciliationError("Issue comments are unavailable")
    if completion_comments(comments) and not args.merged_pr:
        raise ReconciliationError(
            "Issue already has a completion comment; do not rewrite completion evidence"
        )
    report = accepted_report(comments)
    commit, reviewed_range = reviewed_revision(run, args.commit, args.commit_range)
    if args.commit:
        recorded_commit = report_commit(report)
        if not recorded_commit:
            raise ReconciliationError(
                "latest Implementation Report does not name the reviewed commit"
            )
        recorded_revision = run(["git", "rev-parse", recorded_commit], None).strip()
        if recorded_revision != commit:
            raise ReconciliationError(
                "named commit does not match the latest Implementation Report"
            )
    elif reviewed_range not in report:
        raise ReconciliationError(
            "latest Implementation Report does not name the reviewed integration range"
        )
    validate_completion_text(report, commit, 1, True)
    published_commit = commit
    if args.merged_pr:
        if not args.post_merge_verified:
            raise ReconciliationError("PR completion requires --post-merge-verified")
        require_default_branch(run, args.repo, args.branch)
        pr = json_output(run, ["gh", "pr", "view", str(args.merged_pr), "--repo", args.repo,
                               "--json", "state,baseRefName,headRefOid,mergeCommit,closingIssuesReferences"])
        linked = pr.get("closingIssuesReferences", [])
        merge_commit = pr.get("mergeCommit") or {}
        def same_issue(issue: Any) -> bool:
            if not isinstance(issue, dict) or issue.get("number") != args.issue:
                return False
            repository = issue.get("repository") or {}
            owner = repository.get("owner") or {}
            return f"{owner.get('login', '')}/{repository.get('name', '')}".lower() == args.repo.lower()

        if (not isinstance(linked, list) or pr.get("state") != "MERGED" or pr.get("baseRefName") != args.branch
            or pr.get("headRefOid") != commit
            or not any(same_issue(issue) for issue in linked)
            or not merge_commit.get("oid")):
            raise ReconciliationError("merged PR does not match the reviewed revision, branch, and Issue")
        published_commit = merge_commit["oid"]
    published, remote_head = remote_contains(run, published_commit, args.remote, args.branch)
    if not published:
        raise ReconciliationError(
            f"{commit} is not reachable from {args.remote}/{args.branch}"
        )
    if args.frontend_ci_run:
        ci = json_output(
            run,
            [
                "gh",
                "run",
                "view",
                args.frontend_ci_run,
                "--repo",
                args.repo,
                "--json",
                "conclusion,url",
            ],
        )
        if ci.get("conclusion") != "success":
            raise ReconciliationError(
                f"Frontend CI run is not successful: {ci.get('url', args.frontend_ci_run)}"
            )

    items = project_items(run, args.owner, args.project_number)
    item = next(
        (
            value
            for value in items
            if isinstance(value.get("content"), dict)
            and value["content"].get("number") == args.issue
        ),
        None,
    )
    if not isinstance(item, dict) or not isinstance(item.get("id"), str):
        raise ReconciliationError(
            f"Issue #{args.issue} is not in Project #{args.project_number}"
        )
    project_id, status_id, done_id = project_ids(run, args.owner, args.project_number)
    verification = (
        f"accepted Implementation Report; reviewed `{reviewed_range}` and merged `{published_commit}` on `{args.remote}/{args.branch}`; post-merge verification passed"
        if args.merged_pr
        else f"accepted Implementation Report; reviewed `{reviewed_range}` and published `{published_commit}` on `{args.remote}/{args.branch}` at `{remote_head}`"
    )
    comment = (
        "## Completed\n\n"
        f"- Commit: `{commit}`\n"
        f"- Issue: #{args.issue}\n"
        "- Acceptance criteria: complete\n"
        f"- Verification: {verification}"
    )
    if args.frontend_ci_run:
        comment += f"; successful Frontend CI run `{args.frontend_ci_run}`"
    comment += "\n"
    if args.merged_pr:
        comment += f"- Merged PR: #{args.merged_pr}; published commit: `{published_commit}`\n"
    existing = [str(c.get("body", "")) for c in comments if first_heading(str(c.get("body", ""))) == "## Completed"]
    if len(existing) > 1 or (existing and existing[0] != comment):
        raise ReconciliationError("existing completion evidence does not match this delivery")
    if not existing:
        run(
            ["gh", "api", "--method", "POST",
             f"repos/{args.repo}/issues/{args.issue}/comments", "--input", "-"],
            json.dumps({"body": comment}),
        )
    if item.get("status") != "Done":
        run(
            project_command(
                "item-edit", "--id", item["id"], "--project-id", project_id,
                "--field-id", status_id, "--single-select-option-id", done_id,
            ),
            None,
        )
    if data.get("state") == "OPEN":
        run(["gh", "issue", "close", str(args.issue), "--repo", args.repo], None)
    print(f"Completed Issue #{args.issue} at published commit {published_commit}.")
    return 0


def record_pr_failure(args: argparse.Namespace, run: Run) -> int:
    """Reopen one affected Issue and record an observed post-merge failure."""
    if not args.merge_authorized or not args.failure.strip():
        raise ReconciliationError("failure recovery requires merge authorization and a failure description")
    require_default_branch(run, args.repo, args.branch)
    data = issue_data(run, args.repo, args.issue)
    comments = data.get("comments")
    if not isinstance(comments, list) or data.get("state") not in ("OPEN", "CLOSED"):
        raise ReconciliationError("Issue state or comments unavailable")
    pr = json_output(run, ["gh", "pr", "view", str(args.merged_pr), "--repo", args.repo,
                           "--json", "state,baseRefName,closingIssuesReferences"])
    linked = pr.get("closingIssuesReferences")
    if not isinstance(linked, list) or pr.get("state") != "MERGED" or pr.get("baseRefName") != args.branch:
        raise ReconciliationError("PR is not merged into the intended branch")
    def matches(issue: Any) -> bool:
        if not isinstance(issue, dict) or issue.get("number") != args.issue:
            return False
        repo = issue.get("repository") or {}
        owner = repo.get("owner") or {}
        return f"{owner.get('login', '')}/{repo.get('name', '')}".lower() == args.repo.lower()
    if not any(matches(issue) for issue in linked):
        raise ReconciliationError("PR does not link this Issue")
    body = f"## Post-merge verification failure\n\n- PR: #{args.merged_pr}\n- Issue: #{args.issue}\n- Failure: {args.failure.strip()}\n"
    prior = [str(comment.get("body", "")) for comment in comments if first_heading(str(comment.get("body", ""))) == "## Post-merge verification failure"]
    if prior and body not in prior:
        raise ReconciliationError("existing failure evidence differs; inspect before recovery")
    if data["state"] == "CLOSED":
        run(["gh", "issue", "reopen", str(args.issue), "--repo", args.repo], None)
    if body not in prior:
        run(["gh", "api", "--method", "POST", f"repos/{args.repo}/issues/{args.issue}/comments", "--input", "-"], json.dumps({"body": body}))
    print(f"Recorded verification failure for Issue #{args.issue}.")
    return 0


def parser() -> argparse.ArgumentParser:
    command_parser = argparse.ArgumentParser(description=__doc__)
    command_parser.add_argument("--repo", default="gititinyoursoul/soundatlas")
    command_parser.add_argument("--owner", default=DEFAULT_OWNER)
    command_parser.add_argument(
        "--project-number", type=int, default=DEFAULT_PROJECT_NUMBER
    )
    command_parser.add_argument("--remote", default="origin")
    command_parser.add_argument("--branch", default="main")
    subparsers = command_parser.add_subparsers(dest="command", required=True)

    subparsers.add_parser(
        "audit", help="report published completion candidates without mutation"
    )
    complete_parser = subparsers.add_parser(
        "complete", help="complete one verified, published Issue"
    )
    complete_parser.add_argument("--issue", type=int, required=True)
    revision = complete_parser.add_mutually_exclusive_group(required=True)
    revision.add_argument("--commit")
    revision.add_argument(
        "--range", dest="commit_range", help="reviewed <base>..<head> integration range"
    )
    complete_parser.add_argument("--push-authorized", action="store_true")
    complete_parser.add_argument("--merged-pr", type=int, help="merged PR closing this Issue")
    complete_parser.add_argument("--merge-authorized", action="store_true")
    complete_parser.add_argument("--post-merge-verified", action="store_true", help="attest CI and applicable deployment verification")
    complete_parser.add_argument("--working-tree-verified", action="store_true")
    complete_parser.add_argument(
        "--frontend-ci-run",
        help="required when the delivered range triggers Frontend CI",
    )
    failure_parser = subparsers.add_parser("record-pr-failure", help="reopen one affected Issue and record post-merge verification failure")
    failure_parser.add_argument("--issue", type=int, required=True)
    failure_parser.add_argument("--merged-pr", type=int, required=True)
    failure_parser.add_argument("--failure", required=True)
    failure_parser.add_argument("--merge-authorized", action="store_true")
    return command_parser


def main(argv: list[str] | None = None, run: Run = run_command) -> int:
    args = parser().parse_args(argv)
    try:
        if args.command == "audit":
            return audit(
                run,
                args.repo,
                args.owner,
                args.project_number,
                args.remote,
                args.branch,
            )
        if args.command == "record-pr-failure":
            return record_pr_failure(args, run)
        return complete(args, run)
    except (ReconciliationError, ValidationError) as exc:
        print(f"Reconciliation failed: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
