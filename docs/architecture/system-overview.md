# System Overview

SoundAtlas is a map-first interactive music-history application. The public
experience explores curated history across place, time, and cultural connection
through a synchronized map, timeline, route selection, and story panel.

## System boundaries

```text
Curated seed data and enrichment drafts
                |
                v
     Backend schemas and API
                |
                v
 Frontend route, map, timeline, and story state
                |
                v
       Interactive explorer UI
```

The MVP uses curated JSON files under `data/seed/` as the editorial data
source. The backend reads that data for local/API use, while the frontend can
also consume generated static data for the public read-only deployment.

## Main components

- `backend/` — FastAPI application, Pydantic schemas, seed repository, and
  enrichment-related services.
- `frontend/` — SvelteKit/TypeScript application with Leaflet map, timeline,
  route controls, story panel, and shared selection state.
- `data/` — curated seed records and enrichment artifacts.
- `docs/` — product, architecture, data, design, editorial, enrichment, and
  workflow documentation.
- `scripts/` — local development and repository helper commands.

The detailed frontend and backend responsibilities are documented in
[frontend architecture](frontend.md) and [backend architecture](backend.md).

## Product/runtime relationship

The map is the primary MVP surface. Timeline, route selection, marker
selection, related-event navigation, and the story panel use the same central
data and selection model. Product vision, scope, UX principles, and content
rules remain authoritative in [`../mvp-concept.md`](../mvp-concept.md).

## Related documentation

- [Runtime data flow](data-flow.md)
- [Seed data structure](../data/seed-data-structure.md)
- [Current frontend design](../design/current-frontend-design.md)
- [Development container](../dev-container.md)
