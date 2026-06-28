# Specs and Skills Workflow

SoundAtlas uses two layers for agent-driven work:

- Specs define product intent, scope, requirements, and acceptance criteria.
- Skills define reusable execution patterns for planning, implementation, tests, docs, and UX.

Prompts are compatibility entrypoints into those workflows. They stay thin and should not redefine product behavior.

## Workflow rules

- Keep specs as the source of truth for feature intent.
- Implement only from an approved spec revision with clear acceptance criteria.
- Use a skill or prompt entrypoint only to carry out the approved spec.
- When a workflow repeats across multiple features, extract the repeatable part into a skill and leave the prompt as a wrapper if needed.
- Keep feature names stable in spec paths and revision names.
- End every workflow result with a short `Next step` handoff naming the next prompt, skill, or human action when useful.

## Current mapping

| Work type | Source of truth | Current entrypoint |
| --- | --- | --- |
| Spec planning | feature request + approved revision path | `soundatlas-spec-planning` at `.codex/skills/soundatlas-spec-planning`, wrapped by `prompts/plan-feature.md` |
| Backend implementation | approved spec revision | `prompts/implement-backend-api.md` |
| Frontend implementation | approved spec revision | `prompts/implement-frontend-map.md` |
| Test planning and implementation | approved spec revision | `prompts/write-tests.md` |
| Durable documentation | approved spec revision or workflow change | `prompts/update-docs.md` |
| UX audit and critique | current frontend and design baseline | `prompts/design-ux.md` |

## Migration guidance

1. Prefer specs for durable product decisions.
2. Prefer skills for repeatable execution steps.
3. Keep prompts as short, stable wrappers while the repo transitions toward skills.
4. Update workflow docs together when a skill or prompt boundary changes.
