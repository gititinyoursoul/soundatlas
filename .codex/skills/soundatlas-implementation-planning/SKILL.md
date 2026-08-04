---
name: soundatlas-implementation-planning
description: Draft or revise SoundAtlas GitHub Issue intake, Plan Updates, Detailed Plan Updates, and Implementation Reports for frontend, backend, data, documentation, UX, or cross-cutting changes. Use when a SoundAtlas Issue needs to be created, refined for implementation, checked for open questions, or reported after implementation.
---

# SoundAtlas Implementation Planning

Read the repo context before drafting or revising Issue planning content. Start
with:

- `AGENTS.md`
- `docs/implementation-plan-workflow.md`
- `docs/workflow-registry.md`
- the accepted `## Concept` Issue comment or authoritative concept document,
  when concept work was required
- the `soundatlas-implementation-review` result, when finalizing an
  Implementation Report for non-trivial Issue work

Read `prompts/grill-me.md` when the request needs critique, simplification, or
readiness review before Issue content is drafted.

## Workflow

1. Classify the request.
   Decide whether the Issue needs an Intake Issue, Plan Update, Detailed Plan
   Update, or Implementation Report.

2. Inspect the repo before asking questions.
   Resolve discoverable facts from docs, code, seed data, or existing Issues
   before blocking on user input.

   Perform the lightweight Grill-Me check defined by repository guidance. If
   planning would otherwise have to invent material target behavior, runtime
   responsibilities, boundaries, or ownership, return to Grill Me and
   `soundatlas-concept-work` before drafting a plan.

3. Separate intake from planning.
   When creating an Issue, use only the Intake shape: Task, Context, and
   Acceptance Criteria. Do not add speculative implementation steps, technical
   assumptions, or prematurely resolve open questions. State that the Intake
   Issue is not implementation-ready.

   If discovery reveals missing scope before planning, update the Intake body
   and add an `## Intake Revision` comment recording the date, previous scope,
   revised scope, and reason. Wording-only clarifications may proceed without a
   new review; material revisions require a fresh Grill-Me review before the
   Plan Update.

4. Draft or revise Issue planning content.
   Keep planning content in the GitHub Issue body or comments. Do not create
   local or repo-versioned implementation plan files.

   When an accepted concept exists, link to it and derive the plan from its
   target behavior, scope and non-goals, runtime responsibilities, boundaries
   and ownership, and resolved decisions. Do not copy the concept into the
   Plan Update.

   When creating an Issue, choose exactly one approved `priority:p*` label by
   reasoning from blocking level, MVP/release impact, risk reduction, and
   urgency. Use `priority:p2` only as the neutral fallback when `p0`, `p1`, or
   `p3` are not clearly justified. Briefly state the priority rationale.

   Inspect existing open milestones at Issue-creation time. Assign one only
   when completing the Issue directly advances the outcome stated by the
   milestone title and description. Shared labels, a related product area, or
   an indirect benefit are not sufficient. Leave partial, indirect, multiple,
   or ambiguous matches unassigned and explain why. Do not create, rename, or
   broaden milestones without explicit human approval. In the Issue-creation
   handoff, report the milestone decision and rationale alongside the priority
   rationale.

5. Keep the Issue decision-complete for implementation.
   For security, credentials, infrastructure, networking, workflow, UX,
   editorial, cross-cutting, user-visible, vague, or materially ambiguous work,
   require a `## Grill-Me Review` comment before a Plan Update. Clearly
   trivial, local, low-risk work may use the direct path.
   Make assumptions for low-risk implementation details. Stop for approval when
   uncertainty affects product intent, data shape, security, privacy, external
   API behavior, generated media review boundaries, historically sensitive
   claims, irreversible workflow behavior, or production stability.

6. Preserve Acceptance Criteria history.
   If the plan changes the original criteria, include an `Acceptance Criteria
Changes` section instead of silently rewriting the meaning of the Issue.

7. Stop before implementation unless the user explicitly requests implementation
   with wording such as `implement issue #<number>` or the change is clearly
   trivial. Explicit wording does not bypass required review or planning gates.

8. Finalize one combined Implementation Report after review.
   For completed non-trivial Issue work, require
   `soundatlas-implementation-review` before the report is final. Include its
   Review Result in the same comment; do not create a separate routine review
   comment. If the review routes a required correction or material decision,
   keep the report unaccepted until the finding is resolved or explicitly
   reported as blocking.

9. After a completed Issue-based implementation is committed, complete the
   post-commit lifecycle: capture the hash, verify acceptance criteria, confirm
   no Issue-relevant changes remain uncommitted, post the standard completion
   comment, and close the Issue. Leave the Issue open and report the failure if
   verification, commenting, or closing cannot be completed.

## Issue Shapes

Use this shape for a new Intake Issue:

```md
## Task

## Context

## Acceptance Criteria
```

Use this shape for normal planning:

```md
## Plan

## Non-Goals

## Open Questions
```

Use this shape when planning is complex enough to need implementation detail:

```md
## Plan

## Assumptions

## Non-Goals

## Acceptance Criteria Changes

## Implementation Steps

## Validation

## Open Questions
```

Use `Requirements` only when complex product, API, data, security, or workflow
rules would otherwise be unclear.

Use this shape after implementation:

```md
## Summary

## Verification

## Acceptance Criteria Result

## Review Result

## Remaining Risks
```

The standard post-commit completion comment is:

```md
## Completed

- Commit: `<commit hash>`
- Issue: #<number>
- Acceptance criteria: complete
- Verification: `<checks or report reference>`
```

## Planning Rules

- Keep GitHub Issues as the default source of truth for planning,
  implementation, and verification.
- Prefer `Task` over `Goal` for intake because SoundAtlas follow-up work often
  starts as a task, review, investigation, or decision.
- Keep Plan Updates concise by default; use Detailed Plan Updates only when
  implementation would otherwise need to rediscover decisions.
- Require user confirmation for material decisions about product behavior,
  scope, security, privacy, external APIs, editorial/source quality,
  irreversible workflow behavior, or production stability. Record low-risk
  assumptions in the Plan Update instead.
- Do not state `Open Questions: None` while a material decision remains
  unresolved.
- Do not define behavior outside the requested change.
- Do not describe completed non-trivial Issue work as accepted without a
  `soundatlas-implementation-review` result supported by proportionate evidence.
- Keep the Review Result inside the single Implementation Report comment. The
  review skill performs the comparison; this skill records the result.
- Do not fill a missing or contradictory material concept decision inside a
  Plan Update. Return it to Grill Me and concept work.
- Reference an accepted concept instead of duplicating it across implementation
  Issues or plans.
- Prefer small, reviewable revisions over broad rewrites.
- Do not silently broaden an Intake. Split a separate deliverable, changed
  primary outcome, materially different domain/owner, or independently
  sequenced expansion into a linked Issue.
- After a Plan Update exists, record material scope changes under `Acceptance
  Criteria Changes` and rerun required review before implementation. After
  implementation begins, use a linked Issue for material expansion.
- Do not close an Issue for uncommitted, partial, WIP, incomplete, or
  ambiguously scoped work, or when the human explicitly asks to keep it open.
- Unrelated uncommitted changes do not block closure; verify only the
  Issue-relevant working-tree state.
- For cross-cutting changes, plan in this order: data or schema impact, backend
  impact, frontend state impact, UX impact, tests or checks, docs or Issue
  updates.

## Output

Return the planning result in this order:

1. Issue action: create, update body, or add comment.
2. Assumptions.
3. Open questions, if any remain.
4. Draft Issue content or comment content.
5. Validation approach, when implementation is expected.
6. Next step: approve the Plan Update, request implementation with
   `implement issue #<number>`, or review the Implementation Report.
