# Plans And Skills Workflow

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

## Current Mapping

| Work type                               | Source of truth                                 | Current entrypoint                                                                         |
| --------------------------------------- | ----------------------------------------------- | ------------------------------------------------------------------------------------------ |
| Intake critique and planning front door | target artifact, then GitHub Issue when needed  | `prompts/grill-me.md`                                                                      |
| Issue planning support                  | GitHub Issue body/comments                      | `soundatlas-implementation-planning` at `.codex/skills/soundatlas-implementation-planning` |
| Backend implementation                  | approved Issue with Plan Update when needed     | `prompts/implement-backend-api.md` when useful                                             |
| Frontend implementation                 | approved Issue with Plan Update when needed     | `prompts/implement-frontend-map.md` when useful                                            |
| Route editorial workflow                | route folder, approved Issue when non-trivial   | `docs/content/workflow-commands.md` and `prompts/create-route.md`                          |
| Test planning and implementation        | approved Issue and changed behavior             | `prompts/write-tests.md`                                                                   |
| Durable documentation                   | approved Issue, workflow change, or code change | `prompts/update-docs.md`                                                                   |
| UX audit and critique                   | current frontend and design baseline            | `prompts/design-ux.md`                                                                     |

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
