# Implement Frontend Map From Spec

Use this prompt when building or changing the SoundAtlas SvelteKit frontend map experience from an approved spec.

This prompt is the frontend implementation entrypoint for the current workflow. If the repo has a matching frontend skill, use that skill's instructions and keep this prompt as the compatibility wrapper.

## Context to provide

* Approved spec revision path, for example `specs/<feature-slug>/rNN-<short-desc>.md`.
* Desired frontend behavior or component.
* Related backend endpoints or seed fields.
* Expected interaction:

  * route filter
  * timeline range
  * marker selection
  * Story Panel behavior
* Primary viewport target:

  * desktop
  * mobile
  * both
* Route selection model:

  * single-select
  * multi-select
* Surface type:

  * public-facing
  * admin-only
  * mixed
* Whether implementation is approved now or frontend planning only.

## Spec Gate

Before implementing, read the approved spec revision.

Implementation may proceed only when:

* An approved spec revision path is provided, or the change is explicitly marked as trivial.
* The spec has clear frontend-relevant requirements.
* The spec has testable frontend-relevant acceptance criteria.
* Blocking questions are resolved or intentionally deferred.

Do not implement behavior outside the spec.

If implementation reveals required behavior that is not described in the spec revision, draft a new revision first and stop for approval before continuing.

Map implementation work to spec requirements using requirement IDs such as `R1`, `R2`, and `R3`.

Verify completed work against acceptance criteria such as `AC1`, `AC2`, and `AC3`.

## Task

Implement frontend behavior using SvelteKit, TypeScript, and Leaflet.

Do not redefine the product behavior from the prompt. Treat the approved spec as the source of truth.

## Project constraints

* The map is the primary MVP surface.
* Use backend or seed-backed data, not unrelated mock data.
* Keep UI components small and domain-named, such as:

  * `MapView`
  * `Timeline`
  * `RouteFilter`
  * `StoryPanel`
* Ensure route colors, event time ranges, selected event state, and empty states are represented when required by the spec.
* Do not require real audio playback for MVP; use external media links only.
* Avoid layout overlap and make the first viewport usable.
* Keep the active route narrative and map visually dominant.
* Route filters should not overpower the exploration workflow.
* Do not commit changes unless explicitly requested.
* Do not commit secrets, API keys, local paths, generated media files, audio, or video.

## UX state rules

* Identify the central state owner for selected route and selected event before editing components.
* Keep map marker clicks, timeline interactions, route selection, and story navigation synchronized through the same selected event state.
* Default to the MVP route and a meaningful first event when appropriate and seed data exists.
* Make timeline controls interactive when the user is expected to explore event sequence, not only passive route ranges.
* If UI includes review or curation controls, confirm whether the current surface is admin-only.
* If review or curation controls stay visible on a public-facing surface, add an `@todo` for public gating.
* Track timeline density risk near the implementation when future routes with many events may require clustering or compact ticks.

## Process

1. Read the approved spec revision and identify frontend-relevant requirements and acceptance criteria.
2. Inspect the existing SvelteKit route, components, and state ownership before editing.
3. Inspect related backend response shapes or seed-backed data.
4. Define TypeScript types that mirror backend response shapes.
5. Build or update API client functions before wiring UI state.
6. Keep filtering and selection logic testable where possible.
7. Handle loading, empty, error, and selected states.
8. Verify Leaflet is only used in browser-safe code.
9. Check for Svelte warnings, including invalid self-closing non-void elements such as `<iframe />`.
10. If a `TODO.md` item is completed, update `TODO.md`.

## Frontend checks

Run the narrowest relevant frontend validation available.

Prefer:

```sh
npm run check
```

If a more targeted check exists, use it first.

If screenshot validation is expected but blocked, document the blocker clearly.

## Deliverables

Return:

```md
## Summary

- What frontend behavior changed.
- Which spec requirements were implemented.

## Requirement mapping

- R1: implemented in `<file path>`
- R2: implemented in `<file path>`
- R3: implemented in `<file path>`

## Interaction behavior

- Route selection:
- Timeline:
- Marker selection:
- Story Panel:
- Empty/loading/error states:

## Acceptance criteria verification

- AC1: Pass/Fail — evidence
- AC2: Pass/Fail — evidence
- AC3: Pass/Fail — evidence

## Tests/checks run

- `<command>` — Pass/Fail

## Files changed

- `<path>`: `<reason>`

## Spec updates

- None, or:
- `<spec path>`: `<what changed and why>`

## Risks/open questions

- `<risk or question>`

## Suggested commit message

- `feat(frontend): ...`
```
