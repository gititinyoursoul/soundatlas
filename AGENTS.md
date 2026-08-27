# AGENTS.md

## Scope

These instructions apply to the entire repository.

## Communication Style

- Use clear, professional language suited to a technically informed reader.
- Prefer concrete, verifiable wording over bureaucratic or abstract language.
- Name the observed facts, specific actions, relevant artifacts, and direct
  consequences that support a statement.
- When explaining a decision or status, state what was observed, what conclusion
  follows, and what will happen next when applicable.
- Keep verified facts, assumptions, recommendations, and unchecked information
  distinguishable. If something has not been checked, say so directly.
- When work is blocked, name the exact missing information, action, or approval
  and explain how it would remove the blocker.
- When using an abstract label or formal workflow term, explain its concrete
  meaning through the relevant file, command, decision, condition, or
  consequence.
- Use common software terms without unnecessary explanation.
- Explain unfamiliar or SoundAtlas-specific terms when first used.
- Lead with what an action means, then name the formal process when useful.
- Keep responses concise, but include enough detail to understand decisions and tradeoffs.

## Project Context

SoundAtlas is an MVP for an interactive music history app. The first product scope is **New York 1965-1985**, with the vertical slice **Birth of Hip-Hop: Bronx 1970-1985**.

The app should make music history explorable across three axes:

- Place: map and places
- Time: timeline and time ranges
- Sound/culture: events, routes, connections, and sources

## Technical Stack

- Frontend: SvelteKit, TypeScript, Leaflet
- Backend: Python, `uv`, FastAPI
- MVP data: curated JSON seed files under `data/seed/`
- Optional later: SQLite or PostgreSQL/PostGIS

## Working Principles

- Keep changes small, reviewable, and aligned with the MVP scope.
- Build the vertical slice cleanly first before expanding additional routes.
- Prefer curated, traceable data over automated aggregation.
- Minimize human editorial input by having agents propose concrete decisions,
  rationales, merge targets, and review questions. Human review should approve,
  reject, or correct agent proposals rather than synthesize decisions from raw
  artifacts.
- Always include source fields in the data model, even if they remain empty in the internal MVP.
- Do not add audio files to the repository; use only external media links in the MVP.
- Do not commit secrets, tokens, or local paths.

## Lean MVP Guardrail

- Default to the smallest end-to-end change that satisfies the current request.
- SoundAtlas is currently a pre-user MVP. Do not design for scale, multi-user
  administration, generalized platforms, persistence, or speculative automation
  unless an approved Issue explicitly requires it.
- Prefer existing JSON files, CLI commands, route artifacts, and manual review
  over new services, state models, abstractions, or interfaces.
- Keep the first editorial review loop thin: preview the story, choose what
  belongs, notice warnings, and publish the route.
- During planning, identify the smallest useful slice and list platform-style
  behavior as a non-goal unless the approved scope requires it.
- Do not create or expand linked Issues for speculative future work unless the
  human explicitly requests it or the existing Issue workflow requires it.
- When a request can be satisfied by a local change within the approved scope
  and workflow gates, make that change and stop.

## Data Rules

Seed data lives under `data/seed/` and should keep a stable structure:

- `routes.json`: narrative routes
- `places.json`: places with coordinates
- `events.json`: historical events
- `connections.json`: influences and connections between events

IDs should be lowercase, stable, and URL-safe, for example `birth-of-hip-hop` or `1520-sedgwick-avenue`.

Events should contain at least:

- `id`
- `route_id`
- `place_id`
- `title`
- `year_start`
- `year_end`
- `summary`
- `significance`
- `source_urls`
- `media_links`

## Backend Rules

- FastAPI code should live under `backend/app/`.
- API responses should be typed with Pydantic schemas.
- Endpoints should read from the seed files in a data-driven way until a database is introduced.
- Run backend lint, type checks, and tests with `uv run ruff check .`, `uv run pyright`, and `uv run pytest`.

## Frontend Rules

- UI components should be small and domain-named, for example `MapView`, `Timeline`, `RouteFilter`, `StoryPanel`.
- The map is the primary interface of the MVP.
- Timeline, route filter, and story panel should use the same central data state.
- Do not build UI that only works with mock data when seed data already exists.

## Documentation

- Document product and architecture decisions in `docs/`.
- GitHub Issues are the source of truth for planned agent work.
- New planned work should be captured in an Intake Issue with `Task`, `Context`, and `Acceptance Criteria`.
- For feature work, follow the GitHub Issue workflow in `docs/github-issue-workflow.md`.
- At Intake, before accepting a consequential concept or Plan Update, when
  implementation reveals drift or new constraints, and before accepting
  completed implementation, perform a lightweight Grill-Me check. Continue
  without pausing when there is no material finding; use the interactive
  one-finding flow when human confirmation is needed.
- Use `.codex/skills/soundatlas-grill-me` for Grill-Me checks and explicit
  Grill-Me requests. It owns Review Mode selection, Phase Boundaries,
  Materiality routing, and the interactive one-finding flow.
- Use `.codex/skills/soundatlas-concept-work` when the human requests concept
  work or a Grill-Me check finds that planning would otherwise have to invent
  material target behavior, runtime responsibilities, boundaries, or ownership.
  Skip concept work for clear, local, low-risk changes.
- Use `.codex/skills/soundatlas-implementation-review` before accepting
  completed non-trivial Issue work, or during implementation when drift, risk,
  or a new material constraint requires review. Skip it for clearly trivial,
  local, low-risk changes. The skill is read-only and returns material human
  decisions to Grill Me.
- Record the implementation-review result inside the single
  `## Implementation Report` comment. Do not add a separate routine review
  comment or treat review as human commit approval.
- New Issues are intake records, not implementation-ready plans. Non-trivial
  Issue work requires a confirmed Plan Update before implementation; risky,
  vague, or cross-cutting work also requires Grill-Me review. The Plan must
  reference its accepted Concept or state why Concept Work was not required.
  Explicit wording such as `implement issue #<number>` does not bypass those
  gates. Clearly trivial, local, low-risk work may proceed directly.
- Use standardized Issue records: a standalone `## Grill-Me Review` for
  material findings, confirmed decisions, blockers, or explicit standalone
  sessions; `## Concept` when concept work is needed; `## Plan Update` or
  `## Detailed Plan Update`; `## Proceed to Implementation` after the Human
  confirms the latest Plan and authorizes its scope; and `## Implementation
  Report`. Clean lightweight checks may be recorded inline in the next action
  comment or omitted when no durable record is useful.
- Before planning, record scope changes as an `## Intake Revision` comment and
  rerun Grill-Me for material revisions; do not silently broaden an Intake.
- Plan Updates, Detailed Plan Updates, Proceed-to-Implementation records, and
  Implementation Reports should live in the GitHub Issue rather than local or
  repo-versioned plan files.
- Use `docs/workflow-registry.md` as the routing guide for repeatable execution work that should live in skills or prompt wrappers.
- Treat `docs/workflow-registry.md` as the authoritative policy for skill, prompt, compatibility-wrapper, and workflow-document boundaries; correct conflicts in the authoritative source rather than interpreting duplicated instructions.
- Use the repo skill at `.codex/skills/soundatlas-issue-planning` when an Issue
  needs an Intake structure, Plan Update, Detailed Plan Update, Proceed-to-
  Implementation record, or Implementation Report.
- Before the first repository edit for non-trivial Issue work, require a
  `## Proceed to Implementation` record that links the latest Plan and run
  `python scripts/check_issue_readiness.py` against the current exported Issue
  artifacts. Add `--require-grill-review` when risk flags require a recorded
  Grill-Me result. A Grill-Me `Next step` is routing, not implementation
  authorization.
- `TODO.md` is a legacy backlog and should not receive new planned work unless the user explicitly asks for a legacy note.
- If the scope changes, update `docs/mvp-concept.md` first and then create or update the relevant GitHub Issue.
- Codex may set existing approved GitHub labels on Issues. New labels must be proposed and explicitly approved before Codex creates or uses them.
- Track planned SoundAtlas Issues in the `Project Tracker` GitHub Project. Use
  its `Status` field as a visible summary, while Issue bodies and standardized
  comments remain authoritative: `Todo` while the Issue remains at Intake;
  `In Progress` after a required Concept is accepted, a Concept-not-required
  Plan is confirmed, or explicitly authorized trivial direct work begins;
  `Locally Implemented` after an accepted Implementation Report and reviewed
  local commit or range exist; and `Done` only after push, post-push
  verification, and the completion comment succeed. Project status does not
  replace the Issue's separate open or closed state.
- When creating a GitHub Issue, Codex should choose exactly one approved `priority:p*` label by reasoning from blocking level, MVP/release impact, risk reduction, and urgency. Use `priority:p2` only as the neutral fallback when `p0`, `p1`, or `p3` are not clearly justified, and briefly state the priority rationale.
- When creating a GitHub Issue, Codex should inspect existing open milestones and
  assign one only when completing the Issue directly advances the outcome stated
  by that milestone. Shared labels, a related product area, or an indirect
  benefit are not sufficient. Partial, indirect, multiple, or ambiguous matches
  should remain unassigned. Do not create or broaden milestones without explicit
  human approval. Report the milestone decision and rationale alongside the
  priority rationale.
- For editorial workflow changes, preserve the minimal-input review principle:
  agents should surface counts, recommendations, explicit options, and defaults
  before asking for human decisions.

## Prompt Authorization Rules

- When the user asks to use a prompt file, read and follow that prompt's stated output boundary.
- If a prompt says it produces audit findings, critique, plans, or proposals, do not edit code, data, or docs in that turn unless the user explicitly authorizes implementation after receiving the plan.
- For UX/design prompts, default to inspection, findings, and a proposed UX slice, then stop.

## Git Conventions

- After a successful commit-ready gate, automatically stage and create a local
  Issue-scoped commit. The gate requires relevant validation, approved-scope
  and prohibited-artifact checks, an index containing only that work package,
  and a Conventional Commit with an `Issue: #<number>` footer.
- Do not stage or commit into an index that already contains unrelated staged
  work; report it and preserve the existing index unchanged.
- A human must explicitly authorize `git push` after reviewing the named local
  commit or range. A push request for completed Issue work counts as approval
  to close the associated Issue unless the human explicitly says to keep it
  open.
- After an `Accepted` Implementation Report and review of the named local
  commit or range, set the Issue's Project Tracker status to `Locally
  Implemented` while it awaits push. If corrective work invalidates that
  result, return it to `In Progress`. After successful push, verification, and
  completion-comment posting, set Project status to `Done` and explicitly
  close the Issue. Project status does not replace Issue comments, push
  authorization, completion evidence, or the closed state.
- After a successful push, capture the published commit hash, verify all
  acceptance criteria, confirm that no Issue-relevant changes remain
  uncommitted, post the standard commit-referencing completion comment, and
  then close the Issue.
- Unrelated user-owned working-tree changes do not block closure and must not be included merely to make the tree clean.
- Do not push or close an Issue when review is not `Accepted`, work is
  uncommitted, the commit is partial or WIP, acceptance criteria remain
  incomplete, multiple Issues are ambiguously involved, or the user asks to
  keep the ticket open.
- If the push, completion comment, or close operation fails, report the failure
  and leave the Issue open when possible.
- A single agent may use the current branch. Independently active work packages
  must have an owned branch and worktree, with one CLI write owner per worktree.
  Integration and conflict resolution require explicit authorization; a changed
  integration range must be validated and reviewed before push.
- For non-trivial work, the Plan must declare a planned write boundary: exact
  named authoritative paths, a bounded derived-consistency surface for direct
  mechanical alignment, and excluded scope. `AGENTS.md` is always a named
  authority, never a derived update. The Proceed record lists the exact derived
  files found by the pre-write audit; implementation may edit only those files
  and the named authorities. Leave any other path or material scope change
  untouched and create a linked Intake Issue.
- Apply all named-authority and audited derived-file changes in one combined
  repository-edit request when practical; do not split an already authorized
  boundary by surface. This convention cannot suppress filesystem-sandbox,
  credential, or application-level confirmation prompts. Those prompts are
  execution-environment controls, not additional Issue approvals.
- Prefer one coherent Issue work package per commit.
- Keep local folders such as `.venv/`, `node_modules/`, `.vscode/`, and `.github/` ignored.

## Commit Messages

- Use Conventional Commits: `type(scope): subject`
- Allowed types: `feat`, `fix`, `refactor`, `perf`, `test`, `docs`, `build`, `ci`, `chore`, `revert`
- Scope is recommended but optional; if used, keep it short and stable
- Write subjects in the imperative and keep them under 72 characters when possible
- Do not end the subject with a period
- Use `!` for breaking changes, for example `feat(api)!: remove legacy endpoint`
- Add a short body when the reason is not clear
- When implementing from an Issue, include a commit body footer such as `Issue: #123`

## Working Defaults

- Prefer small, reviewable changes over large jumps
- When frontend code changes, run `npm run validate`; for larger changes, run `npm run validate:release` instead
- When backend code changes, run `uv run ruff check .`, `uv run pyright`, and `uv run pytest`
- When data or seed files change, check the JSON structure and references
- When new work packages arise, create or update the relevant GitHub Issue rather than `TODO.md`
