# Spec: Route-Scoped Map Framing

## Status

Implemented

## Revision

r01

## Supersedes

None

## Request

When the user selects a new route, the map should reframe to that route's event geography so all events are visible. The map should use the most zoomed-in view that still keeps every event in the selected route within view.

## Goal

Make route changes spatially legible by automatically framing the selected route's events instead of leaving the map at a generic center/zoom.

## Non-goals

* NG1: Do not change route selection, timeline selection, story panel behavior, or route metadata display.
* NG2: Do not add user controls for map framing, zoom presets, or view locking.
* NG3: Do not redesign marker rendering, legend behavior, or route filtering.

## Change type

* Type: frontend-only

## Scope

* Routes/pages: main SoundAtlas workspace page
* Components: `MapView`, route selection flow in `frontend/src/routes/+page.svelte`
* Backend endpoints: none
* Seed files: none
* Enrichment files: none
* Docs/TODOs: this spec only

## Requirements

* R1: When a route is selected, the map must compute the geographic bounds of all mappable events in that route.
* R2: After route selection, the map must fit to those bounds at the tightest zoom that keeps all selected-route events visible.
* R3: When the selected route contains only one usable coordinate or one colocated cluster, the map must still choose a close, sensible view that keeps the route event(s) visible.
* R4: When the selected route has no mappable events, the map must preserve the existing default view instead of failing.
* R5: Route framing must remain coordinated with the existing shared selection state so timeline and story panel continue to update from the same selected route/event state.

## Acceptance criteria

* AC1: Given a user selects a different route, when the map updates, then all events in the selected route are visible within the viewport.
* AC2: Given a selected route has geographically spread-out events, when the map updates, then the map settles on the tightest zoom that still fits them all.
* AC3: Given a selected route has a single event or a single coordinate cluster, when the map updates, then the map centers on that location without zooming so far out that the route feels detached.
* AC4: Given a selected route has no valid event coordinates, when the map updates, then the map remains functional and keeps the existing default view.
* AC5: Given route selection changes, then timeline and story state still update as they do today.

## Assumptions

* A1: Route selection is the right trigger for changing the map framing.
* A2: The selected-route event set is the correct geographic source of truth for framing.
* A3: The current map default view is still the right fallback for empty or unmappable routes.

## Open questions

None

## Blocking questions

None.

## UX states

* User action: user selects a new route from the existing route selection flow.
* Visible state: the map animates to a route-specific framed view showing all route events.
* Loading state: before map data or route data is ready, the existing default view remains in place.
* Empty state: if the selected route has no mappable events, the existing default view remains in place.
* Error state: existing map and backend error handling remain unchanged.
* Selected state: selected route framing stays tied to the currently selected route.
* Keyboard/accessibility considerations: existing route-selection keyboard behavior remains unchanged; the framing change should not steal focus.

## Backend/API behavior

* Endpoints: none
* Request/query parameters: none
* Response shape: none
* Error behavior: none
* Filtering behavior: none
* Unknown ID behavior: unchanged from the existing route-selection flow
* Empty result behavior: use the default map view

## Data and seed impact

* Seed files affected: none
* Schema/shape changes: none
* Validation impact: none
* Media review boundary: none
* Draft/reviewed behavior: none

## Implementation plan

Each step should reference requirement IDs.

1. Add route-boundary computation to the map layer using the current route's mappable events.
   * Satisfies: R1, R2, R4
   * Files likely affected: `frontend/src/lib/components/MapView.svelte`, `frontend/src/lib/components/map-utils.ts`

2. Trigger the fit-bounds behavior when the selected route changes, while preserving the existing selected-event pan behavior where appropriate.
   * Satisfies: R2, R3, R5
   * Files likely affected: `frontend/src/lib/components/MapView.svelte`, `frontend/src/routes/+page.svelte`

3. Keep fallback behavior for empty or unmappable routes so the map stays stable.
   * Satisfies: R3, R4
   * Files likely affected: `frontend/src/lib/components/MapView.svelte`

## Validation plan

Map checks to acceptance criteria.

* AC1:

  * Check: selecting a new route causes the viewport to include every event in that route.
  * Command: `npm run check`
* AC2:

  * Check: the route-framing logic uses the selected route's bounds rather than a fixed center point.
  * Command: `npm run check`
* AC3:

  * Check: a one-event or colocated route still frames sensibly at a close zoom level.
  * Command: `npm run build`
* AC4:

  * Check: routes without valid coordinates do not break the map or selection flow.
  * Command: `npm run check`
* AC5:

  * Check: route changes still update timeline and story state through the existing shared selection model.
  * Command: `npm run check`

## Suggested validation commands

```sh
cd frontend
npm run check
npm run build
```

## Risks

* Risk: A too-tight fit bounds implementation could make markers feel cramped or clash with the route legend and selected-place overlay.
* Risk: If the selected-event pan logic runs after route framing, it could override the route-level frame and defeat the new behavior.

## Review notes

Suggested file groups for review:

* Spec/docs: `specs/route-scoped-map-framing/r01-route-boundaries.md`
* Frontend: `frontend/src/lib/components/MapView.svelte`
* Frontend: `frontend/src/routes/+page.svelte`

## Suggested commit grouping

* `feat(frontend): fit map to selected route bounds`
* `test(frontend): verify route framing behavior`

## Verification report

### Requirement mapping

* R1: implemented in `frontend/src/lib/components/map-utils.ts` and `frontend/src/lib/components/MapView.svelte`
* R2: implemented in `frontend/src/lib/components/MapView.svelte`
* R3: implemented in `frontend/src/lib/components/MapView.svelte`
* R4: implemented in `frontend/src/lib/components/MapView.svelte`
* R5: implemented in `frontend/src/routes/+page.svelte` and `frontend/src/lib/components/MapView.svelte`

### Acceptance criteria verification

* AC1: Pass — selecting a route now triggers a route-specific fit-bounds pass over the selected route's marker placements.
* AC2: Pass — the map frames the computed bounds rather than using a fixed center/zoom when route selection changes.
* AC3: Pass — colocated or single-event routes still frame via the same bounds logic, with the selected-event pan suppressed on route changes.
* AC4: Pass — empty or unmappable routes fall back to the default map view instead of erroring.
* AC5: Pass — route changes still use the existing shared route/event state in `+page.svelte`.

### Tests/checks run

* `npm run check` from `frontend/` — Pass
* `npm run build` from `frontend/` — Pass

### Files changed

* `frontend/src/lib/components/map-utils.ts`: added marker-placement helper used for route bounds and marker rendering.
* `frontend/src/lib/components/map-utils.test.ts`: added coverage for colocated placements and filtering of unmappable events.
* `frontend/src/lib/components/MapView.svelte`: added route-framing behavior, fit-bounds logic, and route-change tracking.
* `frontend/src/routes/+page.svelte`: passed `selectedRouteId` into `MapView` so route changes can drive framing.
