# Plan Feature

Use this prompt before implementing a new SoundAtlas feature, UX change, data workflow, or cross-cutting change.

## Context To Provide

- Feature or problem statement.
- User value and primary user action.
- Target area:
  - `frontend`
  - `backend`
  - `data/seed`
  - `data/enrichment`
  - `docs`
  - cross-cutting
- Related route, event, or workflow, if any.
- Relevant docs:
  - `README.md`
  - `TODO.md`
  - `AGENTS.md`
  - `docs/seed-validation.md`
  - `docs/media-retrieval/workflow-commands.md`
  - `docs/media-retrieval/youtube-mvp-workflow.md`
- Constraints and non-goals.
- Whether implementation or planning-only is requested.

## Task

Produce a practical implementation plan. Do not write code unless explicitly asked.

If the input is incomplete, do not stop immediately. State reasonable assumptions, list open questions, and produce a plan that can be refined. Only block when missing information would make implementation unsafe, destructive, or likely to violate the project data model.

## Project Constraints

- Keep changes small, reviewable, and MVP-oriented.
- Current product scope is New York 1965-1985 with curated routes, events, places, connections, and external media links.
- Use existing project conventions in `AGENTS.md`.
- Prefer data-driven implementation from `data/seed/` over hardcoded UI mock data.
- Preserve seed file shapes documented in `docs/seed-validation.md`.
- Keep generated media links as `review_status: "draft"` until manually reviewed.
- Do not store audio or video files in the repository.
- Do not commit secrets, API keys, local paths, or generated media files.
- Do not commit changes unless explicitly requested.

## Technical Context

- Frontend: SvelteKit, TypeScript, Leaflet.
- Backend: Python, `uv`, FastAPI, Pydantic.
- MVP data: curated JSON files under `data/seed/`.
- Media retrieval: YouTube-only MVP using `data/enrichment/`.
- Media workflow commands are documented in `docs/media-retrieval/workflow-commands.md`.

## Planning Rules

- First classify the change:
  - frontend-only
  - backend-only
  - seed-data-only
  - enrichment workflow
  - documentation-only
  - cross-cutting
- For cross-cutting changes, plan in this order:
  1. Data/schema impact
  2. Backend/API impact
  3. Frontend state impact
  4. UX/component impact
  5. Tests/checks
  6. Documentation/TODO updates
- For UX changes, explicitly define:
  - user action
  - visible state
  - loading state
  - empty state
  - error state
  - keyboard/accessibility considerations where relevant
- For backend changes, define:
  - affected endpoints
  - schemas
  - seed repository behavior
  - error behavior
  - tests
- For frontend changes, define:
  - affected components
  - shared state changes
  - API/client changes
  - map/timeline/story panel behavior
  - `npm run check` expectation
- For media retrieval changes, define:
  - request-plan impact
  - normalized result impact
  - merge behavior
  - review boundary
  - whether `data/seed/events.json` should change

## Handling Incomplete Input

- State assumptions explicitly before the plan.
- Separate assumptions from open questions.
- Continue with a conservative plan when assumptions are safe.
- Keep risky or irreversible steps behind confirmation.
- Prefer planning small checkpoints over designing a large speculative solution.

Example:

```md
## Assumptions

- This is a frontend-only change.
- Existing API responses stay unchanged.
- The feature should work with current `data/seed/events.json`.
- No new route or media enrichment data is required.

## Open Questions

- Should the behavior apply to all routes or only one route?
- Should mobile behavior differ from desktop?
```

## Deliverables

Return:

1. A short summary of the intended change.
2. A numbered implementation plan with 5-9 reviewable steps.
3. Acceptance criteria.
4. Validation commands.
5. Risks or open questions.
6. Suggested file groups for review.
7. Suggested commit grouping and Conventional Commit messages.

## Output Rules

- Be concrete.
- Avoid generic filler.
- Prefer explicit file paths.
- Do not invent APIs, schema fields, or data.
- If the request is ambiguous, state assumptions before the plan.
