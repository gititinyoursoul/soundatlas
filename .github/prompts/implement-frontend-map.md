# Implement Frontend Map

Use this prompt when building or changing the SoundAtlas SvelteKit frontend map experience.

Context to provide
- Desired UI behavior or component.
- Related backend endpoints or seed fields.
- Expected interaction: route filter, timeline range, marker selection, or Story Panel behavior.

Task
- Implement frontend behavior using SvelteKit, TypeScript, and Leaflet.

Project constraints
- The map is the primary MVP surface.
- Use backend or seed-backed data, not unrelated mock data.
- Keep UI components small and domain-named: `MapView`, `Timeline`, `RouteFilter`, `StoryPanel`.
- Ensure route colors, event time ranges, selected event state, and empty states are represented.
- Do not require real audio playback for MVP; use external media links only.
- Avoid layout overlap and make the first viewport usable.

Process
- Define TypeScript types that mirror backend response shapes.
- Build or update API client functions before wiring UI state.
- Keep filtering logic testable where possible.
- Handle loading, empty, error, and selected states.
- Verify Leaflet is only used in browser-safe code.
- Run the narrowest available frontend check or build if configured.

Deliverables
- Svelte components and API client updates.
- Notes on interaction behavior and empty/error states.
- Validation command run and outcome.
- Suggested commit message, usually `feat(frontend): ...`.
