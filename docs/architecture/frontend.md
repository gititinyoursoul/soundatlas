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

## Implementation constraints

Use established SvelteKit, TypeScript and Leaflet patterns. Identify the
central owner of selected route/event state; marker selection, timeline,
route selection, story navigation and related-event navigation must remain
synchronized through that owner. Preserve route colors, event ranges, selected
states and relevant loading, empty and error behavior within the approved
slice. Keep filtering, selection and derived state testable where practical.

Data-access changes require aligned TypeScript types and API-client behavior
before UI wiring. Preserve the existing visual design and responsive behavior
unless the approved Issue changes them. Leaflet must remain browser-safe and
retain its required global selectors. Check Svelte warnings, including invalid
self-closing non-void elements such as `<iframe />`.

### Styling and Tailwind migration

Tailwind CSS is the canonical application UI styling approach:

- New application UI styling uses Tailwind utilities, with no new
  component-specific legacy CSS.
- Existing component-scoped CSS may remain until migration. Full migration
  requires removing obsolete component-specific CSS.
- The tracked legacy-CSS baseline, including component CSS and approved global
  exceptions, may remain the same or decrease; it must not increase.
- `src/styles/app.css` is the global base-style exception. Third-party/library
  selector overrides belong only in `src/styles/library-overrides.css`.
  Neither exception permits new application component styling.
- Migrating every substantially touched component is a separate later policy
  phase unless an approved Issue explicitly requires it.

## Data boundary

The frontend consumes backend responses during local/API development and
generated static JSON assets for the public read-only deployment. The seed
files remain the editorial source of truth; the frontend does not replace them
with independently authored mock data.

Do not add local audio, video, images, generated media, secrets or API keys.
Media and review controls are admin-only unless the approved Issue explicitly
defines public-facing behavior and its gating.

## Validation and design evidence

`AGENTS.md` owns frontend validation commands, including release/Pages and CI
requirements. The [desktop UI guide](../design/desktop-ui-guide.md),
[current frontend design](../design/current-frontend-design.md) and
[UX workflow](../design/ux-workflow.md) own applicable rules, interaction
states, target references and proportionate desktop runtime/visual evidence
for non-trivial frontend/UX work. Mobile evidence is required only when mobile
behavior is affected; non-visual changes retain the Plan's inapplicability
reason. Missing required evidence or unresolved material UI-quality findings
prevent acceptance under those authorities and implementation review.

See [runtime data flow](data-flow.md), [current frontend design](../design/current-frontend-design.md), the [desktop UI guide](../design/desktop-ui-guide.md), and the [MVP concept](../mvp-concept.md).
