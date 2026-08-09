---
name: soundatlas-documentation-implementation
description: Plan and implement approved SoundAtlas documentation changes by classifying source-of-truth relationships, discovering related references, preserving documentation boundaries, validating consistency, and reporting the result.
---

# SoundAtlas Documentation Implementation

Use this skill for repeatable SoundAtlas documentation and workflow-document
work from an approved GitHub Issue. The approved Issue is the scope authority;
`soundatlas-issue-planning` is the entrypoint for drafting and revising Issue
intake, Plan Updates, Detailed Plan Updates, Proceed-to-Implementation records,
and Issue-level reports under the lifecycle contract in
`docs/github-issue-workflow.md`.

## Required context

Read these before editing:

- `AGENTS.md`
- `docs/github-issue-workflow.md`
- `docs/workflow-registry.md`
- the approved GitHub Issue, including any recorded Grill-Me findings or
  decisions and its `## Plan Update` or `## Detailed Plan Update` when risk
  flags are present. A standalone `## Grill-Me Review` is used when the result
  is material or explicitly standalone; a clean check may be inline in the
  relevant action comment.
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

For non-trivial Issue-based work, require a current `## Plan Update` or
`## Detailed Plan Update` and a later `## Proceed to Implementation` record
linking that exact Plan.

For security, credentials, infrastructure, networking, workflow, UX, editorial,
cross-cutting, user-visible, vague, or materially ambiguous risk flags, also
require a recorded Grill-Me result with required material decisions confirmed
and incorporated into the Plan.

Use a standalone `## Grill-Me Review` for material findings, decisions,
blockers, or explicitly standalone sessions. Record a clean check inline in the
action comment when useful.

Explicit implementation wording does not bypass these gates. Stop for approval
if the requested change affects product intent, source quality, editorial
judgment, publication boundaries, or another high-risk decision outside the
approved Issue. Record low-risk local assumptions in the Implementation Report
or Issue comment.

Before the first repository edit, and again before resuming after a canonical
revision or blocking decision, export the current Issue fields defined in
`docs/github-issue-workflow.md` and require
`python scripts/check_issue_readiness.py --file <export>` to pass. Add
`--require-grill-review` when risk flags require a recorded Grill-Me result. If
the Human has authorized the latest Plan but the Proceed record is missing, use
`soundatlas-issue-planning` to record it first. Do not duplicate validator rules
in this Skill.

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

Follow the commit-ready and local-commit lifecycle in
`docs/github-issue-workflow.md`. Use a Conventional Commit and include
`Issue: #<number>` in the commit body.

After a successful push for completed Issue work, follow the post-push
completion lifecycle in `docs/github-issue-workflow.md`: run the local
completion gate, capture the published commit hash, verify acceptance criteria
and Issue-relevant working-tree state, post the single standard completion
comment, and close the Issue only after that comment succeeds.
