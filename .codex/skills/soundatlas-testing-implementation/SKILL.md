---
name: soundatlas-testing-implementation
description: Plan and implement focused SoundAtlas tests from approved Issues or concrete test scopes, with deterministic fixtures, mocks, environment constraints, backend/frontend validation, and test reporting.
---

# SoundAtlas Testing Implementation

Use this skill for standalone SoundAtlas test planning and implementation
across backend, frontend, data validation, and cross-cutting behavior. The
approved GitHub Issue or concrete focused scope defines what may be tested.
Implementation skills remain responsible for targeted tests covering behavior
they change; this skill is not an additional mandatory stage for every
implementation.

## Required context

Read these before editing:

- `AGENTS.md`
- `docs/github-issue-workflow.md`
- `docs/workflow-registry.md`
- the approved GitHub Issue, including any recorded Grill-Me findings or
  decisions and its `## Plan Update` or `## Detailed Plan Update` when risk
  flags are present. A standalone `## Grill-Me Review` is used when the result
  is material or explicitly standalone; a clean check may be inline in the
  relevant action comment.
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

For non-trivial Issue work, require a current Plan and a `## Proceed to
Implementation` record linking it. Before the first repository edit, and again
before resuming after a canonical revision or blocking decision, export the
current Issue fields defined in `docs/github-issue-workflow.md` and require
`python scripts/check_issue_readiness.py --file <export>` to pass. Add
`--require-grill-review` when risk flags require a recorded Grill-Me result. If
the Human has authorized the latest Plan but the Proceed record is missing, use
`soundatlas-issue-planning` to record it first. Keep deterministic artifact
rules in the shared validator rather than duplicating them here.

For non-trivial work, edit only named authorities and the audited direct
consumers listed by the Plan's planned write boundary and Proceed record. Route
any other path or material scope change to a linked Intake Issue.

## Evidence contract

A focused test scope names the behavior, relevant positive and negative cases,
test level, existing runner, fixture and mock boundaries, environment, and
expected assertions before execution. Prefer a small first slice with minimal,
deterministic, independent fixtures shaped like current seed or API data.
Isolate filesystem writes, network calls, map tiles, and external media. Do not
require real browser network access, audio, video, or large fixtures.

Keep these evidence types distinct:

- **Hypothesis experiment:** tests a proposition or informs a decision. Record
  the hypothesis and observed result. It does not replace required
  deterministic assertions.
- **Deterministic automated coverage:** exercises approved behavior at the
  required unit, component, integration, end-to-end, or seed/data-contract
  level with repeatable inputs and meaningful assertions. Browser tests can
  qualify when deterministic and required; a runner name alone does not prove
  coverage level.
- **Runtime validation:** checks behavior in the actual authorized runtime,
  including browser or Leaflet rendering when required. It does not make up for
  missing deterministic unit, component, integration, or data-contract tests.
- **PR journey QA:** exercises a user journey and records observations. It adds
  broader confidence but cannot alone satisfy required deterministic coverage.

Do not treat different evidence as a substitute for a required coverage level.
For example, server-side rendering does not establish browser interaction, and
a screenshot does not establish unit assertions.

## Runner and environment selection

Choose commands from current `AGENTS.md`, project instructions, manifests, and
the applicable data authority. Use ordinary repository tools when they meet
the scope. When Pane is selected, follow the existing Pane–SoundAtlas
composition contract in `docs/workflow-registry.md`; do not require equivalence
to named Pane methods or a particular provider. A missing provider by itself
does not establish a capability gap.

For project-specific execution, first check project instructions and Compose
configuration and use only an operator-approved mode and service. `project
run` requires explicit one-off approval; Compose membership or healthy status
does not grant it. `project exec` requires a separately authorized running
service. Build or start the stack only when authorized and needed. Do not
install project toolchains in the persistent runtime or bypass a denial.

## Backend guidance

- Use `uv run pytest` for focused backend tests. When backend code changes, run
  the required `uv run ruff check .`, `uv run pyright`, and `uv run pytest`.
- Cover API response behavior, seed loading, filtering, unknown IDs, empty
  results, and reference integrity when relevant to the approved scope.
- Use small fixtures and mock filesystem paths or external services.

## Frontend guidance

- Use the existing Vitest setup for focused frontend tests. `npm test` also
  runs the legacy CSS checker, so a targeted Vitest filter is not the full
  validation gate.
- Use current utility and component test patterns. Identify server-rendered
  component coverage as SSR; do not describe it as browser interaction.
- Use Playwright for browser end-to-end, screenshot, or Leaflet rendering tests
  only when the approved scope requires it. Report Chromium or environment
  blockers separately from available deterministic checks.
- Mock Leaflet, map tiles, and browser network behavior.
- Keep fixtures small and shaped like current API or seed responses.

For frontend code changes, follow `AGENTS.md` validation requirements,
including `npm run validate`; use `validate:release` or `validate:pages` when
their documented conditions apply.

## Data/API guidance

Follow `docs/data/seed-data-validation.md` for seed checks and select the
relevant schema, repository, or API tests for the approved contract. Keep
backend schema/seed evidence and frontend API-client evidence separate unless
the scope includes a test that establishes their interaction.

## Unavailable and partial execution

Distinguish an unmet prerequisite before invocation from a command that started
and failed or produced partial results. Record the tested revision, behavior
and intended evidence level, actual command and environment, result or exact
missing prerequisite, completed and unrun checks, changed paths or partial
effects, and the recovery owner. Mark unavailable checks blocked or unrun,
never passing. Preserve required coverage and stop affected acceptance until
the gap is resolved; runtime recovery mechanics belong to the runtime owner.

If implementation reveals a missing product or high-risk decision, stop and
update the Issue rather than silently expanding scope. A test result alone
does not advance delivery, Project status, publication, or retirement.

## #202 evaluation handoff

Issue #202 owns representative behavior execution and the readiness/GAP-4
verdict. These are prepared cases, not evidence that execution has occurred.
Each requires an approved #202 scope, tested revision, current authorities and
authorization, actual capability/provider/procedure and provenance,
runner/environment, fixture/mock choices, commands, results, and
expected-versus-observed evidence. Include an ordinary-tools path for the same
required checks and selected-Pane evidence only when Pane is chosen.

| Case and entry criteria | Expected outcome | Evidence to record |
| --- | --- | --- |
| Backend API/filter/error behavior with an approved scope and existing `backend/tests/test_api.py` | Use TestClient and deterministic seed input; assert filtering, unknown ID, and invalid range behavior. Use a temporary seed repository for writes; candidate command: `uv run pytest tests/test_api.py`. | Assertions, fixtures and write isolation, actual test level and result; a health check or journey alone is insufficient. |
| Frontend state/rendering with an approved scope and existing selection/Timeline tests | Exercise empty, ordered, and selected states with `npm exec -- vitest run src/lib/data/selection.test.ts src/lib/components/Timeline.test.ts`. | Deterministic inputs and results; identify Timeline server rendering as SSR. Required browser interaction is separate evidence or remains blocked. |
| Data/API contract with an approved schema, seed, or client scope | Check story representation exclusivity/order, references/default place, and mocked API responses; candidate commands: `uv run pytest tests/test_schemas.py tests/test_seed_repository.py` and `npm exec -- vitest run src/lib/api/soundatlas.test.ts`. Do not write production seeds. | Positive and invalid payload results, reference assertions, mock boundary, and separate backend/frontend evidence; do not infer cross-system parity. |
| Unavailable runner, browser, or service, or a denied approved-route prerequisite | Record the unmet prerequisite before start versus a failure after start; retain successful checks, mark unrun obligations, stop affected acceptance, and name the recovery owner. Do not cause a denial intentionally. | Exact prerequisite/error, command if attempted, revision, partial effects, completed/unrun checks, and confirmation that no bypass, install, or pass claim occurred. |

Textual routes and structural checks do not close GAP-4. Retirement remains
blocked until every required #202 case passes and #202 records accepted
affected-row evidence, followed by a Human-confirmed #203 Plan. If evaluation
fails, retain the override and route the correction to its owner; rollback
restores only this slice's prior hunks while preserving user work and canonical
Issue history. Issue #203 owns any later retirement decision; #249 does not
retire this testing override.

## Validation and reporting

Run only checks required by the approved scope and current project guidance.
Workflow or documentation changes use the validation commands named by their
Plan, including `git diff --check` and `python scripts/check_doc_references.py`
when applicable. The Issue lifecycle, implementation review, commit, and
reporting requirements are owned by `docs/github-issue-workflow.md`,
`docs/workflow-registry.md`, and `soundatlas-issue-planning`; follow those
sources instead of duplicating their generic edit and report procedures here.
