# Architecture Documentation

This directory is the source of truth for stable technical descriptions of the
SoundAtlas system. It explains system boundaries, component responsibilities,
and runtime data flow without replacing product, data-contract, design,
editorial, enrichment, or development-environment documentation.

## Documents

- [System overview](system-overview.md) — components, boundaries, and repository structure.
- [Frontend architecture](frontend.md) — SvelteKit, Leaflet, UI state, and client data use.
- [Backend architecture](backend.md) — FastAPI, schemas, seed-backed loading, and endpoints.
- [Runtime data flow](data-flow.md) — seed, API/static build, and frontend paths.

## Related authoritative documentation

- Product and MVP decisions: [`../mvp-concept.md`](../mvp-concept.md)
- Seed structure and validation: [`../data/seed-data-structure.md`](../data/seed-data-structure.md), [`../data/seed-data-validation.md`](../data/seed-data-validation.md)
- Development environment: [`../dev-container.md`](../dev-container.md)
- Current frontend design: [`../design/current-frontend-design.md`](../design/current-frontend-design.md)
- Workflow and Issue planning: [`../workflow-registry.md`](../workflow-registry.md), [`../implementation-plan-workflow.md`](../implementation-plan-workflow.md)

Architecture documents describe existing system behavior. Product or contract
changes must update their authoritative product or data documents first.
