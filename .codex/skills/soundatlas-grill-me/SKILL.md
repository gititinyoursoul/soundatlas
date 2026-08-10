---
name: soundatlas-grill-me
description: Challenge SoundAtlas ideas, Intake Issues, concepts, design boundaries, plans, editorial or UX artifacts, implementation work, and workflow changes with phase-aware critique and Materiality routing. Validate conceptual coherence before implementation planning and detect premature implementation drift. Use when the human requests Grill Me or a named Grill-Me Review Mode, or when repository guidance requires a lightweight check for non-trivial, vague, risky, cross-cutting, drift-prone, or editorially sensitive work.
---

# SoundAtlas Grill Me

Challenge the active artifact without crossing into decisions owned by a later
workflow stage. Keep critique read-only; return confirmed decisions or clean
results to the workflow that owns the artifact.

## Required context

Inspect the smallest useful context before reviewing:

- the active artifact and workflow stage;
- the related GitHub Issue, Concept, Plan Update, implementation diff, editorial
  artifact, UX proposal, or workflow source;
- the desired outcome, constraints, non-goals, and Human Review boundaries;
- relevant repository evidence that can resolve discoverable facts, including
  contrary or historical evidence rather than only supporting examples; and
- validation evidence and current-state documentation for implementation work.

Do not ask the Human for facts that repository inspection can establish.

## Core boundary

Critique first. Do not edit code, data, Documentation, prompts, Skills, Issues,
or normative artifacts; implement changes; publish Content; commit; or mark work
approved from this Skill alone.

Grill Me challenges the active artifact but does not own it:

- the Issue owns why the work is needed and its accepted scope;
- `soundatlas-concept-work` owns synthesis of confirmed target behavior when
  Concept Work is needed;
- Planning owns how an accepted target will be implemented;
- implementation owns authorized changes;
- current-state Documentation owns descriptions of implemented behavior;
- `soundatlas-implementation-review` owns completed-implementation comparison
  and evidence assessment; and
- `docs/github-issue-workflow.md` owns lifecycle timing and the canonical
  completed Grill-Me record.

Concept Work remains conditional. Do not require it when an Intake is already
decision-complete and Planning can choose Design and Implementation mechanisms
without inventing material target behavior, semantics, scope, Ownership,
lifecycle, responsibilities, Human/Agent authority, compatibility, or
Boundaries.

Implementability is not evidence that a Concept is coherent. A schema, API,
class, workflow task, or storage mechanism can be invented for an ambiguous
idea. Require the intended meaning and boundaries to stand on their own before
using feasibility as supporting evidence.

A Grill-Me `Next step` routes the reviewed artifact; it does not confirm a Plan
or authorize implementation. The separate lifecycle record in
`docs/github-issue-workflow.md` owns that Human go-ahead.

## Stage model

Keep these stages distinct:

1. **Problem:** Establish the observed need, affected Human or user, evidence,
   and desired outcome without assuming a solution.
2. **Concept:** Define what the proposed capability means and what behavior it
   must provide.
3. **Design boundaries:** Define responsibilities, authority, lifecycle,
   invariants, and interactions with neighboring concepts without choosing a
   technical representation.
4. **Design validation:** Challenge the Concept and its boundaries with
   counterexamples, failure cases, transitions, and conflicting assumptions.
5. **Implementation planning:** Choose representations, mechanisms, affected
   surfaces, sequencing, tasks, and validation.
6. **Implementation:** Make and verify the authorized changes.

Grill Me primarily works in Concept, Design boundaries, and Design validation.
It may route backward to Problem or forward to Implementation planning, but it
must not collapse the stages. `Design boundaries` here means conceptual
responsibility and interaction boundaries, not schemas, APIs, modules, storage,
or other technical design.

## Review workflow

1. Identify the active artifact, its actual stage, and the smallest applicable
   Review Mode. Do not infer maturity from the artifact's title or detail.
2. Inspect relevant repository evidence before forming findings. Treat code and
   Documentation as evidence of the current system, not proof that its design is
   correct or should be preserved.
3. Separate observed facts, assumptions, solution hypotheses, `Unknown`,
   `Evidence Gap`, recommendations, and Human Decisions.
4. Restate the candidate Concept in mechanism-neutral terms. If this cannot be
   done without inventing meaning, record the conceptual gap.
5. Classify each question or concern by stage before answering it. Abstract a
   later-stage concern to the underlying current-stage requirement only when it
   exposes a material gap.
6. Apply the shared checks and only the Mode-Specific Focus appropriate to the
   active stage. Challenge accepted-looking statements as claims to validate.
7. Detect implementation drift. Stop expanding mechanisms, record their
   implications for later, and return to the unresolved Concept or boundary.
8. Classify each eligible finding by severity and Materiality. Route gaps and
   decisions without silently resolving them in the wrong stage.
9. Give the stage-specific readiness judgment. Continue immediately after a
   clean lightweight check; use the one-finding flow when a material Human
   Decision is required.
10. Return the result to the owning workflow artifact. Do not modify that
    artifact from Grill Me alone.

## Shared checks

Apply only concerns that genuinely cross stages:

- observed facts versus assumptions or hypotheses;
- unclear outcomes, scope, non-goals, or Human Review boundaries;
- contradictions, hidden dependencies, premature automation, or speculative
  future scope;
- editorial, Source, media, rights, historical-claim, security, privacy, or
  production-stability risk when relevant;
- drift between the active artifact and its accepted upstream authority;
- evidence sufficient for the current decision; and
- whether the finding belongs in the current stage or must be routed elsewhere.

Do not apply Planning or implementation criteria to an Idea or Intake merely
because those criteria exist later in the workflow.

Repository evidence may establish current behavior, terminology, compatibility
constraints, and prior decisions. It does not settle whether those choices are
coherent with the current problem and accepted intent. Name the inference when
using current implementation or Documentation to support a design conclusion,
and keep contradictory evidence visible.

## Concept and implementation boundary

Classify questions before proposing answers:

- **Problem:** Does the need, evidence, affected party, or desired outcome
  remain unclear or solution-led?
- **Concept:** Would the answer change intended meaning, target behavior, scope,
  lifecycle, invariants, failure semantics, compatibility, or Human/Agent
  authority?
- **Design boundary:** Would the answer change which responsibility belongs to
  which concept or actor, where that responsibility stops, or how neighboring
  concepts interact?
- **Implementation planning:** Does the answer choose concrete schemas, fields,
  cardinality, enums, algorithms, normalization, storage, APIs, classes,
  modules, files, migrations, components, execution mechanics, sequencing,
  validation tooling, or task breakdowns?
- **Implementation:** Does the answer make or verify an authorized change?

Keep Concept and Design-boundary questions in the design grill. Park
Implementation-planning questions unless a technical constraint exposes an
underlying conceptual consequence. In that case, state the consequence without
selecting the mechanism.

Use this test: if materially different technical mechanisms could satisfy the
same answer without changing intended behavior or responsibility, the mechanism
belongs to Implementation planning. If choosing among the mechanisms would
change meaning, Ownership, lifecycle, an invariant, failure semantics, or a
neighboring boundary, expose that unresolved conceptual choice first.

Implementation drift is likely when:

- nouns in the discussion turn into tables, fields, classes, components, or
  endpoints before their meaning and responsibility are stable;
- a `what`, `why`, `who owns`, `when`, or `what must remain true` question is
  replaced by `where stored`, `which API`, or `what task`;
- a mechanism is offered as the answer to an unresolved invariant or failure
  case;
- a task list makes unresolved design choices look decided; or
- existing code or Documentation is cited as proof rather than current-state
  evidence.

When drift occurs, stop the mechanism-level branch. Record a one-line `Parked
implementation implication`, recover the underlying Concept or Design-boundary
question, and continue only at that level. Do not expand the parked item.

Examples:

- `What must a Research Run preserve historically?` is a Concept question.
  `Which database fields store that snapshot?` is an Implementation-planning
  question to park.
- `Who may publish a route, and what remains true after publication?` is a
  Concept and Design-boundary question. `Which endpoint performs publication?`
  belongs to Implementation planning.
- `What should a reader observe when source evidence is insufficient?` is a
  Concept question. `Which response code or UI component represents it?` belongs
  to Implementation planning.

## Review Modes

Use the smallest mode that fits the active artifact.

### Idea Grill

Test whether an idea is worth pursuing. Focus on:

- observed problem or opportunity;
- affected Human or user;
- evidence and Evidence Gaps;
- assumptions and contradictions;
- desired outcome and why it matters;
- proposed solutions as hypotheses, not requirements; and
- unresolved product, editorial, Source, or domain decisions.

Do not define implementation architecture, APIs, schemas, files, modules,
components, migrations, sequencing, or technical tasks. Surface a technical
constraint only when it materially challenges the idea, then record it for
later validation.

### Issue Grill

Stress-test an Intake Issue or problem statement. Focus on:

- whether Task, Context, and Acceptance Criteria describe the problem and
  observable outcome;
- facts, assumptions, evidence, Unknowns, and Evidence Gaps;
- scope, non-goals, affected domain, and Human decision boundaries;
- solution language that should remain a hypothesis;
- missing product, editorial, Source, or workflow decisions; and
- whether the Intake is decision-complete enough for Planning or needs Concept
  Work.

Do not turn the Intake into an implementation Plan or select architecture,
APIs, schemas, files, components, migrations, sequencing, or technical tasks.
Surface material technical constraints without resolving them prematurely.

### Concept Grill

Validate the Concept and its Design boundaries. Challenge:

- **Terminology and identity:** Are core terms defined consistently? Can two
  participants use the same term while meaning materially different things?
- **Responsibilities and authority:** What must happen, who or what is
  responsible, who may decide, and what is explicitly not that responsibility?
- **Boundaries and Ownership:** Where does each responsibility begin and end?
  What enters or leaves the boundary, and which neighboring concept owns the
  remainder?
- **Lifecycle and transitions:** What brings the concept into relevance, what
  materially changes over its life, what must be preserved historically, and
  when does it cease or become immutable?
- **Invariants:** What must remain true across valid states and transitions,
  independent of implementation?
- **Failure and incomplete cases:** What is the intended outcome when work is
  rejected, interrupted, partial, stale, contradictory, or cannot complete?
  Who retains authority to recover, defer, or stop?
- **Neighbor interactions:** Do adjacent concepts duplicate responsibility,
  create circular Ownership, depend on contradictory terminology, or leave a
  gap between boundaries?
- **Scope and fitness:** Are target behavior, non-goals, compatibility,
  conflicts with normative sources, and lean MVP fit explicit?

Use counterexamples and at least one materially plausible failure or boundary
case when they can change the readiness judgment. Do not enumerate theoretical
edge cases that cannot affect implementation choices or observable behavior.

Challenge existing decisions as claims, including decisions embodied in code
or Documentation. Preserve accepted constraints, but do not treat age,
implementation effort, or existing structure as evidence that the underlying
Concept is correct.

Present only Problem, Concept, and Design-boundary concerns. When an
Implementation-planning concern reveals a conceptual gap, state the underlying
requirement without prescribing the satisfying mechanism. Record only the
implementation topic under `Parked implementation implications` and do not
elaborate it.

Judge readiness as follows:

- **Concept requires more design work:** A material unresolved question could
  change target meaning or behavior, responsibility or authority, lifecycle,
  an invariant, failure semantics, compatibility, a neighboring boundary, or
  MVP scope. State each unresolved conceptual question explicitly.
- **Concept is sufficiently defined for implementation planning:** Planning can
  choose representations, mechanisms, sequencing, and tasks without inventing
  any of those material decisions. List non-blocking implementation implications
  as parked rather than resolving them.

Do not demand theoretical completeness. A bounded assumption, rare edge case,
or unknown is non-blocking when different answers would not materially change
the accepted Concept or the implementation plan. Remaining representation and
mechanism choices are expected inputs to Planning, not evidence that the
Concept is incomplete.

Before reusing an existing Concept for Planning or renewed implementation,
perform focused Concept revalidation when:

- the Human reports that the same conceptual problem continues;
- a later decision changes material target behavior, semantics, scope,
  Ownership, lifecycle, responsibilities, failure behavior, compatibility, or
  Boundaries;
- repeated fixes within one responsibility boundary suggest that the boundary
  itself is underspecified; or
- downstream rejection may indicate semantic or stage-boundary drift.

Distinguish a clear local implementation omission from evidence that the
Concept may be insufficient. Revalidation concludes either that the existing
Concept remains sufficient, with evidence, or that clarification and Concept
Work are required. Use the existing Grill-Me recording route; do not introduce
a new stage, status, or approval gate.

### Plan Grill

Challenge:

- coverage of the accepted Issue and Concept when present;
- mapping of runtime responsibilities to implementation work;
- sequencing, dependencies, data or schema impact, backend impact, frontend
  state, UX, tests, and Documentation;
- validation that proves the intended behavior;
- hidden or unapproved scope; and
- tasks that are small and reviewable.

Return to Concept when the Plan exposes a missing material target decision.

### Editorial Grill

Review route briefs, research dossiers, Candidate Content, Sources, media
plans, seed-promotion readiness, composition decisions, and Publication
boundaries. Keep Agent recommendations advisory and preserve final historical,
Source, media, and Publication judgment for the Human.

### UX Grill

Review UX findings, flows, interface text, density, accessibility, state and
error behavior, responsive behavior, and the proposed UX slice. Stop at
findings and a reviewable proposal unless implementation is separately
authorized.

### Implementation Readiness Grill

Check that the approved Issue, required confirmed Grill-Me decisions, optional
Concept when needed, current Plan Update, matching `## Proceed to
Implementation`, blocking-question resolution, and passing mechanical readiness
validation are present. Keep semantic Materiality assessment in this Skill and
deterministic artifact validation in `scripts/check_issue_readiness.py`.

### Implementation Grill

Challenge work in progress for:

- alignment with the accepted Issue, Concept, and Plan;
- unrecorded design changes caused by technical constraints;
- complexity or workarounds hiding a conceptual problem;
- unrelated files or responsibilities;
- validation coverage; and
- whether work should continue or return to Concept or Planning.

### Implementation Review Grill

Use `soundatlas-implementation-review` for routine completed-implementation
comparison, evidence assessment, finding classification, and routing. Use this
mode only for a material decision or ambiguity returned by that Skill. Do not
repeat the complete implementation review or fix the implementation from this
mode.

## Unknown and Evidence Gap routing

Use `Unknown` when the answer or current behavior is not established. Use
`Evidence Gap` when evidence is insufficient to support a claim or decision.
Neither classification automatically requires a Human Decision.

First inspect discoverable evidence. Then route by Materiality:

- **Non-material:** Record the gap or a bounded assumption and continue when it
  cannot change product intent, accepted scope, target behavior, data shape,
  editorial or Source quality, security, privacy, external API behavior,
  irreversible workflow behavior, Publication, or production stability.
- **Material:** Route to Investigation or Human Clarification and block only the
  affected decision or workflow transition until the gap is resolved or the
  Human explicitly defers it.

Do not convert missing evidence into an invented answer, recommendation, or
confirmed decision.

For Concept Grill, a material change to data concerns its meaning, Ownership,
or required representational capability. Concrete schema shape, cardinality,
normalization, fields, and storage remain Design or Implementation concerns
unless they expose one of those conceptual consequences.

## Lightweight and interactive review

Apply a lightweight Grill-Me check at the transitions required by
`docs/github-issue-workflow.md`. If there is no material finding, continue the
authorized workflow without starting an interactive session. Mention the clean
check only when it improves the handoff.

When material findings exist, briefly state that review is needed. Present one
dependent finding at a time and pause for Human confirmation. An approximate
finding count is optional and never a target. Batch independent factual
findings only when they do not require separate Human Decisions.

Use this shape for a material interactive finding:

```md
## Current Assessment

Proceeding | Needs revision | Blocked | Return to concept | Return to planning

## Finding <n>

- Severity: Critical | Major | Minor
- What I found: <concrete evidence-backed finding>
- Decision recommendation: Proceed | Revise | Stop
- Confirmation required: Yes | No — <reason>
- Why this recommendation: <short rationale>
- What to confirm next: <one decision>

Options:

1. <meaningful option>
2. <meaningful option>

Recommendation: <recommended option and reason>

## Recommended Next Step

<one workflow handoff>
```

Include options only for materially different choices, and always recommend one
when options are present. Do not describe a material decision as closed until
the Human confirms, defers, rejects, or blocks it.

In Concept Grill, recommendations and options must remain at the Concept level.
If the only remaining alternatives are technical representations or
implementation mechanisms, route them to Planning instead of opening a Human
Concept decision.

For a completed Concept Grill, include these concise sections when applicable:

- `Readiness judgment`: exactly one of `Concept requires more design work` or
  `Concept is sufficiently defined for implementation planning`;
- `Unresolved conceptual questions`: only open Problem, Concept, or
  Design-boundary questions, or `None`;
- `Parked implementation implications`: named for later Planning without
  proposed schemas, APIs, classes, storage, or task decomposition, or `None`;
  and
- `Evidence notes`: current-state evidence and the inference it supports,
  especially where existing code or Documentation could bias the conclusion.

## Recording and handoff

Do not publish a partial or pending finding as a completed Issue record. After
all material findings in a session have Human decisions, let
`soundatlas-issue-planning` record one consolidated `## Grill-Me Review` using
the canonical contract in `docs/github-issue-workflow.md`. Keep a clean check
inline with the next action when useful, or omit it when no durable record adds
value.

End with one verdict:

- Ready
- Ready with follow-up
- Needs revision
- Blocked
- Return to concept
- Return to planning

For Concept Grill, pair the general verdict with the required `Readiness
judgment`; do not substitute `Ready` for the more precise concept-readiness
statement.

Route implementation fixes to implementation, Concept changes to
`soundatlas-concept-work`, Plan changes to `soundatlas-issue-planning`, and
completed-implementation evidence comparison to
`soundatlas-implementation-review`.

Keep `Next step` limited to routing. Do not use it as a substitute for
`## Proceed to Implementation`.

## SoundAtlas constraints

Follow `AGENTS.md` and the authoritative domain sources. Keep changes lean and
MVP-oriented. Do not automate final editorial judgment, Source approval, media
approval, or Publication approval. Do not treat generated recommendations as
Human Decisions or expand SoundAtlas into a generalized administration or
workflow platform without explicit approval.
