# Write Tests

Use this prompt when adding tests for existing SoundAtlas code.

Context to provide
- Target module, component, endpoint, or seed validation behavior.
- Expected behavior, edge cases, and any known bug.
- Whether the target is backend, frontend, or data validation.
- Existing test runner or whether test infrastructure must be added first.

Task
- Write focused tests for the target behavior.

Test planning
- Before writing tests, identify the test level: unit, component, integration, end-to-end, or seed/data validation.
- List the behaviors to cover and the behaviors intentionally out of scope.
- Identify required mocks, fixtures, and environment constraints.
- If test infrastructure is missing, plan the smallest setup before adding dependencies.
- Prefer a small first test slice before broad coverage.

Project constraints
- Backend tests should use `pytest` and run through `uv run pytest` when possible.
- Frontend tests should run through an `npm test` script once frontend test infrastructure exists.
- Mock filesystem paths, network calls, and external media sources.
- Do not require real map tiles, browser network access, audio files, or large fixtures.
- Use small fixture data that mirrors `data/seed/` shapes.
- Keep tests deterministic and independent.

Backend coverage ideas
- `GET /health` returns a simple healthy response.
- Seed loader parses all four seed files.
- Event filtering respects `from_year`, `to_year`, and `route_id`.
- Unknown event IDs return the documented error behavior.
- Connections only reference existing events.

Frontend coverage ideas
- Timeline filtering produces the expected visible event IDs.
- Route filters preserve selected route state.
- Story Panel renders selected event fields and empty states.
- API client handles errors and empty responses.

Frontend test guidance
- If no frontend test runner exists, propose and add the smallest appropriate setup first.
- Prefer Vitest for pure TypeScript utilities and lightweight state logic.
- Prefer Svelte Testing Library for component rendering and interaction tests.
- Use Playwright only for browser end-to-end tests, screenshot tests, or Leaflet rendering checks; note environment blockers if Chromium cannot launch.
- Mock Leaflet and map tile/network behavior; do not require real map tiles or browser network access.
- Add or update `npm test` when adding frontend tests.
- Keep frontend fixtures small and shaped like current API/seed responses.

Frontend coverage priorities
- Default route selection chooses `birth-of-hip-hop` when available.
- Route selection is single-select.
- The first route event is selected on load when events exist.
- Timeline event clicks update the shared selected event state.
- Map marker selection and story navigation use the same selected event state.
- Story Panel renders selected event, loading, empty, and API error states.
- Media review controls remain visible for admin use until they are gated.
- API client surfaces request failures.

Deliverables
- Brief test plan before implementation when adding new test infrastructure or covering multiple behaviors.
- New or updated tests in the appropriate test location.
- Notes on what is covered and intentionally not covered.
- Validation command run and outcome.
