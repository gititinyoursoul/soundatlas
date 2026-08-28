# Frontend Architecture

The SoundAtlas frontend is a SvelteKit and TypeScript application with Leaflet
as the MVP map layer. It renders curated/API-backed data and keeps explorer
interactions synchronized through shared route and event state.

## Responsibilities

- Render the map as the primary exploration surface.
- Provide timeline, route selection, navigation, and story-panel views.
- Load and display routes, places, events, connections, and media metadata.
- Coordinate selected route and selected event state across map, timeline, and
  story navigation.
- Present loading, empty, error, and review states where the approved product
  behavior requires them.

## Current structure

```text
frontend/
  src/
    lib/
      api/
      components/
        MapView.svelte
        Timeline.svelte
        RouteFilter.svelte
        StoryPanel.svelte
      types/
    routes/
      +page.svelte
```

Components should remain small and domain-named. Leaflet integration must stay
browser-safe, and map markers, timeline interactions, route selection, and
story navigation must use synchronized state rather than separate mock data.

## Data boundary

The frontend consumes backend responses during local/API development and
generated static JSON assets for the public read-only deployment. The seed
files remain the editorial source of truth; the frontend does not replace them
with independently authored mock data.

See [runtime data flow](data-flow.md), [current frontend design](../design/current-frontend-design.md), the [desktop UI guide](../design/desktop-ui-guide.md), and the [MVP concept](../mvp-concept.md).
