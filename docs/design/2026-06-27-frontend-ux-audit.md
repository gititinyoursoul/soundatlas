# Frontend UX Audit - 2026-06-27

This audit uses `prompts/design-ux.md` and reviews the current SvelteKit frontend without code changes. It is based on source inspection and seed data, not screenshots.

## Scope

- MVP: New York 1965-1985
- Vertical slice: Birth of Hip-Hop: Bronx 1970-1985
- Primary surface: map-first exploration with timeline, route filter, and story panel
- Frontend state owner: `frontend/src/routes/+page.svelte`

## Top Usability Issues

1. The map is technically primary, but not experientially primary yet. The first column stacks topbar, route context, route filter, then map, then timeline. On laptop screens, the route context and controls can make the map feel like one panel among many rather than the main exploration surface.

2. The default route workflow is strong. Selected route and selected event state are centralized in `+page.svelte`, and map, timeline, and story panel receive the same `selectedEventId`. This should be preserved.

3. The Birth of Hip-Hop route claims `1970-1985`, but its first event starts in `1967`. The timeline axis comes from the route years, while out-of-range event positions are visually clamped. This makes prehistory events hard to interpret.

4. Map marker selection works, but the map gives little narrative context by itself. Markers show hover tooltips and selected state, but there is no persistent selected-event label or compact map-side event context.

5. The route filter exposes all routes immediately. That supports expansion, but for the current vertical slice it competes with "Birth of Hip-Hop" as the first guided experience.

6. The public explorer and admin review surface are mixed. `MediaEmbed` still shows media review controls, with a TODO to gate them before a public explorer view.

## Top Visual Hierarchy Issues

1. The story panel has strong readable structure, but it can visually dominate because it is fixed up to `28rem` wide while the map column carries several stacked controls before the map.

2. The timeline duplicates selection affordances: round ticks plus horizontal event cards. This is useful but visually busy.

3. Route context uses warm emphasis and metadata chips, which makes it compete with selected event details. Once an event is selected, current event context should probably win over route metadata.

4. Mobile behavior collapses the layout to one column, but there is no explicit mobile ordering strategy for map, timeline, and story panel. The exploration flow may become long-scroll rather than coordinated.

## Recommended Design Direction

Use **Research Atlas with selected Story Explorer behavior**.

This means:

- Map remains the main surface.
- The route gives orientation but does not overpower event exploration.
- Timeline acts as sequence navigation, not decoration.
- Story panel explains the selected event and sources.
- Admin/media review controls stay visible only until gated.

## Proposed First Redesign Pass

Make the first viewport more map-first without changing data or API behavior.

1. Compress the topbar and route context into a tighter command/header band.
2. Keep `RouteFilter` visible, but make it less visually dominant than map and selected event.
3. Add a selected-event summary overlay or compact caption on the map.
4. Make the timeline read as route sequence navigation, with clearer selected-event emphasis.
5. Preserve the existing central state model in `+page.svelte`.
6. Do not touch backend or seed data yet, except to separately decide how to represent pre-1970 hip-hop prehistory.

## Likely Files Affected

- `frontend/src/routes/+page.svelte`: layout, state-derived presentation, responsive order
- `frontend/src/lib/components/MapView.svelte`: selected event overlay or legend behavior
- `frontend/src/lib/components/Timeline.svelte`: sequence clarity and out-of-range event handling
- `frontend/src/lib/components/RouteFilter.svelte`: visual weight
- `frontend/src/lib/components/StoryPanel.svelte`: event hierarchy and public/admin separation later
- `data/seed/routes.json` or route documentation later: 1967 prehistory vs 1970 route-range decision

## Suggested Next Step

Use `prompts/design-ux.md` Main Screen Redesign Plan to plan the first small UX pass from this audit. Then use `prompts/plan-feature.md` to narrow it into one reviewable implementation change.
