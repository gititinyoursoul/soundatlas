# Refactor Large

Use this prompt when planning or performing a large SoundAtlas refactor that touches several files or changes project structure.

Context to provide
- Goal of the refactor and why it is needed now.
- Affected area: backend, frontend, seed data, docs, or repo structure.
- Intended new layout or old path -> new path mapping.
- Behavior and data contracts that must remain stable.
- What is explicitly out of scope.

Task
- Perform the refactor with minimal breakage and a reviewable, incremental approach.

Project constraints
- Preserve runtime behavior unless explicitly requested.
- Preserve seed data contracts from `docs/seed-validation.md`.
- Keep API response shapes stable once frontend code depends on them.
- Avoid changing curated content while doing structural refactors.
- Avoid broad formatting and unrelated cleanup.
- Prefer mechanical, searchable changes. Use `rg` for imports, paths, and references.

Process
- Start with a short plan and name risk points: imports, API routes, seed loading, schemas, frontend state, docs, tests.
- Break work into small staged groups, usually 1-3 commits.
- Update `AGENTS.md`, `TODO.md`, or docs only when the refactor changes actual workflow or structure.
- For backend structure changes, update `pyproject.toml`, imports, tests, and app entrypoints.
- For frontend structure changes, update component imports, route files, and API client wiring.
- For seed structure changes, update `docs/seed-validation.md` before changing data.
- Run the most targeted available validation and report results.

Deliverables
- Code changes implementing the new structure.
- Updated tests and docs where needed.
- Staged-files grouping plan and suggested commit message(s).
- Validation commands run and outcome.
