# Spec: Event Inspector Width Balance

## Status

Implemented

## Revision

r02

## Supersedes

r01-tabbed-inspector.md

## Request

Give the selected event inspector a little more width on desktop so the inspector feels less cramped. The map does not need the extra space; the right-side event surface should breathe by taking space from map chrome and other framing instead of from the map content itself.

## Goal

Keep the map visually primary while making the event inspector easier to read and use on desktop screens.

## Non-goals

* NG1: Rework backend endpoints or seed data.
* NG2: Redesign the inspector tab model or event content structure.
* NG3: Make the map larger at the expense of the inspector.
* NG4: Change mobile behavior beyond preserving the existing responsive layout.

## Change type

* Type: frontend-only

## Scope

* Routes/pages: `frontend/src/routes/+page.svelte`
* Components: `frontend/src/lib/components/StoryPanel.svelte`, `frontend/src/lib/components/MapView.svelte`, `frontend/src/lib/components/Timeline.svelte`
* Docs/TODOs: `docs/design/current-frontend-design.md` if the intended layout baseline changes

## Requirements

* R1: Increase the desktop width available to the event inspector so selected-event content has more breathing room.
* R2: Reduce map-side chrome or framing before reducing the map content area itself.
* R3: Preserve the map as the primary surface and keep the inspector subordinate to the map in overall visual hierarchy.
* R4: Preserve the existing shared selection state and route/event behavior.
* R5: Leave the mobile interaction model intact unless a responsive adjustment is needed to preserve readability.

## Acceptance criteria

* AC1: On desktop, the event inspector is visibly wider than before and no longer feels cramped.
* AC2: The map still reads as the primary spatial surface after the layout change.
* AC3: The right-side inspector can display selected-event content without needing to compress the map into an equal-weight split.
* AC4: The selection flow still works the same way across map, timeline, and story inspector.
* AC5: Mobile layout remains usable and does not regress as a result of the desktop width change.

## Assumptions

* A1: The current main screen keeps a two-column desktop layout.
* A2: The map, timeline, and inspector continue to share one central selection state in `+page.svelte`.

## Open questions

* Q1: Should the inspector gain width by shrinking the map column, by reducing header chrome, or by both?
* Q2: Should the desktop width change be a fixed ratio adjustment or a breakpoint-specific layout refinement?

## Blocking questions

* BQ1: None.

## UX states

* User action: User selects an event from the map, timeline, or inspector navigation.
* Visible state: The inspector remains readable and slightly wider on desktop while the map stays visually dominant.
* Loading state: Existing loading behavior remains in place.
* Empty state: Existing empty-state behavior remains in place.
* Error state: Existing error-state behavior remains in place.
* Selected state: The selected event remains obvious in the map, timeline, and inspector.
* Keyboard/accessibility considerations: Existing focus and keyboard navigation should continue to work.

## Implementation plan

1. Adjust the desktop layout balance so the inspector receives more width.
   * Satisfies: R1, R3
   * Files likely affected: `frontend/src/routes/+page.svelte`

2. Trim or rebalance map-side framing so the map content itself is not made smaller than necessary.
   * Satisfies: R2, R3
   * Files likely affected: `frontend/src/routes/+page.svelte`, `frontend/src/lib/components/MapView.svelte`

3. Verify the selection workflow still behaves the same across map, timeline, and inspector.
   * Satisfies: R4, R5
   * Files likely affected: `frontend/src/routes/+page.svelte`, `frontend/src/lib/components/Timeline.svelte`, `frontend/src/lib/components/StoryPanel.svelte`

## Validation plan

* AC1:

  * Check: Desktop inspector width is visibly improved.
  * Command: `npm run check`
* AC2:

  * Check: Map still dominates the first viewport.
  * Command: manual browser review
* AC3:

  * Check: Inspector content reads without feeling compressed.
  * Command: manual browser review
* AC4:

  * Check: Map, timeline, and inspector remain in sync.
  * Command: `npm run check`
* AC5:

  * Check: Mobile layout remains usable after the desktop adjustment.
  * Command: manual browser review

## Suggested validation commands

```sh
npm run check
```

## Risks

* Risk: Increasing inspector width too far could weaken the map-first hierarchy.

## Review notes

Suggested file groups for review:

* Spec/docs:
* Frontend:

## Suggested commit grouping

* `docs(spec): widen event inspector desktop balance`

## Verification report

<!-- Fill this in after implementation. -->

### Requirement mapping

* R1: implemented in `<file path>`
* R2: implemented in `<file path>`
* R3: implemented in `<file path>`
* R4: implemented in `<file path>`
* R5: implemented in `<file path>`

### Acceptance criteria verification

* AC1: Pass/Fail — evidence
* AC2: Pass/Fail — evidence
* AC3: Pass/Fail — evidence
* AC4: Pass/Fail — evidence
* AC5: Pass/Fail — evidence

### Tests/checks run

* `<command>` — Pass/Fail

### Files changed

* `<path>`: `<reason>`

### Spec updates during implementation

* None, or:
* `<what changed and why>`
