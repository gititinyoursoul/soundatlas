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
from typing import Any

from check_issue_completion import ValidationError, validate_completion_text

DEFAULT_OWNER = "gititinyoursoul"
DEFAULT_PROJECT_NUMBER = 1
COMMIT_PATTERN = re.compile(r"(?i)\bcommit(?:\s+range)?\s*[:]?\s*`?([0-9a-f]{7,40})`?")


class ReconciliationError(RuntimeError):
    """Raised when completion evidence or a required GitHub action is missing."""


Run = Callable[[list[str], str | None], str]


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
        raise ReconciliationError(f"{' '.join(command[:3])} returned invalid JSON") from exc


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
        raise ReconciliationError(f"latest Implementation Report is not completion-ready: {exc}") from exc
    return reports[-1]


def report_commit(report: str) -> str | None:
    match = COMMIT_PATTERN.search(report)
    return match.group(1) if match else None


def remote_contains(run: Run, commit: str, remote: str, branch: str) -> tuple[bool, str]:
    remote_ref = f"{remote}/{branch}"
    remote_head = run(["git", "rev-parse", remote_ref], None).strip()
    try:
        run(["git", "merge-base", "--is-ancestor", commit, remote_head], None)
    except ReconciliationError:
        return False, remote_head
    return True, remote_head


def reviewed_revision(run: Run, commit: str | None, commit_range: str | None) -> tuple[str, str]:
    """Resolve one reviewed commit or a validated inclusive integration range."""
    if commit:
        return run(["git", "rev-parse", commit], None).strip(), commit
    if not commit_range or ".." not in commit_range:
        raise ReconciliationError("complete requires --commit or --range <base>..<head>")
    base, head = commit_range.split("..", 1)
    if not base or not head:
        raise ReconciliationError("range must use <base>..<head>")
    try:
        run(["git", "merge-base", "--is-ancestor", base, head], None)
    except ReconciliationError as exc:
        raise ReconciliationError(f"reviewed range is not ordered: {commit_range}") from exc
    return run(["git", "rev-parse", head], None).strip(), commit_range


def issue_data(run: Run, repo: str, issue: int) -> dict[str, Any]:
    result = json_output(
        run,
        ["gh", "issue", "view", str(issue), "--repo", repo, "--json", "number,title,state,comments,url"],
    )
    if not isinstance(result, dict):
        raise ReconciliationError(f"Issue #{issue} response is not an object")
    return result


def project_items(run: Run, owner: str, project_number: int) -> list[dict[str, Any]]:
    result = json_output(
        run,
        ["gh", "project", "item-list", str(project_number), "--owner", owner, "--limit", "500", "--format", "json"],
    )
    items = result.get("items") if isinstance(result, dict) else None
    if not isinstance(items, list):
        raise ReconciliationError("Project item list has no items array")
    return [item for item in items if isinstance(item, dict)]


def audit(run: Run, repo: str, owner: str, project_number: int, remote: str, branch: str) -> int:
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
                raise ReconciliationError(f"{commit} is not reachable from {remote}/{branch}")
        except ReconciliationError as exc:
            print(f"# {issue} not a completion candidate: {exc}")
            continue
        candidates += 1
        print(f"# {issue} candidate: {commit} — {title}")
    print(f"Audit complete: {candidates} candidate(s); no GitHub state was changed.")
    return 0


def project_ids(run: Run, owner: str, project_number: int) -> tuple[str, str, str]:
    projects = json_output(run, ["gh", "project", "list", "--owner", owner, "--format", "json"])
    project = next(
        (value for value in projects.get("projects", []) if value.get("number") == project_number), None
    )
    if not isinstance(project, dict) or not isinstance(project.get("id"), str):
        raise ReconciliationError(f"Project #{project_number} was not found for {owner}")
    fields = json_output(run, ["gh", "project", "field-list", str(project_number), "--owner", owner, "--format", "json"])
    status = next((field for field in fields.get("fields", []) if field.get("name") == "Status"), None)
    if not isinstance(status, dict) or not isinstance(status.get("id"), str):
        raise ReconciliationError("Project has no Status field")
    done = next((option for option in status.get("options", []) if option.get("name") == "Done"), None)
    if not isinstance(done, dict) or not isinstance(done.get("id"), str):
        raise ReconciliationError("Project Status field has no Done option")
    return project["id"], status["id"], done["id"]


def complete(args: argparse.Namespace, run: Run) -> int:
    if not args.push_authorized:
        raise ReconciliationError("complete requires --push-authorized")
    if not args.working_tree_verified:
        raise ReconciliationError("complete requires --working-tree-verified")
    data = issue_data(run, args.repo, args.issue)
    if data.get("state") != "OPEN":
        raise ReconciliationError(f"Issue #{args.issue} is not open")
    comments = data.get("comments", [])
    if not isinstance(comments, list):
        raise ReconciliationError("Issue comments are unavailable")
    if completion_comments(comments):
        raise ReconciliationError("Issue already has a completion comment; do not rewrite completion evidence")
    report = accepted_report(comments)
    commit, reviewed_range = reviewed_revision(run, args.commit, args.commit_range)
    if args.commit:
        recorded_commit = report_commit(report)
        if not recorded_commit:
            raise ReconciliationError("latest Implementation Report does not name the reviewed commit")
        recorded_revision = run(["git", "rev-parse", recorded_commit], None).strip()
        if recorded_revision != commit:
            raise ReconciliationError("named commit does not match the latest Implementation Report")
    elif reviewed_range not in report:
        raise ReconciliationError("latest Implementation Report does not name the reviewed integration range")
    validate_completion_text(report, commit, 1, True)
    published, remote_head = remote_contains(run, commit, args.remote, args.branch)
    if not published:
        raise ReconciliationError(f"{commit} is not reachable from {args.remote}/{args.branch}")
    if args.frontend_ci_run:
        ci = json_output(run, ["gh", "run", "view", args.frontend_ci_run, "--repo", args.repo, "--json", "conclusion,url"])
        if ci.get("conclusion") != "success":
            raise ReconciliationError(f"Frontend CI run is not successful: {ci.get('url', args.frontend_ci_run)}")

    items = project_items(run, args.owner, args.project_number)
    item = next(
        (value for value in items if isinstance(value.get("content"), dict) and value["content"].get("number") == args.issue),
        None,
    )
    if not isinstance(item, dict) or not isinstance(item.get("id"), str):
        raise ReconciliationError(f"Issue #{args.issue} is not in Project #{args.project_number}")
    project_id, status_id, done_id = project_ids(run, args.owner, args.project_number)
    comment = (
        "## Completed\n\n"
        f"- Commit: `{commit}`\n"
        f"- Issue: #{args.issue}\n"
        "- Acceptance criteria: complete\n"
        f"- Verification: accepted Implementation Report; reviewed `{reviewed_range}` is published on `{args.remote}/{args.branch}` at `{remote_head}`"
    )
    if args.frontend_ci_run:
        comment += f"; successful Frontend CI run `{args.frontend_ci_run}`"
    comment += "\n"
    run(
        ["gh", "api", "--method", "POST", f"repos/{args.repo}/issues/{args.issue}/comments", "--input", "-"],
        json.dumps({"body": comment}),
    )
    run(
        ["gh", "project", "item-edit", "--id", item["id"], "--project-id", project_id, "--field-id", status_id, "--single-select-option-id", done_id],
        None,
    )
    run(["gh", "issue", "close", str(args.issue), "--repo", args.repo], None)
    print(f"Completed Issue #{args.issue} at published commit {commit}.")
    return 0


def parser() -> argparse.ArgumentParser:
    command_parser = argparse.ArgumentParser(description=__doc__)
    command_parser.add_argument("--repo", default="gititinyoursoul/soundatlas")
    command_parser.add_argument("--owner", default=DEFAULT_OWNER)
    command_parser.add_argument("--project-number", type=int, default=DEFAULT_PROJECT_NUMBER)
    command_parser.add_argument("--remote", default="origin")
    command_parser.add_argument("--branch", default="main")
    subparsers = command_parser.add_subparsers(dest="command", required=True)

    subparsers.add_parser("audit", help="report published completion candidates without mutation")
    complete_parser = subparsers.add_parser("complete", help="complete one verified, published Issue")
    complete_parser.add_argument("--issue", type=int, required=True)
    revision = complete_parser.add_mutually_exclusive_group(required=True)
    revision.add_argument("--commit")
    revision.add_argument("--range", dest="commit_range", help="reviewed <base>..<head> integration range")
    complete_parser.add_argument("--push-authorized", action="store_true")
    complete_parser.add_argument("--working-tree-verified", action="store_true")
    complete_parser.add_argument("--frontend-ci-run", help="required when the delivered range triggers Frontend CI")
    return command_parser


def main(argv: list[str] | None = None, run: Run = run_command) -> int:
    args = parser().parse_args(argv)
    try:
        if args.command == "audit":
            return audit(run, args.repo, args.owner, args.project_number, args.remote, args.branch)
        return complete(args, run)
    except (ReconciliationError, ValidationError) as exc:
        print(f"Reconciliation failed: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
