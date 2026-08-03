# Implement Backend API From Issue

Compatibility wrapper for the `soundatlas-backend-implementation` skill.

Use this historical prompt entrypoint when implementing an approved SoundAtlas
backend Issue. The reusable skill owns the implementation gate, backend
constraints, process, validation, reporting, and post-commit lifecycle:

`.codex/skills/soundatlas-backend-implementation/SKILL.md`

Provide the approved Issue number or URL and, when useful, optional context:

- endpoint or backend behavior in scope
- relevant seed files and expected response shapes
- filtering, unknown-ID, and empty-result behavior
- validation commands or runtime constraints

The approved GitHub Issue remains the source of truth. This wrapper does not
authorize implementation by itself and does not replace the required
Grill-Me/Plan Update gates for risk-flagged work.
