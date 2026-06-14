# Refactor Improve Testability

Use this prompt when SoundAtlas code should become easier to test without changing behavior.

Context to provide
- Target files and current testing pain points.
- Behaviors that must be locked down.
- External dependencies to isolate: filesystem seed reads, API clients, map libraries, browser APIs, or network calls.

Task
- Refactor to improve testability while preserving behavior.

Project constraints
- Preserve API output, seed parsing behavior, and frontend user-visible behavior.
- Prefer small pure helpers for filtering, validation, and data mapping.
- Inject dependencies through parameters where useful, especially seed paths and fetch clients.
- Do not introduce heavy dependencies unless explicitly requested.
- Do not change curated content while improving testability.

Process
- Start with a short plan.
- Identify the behavior to preserve before editing.
- Add or update tests around seed loading, filtering, validation, API responses, or frontend data transforms.
- Keep call sites stable when possible.
- Run targeted tests, preferably `uv run pytest` for backend work.

Deliverables
- Code changes plus tests demonstrating improved testability.
- Brief explanation of introduced seams and why they help.
- Validation run and outcome.
- Suggested commit message.
