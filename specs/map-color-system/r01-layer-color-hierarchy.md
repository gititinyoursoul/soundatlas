# Spec: Map Layer Color Hierarchy

## Status

Implemented

## Revision

r01

## Supersedes

None

## Request

Systemize the map colors so borough colors, contextual place polygons, and route colors work well together. The current borough color style is liked, but the selected South Bronx contextual area should not become a large route-colored fill.

## Goal

Define and implement a small map color hierarchy that keeps the map colorful and elegant while making each color role clear: boroughs communicate geography, contextual polygons communicate place type/context, and route colors communicate narrative selection.

## Non-goals

* NG1: Do not redesign the borough boundary geometry or borough labels.
* NG2: Do not change route colors in seed data.
* NG3: Do not change backend APIs, seed schemas, route selection behavior, timeline behavior, or story panel behavior.
* NG4: Do not introduce a full design-token system beyond the map color roles needed for this slice.

## Change type

* Type: frontend-only
* Type: documentation-only

## Scope

* Routes/pages: main SoundAtlas workspace page
* Components: `MapView`
* Backend endpoints: none
* Seed files: none
* Enrichment files: none
* Docs/TODOs: `docs/design/current-frontend-design.md`

## Requirements

* R1: Document the map color hierarchy: borough color means ambient geography, contextual polygon color means place type/context, and route color means narrative selection.
* R2: Keep the existing borough palette and low-opacity borough styling as the ambient geography layer.
* R3: Contextual place polygons must use semantic place-geometry colors for fills, including when selected.
* R4: Selected contextual place polygons must use route color only as an accent, such as stroke/outline, not as the dominant fill.
* R5: Selected event identity must remain clear through avatar marker ring, selected-place chrome accent, and selected contextual polygon outline.
* R6: The color hierarchy must stay compatible with the current muted OpenStreetMap tile treatment and borough labels.

## Acceptance criteria

* AC1: Given the map renders, then borough overlays still use the existing borough colors with muted opacity.
* AC2: Given South Bronx is the selected place for Birth of Hip-Hop, then the South Bronx polygon no longer appears as a large route-orange fill.
* AC3: Given a contextual place polygon is selected, then its fill color still reflects its place-geometry kind and its outline/accent reflects the selected route color.
* AC4: Given a selected event is visible, then route identity remains obvious through the event avatar ring and selected-place chrome accent.
* AC5: Given the frontend design docs are read, then they describe the map color hierarchy and the intended relationship between borough, contextual polygon, and route colors.
* AC6: Given frontend validation runs, then the Svelte/TypeScript check passes.

## Assumptions

* A1: The current borough palette is visually acceptable and should remain unchanged in this revision.
* A2: Color roles should be coordinated but do not need to come from one single hue scale.
* A3: Route colors remain data-defined in `data/seed/routes.json`.
* A4: Contextual place geometry colors remain frontend-defined until a broader design-token system exists.
* A5: The implementation can refine opacity, stroke weight, and dash style as long as the role hierarchy remains clear.

## Open questions

None.

## Blocking questions

None.

## UX states

* User action: user selects an event whose place has a contextual polygon.
* Visible state: borough geography remains softly visible, the contextual polygon remains readable, and route selection appears as marker/chrome/outline accent.
* Loading state: existing map loading behavior remains unchanged.
* Empty state: if no contextual polygon applies, the map only shows boroughs and event markers as it does now.
* Error state: existing map error behavior remains unchanged.
* Selected state: selected contextual polygons use semantic fill plus route-colored outline/accent.
* Keyboard/accessibility considerations: color remains supplemental; selected event and place names remain available through existing text UI.

## Implementation plan

1. Document the map color hierarchy in the current frontend design doc.
   * Satisfies: R1
   * Files likely affected: `docs/design/current-frontend-design.md`

2. Split contextual polygon fill and stroke styling in `MapView`.
   * Satisfies: R3, R4, R5
   * Files likely affected: `frontend/src/lib/components/MapView.svelte`

3. Preserve borough styling and tile treatment while verifying contextual polygons remain visually compatible.
   * Satisfies: R2, R6
   * Files likely affected: `frontend/src/lib/components/MapView.svelte`

## Validation plan

* AC1:

  * Check: inspect `MapView` borough styling and browser rendering.
  * Command: `cd frontend && npm run check`
* AC2:

  * Check: select a Birth of Hip-Hop event associated with South Bronx and confirm the polygon fill is no longer route-orange.
  * Command: browser or Playwright screenshot review
* AC3:

  * Check: inspect selected contextual polygon style to confirm semantic fill and route-colored outline.
  * Command: `cd frontend && npm run check`
* AC4:

  * Check: select an event and confirm avatar ring and selected-place chrome still use route color.
  * Command: browser or Playwright screenshot review
* AC5:

  * Check: read `docs/design/current-frontend-design.md` for the hierarchy statement.
  * Command: none
* AC6:

  * Check: run frontend validation.
  * Command: `cd frontend && npm run check`

## Suggested validation commands

```sh
cd frontend
npm run check
```

## Risks

* Risk: Reducing route-colored fill may make the selected contextual area feel less obvious. Mitigation: keep a route-colored outline, stronger selected weight, and selected label state.
* Risk: Semantic area colors may still sit too close to borough colors. Mitigation: tune opacity and stroke contrast rather than changing the whole borough palette.

## Review notes

Suggested file groups for review:

* Spec/docs: `specs/map-color-system/r01-layer-color-hierarchy.md`, `docs/design/current-frontend-design.md`
* Frontend: `frontend/src/lib/components/MapView.svelte`

## Suggested commit grouping

* `docs: define map color hierarchy`
* `feat(frontend): refine map contextual polygon colors`

## Verification report

<!-- Fill this in after implementation. -->

### Requirement mapping

* R1: implemented in `docs/design/current-frontend-design.md`
* R2: preserved in `frontend/src/lib/components/MapView.svelte`
* R3: implemented in `frontend/src/lib/components/MapView.svelte` and `frontend/src/lib/data/nyc-place-geometries.ts`
* R4: implemented in `frontend/src/lib/components/MapView.svelte`
* R5: preserved in `frontend/src/lib/components/MapView.svelte`
* R6: preserved in `frontend/src/lib/components/MapView.svelte`

### Acceptance criteria verification

* AC1: Pass — borough styling remains unchanged with existing borough colors, `fillOpacity: 0.2`, muted stroke opacity, and the current tile filter.
* AC2: Pass by code inspection — selected South Bronx uses the semantic `cultural_area` fill instead of the Birth of Hip-Hop route color.
* AC3: Pass — selected contextual polygons use semantic `fillColor` and route-colored `color` for the outline when a selected route color is available.
* AC4: Pass — event avatar rings and selected-place chrome still use route color, while contextual polygon selection uses route color as outline accent.
* AC5: Pass — the current frontend design doc now states the map color hierarchy and route-color boundary.
* AC6: Pass — frontend Svelte/TypeScript validation passed.

### Tests/checks run

* `npm run check` from `frontend/` — Pass

### Files changed

* `docs/design/current-frontend-design.md`: documents the map color hierarchy and route-color boundary.
* `frontend/src/lib/components/MapView.svelte`: splits contextual polygon semantic fill from selected route-colored stroke.
* `frontend/src/lib/data/nyc-place-geometries.ts`: tunes the `cultural_area` color away from route-orange toward a muted contextual area tone.
* `specs/map-color-system/r01-layer-color-hierarchy.md`: records implementation verification.

### Spec updates during implementation

* Marked the approved revision implemented and filled the verification report after validation.
