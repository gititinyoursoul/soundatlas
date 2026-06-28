# AGENTS.md

## Scope

These instructions apply to the entire repository.

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
- Always include source fields in the data model, even if they remain empty in the internal MVP.
- Do not add audio files to the repository; use only external media links in the MVP.
- Do not commit secrets, tokens, or local paths.

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
- Run tests, when present, with `uv run pytest`.

## Frontend Rules

- UI components should be small and domain-named, for example `MapView`, `Timeline`, `RouteFilter`, `StoryPanel`.
- The map is the primary interface of the MVP.
- Timeline, route filter, and story panel should use the same central data state.
- Do not build UI that only works with mock data when seed data already exists.

## Documentation

- Document product and architecture decisions in `docs/`.
- The current task list lives in `TODO.md`.
- For feature work, follow the plan-led workflow in `docs/spec-first-agent-workflow.md`.
- Implementation may start from an approved conversational plan, an explicitly provided spec, or a clearly trivial request.
- Specs in `specs/<feature-slug>/rNN-<short-desc>.md` are optional records for analysis and traceability, not mandatory approval gates.
- Use `docs/skills-workflow.md` as the routing guide for repeatable execution work that should live in skills or prompt wrappers.
- Use the repo skill at `.codex/skills/soundatlas-spec-planning` when a spec record is requested or useful.
- If the scope changes, update `docs/mvp-concept.md` first and then `TODO.md`.

## Prompt Authorization Rules

- When the user asks to use a prompt file, read and follow that prompt's stated output boundary.
- If a prompt says it produces audit findings, critique, plans, or proposals, do not edit code, data, or docs in that turn unless the user explicitly authorizes implementation after receiving the plan.
- For UX/design prompts, default to inspection, findings, and a proposed UX slice, then stop.

## Git Conventions

- Do not make commits without an explicit user request.
- Prefer meaningful commit groups: documentation, data, backend, and frontend separately.
- Keep local folders such as `.venv/`, `node_modules/`, `.vscode/`, and `.github/` ignored.

## Commit Messages

- Use Conventional Commits: `type(scope): subject`
- Allowed types: `feat`, `fix`, `refactor`, `perf`, `test`, `docs`, `build`, `ci`, `chore`, `revert`
- Scope is recommended but optional; if used, keep it short and stable
- Write subjects in the imperative and keep them under 72 characters when possible
- Do not end the subject with a period
- Use `!` for breaking changes, for example `feat(api)!: remove legacy endpoint`
- Add a short body when the reason is not clear

## Working Defaults

- Prefer small, reviewable changes over large jumps
- When frontend code changes, run `npm run check`; for larger changes, also run `npm run build`
- When backend code changes, run `uv run pytest`
- When data or seed files change, check the JSON structure and references
- When new work packages arise, update `TODO.md`
