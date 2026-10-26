---
name: soundatlas-backend-implementation
description: Implement SoundAtlas Python and FastAPI backend changes from approved GitHub Issues, including Pydantic schemas, seed-backed loading, endpoint behavior, filtering, validation, tests, and backend reporting.
---

# SoundAtlas Backend Implementation

This retained entrypoint supplies SoundAtlas requirements for scoped backend
implementation. The runtime selects suitable implementation capabilities and
execution mechanics; ordinary repository/GitHub tools may fulfil them.

Use the registry's [implementation and review composition](../../../docs/workflow-registry.md#implementation-and-review-composition)
for authority inputs, readiness, allowed effects, evidence and stop routes.
When Pane is selected, use its existing composition contract in that registry.
This skill does not prescribe or copy a provider's implementation procedure.

## Required authorities and context

- `AGENTS.md`, `docs/workflow-registry.md` and
  `docs/github-issue-workflow.md` for repository constraints and lifecycle gates.
- The current approved Issue and confirmed decisions, Concept or
  Concept-not-required basis, latest Plan and matching Proceed when required,
  exact named paths and audited derived files, exclusions and allowed effects.
- `docs/architecture/backend.md` for FastAPI/Pydantic, explicit seed loading,
  endpoint continuity and artifact boundaries; `docs/data/seed-data-validation.md`
  for seed-backed behavior and documented data contracts.
- Existing `backend/app/` schemas, handlers, repositories/loaders, relevant
  tests and seed data; the accepted response, filter, unknown-ID and
  empty-result behavior for the slice.
- Applicable project execution/environment authorities and the backend
  validation commands in `AGENTS.md`.

## Required outcome and evidence

The approved slice must provide typed seed-backed behavior consistent with its
schema, data and endpoint contracts. Preserve unaffected endpoint/filter/error
behavior and include focused tests for changed behavior through
`soundatlas-testing-implementation`. An endpoint list is not implicit permission
to expand the MVP or change unrelated behavior.

Return changed paths, acceptance-criteria evidence and actual
`uv run ruff check .`, `uv run pyright` and `uv run pytest` results as required
by `AGENTS.md`, together with applicable seed/reference checks. Record an
unavailable check or partial execution explicitly; it cannot support a pass.
Include risks and unresolved decisions through the registry contract.
`soundatlas-issue-planning` composes the single Issue Implementation Report
including the Review Result; commit and delivery gates remain with the
lifecycle. Preserve this path and discovery manifest until the separate #203
retirement gate.
