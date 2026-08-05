---
name: soundatlas-backend-implementation
description: Implement SoundAtlas Python and FastAPI backend changes from approved GitHub Issues, including Pydantic schemas, seed-backed loading, endpoint behavior, filtering, validation, tests, and backend reporting.
---

# SoundAtlas Backend Implementation

Use this skill for backend implementation work from an approved SoundAtlas
GitHub Issue. The approved Issue is the primary product and scope authority.

## Required context

Read these before editing:

- `AGENTS.md`
- `docs/github-issue-workflow.md`
- `docs/workflow-registry.md`
- `docs/data/seed-data-validation.md` when seed-backed behavior is involved
- the approved GitHub Issue, including any recorded Grill-Me findings or
  decisions and its `## Plan Update` or `## Detailed Plan Update` when risk
  flags are present. A standalone `## Grill-Me Review` is used when the result
  is material or explicitly standalone; a clean check may be inline in the
  relevant action comment.

Optional context may clarify the Issue without overriding it:

- endpoint or backend behavior in scope
- relevant seed files and expected response shapes
- filtering, unknown-ID, and empty-result behavior
- validation commands or runtime constraints

## Implementation gate

Implement only when the user explicitly requests implementation of the approved
Issue, for example `implement issue #<number>`, or when the work is clearly
trivial and low-risk.

For Issue-based work with security, credentials, infrastructure, networking,
workflow, UX, editorial, cross-cutting, user-visible, vague, or materially
ambiguous risk flags, require both:

- a recorded Grill-Me result with required material decisions confirmed;
- a `## Plan Update` or `## Detailed Plan Update` that incorporates them.

Use a standalone `## Grill-Me Review` for material findings, decisions,
blockers, or explicitly standalone sessions. Record a clean check inline in the
action comment when useful.

Explicit implementation wording does not bypass these gates. Stop for approval
if implementation reveals product behavior or another high-risk decision outside
the approved Issue. Record low-risk local assumptions in the Implementation
Report or Issue comment.

## Backend constraints

- Keep FastAPI application code under `backend/app/`.
- Use Python and `uv` patterns already established in the repository.
- Use Pydantic schemas for API response models.
- Load MVP data from `data/seed/` until a database is explicitly introduced.
- Keep route, place, event, and connection field names aligned with seed data.
- Preserve the documented seed contracts in
  `docs/data/seed-data-validation.md`.
- Do not introduce a database unless the approved Issue explicitly requests it.
- Do not commit secrets, API keys, local paths, generated media, audio, or
  video.

## Process

1. Read the approved Issue and identify the exact backend acceptance criteria.
2. Inspect the existing backend structure under `backend/app/`, relevant tests,
   and the related seed data before editing.
3. Check the documented seed contract before changing seed-backed behavior.
4. Define or update Pydantic schemas before endpoint handlers when response
   shapes change.
5. Add or update explicit seed repositories/loaders when data access changes.
6. Implement only the approved backend slice. Preserve existing endpoint,
   filtering, unknown-ID, and empty-result behavior unless the Issue changes it.
7. Add targeted tests for changed behavior.
8. If implementation reveals a missing product or high-risk decision, stop and
   update the Issue rather than silently expanding scope.

## Expected MVP endpoints

The current MVP backend includes:

- `GET /health`
- `GET /routes`
- `GET /events`
- `GET /events/{event_id}`
- `GET /places`
- `GET /connections`

Treat this list as existing context, not permission to change endpoints outside
the approved Issue.

## Validation

Run the narrowest relevant checks first. For backend changes, the repository
defaults are:

```sh
uv run ruff check .
uv run pyright
uv run pytest
```

If a check is unavailable or blocked, report the blocker clearly. Also run
`python scripts/check_doc_references.py` when workflow or documentation files
change.

## Implementation Report

Before finalizing the report for completed non-trivial Issue work, use
`soundatlas-implementation-review`. Resolve or route required findings, then
include its Review Result in this same report. Do not post a separate routine
review comment.

Report in the Issue and final response:

```md
## Summary

- What backend behavior changed.
- Which approved Issue behavior was implemented.

## Acceptance Criteria Result

- AC1: Pass/Fail — evidence

## Verification

- `<command>` — Pass/Fail

## Files Changed

- `<path>`: `<reason>`

## Review Result

- Verdict:
- Reviewer mode:
- Compared artifacts:
- Evidence coverage:
- Findings and routing:
- Documentation impact:

## Remaining Risks

- None, or the specific blocker.
```

Do not commit unless the user explicitly requests it. If committed, use a
Conventional Commit and include `Issue: #<number>` in the commit body.

After a successful commit for completed Issue work, capture the commit hash,
verify the acceptance criteria and Issue-relevant working-tree state, post the
standard completion comment, and close the Issue. Do not close for uncommitted,
partial, WIP, incomplete, or ambiguously scoped work, or when the human asks to
keep the Issue open. If commenting or closing fails, report the failure and
leave the Issue open when possible.
