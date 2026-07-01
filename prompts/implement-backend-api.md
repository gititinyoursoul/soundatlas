# Implement Backend API From Plan Or Local Record

Use this prompt when implementing or changing the SoundAtlas FastAPI backend from an approved plan or local implementation plan record.

This prompt is the backend implementation entrypoint for the current workflow. If the repo has a matching backend skill, use that skill's instructions and keep this prompt as the compatibility wrapper.

## Context to provide

* Approved plan summary or local implementation plan record path, for example `plans/records/P-014-enrichment-query-input.md`.
* Endpoint or backend behavior to implement.
* Relevant seed data and expected API response shape.
* Error behavior and filtering requirements.
* Whether implementation is approved now or backend planning only.

## Implementation Gate

Before implementing, read the approved plan or local implementation plan record.

Implementation may proceed only when:

* An approved plan, provided local implementation plan record path, or clearly trivial request exists.
* Requirements are clear enough to implement.
* Acceptance criteria are testable enough to verify.
* Blocking questions are resolved or intentionally deferred.

Do not implement behavior outside the approved plan or local implementation plan record.

If implementation reveals required behavior outside the approved plan or local implementation plan record, stop for approval when the change affects product behavior or another high-risk boundary. For low-risk implementation detail, record the assumption and continue.

When a local plan record exists, map implementation work to requirement IDs and verify against acceptance criteria.

## Task

Implement backend behavior using Python, `uv`, FastAPI, and Pydantic.

Do not rewrite the product behavior from the prompt. Treat the approved plan or local implementation plan record as the source of truth.

## Project constraints

* Backend application code should live under `backend/app/`.
* Load MVP data from `data/seed/` until a database is introduced.
* Use Pydantic schemas for response models.
* Keep route, place, event, and connection field names aligned with seed data.
* Preserve documented seed contracts from `docs/data/seed-data-validation.md`.
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

1. Read the approved plan or local implementation plan record and identify backend-relevant requirements and acceptance criteria.
2. Inspect existing backend structure under `backend/app/`.
3. Inspect relevant seed data under `data/seed/`.
4. Check `docs/data/seed-data-validation.md` before changing seed-related behavior.
5. Define or update Pydantic schemas before endpoint handlers.
6. Add or update a seed repository or loader with explicit path handling.
7. Implement filtering for `from_year`, `to_year`, and `route_id` when required by the approved plan.
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
- Which approved plan requirements were implemented.

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

## Local plan record updates

- None, or:
- `<local plan record path>`: `<what changed and why>`

## Risks/open questions

- `<risk or question>`

## Suggested commit message

- `feat(backend): ...`
- Commit body footer: `Plan: P-###`

## Next step

- Review the verification report, then commit the backend change with the plan footer or run `prompts/write-tests.md` / `prompts/update-docs.md` if follow-up coverage or docs are needed.
```
