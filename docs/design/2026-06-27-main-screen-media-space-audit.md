# Main Screen Media Space Audit - 2026-06-27

This audit uses `prompts/design-ux.md` and focuses on the main screen structure, space optimization, and how the layout should scale when richer media and image content is added.

It is based on source inspection and the current design baseline, not screenshots.

## Scope

- Primary surface: map-first exploration screen
- Main layout owner: `frontend/src/routes/+page.svelte`
- Relevant components:
  - `frontend/src/lib/components/NavigationDrawer.svelte`
  - `frontend/src/lib/components/MapView.svelte`
  - `frontend/src/lib/components/Timeline.svelte`
  - `frontend/src/lib/components/StoryPanel.svelte`
  - `frontend/src/lib/components/MediaEmbed.svelte`
- Related mockups:
  - `docs/design/main-screen-media-structure-mockups.md`
  - `docs/design/main-screen-event-inspector-story-tab.svg`
  - `docs/design/main-screen-event-inspector-media-tab.svg`

## Top Usability Issues

1. The right-side story panel will not scale well once image and media content grows. It already combines story, significance, connections, sources, and media links in one narrow scrolling column.

2. Media currently lacks a clear information architecture. `media_links` appear as simple links, while `image_links` are part of the review flow but are not yet represented as a public reading or browsing surface.

3. Map, timeline, story, and future media content will compete for first-screen attention unless the screen gets a stricter hierarchy.

4. The timeline is useful as sequence context, but it permanently consumes vertical space. If richer event media is added, the timeline should stay compact and avoid becoming another content feed.

5. Admin review actions and public exploration should remain separated. The navigation drawer can keep the admin media/image review queue, but it should not become the main public media browser.

## Top Visual Hierarchy Issues

The current hierarchy is approximately:

1. Header route context
2. Map
3. Timeline
4. Story panel
5. Drawer/admin review

For a media-rich version, the hierarchy should become:

1. Map and selected event location
2. Selected event inspector
3. Compact timeline/sequence context
4. Media and sources as secondary detail
5. Admin review as a separate overlay workflow

The largest risk is letting images and embeds appear inline everywhere. Media should be discoverable, but not louder than place, time, and event understanding.

## Gaps Between Implementation And Design Baseline

- The current design baseline says sources and media are secondary, but the current component structure has no scalable place for richer media.
- `StoryPanel` is still a general-purpose vertical detail column, not a structured event inspector.
- `MediaEmbed` exists, but embedding playable media directly into the story sidebar would consume too much space.
- `image_links` participate in the admin review queue, but the public-facing story layout does not yet define how images should appear.
- Mobile ordering will need reconsideration once story, media, sources, and route navigation all compete for a single column.

## Recommended Design Direction

Keep the current desktop shell, but change the right side from a free-scrolling story column into an **Event Inspector**.

Recommended inspector structure:

- Sticky selected-event header
- `Story` tab as the default view
- `Media` tab for images, embeds, and media links
- `Sources` tab for source URLs and citation-oriented details
- Compact connection section inside the story view
- Fixed-size media preview and thumbnail areas
- Full image/video inspection through an overlay, lightbox, or dedicated detail surface

The map should remain the dominant visual surface. Media should support the selected event, not replace the map as the primary interaction.

## Proposed First Redesign Pass

1. Rename or reshape the story surface conceptually as an event inspector.
2. Add inspector tabs for `Story`, `Media`, and `Sources`.
3. Keep story and significance visible by default.
4. Show media counts in the story view instead of rendering all media inline.
5. Render images and media in the media view using fixed aspect ratios.
6. Keep the timeline visually compact and subordinate to the map.
7. Keep admin review actions inside the navigation drawer and separate from public media browsing.
8. Update the design baseline after choosing the final inspector structure.

## Component Plan

### `+page.svelte`

Keep ownership of shared state:

- selected route
- selected event
- visible events
- review queue
- drawer state

The top-level screen should continue coordinating map, timeline, drawer, and inspector from one state model.

### `StoryPanel`

Refactor toward an event inspector role:

- sticky selected-event header
- internal tabs or segmented control
- story content as default
- media and sources as secondary views
- stable empty/error/loading states per section

### `MediaEmbed`

Do not render large embeds by default in the story view. Use this component only inside the media tab or a focused media detail surface.

### `NavigationDrawer`

Keep route switching and admin review actions here. If thumbnails are added to review items, use fixed dimensions and avoid turning the drawer into the public media gallery.

### `Timeline`

Keep it as sequence navigation. Avoid adding large cards, thumbnails, or media previews to the timeline.

## Space Rules

- The first viewport should remain map-first.
- The inspector should have fixed-width desktop behavior and internal scrolling.
- Media previews need fixed aspect ratios to avoid layout jumps.
- Rich media should be lazy-loaded or user-initiated.
- Long media lists should scroll inside the media tab.
- Empty and error states should use fixed-height messages rather than expanding the page.

## A11y Checklist

- Inspector tabs are keyboard reachable and expose selected state.
- Focus stays consistent when switching tabs.
- Media thumbnails have accessible labels.
- External media links clearly indicate external navigation.
- Embedded media does not autoplay.
- Focus styles remain visible in the drawer, timeline, and inspector.
- Error and empty states are readable without relying on color alone.

## Mockup References

See `docs/design/main-screen-media-structure-mockups.md` for the visual mockups that accompany this audit.
