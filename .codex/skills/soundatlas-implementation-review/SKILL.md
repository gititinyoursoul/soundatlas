---
name: soundatlas-implementation-review
description: Review completed SoundAtlas Issue implementations against their accepted scope, concept when present, plan, actual diff, proportional evidence, and current-state documentation; classify and route findings without editing artifacts. Use before accepting completed non-trivial Issue work, when explicitly requested, or during implementation when drift, risk, or a new material constraint appears; skip clearly trivial, local, low-risk changes.
---

# SoundAtlas Implementation Review

Determine whether a named local Issue commit or commit range matches its
accepted target and has enough evidence to proceed to human review before push.

This retained SoundAtlas override supplies comparison requirements and results;
the environment selects suitable generic review mechanics. Use the registry's
[implementation and review composition](../../../docs/workflow-registry.md#implementation-and-review-composition)
for capability inputs, precedence, allowed effects and stop routes. Ordinary
repository/GitHub tools may satisfy the contract; when Pane is selected, apply
its existing composition contract there without copying provider procedure.

## Required context

Read the smallest available set that establishes the target and result:

- `AGENTS.md` and the active workflow guidance;
- the originating GitHub Issue, including confirmed revisions and decisions;
- the accepted `## Concept` comment or authoritative concept document, when one
  exists;
- the approved Plan Update or Detailed Plan Update, when one was required;
- the matching `## Proceed to Implementation` record when the current workflow
  required one;
- the Plan's planned write boundary and the Proceed record's audited derived
  files, when the work is non-trivial;
- the exact named committed base/head or explicit commit range, its actual diff, and
  Issue-relevant working-tree state;
- validation results and other supplied evidence; and
- current-state documentation affected by the implementation.

Do not require retroactive concept work merely because an Issue has no concept
artifact. Inspect discoverable evidence before declaring it missing.

## Comparison requirements

Review completed non-trivial Issue work before acceptance; review work in
progress only for drift, risk or a new material constraint. Skip clearly
trivial, local, low-risk changes unless the Human requests review.

Apply the registry's authority precedence: current tracked policy constrains
the Issue; the Issue owns scope/criteria, the Concept owns target behavior when
present, the Plan owns tasks/planned validation, and the matching Proceed
records authorization for that exact Plan. Proceed is not completed-work
approval. Contradictions are findings, not permission to choose a winner.

The comparison must cover material target behaviors, runtime responsibilities,
criteria, Plan completion, non-goals, implementation constraints, scope drift,
unapproved behavior, unrelated changes and documentation claims/impact. Link
each material claim to credible proportional evidence. For non-trivial
user-visible frontend work, include recorded desktop rules, UI-quality findings,
planned runtime evidence and dispositions. Missing or failing evidence is a
finding, not assumed success. Classify and route every material finding below;
return the Review Result to the single Implementation Report, without a
separate routine review comment.

## Reviewer identity and revision evidence

Use `Implementing agent` for self-review. Independent review is appropriate
when requested or materially justified by risk, ambiguity, architecture change
or uncertainty, but its claim requires actual separation evidence. Consume the
bounded [#218 handoff](https://github.com/gititinyoursoul/soundatlas/issues/218#issuecomment-6402197893):

- Identify actual implementing and reviewing clients/processes and how their
  separation was corroborated by actual dispatch or process identity.
- Link the reviewer's own returned comparison and outcome to the requested
  exact base/head or range, identifying evidence inspected and limits.
- Record missing provenance and shared-worktree limits. A role label,
  fresh-tab assertion, model choice or shared Session alone proves no
  separation. Shared-worktree read-only instructions imply no technical write
  isolation; do not assert a security boundary or invent a required
  platform-specific identifier.
- A changed head needs current review evidence. Stale acceptance, a new label
  or a report correction cannot transfer an old comparison to a changed range.

Missing separation/provenance withholds the independent claim. Accurate
implementing-agent wording is allowed only when that mode is otherwise
permitted; an independently required gate remains unmet without evidence.
Generic dispatch and enforcement remain runtime/provider responsibilities.

For non-trivial user-visible frontend work, treat an unresolved material
hierarchy, copy, density, styleguide, accessibility, or interaction finding—or
missing proportionate runtime evidence for a visual claim—as a finding that
prevents an `Accepted` verdict. Route a fix to implementation, unsupported
evidence to validation work, and a material target ambiguity to Grill Me.

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
- **Out-of-boundary change:** leave the path unchanged where possible and route
  the required work to a linked Intake Issue; do not treat a direct consumer as
  authorized unless it appears in the Proceed record's audit.
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
review result in the final Implementation Report. Human review of the committed
diff and an
explicit push request remain separate.

## Review Result

Return this section for inclusion in the single Implementation Report comment:

```md
## Review Result

- Verdict: Accepted | Correction required | Return to planning | Return to concept | Needs decision
- Reviewer mode: Implementing agent | Independent review
- Reviewer evidence: <actual implementer/reviewer identities, separation evidence or limits, exact reviewed range and returned comparison>
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
completion lifecycle must also verify that the reviewed change was pushed, its
Issue-relevant working-tree state, and the single standard completion comment
through the workflow gate in `docs/github-issue-workflow.md`. A local commit or
a posted report must never be treated as acceptance by itself.
