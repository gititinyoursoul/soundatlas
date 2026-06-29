# SoundAtlas TODO

## Current Focus

The goal of the first MVP is a vertical slice for **Birth of Hip-Hop: Bronx 1970-1985**. This slice should fully demonstrate map, timeline, story panel, route filter, and backend data flow once.

Completed work packages are archived in `docs/done.md`.

## Open

### AI Agent Setup and Security

- [ ] Check current AI agent setup and documentation, including current security and rights
- [ ] Configure Playwright screenshot capture to use a different dev server port than the local browser so both can run at the same time
- [ ] Turn plan-feature prompt into a skill
- [ ] Turn backend and frontend implementation prompts into skills
- [ ] Turn write-tests prompt into a skill
- [ ] Turn update-docs prompt into a skill

### Repository Maintenance

- [ ] Add frontend behavior tests for route selection, timeline selection, map/story synchronization, loading/error states, and admin media controls
- [ ] Find a test coverage setup for `uv` and `npm`
- [ ] Split environment dependency management into prod and dev
- [ ] Remove design documents and images that are no longer needed

### Media Enrichment

- [ ] Add a YouTube media availability audit step to the enrichment workflow that records embed vs external playback mode
- [ ] Recheck every current YouTube video link for playable, embeddable, external-only, private, deleted, or unavailable status

### UX and Design

- [ ] Check out Leaflet base map tile style options
- [ ] Check out Leaflet marker design options
- [ ] Check out Leaflet popups and tooltip design options
- [ ] Check out Leaflet GeoJSON overlay design options
- [ ] Check out Leaflet route, region, and era overlay design options
- [ ] Check out Leaflet controls and map chrome design options
- [ ] Decide how pre-1970 hip-hop context should appear in route ranges and timeline layout
- [ ] Gate or remove admin media/image review controls before a public explorer surface
- [ ] Define a separate admin validation workflow before adding Validation back to the drawer
- [ ] Review the selection flow across route, map, timeline, and story panel
- [ ] Document the UX acceptance check against the design checklist
