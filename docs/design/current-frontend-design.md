# Current Frontend Design

This document records the current intended design concept for the SoundAtlas frontend. It is a baseline for UX audits and redesign passes, not a record of every implemented detail.

Update this document when the intended product surface, design direction, state model, or component roles change.

## Purpose

The frontend should let a user explore New York music history through place, time, and story. For the MVP, the first successful experience is understanding **Birth of Hip-Hop: Bronx 1970-1985** through a coordinated map, timeline, route filter, and story panel.

The first screen should be the product experience itself, not a landing page.

## Design Direction

The current direction is **Research Atlas with selected Story Explorer behavior**.

This means:

- Map-first exploration is the dominant interaction.
- A compact app header gives route orientation without overwhelming the map or selected event.
- Timeline clarifies chronology and sequence.
- Story panel explains the selected event in plain, source-aware language.
- Sources and media are discoverable but secondary to place/time/story understanding.
- The visual tone is dense, documentary, restrained, and useful.

## Primary User Workflow

1. User opens the app.
2. The default route is selected.
3. The map shows relevant places and event markers.
4. The timeline shows the route event sequence.
5. User selects an event from the map, timeline, or story navigation.
6. Map, timeline, and story panel update from the same selected event state.
7. User inspects event summary, significance, place, route context, sources, and media.

## Screen Structure

The current main screen is organized around:

- Compact app header: product name, geographic/time scope, active route title, route years, short route context, route metadata, and API/status summary
- Map: primary spatial exploration surface
- Timeline: route sequence and selected event range
- Story panel: selected event details, navigation, sources, and media

The intended hierarchy is:

1. Map and selected event context
2. Timeline sequence
3. Story details
4. Route switching and metadata
5. Sources and media

## State Model

The main page owns the shared exploration state:

- `routes`
- `places`
- `events`
- `connections`
- `selectedRouteId`
- `selectedEventId`
- `isLoading`
- `errorMessage`

Derived state includes:

- visible events for the selected route
- chronologically ordered visible events
- selected event
- selected place
- selected route
- previous and next event
- selected-event connections
- timeline route and year range

Map marker clicks, timeline clicks, route selection, story navigation, and keyboard navigation should continue to use this shared state rather than creating separate local selection models.

## Component Roles

### `frontend/src/routes/+page.svelte`

Owns data loading, shared selection state, derived selected event/place/route state, keyboard navigation, compact app header, and top-level layout.

### `MapView`

Displays places/events spatially with route color and selected marker state. It should remain browser-safe around Leaflet loading and should not require real map tiles for tests.

### `Timeline`

Shows the route chronology and lets users select events. It should clarify event sequence and selected-event position.

### `RouteFilter`

Currently exists as a reusable component for route switching, but it is not part of the main desktop surface. The intended design is a compact route discovery mechanism rather than a prominent control block. It should remain single-select while the MVP uses one active route at a time.

### `StoryPanel`

Explains the selected event with year, route, place, summary, significance, connections, sources, media, and previous/next navigation.

### `MediaEmbed`

Embeds playable media links when available. Current media review controls are useful for internal/admin workflows but should be gated or removed before a public explorer surface.

## Visual Principles

- Keep the map visually primary.
- Use compact, readable panels rather than marketing-style sections.
- Prefer restrained color and clear hierarchy over decorative styling.
- Keep typography dense enough for repeated research use.
- Make selected state obvious across map, timeline, and story.
- Keep sources visible but not louder than event understanding.
- Preserve usable empty, loading, and error states.
- Design laptop-size screens first, then preserve the workflow on mobile.

## Known Design Gaps

- The map does not yet feel dominant enough in the first viewport.
- Route discovery is unresolved; route switching is temporarily removed from the main desktop surface until it has a compact discovery pattern.
- The Birth of Hip-Hop route range starts at 1970, while an early route event starts in 1967.
- Timeline selection has both ticks and event cards, which can feel visually busy.
- Map selected-event context is mostly marker styling and tooltip-based.
- Mobile behavior needs a clearer ordering strategy for map, timeline, and story panel.
- Media review controls are still visible in the current mixed internal/public surface.

## Open Decisions

- How should pre-1970 hip-hop context be represented in route ranges and timeline layout?
- Where should route discovery live: top utility, dropdown, drawer, sidebar, or separate route overview?
- When and how should admin media review controls be gated?
- Should the map include a persistent selected-event caption or overlay?
- Should timeline event cards remain, become more compact, or move into the story panel?

## Related Documents

- `docs/design/ux-workflow.md`
- `docs/design/2026-06-27-frontend-ux-audit.md`
- `prompts/design-ux.md`
- `docs/mvp-concept.md`
