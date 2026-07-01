---
name: soundatlas-spec-planning
description: Draft or revise SoundAtlas local implementation plan records and implementation plans for frontend, backend, data, documentation, UX, or cross-cutting changes. Use when the user explicitly asks for a saved local plan record, or when approved non-trivial work should be preserved for later revision and commit linkage.
---

# SoundAtlas Local Plan Planning

Read the repo context before drafting a local implementation plan record. Start with:

- `AGENTS.md`
- `docs/implementation-plan-workflow.md`
- `docs/skills-workflow.md`
- `plans/template.md`
- `plans/README.md`

Read `prompts/plan-feature.md` only when you need the legacy wrapper wording or a reminder of the planning output shape.

## Workflow

1. Classify the request.
   Use this skill when a local implementation plan record is requested or useful. The default day-to-day workflow is plan-led and does not require a separate planning gate beyond plan approval.

2. Inspect for an existing local plan record only when the user is extending the same in-progress local plan.
   Otherwise create a new plan ID.

3. Choose the short slug.
   Use a short, stable, hyphenated behavior name.
   Prefer behavior names over implementation names.
   Avoid route-specific or temporary wording unless the work is truly route-specific.

4. Choose the local record path.
   Use `plans/records/P-###-<short-slug>.md`.
   Allocate the next sequential `P-###` ID by inspecting existing local records.
   Keep the short slug stable, concrete, and behavior-focused.

5. Draft the local plan record.
   Use the repo template shape from `plans/template.md`.
   Keep it short, practical, and concrete.

6. Make assumptions instead of blocking on low-risk ambiguity.
   Separate assumptions from open questions.
   Block only on high-risk uncertainty such as destructive writes, schema changes, seed shape changes, security, privacy, external API behavior, historically sensitive claims, or irreversible workflow changes.

7. Produce the implementation plan inside the local plan record.
   Map implementation steps to requirement IDs such as `R1`, `R2`, `R3`.
   Map validation to acceptance criteria such as `AC1`, `AC2`, `AC3`.
   Keep the plan decision-complete enough that an implementation skill or engineer can execute without inventing product behavior.

8. Stop before implementation.
   Do not write code, edit non-plan files, or expand into backend, frontend, docs, or test execution.

## Planning Rules

- Keep approved plans as the default source of truth for implementation. Use local plan records as local records for product intent, verification, and later analysis.
- Do not define behavior outside the requested change.
- Prefer small, reviewable revisions over broad rewrites.
- If implementation reveals missing behavior, update the generated local plan record when the detail is low-risk; stop for approval when the change affects product intent or another high-risk boundary.
- For cross-cutting changes, plan in this order: data or schema impact, backend impact, frontend state impact, UX impact, tests or checks, docs or TODO updates.

## Output

Return the planning result in this order:

1. Proposed local plan record path
2. Assumptions
3. Open questions, if any remain
4. Local plan record draft
5. Implementation plan mapped to `R*`
6. Validation plan mapped to `AC*`
7. Next step: approve the plan for implementation, or review the local plan record if the user asked for one

If the request is truly trivial, say so briefly and explain why a local plan record is not needed.
