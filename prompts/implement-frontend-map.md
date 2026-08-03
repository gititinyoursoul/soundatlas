# Implement Frontend Map From Issue

Compatibility wrapper for the `soundatlas-frontend-implementation` skill.

Use this historical prompt entrypoint when implementing an approved SoundAtlas
frontend Issue. The reusable skill owns the implementation gate, frontend
constraints, process, validation, and Implementation Report format:

`.codex/skills/soundatlas-frontend-implementation/SKILL.md`

Provide the approved Issue number or URL and, when useful, optional context:

- viewport target: desktop, mobile, or both
- route selection model: single-select or multi-select
- surface type: public-facing, admin-only, or mixed
- expected interactions and related API or seed fields

The approved GitHub Issue remains the source of truth. This wrapper does not
authorize implementation by itself and does not replace the required
Grill-Me/Plan Update gates for risk-flagged work.
