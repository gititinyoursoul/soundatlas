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
transition, and post-push completion. The workflow registry selects the
entrypoint for each kind of work. Skills and prompts provide the procedures for
producing their assigned artifacts and must follow this lifecycle contract.

In particular, `soundatlas-issue-planning` drafts and revises Intake Issues,
Plan Updates, Detailed Plan Updates, `## Proceed to Implementation` records,
and Implementation Reports. It does not own lifecycle ordering, post-push
closure, or Issue-state management.
`soundatlas-grill-me` owns the phase-aware critique procedure, Review Modes,
Materiality routing, and interactive one-finding flow; this document owns when
that procedure runs and the canonical completed Grill-Me record shape.
`soundatlas-implementation-review` owns implementation comparison, evidence
assessment, finding classification, and routing. This document owns when that
review occurs and how its result enters the Issue lifecycle.

## Safe GitHub Markdown Transport

Every multiline Markdown body created or edited through `gh` must come from a
UTF-8 body file or structured JSON sent through standard input. Do not pass
multiline Markdown through `--body`, interpolate it into a shell command, or
embed JSON-escaped newlines in a shell argument.

Use `--body-file` when the command supports it:

```sh
gh issue create --title "Title" --body-file issue.md
gh issue edit <number> --body-file issue.md
gh issue comment <number> --body-file comment.md
gh pr create --title "Title" --body-file pull-request.md
gh pr edit <number> --body-file pull-request.md
gh pr comment <number> --body-file comment.md
```

For API-only operations, encode the body from the file and send the JSON
through stdin:

```sh
python scripts/gh_markdown_payload.py --file comment.md \
  | gh api --method POST repos/<owner>/<repo>/issues/<number>/comments --input -
```

Read the created or edited body back when practical:

```sh
gh issue view <number> --json body --jq .body
```

The payload helper is local and non-mutating; it only emits JSON. Titles,
labels, milestone names, and other short scalar arguments are not Markdown
bodies and may remain command arguments.

## Workflow

```text
1. Human gives a feature/change request.
2. Agent inspects the repo before asking questions when local context can answer them.
3. Agent creates an Intake Issue containing only Task, Context, and Acceptance Criteria.
4. Agent performs a lightweight Grill-Me check and runs the interactive review when a material finding needs human confirmation.
5. If planning would otherwise invent material target behavior, runtime responsibilities, boundaries, or ownership, the agent uses `soundatlas-concept-work` and records an `## Concept` comment or linked authoritative document.
6. Agent adds a `## Plan Update` or `## Detailed Plan Update` after required decisions are confirmed. The plan references its accepted Concept or records why Concept Work was not required.
7. Human starts implementation with explicit wording such as "implement issue #<number>". This confirms the latest Plan Update and authorizes only its recorded scope.
8. Agent records `## Proceed to Implementation`, linking the exact confirmed Plan Update, and runs the readiness validator before the first repository edit.
9. Agent implements from the validated Issue content.
10. Agent validates the change with the relevant checks.
11. When the commit-ready gate passes, agent stages only the Issue-scoped files
    and creates a local Conventional Commit with an `Issue: #<number>` footer.
12. For completed non-trivial Issue work, agent uses
    `soundatlas-implementation-review` against that named local commit or an
    explicit local commit range.
13. Agent posts one combined `## Implementation Report` containing the review
    result.
14. Human reviews the committed diff and explicitly authorizes a push when the
    work is ready.
15. Agent pushes only the reviewed commit or reviewed integration range.
16. After a successful push, agent captures the published commit hash and runs
    the local completion gate. The gate must confirm the canonical report
    shape, checked acceptance criteria, an `Accepted` implementation review,
    exactly one completion comment plan, and Issue-relevant working-tree
    verification.
17. Agent posts the standard completion comment only after the gate passes and
    closes the Issue only after that comment succeeds.
18. If review, push, post-push verification, or a GitHub operation fails,
    agent reports the failure and leaves the Issue open when possible.
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
Grill-Me result before a `## Plan Update` or `## Detailed Plan Update` is added.
Use a standalone `## Grill-Me Review` when that result contains a material
finding, decision, blocker, or explicit standalone session; a clean result may
be recorded inline in the next action comment.

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
the one-finding flow in `soundatlas-grill-me`.

At the completed-implementation transition, the lightweight check selects
`soundatlas-implementation-review` for non-trivial Issue work. Grill Me becomes
interactive only when the review returns a material human decision.

For any risk-flagged work, run `soundatlas-grill-me` after intake creation and
before planning or implementation. Keep a material finding that is awaiting
human confirmation in the interactive conversation; do not publish it as a
completed Issue comment. After all material findings have decisions, record one
consolidated standalone `## Grill-Me Review`. For a clean check, use a concise
inline note in the next action comment when useful, or omit the note when no
durable record is needed.

Each material finding must state whether user confirmation is required. User
confirmation is required for product behavior, scope, security, privacy,
external API behavior, editorial or source decisions, irreversible workflow
behavior, and production stability. Low-risk implementation details may be
assumed when recorded in the later Plan Update.

Do not mark open questions as resolved while a material decision remains
unconfirmed.

A completed `## Grill-Me Review` uses this minimal shape:

```md
## Grill-Me Review

**Stage:** Intake | Plan | Implementation | Implementation Review

### Findings and decisions

1. **Finding:** <material finding>
   **Decision:** Confirmed by human — <decision>

**Next step:** <Plan Update | Concept Work | Blocked>
```

For multiple findings, number each `Finding`/`Decision` pair in the same
comment. Every material finding must have an explicit decision, including a
decision to defer, reject, or remain blocked. A `## Plan Update` must not rely
on the plan itself to claim that a missing Grill-Me decision was confirmed.
`Next step` records workflow routing; it does not by itself confirm a Plan or
authorize implementation.

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

Add a Plan Update in the Issue before non-trivial implementation. A
decision-complete Intake may use a concise Plan with the Concept-not-required
rationale; it does not skip the pre-implementation artifact gate.

Before `## Plan`, include exactly one planning-basis line:

```md
Target Concept: [<accepted Concept>](<Issue comment or authoritative document>)
```

or:

```md
Concept Work: Not required — <why the Intake is decision-complete>
```

The planning entrypoint must establish that basis before producing technical
solution detail. A Concept-not-required rationale is not a separate workflow
status or approval step.

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
  when one exists; otherwise record the concise Concept-not-required rationale.
  Do not copy a Concept into the Plan Update.
- If planning exposes a missing or contradictory material target decision,
  return to Grill Me and concept work instead of resolving it in the plan.
- For risk-flagged work, add the Plan Update only after the Issue contains a
  recorded Grill-Me result with required decisions confirmed. Use a standalone
  `## Grill-Me Review` when the result contains a material finding, decision,
  blocker, or explicit standalone session; a clean check may be recorded inline
  in the Plan Update with the `Grill-Me check: clean` prefix.
- Use `Acceptance Criteria Changes` whenever the original criteria are changed.
  Do not silently rewrite the meaning of the Issue.
- Use `Requirements` only when complex product, API, data, security, or workflow
  rules would otherwise be unclear.
- Stop for approval when open questions affect product intent, data shape,
  security, privacy, external API behavior, generated media review boundaries,
  historically sensitive claims, irreversible workflow behavior, or production
  stability.
- For mechanical readiness, `## Open Questions` must start with `None` or each
  remaining item must say `Deferred by human` and `non-blocking`. Do not use
  either marker to hide a material unresolved decision.

## Proceed to Implementation

For non-trivial Issue work, one explicit human implementation request after the
latest Plan Update both confirms that Plan and authorizes its recorded scope.
Before editing repository artifacts, use `soundatlas-issue-planning` to record:

```md
## Proceed to Implementation

- Plan: [<exact Plan Update>](<Issue comment URL>)
- Human decision: Proceed with this plan.
- Authorized scope: Issue #<number> <concise scope reference>
```

The heading and fields are a durable authorization record, not a new approval
status. Do not infer it from a Grill-Me `Next step`, technical readiness, a
request to inspect or plan an Issue, or implementation wording that predates the
latest Plan Update.

## Planned Write Boundary

Every non-trivial Plan Update or Detailed Plan Update must declare its planned
write boundary before implementation. The boundary has three parts:

1. **Named authoritative paths:** exact files whose policy, product, workflow,
   or other source-of-truth content the Issue changes. `AGENTS.md` is always a
   named authoritative path; it is never included only as a derived update.
2. **Derived-consistency surface:** a bounded class of direct consumers of the
   named authorities, with its relationship and permitted mechanical alignment
   stated. It is not a blanket directory-edit allowance and may not introduce
   new behavior or policy.
3. **Excluded scope:** paths or change types that remain outside the Issue.

Before the first repository edit, audit the declared derived-consistency surface
and list each exact derived file to be changed in the matching `## Proceed to
Implementation` record. The Human's implementation authorization covers the
named authorities and those audited derived files only.

When a newly discovered file is not a listed authority or audited direct
consumer, leave it unchanged and create a linked Intake Issue. Do the same when
the proposed change would add a new policy, behavior, domain, or material scope
even if the file is inside a declared derived-consistency surface. List every
derived file actually changed in the Implementation Report.

A later Plan Update, Detailed Plan Update, Intake Revision, Concept, or
Grill-Me decision that routes work back to Concept, Planning, or Blocked
invalidates the earlier go-ahead. The Human must authorize the current Plan and
the agent must record a new `## Proceed to Implementation` before work resumes.
Routine comments and implementation evidence do not invalidate it.

Do not rewrite historical Issue comments to add this record. When existing open
work next enters implementation, use its current canonical artifacts when they
already satisfy the gate; otherwise add a new Plan Update and go-ahead while
preserving the earlier history. Closed Issues need no migration.

## Implementation Gate

Implementation may proceed when:

- The human explicitly requests implementation of the latest Plan with wording
  such as `implement issue #<number>`, or the change is clearly trivial.
- The Issue contains enough Task, Plan, and Acceptance Criteria detail to
  implement safely.
- Blocking questions are resolved or intentionally deferred.
- For non-trivial work, the Issue contains a current `## Plan Update` or
  `## Detailed Plan Update`, followed by a matching `## Proceed to
  Implementation`.
- The Plan declares a planned write boundary, and the matching Proceed record
  lists the exact derived files found by its pre-write audit.
- For risk-flagged work, the Issue also contains its required Grill-Me result.
  The result may be inline in the Plan when clean; material findings, decisions,
  blockers, and standalone sessions use `## Grill-Me Review`.
- The shared readiness validator passes immediately before the first Issue-scoped
  repository edit.

Explicit implementation wording does not bypass a required Grill-Me review or
Plan Update, the go-ahead record, or validation. A low-risk assumption may be
recorded and carried forward; a material unresolved decision requires user
confirmation before implementation.

Export the current Issue artifacts and run the non-mutating check with:

```sh
gh issue view <number> --json number,body,comments \
  | python scripts/check_issue_readiness.py --file -
```

Add `--require-grill-review` when the Issue has a risk flag that requires a
recorded Grill-Me result. Without that flag, the validator still validates any
Grill-Me records that are present; the Plan's Concept basis carries the semantic
pre-planning decision for the clean or omitted-check path.

The validator checks canonical artifact structure and ordering. It does not
decide Materiality, create Issue comments, or replace the semantic checks owned
by Grill Me and Issue Planning. Clearly trivial, local, low-risk work remains on
the direct path and does not invoke this non-trivial-Issue gate.

The agent must not implement behavior outside the approved Issue content. If
implementation reveals missing behavior, the agent should:

- Continue and record an assumption when the decision is low-risk and local to
  implementation.
- Stop for approval when the decision changes product behavior or another
  high-risk boundary.

If drift produces a new Plan, Intake Revision, Concept, or blocking Grill-Me
decision, the existing go-ahead is invalid. Record a new go-ahead for the
current Plan and rerun readiness validation before implementation resumes.

## Implementation Review

Use `.codex/skills/soundatlas-implementation-review` once before accepting
completed non-trivial Issue work. The review compares a named local commit or
an explicit local commit range created after the commit-ready gate. Skip it for
clearly trivial, local, low-risk changes. During implementation, use it only
when drift, risk, or a new material constraint requires comparison before work
continues.

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

Before a report can support completion, run the local validation gate:

```sh
python scripts/check_issue_completion.py report --file implementation-report.md
```

The report must contain all canonical sections, at least one acceptance
checklist item, no unchecked acceptance item, and `- Verdict: Accepted` in its
Review Result. A report with open criteria or a non-`Accepted` verdict remains
an implementation status record, not a completion record.

## Commit-Ready Gate and Local Commits

After implementation validation succeeds, the agent creates a local commit
without a separate commit request only when every commit-ready condition holds:

- relevant validation has passed;
- the change remains within the approved Issue scope;
- the selected files contain no secrets, tokens, local paths, generated media,
  or other prohibited artifacts;
- the Git index contains only files belonging to that work package; and
- the commit has a Conventional Commit subject and an `Issue: #<number>`
  footer.

If the index already contains unrelated staged work, the agent must not stage
or commit into that index. It reports the conflict and leaves the existing
staged work unchanged.

A single agent or sequential work may use the current branch. Independently
active work packages must each own a branch and worktree, with one CLI write
owner per worktree. Other CLIs may inspect, test, or review that worktree but
must not stage, commit, switch branches, rebase, merge, or otherwise change it.

Branch integration is explicit. A fast-forward preserves the reviewed commit;
any rebase, merge, cherry-pick, or conflict resolution that changes the
integration range requires relevant validation and review of that resulting
range before push. The workflow does not automate integration or conflict
resolution.

## Post-Push Completion and Issue Closure

For completed Issue-based work, an explicit request to push the reviewed change
counts as authorization to close the associated Issue unless the human
explicitly asks to keep it open. A local commit, an `Accepted` review, or a
push alone does not establish Issue closure.
Issue closure is a mandatory, ordered post-push step:

1. Confirm that the reviewed commit or integration range was pushed to the
   intended remote branch, then capture its published commit hash.
2. Run the completion gate with the report, commit hash, one planned completion
   comment, and Issue-relevant working-tree verification:

   ```sh
   python scripts/check_issue_completion.py completion \
     --report implementation-report.md \
     --commit <commit-hash> \
     --completion-comments 1 \
     --working-tree-verified
   ```

3. Verify every acceptance criterion against the committed change and checks.
4. Confirm that no Issue-relevant files remain modified or uncommitted.
   Unrelated user-owned changes do not block closure and must not be included
   merely to make the tree clean.
5. Post the single completion comment using this format:

   ```md
   ## Completed

   - Commit: `<commit hash>`
   - Issue: #<number>
   - Acceptance criteria: complete
   - Verification: `<checks or report reference>`
   ```

6. Close the Issue only after the completion comment succeeds.

Do not push or close the Issue when the review is not `Accepted`, the work is
uncommitted, the commit is partial or WIP, an acceptance criterion is
incomplete, the commit covers multiple Issues without an unambiguous mapping,
or the human explicitly asks to keep the Issue open. If the push, completion
comment, or close operation fails, report the failure and leave the Issue open
when possible.

The completion sequence must remain distinct in the workflow record: the
Implementation Report describes the reviewed result, the local commit records
the work package, the push publishes the reviewed change, the working-tree
check verifies relevant completeness, the completion comment provides Issue
evidence, and closing the Issue records the final lifecycle state.

The safe transport rule above also applies to the standard completion comment.
Use the generic `scripts/gh_markdown_payload.py` helper for API-only Markdown
payloads.

Do not add a separate `done` label for completion.

## Commit Reference

When implementation work is locally committed, keep the Conventional Commit
subject clean and reference the Issue in the commit body:

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
- Do not commit changes outside the commit-ready Issue workflow.
