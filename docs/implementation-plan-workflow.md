# GitHub Issue Workflow

This document defines the lightweight Issue-based workflow for SoundAtlas agent
work.

The default workflow is Issue-led:

> Create an Intake Issue first. For risky, vague, or cross-cutting work, run
> Grill-Me and record confirmed decisions before adding a Plan Update or
> implementing. Explicit implementation wording does not bypass those gates.

GitHub Issues are the source of truth for planned agent work. `TODO.md` is a
legacy backlog and should not receive new planned work unless the human
explicitly asks for a legacy note.

## Workflow

```text
1. Human gives a feature/change request.
2. Agent inspects the repo before asking questions when local context can answer them.
3. Agent creates an Intake Issue containing only Task, Context, and Acceptance Criteria.
4. If risk flags are present, agent runs Grill-Me and records a `## Grill-Me Review` comment with findings and confirmed decisions.
5. Agent adds a `## Plan Update` or `## Detailed Plan Update` after required decisions are confirmed.
6. Human starts implementation with explicit wording such as "implement issue #<number>".
7. Agent implements from the approved Issue content.
8. Agent validates the change with the relevant checks.
9. Agent posts an `## Implementation Report` in the Issue or final response.
10. Human reviews the local diff and explicitly requests a commit when the work
    is ready.
11. After a successful commit, agent captures the commit hash, verifies the
    acceptance criteria, confirms that no Issue-relevant changes remain
    uncommitted, posts the standard completion comment, and closes the Issue.
12. If any post-commit verification or GitHub operation fails, agent reports
    the failure and leaves the Issue open when possible.
```

For clearly trivial, local, low-risk changes, the agent may proceed directly
when the request is clear. This exception does not apply to security,
credentials, infrastructure, networking, workflow, UX, editorial,
cross-cutting, user-visible, or materially ambiguous work.

## Intake Issue

Create or update an Intake Issue when work is non-trivial, user-visible,
workflow-changing, cross-cutting, or likely to need later review.

Use this minimum structure:

```md
## Task

<What should be changed, investigated, decided, or fixed?>

## Context

<Why it matters, relevant files or workflow notes, optional links.>

## Acceptance Criteria

- [ ] <Concrete done condition>
```

Keep the intake lightweight. The `Task` can be close to a TODO item. Avoid
forcing a broad product `Goal` when the work is a small task, review,
investigation, or decision. An Intake Issue is not implementation-ready and
must not include speculative implementation steps, technical assumptions, or
prematurely resolved open questions.

## Grill-Me Review

For any risk-flagged work, run `prompts/grill-me.md` after intake creation and
before planning or implementation. Record the review in an Issue comment with
the heading `## Grill-Me Review`.

Each material finding must state whether user confirmation is required. User
confirmation is required for product behavior, scope, security, privacy,
external API behavior, editorial or source decisions, irreversible workflow
behavior, and production stability. Low-risk implementation details may be
assumed when recorded in the later Plan Update.

Do not mark open questions as resolved while a material decision remains
unconfirmed.

Codex may set existing approved GitHub labels on Issues. New labels must be
proposed and explicitly approved before Codex creates or uses them.

Recommended label families are:

- `type:feature`
- `type:bug`
- `type:refactor`
- `type:chore`
- `area:<feature-or-component>`
- `priority:p0`
- `priority:p1`
- `priority:p2`
- `priority:p3`
- `blocked`

When Codex creates an Issue, it should assign exactly one approved priority
label unless the human explicitly asks not to. Choose the priority by reasoning
from blocking level, MVP or release impact, risk reduction, and urgency. Use
`priority:p2` only as the neutral fallback when `p0`, `p1`, or `p3` are not
clearly justified. Briefly state the priority rationale when creating the Issue.

Priority meanings:

- `priority:p0`: urgent or blocking; release or development work cannot
  continue safely.
- `priority:p1`: next up; directly supports current MVP or reduces major risk.
- `priority:p2`: important later; valuable but not blocking current work.
- `priority:p3`: backlog or nice-to-have; no near-term commitment.

## Plan Update

Add a Plan Update in the Issue before non-trivial implementation when the Intake
Issue is not already decision-complete.

Use this structure for normal work:

```md
## Plan

## Non-Goals

## Open Questions
```

Use a Detailed Plan Update when the work is cross-cutting, risky, or has enough
detail that future implementation should not rediscover decisions:

```md
## Plan

## Assumptions

## Non-Goals

## Acceptance Criteria Changes

## Implementation Steps

## Validation

## Open Questions
```

Rules:

- Keep the plan in the GitHub Issue, not in a local or repo-versioned plan file.
- For risk-flagged work, add the Plan Update only after the Issue contains a
  `## Grill-Me Review` comment with required decisions confirmed.
- Use `Acceptance Criteria Changes` whenever the original criteria are changed.
  Do not silently rewrite the meaning of the Issue.
- Use `Requirements` only when complex product, API, data, security, or workflow
  rules would otherwise be unclear.
- Stop for approval when open questions affect product intent, data shape,
  security, privacy, external API behavior, generated media review boundaries,
  historically sensitive claims, irreversible workflow behavior, or production
  stability.

## Implementation Gate

Implementation may proceed when:

- The human explicitly requests implementation of an Issue with wording such as
  `implement issue #<number>`, or the change is clearly trivial.
- The Issue contains enough Task, Plan, and Acceptance Criteria detail to
  implement safely.
- Blocking questions are resolved or intentionally deferred.
- For risk-flagged work, the Issue contains a `## Grill-Me Review` comment and a
  confirmed `## Plan Update` or `## Detailed Plan Update`.

Explicit implementation wording does not bypass a required Grill-Me review or
Plan Update. A low-risk assumption may be recorded and carried forward; a
material unresolved decision requires user confirmation before implementation.

The agent must not implement behavior outside the approved Issue content. If
implementation reveals missing behavior, the agent should:

- Continue and record an assumption when the decision is low-risk and local to
  implementation.
- Stop for approval when the decision changes product behavior or another
  high-risk boundary.

## Implementation Report

After implementation, report in the final response and, when useful, as an Issue
comment:

```md
## Summary

- What changed.

## Verification

- `<command>` - Pass/Fail

## Acceptance Criteria Result

- [x] `<criterion>` - evidence
- [ ] `<criterion>` - blocker or remaining work

## Remaining Risks

- None, or:
- `<risk and follow-up>`
```

Do not close the Issue just because implementation has started or the report was
posted.

## Post-Commit Completion and Issue Closure

For completed Issue-based work, a request to commit counts as authorization to
close the associated Issue unless the human explicitly asks to keep it open.
Issue closure is a mandatory, ordered post-commit step:

1. Capture the successful commit hash.
2. Verify every acceptance criterion against the committed change and checks.
3. Confirm that no Issue-relevant files remain modified or uncommitted. Unrelated
   user-owned changes do not block closure and must not be included merely to
   make the tree clean.
4. Post the completion comment using this format:

   ```md
   ## Completed

   - Commit: `<commit hash>`
   - Issue: #<number>
   - Acceptance criteria: complete
   - Verification: `<checks or report reference>`
   ```

5. Close the Issue only after the completion comment succeeds.

Do not close the Issue when the work is uncommitted, the commit is partial or
WIP, an acceptance criterion is incomplete, the commit covers multiple Issues
without an unambiguous mapping, or the human explicitly asks to keep the Issue
open. If the completion comment or close operation fails, report the failure
and leave the Issue open when possible.

The completion sequence must remain distinct in the workflow record: the
Implementation Report describes the result, the commit records the change, the
working-tree check verifies relevant completeness, the completion comment
provides Issue evidence, and closing the Issue records the final lifecycle
state.

Do not add a separate `done` label for completion.

## Commit Reference

When implementation work is committed, keep the Conventional Commit subject
clean and reference the Issue in the commit body:

```text
feat(data): improve enrichment input

Issue: #123
```

This is a documented convention, not a hook-enforced rule in the current
workflow.

## SoundAtlas Project Constraints

Plans and implementation should respect these project constraints:

- Keep changes small, reviewable, and MVP-oriented.
- Current product scope is New York 1965-1985 with curated routes, events,
  places, connections, and external media links.
- Use existing project conventions in `AGENTS.md`.
- Prefer data-driven implementation from `data/seed/` over hardcoded UI mock
  data.
- Preserve seed file shapes documented in `docs/data/seed-data-validation.md`.
- Keep generated media links as `review_status: "draft"` until manually
  reviewed.
- Do not store audio or video files in the repository.
- Do not commit secrets, API keys, local paths, or generated media files.
- Do not commit changes unless explicitly requested.
