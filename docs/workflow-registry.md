# Workflow Registry

SoundAtlas uses three lightweight layers for agent-driven work:

- GitHub Issues are the source of truth for planned agent work.
- Issue comments and body updates hold Intake Issues, Concept records, Plan
  Updates, Detailed Plan Updates, Proceed-to-Implementation records, and
  Implementation Reports.
- Skills and prompts define reusable execution patterns for critique, planning,
  implementation, tests, docs, and UX.

Prompts provide scoped interactive or compatibility entrypoints. They should
not redefine product behavior or Skill procedures. The `soundatlas-grill-me`
Skill is the central phase-aware critique entrypoint. The
`soundatlas-concept-work` Skill synthesizes confirmed decisions when Concept
Work is needed. The `soundatlas-implementation-review` Skill performs the
repeatable completion comparison and evidence assessment. The
`soundatlas-issue-planning` Skill is the durable Issue-writing mechanism for
implementation plans, Proceed-to-Implementation records, and the combined
Implementation Report.

All multiline GitHub Markdown body transport follows the safe file/stdin rule
in `docs/github-issue-workflow.md`; the generic helper is
`scripts/gh_markdown_payload.py`.

`soundatlas-grill-me` owns Review Mode selection, Phase Boundaries, Materiality
routing, and the interactive one-finding flow. It may briefly indicate whether
material findings are present and, when useful, give an approximate count. The
count is optional and never a target. Material findings are presented one at a
time with a recommendation and pause for Human confirmation.

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
scope, decisions, plans, implementation go-ahead, and completion evidence. The
local readiness validator checks those artifacts but does not advance state.

```text
Request
  |
  +-- Clearly trivial, local, and low-risk
  |     -> Direct implementation
  |     -> Relevant validation
  |     -> Commit-ready gate + local commit
  |     -> Review committed diff
  |     -> Human push request
  |     -> Push + completion comment + Issue closure
  |
  +-- Non-trivial work
        -> Intake Issue
        -> Lightweight Grill-Me check
             no material finding -> continue
             material finding    -> Interactive Grill Me -> confirmed decisions
        -> Optional concept work when requested or needed
        -> Plan Update as required
        -> Explicit implementation request
        -> Proceed to Implementation record
        -> Readiness validation
        -> Relevant execution skill
        -> Validation
        -> Commit-ready gate + local commit
        -> soundatlas-implementation-review
        -> Combined Implementation Report
        -> Human review of committed diff
        -> Human push request
        -> Push + completion comment + Issue closure
```

Concept work is conditional. Use it when explicitly requested or when planning
would otherwise have to invent material target behavior, runtime
responsibilities, boundaries, or ownership; otherwise skip it. The plan
references an accepted concept rather than copying it.

"Automatic" means the agent is instructed to perform the lightweight checks
and may select a skill implicitly. For example, Grill-Me, Concept Work, and
Implementation Review metadata permit implicit selection.
This is agent routing, not independently executing automation.

This overview does not redefine ownership. `AGENTS.md` owns repository-wide
constraints, this registry owns routing and entrypoint selection,
`docs/github-issue-workflow.md` owns the detailed Issue lifecycle, and
GitHub Issues hold the durable work record. The canonical table below maps each
work type to its prompt or skill.

Implementation review is read-only and produces a Review Result inside the
single Implementation Report comment. Human review of the committed diff, push
authorization, and post-push closure remain separate lifecycle concerns in
`docs/github-issue-workflow.md`.

## Skill, Prompt, and Source Boundary Policy

This section is authoritative for repository-wide entrypoint selection and
document ownership.

### Use a skill for repeatable execution

Use a reusable skill when work has a stable, repeatable execution or review
procedure, domain constraints, routing or validation steps, and an output format
that agents should apply consistently. A skill may cover a broad domain rather
than one feature. The approved GitHub Issue remains the product and scope
authority.

Current examples include:

- phase-aware critique and Materiality routing: `soundatlas-grill-me`;
- concept synthesis and recording: `soundatlas-concept-work`;
- implementation comparison and evidence assessment:
  `soundatlas-implementation-review`;
- frontend implementation: `soundatlas-frontend-implementation`;
- backend implementation: `soundatlas-backend-implementation`;
- Issue intake, planning, and reports: `soundatlas-issue-planning`.

### Keep a prompt for bounded specialized interaction

Keep work in a prompt when its interaction is specialized to one bounded output
and does not need a reusable execution procedure of its own. Current examples
include UX audit and critique, route editorial work, seed curation, and YouTube
query planning. Interaction alone does not require a prompt when the repository
needs one central, repeatable procedure such as `soundatlas-grill-me`.

Documentation prompts may remain the active entrypoint until their
corresponding skill extraction is completed; the registry row must identify
that transitional status.

### Use a compatibility wrapper during migration

When repeatable guidance is extracted from an existing prompt into a skill,
keep the existing prompt as a thin compatibility wrapper by default. The wrapper
may identify the skill, preserve the historical entrypoint, collect concise
optional context, and state the output boundary. It must not duplicate or
override the skill’s implementation rules.

Remove or rename a legacy wrapper only when an approved Issue explicitly
authorizes it after repository references and compatibility needs have been
reviewed.

### Document ownership and precedence

- `AGENTS.md` owns repository-wide constraints and working conventions.
- `docs/workflow-registry.md` owns routing, entrypoint selection, document
  ownership, and precedence explicitly stated here.
- Domain source documents own product, data, editorial, UX, and other
  domain-specific rules.
- Skills own repeatable execution behavior, validation, reporting guidance, and
  phase-aware interaction when the registry assigns it.
- Prompts own bounded interactive behavior or compatibility-entrypoint guidance
  assigned by the registry.
- GitHub Issues own planned scope, confirmed decisions, acceptance criteria,
  default `## Concept` records, `## Proceed to Implementation` records, and
  implementation reports. When the human selects an authoritative concept
  document under `docs/`, that document owns the concept and the Issue links to
  it without duplication.

### Planned write boundaries

For non-trivial implementation, the Plan names the exact authoritative paths it
changes and declares a bounded derived-consistency surface. The matching Proceed
record lists the exact direct consumers found by a pre-write audit. Those files
may receive mechanical alignment only; they are not a general permission to
edit a directory or alter behavior. `AGENTS.md` is always an explicitly named
authority. A file or change outside this boundary remains untouched and is
routed to a linked Intake Issue. Apply the declared boundary in one combined
repository-edit request when practical. Environment confirmation prompts remain
independent safeguards. The lifecycle contract and canonical record shape live
in `docs/github-issue-workflow.md`.

The detailed lifecycle and canonical Issue artifact shapes live in
`docs/github-issue-workflow.md`. `soundatlas-issue-planning` owns the procedure
for drafting and revising those artifacts, but not lifecycle ordering,
post-push closure, or Issue-state management.

`scripts/check_issue_readiness.py` owns deterministic pre-implementation
artifact checks. It does not decide Materiality, infer Human authorization,
write Issue comments, or replace the semantic routing owned by Grill Me and
Issue Planning.

For completion review, `soundatlas-implementation-review` owns comparison,
proportional evidence assessment, finding classification, and routing. Grill Me
owns material human decisions; implementation owns fixes;
`soundatlas-issue-planning` owns the combined Implementation Report;
and the human owns push authorization. The review skill does not manage Issue
state labels.

When execution documents conflict, the registry resolves the conflict only when
it explicitly defines precedence. Otherwise, correct the conflict in the
authoritative source rather than interpreting it on the agent's own authority.

### Migration standard

For an approved prompt-to-skill extraction:

1. Create or update an Issue before changing workflow guidance.
2. Preserve the existing behavior, gates, constraints, and output expectations
   while separating reusable execution guidance from any retained prompt
   boundary.
3. Make the new skill authoritative for repeatable execution.
4. Reduce the existing prompt to a compatibility wrapper when compatibility
   matters; remove it only when the approved Issue includes a completed
   reference and compatibility audit.
5. Update the registry and active references in the same change.
6. Validate references, skill structure, and scope; do not include application,
   seed-data, or production behavior changes unless separately approved.

### Boundary examples

| Work category | Default boundary | Current guidance |
| --- | --- | --- |
| Frontend implementation | Skill | `soundatlas-frontend-implementation` |
| Backend implementation | Skill | `soundatlas-backend-implementation` |
| Concept synthesis | Skill | `soundatlas-concept-work` |
| Implementation review | Skill | `soundatlas-implementation-review` |
| Documentation updates | Skill | `soundatlas-documentation-implementation` |
| Test planning and implementation | Skill | `soundatlas-testing-implementation` |
| Editorial route and seed curation | Interactive prompt | `prompts/create-route.md`, `prompts/curate-seed-data.md` |
| Phase-aware critique | Skill | `soundatlas-grill-me` |
| UX critique and review | Interactive prompt | `prompts/design-ux.md` |
| Enrichment query planning | Human-reviewed prompt | `prompts/generate-youtube-search-queries.md` |

## Workflow Rules

- Create an Intake Issue first for non-trivial work. Use
  `soundatlas-grill-me` to inspect, critique, simplify, and identify blockers
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
- Before technical planning detail, require the Plan to reference its accepted
  Concept or state why Concept Work was not required. This is a semantic check,
  not a new Concept status.
- Implement from a non-trivial Issue only after the Plan gate is complete, the
  Human explicitly confirms the latest Plan with wording such as `implement
  issue #<number>`, the agent records `## Proceed to Implementation`, and the
  shared readiness validator passes. Risk-flagged work also requires its
  Grill-Me gate. Clearly trivial, local, low-risk work may proceed directly.
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
- After a successful push for completed Issue work, run the local completion
  gate, capture the published hash, verify Issue-relevant completeness, post
  the single standard completion comment, and close the Issue only after that
  comment succeeds. Preserve the documented exceptions in
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
| Phase-aware critique and planning front door | Skill                             | Intake Issue when non-trivial                                                | `.codex/skills/soundatlas-grill-me/SKILL.md` for procedure; `docs/github-issue-workflow.md` for lifecycle and completed records | `.codex/skills/soundatlas-grill-me/SKILL.md`                                                                   | Finding, verdict, or workflow handoff                               |
| Concept synthesis                       | Skill                                  | Confirmed material decisions; only when concept work is needed               | `## Concept` Issue comment or one human-confirmed authoritative document under `docs/` | `.codex/skills/soundatlas-concept-work/SKILL.md`                                                            | Five-part concept or link to its authoritative document             |
| Implementation review                   | Skill                                  | Completed non-trivial Issue work, or drift/risk during implementation        | Approved Issue, concept when present, plan, actual diff, evidence, and current-state docs | `.codex/skills/soundatlas-implementation-review/SKILL.md`                                               | Review Result inside the single Implementation Report               |
| Issue intake, planning, and reports     | Skill                                  | Intake or Grill-Me as required by risk                                       | GitHub Issue body/comments; lifecycle in `docs/github-issue-workflow.md`            | `.codex/skills/soundatlas-issue-planning/SKILL.md`                                                     | Intake, Plan Update, Detailed Plan Update, Proceed record, or Implementation Report |
| Frontend implementation                 | Skill                                  | Validated latest Plan and Proceed record when non-trivial                    | Approved GitHub Issue; `.codex/skills/soundatlas-frontend-implementation/SKILL.md` | `.codex/skills/soundatlas-frontend-implementation/SKILL.md`                                                      | Frontend changes and implementation report                          |
| Backend implementation                  | Skill                                  | Validated latest Plan and Proceed record when non-trivial                    | Approved GitHub Issue; `.codex/skills/soundatlas-backend-implementation/SKILL.md` | `.codex/skills/soundatlas-backend-implementation/SKILL.md`                                                        | Backend changes and implementation report                           |
| Documentation and workflow changes      | Skill                                  | Validated latest Plan and Proceed record when non-trivial                    | Approved GitHub Issue; `.codex/skills/soundatlas-documentation-implementation/SKILL.md` | `.codex/skills/soundatlas-documentation-implementation/SKILL.md`                                                  | Documentation changes and implementation report                     |
| Test planning and implementation        | Skill                                  | Validated latest Plan and Proceed record for non-trivial Issue work          | Approved GitHub Issue or focused scope; `.codex/skills/soundatlas-testing-implementation/SKILL.md` | `.codex/skills/soundatlas-testing-implementation/SKILL.md`                                                        | Tests and verification report                                       |
| UX audit and critique                   | Prompt                                 | Inspection before implementation; Grill-Me before Issue planning when needed | `docs/design/current-frontend-design.md` and relevant audit                        | `prompts/design-ux.md`                                                                                          | Findings, UX slice, or audit                                        |
| Route editorial workflow                | Prompt plus command reference          | Grill-Me and approved Issue before broad route/seed changes                  | Route-folder artifacts and `docs/content/editorial-workflow.md`                    | `prompts/create-route.md` and `docs/content/workflow-commands.md`                                               | Route artifacts and reviewed seed proposal                          |
| Seed data curation                      | Prompt                                 | Grill-Me and accepted-event boundary for non-trivial work                    | `docs/data/seed-data-validation.md` and accepted route artifacts                   | `prompts/curate-seed-data.md`                                                                                   | Seed changes or review proposal                                     |
| YouTube query planning                  | Standalone prompt                      | Source/event context and human review                                        | `prompts/generate-youtube-search-queries.md` and enrichment docs                   | `prompts/generate-youtube-search-queries.md`                                                                    | Draft request plan                                                  |

The registry covers active human-facing entrypoints and source-of-truth
documents. Generated route artifacts, `*.ai-draft.*` files, screenshots,
mockups, and archival records are not registry entries.

Frontend, backend, documentation, and testing implementation route directly to
their corresponding skills. Grill Me also routes directly to
`soundatlas-grill-me`. The YouTube query prompt remains a prompt because its
specialized output boundary is intentional.

## Migration Guidance

1. Use `soundatlas-grill-me` for explicit Grill-Me requests and for vague,
   risky, cross-cutting, drift-prone, or editorially sensitive work.
2. Use `soundatlas-concept-work` after confirmed Grill-Me decisions when an
   implementation plan would otherwise have to invent the target.
3. Use `soundatlas-implementation-review` for the repeatable implementation and
   evidence comparison; return material decisions to Grill Me.
4. Use GitHub Issues as the durable planning, implementation, and verification
   record for non-trivial work.
5. Use `soundatlas-issue-planning` to create Issue bodies, plans,
   Proceed-to-Implementation records, and the combined Implementation Report
   without copying accepted concepts.
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
- `## Proceed to Implementation` records the Human's confirmation of the exact
  latest Plan and authorization of its scope. A Grill-Me `Next step` does not
  substitute for this record.
- `## Implementation Report` records completed work, verification, the Review
  Result, and remaining risks. Routine implementation review does not create a
  separate Issue comment.

Material decisions about product behavior, scope, security, privacy, external
APIs, editorial/source quality, irreversible workflow behavior, or production
stability require user confirmation. Low-risk implementation assumptions may be
recorded in the Plan Update. Do not use `Open Questions: None` while a material
decision remains unresolved.
