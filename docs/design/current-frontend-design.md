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

The approved navigation target is illustrated in
[`persistent-route-multi-review-navigation.svg`](mockups/persistent-route-multi-review-navigation.svg).
It is a design target, not a statement that the current frontend already
implements multi-route review summaries.

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
- Persistent route selector: directly visible in the primary interface in every mode, with one active route controlling map, timeline, and story context
- Operational navigation: mode-specific access to editorial route review and admin media/image review without owning route selection
- Editorial all-routes overview: simultaneous route-level readiness summaries with one active route detail and no bulk approval or publication
- Map: primary spatial exploration surface
- Timeline: route sequence and selected event range
- Event inspector: selected event details, navigation, sources, related events, and media

The intended hierarchy is:

1. Active route and map context
2. Timeline sequence
3. Selected-event story and relationships
4. Mode-specific review tasks
5. Sources and media

## Navigation Across Modes

The route selector is an exploration control, not an administrative task. It
must remain directly available in every mode and must not require opening the
navigation drawer or entering a nested route subview.

| Mode | Persistent primary navigation | Mode-specific operations |
| --- | --- | --- |
| Public static explorer | Select one active route | None; editorial and media review remain unavailable |
| API/admin explorer | Select one active route | Media/image review may span events from several routes |
| Editorial mode | Select one active route and retain an all-routes readiness overview | Inspect and change one route's exact review revision; publish only that selected revision |

“Several routes at the same time” means that editorial route summaries remain
visible together for orientation and work selection. It does not mean that
several routes become active on the map or timeline, or that approval and
publication become bulk operations.

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

The navigation target introduces a distinction between two kinds of route
state:

- **Active route:** the single route controlling the map, timeline, StoryPanel,
  detailed editorial review, and revision-bound publication action.
- **All-routes review overview:** route-level counts, warnings, blockers,
  availability, and readiness used to choose the next route to inspect. This
  overview does not own editorial decisions or publication authority.

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

Remains an operational surface for mode-specific editorial and admin work. It
does not own primary route selection. Public mode does not expose restricted
review actions; API/admin mode may expose media review; editorial mode exposes
route review and exact-revision publication controls.

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

Owns directly visible, single-select route switching in the primary interface.
The desktop treatment may use a compact route rail or equivalent persistent
control. The narrow-screen treatment may condense the same choices, but it must
remain visible and operable without opening a hidden navigation layer.

## Responsive And Accessibility Behavior

- Narrow screens retain a directly visible active-route control and access to
  the other routes; route selection must not disappear at a breakpoint.
- A compact selector may be paired with horizontally accessible route choices,
  provided every route remains keyboard and touch operable.
- Active-route state must be conveyed by text or programmatic state as well as
  color.
- Route choices use descriptive accessible names and expose the current choice.
- Editorial readiness summaries distinguish ready, warning, blocked, draft,
  unavailable, loading, and error states without relying only on color.
- Moving between route summaries and one route's detail preserves focus context
  and does not imply that more than one revision is being edited.

## Navigation Non-Goals

- Showing several routes' events together on the map or timeline.
- Bulk editorial approval, bulk overrides, or bulk publication.
- A generalized dashboard, multi-user administration system, or new editorial
  workflow service.
- Moving media review into the public explorer.
- Treating the all-routes overview as an authority over route-specific review
  records.

### `StoryPanel`

Implements the selected event inspector. It explains the selected event with a
compact title-and-metadata header, stable previous/next navigation, Story,
Media, and Related tabs, readable sources, and a continuous story block. Its
Story tab exposes every event place as a keyboard/touch focus control and gives
area precision and place-relationship direction, context, and sources textual
equivalents. The media tab remains exploratory rather than an admin review
surface.

#### Event story hierarchy

![Event StoryPanel mockup showing an Event title followed by two ordered titled story sections, each with one paragraph.](mockups/issue-160-event-story-section-hierarchy.png)

The route narrative groups Events. Each selected Event is the complete
reader-facing chapter beneath its Event title. A section-based Event contains
one or more ordered story sections, each with a distinct Human-reviewed heading
and body.

The current hierarchy is: route narrative section -> Event title/chapter ->
ordered story-section heading and one rendered paragraph. `StoryPanel` renders
each story-section body as a single HTML paragraph. Multiple paragraphs beneath
one story-section heading are not currently supported. This mockup documents
current behavior; it does not authorize new route copy or a behavior change.

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
- The persistent route-selector and all-routes editorial overview are approved design targets but are not yet implemented.
- The Birth of Hip-Hop route range starts at 1970, while an early route event starts in 1967.
- Timeline selection has both ticks and event cards, which can feel visually busy.
- If the horizontal event-card strip remains, selected cards should stay centered so the fallback does not feel detached from the active selection.
- Map selected-event context is split between the compact route header, selected marker/place chrome, timeline, and inspector; it may still need a better single focal cue.
- Mobile behavior has an implemented ordering strategy, but persistent route selection and editorial overview still require implementation and screenshot review.
- Public mode must continue to hide or gate editorial and media/image review actions.
- Public-facing image/media browsing still needs a clearer behavior definition for fixed preview dimensions, long media lists, lazy loading, and focused image/video inspection.

## Open Decisions

- How should pre-1970 hip-hop context be represented in route ranges and timeline layout?
- Should restricted drawer/admin items be hidden or disabled in public-facing contexts?
- What is the public-mode boundary for hiding or gating the admin drawer media/image review workflow?
- Should timeline event cards remain, become more compact, or move into the inspector?
- Should the route header be reduced further once the story inspector becomes more self-contained?

## Related Documents

- `docs/design/ux-workflow.md`
- `docs/design/route-entry-spatial-presentation.md`
- `prompts/design-ux.md`
- `docs/mvp-concept.md`
