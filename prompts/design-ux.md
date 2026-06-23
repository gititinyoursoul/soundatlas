# Design UX

Reusable prompts for UX and design work on SoundAtlas. These are working templates, not project documentation.

## Shared Context

Use this context at the top of UX/design prompts when the session does not already have enough project context:

```text
Act as a senior UX/product designer and frontend engineer for SoundAtlas.

Project context:
- SoundAtlas is an interactive music history app.
- MVP scope: New York 1965-1985.
- Vertical slice: Birth of Hip-Hop: Bronx 1970-1985.
- The map is the primary interface.
- Timeline, route filter, and story panel should share one central selection state.
- Use real seed data where possible; avoid mock-only UI.
- The visual tone should be dense, documentary, source-aware, and usable.

When reviewing or designing, focus on:
- Map-first exploration
- Place/time/story clarity
- Visual hierarchy
- Interaction flow
- Responsive behavior
- Source and media discoverability
- Small, reviewable implementation steps

Do not suggest a landing page unless explicitly requested.
Do not propose broad redesigns before auditing the current frontend.
```

## UX Audit

Use this before changing frontend code:

```text
Review the current SvelteKit frontend as a UX/product engineer.

Focus on the MVP: map-first exploration of New York 1965-1985, with the first vertical slice being Birth of Hip-Hop: Bronx 1970-1985.

Identify the biggest usability and visual design issues. Cover:
- Current layout structure
- Data flow and shared selection state
- Component boundaries
- UX friction
- Missing states
- Visual hierarchy and design inconsistencies

Do not make changes yet. Return:
- Top usability issues
- Top visual hierarchy issues
- Recommended design direction
- Proposed first redesign pass
- Files and components likely affected
```

## Main Screen Redesign Plan

Use this after the UX audit, before implementation:

```text
Design the main SoundAtlas exploration screen.

Constraints:
- SvelteKit + TypeScript
- Leaflet map is primary
- Use existing seed data
- Components should stay small and domain-named, such as MapView, Timeline, RouteFilter, and StoryPanel
- No mock-only UI
- Dense, documentary, usable MVP style
- The first screen should be the product experience, not a landing page

Primary workflow:
1. User selects the Birth of Hip-Hop route.
2. The map shows Bronx places relevant to the route.
3. The timeline shows the route event sequence from 1970 to 1985.
4. User selects an event from the map or timeline.
5. Map, timeline, and story panel update from the same central state.
6. User can inspect summary, significance, sources, and media links.

Give me a component/layout plan before coding. Include:
- Layout structure
- Interaction model
- Shared state model
- Responsive behavior
- Implementation passes
- Risks or open questions
```

## Screenshot Critique

Use this after running the app and capturing desktop or mobile screenshots:

```text
Critique this SoundAtlas screen like a senior product designer.

Focus on:
- Whether the map feels like the primary surface
- Place/time/story clarity
- Visual hierarchy
- Spacing and density
- Readability
- Affordances and interaction cues
- Source and media discoverability
- Responsive layout issues

Suggest specific changes, not general advice.
Prioritize the changes by user impact and implementation size.
```
