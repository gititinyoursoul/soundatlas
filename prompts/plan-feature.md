# Spec + Plan Feature

Use this prompt before implementing a new SoundAtlas feature, UX change, data workflow, or cross-cutting change.

This prompt is the planning entrypoint for the current spec-first workflow. Use the `soundatlas-spec-planning` skill for this task and keep this prompt as the compatibility wrapper.

The goal is to prevent implementation from starting from a vague request. First draft a new spec revision, then produce a practical implementation plan from that revision.

Core rule:

> Do not implement directly from a prompt. Implementation may only proceed from an explicit spec and acceptance criteria.

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
  * `TODO.md`
  * `AGENTS.md`
  * `docs/seed-validation.md`
  * `docs/media-retrieval/workflow-commands.md`
  * `docs/media-retrieval/youtube-mvp-workflow.md`
* Constraints and non-goals.
* Whether implementation or planning-only is requested.
* Existing approved spec revision path, if updating a previous revision.

## Task

Produce a small spec and a practical implementation plan.

Do not write code unless explicitly asked.

If implementation is requested, still draft a new spec revision first. Then produce the plan. Only proceed to code after the revision is explicit enough to implement safely.

If the input is incomplete, do not stop immediately. State reasonable assumptions, list open questions, and produce a spec and plan that can be refined. Only block when missing information would make implementation unsafe, destructive, likely to violate the project data model, or likely to create incorrect historical/data behavior.

## Project Constraints

* Keep changes small, reviewable, and MVP-oriented.
* Current product scope is New York 1965-1985 with curated routes, events, places, connections, and external media links.
* Use existing project conventions in `AGENTS.md`.
* Prefer data-driven implementation from `data/seed/` over hardcoded UI mock data.
* Preserve seed file shapes documented in `docs/seed-validation.md`.
* Keep generated media links as `review_status: "draft"` until manually reviewed.
* Do not store audio or video files in the repository.
* Do not commit secrets, API keys, local paths, or generated media files.
* Do not commit changes unless explicitly requested.

## Technical Context

* Frontend: SvelteKit, TypeScript, Leaflet.
* Backend: Python, `uv`, FastAPI, Pydantic.
* MVP data: curated JSON files under `data/seed/`.
* Media retrieval: YouTube-only MVP using `data/enrichment/`.
* Media workflow commands are documented in `docs/media-retrieval/workflow-commands.md`.

## Spec Rules

Before planning implementation, create or update a lightweight spec.

Recommended location:

```text
specs/<feature-slug>/rNN-<short-desc>.md
```

If the repository already has a better convention for specs or feature docs, follow that convention instead.

The spec must include:

```md
# Spec: <feature/change name>

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

## Spec Gate

Implementation may proceed only when:

* The goal is clear.
* Non-goals are listed.
* Requirements describe intended behavior.
* Acceptance criteria are testable.
* Assumptions are explicit.
* Blocking open questions are resolved or intentionally deferred.

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
6. Documentation/TODO updates

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

## Linking Plan To Spec

The implementation plan must reference spec requirements.

Use requirement IDs from the spec:

```md
## Implementation Plan

1. Update route data loading for related events.
   - Satisfies: R1, R2
   - Files likely affected: `src/routes/...`

2. Add empty state for routes with no related events.
   - Satisfies: R3
   - Files likely affected: `src/lib/components/...`
```

Tests and validation must reference acceptance criteria:

```md
## Validation

- AC1: covered by component test or manual route check.
- AC2: covered by seed fixture check.
- AC3: covered by `npm run check`.
```

## Handling Incomplete Input

* State assumptions explicitly before the spec.
* Separate assumptions from open questions.
* Continue with a conservative spec and plan when assumptions are safe.
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
2. A proposed spec revision path.
3. The spec content, or a summary of changes to the existing approved revision.
4. A numbered implementation plan with 5-9 reviewable steps.
5. Acceptance criteria.
6. Validation commands.
7. Risks or open questions.
8. Suggested file groups for review.
9. Suggested commit grouping and Conventional Commit messages.
10. Next step: the concrete follow-up action, usually spec review/approval followed by the relevant implementation prompt.

## Output Rules

* Be concrete.
* Avoid generic filler.
* Prefer explicit file paths.
* Do not invent APIs, schema fields, or data.
* If the request is ambiguous, state assumptions before the spec.
* Do not write code unless explicitly asked.
* Do not modify product behavior outside the spec.
* If implementation reveals needed behavior not covered by the spec, draft a new revision first and stop for approval.
* End with a `Next step` line naming the next prompt, skill, or human action.
