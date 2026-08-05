# GitHub Issue Workflow

This document defines the lightweight Issue-based workflow for SoundAtlas agent
work.

The default workflow is Issue-led:

> Create an Intake Issue first. For risky, vague, or cross-cutting work, run
> Grill-Me and record confirmed decisions. Use concept work only when planning
> would otherwise have to invent the target, then add a Plan Update. Explicit
> implementation wording does not bypass those gates.

GitHub Issues are the source of truth for planned agent work. `TODO.md` is a
legacy backlog and should not receive new planned work unless the human
explicitly asks for a legacy note.

## Authority and Skill Boundaries

This document is the normative contract for the GitHub Issue lifecycle: its
sequence, gates, required Issue comment shapes, implementation-review
transition, and post-commit completion. The workflow registry selects the
entrypoint for each kind of work. Skills and prompts provide the procedures for
producing their assigned artifacts and must follow this lifecycle contract.

In particular, `soundatlas-issue-planning` drafts and revises Intake Issues,
Plan Updates, Detailed Plan Updates, and Implementation Reports. It does not
own lifecycle ordering, post-commit closure, or Issue-state management.
`soundatlas-implementation-review` owns implementation comparison, evidence
assessment, finding classification, and routing. This document owns when that
review occurs and how its result enters the Issue lifecycle.

## Workflow

```text
1. Human gives a feature/change request.
2. Agent inspects the repo before asking questions when local context can answer them.
3. Agent creates an Intake Issue containing only Task, Context, and Acceptance Criteria.
4. Agent performs a lightweight Grill-Me check and runs the interactive review when a material finding needs human confirmation.
5. If planning would otherwise invent material target behavior, runtime responsibilities, boundaries, or ownership, the agent uses `soundatlas-concept-work` and records an `## Concept` comment or linked authoritative document.
6. Agent adds a `## Plan Update` or `## Detailed Plan Update` after required decisions are confirmed.
7. Human starts implementation with explicit wording such as "implement issue #<number>".
8. Agent implements from the approved Issue content.
9. Agent validates the change with the relevant checks.
10. For completed non-trivial Issue work, agent uses `soundatlas-implementation-review` to compare the accepted target, implementation, evidence, and documentation.
11. Agent posts one combined `## Implementation Report` containing the review result.
12. Human reviews the local diff and explicitly requests a commit when the work
    is ready.
13. After a successful commit, agent captures the commit hash, verifies the
    acceptance criteria, confirms that no Issue-relevant changes remain
    uncommitted, posts the standard completion comment, and closes the Issue.
14. If any post-commit verification or GitHub operation fails, agent reports
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

## Intake Revision

An Intake may be revised before planning when discovery or user discussion
reveals a missing requirement. Update the Issue body so it shows the current
`Task`, `Context`, and `Acceptance Criteria`, and preserve the change history in
an Issue comment:

```md
## Intake Revision

- Date: YYYY-MM-DD
- Previous scope: <what the Intake said before>
- Revised scope: <what the Intake says now>
- Reason: <why the revision is needed>
```

Do not silently broaden an Intake by editing its body without this record.
Wording-only clarifications do not require a new Grill-Me review. A material
revision becomes the new pre-planning artifact and must receive a fresh
`## Grill-Me Review` before a `## Plan Update` or `## Detailed Plan Update` is
added.

Create a linked Issue instead of revising the current Intake when the expansion
introduces a separate deliverable, changes the primary outcome, crosses a
materially different domain or owner, or needs independent sequencing.

After a Plan Update exists but before implementation begins, record material
scope changes in an `Acceptance Criteria Changes` section, update the plan, and
run the required review again. After implementation begins, track material
scope expansion in a linked Issue rather than silently changing the approved
implementation boundary.

## Grill-Me Review

Perform a lightweight Grill-Me check:

- at Intake;
- before accepting a consequential concept;
- before approving a broad or risky Plan Update;
- when implementation reveals drift, conflicting assumptions, or new
  constraints; and
- before accepting completed implementation.

If no material finding exists, continue without starting an interactive review
or adding an approval step. If a material finding needs human confirmation, use
the one-finding flow in `prompts/grill-me.md`.

At the completed-implementation transition, the lightweight check selects
`soundatlas-implementation-review` for non-trivial Issue work. Grill Me becomes
interactive only when the review returns a material human decision.

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

At Issue-creation time, inspect the existing open milestones. Assign the Issue
to one milestone only when completing the Issue directly advances the outcome
stated by that milestone's title and description. Shared labels, a related
product area, or an indirect benefit do not establish a direct match. Treat
partial, indirect, multiple, or otherwise ambiguous matches as no clear match:
leave the Issue unassigned and state why.

Do not create, rename, or broaden a milestone without explicit human approval.
The Issue-creation handoff must report both the selected priority and its
rationale and the milestone decision and its rationale. When no existing open
milestone fits, explicitly report that the Issue was left unassigned.

Priority meanings:

- `priority:p0`: urgent or blocking; release or development work cannot
  continue safely.
- `priority:p1`: next up; directly supports current MVP or reduces major risk.
- `priority:p2`: important later; valuable but not blocking current work.
- `priority:p3`: backlog or nice-to-have; no near-term commitment.

## Concept Work

Use `.codex/skills/soundatlas-concept-work` when the human requests concept work
or a Grill-Me check finds that implementation planning would otherwise have to
invent material target behavior, runtime responsibilities, boundaries, or
ownership. Concept work is optional and repeatable, not a mandatory stage. Skip
it for clear, local, low-risk work.

Grill Me challenges assumptions and obtains human confirmation. Concept work
synthesizes the confirmed target. Implementation planning turns that target
into tasks, sequencing, and validation.

Use this minimum concept shape:

```md
## Concept

### Target behavior

### Scope and non-goals

### Runtime responsibilities

### Boundaries and ownership

### Unresolved decisions
```

Runtime responsibilities describe what the running system must do. Boundaries
and ownership describe responsibility, authority, and where each responsibility
stops. Do not choose components, files, schemas, or services unless an accepted
constraint requires the choice.

Record the concept as an `## Concept` comment on the originating Issue by
default. Use one authoritative document under `docs/` instead when the concept
spans several Issues or system areas, defines durable behavior or terminology,
guides future work, or changes a product or architecture source of truth. Get
human confirmation before creating or changing that document. Link it from the
Issue rather than duplicating it.

Concept work is ready for planning when material decisions are confirmed and
no unresolved decision would force planning to invent target behavior. It does
not add a separate approval status.

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
- Reference an accepted `## Concept` comment or authoritative concept document
  when one exists; do not copy it into the Plan Update.
- If planning exposes a missing or contradictory material target decision,
  return to Grill Me and concept work instead of resolving it in the plan.
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

## Implementation Review

Use `.codex/skills/soundatlas-implementation-review` once before accepting
completed non-trivial Issue work. Skip it for clearly trivial, local, low-risk
changes. During implementation, use it only when drift, risk, or a new material
constraint requires comparison before work continues.

At this transition, select the review skill for the comparison, evidence
assessment, finding classification, and routing defined by that skill. It is
read-only and returns material human decisions to Grill Me. Do not require
retroactive concept work for an Issue that did not need it. Resolve required
findings and rerun the review before finalizing the Implementation Report.
Routine review remains part of that single report rather than a separate Issue
comment.

## Implementation Report

After review, post one combined `## Implementation Report` comment for completed
non-trivial Issue work and summarize it in the final response. The review result
is a section of this report, not a second comment.

```md
## Summary

- What changed.

## Verification

- `<command>` - Pass/Fail

## Acceptance Criteria Result

- [x] `<criterion>` - evidence
- [ ] `<criterion>` - blocker or remaining work

## Review Result

- Verdict: Accepted | Correction required | Return to planning | Return to concept | Needs decision
- Reviewer mode: Implementing agent | Independent review
- Compared artifacts: `<artifacts actually reviewed>`
- Evidence coverage: `<material claims and evidence or gaps>`
- Findings and routing: None | `<finding and destination>`
- Documentation impact: Current | Corrected within scope | Routed

## Remaining Risks

- None, or:
- `<risk and follow-up>`
```

Use `Accepted` only when no material review finding remains. If work is blocked,
record the finding without describing the implementation as accepted. Do not
close the Issue just because implementation has started or the report was
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
