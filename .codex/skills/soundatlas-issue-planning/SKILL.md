---
name: soundatlas-issue-planning
description: Draft or revise SoundAtlas GitHub Issue intake, Plan Updates, Detailed Plan Updates, and Implementation Reports for frontend, backend, data, documentation, UX, or cross-cutting changes. Use when a SoundAtlas Issue needs to be created, refined for implementation, checked for open questions, or reported after implementation.
---

# SoundAtlas Issue Planning

Read the repo context before drafting or revising Issue planning content. Start
with:

- `AGENTS.md`
- `docs/github-issue-workflow.md`
- `docs/workflow-registry.md`
- the accepted `## Concept` Issue comment or authoritative concept document,
  when concept work was required
- the `soundatlas-implementation-review` result, when finalizing an
  Implementation Report for non-trivial Issue work

Read `prompts/grill-me.md` when the request needs critique, simplification, or
readiness review before Issue content is drafted.

## Workflow

1. Classify the request.
   Decide whether the Issue needs an Intake Issue, Plan Update, Detailed Plan
   Update, or Implementation Report.

2. Inspect the repo before asking questions.
   Resolve discoverable facts from docs, code, seed data, or existing Issues
   before blocking on user input.

   Perform the lightweight Grill-Me check defined by repository guidance. If
   planning would otherwise have to invent material target behavior, runtime
   responsibilities, boundaries, or ownership, return to Grill Me and
   `soundatlas-concept-work` before drafting a plan.

3. Separate intake from planning.
   When creating an Issue, use only the Intake shape: Task, Context, and
   Acceptance Criteria. Do not add speculative implementation steps, technical
   assumptions, or prematurely resolve open questions. State that the Intake
   Issue is not implementation-ready.

   If discovery reveals missing scope before planning, update the Intake body
   and add an `## Intake Revision` comment recording the date, previous scope,
   revised scope, and reason. Wording-only clarifications may proceed without a
   new review; material revisions require a fresh Grill-Me review before the
   Plan Update.

4. Draft or revise Issue planning content.
   Keep planning content in the GitHub Issue body or comments. Do not create
   local or repo-versioned implementation plan files.

   When an accepted concept exists, link to it and derive the plan from its
   target behavior, scope and non-goals, runtime responsibilities, boundaries
   and ownership, and resolved decisions. Do not copy the concept into the
   Plan Update.

   When creating an Issue, choose exactly one approved `priority:p*` label by
   reasoning from blocking level, MVP/release impact, risk reduction, and
   urgency. Use `priority:p2` only as the neutral fallback when `p0`, `p1`, or
   `p3` are not clearly justified. Briefly state the priority rationale.

   Inspect existing open milestones at Issue-creation time. Assign one only
   when completing the Issue directly advances the outcome stated by the
   milestone title and description. Shared labels, a related product area, or
   an indirect benefit are not sufficient. Leave partial, indirect, multiple,
   or ambiguous matches unassigned and explain why. Do not create, rename, or
   broaden milestones without explicit human approval. In the Issue-creation
   handoff, report the milestone decision and rationale alongside the priority
   rationale.

5. Keep the Issue decision-complete for implementation.
   For security, credentials, infrastructure, networking, workflow, UX,
   editorial, cross-cutting, user-visible, vague, or materially ambiguous work,
   require a recorded Grill-Me result before a Plan Update. Use a standalone
   `## Grill-Me Review` for material findings, decisions, blockers, or explicit
   standalone sessions. A clean check may be recorded inline in the Plan Update.
   Clearly trivial, local, low-risk work may use the direct path only when the
   lifecycle document permits that exception; workflow changes remain gated
   there.
   Make assumptions for low-risk implementation details. Stop for approval when
   uncertainty affects product intent, data shape, security, privacy, external
   API behavior, generated media review boundaries, historically sensitive
   claims, irreversible workflow behavior, or production stability.

   Treat a material Grill-Me record as complete only when it contains a
   `Stage`, an explicit `Decision` for every material `Finding`, and a `Next
   step`. Keep pending findings in the interactive conversation until the
   human confirms, defers, rejects, or blocks them. For multiple findings,
   require one numbered finding/decision pair per finding in the same
   consolidated `## Grill-Me Review` comment.

6. Preserve Acceptance Criteria history.
   If the plan changes the original criteria, include an `Acceptance Criteria
Changes` section instead of silently rewriting the meaning of the Issue.

7. Stop before implementation unless the user explicitly requests implementation
   with wording such as `implement issue #<number>` or the change qualifies for
   the direct path in `docs/github-issue-workflow.md`. Explicit wording does not
   bypass required review or planning gates.

8. Finalize one combined Implementation Report after review.
   For completed non-trivial Issue work, require
   `soundatlas-implementation-review` before the report is final. Include its
   Review Result in the same comment; do not create a separate routine review
   comment. If the review routes a required correction or material decision,
   keep the report unaccepted until the finding is resolved or explicitly
   reported as blocking.

   Run `python scripts/check_issue_completion.py report --file <report>` before
   treating the report as a completion candidate. A commit alone is not an
   Accepted report or a closure decision.

9. After implementation reporting, follow the post-commit lifecycle defined in
   `docs/github-issue-workflow.md`. This skill does not own commit
   authorization, completion comments, or Issue closure.

   Post-commit completion requires the local completion gate, one standard
   completion comment, and successful comment posting before closure. Keep an
   incomplete report or non-`Accepted` review open for correction.

## Issue Artifact Contracts

Use the canonical Intake, Plan Update, Detailed Plan Update, and
Implementation Report shapes in `docs/github-issue-workflow.md`. Use
`Requirements` only when complex product, API, data, security, or workflow
rules would otherwise be unclear.

## Planning Rules

- Keep GitHub Issues as the default source of truth for planning,
  implementation, and verification.
- Prefer `Task` over `Goal` for intake because SoundAtlas follow-up work often
  starts as a task, review, investigation, or decision.
- Keep Plan Updates concise by default; use Detailed Plan Updates only when
  implementation would otherwise need to rediscover decisions.
- Require user confirmation for material decisions about product behavior,
  scope, security, privacy, external APIs, editorial/source quality,
  irreversible workflow behavior, or production stability. Record low-risk
  assumptions in the Plan Update instead.
- Do not state `Open Questions: None` while a material decision remains
  unresolved.
- Do not define behavior outside the requested change.
- Do not describe completed non-trivial Issue work as accepted without a
  `soundatlas-implementation-review` result supported by proportionate evidence.
- Keep the Review Result inside the single Implementation Report comment. The
  review skill performs the comparison; this skill records the result.
- Do not fill a missing or contradictory material concept decision inside a
  Plan Update. Return it to Grill Me and concept work.
- Before producing a Plan Update for risk-flagged work, verify that the
  completed Grill-Me comment itself contains `Stage`, every material `Finding`
  with its `Decision`, and `Next step`. Do not treat a statement inside the
  Plan Update as a substitute for a missing human decision in the Grill-Me
  record.
- Reference an accepted concept instead of duplicating it across implementation
  Issues or plans.
- Prefer small, reviewable revisions over broad rewrites.
- Do not silently broaden an Intake. Split a separate deliverable, changed
  primary outcome, materially different domain/owner, or independently
  sequenced expansion into a linked Issue.
- After a Plan Update exists, record material scope changes under `Acceptance
  Criteria Changes` and rerun required review before implementation. After
  implementation begins, use a linked Issue for material expansion.
- For cross-cutting changes, plan in this order: data or schema impact, backend
  impact, frontend state impact, UX impact, tests or checks, docs or Issue
  updates.

## Output

Return the planning result in this order:

1. Issue action: create, update body, or add comment.
2. Assumptions.
3. Open questions, if any remain.
4. Draft Issue content or comment content.
5. Validation approach, when implementation is expected.
6. Next step: approve the Plan Update, request implementation with
   `implement issue #<number>`, or review the Implementation Report.
