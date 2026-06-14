# Test Writing

Use this prompt when adding tests for existing SoundAtlas code.

Context to provide
- Target module, component, endpoint, or seed validation behavior.
- Expected behavior, edge cases, and any known bug.
- Whether the target is backend, frontend, or data validation.

Task
- Write focused tests for the target behavior.

Project constraints
- Backend tests should use `pytest` and run through `uv run pytest` when possible.
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

Deliverables
- New or updated tests in the appropriate test location.
- Notes on what is covered and intentionally not covered.
- Validation command run and outcome.
