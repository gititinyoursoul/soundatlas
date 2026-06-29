# Plans, Specs, and Skills Workflow

SoundAtlas uses three lightweight layers for agent-driven work:

* Plans define the next implementation move and are the normal approval artifact.
* Specs under `specs/` are optional local records for analysis, traceability, and later verification. During solo work they are gitignored by default and normally remain uncommitted.
* Skills and prompts define reusable execution patterns for planning, implementation, tests, docs, and UX.

Prompts are compatibility entrypoints into those workflows. They should stay thin and should not redefine product behavior.

## Workflow Rules

* Do not implement from a vague request. Inspect the repo and create a concrete plan for non-trivial work.
* Implement from an approved plan, an explicitly provided spec, or a clearly trivial request.
* Create a local spec record when the human asks for one or when non-trivial work would benefit from later analysis.
* A generated spec record does not need a separate approval step.
* Use a skill or prompt entrypoint to carry out the approved plan or provided spec.
* When a workflow repeats across multiple features, extract the repeatable part into a skill and leave the prompt as a wrapper if needed.
* Keep feature names stable in local spec paths and revision names.
* End every workflow result with a short `Next step` handoff when useful.

## Current Mapping

| Work type | Source of truth | Current entrypoint |
| --- | --- | --- |
| Conversational planning | feature request + repo inspection | direct agent plan, optionally supported by `prompts/plan-feature.md` |
| Local spec record creation | approved plan or explicit spec request | `soundatlas-spec-planning` at `.codex/skills/soundatlas-spec-planning`, wrapped by `prompts/plan-feature.md` |
| Backend implementation | approved plan or provided spec | `prompts/implement-backend-api.md` when useful |
| Frontend implementation | approved plan or provided spec | `prompts/implement-frontend-map.md` when useful |
| Test planning and implementation | approved plan or provided spec | `prompts/write-tests.md` |
| Durable documentation | approved plan, provided spec, or workflow change | `prompts/update-docs.md` |
| UX audit and critique | current frontend and design baseline | `prompts/design-ux.md` |

## Migration Guidance

1. Prefer conversational plans for day-to-day development.
2. Use specs as records for later analysis, not as mandatory gates.
3. Prefer skills for repeatable execution steps.
4. Keep prompts as short, stable wrappers while the repo transitions toward skills.
5. Update workflow docs together when a skill or prompt boundary changes.
