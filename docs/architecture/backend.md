# Backend Architecture

The SoundAtlas backend is a Python 3.13 FastAPI application managed with `uv`.
It provides typed API responses over curated seed data and leaves database
storage for a later product phase.

## Responsibilities

- Load curated JSON records from `data/seed/`.
- Validate API responses with Pydantic schemas.
- Expose route, place, event, and connection data to the frontend.
- Apply approved filtering and identify unknown or empty results according to
  endpoint behavior.
- Keep field names aligned with the documented seed contracts.

## Current structure

```text
backend/
  app/
    main.py
    config.py
    seed_repository.py
    schemas.py
    media_enrichment/
      services.py
      settings.py
  scripts/
  pyproject.toml
  uv.lock
```

## MVP endpoint boundary

- `GET /health`
- `GET /routes`
- `GET /places`
- `GET /events`
- `GET /events/{event_id}`
- `GET /connections`
- `PATCH /events/{event_id}/links`
- `PATCH /events/{event_id}/media-links`

The endpoint list describes the current system; endpoint changes require an
approved Issue and corresponding schema/tests.

## Data and future storage

The backend currently reads static JSON seed files. SQLite or PostgreSQL/PostGIS
may be introduced later for editing, imports, source maintenance, or more
complex filters, but they are not part of the current MVP architecture.

See [seed data structure](../data/seed-data-structure.md), [seed validation](../data/seed-data-validation.md), and [runtime data flow](data-flow.md).
