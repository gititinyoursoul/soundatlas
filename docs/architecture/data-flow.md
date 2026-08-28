# Runtime Data Flow

SoundAtlas has two related runtime paths: local/API development and the public
read-only static deployment. Both originate from curated seed data.

## Local/API path

```text
data/seed/*.json
        |
        v
backend seed repository -> Pydantic schemas -> FastAPI endpoints
                                                    |
                                                    v
                                         SvelteKit frontend client/state
```

The backend reads routes, places, events, and connections from the seed files.
For navigation, it derives published and current-review revision membership from
the route publication and review artifacts under `docs/content/routes/`; seed
`review_status` is not publication evidence. Every seed route remains a
reader baseline until replaced. The frontend
requests the typed API responses and route-navigation summary for map, timeline,
route, and story-panel state.

## Public static path

```text
data/seed/*.json + route review/publication artifacts
        |
        v
frontend build generation -> frontend/static/soundatlas-data/
                                                        |
                                                        v
                                             read-only deployed frontend
```

Generated static assets are build inputs for the public deployment and do not
replace `data/seed/` or review/publication artifacts as editorial sources of
truth. Build generation emits a route-navigation summary and filters public
routes, events, places, and connections to published and legacy reader routes.

## Ownership boundaries

- Seed shape and validation: [`../data/seed-data-structure.md`](../data/seed-data-structure.md) and [`../data/seed-data-validation.md`](../data/seed-data-validation.md)
- API schemas and endpoint behavior: [backend architecture](backend.md) and the backend application
- UI state and rendering: [frontend architecture](frontend.md), [current frontend design](../design/current-frontend-design.md), and the [desktop UI guide](../design/desktop-ui-guide.md)
- Media/image enrichment drafts: [`../enrichment/`](../enrichment/)

No audio, video, or image files are stored in the repository; the MVP uses
external media links and review metadata.
