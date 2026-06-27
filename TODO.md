# SoundAtlas TODO

## Current Focus

The goal of the first MVP is a vertical slice for **Birth of Hip-Hop: Bronx 1970-1985**. This slice should fully demonstrate map, timeline, story panel, route filter, and backend data flow once.

Completed work packages are archived in `docs/done.md`.

## Open

### AI Agent Setup and Security

- [ ] Check current AI agent setup and documentation, including current security and rights
- [x] Rebuild the dev container and verify Playwright Chromium screenshot capture now that the workspace image installs the required browser runtime libraries and exposes a writable Playwright cache

### Repository Maintenance

- [ ] Resolve Git line-ending warning: `warning: in the working copy of 'TODO.md', LF will be replaced by CRLF the next time Git touches it`
- [x] Add frontend test infrastructure and an `npm test` script
- [ ] Add frontend behavior tests for route selection, timeline selection, map/story synchronization, loading/error states, and admin media controls

### UX and Design

- [x] Plan the first map-first UX pass from `docs/design/2026-06-27-frontend-ux-audit.md` and `docs/design/current-frontend-design.md`
- [x] Draft a UI plan for the main exploration view
- [x] Compress the topbar and active route context so the map becomes more dominant in the first viewport
- [x] Add a persistent selected-event summary, caption, or overlay to the map
- [x] Clarify timeline sequence navigation and selected-event emphasis
- [ ] Decide how pre-1970 hip-hop context should appear in route ranges and timeline layout
- [x] Define and implement a mobile ordering strategy for map, timeline, and story panel
- [ ] Gate or remove admin media/image review controls before a public explorer surface
- [ ] Run screenshot critique after the first map-first UX pass
- [x] Reduce route controls/topbar footprint after first map-first pass; current route controls take more topbar space than intended
- [x] Consolidate the topbar and route context into a single compact app header without settings or saved controls
- [x] Implement a desktop overlay navigation drawer with expanded and collapsed icon-only states
- [x] Rework navigation pane for current admin mode: keep route switching and media/image review, remove Research and Validation for now
- [ ] Define a separate admin validation workflow before adding Validation back to the drawer
- [x] Rework route discovery so users can find/switch routes without route controls dominating the desktop header
- [x] Rework selected-event map caption so it adds map-specific context instead of duplicating story panel information
- [x] Fix map layout height so switching between events does not resize the map
- [x] Reduce duplicated route event surfaces; events are currently visible in at least four UI locations
- [ ] Review the selection flow across route, map, timeline, and story panel
- [ ] Document the UX acceptance check against the design checklist
- [x] Run a no-code UX audit of the current frontend app
- [x] Choose the UX design direction for the MVP
- [x] Default the desktop app to the `birth-of-hip-hop` route and select the first route event on load
- [x] Change desktop route selection from multi-select toggles to single-select route selection for the MVP
- [x] Make the desktop timeline show clickable route event ticks instead of only the route year range
- [x] Track timeline density risk for future routes with many events and define when to switch from individual labels to clustering or compact ticks
- [x] Add selected route context to the desktop workspace, including summary or thesis, date range, and visible event count
- [x] Reduce desktop route filter prominence so the active route narrative leads the first view
- [x] Add a compact desktop map legend for route colors and selected event state
- [x] Add `@todo` follow-up in the media review UI noting that internal admin actions should be hidden or gated before a public explorer view
- [x] Improve desktop loading, empty, and API error states across map, timeline, and story panel
