---
name: soundatlas-documentation-implementation
description: Plan and implement approved SoundAtlas documentation changes by classifying source-of-truth relationships, discovering related references, preserving documentation boundaries, validating consistency, and reporting the result.
---

# SoundAtlas Documentation Implementation

Use this skill for repeatable SoundAtlas documentation and workflow-document
work from an approved GitHub Issue. The approved Issue is the scope authority;
`soundatlas-issue-planning` is the entrypoint for drafting and revising Issue
intake, Plan Updates, Detailed Plan Updates, and Issue-level reports under the
lifecycle contract in `docs/github-issue-workflow.md`.

## Required context

Read these before editing:

- `AGENTS.md`
- `docs/github-issue-workflow.md`
- `docs/workflow-registry.md`
- the approved GitHub Issue, including its `## Grill-Me Review` and `## Plan
  Update` or `## Detailed Plan Update` comments when risk flags are present
- the target document and directly related references

Optional context may clarify the Issue without overriding it:

- target documentation area or file
- related product, architecture, workflow, or source-of-truth decision
- whether the output is a plan, an approved edit, an audit, or an archive update
- formatting or validation commands

## Implementation gate

Implement only when the user explicitly requests implementation of the approved
Issue, for example `implement issue #<number>`, or when the work is clearly
trivial and low-risk.

For Issue-based work with security, credentials, infrastructure, networking,
workflow, UX, editorial, cross-cutting, user-visible, vague, or materially
ambiguous risk flags, require both:

- a `## Grill-Me Review` comment with required material decisions confirmed;
- a `## Plan Update` or `## Detailed Plan Update` that incorporates them.

Explicit implementation wording does not bypass these gates. Stop for approval
if the requested change affects product intent, source quality, editorial
judgment, publication boundaries, or another high-risk decision outside the
approved Issue. Record low-risk local assumptions in the Implementation Report
or Issue comment.

## Documentation boundaries

Classify each target before editing:

- **Source of truth** — authoritative product, architecture, workflow, data, or
  editorial rules. Update it only when the approved Issue explicitly changes
  that authority.
- **Derived guidance** — summaries, instructions, or companion views that must
  remain consistent with their source. Update them only when the source or
  approved Issue requires it.
- **Workflow/process** — repeatable instructions for agents or reviewers. Keep
  routing and ownership aligned with `docs/workflow-registry.md`.
- **Archive/history** — records of completed decisions or past work. Preserve
  historical meaning; do not silently convert an archive into a source of truth.

The approved Issue defines the requested scope. Discover directly related
references and authoritative documents before editing, but do not broaden the
change to every document that mentions the target. Do not edit application code,
seed data, APIs, deployment configuration, or production behavior unless the
approved Issue explicitly includes that scope.

## Process

1. Read the approved Issue and identify the exact documentation acceptance
   criteria and output boundary.
2. Inspect the target document and classify its source-of-truth relationship.
3. Identify the authoritative source, derived companions, active references,
   and any compatibility-wrapper or registry entries that must stay aligned.
4. Decide whether the request is planning-only, an approved documentation edit,
   an audit, or an archive update. Keep GitHub Issue planning with
   `soundatlas-issue-planning`.
5. Make the smallest approved documentation change. Preserve source ownership,
   existing terminology, and related workflow gates.
6. Check for stale, duplicated, or contradictory active references without
   rewriting unrelated documentation.
7. If the change reveals a missing product, source, editorial, or high-risk
   decision, stop and update the Issue rather than silently expanding scope.

## Validation

Run the narrowest relevant checks first:

```sh
git diff --check
python scripts/check_doc_references.py
```

Also run relevant Markdown formatting, schema, or domain-specific checks when
the approved Issue requires them. For workflow or skill changes, manually audit
the changed paths to confirm no application, seed-data, or production files
changed.

## Documentation Report

Before finalizing the report for completed non-trivial Issue work, use
`soundatlas-implementation-review`. Resolve or route required findings, then
include its Review Result in this same report. Do not post a separate routine
review comment.

Report in the Issue and final response:

```md
## Summary

- What documentation changed and why.
- Which approved Issue behavior was implemented.

## Source-of-Truth Classification

- Target category:
- Authoritative source:
- Related documents checked:

## Acceptance Criteria Result

- AC1: Pass/Fail — evidence

## Verification

- `<command>` — Pass/Fail

## Files Changed

- `<path>`: `<reason>`

## Review Result

- Verdict:
- Reviewer mode:
- Compared artifacts:
- Evidence coverage:
- Findings and routing:
- Documentation impact:

## Remaining Risks

- None, or the specific blocker.
```

Do not commit unless the user explicitly requests it. If committed, use a
Conventional Commit and include `Issue: #<number>` in the commit body.

After a successful commit for completed Issue work, capture the commit hash,
verify the acceptance criteria and Issue-relevant working-tree state, post the
standard completion comment, and close the Issue. Do not close for uncommitted,
partial, WIP, incomplete, or ambiguously scoped work, or when the human asks to
keep the Issue open. If commenting or closing fails, report the failure and
leave the Issue open when possible.
