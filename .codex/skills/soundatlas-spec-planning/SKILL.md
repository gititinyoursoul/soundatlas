---
name: soundatlas-spec-planning
description: Draft or revise SoundAtlas spec records and implementation plans for frontend, backend, data, documentation, UX, or cross-cutting changes. Use when the user explicitly asks for a spec, when a generated spec record would help later analysis, or when an existing SoundAtlas spec family needs a new revision, clarified assumptions, or a requirement-mapped plan.
---

# SoundAtlas Spec Planning

Read the repo context before drafting a spec. Start with:

- `AGENTS.md`
- `docs/spec-first-agent-workflow.md`
- `docs/skills-workflow.md`
- `specs/template.md`
- the relevant existing spec family under `specs/`, if one exists

Read `prompts/plan-feature.md` only when you need the legacy wrapper wording or a reminder of the planning output shape.

## Workflow

1. Classify the request.
   Use this skill when a spec record is requested or useful. The default day-to-day workflow is plan-led and does not require a spec gate.

2. Inspect for an existing spec family before creating a new one.
   Reuse an existing feature slug when the request extends the same user-facing behavior, workflow, or ownership boundary.

3. Choose the feature slug.
   Use a short, stable, hyphenated feature name.
   Prefer behavior names over implementation names.
   Avoid route-specific or temporary wording unless the feature is truly route-specific.

4. Choose the revision path.
   Use `specs/<feature-slug>/rNN-<short-desc>.md`.
   If the family exists, increment the highest existing `rNN`.
   If the family does not exist, start at `r01`.
   Keep the short description stable, concrete, and behavior-focused.

5. Draft the spec.
   Use the repo template shape:
   `Request`, `Goal`, `Non-goals`, `Requirements`, `Acceptance criteria`, `Assumptions`, `Open questions`.
   Keep it short, practical, and concrete.

6. Make assumptions instead of blocking on low-risk ambiguity.
   Separate assumptions from open questions.
   Block only on high-risk uncertainty such as destructive writes, schema changes, seed shape changes, security, privacy, external API behavior, historically sensitive claims, or irreversible workflow changes.

7. Produce the implementation plan after the spec record.
   Map implementation steps to requirement IDs such as `R1`, `R2`, `R3`.
   Map validation to acceptance criteria such as `AC1`, `AC2`, `AC3`.
   Keep the plan decision-complete enough that an implementation skill or engineer can execute without inventing product behavior.

8. Stop before implementation.
   Do not write code, edit non-spec files, or expand into backend, frontend, docs, or test execution.

## Planning Rules

- Keep approved plans as the default source of truth for implementation. Use specs as records for product intent, verification, and later analysis.
- Do not define behavior outside the requested change.
- Prefer small, reviewable revisions over broad rewrites.
- If implementation reveals missing behavior, update the generated spec record when the detail is low-risk; stop for approval when the change affects product intent or another high-risk boundary.
- For cross-cutting changes, plan in this order: data or schema impact, backend impact, frontend state impact, UX impact, tests or checks, docs or TODO updates.

## Output

Return the planning result in this order:

1. Proposed spec path
2. Assumptions
3. Open questions, if any remain
4. Spec draft
5. Implementation plan mapped to `R*`
6. Validation plan mapped to `AC*`
7. Next step: approve the plan for implementation, or review the spec record if the user asked for one

If the request is truly trivial, say so briefly and explain why a spec is not needed.
