# Spec: Event Inspector Connected Navigation And Stable Header

## Status

Implemented

## Revision

r03

## Supersedes

r02-more-inspector-width.md

## Request

Turn the event-inspector critique slices into an implementation plan and then implement them: connections should be clickable and open the connected event, the redundant "Selected event" label above the header should be removed, and the previous/next navigation controls should not move when switching events.

## Goal

Make the event inspector read as a stable research surface with actionable narrative links between events.

## Non-goals

* NG1: Redesign the media tab or sources tab.
* NG2: Change backend endpoints or seed data shape.
* NG3: Redesign the timeline or map beyond keeping them in sync with inspector-driven navigation.

## Change type

* Type: frontend-only

## Scope

* Routes/pages: `frontend/src/routes/+page.svelte`
* Components: `frontend/src/lib/components/StoryPanel.svelte`
* Backend endpoints: None
* Seed files: None
* Enrichment files: None
* Docs/TODOs: `docs/design/current-frontend-design.md`

## Requirements

* R1: The story inspector must render connections as clickable connected-event rows instead of passive bullet text.
* R2: Clicking a connection row must open the connected event and keep inspector, map, and timeline selection in sync.
* R3: If a connection targets an event on another route, the route and event selection must change together.
* R4: The redundant "Selected event" label above the event title must be removed.
* R5: Previous/next navigation controls must keep a stable layout position while switching events.
* R6: Connection rows must expose the relationship type in human-readable form.
* R7: The story tab must present summary and significance as one reading flow instead of two equal cards.
* R8: Previous/next controls must expose the adjacent event title on hover and keyboard focus without expanding the header layout.
* R9: Source links must show readable source labels instead of generic numbered labels.
* R10: Public media labels must be framed for exploration and must not expose review-status language.
* R11: Media marked as external-only must render as an external action instead of an embedded player.
* R12: External-only media must use a dedicated preview state distinct from empty or missing media.
* R13: Sources must move into the Story tab as compact support links, and the standalone Sources tab must become a Related tab for connections.

## Acceptance criteria

* AC1: The story tab shows compact connected-event rows with title, secondary metadata, and connection summary.
* AC2: Clicking a connected-event row updates the selected event across the shared page state.
* AC3: Cross-route connections switch to the destination route and event in one interaction.
* AC4: The inspector header no longer shows "Selected event".
* AC5: Previous/next controls stay visually anchored while different events with different title lengths are selected.
* AC6: Each connection row shows both direction and relationship type.
* AC7: The summary reads as the primary story body and significance reads as a subordinate editorial note.
* AC8: Hovering or focusing a previous/next control shows only the adjacent event title.
* AC9: Source links use recognizable source names or cleaned hostnames.
* AC10: The media list is headed "Media to explore" and media subtitles do not include review status.
* AC11: External-only YouTube media shows an "Open on YouTube" action and no iframe.
* AC12: External-only media shows a provider cue, title, subtitle, and external-open action in the preview area.
* AC13: The tab row reads Story, Media, Related; Story contains compact source links; Related contains connection rows.

## Assumptions

* A1: Page-level shared selection state in `+page.svelte` remains the single source of truth.
* A2: The current tab model stays in place for this refinement.
* A3: Compact rows are preferred over mini event cards for the connections section.

## Open questions

* Q1: None.

## Blocking questions

* BQ1: None.

## UX states

* User action: User clicks a connection row, previous/next button, map marker, or timeline event.
* Visible state: The inspector shows a compact title/meta header, stable previous/next controls, and connected-event rows in the story tab.
* Loading state: Existing route-event loading state remains unchanged.
* Empty state: Existing empty-state copy remains unchanged when no event is selected or no connections exist.
* Error state: Existing error-state copy remains unchanged.
* Selected state: The selected event remains synchronized across story inspector, map, and timeline.
* Keyboard/accessibility considerations: Connected-event rows must remain button-based and keyboard reachable.

## Implementation plan

1. Enrich selected connections in page state with connected event, place, route, and direction metadata.
   * Satisfies: R1, R2, R3
   * Files likely affected: `frontend/src/routes/+page.svelte`, `frontend/src/lib/types/soundatlas.ts`

2. Rework the inspector header into a compact title/meta block and a stable navigation block.
   * Satisfies: R4, R5
   * Files likely affected: `frontend/src/lib/components/StoryPanel.svelte`

3. Replace passive connection bullets with compact connected-event rows that use the central navigation callback.
   * Satisfies: R1, R2, R3
   * Files likely affected: `frontend/src/lib/components/StoryPanel.svelte`, `frontend/src/routes/+page.svelte`

4. Update frontend design documentation to reflect the inspector's new connected-event navigation behavior.
   * Satisfies: R1, R5
   * Files likely affected: `docs/design/current-frontend-design.md`

5. Add human-readable relationship type labels to the compact connection rows.
   * Satisfies: R6
   * Files likely affected: `frontend/src/lib/components/StoryPanel.svelte`

6. Rework the story tab hierarchy so summary and significance share one reading block while connections remain a distinct exploration section.
   * Satisfies: R7
   * Files likely affected: `frontend/src/lib/components/StoryPanel.svelte`

7. Add hover/focus tooltips to previous/next controls using adjacent event titles.
   * Satisfies: R8
   * Files likely affected: `frontend/src/lib/components/StoryPanel.svelte`

8. Format source URLs into readable labels while keeping links external and traceable.
   * Satisfies: R9
   * Files likely affected: `frontend/src/lib/components/StoryPanel.svelte`

9. Reframe media labels for public exploration and remove review-status copy from the inspector media tab.
   * Satisfies: R10
   * Files likely affected: `frontend/src/lib/components/StoryPanel.svelte`

10. Respect media playback mode so external-only YouTube links do not attempt to render as embeds.
   * Satisfies: R11
   * Files likely affected: `data/seed/events.json`, `frontend/src/lib/components/StoryPanel.svelte`, `frontend/src/lib/components/MediaEmbed.svelte`, `frontend/src/lib/types/soundatlas.ts`, `backend/app/schemas.py`

11. Add a dedicated external media preview state so external-only items remain part of media exploration.
   * Satisfies: R12
   * Files likely affected: `frontend/src/lib/components/StoryPanel.svelte`

12. Move sources into Story and replace the Sources tab with Related connections.
   * Satisfies: R13
   * Files likely affected: `frontend/src/lib/components/StoryPanel.svelte`, `docs/design/current-frontend-design.md`

## Validation plan

* AC1:

  * Check: Story tab renders compact connected-event rows rather than summary bullets.
  * Command: `npm run check`
* AC2:

  * Check: Inspector click targets compile against shared page state without prop mismatch.
  * Command: `npm run check`
* AC3:

  * Check: Cross-route connection handling is wired through route-aware navigation.
  * Command: `npm run check`
* AC4:

  * Check: Header markup no longer includes the eyebrow label.
  * Command: `npm run check`
* AC5:

  * Check: Navigation controls live in a dedicated stable layout block.
  * Command: `npm run check`
* AC6:

  * Check: Connection rows show direction and humanized relationship type.
  * Command: `npm run check`
* AC7:

  * Check: Story tab shows one reading block with a subordinate significance note.
  * Command: `npm run check`
* AC8:

  * Check: Previous/next tooltip content is sourced from the adjacent event title only.
  * Command: `npm run check`
* AC9:

  * Check: Sources tab no longer renders generic `Source 1` labels.
  * Command: `npm run check`
* AC10:

  * Check: Media tab uses exploratory copy and public subtitles omit review state.
  * Command: `npm run check`
* AC11:

  * Check: External-only media is filtered out of embedded playback and gets an external-open action.
  * Command: `npm run check`, `cd backend && uv run pytest`
* AC12:

  * Check: External-only media does not reuse the generic placeholder visual state.
  * Command: `npm run check`
* AC13:

  * Check: Sources are inline in Story and connections render under Related.
  * Command: `npm run check`

## Suggested validation commands

```sh
npm run check
```

## Risks

* Risk: Cross-route connection clicks could fall out of sync if future selection logic splits route and event ownership again.

## Review notes

Suggested file groups for review:

* Spec/docs: `specs/event-inspector/r03-connected-event-navigation-and-stable-header.md`, `docs/design/current-frontend-design.md`
* Backend: None
* Frontend: `frontend/src/routes/+page.svelte`, `frontend/src/lib/components/StoryPanel.svelte`, `frontend/src/lib/types/soundatlas.ts`
* Data/seed: None
* Tests: Typecheck only in this slice

## Suggested commit grouping

* `feat(frontend): refine event inspector connections`
* `docs(spec): record inspector connection navigation`

## Verification report

### Requirement mapping

* R1: implemented in `frontend/src/routes/+page.svelte`, `frontend/src/lib/components/StoryPanel.svelte`
* R2: implemented in `frontend/src/routes/+page.svelte`, `frontend/src/lib/components/StoryPanel.svelte`
* R3: implemented in `frontend/src/routes/+page.svelte`
* R4: implemented in `frontend/src/lib/components/StoryPanel.svelte`
* R5: implemented in `frontend/src/lib/components/StoryPanel.svelte`
* R6: implemented in `frontend/src/lib/components/StoryPanel.svelte`
* R7: implemented in `frontend/src/lib/components/StoryPanel.svelte`
* R8: implemented in `frontend/src/lib/components/StoryPanel.svelte`
* R9: implemented in `frontend/src/lib/components/StoryPanel.svelte`
* R10: implemented in `frontend/src/lib/components/StoryPanel.svelte`
* R11: implemented in `data/seed/events.json`, `frontend/src/lib/components/StoryPanel.svelte`, `frontend/src/lib/components/MediaEmbed.svelte`, `frontend/src/lib/types/soundatlas.ts`, `backend/app/schemas.py`
* R12: implemented in `frontend/src/lib/components/StoryPanel.svelte`
* R13: implemented in `frontend/src/lib/components/StoryPanel.svelte`

### Acceptance criteria verification

* AC1: Pass — compact connected-event rows replace the previous bullet list in `StoryPanel.svelte`
* AC2: Pass — connection rows call the shared page navigation callback with target event ID
* AC3: Pass — navigation callback accepts optional route ID and updates route before event selection
* AC4: Pass — the eyebrow label is removed from the header markup
* AC5: Pass — previous/next controls now live in a dedicated header grid block
* AC6: Pass — compact rows show direction and humanized relationship type
* AC7: Pass — story summary and significance now share one reading block
* AC8: Pass — previous/next controls expose adjacent event titles via hover/focus tooltips
* AC9: Pass — source links render readable source labels derived from URL hosts
* AC10: Pass — media tab copy is exploratory and public subtitles omit review status
* AC11: Pass — external-only media opens on YouTube instead of rendering an iframe
* AC12: Pass — external-only media has a dedicated preview state with provider cue and external action
* AC13: Pass — sources are inline in Story and related-event rows live in the Related tab

### Tests/checks run

* `npm run check` — Pass

### Files changed

* `specs/event-inspector/r03-connected-event-navigation-and-stable-header.md`: records the implemented inspector refinement

### Spec updates during implementation

* None
