# Plans And Skills Workflow

SoundAtlas uses three lightweight layers for agent-driven work:

* Plans define the next implementation move and are the normal approval artifact.
* Local implementation plan records under `plans/records/` preserve implemented non-trivial plans for later revision. During solo work they are gitignored by default and normally remain uncommitted.
* Skills and prompts define reusable execution patterns for planning, implementation, tests, docs, and UX.

Prompts are compatibility entrypoints into those workflows. They should stay thin and should not redefine product behavior.

## Workflow Rules

* Do not implement from a vague request. Inspect the repo and create a concrete plan for non-trivial work.
* Implement from an approved plan, a local implementation plan record, or a clearly trivial request.
* Create a local implementation plan record for approved non-trivial work before implementation starts.
* Use a skill or prompt entrypoint to carry out the approved plan or local plan record.
* When a workflow repeats across multiple features, extract the repeatable part into a skill and leave the prompt as a wrapper if needed.
* Keep plan IDs and short slugs stable in local plan record paths.
* End every workflow result with a short `Next step` handoff when useful.

## Current Mapping

| Work type | Source of truth | Current entrypoint |
| --- | --- | --- |
| Conversational planning | feature request + repo inspection | direct agent plan, optionally supported by `prompts/plan-feature.md` |
| Local implementation plan record creation | approved plan or explicit record request | `soundatlas-spec-planning` at `.codex/skills/soundatlas-spec-planning`, wrapped by `prompts/plan-feature.md` |
| Backend implementation | approved plan or local plan record | `prompts/implement-backend-api.md` when useful |
| Frontend implementation | approved plan or local plan record | `prompts/implement-frontend-map.md` when useful |
| Test planning and implementation | approved plan or local plan record | `prompts/write-tests.md` |
| Durable documentation | approved plan, local plan record, or workflow change | `prompts/update-docs.md` |
| UX audit and critique | current frontend and design baseline | `prompts/design-ux.md` |

## Migration Guidance

1. Prefer conversational plans for day-to-day development.
2. Use local implementation plan records for later analysis and verification.
3. Prefer skills for repeatable execution steps.
4. Keep prompts as short, stable wrappers while the repo transitions toward skills.
5. Update workflow docs together when a skill or prompt boundary changes.
