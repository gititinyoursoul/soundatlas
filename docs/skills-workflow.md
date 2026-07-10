# Plans And Skills Workflow

SoundAtlas uses three lightweight layers for agent-driven work:

* GitHub Issues are the source of truth for planned agent work.
* Issue comments and body updates hold Intake Issues, Plan Updates, Detailed Plan
  Updates, and Implementation Reports.
* Skills and prompts define reusable execution patterns for critique, planning,
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

* Do not implement from a vague request. Use `prompts/grill-me.md` to inspect,
  critique, simplify, and identify blockers before non-trivial work becomes an
  Intake Issue or Plan Update.
* Treat prompt, skill, workflow-doc, `AGENTS.md`, planning-rule, and
  implementation-gate changes as non-trivial by default. Create or update a
  GitHub Issue before implementation.
* Capture new planned work with `Task`, `Context`, and `Acceptance Criteria`
  through `soundatlas-implementation-planning`.
* Add a Plan Update or Detailed Plan Update in the Issue when implementation
  needs more decisions.
* Implement from an approved Issue after explicit wording such as
  `implement issue #<number>`, or from a clearly trivial request.
* Use a skill or prompt entrypoint to carry out the approved Issue content.
* Let Codex set existing approved Issue labels when useful. New labels must be
  proposed and explicitly approved before Codex creates or uses them.
* Post an Implementation Report after non-trivial implementation.
* End every workflow result with a short `Next step` handoff when useful.

## Current Mapping

| Work type | Source of truth | Current entrypoint |
| --- | --- | --- |
| Intake critique and planning front door | target artifact, then GitHub Issue when needed | `prompts/grill-me.md` |
| Issue planning support | GitHub Issue body/comments | `soundatlas-implementation-planning` at `.codex/skills/soundatlas-implementation-planning` |
| Backend implementation | approved Issue with Plan Update when needed | `prompts/implement-backend-api.md` when useful |
| Frontend implementation | approved Issue with Plan Update when needed | `prompts/implement-frontend-map.md` when useful |
| Route editorial workflow | route folder, approved Issue when non-trivial | `docs/content/workflow-commands.md` and `prompts/create-route.md` |
| Test planning and implementation | approved Issue and changed behavior | `prompts/write-tests.md` |
| Durable documentation | approved Issue, workflow change, or code change | `prompts/update-docs.md` |
| UX audit and critique | current frontend and design baseline | `prompts/design-ux.md` |

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
