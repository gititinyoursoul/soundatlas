# Spec: Timeline Sequence

## Status

Draft

## Revision

r01

## Supersedes

None

## Request

Tighten the SoundAtlas timeline so it behaves as compact sequence context instead of a second content feed.

## Goal

The timeline should clearly show route chronology, selected-event position, and usable event selection while staying visually subordinate to the map and event inspector.

## Non-goals

* NG1: Turn the timeline into a chronology workspace or content board.
* NG2: Change backend data shape.

## Change type

* Type: frontend-only

## Scope

* Routes/pages: `frontend/src/routes/+page.svelte`
* Components: `frontend/src/lib/components/Timeline.svelte`
* Docs/TODOs: `docs/design/current-frontend-design.md`

## Requirements

* R1: The timeline must present route span and event positions as a compact sequence band.
* R2: The selected event must be obvious without relying on a separate event-card list; if that strip remains as a fallback, it must center the selected card in the strip viewport.
* R3: The timeline must support keyboard and pointer selection.
* R4: The timeline must handle denser future routes without collapsing into clutter.
* R5: The timeline must support the current pre-1970 Birth of Hip-Hop context without making the component feel like a chronology board.

## Acceptance criteria

* AC1: The timeline reads as compact sequence context rather than a separate content panel.
* AC2: Event selection is clear and usable from the timeline, and any retained event-card strip keeps the selected card centered in view.
* AC3: Route span and chronology remain legible.
* AC4: The component remains subordinate to the map and event inspector in the first viewport.
* AC5: The design can accommodate denser future routes without becoming cluttered.

## Assumptions

* A1: The timeline continues to receive the shared selected-event state from the page shell.
* A2: The map remains the primary surface.

## Open questions

* Q1: Should the timeline keep the horizontal event-card strip at all, or should it be removed once density no longer requires it?
* Q2: Should the pre-1970 event be clamped, shown in a prehistory band, or called out in the header?
