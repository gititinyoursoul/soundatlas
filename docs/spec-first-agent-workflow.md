# Spec-First Agent Workflow

This document defines the lightweight spec-first workflow for agent-driven development in SoundAtlas.

The goal is to prevent agents from jumping directly from vague requests into implementation. For non-trivial feature work, behavior changes, data workflow changes, UX changes, backend changes, or cross-cutting changes, the agent should first draft a new spec revision in the feature's spec folder, then implement against that approved revision.

Core rule:

> Do not implement directly from a prompt. Implement only from an approved spec with acceptance criteria.

## When to use this workflow

Use the spec-first workflow for:

* New features
* UX behavior changes
* Backend/API behavior changes
* Seed data shape or data workflow changes
* Media retrieval or enrichment workflow changes
* Cross-cutting frontend/backend/data changes
* Non-trivial refactors
* Anything involving user-visible behavior
* Anything involving production-critical flows

A full spec is usually not needed for:

* Typo fixes
* Formatting-only changes
* Tiny copy edits
* Mechanical renames
* Comments-only changes
* Trivial documentation edits
* Dependency bumps with no behavior change

For trivial changes, the agent may proceed without a full spec if the request is explicitly marked as trivial and the agent briefly states why it is safe.

## MVP workflow

The current MVP workflow is:

```text
1. Human gives a feature/change request.
2. Agent drafts a new spec revision in the feature's spec folder.
3. Agent lists assumptions and open questions.
4. Human reviews and approves the spec revision.
5. Agent creates or uses an implementation plan from the approved revision.
6. Agent implements only what is in the approved revision.
7. Agent verifies implementation against acceptance criteria.
8. If implementation reveals missing behavior, agent drafts a new revision instead of editing the approved file.
```

The approved revision is the source of truth for intended behavior.

The implementation plan explains how to make the spec real.

The verification report proves whether the implementation satisfies the acceptance criteria.

## Prompt structure

SoundAtlas uses three main prompt types:

| Prompt                             | Purpose                                                       |
| ---------------------------------- | ------------------------------------------------------------- |
| `Spec + Plan Feature`              | Defines intended behavior and creates the implementation plan |
| `Implement Backend API From Spec`  | Implements backend behavior from an approved spec             |
| `Implement Frontend Map From Spec` | Implements frontend behavior from an approved spec            |

The implementation prompts should not redefine product behavior. They should read the approved spec revision, implement only the relevant slice, and verify against acceptance criteria.

## Recommended repo structure

```text
AGENTS.md
docs/
  spec-first-agent-workflow.md
specs/
  template.md
  <feature-slug>/
    r01-<short-desc>.md
    r02-<short-desc>.md
```

`AGENTS.md` should contain only a short pointer to this workflow:

```md
## Spec-first workflow

For feature work, behavior changes, or non-trivial refactors, follow the spec-first process in `docs/spec-first-agent-workflow.md`.

Do not implement directly from a vague request. Create or update a spec first, then implement against approved acceptance criteria.
```

## Spec location

Place feature specs under:

```text
specs/<feature-slug>/rNN-<short-desc>.md
```

Examples:

```text
specs/route-filtering/r01-selection-behavior.md
specs/story-panel-selection/r01-tabbed-inspector.md
specs/youtube-draft-review/r01-draft-review-flow.md
specs/event-time-range-filtering/r01-year-range-filtering.md
```

Spec families live in feature directories. Revision files are immutable once approved.

If a future repository convention provides a better home for specs, use that convention consistently.

## Minimum spec template

Each spec should be short and practical.

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

## Spec quality rules

A spec is ready for implementation when:

* The goal is clear.
* Non-goals are listed.
* Requirements describe intended behavior.
* Acceptance criteria are concrete and testable.
* Assumptions are explicit.
* Blocking open questions are resolved or intentionally deferred.

Avoid vague acceptance criteria such as:

```md
- The UI works well.
- The data is correct.
- The flow is improved.
```

Prefer concrete acceptance criteria such as:

```md
- Given a user opens a route detail page, when the route has related events, then the page shows those events in chronological order.
- Given an event has no reviewed media links, then the UI does not show draft media links as playable content.
- Given seed validation runs, then the changed seed files pass the documented validation checks.
```

## Spec gate

Implementation may proceed only when:

* An approved spec revision path is provided, or the change is explicitly marked as trivial.
* The spec has clear requirements.
* The spec has testable acceptance criteria.
* Blocking questions are resolved or intentionally deferred.

The agent must not implement behavior outside the spec.

If implementation reveals required behavior not described in the approved revision, the agent must draft a new revision first and stop for approval before continuing.

## Blocking questions

Most incomplete input should not stop the agent. The agent should make conservative assumptions and document them.

However, the agent must stop for approval when missing information involves:

* Data loss
* Destructive writes
* Schema changes
* Seed data shape changes
* Permissions or security
* Privacy
* External API behavior
* Generated media review boundaries
* Historically sensitive or uncertain claims
* Irreversible workflow changes
* Production stability risks

## SoundAtlas project constraints

Specs and implementation plans should respect these project constraints:

* Keep changes small, reviewable, and MVP-oriented.
* Current product scope is New York 1965-1985 with curated routes, events, places, connections, and external media links.
* Use existing project conventions in `AGENTS.md`.
* Prefer data-driven implementation from `data/seed/` over hardcoded UI mock data.
* Preserve seed file shapes documented in `docs/seed-validation.md`.
* Keep generated media links as `review_status: "draft"` until manually reviewed.
* Do not store audio or video files in the repository.
* Do not commit secrets, API keys, local paths, or generated media files.
* Do not commit changes unless explicitly requested.

## Planning from a spec

After the spec is drafted, the implementation plan should reference requirement IDs.

Example:

```md
## Implementation Plan

1. Update route data loading for related events.
   - Satisfies: R1, R2
   - Files likely affected: `src/routes/...`

2. Add empty state for routes with no related events.
   - Satisfies: R3
   - Files likely affected: `src/lib/components/...`

3. Add validation coverage.
   - Satisfies: AC1, AC2
   - Files likely affected: `src/lib/...`
```

## Implementation from a spec

When implementation begins, the agent should:

1. Read the approved spec revision.
2. Identify relevant requirements and acceptance criteria.
3. Inspect the existing code before editing.
4. Implement only the behavior described in the spec.
5. Keep changes small and reviewable.
6. Add or update tests/checks where appropriate.
7. Update `TODO.md` only if a TODO item is completed or workflow expectations change.
8. Stop and draft a new spec revision first if new behavior is required.

## Backend implementation expectations

For backend work, use the `Implement Backend API From Spec` prompt.

Backend implementation should:

* Use Python, `uv`, FastAPI, and Pydantic.
* Keep backend application code under `backend/app/`.
* Load MVP data from `data/seed/` until a database is explicitly introduced.
* Use Pydantic schemas for response models.
* Keep route, place, event, and connection field names aligned with seed data.
* Preserve documented seed contracts from `docs/seed-validation.md`.
* Define schemas before endpoint handlers.
* Add or update seed repository behavior with explicit path handling.
* Define unknown ID and empty result behavior.
* Add targeted tests for changed behavior.

Preferred validation:

```sh
cd backend
uv run pytest
```

## Frontend implementation expectations

For frontend map work, use the `Implement Frontend Map From Spec` prompt.

Frontend implementation should:

* Use SvelteKit, TypeScript, and Leaflet.
* Use backend or seed-backed data, not unrelated mock data.
* Keep UI components small and domain-named, such as `MapView`, `Timeline`, `RouteFilter`, and `StoryPanel`.
* Identify the central state owner for selected route and selected event before editing components.
* Keep map marker clicks, timeline interactions, route selection, and story navigation synchronized through the same selected event state.
* Handle loading, empty, error, and selected states.
* Verify Leaflet is only used in browser-safe code.
* Check for Svelte warnings, including invalid self-closing non-void elements such as `<iframe />`.
* Avoid layout overlap and make the first viewport usable.
* Keep the active route narrative and map visually dominant.

Preferred validation:

```sh
npm run check
```

If a narrower frontend check exists, use it first.

## Verification report

After implementation, the agent must report verification against the spec.

Use this format:

```md
## Summary

- What changed.
- Which spec requirements were implemented.

## Requirement mapping

- R1: implemented in `<file path>`
- R2: implemented in `<file path>`
- R3: implemented in `<file path>`

## Acceptance criteria verification

- AC1: Pass/Fail — evidence
- AC2: Pass/Fail — evidence
- AC3: Pass/Fail — evidence

## Tests/checks run

- `<command>` — Pass/Fail

## Files changed

- `<path>`: `<reason>`

## Spec updates

- None, or:
- `<spec path>`: `<what changed and why>`

## Risks/open questions

- `<risk or question>`

## Suggested commit message

- `feat(frontend): ...`
- `feat(backend): ...`
- `test(backend): ...`
- `docs: ...`
```

## Practical Codex CLI usage

### Step 1: create the spec and plan

```text
Use the Spec + Plan Feature prompt for this change:

<describe feature/change>

Planning only. Do not implement yet.
```

Expected output:

* Proposed spec path
* Spec content
* Implementation plan
* Acceptance criteria
* Validation commands
* Risks/open questions
* Suggested file groups
* Suggested commit grouping

### Step 2: approve the spec

After reviewing and editing the spec, explicitly approve it:

```text
The spec revision `specs/<feature-slug>/rNN-<short-desc>.md` is approved.

Implement only what is described in the spec.
Map changes to requirements.
Validate against the acceptance criteria.
Stop and draft a new spec revision first if behavior needs to change.
```

### Step 3: run the relevant implementation prompt

For backend work:

```text
Use Implement Backend API From Spec.

Approved spec revision: `specs/<feature-slug>/rNN-<short-desc>.md`.

Implement only the backend requirements from the spec.
Verify against the backend-relevant acceptance criteria.
```

For frontend map work:

```text
Use Implement Frontend Map From Spec.

Approved spec revision: `specs/<feature-slug>/rNN-<short-desc>.md`.

Implement only the frontend requirements from the spec.
Verify against the frontend-relevant acceptance criteria.
```

### Step 4: verify

After implementation, require a verification report:

```text
Verify the completed work against `specs/<feature-slug>/rNN-<short-desc>.md`.

Report:
- each acceptance criterion as Pass/Fail
- evidence for each result
- tests/checks run
- files changed
- whether the spec changed during implementation
```

## Cross-cutting changes

For changes involving backend, frontend, and data, implement in slices.

Recommended order:

```text
1. Spec + plan
2. Backend/API behavior
3. Frontend API client/types
4. Frontend state and UI behavior
5. Tests/checks
6. Docs/TODO updates
7. Verification report
```

Each slice should still map back to the same spec requirements and acceptance criteria.

## Spec drift

Spec drift happens when implementation behavior differs from the approved spec.

The agent must not silently allow spec drift.

If implementation requires behavior not covered by the spec:

1. Update the spec with the proposed behavior.
2. Explain why the change is needed.
3. Stop for approval.
4. Resume implementation only after approval.

## Smallest enforceable version

At minimum, every non-trivial feature/change needs:

```md
## Goal

## Requirements

## Acceptance criteria

## Assumptions
```

The MVP is intentionally lightweight:

> One spec family, one approved revision, implementation from that revision, verification against acceptance criteria.
