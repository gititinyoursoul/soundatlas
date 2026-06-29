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

### Image Enrichment

- [ ] Add LOC and Internet Archive providers to the image enrichment workflow
- [ ] Define and enforce the public-image visibility boundary so only reviewed image links render in public-facing UI
- [ ] Implement the reviewed-image presentation behavior in the story panel, including first-image header, attribution, and visible rights notice
- [ ] Confirm the image enrichment pass can reliably reach 3-5 candidates per event when source coverage exists
- [ ] Expand provider-specific image normalization so search, pagination, and rights mapping are encapsulated by provider modules

### UX and Design

- [ ] Explore a landing page design concept and decide whether it belongs outside the main map-first app surface
- [ ] Explore first route selection behavior for new users before entering the main exploration workspace
- [ ] Explore search bar functionality for finding routes, events, places, sources, and media
- [ ] Run current screenshots and recheck whether the map feels dominant enough in the first viewport
- [ ] Check out Leaflet base map tile style options
- [ ] Check out Leaflet marker design options
- [ ] Check out Leaflet popups and tooltip design options
- [ ] Check out Leaflet GeoJSON overlay design options
- [ ] Check out Leaflet route, region, and era overlay design options
- [ ] Check out Leaflet controls and map chrome design options
- [ ] Decide how pre-1970 hip-hop context should appear in route ranges and timeline layout
- [ ] Decide whether drawer route selection should keep the overlay open or close after selection
- [ ] Define the public/admin visibility policy for restricted drawer items, including hidden vs disabled behavior
- [ ] Gate or remove admin media/image review controls before a public explorer surface
- [ ] Define a separate admin validation workflow before adding Validation back to the drawer
- [ ] Decide whether timeline event cards should remain, become more compact, or move into the story inspector
- [ ] Review timeline density behavior for future routes with more events
- [ ] Review the selected-event focal cue across header, map marker/place chrome, timeline, and inspector
- [ ] Reconcile the current mobile ordering implementation with the design baseline and update docs as needed
- [ ] Define public-facing image/media browsing behavior, including fixed preview dimensions, long-list handling, lazy loading, and focused image/video inspection
- [ ] Rework image and media exploration in the story inspector
- [ ] Review the selection flow across route, map, timeline, and story panel
- [ ] Document the UX acceptance check against the design checklist
