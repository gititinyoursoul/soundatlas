# Workflow Registry

SoundAtlas uses three lightweight layers for agent-driven work:

- GitHub Issues are the source of truth for planned agent work.
- Issue comments and body updates hold Intake Issues, Concept records, Plan
  Updates, Detailed Plan Updates, and Implementation Reports.
- Skills and prompts define reusable execution patterns for critique, planning,
  implementation, tests, docs, and UX.

Prompts are compatibility entrypoints into those workflows. They should stay
thin and should not redefine product behavior. `prompts/grill-me.md` is the
default human-facing critique entrypoint. The
`soundatlas-concept-work` skill synthesizes confirmed decisions when concept
work is needed. The `soundatlas-implementation-review` skill performs the
repeatable completion comparison and evidence assessment. The
`soundatlas-issue-planning` skill is the durable Issue-writing
mechanism for implementation plans and the combined Implementation Report.

All multiline GitHub Markdown body transport follows the safe file/stdin rule
in `docs/github-issue-workflow.md`; the generic helper is
`scripts/gh_markdown_payload.py`.

`prompts/grill-me.md` is intentionally interactive: it may briefly indicate
whether material findings are present and, when useful, give an approximate
count. The count is optional and never a target. It should then present one
finding at a time, with a recommendation, and pause for user confirmation before
continuing to the next finding. When a finding requires a material decision, it
should offer meaningful options and a recommended choice.

At the agreed workflow transitions, first apply a lightweight Grill-Me check.
Continue without an interactive session when there is no material finding. If
planning would otherwise invent material target behavior, runtime
responsibilities, boundaries, or ownership, resolve material decisions through
Grill Me and then use `soundatlas-concept-work` to record the concept.
Before accepting completed non-trivial Issue work, use
`soundatlas-implementation-review`; return only material human decisions to
Grill Me.

## Orchestration At A Glance

SoundAtlas uses instruction-driven orchestration. There is no workflow service,
state machine, Git hook, or GitHub Action that advances work automatically.
Agents follow the repository guidance, while GitHub Issues preserve the durable
scope, decisions, plans, and completion evidence.

```text
Request
  |
  +-- Clearly trivial, local, and low-risk
  |     -> Direct implementation
  |     -> Relevant validation
  |     -> Human commit request
  |     -> Commit
  |
  +-- Non-trivial work
        -> Intake Issue
        -> Lightweight Grill-Me check
             no material finding -> continue
             material finding    -> Interactive Grill Me -> confirmed decisions
        -> Optional concept work when requested or needed
        -> Plan Update as required
        -> Explicit implementation request
        -> Relevant execution skill
        -> Validation
        -> soundatlas-implementation-review
        -> Combined Implementation Report
        -> Human diff review
        -> Human commit request
        -> Commit + completion comment + Issue closure
```

Concept work is conditional. Use it when explicitly requested or when planning
would otherwise have to invent material target behavior, runtime
responsibilities, boundaries, or ownership; otherwise skip it. The plan
references an accepted concept rather than copying it.

"Automatic" means the agent is instructed to perform the lightweight checks
and may select a skill implicitly. For example,
the concept-work and implementation-review metadata permit implicit selection.
This is agent routing, not independently executing automation.

This overview does not redefine ownership. `AGENTS.md` owns repository-wide
constraints, this registry owns routing and entrypoint selection,
`docs/github-issue-workflow.md` owns the detailed Issue lifecycle, and
GitHub Issues hold the durable work record. The canonical table below maps each
work type to its prompt or skill.

Implementation review is read-only and produces a Review Result inside the
single Implementation Report comment. Human diff review, commit authorization,
and post-commit closure remain separate lifecycle concerns in
`docs/github-issue-workflow.md`.

## Skill, Prompt, and Source Boundary Policy

This section is authoritative for repository-wide entrypoint selection and
document ownership.

### Use a skill for repeatable execution

Use a reusable skill when work has a stable, repeatable implementation process,
domain constraints, validation steps, and a report format that agents should
apply consistently. A skill may cover a broad domain rather than one feature.
The approved GitHub Issue remains the product and scope authority.

Current examples include:

- concept synthesis and recording: `soundatlas-concept-work`;
- implementation comparison and evidence assessment:
  `soundatlas-implementation-review`;
- frontend implementation: `soundatlas-frontend-implementation`;
- backend implementation: `soundatlas-backend-implementation`;
- Issue intake, planning, and reports: `soundatlas-issue-planning`.

### Keep a prompt for interactive or human-review-bound work

Keep work in a prompt when its value depends on conversational critique,
stepwise human decisions, source or media review, editorial judgment, or a
proposal that must be narrowed before implementation. Current examples include
Grill-Me review, UX audit and critique, route editorial work, seed curation, and
YouTube query planning.

Documentation prompts may remain the active entrypoint until their
corresponding skill extraction is completed; the registry row must identify
that transitional status.

### Use a compatibility wrapper during migration

When repeatable guidance is extracted from an existing prompt into a skill,
keep the existing prompt as a thin compatibility wrapper by default. The wrapper
may identify the skill, preserve the historical entrypoint, collect concise
optional context, and state the output boundary. It must not duplicate or
override the skill’s implementation rules.

Remove or rename a legacy wrapper only through a separate approved Issue after
repository references and compatibility needs have been reviewed.

### Document ownership and precedence

- `AGENTS.md` owns repository-wide constraints and working conventions.
- `docs/workflow-registry.md` owns routing, entrypoint selection, document
  ownership, and precedence explicitly stated here.
- Domain source documents own product, data, editorial, UX, and other
  domain-specific rules.
- Skills own repeatable execution behavior, validation, and reporting guidance.
- Prompts own interactive behavior or compatibility-entrypoint guidance.
- GitHub Issues own planned scope, confirmed decisions, acceptance criteria,
  default `## Concept` records, and implementation reports. When the human
  selects an authoritative concept document under `docs/`, that document owns
  the concept and the Issue links to it without duplication.

The detailed lifecycle and canonical Issue artifact shapes live in
`docs/github-issue-workflow.md`. `soundatlas-issue-planning` owns the procedure
for drafting and revising those artifacts, but not lifecycle ordering,
post-commit closure, or Issue-state management.

For completion review, `soundatlas-implementation-review` owns comparison,
proportional evidence assessment, finding classification, and routing. Grill Me
owns material human decisions; implementation owns fixes;
`soundatlas-issue-planning` owns the combined Implementation Report;
and the human owns commit authorization. The review skill does not manage Issue
state labels.

When execution documents conflict, the registry resolves the conflict only when
it explicitly defines precedence. Otherwise, correct the conflict in the
authoritative source rather than interpreting it on the agent's own authority.

### Migration standard

For an approved prompt-to-skill extraction:

1. Create or update an Issue before changing workflow guidance.
2. Preserve the existing behavior, gates, constraints, and output expectations
   while separating reusable execution guidance from the prompt boundary.
3. Make the new skill authoritative for repeatable execution.
4. Reduce the existing prompt to a compatibility wrapper when compatibility
   matters.
5. Update the registry and active references in the same change.
6. Validate references, skill structure, and scope; do not include application,
   seed-data, or production behavior changes unless separately approved.

### Boundary examples

| Work category | Default boundary | Current guidance |
| --- | --- | --- |
| Frontend implementation | Skill, with legacy wrapper | `soundatlas-frontend-implementation` |
| Backend implementation | Skill, with legacy wrapper | `soundatlas-backend-implementation` |
| Concept synthesis | Skill | `soundatlas-concept-work` |
| Implementation review | Skill | `soundatlas-implementation-review` |
| Documentation updates | Skill, with legacy wrapper | `soundatlas-documentation-implementation` |
| Test planning and implementation | Skill, with legacy wrapper | `soundatlas-testing-implementation` |
| Editorial route and seed curation | Interactive prompt | `prompts/create-route.md`, `prompts/curate-seed-data.md` |
| UX critique and review | Interactive prompt | `prompts/design-ux.md`, `prompts/grill-me.md` |
| Enrichment query planning | Human-reviewed prompt | `prompts/generate-youtube-search-queries.md` |

## Workflow Rules

- Create an Intake Issue first for non-trivial work. Use
  `prompts/grill-me.md` to inspect, critique, simplify, and identify blockers
  before a risk-flagged Issue receives a Plan Update or implementation.
- Apply a lightweight Grill-Me check at Intake, before accepting a consequential
  concept or broad Plan Update, when implementation reveals drift or new
  constraints, and before accepting completed implementation. Continue without
  pausing when no material finding exists.
- Use `soundatlas-concept-work` when requested explicitly or when a Grill-Me
  check finds that implementation planning would otherwise invent material
  target behavior, runtime responsibilities, boundaries, or ownership. Skip it
  for clear, local, low-risk work.
- Use `soundatlas-implementation-review` before accepting completed non-trivial
  Issue work. Skip clearly trivial, local, low-risk changes. During
  implementation, use it only for drift, risk, or a new material constraint.
  Keep it read-only and return material human decisions to Grill Me.
- Treat prompt, skill, workflow-doc, `AGENTS.md`, planning-rule, and
  implementation-gate changes as non-trivial by default. Create or update a
  GitHub Issue before implementation.
- Capture new planned work with `Task`, `Context`, and `Acceptance Criteria`
  through `soundatlas-issue-planning`.
- Allow Intake Revisions with a visible `## Intake Revision` history comment;
  material revisions require Grill-Me before planning, while material expansion
  after implementation begins requires a linked Issue. See
  `docs/github-issue-workflow.md` for the phase-specific rules.
- Record the Grill-Me result before a `## Plan Update` or `## Detailed Plan
  Update` when risk flags are present. Use a standalone `## Grill-Me Review`
  for material findings, decisions, blockers, or explicit standalone sessions;
  record clean checks inline in the action comment when useful.
- Implement from a risk-flagged Issue only after the review and plan gates are
  complete plus explicit wording such as `implement issue #<number>`. Clearly
  trivial, local, low-risk work may proceed directly.
- Use a skill or prompt entrypoint to carry out the approved Issue content.
- Let Codex set existing approved Issue labels when useful. New labels must be
  proposed and explicitly approved before Codex creates or uses them.
- When creating an Issue, choose exactly one approved `priority:p*` label with
  explicit rationale. Use `priority:p2` only as the neutral fallback when no
  stronger priority signal applies.
- Inspect existing open milestones when creating an Issue. Assign one only when
  the Issue's primary deliverable directly advances the milestone outcome;
  leave partial, indirect, multiple, or ambiguous matches unassigned. Report
  the milestone decision and rationale alongside the priority rationale, and do
  not create or broaden milestones without explicit human approval.
- After required findings are resolved, post one Implementation Report
  containing the Review Result. Do not post a separate routine review comment.
- After a successful commit for completed Issue work, run the local completion
  gate, capture the hash, verify Issue-relevant completeness, post the single
  standard completion comment, and close the Issue only after that comment
  succeeds. Preserve the documented exceptions in
  `docs/github-issue-workflow.md`.
- End every workflow result with a short `Next step` handoff when useful.

## Canonical Workflow Registry

This table is the canonical routing registry. It owns entrypoint selection,
document ownership, and any precedence explicitly stated here. The linked
source owns detailed behavior, commands, constraints, and output formats.

When execution documents conflict, the registry resolves the conflict only if
it explicitly defines precedence between those documents. Otherwise, the
conflict must be corrected in the authoritative source rather than interpreted
by the agent.

| Work type                               | Kind                                   | Required gate                                                                | Authoritative source                                                               | Entrypoint                                                                                                      | Output                                                              |
| --------------------------------------- | -------------------------------------- | ---------------------------------------------------------------------------- | ---------------------------------------------------------------------------------- | --------------------------------------------------------------------------------------------------------------- | ------------------------------------------------------------------- |
| Intake critique and planning front door | Interactive prompt                     | Intake Issue when non-trivial                                                | `prompts/grill-me.md` for review format; GitHub Issue for decisions                | `prompts/grill-me.md`                                                                                           | Standalone decision record or inline action note                    |
| Concept synthesis                       | Skill                                  | Confirmed material decisions; only when concept work is needed               | `## Concept` Issue comment or one human-confirmed authoritative document under `docs/` | `.codex/skills/soundatlas-concept-work/SKILL.md`                                                            | Five-part concept or link to its authoritative document             |
| Implementation review                   | Skill                                  | Completed non-trivial Issue work, or drift/risk during implementation        | Approved Issue, concept when present, plan, actual diff, evidence, and current-state docs | `.codex/skills/soundatlas-implementation-review/SKILL.md`                                               | Review Result inside the single Implementation Report               |
| Issue intake, planning, and reports     | Skill                                  | Intake or Grill-Me as required by risk                                       | GitHub Issue body/comments; lifecycle in `docs/github-issue-workflow.md`            | `.codex/skills/soundatlas-issue-planning/SKILL.md`                                                     | Intake, Plan Update, Detailed Plan Update, or Implementation Report |
| Frontend implementation                 | Skill plus compatibility wrapper       | Approved Issue; Grill-Me and Plan Update when risk-flagged                   | Approved GitHub Issue; `.codex/skills/soundatlas-frontend-implementation/SKILL.md` | `.codex/skills/soundatlas-frontend-implementation/SKILL.md` with `prompts/implement-frontend-map.md` as wrapper | Frontend changes and implementation report                          |
| Backend implementation                  | Skill plus compatibility wrapper       | Approved Issue; Grill-Me and Plan Update when risk-flagged                   | Approved GitHub Issue; `.codex/skills/soundatlas-backend-implementation/SKILL.md` | `.codex/skills/soundatlas-backend-implementation/SKILL.md` with `prompts/implement-backend-api.md` as wrapper | Backend changes and implementation report                           |
| Documentation and workflow changes      | Skill plus compatibility wrapper       | Approved Issue; Grill-Me for workflow or other risk-flagged changes          | Approved GitHub Issue; `.codex/skills/soundatlas-documentation-implementation/SKILL.md` | `.codex/skills/soundatlas-documentation-implementation/SKILL.md` with `prompts/update-docs.md` as wrapper        | Documentation changes and implementation report                     |
| Test planning and implementation        | Skill plus compatibility wrapper       | Approved Issue or focused test scope; Grill-Me for risk-flagged work         | Approved GitHub Issue or focused scope; `.codex/skills/soundatlas-testing-implementation/SKILL.md` | `.codex/skills/soundatlas-testing-implementation/SKILL.md` with `prompts/write-tests.md` as wrapper               | Tests and verification report                                       |
| UX audit and critique                   | Prompt                                 | Inspection before implementation; Grill-Me before Issue planning when needed | `docs/design/current-frontend-design.md` and relevant audit                        | `prompts/design-ux.md`                                                                                          | Findings, UX slice, or audit                                        |
| Route editorial workflow                | Prompt plus command reference          | Grill-Me and approved Issue before broad route/seed changes                  | Route-folder artifacts and `docs/content/editorial-workflow.md`                    | `prompts/create-route.md` and `docs/content/workflow-commands.md`                                               | Route artifacts and reviewed seed proposal                          |
| Seed data curation                      | Prompt                                 | Grill-Me and accepted-event boundary for non-trivial work                    | `docs/data/seed-data-validation.md` and accepted route artifacts                   | `prompts/curate-seed-data.md`                                                                                   | Seed changes or review proposal                                     |
| YouTube query planning                  | Standalone prompt                      | Source/event context and human review                                        | `prompts/generate-youtube-search-queries.md` and enrichment docs                   | `prompts/generate-youtube-search-queries.md`                                                                    | Draft request plan                                                  |

The registry covers active human-facing entrypoints and source-of-truth
documents. Generated route artifacts, `*.ai-draft.*` files, screenshots,
mockups, and archival records are not registry entries.

The frontend, backend, documentation, and testing implementation prompts are
compatibility wrappers for their completed skills. `grill-me.md`
and the YouTube query prompt remain prompts because their interactive or
specialized output boundaries are intentional.

## Migration Guidance

1. Prefer `prompts/grill-me.md` or conversational grill-me review for vague,
   risky, cross-cutting, or editorially sensitive work.
2. Use `soundatlas-concept-work` after confirmed Grill-Me decisions when an
   implementation plan would otherwise have to invent the target.
3. Use `soundatlas-implementation-review` for the repeatable implementation and
   evidence comparison; return material decisions to Grill Me.
4. Use GitHub Issues as the durable planning, implementation, and verification
   record for non-trivial work.
5. Use `soundatlas-issue-planning` to create Issue bodies, plans, and
   the combined Implementation Report without copying accepted concepts.
6. Prefer skills for repeatable execution steps.
7. Keep prompts as short, stable wrappers while the repo transitions toward
   skills.
8. Update workflow docs together when a skill or prompt boundary changes.

Run the manual reference check from the repository root with:

```sh
python scripts/check_doc_references.py
```

The checker covers active guidance surfaces only. It ignores URLs, placeholders,
generated or optional artifacts, and intentionally historical/archive paths.
CI enforcement is deferred until manual use establishes a low-noise baseline.

### Stage markers and decision materiality

Use standardized Issue comments as the canonical workflow record:

- `## Grill-Me Review` records findings, confirmation requirements, and
  confirmed decisions.
- `## Concept` records the accepted target when concept work is needed, unless
  the Issue links to one authoritative concept document under `docs/`.
- `## Plan Update` or `## Detailed Plan Update` records implementation-ready
  scope after required decisions are confirmed.
- `## Implementation Report` records completed work, verification, the Review
  Result, and remaining risks. Routine implementation review does not create a
  separate Issue comment.

Material decisions about product behavior, scope, security, privacy, external
APIs, editorial/source quality, irreversible workflow behavior, or production
stability require user confirmation. Low-risk implementation assumptions may be
recorded in the Plan Update. Do not use `Open Questions: None` while a material
decision remains unresolved.
