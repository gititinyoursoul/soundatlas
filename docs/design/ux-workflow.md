# UX and Design Workflow with GPT

This note describes a practical GPT-assisted workflow for improving the SoundAtlas UX and visual design. The goal is to use GPT as a product and design partner for small, inspectable iterations, not as a vague "make it pretty" generator.

## Product Frame

SoundAtlas should answer one core MVP question first:

> How should a user explore Birth of Hip-Hop: Bronx 1970-1985 through place, time, and story?

The first screen should be the actual exploration surface, not a landing page. For the MVP, the primary interface is:

- Map
- Timeline
- Route filter
- Story panel

The design should make music history understandable across three axes:

- Place: map, places, neighborhoods, venues, and movement
- Time: event years, periods, and sequence
- Sound and culture: events, routes, connections, sources, and media links

## Recommended Workflow

### 1. Audit the Current App

Start by asking GPT or Codex to inspect the frontend without changing code.

Useful prompt:

```text
Review the current SvelteKit frontend as a UX/product engineer.
Focus on the MVP: map-first exploration of New York 1965-1985.
Identify the biggest usability and visual design issues.
Do not make changes yet.
```

The audit should cover:

- Current layout structure
- Data flow and shared selection state
- Component boundaries
- UX friction
- Missing states
- Visual hierarchy and design inconsistencies

### 2. Choose a Design Direction

Before coding, ask for a small set of concrete design directions. Avoid generic style words.

Useful prompt:

```text
Propose 3 UX/design directions for SoundAtlas.
Each should describe layout, interaction model, visual tone, information density,
and tradeoffs. Keep them realistic for an MVP.
```

Possible directions:

- Research Atlas: dense, map-first, documentary, source-aware
- Story Explorer: guided narrative route with map and timeline support
- Cultural Network: emphasizes relationships between events, places, artists, scenes, and media

For the current MVP, the safest default is probably Research Atlas with selected Story Explorer behaviors.

### 3. Work on One Screen and One Workflow

Do not redesign the whole app at once. Start with the main exploration view.

Primary workflow:

1. User selects the "Birth of Hip-Hop" route.
2. The map shows Bronx places relevant to the route.
3. The timeline shows the route's event sequence from 1970 to 1985.
4. User selects an event from the map or timeline.
5. Map, timeline, and story panel update from the same central state.
6. User can inspect summary, significance, sources, and media links.

### 4. Ask for a Concrete UI Plan

Before implementation, ask GPT for a layout and component plan that respects the existing stack.

Useful prompt:

```text
Design the main SoundAtlas exploration screen.
Constraints:
- SvelteKit + TypeScript
- Leaflet map is primary
- Use existing seed data
- Components should stay small: MapView, Timeline, RouteFilter, StoryPanel
- No mock-only UI
- Dense, documentary, usable MVP style
Give me a component/layout plan before coding.
```

### 5. Implement in Small Passes

Recommended implementation order:

1. Layout shell: map, side panel, bottom timeline
2. Shared selection state: selected route, event, place, and year range
3. Map marker states and interactions
4. Timeline interactions
5. Story panel content and hierarchy
6. Empty, loading, and error states
7. Responsive layout

Each pass should remain reviewable and should use the existing seed data rather than mock-only data.

### 6. Critique with Screenshots

After a visual pass, run the app and use screenshots for critique.

Useful prompt:

```text
Critique this screen like a senior product designer.
Focus on hierarchy, spacing, affordances, readability, and whether the map feels primary.
Suggest specific changes, not general advice.
```

Repeat in small loops: implement, screenshot, critique, adjust.

## Design Checklist

Use this checklist for each UX change:

- Can the user immediately tell this is about music history in place and time?
- Is the map clearly the main surface?
- Does selecting a place or event update map, timeline, and story together?
- Does the timeline clarify sequence rather than just decorate the page?
- Are source links visible but not dominant?
- Does the UI work with the real seed data?
- Are empty, loading, and error states handled?
- Is the app usable on laptop-size screens first?
- Does the responsive version preserve the exploration workflow?

## Technical Validation

When frontend code changes, run:

```bash
npm run check
```

For larger visual or layout changes, also run:

```bash
npm run build
```

When possible, inspect the running app in desktop and mobile viewports before considering a UX pass complete.

## Immediate Next Step

The next useful step is a no-code UX audit of the current frontend. That audit should produce:

- Top usability issues
- Top visual hierarchy issues
- Recommended design direction
- Proposed first redesign pass
- Files and components likely affected

