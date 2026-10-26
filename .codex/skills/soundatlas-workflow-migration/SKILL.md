---
name: soundatlas-workflow-migration
description: Compose one approved SoundAtlas workflow migration slice from required capabilities, outcomes and constraints, preserving tracked authority, execution evidence, ordinary-tools usability and fail-closed stops. Temporary Milestone 9 skill for Issues #247–#251; not a general workflow replacement.
---

# SoundAtlas Workflow Migration

Use this temporary skill only for an approved migration child Issue #247,
#248, #249, #250, or #251. SoundAtlas defines required capabilities, outcomes
and domain constraints. The active environment chooses suitable providers,
tools, skills and delegation for the concrete task. Different methods may
satisfy the same requirements; procedural equivalence to a named Pane skill
is not required.

Use the existing [decision/planning requirements](../../../docs/workflow-registry.md#decision-and-planning-composition).
When a Pane mechanism is selected, apply the conditional #246 composition
contract in that registry, including its envelope, provenance, drift checks,
gap routing and fail-closed stops. This skill does not replace that authority,
generalize its provider mechanics or require Pane for ordinary work.

## Required context

Read current canonical records and tracked authorities before execution:

- the child Issue, accepted Plan, matching Proceed and applicable Human
  decisions;
- the accepted #200 Inventory and Migration Map and its atomic classification,
  with any linked prospective authority clarifications;
- the current registry and applicable #246 composition contract;
- `AGENTS.md`, `docs/github-issue-workflow.md` and every domain/validation
  authority named by the Plan;
- the exact write boundary, excluded scope, Proceed audit, allowed effects and
  stop routes; and
- the ordinary repository/GitHub tools and tracked non-Pane route.

Historical provider mappings are evidence, not a requirement to select those
providers. Preserve accepted classifications, domain responsibilities, gaps
and canonical authority; do not silently reinterpret a conflicting live rule.

## Supported migration themes

The supported input is exactly one child Issue and its applicable #200 rows:

| Issue | Migration theme | Required capability and retained constraints |
| --- | --- | --- |
| #247 | bounded decision/planning consolidation | Exploration, defect investigation, independent critique when required, planning and canonical composition; retain phase, Concept and Issue responsibilities. |
| #248 | implementation and review entrypoints | Scoped frontend/backend/docs implementation and evidence-based review; retain authority, validation, review outcomes and independence requirements. |
| #249 | deterministic test entrypoints | Focused deterministic test design/execution, levels, fixtures/mocks and environment evidence; experiments or journey QA cannot replace required coverage. |
| #250 | [commit and delivery entrypoints](../../../docs/workflow-registry.md#commit-and-delivery-composition) | Selective staging, commit/delivery evidence and handoff within exact Human authorization and Git/lifecycle integrity rules; see [delivery identity and partial outcomes](../../../docs/github-issue-workflow.md#delivery-identity-and-partial-outcomes). |
| #251 | domain and compatibility entrypoints | Domain work and compatibility/reference audits within existing editorial/data/UX contracts, Human checkpoints and publication boundaries. |

Do not accept an unsupported Issue, invent a theme or reclassify an atomic
#200 row. A material reclassification returns to #200/#201 planning.
GAP-1..3 remain open for #202 evidence; naming capabilities does not close them.

## Composition procedure

1. Extract and identify the applicable SoundAtlas correctness requirements and
   their tracked owners before reducing or replacing procedure. Verify current
   canonical scope, Plan/Proceed, Human gates, exact boundary, required
   validation, allowed effects, rollback and ordinary-tools route.
2. The active environment selects capabilities by suitability for the concrete
   task, required outcome and applicable constraints. Discovery, technical
   provider/tool/skill selection and delegation are execution concerns, not
   project workflow routes. Ordinary repository/GitHub tools may fulfil the
   requirements. Apply #246's existing guarantees when Pane is selected.
3. Use or delegate only the suitable generic procedure within those conditions.
   Capture actual execution evidence and stop outcomes. Do not copy generic
   provider procedure here, fork Pane locally or substitute runtime artifacts
   for SoundAtlas authority.
4. Reconcile durable results into the canonical Issue Plan, report and other
   SoundAtlas-owned records required by the lifecycle. Local runtime plans,
   generated briefs, Session text and temporary state remain advisory.
5. Apply only the current Proceed boundary. Changed authority, a new path,
   reclassification or material scope drift stops mutation and returns to
   planning for a revised confirmed Plan, Proceed and readiness.

## Per-slice migration record

Return stage-appropriate evidence in the existing child Issue lifecycle:

- Issue, stage, accepted #200 classification and preserved authorities;
- repository revision, branch/worktree and actual selected runtime, tools,
  skills and invoked procedure, with applicable versions/source revision or
  content digest; version equality alone is not provenance;
- concrete Pane/RunPane and skill-bundle provenance when Pane is actually used,
  without requiring fabricated Pane evidence for ordinary-tools execution;
- current Plan/Proceed links, exact boundary, exclusions, Human gates, allowed
  effects and ordinary-tools route;
- changed authorities/entrypoints, retained gaps/overrides, performed work,
  validation commands/results and unavailable-environment evidence;
- unmet capability before invocation versus started/partial failure, last
  verified state, observed changed paths/effects, incomplete work, unresolved
  decisions and recovery owner;
- rollback restoring only the reviewed prior hunks/route while preserving user
  work and canonical history; and
- #202 representative-evaluation handoff with the actual provider/provenance,
  evidence limits and required Pane/non-Pane outcomes.

These are execution records, not a new Plan, approval, workflow state or
authority. Structural checks and document scenarios do not prove parity.

## Fail-closed stops and destinations

Stop the affected gated work and report the exact condition:

- Missing required Issue, accepted #200 row, applicable #246 composition
  contract, authority, Plan/Proceed, Human decision or validation environment:
  return to Issue Planning or the owning Human gate.
- Unresolved material decision, contradictory authorities or unclear owner:
  return to Grill Me, Concept Work or the named authority owner.
- Required capability/evidence genuinely unmet before invocation: report the
  missing outcome and affected gate. Absence of a named Pane skill alone does
  not establish absence of the generic capability. For a selected Pane route,
  preserve #246's missing-capability, drift and gap-routing requirements; do
  not emulate or fork the provider.
- Started invocation fails, is interrupted or partial: preserve Issue records
  and user work; report last verified revision, changed paths, observed effects
  and incomplete work. Recheck authority/boundary before resumption. Do not
  assume a clean fallback, silently repeat effects or infer completion.
- Stale/mismatched authority, revision or boundary, unsupported theme or
  out-of-bound behavior: leave excluded work untouched and return to planning
  or a linked Intake as applicable.
- Required tool, service, permission, credential boundary or validation
  unavailable/failing: report the exact prerequisite or correction route,
  without weaker evidence or a completion claim.
- Provider defaults imply push, PR, integration, merge, publication, deployment,
  release, Project mutation, closure or retirement without exact authorization:
  suppress that effect and return to its SoundAtlas/Human gate.
- Retirement before dependent work and accepted #202 evidence: retain the skill
  and route the decision to #203.

The runtime owns discovery, retry, delegation and recovery mechanics. These
requirements constrain authority, evidence and allowed outcomes; they prescribe
no provider-specific fallback.

## Non-Pane path

The skill is optional. A contributor without Pane starts at `AGENTS.md`,
follows the registry to the lifecycle/current Issue, reads the same authorities
and exact boundary, works with ordinary repository/GitHub tools, and records
actual validation, stop outcomes, rollback and execution evidence.
Equivalent correctness and evidence are required; identical procedure, Pane
installation, cached skills and Session state are not.

## Sunset

This temporary runner cannot authorize commits, pushes, PR creation,
integration, merge, publication, deployment, release, Project mutation, closure
or retirement. Do not make it a dependency of ordinary SoundAtlas work.
Issue #203 owns removal or reduction after #247–#251 no longer depend on it and
#202 accepts representative evidence for affected rows. Only a Human-confirmed
#203 Plan and accepted report may retire it.
