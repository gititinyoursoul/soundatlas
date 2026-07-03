# Plan Feature

Use this prompt before implementing a new SoundAtlas feature, UX change, data
workflow, or cross-cutting change.

This prompt is the planning entrypoint for the GitHub Issue workflow.

Core rule:

> Do not implement directly from a vague prompt. Capture non-trivial planned
> work in a GitHub Issue, refine the plan in that Issue, and implement only
> after explicit wording such as `implement issue #<number>`.

## Context To Provide

* Feature, task, problem, review, or decision statement.
* User value and primary user action, when relevant.
* Target area:
  * `frontend`
  * `backend`
  * `data/seed`
  * `data/enrichment`
  * `docs`
  * cross-cutting
* Related route, event, place, media item, workflow, or Issue number.
* Relevant docs:
  * `README.md`
  * `AGENTS.md`
  * `docs/implementation-plan-workflow.md`
  * `docs/data/seed-data-validation.md`
  * `docs/content/workflow-commands.md`
  * `docs/enrichment/media/workflow-commands.md`
* Constraints and non-goals.
* Whether implementation or planning-only is requested.

## Task

Create or update GitHub Issue planning content. Do not create local or
repo-versioned implementation plan files.

For a new Intake Issue, use:

```md
## Task

## Context

## Acceptance Criteria
```

For a normal Plan Update, use:

```md
## Plan

## Non-Goals

## Open Questions
```

For a Detailed Plan Update, use:

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

If implementation is requested in the same turn, produce or inspect the Issue
plan first and proceed only after implementation is clearly approved, normally
with wording such as `implement issue #<number>`.

## Project Constraints

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

## Implementation Gate

Implementation may proceed only when:

* The Issue has enough Task, Plan, and Acceptance Criteria detail to implement.
* Blocking open questions are resolved or intentionally deferred.
* For GitHub Issue work, the human has explicitly requested implementation with
  wording such as `implement issue #<number>`.

Blocking questions include anything involving:

* data loss
* destructive writes
* schema changes
* seed data shape changes
* permissions/security
* privacy
* external API behavior
* generated media review boundaries
* historically sensitive or uncertain claims
* irreversible workflow changes

For low-risk ambiguity, make a conservative assumption and continue.

## GitHub Issue Rules

Codex may set existing approved GitHub labels on Issues. New labels must be
proposed and explicitly approved before Codex creates or uses them.

Recommended label families:

* `type:feature`
* `type:bug`
* `type:refactor`
* `type:chore`
* `area:<feature-or-component>`
* `blocked`

An Issue is done when implementation is complete, relevant checks have run or
blockers are documented, and Acceptance Criteria have been verified. Close it
with `gh issue close <number>` only when the human explicitly requests or
clearly approves closure. Do not add a separate `done` label.

## Planning Rules

First classify the change:

* frontend-only
* backend-only
* seed-data-only
* enrichment workflow
* documentation-only
* cross-cutting

For cross-cutting changes, plan in this order:

1. Data/schema impact
2. Backend/API impact
3. Frontend state impact
4. UX/component impact
5. Tests/checks
6. Documentation or Issue updates

For UX changes, explicitly define:

* user action
* visible state
* loading state
* empty state
* error state
* keyboard/accessibility considerations where relevant

For backend changes, define:

* affected endpoints
* schemas
* seed repository behavior
* error behavior
* tests

For frontend changes, define:

* affected components
* shared state changes
* API/client changes
* map/timeline/story panel behavior
* `npm run check` expectation

For media retrieval changes, define:

* request-plan impact
* normalized result impact
* merge behavior
* review boundary
* whether `data/seed/events.json` should change

## Implementation Report

After implementation, report:

```md
## Summary

## Verification

## Acceptance Criteria Result

## Remaining Risks
```

## Deliverables

Return:

1. A short summary of the intended change.
2. The Issue action: create Issue, update Issue body, or add Issue comment.
3. Assumptions.
4. Open questions, if any remain.
5. Intake Issue, Plan Update, Detailed Plan Update, or Implementation Report
   content.
6. Validation approach, when implementation is expected.
7. Next step: approve the Plan Update, request implementation with
   `implement issue #<number>`, or review the Implementation Report.

## Output Rules

* Be concrete.
* Avoid generic filler.
* Prefer explicit file paths when they clarify scope.
* Do not invent APIs, schema fields, or data.
* If the request is ambiguous, state assumptions before the plan.
* Do not write code unless explicitly asked.
* Do not modify product behavior outside the approved Issue.
* If implementation reveals needed behavior outside the approved Issue, stop for
  approval when the difference changes product intent or another high-risk
  boundary.
