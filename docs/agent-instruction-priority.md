# Agent Instruction Priority

This document records how agent instructions should be interpreted in this repository. It is a repo-level reference for future SoundAtlas work; it does not override system or developer instructions.

## Priority Order

1. System instructions

   Highest priority. These come from the platform and cannot be configured by this repository.

   SoundAtlas example: tool safety, browsing rules, copyright limits, and the rule that system instructions override developer, repo, prompt, and user text.

   Configurable: no.

2. Developer or agent instructions

   These define how the agent should behave in the current environment. They are not stored in `/workspace`.

   SoundAtlas example: the default behavior that says the agent should generally implement unless the user explicitly asks for a plan, asks a question, is brainstorming, or otherwise makes clear that code should not be written.

   Configurable: not from the repository. Repo instructions can clarify what counts as a planning-only signal, but cannot directly reorder or delete developer instructions.

3. Current user request

   The latest user message controls the immediate task unless it conflicts with higher-priority instructions.

   SoundAtlas example: `use prompts/design-ux.md on the active route display above the map` should be interpreted through that prompt's output boundary. A later request such as `revert this change` explicitly authorizes reverting the prior implementation.

   Configurable: yes, through clear request wording such as `plan only`, `do not edit files`, `implement this approved plan`, or `implement from this local plan record`.

4. Repo instructions in `AGENTS.md`

   These are the repository-wide SoundAtlas rules.

   SoundAtlas examples:

   - Feature work follows the implementation-plan workflow in `docs/implementation-plan-workflow.md`.
   - The map is the primary interface.
   - Frontend changes run `npm run check`.
   - Backend changes run `uv run pytest`.
   - Commits require an explicit user request.

   Configurable: yes. This is the strongest repository-controlled place for broad agent guardrails.

5. Triggered skill instructions

   Skills apply when the task matches the skill description or the user names the skill.

   SoundAtlas example: `.codex/skills/soundatlas-spec-planning/SKILL.md` says to draft local implementation plan records for non-trivial UX, frontend, backend, data, documentation, and cross-cutting changes, then stop before implementation.

   Configurable: yes, by editing repo skills or adding new skills. Skill priority itself cannot be raised above system, developer, user, or repo instructions.

6. Prompt file instructions

   Prompt files guide a specific workflow when the user asks to use them.

   SoundAtlas example: `prompts/design-ux.md` says UX prompts produce audit findings, critique, and UX slice proposals, and do not authorize implementation.

   Configurable: yes, by editing prompt files. Prompt boundaries should be kept explicit when a prompt is planning-only.

7. Workflow docs and design baselines

   These are supporting repository documents that define process and product intent.

   SoundAtlas examples:

   - `docs/implementation-plan-workflow.md` says not to implement from vague requests, and to implement from approved plans, local plan records, or clearly trivial requests.
   - `docs/skills-workflow.md` maps UX audit work to `prompts/design-ux.md`.
   - `docs/design/current-frontend-design.md` records the intended frontend design baseline.

   Configurable: yes. These documents are stronger when `AGENTS.md` points to them clearly.

8. Existing codebase patterns

   These guide implementation only after implementation is authorized.

   SoundAtlas examples:

   - Shared frontend exploration state lives in `frontend/src/routes/+page.svelte`.
   - Domain components include `MapView`, `Timeline`, `RouteFilter`, and `StoryPanel`.
   - Seed data comes from `data/seed/`.
   - Backend API responses use typed schemas.

   Configurable: indirectly, by changing the codebase. This is convention, not an instruction layer.

## Repo Configuration Guidance

The top instruction levels cannot be reordered by the repository. The effective fixed order is system instructions, developer instructions, current user request, then repository and workflow instructions.

The repository can still reduce ambiguity by documenting local interpretation rules. In SoundAtlas, `AGENTS.md` includes prompt authorization rules:

```md
## Prompt Authorization Rules

- When the user asks to use a prompt file, read and follow that prompt's stated output boundary.
- If a prompt says it produces audit findings, critique, plans, or proposals, do not edit code, data, or docs in that turn unless the user explicitly authorizes implementation after receiving the plan.
- For UX/design prompts, default to inspection, findings, and a proposed UX slice, then stop.
```

This rule clarifies that a planning-only prompt counts as a clear signal that code should not be written in that turn.
