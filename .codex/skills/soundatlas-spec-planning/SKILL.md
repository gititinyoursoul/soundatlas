---
name: soundatlas-spec-planning
description: Draft or revise SoundAtlas feature specs and implementation plans for non-trivial frontend, backend, data, documentation, UX, or cross-cutting changes. Use when a request should become an approved spec revision under the SoundAtlas specs directory before implementation, or when an existing SoundAtlas spec family needs a new revision, clarified assumptions, or a requirement-mapped plan.
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
   Treat the skill as the default path for non-trivial feature work, UX behavior changes, backend/API changes, seed or enrichment workflow changes, documentation behavior changes, and cross-cutting work.

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

7. Produce the implementation plan after the spec.
   Map implementation steps to requirement IDs such as `R1`, `R2`, `R3`.
   Map validation to acceptance criteria such as `AC1`, `AC2`, `AC3`.
   Keep the plan decision-complete enough that an implementation skill or engineer can execute without inventing product behavior.

8. Stop before implementation.
   Do not write code, edit non-spec files, or expand into backend, frontend, docs, or test execution.

## Planning Rules

- Keep specs as the source of truth for product intent.
- Do not define behavior outside the requested change.
- Prefer small, reviewable revisions over broad rewrites.
- If implementation reveals missing behavior, draft a new revision instead of editing the approved revision in place.
- For cross-cutting changes, plan in this order: data or schema impact, backend impact, frontend state impact, UX impact, tests or checks, docs or TODO updates.

## Output

Return the planning result in this order:

1. Proposed spec path
2. Assumptions
3. Open questions, if any remain
4. Spec draft
5. Implementation plan mapped to `R*`
6. Validation plan mapped to `AC*`
7. Next step: usually review and approve the proposed spec revision, then use the relevant implementation, test, docs, or UX workflow

If the request is truly trivial, say so briefly and explain why a spec is not needed.
