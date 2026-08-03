# Workflow Registry

SoundAtlas uses three lightweight layers for agent-driven work:

- GitHub Issues are the source of truth for planned agent work.
- Issue comments and body updates hold Intake Issues, Plan Updates, Detailed Plan
  Updates, and Implementation Reports.
- Skills and prompts define reusable execution patterns for critique, planning,
  implementation, tests, docs, and UX.

Prompts are compatibility entrypoints into those workflows. They should stay
thin and should not redefine product behavior. `prompts/grill-me.md` is the
default human-facing planning and critique entrypoint. The
`soundatlas-implementation-planning` skill is the durable Issue-writing
mechanism after a grill-me pass identifies work that should proceed.

`prompts/grill-me.md` is intentionally interactive: it should first give a
short estimate of how many material findings it sees, then present one finding
at a time, with a recommendation, and pause for user confirmation before
continuing to the next finding. When a finding requires a material decision, it
should offer meaningful options and a recommended choice.

## Workflow Rules

- Create an Intake Issue first for non-trivial work. Use
  `prompts/grill-me.md` to inspect, critique, simplify, and identify blockers
  before a risk-flagged Issue receives a Plan Update or implementation.
- Treat prompt, skill, workflow-doc, `AGENTS.md`, planning-rule, and
  implementation-gate changes as non-trivial by default. Create or update a
  GitHub Issue before implementation.
- Capture new planned work with `Task`, `Context`, and `Acceptance Criteria`
  through `soundatlas-implementation-planning`.
- Add a `## Grill-Me Review` comment before a `## Plan Update` or
  `## Detailed Plan Update` when risk flags are present.
- Implement from a risk-flagged Issue only after the review and plan gates are
  complete plus explicit wording such as `implement issue #<number>`. Clearly
  trivial, local, low-risk work may proceed directly.
- Use a skill or prompt entrypoint to carry out the approved Issue content.
- Let Codex set existing approved Issue labels when useful. New labels must be
  proposed and explicitly approved before Codex creates or uses them.
- When creating an Issue, choose exactly one approved `priority:p*` label with
  explicit rationale. Use `priority:p2` only as the neutral fallback when no
  stronger priority signal applies.
- Post an Implementation Report after non-trivial implementation.
- End every workflow result with a short `Next step` handoff when useful.

## Canonical Workflow Registry

This table is the canonical routing registry. It owns entrypoint selection,
document ownership, and any precedence explicitly stated here. The linked
source owns detailed behavior, commands, constraints, and output formats.

When execution documents conflict, the registry resolves the conflict only if
it explicitly defines precedence between those documents. Otherwise, the
conflict must be corrected in the authoritative source rather than interpreted
by the agent.

| Work type                               | Kind                                   | Required gate                                                                | Authoritative source                                                            | Entrypoint                                                        | Output                                                              |
| --------------------------------------- | -------------------------------------- | ---------------------------------------------------------------------------- | ------------------------------------------------------------------------------- | ----------------------------------------------------------------- | ------------------------------------------------------------------- |
| Intake critique and planning front door | Interactive prompt                     | Intake Issue when non-trivial                                                | `prompts/grill-me.md` for review format; GitHub Issue for decisions             | `prompts/grill-me.md`                                             | `## Grill-Me Review` comment                                        |
| Issue intake, planning, and reports     | Skill                                  | Intake or Grill-Me as required by risk                                       | GitHub Issue body/comments; lifecycle in `docs/implementation-plan-workflow.md` | `.codex/skills/soundatlas-implementation-planning/SKILL.md`       | Intake, Plan Update, Detailed Plan Update, or Implementation Report |
| Frontend implementation                 | Compatibility wrapper; skill candidate | Approved Issue; Grill-Me and Plan Update when risk-flagged                   | Approved GitHub Issue; frontend implementation guidance                         | `prompts/implement-frontend-map.md`                               | Frontend changes and implementation report                          |
| Backend implementation                  | Compatibility wrapper; skill candidate | Approved Issue; Grill-Me and Plan Update when risk-flagged                   | Approved GitHub Issue; backend implementation guidance                          | `prompts/implement-backend-api.md`                                | Backend changes and implementation report                           |
| Documentation and workflow changes      | Compatibility wrapper; skill candidate | Approved Issue; Grill-Me for workflow or other risk-flagged changes          | Approved GitHub Issue; `docs/implementation-plan-workflow.md`                   | `prompts/update-docs.md`                                          | Documentation changes and implementation report                     |
| Test planning and implementation        | Compatibility wrapper; skill candidate | Focused test plan; Grill-Me for risk-flagged Issue work                      | Approved GitHub Issue and changed behavior                                      | `prompts/write-tests.md`                                          | Tests and verification report                                       |
| UX audit and critique                   | Prompt                                 | Inspection before implementation; Grill-Me before Issue planning when needed | `docs/design/current-frontend-design.md` and relevant audit                     | `prompts/design-ux.md`                                            | Findings, UX slice, or audit                                        |
| Route editorial workflow                | Prompt plus command reference          | Grill-Me and approved Issue before broad route/seed changes                  | Route-folder artifacts and `docs/content/editorial-workflow.md`                 | `prompts/create-route.md` and `docs/content/workflow-commands.md` | Route artifacts and reviewed seed proposal                          |
| Seed data curation                      | Prompt                                 | Grill-Me and accepted-event boundary for non-trivial work                    | `docs/data/seed-data-validation.md` and accepted route artifacts                | `prompts/curate-seed-data.md`                                     | Seed changes or review proposal                                     |
| YouTube query planning                  | Standalone prompt                      | Source/event context and human review                                        | `prompts/generate-youtube-search-queries.md` and enrichment docs                | `prompts/generate-youtube-search-queries.md`                      | Draft request plan                                                  |

The registry covers active human-facing entrypoints and source-of-truth
documents. Generated route artifacts, `*.ai-draft.*` files, screenshots,
mockups, and archival records are not registry entries.

The implementation, documentation, and testing prompts remain compatibility
wrappers until their corresponding skill Issues are completed. `grill-me.md`
and the YouTube query prompt remain prompts because their interactive or
specialized output boundaries are intentional.

## Migration Guidance

1. Prefer `prompts/grill-me.md` or conversational grill-me review for vague,
   risky, cross-cutting, or editorially sensitive work.
2. Use GitHub Issues as the durable planning, implementation, and verification
   record for non-trivial work.
3. Use `soundatlas-implementation-planning` to turn selected grill-me findings
   and decisions into Issue bodies or comments.
4. Prefer skills for repeatable execution steps.
5. Keep prompts as short, stable wrappers while the repo transitions toward
   skills.
6. Update workflow docs together when a skill or prompt boundary changes.

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
- `## Plan Update` or `## Detailed Plan Update` records implementation-ready
  scope after required decisions are confirmed.
- `## Implementation Report` records completed work and verification.

Material decisions about product behavior, scope, security, privacy, external
APIs, editorial/source quality, irreversible workflow behavior, or production
stability require user confirmation. Low-risk implementation assumptions may be
recorded in the Plan Update. Do not use `Open Questions: None` while a material
decision remains unresolved.
