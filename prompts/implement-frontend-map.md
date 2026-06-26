# Implement Frontend Map

Use this prompt when building or changing the SoundAtlas SvelteKit frontend map experience.

Context to provide
- Desired UI behavior or component.
- Related backend endpoints or seed fields.
- Expected interaction: route filter, timeline range, marker selection, or Story Panel behavior.
- Primary viewport target: desktop, mobile, or both.
- Route selection model: single-select or multi-select.
- Whether the surface is public-facing, admin-only, or mixed.

Task
- Implement frontend behavior using SvelteKit, TypeScript, and Leaflet.

Project constraints
- The map is the primary MVP surface.
- Use backend or seed-backed data, not unrelated mock data.
- Keep UI components small and domain-named: `MapView`, `Timeline`, `RouteFilter`, `StoryPanel`.
- Ensure route colors, event time ranges, selected event state, and empty states are represented.
- Do not require real audio playback for MVP; use external media links only.
- Avoid layout overlap and make the first viewport usable.
- Keep the active route narrative and map visually dominant; route filters should not overpower the exploration workflow.

UX state rules
- Identify the central state owner for selected route and selected event before editing components.
- Keep map marker clicks, timeline interactions, route selection, and story navigation synchronized through the same selected event state.
- Default to the MVP route and a meaningful first event when appropriate and seed data exists.
- Make timeline controls interactive when the user is expected to explore event sequence, not only passive route ranges.
- If UI includes review or curation controls, confirm whether the current surface is admin-only; if kept visible, add an `@todo` for public gating.
- Track timeline density risk near the implementation when future routes with many events may require clustering or compact ticks.

Process
- Define TypeScript types that mirror backend response shapes.
- Build or update API client functions before wiring UI state.
- Keep filtering logic testable where possible.
- Handle loading, empty, error, and selected states.
- Verify Leaflet is only used in browser-safe code.
- Check for Svelte warnings, including invalid self-closing non-void elements such as `<iframe />`.
- If a TODO item is completed, update `TODO.md`.
- If screenshot validation is expected but blocked, document the blocker.
- Run the narrowest available frontend check or build if configured.

Deliverables
- Svelte components and API client updates.
- Notes on interaction behavior and empty/error states.
- Validation command run and outcome.
- Suggested commit message, usually `feat(frontend): ...`.
