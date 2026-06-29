# Plan-Led Agent Workflow

This document defines the lightweight agent workflow for SoundAtlas.

The default workflow is now plan-led:

> Do not implement from a vague request. Inspect the repo, propose a concrete plan when the work is non-trivial, and implement after the human approves that plan. Specs are optional local planning records, not a mandatory approval gate.

The filename stays `docs/spec-first-agent-workflow.md` for compatibility with existing links and prompts.

## When to Plan

Use a plan before implementation for:

* New features
* UX behavior changes
* Backend/API behavior changes
* Seed data shape or data workflow changes
* Media retrieval or enrichment workflow changes
* Cross-cutting frontend/backend/data changes
* Non-trivial refactors
* Anything involving user-visible behavior
* Anything involving production-critical flows

A plan is usually not needed for:

* Typo fixes
* Formatting-only changes
* Tiny copy edits
* Mechanical renames
* Comments-only changes
* Trivial documentation edits
* Dependency bumps with no behavior change

For trivial changes, the agent may proceed directly if the request is clear and low-risk.

## Default Workflow

```text
1. Human gives a feature/change request.
2. Agent inspects the repo before asking questions.
3. Agent proposes a concrete implementation plan when the work is non-trivial.
4. Human approves the plan with wording such as "approved", "implement the plan", or "please do it".
5. Agent implements the approved plan.
6. Agent validates the change with the relevant checks.
7. Agent reports what changed, what was verified, and any remaining risk.
```

The approved plan is the source of truth for intended behavior during that implementation turn.

## Specs As Local Records

Specs under `specs/` are local planning records. In solo work they are gitignored by default and are not mandatory approval gates.

Create a local spec record when:

* The human explicitly asks for one.
* A plan is approved for non-trivial feature, UX, backend, data, or cross-cutting work and the implementation would benefit from later analysis.
* The work introduces behavior that future agents need to verify against acceptance criteria.

The spec record does not need separate human approval. It should capture the approved plan and the final verification result.

Use this path:

```text
specs/<feature-slug>/rNN-<short-desc>.md
```

For generated records, use:

* Status before implementation: `Approved`
* Status after successful implementation: `Implemented`
* Contents: request, goal, non-goals, requirements, acceptance criteria, assumptions, implementation plan, validation plan, and verification report

If a spec already exists for the work, the agent may implement from it, but the spec is still just the chosen source of truth for that task, not a repository-wide requirement.

Do not commit spec files during solo work unless the human explicitly asks for them to be committed.

## Implementation Gate

Implementation may proceed when:

* The human has approved a concrete plan, or the human provided a spec for this task, or the change is clearly trivial.
* Requirements are clear enough to implement.
* Acceptance criteria are testable enough to verify.
* Blocking questions are resolved or intentionally deferred.

The agent must not implement behavior outside the approved plan or provided spec.

If implementation reveals missing behavior, the agent should:

* Continue and record an assumption when the decision is low-risk and local to implementation.
* Stop for approval when the decision changes product behavior, data shape, security, privacy, external API behavior, generated media review boundaries, historically sensitive claims, irreversible workflow behavior, or production stability.

## Blocking Questions

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

## SoundAtlas Project Constraints

Plans and implementation should respect these project constraints:

* Keep changes small, reviewable, and MVP-oriented.
* Current product scope is New York 1965-1985 with curated routes, events, places, connections, and external media links.
* Use existing project conventions in `AGENTS.md`.
* Prefer data-driven implementation from `data/seed/` over hardcoded UI mock data.
* Preserve seed file shapes documented in `docs/seed-validation.md`.
* Keep generated media links as `review_status: "draft"` until manually reviewed.
* Do not store audio or video files in the repository.
* Do not commit secrets, API keys, local paths, or generated media files.
* Do not commit changes unless explicitly requested.

## Backend Implementation Expectations

Backend implementation should:

* Use Python, `uv`, FastAPI, and Pydantic.
* Keep backend application code under `backend/app/`.
* Load MVP data from `data/seed/` until a database is explicitly introduced.
* Use Pydantic schemas for response models.
* Keep route, place, event, and connection field names aligned with seed data.
* Preserve documented seed contracts from `docs/seed-validation.md`.
* Define unknown ID and empty result behavior.
* Add targeted tests for changed behavior.

Preferred validation:

```sh
cd backend
uv run pytest
```

## Frontend Implementation Expectations

Frontend implementation should:

* Use SvelteKit, TypeScript, and Leaflet.
* Use backend or seed-backed data, not unrelated mock data.
* Keep UI components small and domain-named, such as `MapView`, `Timeline`, `RouteFilter`, and `StoryPanel`.
* Identify the central state owner for selected route and selected event before editing components.
* Keep map marker clicks, timeline interactions, route selection, and story navigation synchronized through the same selected event state.
* Handle loading, empty, error, and selected states.
* Verify Leaflet is only used in browser-safe code.
* Avoid layout overlap and make the first viewport usable.
* Keep the active route narrative and map visually dominant.

Preferred validation:

```sh
cd frontend
npm run check
```

If a narrower frontend check exists, use it first.

## Verification Report

After implementation, the agent should report:

```md
## Summary

- What changed.
- Which approved plan/spec requirement was implemented.

## Verification

- `<command>` - Pass/Fail

## Files changed

- `<path>`: `<reason>`

## Assumptions or drift

- None, or:
- `<assumption/change and why it stayed within the approved plan>`

## Next step

- `<concrete follow-up action>`
```

If a local spec record was created, update its verification report before finishing.

## Practical Codex Usage

Typical fast path:

```text
Plan this change first:

<describe feature/change>
```

Then approve the plan:

```text
Implement the plan.
```

For work that needs a record:

```text
Implement the plan and create a local spec record for analysis.
```

For work that should stay planning-only:

```text
Planning only. Do not edit files.
```

## Drift

Drift happens when implementation behavior differs from the approved plan or spec.

The agent must not silently allow drift. It should record low-risk implementation assumptions in the final report or generated spec record, and stop for approval when the difference changes product intent or another high-risk boundary.
