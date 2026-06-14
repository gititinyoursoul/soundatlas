# Plan Feature

Use this prompt when you want an implementation plan for a new SoundAtlas feature before writing code.

Context to provide
- Feature description and user value.
- Target area: `backend`, `frontend`, `data/seed`, `docs`, or cross-cutting.
- Related MVP route or slice, especially `birth-of-hip-hop`.
- Constraints: no schema breakage, no unreviewed content expansion, no unrelated refactors.
- Non-goals for this change.

Task
- Produce an implementation plan for the feature.

Project constraints
- Keep the MVP focused on New York 1965-1985 and the `Birth of Hip-Hop` vertical slice unless explicitly requested.
- Use existing project conventions in `AGENTS.md`.
- Prefer data-driven implementation from `data/seed/` over hardcoded UI mock data.
- Preserve the seed file shapes documented in `docs/seed-validation.md`.
- Backend work uses Python, `uv`, FastAPI, and Pydantic.
- Frontend work uses SvelteKit, TypeScript, and Leaflet.

Deliverables
- A numbered plan with 5-9 reviewable steps.
- Acceptance criteria that define "done".
- Validation steps, e.g. JSON validation, `uv run pytest`, or frontend smoke checks.
- Open questions or assumptions that should be confirmed before implementation.
- Suggested staged-files grouping and commit message(s).
