# SoundAtlas TODO

## Current Focus

The goal of the first MVP is a vertical slice for **Birth of Hip-Hop: Bronx 1970-1985**. This slice should fully demonstrate map, timeline, story panel, route filter, and backend data flow once.

Completed work packages are archived in `docs/done.md`.

## Priority

- Current: improve enrichment quality and unify the shared upstream input for image and media queries.
- Next up: rethink how media types and images are presented and explored in the app.

## Open

### AI Agent Setup and Security

- [ ] Check current AI agent setup and documentation, including current security and rights
- [ ] Upgrade the dev container Codex CLI pin to `@openai/codex` `0.142.4`, rebuild the workspace image, and verify `codex --version`
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
- [ ] Compare `docs/media-retrieval/event-search-components.md` with the image retrieval brief approach and choose one shared upstream process for both image and media enrichment
- [ ] Make `docs/media-retrieval/event-search-components.md` the shared upstream search-input model for both image and media enrichment so query planning starts from the same structured base
- [ ] Improve `event-search-components` with richer time context, structured place disambiguation, typed works, primary supporting terms, and targeted review warnings
- [ ] Fix media enrichment so genre-correct playlists from the wrong decade are filtered or clearly flagged before review

### Enrichment Orchestration

- [ ] Add a single script that triggers all enrichment passes for one event, including media and images, so one command can refresh the full enrichment state
- [ ] Add a shared event-search-components generator so media and image enrichment start from the same structured input
- [ ] Add a shared enrichment preview command that shows media and image query plans for one event side by side
- [ ] Streamline media and image quality reports so they can generate missing provider query results before reporting, instead of requiring separate manual result-generation steps

### Image Enrichment

- [ ] Add LOC and Internet Archive providers to the image enrichment workflow
- [ ] Fix artist image queries so they prefer historically relevant/era-appropriate artists instead of only newer artists with matching names
- [ ] Add place disambiguation to image enrichment so same-name places from other cities or countries are filtered or clearly flagged
- [ ] Add era checks to venue image candidates so wrong-era venue photos are filtered or clearly flagged
- [ ] Show why each image candidate was selected during review, including matched query, specificity signals, confidence, and warning reasons
- [ ] Improve Wild Style image enrichment so fetched images include enough event/context explanation for review
- [ ] Define and enforce the public-image visibility boundary so only reviewed image links render in public-facing UI
- [ ] Implement the reviewed-image presentation behavior in the story panel, including first-image header, attribution, and visible rights notice
- [ ] Confirm the image enrichment pass can reliably reach 3-5 candidates per event when source coverage exists
- [ ] Add final cross-query ranking for image enrichment so candidates are collected across planned queries and the best matches are kept per event
- [ ] Expand provider-specific image normalization so search, pagination, and rights mapping are encapsulated by provider modules

### UX and Design

#### Discovery And Entry

- [ ] Explore a landing page design concept and decide whether it belongs outside the main map-first app surface
- [ ] Explore first route selection behavior for new users before entering the main exploration workspace
- [ ] Explore search bar functionality for finding routes, events, places, sources, and media

#### Map And Timeline

- [ ] Run current screenshots and recheck whether the map feels dominant enough in the first viewport
- [ ] Check out Leaflet base map tile style options
- [ ] Check out Leaflet marker design options
- [ ] Check out Leaflet popups and tooltip design options
- [ ] Check out Leaflet GeoJSON overlay design options
- [ ] Check out Leaflet route, region, and era overlay design options
- [ ] Check out Leaflet controls and map chrome design options
- [ ] Decide how pre-1970 hip-hop context should appear in route ranges and timeline layout
- [ ] Decide whether drawer route selection should keep the overlay open or close after selection
- [ ] Review timeline density behavior for future routes with more events
- [ ] Review the selected-event focal cue across header, map marker/place chrome, timeline, and inspector
- [ ] Reconcile the current mobile ordering implementation with the design baseline and update docs as needed
- [ ] Decide whether timeline event cards should remain, become more compact, or move into the story inspector
- [ ] Review the selection flow across route, map, timeline, and story panel
- [ ] Document the UX acceptance check against the design checklist

#### Media And Image UX

- [ ] Define public-facing image/media browsing behavior, including fixed preview dimensions, long-list handling, lazy loading, and focused image/video inspection
- [ ] Rethink how media types and images should be used in the app, including whether they belong in the story inspector, as evidence, or as primary browsing content
- [ ] Rework image and media exploration in the story inspector

#### Admin And Visibility

- [ ] Define the public/admin visibility policy for restricted drawer items, including hidden vs disabled behavior
- [ ] Gate or remove admin media/image review controls before a public explorer surface
- [ ] Define a separate admin validation workflow before adding Validation back to the drawer
