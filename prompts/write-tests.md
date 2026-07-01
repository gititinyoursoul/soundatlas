# Write Tests

Use this prompt when adding tests for existing SoundAtlas code.

This prompt is the test-planning and test-implementation entrypoint for the current workflow. If the repo has a matching testing skill, use that skill's instructions and keep this prompt as the compatibility wrapper.

The goal is to prevent agents from jumping straight from "add tests" into broad or brittle test changes. First produce a focused test plan, then implement only the approved test slice.

Core rule:

> Do not write tests directly from a vague request. Plan the test scope first, then implement only the approved tests.

## Context To Provide

* Target module, component, endpoint, data workflow, or seed validation behavior.
* Provided local implementation plan record path, if the tests verify a recorded planned change.
* Expected behavior, edge cases, and any known bug.
* Whether the target is backend, frontend, data validation, or cross-cutting.
* Existing test runner or whether test infrastructure must be added first.
* Whether implementation or planning-only is requested.

## Task

Produce a focused test plan first.

Do not write tests unless explicitly asked after the plan is concrete, or unless the user explicitly asks for implementation in the same request and the plan is small, low-risk, and decision complete.

If the input is incomplete, inspect the relevant code and existing tests before asking questions. Make conservative assumptions when safe, and list anything intentionally out of scope.

## Test Plan Requirements

The test plan must identify:

* Test level: unit, component, integration, end-to-end, or seed/data validation.
* Existing behavior and current coverage.
* Behaviors to cover.
* Behaviors intentionally out of scope.
* Required mocks, fixtures, and environment constraints.
* Test files to add or update.
* Validation commands to run.
* Risks, blockers, or missing infrastructure.

Prefer a small first test slice before broad coverage.

## Project Constraints

* Backend tests should use `pytest` and run through `uv run pytest` when possible.
* Frontend tests should run through `npm test` once frontend test infrastructure exists.
* Mock filesystem paths, network calls, map tiles, and external media sources.
* Do not require real browser network access, audio files, video files, or large fixtures.
* Use small fixture data that mirrors `data/seed/` shapes.
* Keep tests deterministic and independent.
* Do not commit changes unless explicitly requested.

## Backend Coverage Ideas

* `GET /health` returns a simple healthy response.
* Seed loader parses all four seed files.
* Event filtering respects `from_year`, `to_year`, and `route_id`.
* Unknown event IDs return the documented error behavior.
* Connections only reference existing events.

## Frontend Coverage Guidance

* If no frontend test runner exists, propose the smallest appropriate setup before adding dependencies.
* Prefer Vitest for pure TypeScript utilities and lightweight state logic.
* Prefer Svelte Testing Library for component rendering and interaction tests.
* Use Playwright only for browser end-to-end tests, screenshot tests, or Leaflet rendering checks; note environment blockers if Chromium cannot launch.
* Mock Leaflet and map tile/network behavior; do not require real map tiles or browser network access.
* Add or update `npm test` only if adding or changing frontend test infrastructure.
* Keep frontend fixtures small and shaped like current API/seed responses.

## Frontend Coverage Priorities

* Default route selection chooses `birth-of-hip-hop` when available.
* Route selection is single-select.
* The first route event is selected on load when events exist.
* Timeline event clicks update the shared selected event state.
* Map marker selection and story navigation use the same selected event state.
* Story Panel renders selected event, loading, empty, and API error states.
* Media review controls remain visible for admin use until they are gated.
* API client surfaces request failures.

## Implementation Rules

When implementation is approved:

1. Read the test plan and any local implementation plan record it references.
2. Inspect the existing tests and target code before editing.
3. Add only the tests described in the plan.
4. Keep fixtures minimal and local to the test when possible.
5. Avoid broad test infrastructure changes unless the plan explicitly requires them.
6. Run the narrowest relevant validation command first, then broader checks when useful.
7. Report what is covered, what is intentionally out of scope, and any remaining gaps.

## Deliverables

For planning-only requests, return:

1. A short summary of the target behavior.
2. Test level and rationale.
3. Planned test cases.
4. Fixtures and mocks.
5. Files likely affected.
6. Validation commands.
7. Risks, blockers, or out-of-scope behavior.
8. Next step: approve the planned test slice or refine blockers before implementation.

For implementation requests, return:

1. New or updated tests.
2. Notes on what is covered and intentionally not covered.
3. Validation command run and outcome.
4. Next step: commit the tests, add the next missing coverage slice, or run the related implementation/docs workflow.
