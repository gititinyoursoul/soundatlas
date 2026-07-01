# Implement Frontend Map From Plan Or Local Record

Use this prompt when building or changing the SoundAtlas SvelteKit frontend map experience from an approved plan or local implementation plan record.

This prompt is the frontend implementation entrypoint for the current workflow. If the repo has a matching frontend skill, use that skill's instructions and keep this prompt as the compatibility wrapper.

## Context to provide

* Approved plan summary or local implementation plan record path, for example `plans/records/P-014-enrichment-query-input.md`.
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

## Implementation Gate

Before implementing, read the approved plan or local implementation plan record.

Implementation may proceed only when:

* An approved plan, provided local implementation plan record path, or clearly trivial request exists.
* The requirements are clear enough to implement.
* Acceptance criteria are testable enough to verify.
* Blocking questions are resolved or intentionally deferred.

Do not implement behavior outside the approved plan or local implementation plan record.

If implementation reveals required behavior outside the approved plan or local implementation plan record, stop for approval when the change affects product behavior or another high-risk boundary. For low-risk implementation detail, record the assumption and continue.

When a local plan record exists, map implementation work to requirement IDs and verify against acceptance criteria.

## Task

Implement frontend behavior using SvelteKit, TypeScript, and Leaflet.

Do not redefine the product behavior from the prompt. Treat the approved plan or local implementation plan record as the source of truth.

## Project constraints

* The map is the primary MVP surface.
* Use backend or seed-backed data, not unrelated mock data.
* Keep UI components small and domain-named, such as:

  * `MapView`
  * `Timeline`
  * `RouteFilter`
  * `StoryPanel`
* Ensure route colors, event time ranges, selected event state, and empty states are represented when required by the approved plan.
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

1. Read the approved plan or local implementation plan record and identify frontend-relevant requirements and acceptance criteria.
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
- Which approved plan requirements were implemented.

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

## Local plan record updates

- None, or:
- `<local plan record path>`: `<what changed and why>`

## Risks/open questions

- `<risk or question>`

## Suggested commit message

- `feat(frontend): ...`
- Commit body footer: `Plan: P-###`

## Next step

- Review the verification report, then commit the frontend change with the plan footer or run `prompts/write-tests.md` / `prompts/update-docs.md` if follow-up coverage or docs are needed.
```
