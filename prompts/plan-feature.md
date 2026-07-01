# Plan Feature

Use this prompt before implementing a new SoundAtlas feature, UX change, data workflow, or cross-cutting change.

This prompt is the planning entrypoint for the current implementation-plan workflow.

The goal is to prevent implementation from starting from a vague request. First produce a practical implementation plan and capture non-trivial planned agent work in a GitHub Issue. For approved non-trivial work, save that plan locally as an implementation plan record before implementation starts.

Core rule:

> Do not implement directly from a vague prompt. Implementation may proceed from an approved Issue after explicit wording such as `implement issue #<number>`, an approved plan, a local implementation plan record, or a clearly trivial request.

## Context To Provide

* Feature or problem statement.
* User value and primary user action.
* Target area:

  * `frontend`
  * `backend`
  * `data/seed`
  * `data/enrichment`
  * `docs`
  * cross-cutting
* Related route, event, place, media item, or workflow, if any.
* Relevant docs:

  * `README.md`
  * `AGENTS.md`
  * `docs/data/seed-data-validation.md`
  * `docs/enrichment/media/workflow-commands.md`
  * `docs/enrichment/media/youtube-mvp-workflow.md`
* Constraints and non-goals.
* Whether implementation or planning-only is requested.
* Existing local implementation plan record path, if using or updating a previous record.

## Task

Produce a practical implementation plan. For non-trivial planned agent work, create or update a GitHub Issue with Goal, Plan, and Acceptance Criteria when authorized. If requested, also produce a local implementation plan record path and record content that can be saved under `plans/records/`.

Do not write code unless explicitly asked.

If implementation is requested in the same turn, produce the plan first and proceed only after implementation is clearly approved, normally with wording such as `implement issue #<number>`. For non-trivial approved work, create the local implementation plan record before implementation and update it after verification.

If the input is incomplete, do not stop immediately. State reasonable assumptions, list open questions, and produce a plan and local record shape that can be refined. Only block when missing information would make implementation unsafe, destructive, likely to violate the project data model, or likely to create incorrect historical/data behavior.

## Project Constraints

* Keep changes small, reviewable, and MVP-oriented.
* Current product scope is New York 1965-1985 with curated routes, events, places, connections, and external media links.
* Use existing project conventions in `AGENTS.md`.
* Prefer data-driven implementation from `data/seed/` over hardcoded UI mock data.
* Preserve seed file shapes documented in `docs/data/seed-data-validation.md`.
* Keep generated media links as `review_status: "draft"` until manually reviewed.
* Do not store audio or video files in the repository.
* Do not commit secrets, API keys, local paths, or generated media files.
* Do not commit changes unless explicitly requested.

## Technical Context

* Frontend: SvelteKit, TypeScript, Leaflet.
* Backend: Python, `uv`, FastAPI, Pydantic.
* MVP data: curated JSON files under `data/seed/`.
* Media retrieval: YouTube-only MVP using `data/enrichment/`.
* Media workflow commands are documented in `docs/enrichment/media/workflow-commands.md`.

## Local Implementation Plan Record Rules

When a local implementation plan record is requested or needed for approved non-trivial work, create or update a lightweight local plan record.

Recommended location:

```text
plans/records/P-###-<short-slug>.md
```

Treat this as a local, gitignored workspace path during solo work unless the human explicitly asks to commit the file.

The record must include:

```md
# Implementation Plan: <feature/change name>

## Plan ID
P-###

## Request
What the human asked for.

## Goal
What outcome we want.

## Non-goals
What we are not doing in this change.

## Requirements
- R1:
- R2:
- R3:

## Acceptance criteria
- AC1:
- AC2:
- AC3:

## Assumptions
- A1:

## Open questions
- Q1:
```

Acceptance criteria must be concrete and testable.

Avoid vague criteria like:

```md
- The UI works well.
- The data is correct.
- The flow is improved.
```

Prefer criteria like:

```md
- Given a user opens a route detail page, when the route has related events, then the page shows those events in chronological order.
- Given an event has no reviewed media links, then the UI does not show draft media links as playable content.
- Given seed validation runs, then the changed seed files pass the documented validation checks.
```

## Implementation Gate

Implementation may proceed only when:

* The goal is clear.
* Non-goals are listed.
* Requirements describe intended behavior.
* Acceptance criteria are testable.
* Assumptions are explicit.
* Blocking open questions are resolved or intentionally deferred.
* For GitHub Issue work, the human has explicitly requested implementation with wording such as `implement issue #<number>`.

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

Each planned Issue should include:

```md
## Goal

## Plan

## Acceptance Criteria
```

Use optional `Non-Goals` and `Risks / Open Questions` sections when they clarify boundaries.

Codex may set existing approved GitHub labels on Issues. New labels must be proposed and explicitly approved before Codex creates or uses them.

Recommended label families:

* `type:feature`
* `type:bug`
* `type:refactor`
* `type:chore`
* `area:<feature-or-component>`
* `blocked`

An Issue is done when implementation is complete, relevant checks have run or blockers are documented, and Acceptance Criteria have been verified. Close it with `gh issue close <number>` only when the human explicitly requests or clearly approves closure. Do not add a separate `done` label.

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

## Linking Plan To Local Records

If a local implementation plan record exists, the implementation plan should reference that record's requirements.

Use requirement IDs from the record:

```md
## Implementation Plan

1. Update route data loading for related events.
   - Satisfies: R1, R2
   - Files likely affected: `src/routes/...`

2. Add empty state for routes with no related events.
   - Satisfies: R3
   - Files likely affected: `src/lib/components/...`
```

When a local plan record exists, tests and validation should reference acceptance criteria:

```md
## Validation

- AC1: covered by component test or manual route check.
- AC2: covered by seed fixture check.
- AC3: covered by `npm run check`.
```

## Handling Incomplete Input

* State assumptions explicitly before the plan or local implementation plan record.
* Separate assumptions from open questions.
* Continue with a conservative plan when assumptions are safe.
* Keep risky or irreversible steps behind confirmation.
* Prefer planning small checkpoints over designing a large speculative solution.

Example:

```md
## Assumptions

- This is a frontend-only change.
- Existing API responses stay unchanged.
- The feature should work with current `data/seed/events.json`.
- No new route or media enrichment data is required.

## Open Questions

- Should the behavior apply to all routes or only one route?
- Should mobile behavior differ from desktop?
```

## Deliverables

Return:

1. A short summary of the intended change.
2. A proposed local implementation plan record path, if a record is requested or needed.
3. The local record content or summary, if a record is included.
4. A numbered implementation plan with 5-9 reviewable steps.
5. Acceptance criteria.
6. Validation commands.
7. Risks or open questions.
8. Suggested file groups for review.
9. Suggested commit grouping and Conventional Commit messages, including a `Plan: P-###` body footer example.
10. Next step: the concrete follow-up action, usually plan approval followed by implementation.

## Output Rules

* Be concrete.
* Avoid generic filler.
* Prefer explicit file paths.
* Do not invent APIs, schema fields, or data.
* If the request is ambiguous, state assumptions before the plan.
* Do not write code unless explicitly asked.
* Do not modify product behavior outside the approved Issue, approved plan, or local implementation plan record.
* If implementation reveals needed behavior outside the approved Issue or plan, stop for approval when the difference changes product intent or another high-risk boundary.
* End with a `Next step` line naming the next prompt, skill, or human action.
