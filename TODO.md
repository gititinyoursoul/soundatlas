# SoundAtlas TODO

## Current Focus

The goal of the first MVP is a vertical slice for **Birth of Hip-Hop: Bronx 1970-1985**. This slice should fully demonstrate map, timeline, story panel, route filter, and backend data flow once.

Completed work packages are archived in `docs/done.md`.

## Open

### AI Agent Setup and Security

- [ ] Check current AI agent setup and documentation, including current security and rights
- [ ] Fix Playwright Chromium screenshot capture in the agent/dev environment: Chromium downloads successfully, but cannot launch because required OS libraries such as `libglib-2.0.so.0` are missing, and `npx playwright install-deps chromium` cannot switch to root in the current container

### Repository Maintenance

- [ ] Resolve Git line-ending warning: `warning: in the working copy of 'TODO.md', LF will be replaced by CRLF the next time Git touches it`

### UX and Design

- [ ] Run a no-code UX audit of the current frontend app
- [ ] Choose the UX design direction for the MVP
- [ ] Draft a UI plan for the main exploration view
- [ ] Review the selection flow across route, map, timeline, and story panel
- [ ] Run screenshot critique for desktop
- [ ] Document the UX acceptance check against the design checklist
- [x] Default the desktop app to the `birth-of-hip-hop` route and select the first route event on load
- [x] Change desktop route selection from multi-select toggles to single-select route selection for the MVP
- [ ] Make the desktop timeline show clickable route event ticks instead of only the route year range
- [ ] Track timeline density risk for future routes with many events and define when to switch from individual labels to clustering or compact ticks
- [ ] Add selected route context to the desktop workspace, including summary or thesis, date range, and visible event count
- [ ] Reduce desktop route filter prominence so the active route narrative leads the first view
- [ ] Add a compact desktop map legend for route colors and selected event state
- [ ] Add `@todo` follow-up in the media review UI noting that internal admin actions should be hidden or gated before a public explorer view
- [ ] Improve desktop loading, empty, and API error states across map, timeline, and story panel
