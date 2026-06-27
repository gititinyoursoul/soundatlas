# Event Inspector Spec - 2026-06-27

This specification defines the event inspector for the main SoundAtlas screen. It turns the right-side story surface into a tabbed inspector with `Story`, `Media`, and `Sources` views while keeping the map primary and the timeline compact.

It is based on `prompts/plan-feature.md`, the main-screen media space audit, and the current frontend design baseline.

## Change Classification

- Frontend UX change
- Cross-cutting with docs updates only
- No backend or seed schema changes required

## Summary

The current story panel is a single scrolling detail column. That works for a text-first slice, but it does not scale well once image previews, media embeds, and citation material compete for the same space.

The new event inspector keeps the selected event details in one place, but separates them into three focused views:

- `Story`: the default reading view for narrative, significance, and connections
- `Media`: a preview surface for image links and playable media links
- `Sources`: a citation-oriented list of source URLs

The map remains the primary interaction surface. The timeline stays visible as compact sequence context. Admin review actions remain separate from public browsing.

## Assumptions

- Existing event data already contains the fields needed for this layout: `summary`, `significance`, `connections`, `source_urls`, `media_links`, and `image_links`.
- The inspector is a frontend-only structural change.
- Public browsing should not expose admin review controls by default.
- The main shell and shared selection state stay owned by `frontend/src/routes/+page.svelte`.

## Open Questions

- Should the inspector remember the last selected tab per event, or always reset to `Story` when selection changes?
- Should `Media` prioritize image previews or playable media when both exist?
- Should the inspector use the same tab layout on mobile, or collapse to a different control pattern at narrow widths?
- Should sources and media counts appear only in the inspector header, or also in the story body as context?

## User Action

The primary action is selecting an event from the map, timeline, or navigation controls and then inspecting that event through the right-side panel.

The user should be able to:

- read the story and significance without leaving the selected event
- switch to media previews without losing the event context
- check citations separately from the media gallery
- navigate to the previous or next event from within the inspector

## Screen Structure

The main screen should remain organized as:

1. Map
2. Timeline
3. Event inspector
4. Navigation drawer

The inspector itself should be organized as:

1. Sticky selected-event header
2. Tab list
3. Tab content
4. Internal scrolling only inside the panel body

## Layout Rules

- The map remains the visual anchor for the first viewport.
- The inspector should have a fixed desktop width and internal scrolling.
- The tab header should remain visible while the content scrolls.
- Media previews should use fixed aspect ratios to prevent layout jumps.
- Long source lists should scroll inside the Sources tab rather than expanding the page.
- The timeline should stay compact and visually subordinate to the map.

## Tab Behavior

### Story

The Story tab is the default state.

It should show:

- event title
- event year or year range
- place
- route context
- summary
- significance
- a short connection list

The Story tab should feel like a reading view, not a dashboard.

### Media

The Media tab is a browsing and preview surface.

It should show:

- one featured preview at a time
- image thumbnails with fixed dimensions
- playable media when an embed is available
- a fallback external link when a playable embed is not available

Media should support the selected event, not replace the map as the main surface.

### Sources

The Sources tab is a citation surface.

It should show:

- source URLs as external links
- a short note about traceability and public browsing

Sources should be separated from media so citations do not compete with previews.

## Component Roles

### `frontend/src/lib/components/StoryPanel.svelte`

Refactor this component into the event inspector shell.

Responsibilities:

- render the sticky header
- manage tab state
- render story, media, and sources panels
- show previous/next navigation
- use existing event data without inventing new fields

### `frontend/src/lib/components/MediaEmbed.svelte`

Keep this component for playable media embeds, but make admin review actions optional so the public inspector does not expose them.

### `frontend/src/routes/+page.svelte`

Keep shared data state and event selection in the page shell.

The page should continue to own:

- route selection
- selected event
- visible events
- connections
- loading and error state
- navigation drawer state

### `frontend/src/lib/components/Timeline.svelte`

Keep it as sequence navigation.

Do not add media previews or rich cards to the timeline.

### `frontend/src/lib/components/NavigationDrawer.svelte`

Keep admin review actions and route switching here.

The drawer should remain separate from the public media browsing experience.

## Data Usage

The inspector should rely on the current event model:

- `summary`
- `significance`
- `source_urls`
- `media_links`
- `image_links`
- `connections`

No new schema fields are required for the first pass.

## Accessibility

- Tabs must be keyboard reachable.
- Active tab state must be exposed with `aria-selected`.
- Tab panels must be properly associated with their tabs.
- External links must clearly open off-site.
- Media embeds must not autoplay.
- Empty and error states must be readable without relying on color alone.

## Acceptance Criteria

- The right-side panel reads as an event inspector rather than a generic story column.
- The Story tab presents the core narrative and significance clearly.
- The Media tab presents image and media previews in fixed-size layouts.
- The Sources tab presents citations separately from the media gallery.
- The map remains the dominant first-screen surface.
- The timeline remains compact and subordinate to the map.
- Public browsing does not expose admin review controls.

## Related Documents

- `docs/design/2026-06-27-main-screen-media-space-audit.md`
- `docs/design/main-screen-media-structure-mockups.md`
- `docs/design/current-frontend-design.md`
- `prompts/plan-feature.md`
