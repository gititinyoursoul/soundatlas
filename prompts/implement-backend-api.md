# Implement Backend API

Use this prompt when implementing or changing the SoundAtlas FastAPI backend.

Context to provide
- Endpoint or backend behavior to implement.
- Relevant seed data and expected API response shape.
- Error behavior and filtering requirements.

Task
- Implement backend behavior using Python, `uv`, FastAPI, and Pydantic.

Project constraints
- Backend application code should live under `backend/app/`.
- Load MVP data from `data/seed/` until a database is introduced.
- Use Pydantic schemas for response models.
- Keep route, place, event, and connection field names aligned with seed data.
- Preserve documented seed contracts from `docs/seed-validation.md`.
- Do not introduce a database until explicitly requested.

Expected MVP endpoints
- `GET /health`
- `GET /routes`
- `GET /events`
- `GET /events/{event_id}`
- `GET /places`
- `GET /connections`

Process
- Define schemas before endpoint handlers.
- Add a seed repository or loader with explicit path handling.
- Implement filtering for `from_year`, `to_year`, and `route_id`.
- Define behavior for unknown IDs and empty results.
- Add targeted tests for health, seed loading, event filtering, and unknown IDs.
- Run `uv run pytest` from `backend/` when tests exist.

Deliverables
- Backend code changes.
- Tests for changed behavior.
- Updated docs or TODOs if workflow changes.
- Validation command run and outcome.
- Suggested commit message, usually `feat(backend): ...` or `test(backend): ...`.
