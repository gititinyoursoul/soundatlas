---
name: soundatlas-implementation-review
description: Review completed SoundAtlas Issue implementations against their accepted scope, concept when present, plan, actual diff, proportional evidence, and current-state documentation; classify and route findings without editing artifacts. Use before accepting completed non-trivial Issue work, when explicitly requested, or during implementation when drift, risk, or a new material constraint appears; skip clearly trivial, local, low-risk changes.
---

# SoundAtlas Implementation Review

Determine whether implemented work matches its accepted target and has enough
evidence to proceed to human diff review.

## Required context

Read the smallest available set that establishes the target and result:

- `AGENTS.md` and the active workflow guidance;
- the originating GitHub Issue, including confirmed revisions and decisions;
- the accepted `## Concept` comment or authoritative concept document, when one
  exists;
- the approved Plan Update or Detailed Plan Update, when one was required;
- the matching `## Proceed to Implementation` record when the current workflow
  required one;
- the actual diff and Issue-relevant working-tree state;
- validation results and other supplied evidence; and
- current-state documentation affected by the implementation.

Do not require retroactive concept work merely because an Issue has no concept
artifact. Inspect discoverable evidence before declaring it missing.

## Workflow

1. Confirm the trigger.
   Review completed non-trivial Issue work before it is accepted. Review work in
   progress only when drift, risk, or a new material constraint appears. Skip a
   clearly trivial, local, low-risk change unless the human requests review.
2. Record reviewer mode.
   Use `implementing agent` by default. Use `independent review` when the human
   requests it or when risk, ambiguity, architecture change, or uncertainty
   materially justifies it. Do not imply independence when self-reviewing.
3. Establish the available authorities.
   Treat the Issue as the scope and acceptance-criteria authority, the concept
   as the target-behavior authority when present, and the plan as the authority
   for implementation tasks and planned validation. Treat the Proceed record as
   evidence of Human authorization for that exact Plan, not approval of the
   completed implementation. Treat contradictions as findings instead of
   silently choosing a winner.
4. Identify material claims.
   List the target behaviors, runtime responsibilities, acceptance criteria,
   non-goals, and material documentation claims the implementation must support.
5. Assess evidence proportionately.
   Map each material claim to credible evidence. Use existing automated checks
   when they establish the claim. Inspect or request focused runtime,
   integration, visual, or manual evidence only where ordinary checks leave a
   material gap. A missing or failing check is evidence of a finding, not a
   reason to assume success.
6. Compare the implementation.
   Inspect target coverage, plan completion, unapproved behavior, non-goal
   preservation, scope drift, implementation constraints, unrelated changes,
   and documentation impact.
7. Classify and route every material finding.
8. Produce the Review Result for the existing Implementation Report. Do not
   create a separate routine review comment.

## Evidence rules

- Prefer the smallest direct evidence that supports the claim.
- Do not demand every evidence type for every change.
- Treat tests as sufficient only for behavior they actually exercise.
- Use runtime or integration evidence for responsibilities that isolated checks
  cannot establish.
- Use visual or manual evidence only when deterministic checks do not establish
  the relevant interaction or presentation.
- State an evidence gap explicitly; do not replace evidence with confidence.

## Finding routes

Use these categories and destinations:

- **Implementation defect:** return accepted but incorrectly implemented
  behavior to implementation.
- **Insufficient evidence:** return the unsupported claim to implementation or
  validation work.
- **Incomplete plan:** return target behavior omitted by the plan to
  implementation planning.
- **Incomplete or conflicting concept:** return a missing or contradictory
  target to concept work.
- **Unresolved material decision:** return the decision to Grill Me.
- **Stale documentation:** route the mismatch to documentation work within the
  approved scope or recommend a follow-up.
- **Unrelated change:** preserve the user-owned change and exclude it from the
  Issue implementation and commit.
- **Optional enhancement:** recommend follow-up work without creating an Issue
  automatically.
- **Accepted implementation:** proceed only when no material finding remains and
  the target has proportionate evidence.

When several findings exist, report each category and route. Do not broaden the
active Issue to absorb an optional enhancement.

## Read-only boundary

This skill may inspect artifacts, assess evidence, run or request focused
non-destructive checks, classify findings, and recommend routing.

Do not use this skill to:

- edit code, data, documentation, concepts, plans, or Issue scope;
- fix findings;
- resolve material decisions;
- create follow-up Issues automatically;
- create or manage `stage:*` or `status:*` labels;
- commit or close an Issue; or
- claim human approval.

The surrounding workflow performs authorized corrections. Grill Me handles
material human decisions. `soundatlas-issue-planning` records the
review result in the final Implementation Report. Human diff review and an
explicit commit request remain separate.

## Review Result

Return this section for inclusion in the single Implementation Report comment:

```md
## Review Result

- Verdict: Accepted | Correction required | Return to planning | Return to concept | Needs decision
- Reviewer mode: Implementing agent | Independent review
- Compared artifacts: <artifacts actually reviewed>
- Evidence coverage: <material claims and supporting evidence or gaps>
- Findings and routing: None | <category, evidence, affected responsibility, destination>
- Documentation impact: Current | Corrected within scope | Routed
```

Use `Accepted` only when no material finding remains. If correction or a
decision is required, return the result to the named workflow destination and
do not describe the implementation as accepted. Finalize the Implementation
Report after required findings are resolved or explicitly reported as blocking.

An `Accepted` result is necessary but not sufficient for Issue closure. The
completion lifecycle must also verify the committed change, Issue-relevant
working-tree state, and the single standard completion comment through the
workflow gate in `docs/github-issue-workflow.md`. A commit or a posted report
must never be treated as acceptance by itself.
