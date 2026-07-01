# Implementation Plan Workflow

This document defines the lightweight implementation-plan workflow for
SoundAtlas.

The default workflow is plan-led:

> Do not implement from a vague request. Inspect the repo, propose a concrete
> implementation plan when the work is non-trivial, capture planned agent work
> in GitHub Issues, save an approved non-trivial implementation plan locally,
> and implement only after an explicit implementation request.

GitHub Issues are the source of truth for planned agent work. `TODO.md` is a
legacy backlog and should not receive new planned work unless the human
explicitly asks for a legacy note.

## When To Plan

Use a plan before implementation for:

* New features
* UX behavior changes
* Backend/API behavior changes
* Seed data shape or data workflow changes
* Media retrieval or enrichment workflow changes
* Cross-cutting frontend/backend/data changes
* Non-trivial refactors
* Anything involving user-visible behavior
* Anything involving production-critical flows

A plan is usually not needed for:

* Typo fixes
* Formatting-only changes
* Tiny copy edits
* Mechanical renames
* Comments-only changes
* Trivial documentation edits
* Dependency bumps with no behavior change

For trivial changes, the agent may proceed directly if the request is clear and
low-risk.

## Default Workflow

```text
1. Human gives a feature/change request.
2. Agent inspects the repo before asking questions.
3. Agent creates or updates a GitHub Issue for non-trivial planned work.
4. The Issue captures Goal, Plan, and Acceptance Criteria.
5. Human starts implementation with explicit wording such as "implement issue #<number>".
6. Agent saves a local implementation plan record before non-trivial implementation.
7. Agent implements the approved Issue or local plan record.
8. Agent validates the change with the relevant checks.
9. Agent reports what changed, what was verified, and any remaining risk.
```

The approved Issue and local plan record are the source of truth for intended
behavior during that implementation turn.

## GitHub Issue Structure

Each planned work Issue should include:

* `Goal`: the intended outcome and why it matters.
* `Plan`: the concrete behavior-level implementation approach.
* `Acceptance Criteria`: testable conditions for completion.

Use optional `Non-Goals` or `Risks / Open Questions` sections only when they
clarify boundaries or unresolved decisions.

Codex may set existing approved GitHub labels on Issues. New labels must be
proposed and explicitly approved before Codex creates or uses them.

Recommended label families are:

* `type:feature`
* `type:bug`
* `type:refactor`
* `type:chore`
* `area:<feature-or-component>`
* `blocked`

## Local Plan Records

For implemented non-trivial work, save a local implementation plan record under:

```text
plans/records/P-###-<short-slug>.md
```

These records are gitignored during solo work. They are for later revision and
verification, not for normal commits.

Use the tracked guidance here:

```text
plans/README.md
plans/template.md
```

The local plan record should capture:

* request
* goal
* non-goals
* requirements
* acceptance criteria
* assumptions
* open questions
* implementation plan
* validation plan
* verification report
* related commits

## Implementation Gate

Implementation may proceed when:

* The human has explicitly requested implementation of an approved Issue with wording such as `implement issue #<number>`, or has approved a concrete plan, or a local implementation plan record exists for that approved Issue or plan, or the change is clearly trivial.
* Requirements are clear enough to implement.
* Acceptance criteria are testable enough to verify.
* Blocking questions are resolved or intentionally deferred.

The agent must not implement behavior outside the approved Issue, approved plan,
or local plan record.

If implementation reveals missing behavior, the agent should:

* Continue and record an assumption when the decision is low-risk and local to implementation.
* Stop for approval when the decision changes product behavior, data shape, security, privacy, external API behavior, generated media review boundaries, historically sensitive claims, irreversible workflow behavior, or production stability.

## Blocking Questions

Most incomplete input should not stop the agent. The agent should make
conservative assumptions and document them.

However, the agent must stop for approval when missing information involves:

* Data loss
* Destructive writes
* Schema changes
* Seed data shape changes
* Permissions or security
* Privacy
* External API behavior
* Generated media review boundaries
* Historically sensitive or uncertain claims
* Irreversible workflow changes
* Production stability risks

## SoundAtlas Project Constraints

Plans and implementation should respect these project constraints:

* Keep changes small, reviewable, and MVP-oriented.
* Current product scope is New York 1965-1985 with curated routes, events, places, connections, and external media links.
* Use existing project conventions in `AGENTS.md`.
* Prefer data-driven implementation from `data/seed/` over hardcoded UI mock data.
* Preserve seed file shapes documented in `docs/data/seed-data-validation.md`.
* Keep generated media links as `review_status: "draft"` until manually reviewed.
* Do not store audio or video files in the repository.
* Do not commit secrets, API keys, local paths, or generated media files.
* Do not commit changes unless explicitly requested.

## Commit Reference

When implementation work is committed, keep the Conventional Commit subject
clean and reference the plan ID in the commit body:

```text
feat(data): improve enrichment input

Plan: P-014
```

This is a documented convention, not a hook-enforced rule in the current
workflow.

## Closing Issues

An Issue is done when the local implementation is complete, relevant checks have
run or blockers are documented, and the Acceptance Criteria have been verified
in the final report.

Codex should not close Issues just because implementation has started. Close the
Issue with `gh issue close <number>` only when the human explicitly requests or
clearly approves closure after reviewing the local result. Prefer adding a short
completion comment with summary, checks, and remaining risks before closure.

Do not add a separate `done` label for completion.

## Verification Report

After implementation, the agent should report:

```md
## Summary

- What changed.
- Which approved plan requirements were implemented.

## Verification

- `<command>` - Pass/Fail

## Files changed

- `<path>`: `<reason>`

## Assumptions or drift

- None, or:
- `<assumption/change and why it stayed within the approved plan>`

## Next step

- `<concrete follow-up action>`
```

If a local plan record was created, update its verification report before
finishing.

## Practical Codex Usage

Typical fast path:

```text
Plan this change first:

<describe feature/change>
```

Then approve the plan in GitHub and start implementation:

```text
Implement issue #<number>.
```

For work that needs a local record:

```text
Implement the plan and save a local implementation plan record.
```

For work that should stay planning-only:

```text
Planning only. Do not edit files.
```

## Drift

Drift happens when implementation behavior differs from the approved plan or
local plan record.

The agent must not silently allow drift. It should record low-risk
implementation assumptions in the final report or local plan record, and stop
for approval when the difference changes product intent or another high-risk
boundary.
