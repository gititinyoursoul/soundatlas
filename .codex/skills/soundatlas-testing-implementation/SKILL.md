---
name: soundatlas-testing-implementation
description: Plan and implement focused SoundAtlas tests from approved Issues or concrete test scopes, with deterministic fixtures, mocks, environment constraints, backend/frontend validation, and test reporting.
---

# SoundAtlas Testing Implementation

Use this skill for standalone SoundAtlas test planning and test implementation
across backend, frontend, data validation, and cross-cutting behavior. The
approved GitHub Issue or concrete focused test scope defines what may be
tested. Implementation skills remain responsible for targeted tests covering
behavior they change; this skill is not a mandatory separate gate for every
implementation.

## Required context

Read these before editing:

- `AGENTS.md`
- `docs/implementation-plan-workflow.md`
- `docs/workflow-registry.md`
- the approved GitHub Issue and its `## Grill-Me Review` and `## Plan Update`
  or `## Detailed Plan Update` comments when risk flags are present
- existing tests and the target code or data workflow

Optional context may clarify the test slice without overriding its scope:

- target module, component, endpoint, data workflow, or seed validation
- expected behavior, edge cases, and known bugs
- test level and existing runner
- fixture, mock, filesystem, network, browser, or environment constraints

## Planning and implementation boundary

Support planning-only output when the test scope is not implementation-ready.
Before writing tests, require either:

- an approved GitHub Issue with testable acceptance criteria; or
- a concrete, focused test scope that identifies behavior, test level, files,
  fixtures/mocks, and validation commands.

Do not write tests directly from a vague request. Explicit implementation
wording does not bypass required Grill-Me and Plan Update gates for risky,
workflow, cross-cutting, or materially ambiguous work. Clearly trivial,
local, low-risk test changes may proceed directly.

## Process

1. Read the approved Issue or focused test request and identify the exact test
   behavior and acceptance boundary.
2. Inspect existing tests, coverage patterns, and target code before editing.
3. Define the test level: unit, component, integration, end-to-end, or
   seed/data validation.
4. Identify current coverage, behaviors to cover, intentional out-of-scope
   behavior, required fixtures/mocks, and environment constraints.
5. Prefer a small first test slice before broad coverage.
6. Add only the tests in the approved or focused scope. Keep fixtures minimal,
   deterministic, independent, and shaped like current seed/API responses.
7. Mock filesystem paths, network calls, map tiles, and external media. Do not
   require real browser network access, audio, video, or large fixtures.
8. If implementation reveals a missing product or high-risk decision, stop and
   update the Issue rather than silently expanding test scope.

## Backend guidance

- Use `pytest` through `uv run pytest` when possible.
- Cover API response behavior, seed loading, filtering, unknown IDs, empty
  results, and reference integrity when relevant to the approved scope.
- Use small fixtures and mock filesystem paths or external services.

## Frontend guidance

- Use `npm test` once frontend test infrastructure exists.
- Prefer Vitest for pure TypeScript utilities and lightweight state logic.
- Prefer Svelte Testing Library for component rendering and interaction tests.
- Use Playwright for browser end-to-end, screenshot, or Leaflet rendering tests
  only when the scope requires it; report Chromium/environment blockers.
- Mock Leaflet, map tiles, and browser network behavior.
- Keep fixtures small and shaped like current API or seed responses.

## Validation

Run the narrowest relevant command first, then broader checks when useful:

```sh
uv run pytest
npm test
```

Run only the applicable command for the target area. Also run
`git diff --check` and `python scripts/check_doc_references.py` when workflow or
documentation files change.

## Test Report

Before finalizing the report for completed non-trivial Issue work, use
`soundatlas-implementation-review`. Resolve or route required findings, then
include its Review Result in this same report. Do not post a separate routine
review comment.

Report in the Issue and final response:

```md
## Summary

- What test coverage changed.
- Which approved behavior or focused scope was covered.

## Coverage and Scope

- Test level:
- Covered behavior:
- Intentionally out of scope:
- Fixtures/mocks/environment:

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

- None, or the specific gap/blocker.
```

Do not commit unless the user explicitly requests it. If committed, use a
Conventional Commit and include `Issue: #<number>` in the commit body.

After a successful commit for completed Issue work, capture the commit hash,
verify the acceptance criteria and Issue-relevant working-tree state, post the
standard completion comment, and close the Issue. Do not close for uncommitted,
partial, WIP, incomplete, or ambiguously scoped work, or when the human asks to
keep the Issue open. If commenting or closing fails, report the failure and
leave the Issue open when possible.
