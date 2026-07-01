# Plans And Skills Workflow

SoundAtlas uses three lightweight layers for agent-driven work:

* GitHub Issues are the source of truth for planned agent work.
* Issue comments and body updates hold Intake Issues, Plan Updates, Detailed Plan
  Updates, and Implementation Reports.
* Skills and prompts define reusable execution patterns for planning,
  implementation, tests, docs, and UX.

Prompts are compatibility entrypoints into those workflows. They should stay
thin and should not redefine product behavior.

## Workflow Rules

* Do not implement from a vague request. Inspect the repo and create or update
  an Intake Issue for non-trivial work.
* Capture new planned work with `Task`, `Context`, and `Acceptance Criteria`.
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
| Intake and planning | GitHub Issue body/comments | direct agent work, optionally supported by `prompts/plan-feature.md` |
| Issue planning support | GitHub Issue body/comments | `soundatlas-implementation-planning` at `.codex/skills/soundatlas-implementation-planning` |
| Backend implementation | approved Issue with Plan Update when needed | `prompts/implement-backend-api.md` when useful |
| Frontend implementation | approved Issue with Plan Update when needed | `prompts/implement-frontend-map.md` when useful |
| Test planning and implementation | approved Issue and changed behavior | `prompts/write-tests.md` |
| Durable documentation | approved Issue, workflow change, or code change | `prompts/update-docs.md` |
| UX audit and critique | current frontend and design baseline | `prompts/design-ux.md` |

## Migration Guidance

1. Prefer conversational planning for day-to-day development.
2. Use GitHub Issues as the durable planning, implementation, and verification
   record for non-trivial work.
3. Prefer skills for repeatable execution steps.
4. Keep prompts as short, stable wrappers while the repo transitions toward
   skills.
5. Update workflow docs together when a skill or prompt boundary changes.
