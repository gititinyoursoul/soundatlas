---
name: soundatlas-grill-me
description: Challenge SoundAtlas ideas, Intake Issues, concepts, plans, editorial or UX artifacts, implementation work, and workflow changes with phase-aware critique and Materiality routing. Use when the human requests Grill Me or a named Grill-Me Review Mode, or when repository guidance requires a lightweight check for non-trivial, vague, risky, cross-cutting, drift-prone, or editorially sensitive work.
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
- relevant repository evidence that can resolve discoverable facts; and
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

A Grill-Me `Next step` routes the reviewed artifact; it does not confirm a Plan
or authorize implementation. The separate lifecycle record in
`docs/github-issue-workflow.md` owns that Human go-ahead.

## Review workflow

1. Identify the active artifact and select the smallest applicable Review Mode.
2. Inspect relevant repository evidence before forming findings.
3. Separate observed facts, assumptions, solution hypotheses, `Unknown`,
   `Evidence Gap`, recommendations, and Human Decisions.
4. Classify each concern for relevance to the active phase before judging its
   severity or Materiality. Abstract a later-stage concern to the current
   phase only when it exposes a material gap owned by that phase.
5. Apply the shared checks and only the Mode-Specific Focus appropriate to the
   active stage.
6. Classify each eligible finding by severity and Materiality. Route gaps and
   decisions without silently resolving them in the wrong stage.
7. Continue immediately after a clean lightweight check. Use the one-finding
   flow when a material Human Decision is required.
8. Return the result to the owning workflow artifact. Do not modify that
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

Challenge:

- explicit target behavior;
- scope and non-goals;
- material runtime responsibilities required to define the intended behavior;
- Boundaries and Ownership;
- conflicts with normative sources;
- lean MVP fit; and
- unresolved decisions that would force Planning to invent material target
  behavior, semantics, Ownership, lifecycle, responsibilities, Human/Agent
  authority, compatibility, Boundaries, or externally observable behavior.

Before presenting a Concept finding, classify the concern internally:

- **Concept:** changes material target behavior, semantics, scope, Ownership,
  lifecycle, responsibilities, Human/Agent authority, compatibility, or
  architectural Boundaries;
- **Design:** chooses how an accepted Concept is represented or achieved; or
- **Implementation:** chooses concrete schemas, fields, cardinality, enums,
  algorithms, normalization, storage, APIs, modules, files, migrations, or
  execution mechanics.

Present only Concept concerns. When a Design or Implementation concern reveals
a conceptual gap, state the underlying requirement without prescribing the
mechanism that satisfies it. Ask: could multiple materially different
technical designs satisfy this requirement without changing the intended
product or workflow behavior? If yes, keep the requirement in Concept and
defer the representation or mechanism to Planning.

Do not choose Design or Implementation details. When an accepted constraint
exposes a material conceptual consequence, surface that consequence and defer
the mechanism that satisfies it to Planning.

A Concept is complete when Planning can choose technical representations and
implementation mechanisms without inventing material target behavior,
semantics, Ownership, lifecycle, responsibilities, Human/Agent authority,
compatibility, Boundaries, or MVP scope. Remaining Design or Implementation
ambiguity is not evidence that the Concept is incomplete. End Concept Grill
when no material Concept finding remains.

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
