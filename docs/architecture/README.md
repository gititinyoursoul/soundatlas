# Architecture Documentation

This directory contains current-system architecture sources and clearly labeled
target-direction guidance. It covers system boundaries, component
responsibilities, and runtime data flow without replacing product,
data-contract, design, editorial, enrichment, or development-environment
documentation.

## Current-system descriptions

- [System overview](system-overview.md) — components, boundaries, and repository structure.
- [Frontend architecture](frontend.md) — SvelteKit, Leaflet, UI state, and client data use.
- [Backend architecture](backend.md) — FastAPI, schemas, seed-backed loading, and endpoints.
- [Runtime data flow](data-flow.md) — seed, API/static build, and frontend paths.

These documents are the architecture source of truth for the implemented areas
they describe.

## Current target direction

- [Pane Workspace Runtime Target Principles](pane-workspace-runtime-target-principles.md) — the current minimal, project-neutral runtime scope, responsibility boundary, evidence standard, and deferred questions confirmed by Issue #241.

## Historical target-direction inputs

- [Development Platform Target Principles](development-platform-target-principles.md) — historical, non-binding ownership guidance derived from Issue #209.
- [Development Platform Runtime Architecture Evaluation](development-platform-runtime-architecture-evaluation.md) — Issue #208's historical shared-runtime recommendation, candidate comparison, and evidence gaps.
- [C-Compatible Per-Project Runtime Migration](development-platform-c-compatible-per-project-runtime-migration.md) — Issue #237's historical C-compatible migration design and rollback analysis.

These artifacts remain evidence for the current runtime target, but their
Candidate C, shared-platform, and future-contract direction is not a Milestone
10 requirement. None of the target-direction documents describes implemented
current behavior.

## Related authoritative documentation

- Product and MVP decisions: [`../mvp-concept.md`](../mvp-concept.md)
- Seed structure and validation: [`../data/seed-data-structure.md`](../data/seed-data-structure.md), [`../data/seed-data-validation.md`](../data/seed-data-validation.md)
- Development environment: [`../dev-container.md`](../dev-container.md)
- Current frontend design: [`../design/current-frontend-design.md`](../design/current-frontend-design.md)
- Workflow and Issue planning: [`../workflow-registry.md`](../workflow-registry.md), [`../github-issue-workflow.md`](../github-issue-workflow.md)

Product and data changes update their authoritative documents rather than this
index. Any later broader architecture direction requires its own approved Issue
and current multi-project evidence. The architecture index must continue to
distinguish that future proposal from the current target and implemented
behavior.
