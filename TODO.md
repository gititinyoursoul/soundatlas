# SoundAtlas TODO

## Current Focus

The goal of the first MVP is a vertical slice for **Birth of Hip-Hop: Bronx 1970-1985**. This slice should fully demonstrate map, timeline, story panel, route filter, and backend data flow once.

Completed work packages are archived in `docs/done.md`.

## Open

### AI Agent Setup and Security

- [ ] Check current AI agent setup and documentation, including current security and rights
- [ ] Configure Playwright screenshot capture to use a different dev server port than the local browser so both can run at the same time

### Repository Maintenance

- [ ] Resolve Git line-ending warning: `warning: in the working copy of 'TODO.md', LF will be replaced by CRLF the next time Git touches it`
- [ ] Add frontend behavior tests for route selection, timeline selection, map/story synchronization, loading/error states, and admin media controls
- [ ] Find a test coverage setup for `uv` and `npm`
- [ ] Split environment dependency management into prod and dev
- [ ] Remove design documents and images that are no longer needed

### UX and Design

- [ ] Decide how pre-1970 hip-hop context should appear in route ranges and timeline layout
- [ ] Gate or remove admin media/image review controls before a public explorer surface
- [ ] Run screenshot critique after the first map-first UX pass
- [ ] Define a separate admin validation workflow before adding Validation back to the drawer
- [ ] Review the selection flow across route, map, timeline, and story panel
- [ ] Document the UX acceptance check against the design checklist
