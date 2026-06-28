# Implement Backend API From Spec

Use this prompt when implementing or changing the SoundAtlas FastAPI backend from an approved spec.

This prompt is the backend implementation entrypoint for the current workflow. If the repo has a matching backend skill, use that skill's instructions and keep this prompt as the compatibility wrapper.

## Context to provide

* Approved spec revision path, for example `specs/<feature-slug>/rNN-<short-desc>.md`.
* Endpoint or backend behavior to implement.
* Relevant seed data and expected API response shape.
* Error behavior and filtering requirements.
* Whether implementation is approved now or backend planning only.

## Spec Gate

Before implementing, read the approved spec revision.

Implementation may proceed only when:

* An approved spec revision path is provided, or the change is explicitly marked as trivial.
* The spec has clear requirements.
* The spec has testable acceptance criteria.
* Blocking questions are resolved or intentionally deferred.

Do not implement behavior outside the spec.

If implementation reveals required behavior that is not described in the spec revision, draft a new revision first and stop for approval before continuing.

Map implementation work to spec requirements using requirement IDs such as `R1`, `R2`, and `R3`.

Verify completed work against acceptance criteria such as `AC1`, `AC2`, and `AC3`.

## Task

Implement backend behavior using Python, `uv`, FastAPI, and Pydantic.

Do not rewrite the product behavior from the prompt. Treat the approved spec as the source of truth.

## Project constraints

* Backend application code should live under `backend/app/`.
* Load MVP data from `data/seed/` until a database is introduced.
* Use Pydantic schemas for response models.
* Keep route, place, event, and connection field names aligned with seed data.
* Preserve documented seed contracts from `docs/seed-validation.md`.
* Do not introduce a database until explicitly requested.
* Do not commit changes unless explicitly requested.
* Do not commit secrets, API keys, local paths, generated media files, audio, or video.

## Expected MVP endpoints

* `GET /health`
* `GET /routes`
* `GET /events`
* `GET /events/{event_id}`
* `GET /places`
* `GET /connections`

## Process

1. Read the approved spec revision and identify backend-relevant requirements and acceptance criteria.
2. Inspect existing backend structure under `backend/app/`.
3. Inspect relevant seed data under `data/seed/`.
4. Check `docs/seed-validation.md` before changing seed-related behavior.
5. Define or update Pydantic schemas before endpoint handlers.
6. Add or update a seed repository or loader with explicit path handling.
7. Implement filtering for `from_year`, `to_year`, and `route_id` when required by the spec.
8. Define behavior for unknown IDs and empty results.
9. Add targeted tests for changed behavior.
10. Update docs or `TODO.md` only if workflow or completed TODOs change.

## Backend checks

Run the narrowest relevant backend validation available.

Prefer:

```sh
cd backend
uv run pytest
```

If tests are missing or blocked, state the blocker clearly.

## Verification report

Return:

```md
## Summary

- What backend behavior changed.
- Which spec requirements were implemented.

## Requirement mapping

- R1: implemented in `<file path>`
- R2: implemented in `<file path>`

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

- `feat(backend): ...`

## Next step

- Review the verification report, then commit the backend change or run `prompts/write-tests.md` / `prompts/update-docs.md` if follow-up coverage or docs are needed.
```
