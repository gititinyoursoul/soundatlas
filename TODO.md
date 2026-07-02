# SoundAtlas TODO

> Legacy backlog: GitHub Issues are now the source of truth for planned agent
> work. Do not add new planned work here unless explicitly requested as a legacy
> note. Existing entries remain for reference and can be migrated to Issues when
> useful.

## Current Focus

The goal of the first MVP is a vertical slice for **Birth of Hip-Hop: Bronx 1970-1985**. This slice should fully demonstrate map, timeline, story panel, route filter, and backend data flow once.

Completed work packages are archived in `docs/done.md`.

## Priority

- Current: improve enrichment quality and unify the shared upstream input for image and media queries.
- Next up: rethink how media types and images are presented and explored in the app.

## Open

### Enrichment

#### Upstream Inputs

- [ ] Add a route seed scaffold or preview command that reduces manual route updates by checking route, place, event, and connection changes before writing seed JSON

#### Image Enrichment

- [ ] Add LOC and Internet Archive providers to the image enrichment workflow
- [ ] Define and enforce the public-image visibility boundary so only reviewed image links render in public-facing UI
- [ ] Implement the reviewed-image presentation behavior in the story panel, including first-image header, attribution, and visible rights notice

### Repo And Agent Workflow

- [ ] Turn plan-feature prompt into a skill
- [ ] Turn backend and frontend implementation prompts into skills
- [ ] Turn write-tests prompt into a skill
- [ ] Turn update-docs prompt into a skill

### Repository Maintenance

- [ ] Review and address 3 low severity frontend npm audit vulnerabilities
- [ ] Add frontend behavior tests for route selection, timeline selection, map/story synchronization, loading/error states, and admin media controls
- [ ] Find a test coverage setup for `uv` and `npm`
- [ ] Split environment dependency management into prod and dev

### UX and Design

#### Discovery And Entry

- [ ] Explore a landing page design concept and decide whether it belongs outside the main map-first app surface
- [ ] Explore first route selection behavior for new users before entering the main exploration workspace
- [ ] Explore search bar functionality for finding routes, events, places, sources, and media

#### Map And Timeline

- [ ] Check out Leaflet base map tile style options
- [ ] Check out Leaflet marker design options
- [ ] Check out Leaflet popups and tooltip design options
- [ ] Check out Leaflet GeoJSON overlay design options
- [ ] Check out Leaflet route, region, and era overlay design options
- [ ] Check out Leaflet controls and map chrome design options
- [ ] Decide how pre-1970 hip-hop context should appear in route ranges and timeline layout
- [ ] Decide whether drawer route selection should keep the overlay open or close after selection
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
