# Spec: Active Route Header Color Cue

## Status

Implemented

## Revision

r01

## Supersedes

None

## Request

Use the UX plan for the active route display above the map, but do not show the words "Active route", do not show event count, route tags, or source count in this part of the UI, and avoid adding a route card or increasing header height.

This spec was created retroactively after implementation to repair the skipped spec gate.

## Goal

Make the current route easier to recognize above the map by using the route color as a compact visual cue while keeping the app header map-first and concise.

## Non-goals

* NG1: Do not add a route card, large panel, or extra header section.
* NG2: Do not change route selection behavior, navigation drawer behavior, map markers, timeline behavior, or story panel content.
* NG3: Do not display event count, route tags, or route source count in the active route header area.

## Change type

* Type: frontend-only

## Scope

* Routes/pages: main SoundAtlas workspace page
* Components: app header route context in `frontend/src/routes/+page.svelte`
* Backend endpoints: none
* Seed files: none
* Enrichment files: none
* Docs/TODOs: this spec only

## Requirements

* R1: The route context above the map must show the selected route title, selected route year range when loaded, and compact route thesis or summary.
* R2: The route context must use `activeRoute.color` as a visual accent, with a neutral fallback color before route data loads.
* R3: The route context must not show visible "Active route" copy, event count, route tags, or source count.
* R4: The route context must preserve the existing shared selection state and must not introduce a new local route-selection model.
* R5: The route context must preserve the compact app header footprint and keep the map directly below the header.

## Acceptance criteria

* AC1: Given route data is loaded, when the main workspace renders, then the route context shows route title, route years, and thesis or summary.
* AC2: Given the selected route has a color, when the main workspace renders, then the route context uses that color as a non-text visual accent.
* AC3: Given the main workspace renders, then the route context does not include visible "Active route" text, event count, route tags, or source count.
* AC4: Given the route is switched through existing route selection, then the route context updates from the existing `activeRoute` derived state.
* AC5: Given a mobile viewport, then the route title can wrap without requiring the hidden metadata to reappear.

## Assumptions

* A1: The existing app header is the correct location for route orientation.
* A2: The color accent, title, years, and thesis/summary are enough to communicate current route context.
* A3: Route metadata remains discoverable elsewhere, such as route selection or story surfaces, and does not need to be duplicated in this header.

## Open questions

None.

## Blocking questions

None.

## UX states

* User action: user opens the app or changes route through the existing route selection flow.
* Visible state: route context shows a route-color accent, route title, optional year range, and route thesis/summary.
* Loading state: route context falls back to "Loading route context" and neutral accent color before route data loads.
* Empty state: if no route is available, the loading/fallback route context remains stable.
* Error state: existing backend unavailable notice remains unchanged.
* Selected state: selected route is represented by the active route title and color accent.
* Keyboard/accessibility considerations: existing app header focus behavior remains unchanged; color is supplemental because route title remains visible text.

## Implementation plan

1. Replace the route eyebrow and metadata row with a compact route identity block.
   * Satisfies: R1, R3, R5
   * Files likely affected: `frontend/src/routes/+page.svelte`

2. Bind a CSS custom property to `activeRoute.color` and render a narrow decorative accent.
   * Satisfies: R2, R4
   * Files likely affected: `frontend/src/routes/+page.svelte`

3. Remove unused derived tag display state and obsolete metadata CSS.
   * Satisfies: R3, R5
   * Files likely affected: `frontend/src/routes/+page.svelte`

## Validation plan

* AC1:

  * Check: inspect rendered markup and derived values for title, years, and summary.
  * Command: `npm run check`
* AC2:

  * Check: verify route context uses `--route-color` from `activeRoute.color`.
  * Command: `npm run check`
* AC3:

  * Check: inspect markup to confirm removed label, event count, tags, and source count.
  * Command: `npm run check`
* AC4:

  * Check: verify route context still derives from existing `activeRoute`.
  * Command: `npm run check`
* AC5:

  * Check: inspect responsive CSS for mobile route heading wrap behavior.
  * Command: `npm run build`

## Suggested validation commands

```sh
cd frontend
npm run check
npm run build
```

## Risks

* Risk: Without the explicit "Active route" label, some users may initially read the header as static page context. Mitigation: the route color accent and placement above the map are intended to communicate current route context without extra text.

## Review notes

Suggested file groups for review:

* Spec/docs: `specs/active-route-display/r01-route-color-header.md`
* Frontend: `frontend/src/routes/+page.svelte`

## Suggested commit grouping

* `feat(frontend): add route color cue to header`
* `docs: add active route display spec`

## Verification report

### Requirement mapping

* R1: implemented in `frontend/src/routes/+page.svelte`
* R2: implemented in `frontend/src/routes/+page.svelte`
* R3: implemented in `frontend/src/routes/+page.svelte`
* R4: implemented in `frontend/src/routes/+page.svelte`
* R5: implemented in `frontend/src/routes/+page.svelte`

### Acceptance criteria verification

* AC1: Pass — route context renders `headerRouteTitle`, optional `headerRouteYears`, and `headerRouteSummary`.
* AC2: Pass — route context sets `--route-color` from `activeRoute?.color` with fallback `#314151`, and `.route-accent` uses it.
* AC3: Pass — route context no longer renders "Active route", event count, route tags, or source count.
* AC4: Pass — route display still derives from existing `activeRoute`; no local selection model was added.
* AC5: Pass — mobile CSS allows the route heading to stack and title to wrap.

### Tests/checks run

* `npm run check` from `frontend/` — Pass
* `npm run build` from `frontend/` — Pass

### Files changed

* `frontend/src/routes/+page.svelte`: implements compact route color cue and removes header route metadata.
* `specs/active-route-display/r01-route-color-header.md`: records the retroactive spec, acceptance criteria, implementation mapping, and verification.

### Spec updates during implementation

* This spec was created after implementation to document the already approved UX slice and repair the skipped spec step.
