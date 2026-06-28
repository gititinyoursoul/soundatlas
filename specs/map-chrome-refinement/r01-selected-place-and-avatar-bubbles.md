# Spec: Selected Place Chrome and Avatar Bubble Refinement

## Status

Implemented

## Revision

r01

## Supersedes

None

## Request

After the screenshot critique, reduce map chrome density by refining the selected-place overlay and avatar event bubbles. The temporary debug overlay has already been removed.

## Goal

Keep the map as the primary surface while making selected place context and event avatar markers useful without crowding the map, especially on mobile.

## Non-goals

* NG1: Do not change route selection, event selection, timeline behavior, or story panel content.
* NG2: Do not change backend APIs, seed data, image link data, or route/event schemas.
* NG3: Do not reintroduce a map legend or debug overlay.
* NG4: Do not redesign borough or contextual place geometry data.

## Change type

* Type: frontend-only

## Scope

* Routes/pages: main SoundAtlas workspace page
* Components: `MapView`, map marker helpers in `map-utils`
* Backend endpoints: none
* Seed files: none
* Enrichment files: none
* Docs/TODOs: this spec only

## Requirements

* R1: The selected-place overlay must stay visible when an event has a selected place, but it must use less map area than the current desktop and mobile card.
* R2: On mobile-width viewports, selected-place chrome must not cover the selected event cluster or materially block timeline access.
* R3: Avatar event bubbles must remain route-colored, clickable, and visually distinct from borough/place labels.
* R4: The selected event avatar must remain clearly identifiable without becoming large enough to dominate nearby route events.
* R5: Marker rendering must continue to use the existing shared `selectedEventId`, selected route events, places, and routes; no local map-only selection model may be introduced.
* R6: The map must not show diagnostic state such as route ids, placement counts, marker counts, or render errors in the user-facing UI.

## Acceptance criteria

* AC1: Given an event is selected, then the map shows compact selected-place context with place name, borough, and route-event count when available.
* AC2: Given a 390px-wide mobile viewport, then the selected-place overlay occupies a compact bottom position and leaves the selected marker cluster and timeline controls usable.
* AC3: Given a route with multiple events visible, then all avatar markers remain clickable and use the route color as the marker ring.
* AC4: Given an event is selected, then its avatar is visibly emphasized compared with other avatars without exceeding a compact marker footprint.
* AC5: Given the main map renders, then no debug overlay or diagnostic text appears on the map.
* AC6: Given route or event selection changes, then selected-place chrome and avatar selection update from the existing shared state.

## Assumptions

* A1: The current avatar marker concept is kept; this pass refines size, contrast, and map density rather than replacing avatars.
* A2: The selected-place overlay remains useful because the map marker alone does not communicate place name and borough.
* A3: Existing route color values are sufficient for marker rings and selected-place accent color.

## Open questions

None.

## Blocking questions

None.

## UX states

* User action: user selects an event from the map, timeline, or story navigation.
* Visible state: selected marker is emphasized and a compact selected-place overlay appears.
* Loading state: existing loading behavior remains unchanged; no selected-place overlay is shown until place data is available.
* Empty state: if no selected place exists, no selected-place overlay is shown.
* Error state: existing backend/map error behavior remains unchanged.
* Selected state: selected marker and selected-place overlay both derive from the same selected event/place state.
* Keyboard/accessibility considerations: selected-place overlay should remain non-interactive status content unless a future spec adds controls; marker click targets must remain large enough for pointer use.

## Implementation plan

1. Compact the selected-place overlay layout and responsive CSS.
   * Satisfies: R1, R2
   * Files likely affected: `frontend/src/lib/components/MapView.svelte`

2. Tune avatar marker sizing, selected scale, ring weight, and shadow so markers read as event points rather than map-obscuring bubbles.
   * Satisfies: R3, R4
   * Files likely affected: `frontend/src/lib/components/map-utils.ts`, `frontend/src/lib/components/MapView.svelte`

3. Preserve the existing marker placement and selection data flow while removing any remaining diagnostic UI.
   * Satisfies: R5, R6
   * Files likely affected: `frontend/src/lib/components/MapView.svelte`

4. Update focused marker helper tests for the final default and selected avatar dimensions.
   * Satisfies: R3, R4
   * Files likely affected: `frontend/src/lib/components/map-utils.test.ts`

## Validation plan

* AC1:

  * Check: selected-place overlay still shows place name, borough, and route-event count when available.
  * Command: `npm run check`
* AC2:

  * Check: capture or manually inspect a 390px-wide mobile viewport to confirm the selected-place overlay does not dominate the map.
  * Command: Playwright screenshot or manual browser review
* AC3:

  * Check: marker helper tests confirm route color ring remains in avatar markup.
  * Command: `npm run test -- map-utils.test.ts`
* AC4:

  * Check: marker helper tests confirm selected avatar dimensions and selected class.
  * Command: `npm run test -- map-utils.test.ts`
* AC5:

  * Check: inspect map markup and screenshot to confirm no diagnostic overlay remains.
  * Command: `npm run check`
* AC6:

  * Check: route/event changes still pass selected route events, selected event, selected place, and selected route into `MapView`.
  * Command: `npm run check`

## Suggested validation commands

```sh
cd frontend
npm run check
npm run test -- map-utils.test.ts
npm run build
```

## Risks

* Risk: Smaller avatars may become hard to distinguish on dense map tiles. Mitigation: keep route-color ring and selected emphasis.
* Risk: A too-small selected-place overlay may no longer explain why the highlighted place matters. Mitigation: keep place name, borough, and route-event count.

## Review notes

Suggested file groups for review:

* Spec/docs: `specs/map-chrome-refinement/r01-selected-place-and-avatar-bubbles.md`
* Frontend: `frontend/src/lib/components/MapView.svelte`
* Tests/helpers: `frontend/src/lib/components/map-utils.ts`, `frontend/src/lib/components/map-utils.test.ts`

## Suggested commit grouping

* `fix(frontend): remove map debug overlay`
* `feat(frontend): refine map selected-place and avatar chrome`

## Verification report

<!-- Fill this in after implementation. -->

### Requirement mapping

* R1: implemented in `frontend/src/lib/components/MapView.svelte`
* R2: implemented in `frontend/src/lib/components/MapView.svelte`
* R3: implemented in `frontend/src/lib/components/map-utils.ts` and `frontend/src/lib/components/MapView.svelte`
* R4: implemented in `frontend/src/lib/components/map-utils.ts` and `frontend/src/lib/components/MapView.svelte`
* R5: preserved in `frontend/src/lib/components/MapView.svelte`
* R6: implemented in `frontend/src/lib/components/MapView.svelte`

### Acceptance criteria verification

* AC1: Pass — selected-place chrome still shows place name, borough, and route-event count.
* AC2: Pass — mobile screenshot at 390px shows a compact bottom overlay that leaves room for the zoom control and timeline.
* AC3: Pass — marker helpers still include the route color ring in avatar markup.
* AC4: Pass — selected avatar uses the selected class and compact `38px` dimensions; unselected avatars use `30px`.
* AC5: Pass — map screenshots and markup no longer show diagnostic route, placement, marker, or render-error text.
* AC6: Pass — `MapView` still receives selected route events, `selectedEventId`, `selectedPlace`, and `selectedRoute` from the main shared state.

### Tests/checks run

* `npm run check` from `frontend/` — Pass
* `npm run test -- map-utils.test.ts` from `frontend/` — Pass
* `npm run build` from `frontend/` — Pass
* Playwright screenshots captured:
  * `screenshots/map-chrome-refinement-desktop.png`
  * `screenshots/map-chrome-refinement-mobile.png`

### Files changed

* `frontend/src/lib/components/MapView.svelte`: compacted selected-place chrome and tuned avatar marker CSS.
* `frontend/src/lib/components/map-utils.ts`: reduced default and selected avatar marker dimensions.
* `frontend/src/lib/components/map-utils.test.ts`: updated marker dimension assertions.
* `specs/map-chrome-refinement/r01-selected-place-and-avatar-bubbles.md`: recorded implementation verification.

### Spec updates during implementation

* Marked the spec implemented and filled the verification report after validation.
