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

## Target-direction guidance

- [Development Platform Target Principles](development-platform-target-principles.md) — non-binding target-direction guidance for later platform and contract evaluation.

This guidance records evaluation criteria, not implemented behavior or a
binding development-platform contract.

## Related authoritative documentation

- Product and MVP decisions: [`../mvp-concept.md`](../mvp-concept.md)
- Seed structure and validation: [`../data/seed-data-structure.md`](../data/seed-data-structure.md), [`../data/seed-data-validation.md`](../data/seed-data-validation.md)
- Development environment: [`../dev-container.md`](../dev-container.md)
- Current frontend design: [`../design/current-frontend-design.md`](../design/current-frontend-design.md)
- Workflow and Issue planning: [`../workflow-registry.md`](../workflow-registry.md), [`../github-issue-workflow.md`](../github-issue-workflow.md)

Product and data changes update their authoritative documents rather than this
index. A later approved decision or design artifact can establish a binding
development-platform contract, with the GitHub issue controlling that work
recording Human approval and identifying the authoritative artifact. That approved
decision determines whether these non-binding principles remain aligned, need
revision, or are superseded. If superseded, this index points directly to the
replacement authority and labels or replaces the older entry so readers are
not left with stale guidance.
