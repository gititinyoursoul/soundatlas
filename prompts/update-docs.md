# Update Docs

Use this prompt when updating durable SoundAtlas documentation that should stay aligned with product, architecture, or workflow changes.

This prompt is the documentation entrypoint for the current workflow. If the repo has a matching docs skill, use that skill's instructions and keep this prompt as the compatibility wrapper.

## Context to provide

* Target docs or documentation area.
* Why the documentation needs to change now.
* Related feature, local implementation plan record, workflow, or code change.
* Whether the docs change should update the local implementation plan record or commit guidance.
* Whether the task is documentation-only or accompanies another change.
* Constraints on wording, scope, or source of truth.

## Task

Inspect the current documentation first, then produce a small documentation plan or make the approved documentation edits.

Do not treat this as a generic cleanup prompt. Use it for durable docs that other prompts or workflows rely on.

## When to use

Use this prompt for:

* `docs/implementation-plan-workflow.md`
* `docs/design/current-frontend-design.md`
* `docs/mvp-concept.md`
* route concept docs under `docs/routes/`
* workflow docs under `docs/`
* durable archive docs such as `docs/done.md`

Do not use it for:

* Trivial copy edits
* Pure formatting cleanup
* Comments-only changes
* Code changes that merely mention docs as a side effect

## Document categories

Classify the target docs before editing:

* Source of truth
* Derived guidance
* Workflow / process
* Archive / history

Preserve the role of the document. Do not turn an archive into a source of truth or duplicate one source across multiple files.

## Planning rules

If the documentation change is non-trivial:

1. Inspect the relevant source docs and related prompts.
2. Identify what is authoritative and what must stay consistent.
3. List the exact documentation changes needed.
4. Note any related code, prompt, workflow, local plan record, or commit-guidance updates that should happen together.

If the documentation update is trivial, make the smallest change directly.

## Project constraints

* Keep wording concise and aligned with repo conventions.
* Preserve source-of-truth documents unless the change explicitly updates them.
* Avoid broad rewrites or style-only edits.
* Do not change curated content unless the task explicitly asks for it.
* When the workflow changes, keep prompts, skills, `AGENTS.md`, and workflow docs aligned in the same pass.
* When documentation supports implemented plan work, keep plan-record and commit-reference examples consistent with `plans/README.md`.
* Do not commit changes unless explicitly requested.

## Deliverables

For planning-only requests, return:

1. A short summary of the documentation target.
2. Document category and source-of-truth relationship.
3. Planned edits.
4. Related docs, prompts, skills, or plan-record guidance to update together.
5. Risks or ambiguities.
6. Next step: approve the documentation plan or identify the missing source of truth.

For implementation requests, return:

1. Updated documentation.
2. Notes on what was changed and why.
3. Validation or review notes if relevant.
4. Note any related local implementation plan record or commit-message guidance that also changed.
5. Next step: commit the docs or continue with the related implementation-plan, implementation, or test workflow.
