# Write Tests

Compatibility wrapper for the `soundatlas-testing-implementation` skill.

Use this historical prompt entrypoint when planning or implementing approved
SoundAtlas test work. The reusable skill owns focused test planning, scope
gates, fixtures and mocks, backend/frontend guidance, validation, reporting,
and post-commit lifecycle:

`.codex/skills/soundatlas-testing-implementation/SKILL.md`

Provide the approved Issue number or URL and, when useful, optional context:

- target module, component, endpoint, data workflow, or seed validation
- expected behavior, edge cases, and known bugs
- target area and test level
- existing runner, fixture, mock, or environment constraints
- whether planning-only output or approved implementation is requested

The approved GitHub Issue or concrete focused test scope remains authoritative.
This wrapper does not authorize implementation by itself and does not replace
the required Grill-Me/Plan Update gates for risk-flagged work.
