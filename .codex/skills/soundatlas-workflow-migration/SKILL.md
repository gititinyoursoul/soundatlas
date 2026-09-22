---
name: soundatlas-workflow-migration
description: Compose one approved SoundAtlas workflow migration slice with the Pane–SoundAtlas contract, preserving tracked authority, bounded evidence, non-Pane parity, and fail-closed stops. Temporary Milestone 9 skill for Issues #247–#251; not a general workflow replacement.
---

# SoundAtlas Workflow Migration

Use this temporary skill only for an approved migration child Issue #247,
#248, #249, #250, or #251. It operationalizes the tracked Pane–SoundAtlas
composition contract in `docs/workflow-registry.md`; it does not create a
second contract, replace a SoundAtlas authority, or become a required path for
contributors who do not use Pane.

## Required context

Read the current canonical records and tracked authorities before invoking any
generic mechanism:

- the migration child Issue, its accepted Plan, matching Proceed record, and
  applicable Human decisions;
- the accepted #200 Inventory and Migration Map and its atomic classification;
- the accepted #246 composition contract and the current
  `docs/workflow-registry.md`;
- `AGENTS.md`, `docs/github-issue-workflow.md`, and every named domain or
  validation authority in the current Plan;
- the Plan's exact write boundary, excluded scope, and Proceed audit; and
- the equivalent non-Pane commands and tracked route.

The run must also identify the repository revision, branch/worktree, Issue URL,
requested stage, exact Pane and RunPane versions, selected capability, skill
bundle provenance or content digest, allowed external effects, and stop routes.
Version equality alone is not provenance.

## Supported migration themes

The supported input is exactly one of these child Issues and its applicable
#200 rows:

| Issue | Migration theme | Generic procedure is delegated to Pane |
| --- | --- | --- |
| #247 | discussion, planning, and decision/planning entrypoints | `discussion`, `investigate`, `reality-check`, `create-plan`, `plan-reviewer` |
| #248 | implementation and review entrypoints | `implement`, `implementer`, `implementation-reviewer` |
| #249 | deterministic test entrypoints | `smallest-test`, `pr-test-automation` |
| #250 | commit and delivery entrypoints | `commit`, `handoff`, `prepare-pr` only where separately authorized |
| #251 | domain and compatibility entrypoints | the applicable named Pane capability from the accepted #200 row |

Do not accept an unsupported Issue, invent a theme, or reclassify an atomic
#200 row. Route a material reclassification to #200/#201 planning.

## Composition procedure

1. Assemble the #246 composition envelope for the requested stage. Confirm the
   canonical Issue scope, current Plan/Proceed boundary, tracked authorities,
   Human gates, validation, rollback, allowed effects, and non-Pane route.
2. Compare the selected Pane capability and skill-bundle evidence with the
   accepted row. If capability identity, inputs, outputs, approval behavior,
   external effects, or stop behavior has materially drifted, stop before use
   and return to planning/evaluation.
3. Delegate only the generic working procedure to the named Pane capability.
   Pass the SoundAtlas envelope to it and capture its returned evidence and
   stop condition. Do not copy Pane procedure into this skill or fork a
   repository-local Pane workflow.
4. Reconcile durable results into the canonical Issue Plan, report, and other
   SoundAtlas-owned records required by the lifecycle. Local Pane plans,
   generated briefs, Session text, and temporary runner state remain advisory.
5. Apply only the current Proceed write boundary. A new path, changed
   authority, reclassification, or material scope change stops the run and
   returns to Issue Planning for a revised Plan and Proceed record.

## Per-slice migration record

Produce one evidence record for the child Issue containing:

- Issue, stage, accepted #200 classification, and preserved SoundAtlas
  authorities;
- selected Pane capability, Pane/RunPane versions, bundle provenance/digest,
  and repository/worktree revision;
- current Plan/Proceed URLs, exact write boundary, excluded scope, Human gates,
  allowed effects, and equivalent non-Pane route;
- changed authorities and entrypoints, retained gaps and intentional
  overrides, and the delegated procedure used;
- validation commands, results, unavailable-environment evidence, unresolved
  decisions, and the exact stop state if the run did not complete;
- rollback path that restores the prior tracked route without discarding Issue
  records or user work; and
- #202 representative-evaluation handoff, including the evidence needed to
  compare Pane and non-Pane outcomes.

The record is evidence for the existing Issue lifecycle. It is not a new Plan,
approval, workflow state, Project status, or authority.

## Fail-closed stops and destinations

Stop repository mutation and record the exact condition when any of the
following occurs:

- missing Issue, accepted #200 row, #246 contract, required authority, Plan,
  Proceed, Human decision, or validation environment → Issue Planning or the
  owning Human gate;
- unresolved material decision, contradictory authorities, or unclear owner →
  Grill Me, Concept Work, or the named authority owner;
- missing, renamed, or materially changed Pane capability → retain the
  non-Pane path and route a separate Pane capability ticket; never create a
  local fork;
- stale Plan/Proceed, changed revision, boundary drift, or unsupported theme →
  return to planning and obtain a fresh confirmed Plan/Proceed;
- requested behavior outside the boundary → leave it untouched and route a
  linked Intake Issue;
- unavailable required tool, permission, credential boundary, or failed
  validation → report the exact prerequisite or correction route without
  substituting weaker evidence;
- an implied Pane default requests push, PR creation, merge, publication,
  deployment, release, Project mutation, closure, or retirement without its
  separate authorization → suppress that effect and return to the exact
  SoundAtlas/Human gate; or
- retirement is requested before dependent work and accepted #202 evidence →
  retain the skill and route the decision to #203.

## Non-Pane path

The skill is optional. A contributor without Pane starts at `AGENTS.md`, follows
the registry to the lifecycle and current Issue, reads the same authorities and
write boundary, performs the work with ordinary repository tools, and records
the same validation, stop outcomes, rollback, provenance, and #202 evidence.
Equivalent correctness and evidence are required; Pane-specific procedure and
Session state are not.

## Sunset

This temporary runner cannot authorize commits, pushes, PR creation, merge,
publication, deployment, release, Project mutation, closure, or retirement.
It is a Milestone 9 runner; do not make it a dependency of ordinary
SoundAtlas work. Issue #203 owns removal or reduction after #247–#251 no longer
depend on it and #202 has accepted representative evidence for the affected
rows. Only a Human-confirmed #203 Plan and accepted report may retire it.
