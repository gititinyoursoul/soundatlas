---
name: soundatlas-implementation-planning
description: Draft or revise SoundAtlas GitHub Issue intake, Plan Updates, Detailed Plan Updates, and Implementation Reports for frontend, backend, data, documentation, UX, or cross-cutting changes. Use when a SoundAtlas Issue needs to be created, refined for implementation, checked for open questions, or reported after implementation.
---

# SoundAtlas Implementation Planning

Read the repo context before drafting or revising Issue planning content. Start
with:

- `AGENTS.md`
- `docs/implementation-plan-workflow.md`
- `docs/skills-workflow.md`

Read `prompts/grill-me.md` when the request needs critique, simplification, or
readiness review before Issue content is drafted. `prompts/plan-feature.md` is
only a deprecated compatibility alias.

## Workflow

1. Classify the request.
   Decide whether the Issue needs an Intake Issue, Plan Update, Detailed Plan
   Update, or Implementation Report.

2. Inspect the repo before asking questions.
   Resolve discoverable facts from docs, code, seed data, or existing Issues
   before blocking on user input.

3. Draft or revise Issue content.
   Keep planning content in the GitHub Issue body or comments. Do not create
   local or repo-versioned implementation plan files.

4. Keep the Issue decision-complete for implementation.
   Make assumptions for low-risk implementation details. Stop for approval when
   uncertainty affects product intent, data shape, security, privacy, external
   API behavior, generated media review boundaries, historically sensitive
   claims, irreversible workflow behavior, or production stability.

5. Preserve Acceptance Criteria history.
   If the plan changes the original criteria, include an `Acceptance Criteria
   Changes` section instead of silently rewriting the meaning of the Issue.

6. Stop before implementation unless the user explicitly requests implementation
   with wording such as `implement issue #<number>` or the change is clearly
   trivial.

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

## Remaining Risks
```

## Planning Rules

- Keep GitHub Issues as the default source of truth for planning,
  implementation, and verification.
- Prefer `Task` over `Goal` for intake because SoundAtlas follow-up work often
  starts as a task, review, investigation, or decision.
- Keep Plan Updates concise by default; use Detailed Plan Updates only when
  implementation would otherwise need to rediscover decisions.
- Do not define behavior outside the requested change.
- Prefer small, reviewable revisions over broad rewrites.
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
