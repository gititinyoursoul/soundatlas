# GitHub Issue Workflow

This document defines the lightweight Issue-based workflow for SoundAtlas agent
work.

The default workflow is Issue-led:

> Do not implement from a vague request. Capture non-trivial planned agent work
> in a GitHub Issue, refine the plan in that Issue, and implement only after an
> explicit implementation request such as `implement issue #<number>`.

GitHub Issues are the source of truth for planned agent work. `TODO.md` is a
legacy backlog and should not receive new planned work unless the human
explicitly asks for a legacy note.

## Workflow

```text
1. Human gives a feature/change request.
2. Agent inspects the repo before asking questions when local context can answer them.
3. Agent creates or updates an Intake Issue for non-trivial planned work.
4. Agent adds a Plan Update or Detailed Plan Update in the Issue when planning is needed.
5. Human starts implementation with explicit wording such as "implement issue #<number>".
6. Agent implements from the approved Issue content.
7. Agent validates the change with the relevant checks.
8. Agent posts an Implementation Report in the Issue or final response.
9. Human reviews the local diff and explicitly approves closing the Issue.
```

For clearly trivial changes, the agent may proceed directly when the request is
clear and low-risk.

## Intake Issue

Create or update an Intake Issue when work is non-trivial, user-visible,
workflow-changing, cross-cutting, or likely to need later review.

Use this minimum structure:

```md
## Task

<What should be changed, investigated, decided, or fixed?>

## Context

<Why it matters, relevant files or workflow notes, optional links.>

## Acceptance Criteria

- [ ] <Concrete done condition>
```

Keep the intake lightweight. The `Task` can be close to a TODO item. Avoid
forcing a broad product `Goal` when the work is a small task, review,
investigation, or decision.

Codex may set existing approved GitHub labels on Issues. New labels must be
proposed and explicitly approved before Codex creates or uses them.

Recommended label families are:

* `type:feature`
* `type:bug`
* `type:refactor`
* `type:chore`
* `area:<feature-or-component>`
* `blocked`

## Plan Update

Add a Plan Update in the Issue before non-trivial implementation when the Intake
Issue is not already decision-complete.

Use this structure for normal work:

```md
## Plan

## Non-Goals

## Open Questions
```

Use a Detailed Plan Update when the work is cross-cutting, risky, or has enough
detail that future implementation should not rediscover decisions:

```md
## Plan

## Assumptions

## Non-Goals

## Acceptance Criteria Changes

## Implementation Steps

## Validation

## Open Questions
```

Rules:

* Keep the plan in the GitHub Issue, not in a local or repo-versioned plan file.
* Use `Acceptance Criteria Changes` whenever the original criteria are changed.
  Do not silently rewrite the meaning of the Issue.
* Use `Requirements` only when complex product, API, data, security, or workflow
  rules would otherwise be unclear.
* Stop for approval when open questions affect product intent, data shape,
  security, privacy, external API behavior, generated media review boundaries,
  historically sensitive claims, irreversible workflow behavior, or production
  stability.

## Implementation Gate

Implementation may proceed when:

* The human explicitly requests implementation of an Issue with wording such as
  `implement issue #<number>`, or the change is clearly trivial.
* The Issue contains enough Task, Plan, and Acceptance Criteria detail to
  implement safely.
* Blocking questions are resolved or intentionally deferred.

The agent must not implement behavior outside the approved Issue content. If
implementation reveals missing behavior, the agent should:

* Continue and record an assumption when the decision is low-risk and local to
  implementation.
* Stop for approval when the decision changes product behavior or another
  high-risk boundary.

## Implementation Report

After implementation, report in the final response and, when useful, as an Issue
comment:

```md
## Summary

- What changed.

## Verification

- `<command>` - Pass/Fail

## Acceptance Criteria Result

- [x] `<criterion>` - evidence
- [ ] `<criterion>` - blocker or remaining work

## Remaining Risks

- None, or:
- `<risk and follow-up>`
```

Do not close the Issue just because implementation has started or the report was
posted. Close the Issue with `gh issue close <number>` only when the human
explicitly requests or clearly approves closure after reviewing the local
result.

Do not add a separate `done` label for completion.

## Commit Reference

When implementation work is committed, keep the Conventional Commit subject
clean and reference the Issue in the commit body:

```text
feat(data): improve enrichment input

Issue: #123
```

This is a documented convention, not a hook-enforced rule in the current
workflow.

## SoundAtlas Project Constraints

Plans and implementation should respect these project constraints:

* Keep changes small, reviewable, and MVP-oriented.
* Current product scope is New York 1965-1985 with curated routes, events,
  places, connections, and external media links.
* Use existing project conventions in `AGENTS.md`.
* Prefer data-driven implementation from `data/seed/` over hardcoded UI mock
  data.
* Preserve seed file shapes documented in `docs/data/seed-data-validation.md`.
* Keep generated media links as `review_status: "draft"` until manually
  reviewed.
* Do not store audio or video files in the repository.
* Do not commit secrets, API keys, local paths, or generated media files.
* Do not commit changes unless explicitly requested.
