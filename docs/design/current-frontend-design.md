# Current Frontend Design

This document records the current intended design concept for the SoundAtlas frontend. It is a baseline for UX audits and redesign passes, not a record of every implemented detail.

Update this document when the intended product surface, design direction, state model, or component roles change.

## Purpose

The frontend should let a user explore New York music history through place, time, and story. For the MVP, the first successful experience is understanding **Birth of Hip-Hop: Bronx 1970-1985** through a coordinated map, route sequence timeline, route switching, and selected event inspector.

The first screen should be the product experience itself, not a landing page.

## Design Direction

The current direction is **Research Atlas with selected Story Explorer behavior**.

This means:

- Map-first exploration is the dominant interaction.
- A compact app header gives route orientation without overwhelming the map or selected event.
- The selected event inspector should have enough desktop width to read comfortably without making the map feel secondary.
- Timeline clarifies chronology and sequence.
- The event inspector explains the selected event in plain, source-aware language.
- Sources and media are discoverable but secondary to place/time/story understanding.
- Route context should stay compact and visible above the map without duplicating the inspector.
- The visual tone is dense, documentary, restrained, and useful.

## Primary User Workflow

1. User opens the app.
2. The default route is selected.
3. The map shows relevant places and event markers.
4. The timeline shows the route event sequence.
5. User selects an event from the map, timeline, or inspector navigation.
6. Map, timeline, and event inspector update from the same selected event state.
7. User may focus any place within the selected event from the map or inspector.
8. User inspects the Event's ordered titled story or legacy prose, places,
   route context, sources, and media.

## Screen Structure

The current main screen is organized around:

- Compact app header: product name, geographic/time scope, active route title, route years, short route context, and API/status summary
- Desktop overlay navigation drawer: icon trigger in the header, expanded/collapsed states, route switching, compact editorial route review, admin media/image review queue, direct review actions, and dim overlay behavior
- Map: primary spatial exploration surface
- Timeline: route sequence and selected event range
- Event inspector: selected event details, navigation, sources, related events, and media

The intended hierarchy is:

1. Map and selected event context
2. Timeline sequence
3. Selected-event story and relationships
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
- `selectedPlaceId`
- `isLoading`
- `errorMessage`
- `isNavigationOpen`
- `navigationVariant`
- `activeNavigationItemId`
- `reviewSavingItemId`
- `reviewErrorMessage`

Derived state includes:

- visible events for the selected route
- chronologically ordered visible events
- selected event
- selected place
- selected route
- previous and next event
- selected-event connections
- timeline route and year range
- route event counts
- review queue items

Map marker and polygon clicks, timeline clicks, route selection, inspector
navigation, StoryPanel place controls, related-event clicks, and keyboard
navigation use this shared state rather than separate local selection models.
The selected event remains the story identity; `selectedPlaceId` is constrained
to that event's places and falls back to `default_place_id` only when the
current focus is not valid for the event.

## Component Roles

### `frontend/src/routes/+page.svelte`

Owns data loading, shared selection state, derived selected event/place/route state, keyboard navigation, compact app header, desktop drawer state, and top-level layout.

### `NavigationDrawer`

Provides the desktop-only overlay drawer for route switching and the current editorial and admin review workflows. It supports expanded and collapsed icon-only states, a real-data route list subview, a compact route-readiness and event-finding review, a draft media/image review queue with direct review/reject actions, dim overlay close behavior, `Esc` close behavior, focus return, active item state, and loading/error/empty patterns.

### `Icon`

Provides the local line icons used by the drawer trigger and navigation drawer until a shared icon package or design system is introduced.

### `MapView`

Displays compositional event geography with route color, selected-event state,
and stronger focused-place state. It remains browser-safe around Leaflet
loading and does not require real map tiles for tests. It renders point markers,
shared Polygon/MultiPolygon place geometry, explicit relationship connectors,
selected-place chrome, and separate ambient borough context.

Map color hierarchy:

- Borough color describes ambient geography.
- Place polygon color and line style describe site or interpretive area context.
- Route color describes narrative selection through marker rings, selected-place chrome, and selected contextual polygon outlines.
- Route color should not dominate large map polygon fills; selected contextual polygons should keep semantic fills and use route color as an accent.

Shared geography follows `route-entry-spatial-presentation.md` and arrives
through the same API/static place data as point locations. When several visible
events share a clicked area, the current applicable event is preserved, a sole
matching event is selected, or a compact event chooser is shown.

### `Timeline`

Shows the route chronology and lets users select events. It should clarify event sequence and selected-event position. If the horizontal event-card strip remains as a fallback, it should keep the selected card centered in view.

### `RouteFilter`

Currently exists as a reusable component for route switching, but it is not part of the main desktop surface. Desktop route discovery and route switching now live in the navigation drawer route list. It should remain single-select while the MVP uses one active route at a time.

### `StoryPanel`

Implements the selected event inspector. It explains the selected event with a
compact title-and-metadata header, stable previous/next navigation, Story,
Media, and Related tabs, readable sources, and a continuous story block. Its
Story tab exposes every event place as a keyboard/touch focus control and gives
area precision and place-relationship direction, context, and sources textual
equivalents. The media tab remains exploratory rather than an admin review
surface.

### `MediaEmbed`

Embeds playable media links when available. The active admin review workflow now lives in the navigation drawer; any embedded media controls should stay secondary to the public story-reading surface.

## Visual Principles

- Keep the map visually primary.
- Use compact, readable panels rather than marketing-style sections.
- Prefer restrained color and clear hierarchy over decorative styling.
- Keep typography dense enough for repeated research use.
- Make selected state obvious across map, timeline, and inspector.
- Keep sources visible but not louder than event understanding.
- Preserve usable empty, loading, and error states.
- Design laptop-size screens first, then preserve the workflow on mobile.

## Known Design Gaps

- The map does not yet feel dominant enough in the first viewport.
- The drawer route list needs screenshot critique to decide whether route selection should keep the overlay open or close after selection.
- The Birth of Hip-Hop route range starts at 1970, while an early route event starts in 1967.
- Timeline selection has both ticks and event cards, which can feel visually busy.
- If the horizontal event-card strip remains, selected cards should stay centered so the fallback does not feel detached from the active selection.
- Map selected-event context is split between the compact route header, selected marker/place chrome, timeline, and inspector; it may still need a better single focal cue.
- Mobile behavior has an implemented ordering strategy, but it needs review against the current design baseline and screenshots.
- Public mode must continue to hide or gate editorial and media/image review actions.
- Public-facing image/media browsing still needs a clearer behavior definition for fixed preview dimensions, long media lists, lazy loading, and focused image/video inspection.

## Open Decisions

- How should pre-1970 hip-hop context be represented in route ranges and timeline layout?
- Should drawer route selection keep the overlay open on desktop, or close after a route is selected?
- Should restricted drawer/admin items be hidden or disabled in public-facing contexts?
- What is the public-mode boundary for hiding or gating the admin drawer media/image review workflow?
- Should timeline event cards remain, become more compact, or move into the inspector?
- Should the route header be reduced further once the story inspector becomes more self-contained?

## Related Documents

- `docs/design/ux-workflow.md`
- `docs/design/route-entry-spatial-presentation.md`
- `prompts/design-ux.md`
- `docs/mvp-concept.md`
