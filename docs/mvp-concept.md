# SoundAtlas MVP Concept

## Working Title

**SoundAtlas: New York 1965-1985**

An interactive music history app that shows how musical scenes in New York influenced each other across place, time, and culture. The dramatic center is New York around 1977, but the MVP deliberately explains both the earlier context and the later development.

## Product Vision

SoundAtlas makes music history explorable as a map with a timeline. Users do not only see isolated events; they understand relationships between places, clubs, communities, technical developments, social conditions, and musical influences.

The first MVP focuses on New York between 1965 and 1985. This period is small enough for a curated prototype and dense enough to demonstrate the core product promise.

## Guiding Question

How did New York become a musical hub between 1965 and 1985, and why does this development intensify around 1977?

## Audience

- Music listeners who want to understand relationships between genres
- Teachers and learners in music, cultural history, and urban history
- Cultural journalism, museums, archives, and curated digital exhibitions
- Users who prefer exploratory learning over linear learning

## MVP Scope

The current MVP route set starts with these curated route areas:

1. **Birth of Hip-Hop**
   - Period: roughly 1970-1985
   - Places: Bronx, Harlem, Manhattan
   - Focus: sound system culture, funk breaks, block parties, DJing, MCing, graffiti, early rap records

2. **Disco to Dance Music**
   - Period: roughly 1973-1985
   - Places: Manhattan, Brooklyn, Queens
   - Focus: club culture, queer spaces, DJ technique, extended mixes, Paradise Garage, post-disco, garage

3. **Punk & New Wave**
   - Period: roughly 1973-1982
   - Places: Bowery, Lower East Side, Downtown Manhattan
   - Focus: CBGB, DIY culture, punk, no wave, new wave, later pop aesthetics

4. **Salsa & Migration**
   - Period: roughly 1965-1980
   - Places: Spanish Harlem, Bronx, Manhattan
   - Focus: Puerto Rican and Caribbean communities, the Fania environment, Latin music as transnational urban culture

5. **Downtown Experiment**
   - Period: roughly 1970-1985
   - Places: SoHo, Lower East Side, Tribeca
   - Focus: loft jazz, minimalism, performance art, no wave, club and art scenes

## Non-Goals for the MVP

- No complete music encyclopedia
- No global world map in the first step
- No proprietary audio or streaming infrastructure
- No public user login, user accounts, playlists, or social features
- No automated data aggregation without editorial review

## Access Model

The public MVP does not require login. A user should be able to open the app, select routes, inspect places and events, read sources, and follow external media links without creating an account.

The MVP may still include an internal admin or editor workflow for validation. That workflow is not a public user feature; it exists to review curated data, validate seed structure, inspect draft media/source links, and mark content as ready for publication. Admin validation controls should be gated, hidden, or clearly separated from the public explorer surface.

## Core Experience

The first view shows a map-first New York workspace with a route sequence timeline. Users can select a route, move through the event sequence, and click events on the map.

Clicking a point opens an event inspector with:

- Title and year
- Place and scene
- Short narrative summary
- Significance for the route
- Connections to earlier and later events
- Source links
- Optional listening examples as external links

## Main Views

### Map View

The map is the primary surface. Every event has coordinates and is color-coded by route. The currently selected route determines the visible event set.

Key functions:

- Marker per event
- Color per route
- Hover or click state
- Optional lines for direct influences
- MVP focus on New York instead of a world map

### Timeline View

The timeline shows the selected route's event sequence and selected-event range. It is sequence navigation, not the primary content surface and not currently a global time-range filter.

Key functions:

- Show the active route's year span
- Show clickable event positions
- Highlight the selected event or event range
- Keep the selected event synchronized with the map and event inspector
- Preserve the open decision about how pre-1970 hip-hop context should appear when a route range starts at 1970

### Event Inspector

The story panel component now behaves as a selected event inspector. It explains the selected event, makes relationships visible, and keeps sources and media discoverable without making them louder than the map.

Key functions:

- Event title, year range, place, and route context
- Story tab with summary, significance, and compact source links
- Media tab with image/media previews and external media actions
- Related tab with incoming and outgoing connections
- Previous/next event navigation
- Clickable connected events that keep route, map, timeline, and inspector state synchronized

### Route Switching

The MVP uses one active route at a time. `Birth of Hip-Hop` is selected by default so the first experience is not empty or unclear.

Desktop route discovery and route switching currently live in the overlay navigation drawer rather than a prominent route filter in the main header. The reusable `RouteFilter` component may still exist, but it is not the main desktop route-switching surface.

## First Vertical Slice

The first fully implemented slice is:

**Birth of Hip-Hop: Bronx 1970-1985**

This route is a good fit because it clearly demonstrates the app's basic principle:

`Jamaican soundsystems -> Bronx DJ culture -> breakbeats -> block parties -> rap records -> film/radio/global spread`

The slice contains:

- A curated event sequence selected through the editorial workflow
- Places and coordinates that make the route geographically legible
- Connections that explain influence, context, media spread, and scene formation
- Map, timeline, route switching, and event inspector
- Data from curated JSON seed files through the FastAPI backend

## Example Events for the First Slice

| Year | Place | Title | Route |
| --- | --- | --- | --- |
| ca. 1967-1972 | Bronx | Caribbean sound system influences in New York | Birth of Hip-Hop |
| 1973 | 1520 Sedgwick Avenue | Kool Herc's Back-to-School Jam | Birth of Hip-Hop |
| 1974-1976 | Bronx parks and community centers | Block parties spread DJ techniques | Birth of Hip-Hop |
| 1976-1977 | Bronx | Grandmaster Flash refines DJ techniques | Birth of Hip-Hop |
| 1977 | New York City | The blackout as an urban rupture | Birth of Hip-Hop |
| 1979 | New York / New Jersey | Rapper's Delight makes rap visible on record | Birth of Hip-Hop |
| 1981 | Manhattan / Bronx | Hip-hop reaches downtown clubs and the art scene | Birth of Hip-Hop |
| 1982 | New York | Wild Style documents early hip-hop culture | Birth of Hip-Hop |
| 1983-1984 | NYC / global | Hip-hop spreads through film, TV, and records | Birth of Hip-Hop |

## Data Model

The MVP should be data-driven. The frontend only renders what the backend provides.

### Route

```json
{
  "id": "birth-of-hip-hop",
  "title": "Birth of Hip-Hop",
  "color": "#e4572e",
  "creator": "gpt-5.5",
  "year_start": 1970,
  "year_end": 1985,
  "summary": "How local parties, DJ technique, Bronx communities, and media circulation turned hip-hop into a global cultural form.",
  "thesis": "Hip-hop emerges from DJ practice, community spaces, urban conditions, and media circulation, not from a single point of origin.",
  "tags": ["dj-culture", "block-party", "breakbeat", "bronx"],
  "review_status": "draft",
  "source_urls": []
}
```

### Place

```json
{
  "id": "1520-sedgwick-avenue",
  "name": "1520 Sedgwick Avenue",
  "borough": "Bronx",
  "place_type": "venue",
  "latitude": 40.8459,
  "longitude": -73.9230,
  "summary": "Apartment building associated with an early Kool Herc party.",
  "review_status": "draft",
  "source_urls": []
}
```

### Event

```json
{
  "id": "kool-herc-back-to-school-jam",
  "route_id": "birth-of-hip-hop",
  "place_id": "1520-sedgwick-avenue",
  "title": "Kool Herc's Back-to-School Jam",
  "year_start": 1973,
  "year_end": 1973,
  "summary": "A party often cited as a symbolic origin point for hip-hop culture.",
  "significance": "Shows how DJ practice, community space and youth culture converged in the Bronx.",
  "tags": ["dj-culture", "block-party", "bronx"],
  "review_status": "draft",
  "source_urls": [],
  "media_links": [],
  "image_links": []
}
```

### Connection

```json
{
  "id": "soundsystems-to-kool-herc",
  "from_event_id": "caribbean-soundsystem-influences",
  "to_event_id": "kool-herc-back-to-school-jam",
  "type": "influence",
  "summary": "Connects Jamaican soundsystem practice with early Bronx DJ culture.",
  "review_status": "draft"
}
```

## Backend Concept

Technology:

- Python
- `uv`
- FastAPI
- Curated JSON seed files for the MVP
- Optional later: SQLite, once editing, imports, source maintenance, or more complex filters are needed
- Optional later: PostgreSQL/PostGIS

Current structure:

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

MVP endpoints:

```text
GET /health
GET /routes
GET /events?from_year=1965&to_year=1985&route_id=birth-of-hip-hop
GET /events/{event_id}
PATCH /events/{event_id}/links
GET /places
GET /connections?route_id=birth-of-hip-hop
```

The backend currently loads data from static JSON seed files. SQLite becomes useful once editing, imports, source maintenance, or more complex filters are needed.

## Frontend Concept

Technology:

- SvelteKit
- Leaflet in the MVP
- TypeScript recommended
- Optional later: MapLibre GL, if vector maps, layer styling, or more complex map interactions become important

Current structure:

```text
frontend/
  src/
    lib/
      api/
      components/
        MapView.svelte
        Timeline.svelte
        RouteFilter.svelte
        StoryPanel.svelte
      types/
    routes/
      +page.svelte
```

Frontend state:

- Active route
- Selected event
- Loaded events, places, and connections
- Navigation drawer state
- Review queue state for draft media/image links

## UX Principles

- The map is the main product, not an add-on to the timeline.
- 1977 is marked as a hub, but not isolated.
- Every route needs a clear thesis; otherwise it becomes an event list.
- Sources and uncertainty are made visible.
- Audio is context, not a prerequisite for use.

## Content Rules

Every event needs at least:

- Year or date range
- Specific place or justified region
- Route
- Short summary
- Significance within the route
- At least one source before publication

For the internal MVP, sources may still be empty, but the data model must include them from the beginning.

## Success Criteria for the MVP

The MVP is successful if a user understands within five minutes:

- Why New York 1965-1985 matters musically
- How at least one scene emerged from several influences
- Which places, people, and technologies played a role
- How the development continues after 1977

## Implementation Plan

### Phase 1: Concept and Data

- Finalize this concept
- Develop the "Birth of Hip-Hop" route through the editorial workflow
- Select events, places, and coordinates based on the route dossier and concept
- Define the source structure

### Phase 2: Backend Slice

- Structure the FastAPI app
- Create JSON seed data
- Provide endpoints for routes, events, places, and connections
- Add simple validation for the seed data
- Keep public read endpoints usable without login; reserve any validation/admin actions for internal use

### Phase 3: Frontend Slice

- Check or initialize the SvelteKit base structure
- Add the Leaflet map
- Build the route sequence timeline
- Connect the event inspector
- Add route switching
- Keep the public explorer usable without authentication and separate admin validation controls from the main user flow

### Phase 4: Editorial Expansion

- Expand additional routes through the same brief, dossier, concept, and seed
  transfer workflow
- Make connections between routes visible
- Complete sources
- Run the first review of the user flow

## Open Decisions

- Should events be told as precise points or as time ranges?
- How strict do sources need to be in the first internal prototype?
- Which map base should be used: OpenStreetMap tiles, MapLibre, or a custom style?
- Should audio initially appear only as an external link or be embedded directly?
- What is the minimal admin validation workflow: seed validation only, media/source review, publication status, or all of these?
- How should pre-1970 hip-hop context be represented in route ranges and timeline layout?
- What is the public-mode boundary for hiding or gating admin media/image review controls?

## Next Concrete Step

Next, continue tightening the current map-first exploration slice: decide how pre-1970 hip-hop context should appear in route ranges and timeline layout, review the selection flow across route, map, timeline, and inspector, and gate or remove admin media/image review controls before a public explorer surface.
