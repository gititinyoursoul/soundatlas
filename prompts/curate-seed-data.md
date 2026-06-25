# Curate Seed Data

Use this prompt when adding or updating curated SoundAtlas seed data.

Context to provide
- Route or topic to add, e.g. `birth-of-hip-hop`.
- Intended time range, places, events, and connections.
- Source material or known uncertainty.
- Whether this is draft content or publication-ready content.

Task
- Add or update seed data under `data/seed/`.

Project constraints
- Follow `docs/seed-validation.md`.
- Preserve stable IDs once frontend or backend code may reference them.
- Use `review_status: "draft"` unless the user explicitly asks for reviewed content.
- Always model `source_urls` and `media_links` as arrays.
- Do not add local audio files, images, or scraped media.
- Be careful with contested historical claims; mark uncertainty in wording rather than overstating.

Process
- Check the route concept in `docs/routes/` and MVP scope in `docs/mvp-concept.md`.
- Update the smallest necessary set of seed files: routes, places, events, connections.
- Keep event wording concise: `summary` for what happened, `significance` for why it matters.
- Validate JSON syntax and cross-references if tooling is available.
- Update `TODO.md` only for tasks that are actually completed.

Deliverables
- Updated seed files.
- Any updated route or validation docs.
- Validation run and outcome.
- Suggested commit message, usually `data: ...`.
