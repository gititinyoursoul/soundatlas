#!/usr/bin/env python3
"""Validate SoundAtlas Issue readiness artifacts without mutating GitHub."""

from __future__ import annotations

import argparse
import json
import re
import sys
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Any

BASE_PLAN_SECTIONS = ("## Plan", "## Non-Goals", "## Open Questions")
DETAILED_PLAN_SECTIONS = (
    "## Assumptions",
    "## Acceptance Criteria Changes",
    "## Implementation Steps",
    "## Validation",
)
PLAN_HEADINGS = ("## Plan Update", "## Detailed Plan Update")
REVISION_HEADINGS = ("## Intake Revision", "## Concept")


class ValidationError(ValueError):
    """Raised when Issue artifacts do not satisfy the readiness contract."""


@dataclass(frozen=True)
class IssueComment:
    body: str
    url: str
    created_at: datetime
    original_index: int


def order_key(comment: IssueComment) -> tuple[datetime, int]:
    return comment.created_at, comment.original_index


def decode_json(text: str, source: str) -> dict[str, Any]:
    try:
        value = json.loads(text)
    except json.JSONDecodeError as exc:
        raise ValidationError(f"invalid JSON in {source}: {exc}") from exc
    if not isinstance(value, dict):
        raise ValidationError("Issue export must be a JSON object")
    return value


def read_json(path: str) -> dict[str, Any]:
    if path == "-":
        return decode_json(sys.stdin.read(), "standard input")
    source = Path(path)
    try:
        return decode_json(source.read_text(encoding="utf-8"), str(source))
    except OSError as exc:
        raise ValidationError(f"cannot read {source}: {exc}") from exc


def parse_timestamp(value: object, index: int) -> datetime:
    if not isinstance(value, str) or not value:
        raise ValidationError(f"comment {index} has no createdAt timestamp")
    try:
        parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
    except ValueError as exc:
        raise ValidationError(f"comment {index} has an invalid createdAt timestamp") from exc
    if parsed.tzinfo is None:
        raise ValidationError(f"comment {index} createdAt timestamp has no timezone")
    return parsed


def parse_comments(value: object) -> list[IssueComment]:
    if not isinstance(value, list):
        raise ValidationError("Issue export has no comments list")
    comments: list[IssueComment] = []
    for index, item in enumerate(value, start=1):
        if not isinstance(item, dict):
            raise ValidationError(f"comment {index} must be a JSON object")
        body = item.get("body")
        url = item.get("url")
        if not isinstance(body, str):
            raise ValidationError(f"comment {index} has no body")
        if not isinstance(url, str) or not url:
            raise ValidationError(f"comment {index} has no URL")
        comments.append(
            IssueComment(
                body=body,
                url=url,
                created_at=parse_timestamp(item.get("createdAt"), index),
                original_index=index,
            )
        )
    return sorted(comments, key=order_key)


def first_heading(text: str) -> str | None:
    for line in text.splitlines():
        stripped = line.strip()
        if stripped:
            return stripped if stripped.startswith("## ") else None
    return None


def section(text: str, heading: str) -> str:
    match = re.search(rf"(?m)^{re.escape(heading)}\s*$", text)
    if not match:
        raise ValidationError(f"missing required section: {heading}")
    remainder = text[match.end() :]
    next_heading = re.search(r"(?m)^##\s+", remainder)
    return remainder if not next_heading else remainder[: next_heading.start()]


def validate_intake(issue_body: str) -> None:
    for heading in ("## Task", "## Context", "## Acceptance Criteria"):
        section(issue_body, heading)
    acceptance = section(issue_body, "## Acceptance Criteria")
    if not re.search(r"(?m)^\s*- \[[ xX]\]\s+\S", acceptance):
        raise ValidationError("Acceptance Criteria contains no checklist items")


def validate_grill_review(comment: IssueComment) -> None:
    body = comment.body
    if not re.search(
        r"(?m)^\*\*Stage:\*\*\s*(Intake|Plan|Implementation|Implementation Review)\s*$",
        body,
    ):
        raise ValidationError(f"Grill-Me Review is missing a valid Stage: {comment.url}")
    finding_count = len(re.findall(r"\*\*Finding:\*\*", body))
    decision_count = len(re.findall(r"\*\*Decision:\*\*", body))
    if finding_count == 0:
        raise ValidationError(f"Grill-Me Review contains no findings: {comment.url}")
    if finding_count != decision_count:
        raise ValidationError(
            f"Grill-Me Review has {finding_count} finding(s) and "
            f"{decision_count} decision(s): {comment.url}"
        )
    decisions = re.findall(r"(?m)^\s*\*\*Decision:\*\*\s*(.+?)\s*$", body)
    if len(decisions) != decision_count or any(
        not re.match(
            r"(?i)^(?:(?:Confirmed|Deferred|Rejected) by human|Blocked(?: by human)?)\b",
            decision,
        )
        for decision in decisions
    ):
        raise ValidationError(
            f"Grill-Me Review contains an unconfirmed or malformed Decision: {comment.url}"
        )
    if not re.search(r"(?m)^\*\*Next step:\*\*\s*\S", body):
        raise ValidationError(f"Grill-Me Review is missing Next step: {comment.url}")


def open_questions_are_non_blocking(text: str) -> bool:
    content = section(text, "## Open Questions").strip()
    if re.match(r"(?i)^(?:[-*]\s*)?None\b", content):
        return True
    lines = [line.strip() for line in content.splitlines() if line.strip()]
    return bool(lines) and all(
        re.search(r"(?i)\bdeferred by human\b", line)
        and re.search(r"(?i)\bnon[- ]blocking\b", line)
        for line in lines
    )


def validate_plan(comment: IssueComment) -> str | None:
    body = comment.body
    heading = first_heading(body)
    required = BASE_PLAN_SECTIONS
    if heading == "## Detailed Plan Update":
        required += DETAILED_PLAN_SECTIONS
    for required_heading in required:
        section(body, required_heading)
    if not open_questions_are_non_blocking(body):
        raise ValidationError(
            "Open Questions must be None or explicitly deferred by the human as non-blocking"
        )

    target_concept = re.search(
        r"(?m)^Target Concept:\s*\[[^\]]+\]\((https?://[^)]+)\)\s*$", body
    )
    concept_not_required = re.search(
        r"(?m)^Concept Work:\s*Not required\s*[—-]\s*\S.+$", body
    )
    if not target_concept and not concept_not_required:
        raise ValidationError(
            "Plan must reference its Target Concept or explain why Concept Work was not required"
        )
    return None if not target_concept else target_concept.group(1)


def review_next_step(comment: IssueComment) -> str:
    next_step = re.search(r"(?m)^\*\*Next step:\*\*\s*(.+?)\s*$", comment.body)
    return "" if not next_step else next_step.group(1)


def review_routes_backward(comment: IssueComment) -> bool:
    return bool(
        re.search(
            r"(?i)\b(blocked|concept work|record(?: the)? .{0,40}concept|plan update|return to concept|return to planning)\b",
            review_next_step(comment),
        )
    )


def validate_go_ahead(comment: IssueComment, issue_number: int, plan_url: str) -> None:
    plan = re.search(r"(?m)^- Plan:\s*\[[^\]]+\]\((https?://[^)]+)\)\s*$", comment.body)
    if not plan:
        raise ValidationError("Proceed to Implementation is missing a linked Plan")
    if plan.group(1) != plan_url:
        raise ValidationError("Proceed to Implementation does not link the latest Plan Update")
    if not re.search(
        r"(?m)^- Human decision:\s*Proceed with this plan\.\s*$", comment.body
    ):
        raise ValidationError(
            "Proceed to Implementation is missing the confirmed human decision"
        )
    scope = re.search(r"(?m)^- Authorized scope:\s*(\S.+?)\s*$", comment.body)
    if not scope:
        raise ValidationError("Proceed to Implementation is missing Authorized scope")
    if not re.search(rf"(?:\bIssue\s*)?#{issue_number}\b", scope.group(1)):
        raise ValidationError(
            f"Proceed to Implementation does not authorize Issue #{issue_number}"
        )


def validate_issue(issue: dict[str, Any], *, require_grill_review: bool = False) -> str:
    number = issue.get("number")
    body = issue.get("body")
    if type(number) is not int or number < 1:
        raise ValidationError("Issue export has no valid Issue number")
    if not isinstance(body, str):
        raise ValidationError("Issue export has no body")
    validate_intake(body)
    comments = parse_comments(issue.get("comments"))

    reviews = [comment for comment in comments if first_heading(comment.body) == "## Grill-Me Review"]
    plans = [comment for comment in comments if first_heading(comment.body) in PLAN_HEADINGS]
    go_aheads = [
        comment for comment in comments if first_heading(comment.body) == "## Proceed to Implementation"
    ]

    if require_grill_review and not reviews and not any(
        "Grill-Me check: clean" in comment.body for comment in plans
    ):
        raise ValidationError("no completed Grill-Me Review or inline clean check was found")
    for review in reviews:
        validate_grill_review(review)
    if not plans:
        raise ValidationError("no Plan Update or Detailed Plan Update was found")

    latest_plan = plans[-1]
    target_concept_url = validate_plan(latest_plan)

    if target_concept_url and "#issuecomment-" in target_concept_url:
        matching_concepts = [
            comment
            for comment in comments
            if comment.url == target_concept_url
            and first_heading(comment.body) == "## Concept"
            and order_key(comment) < order_key(latest_plan)
        ]
        if not matching_concepts:
            raise ValidationError("Target Concept does not link an earlier Concept comment")

    reviews_before_plan = [
        review for review in reviews if order_key(review) < order_key(latest_plan)
    ]
    if reviews_before_plan:
        latest_review = reviews_before_plan[-1]
        next_step = review_next_step(latest_review)
        if re.search(r"(?i)\bblocked\b", next_step):
            raise ValidationError("the latest pre-Plan Grill-Me Review remains blocked")
        if re.search(
            r"(?i)\b(concept work|record(?: the)? .{0,40}concept|return to concept)\b",
            next_step,
        ):
            concepts_after_review = [
                comment
                for comment in comments
                if first_heading(comment.body) == "## Concept"
                and order_key(latest_review) < order_key(comment) < order_key(latest_plan)
            ]
            if not concepts_after_review:
                raise ValidationError(
                    "the latest pre-Plan Grill-Me Review requires a later Concept"
                )

    later_revisions = [
        comment
        for comment in comments
        if order_key(comment) > order_key(latest_plan)
        and first_heading(comment.body) in REVISION_HEADINGS
    ]
    if later_revisions:
        raise ValidationError(
            f"latest Plan Update is superseded by {first_heading(later_revisions[-1].body)}"
        )

    later_backward_reviews = [
        review
        for review in reviews
        if order_key(review) > order_key(latest_plan) and review_routes_backward(review)
    ]
    if later_backward_reviews:
        raise ValidationError("a later Grill-Me Review routes the Issue away from implementation")

    if not go_aheads:
        raise ValidationError("no Proceed to Implementation record was found")
    latest_go_ahead = go_aheads[-1]
    if order_key(latest_go_ahead) <= order_key(latest_plan):
        raise ValidationError("Proceed to Implementation must follow the latest Plan Update")
    validate_go_ahead(latest_go_ahead, number, latest_plan.url)

    invalidators_after_go_ahead = [
        comment
        for comment in comments
        if order_key(comment) > order_key(latest_go_ahead)
        and (
            first_heading(comment.body) in (*PLAN_HEADINGS, *REVISION_HEADINGS)
            or (
                first_heading(comment.body) == "## Grill-Me Review"
                and review_routes_backward(comment)
            )
        )
    ]
    if invalidators_after_go_ahead:
        raise ValidationError("a later canonical revision or blocking decision invalidates the go-ahead")

    return latest_plan.url


def parser() -> argparse.ArgumentParser:
    command_parser = argparse.ArgumentParser(description=__doc__)
    command_parser.add_argument(
        "--file", required=True, help="GitHub Issue JSON export, or - for standard input"
    )
    command_parser.add_argument(
        "--require-grill-review",
        action="store_true",
        help="require a completed Grill-Me Review or inline clean check",
    )
    return command_parser


def main(argv: list[str] | None = None) -> int:
    args = parser().parse_args(argv)
    try:
        issue = read_json(args.file)
        plan_url = validate_issue(issue, require_grill_review=args.require_grill_review)
    except ValidationError as exc:
        print(f"Validation failed: {exc}", file=sys.stderr)
        return 1

    print(f"Validation passed: ready to implement from {plan_url}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
