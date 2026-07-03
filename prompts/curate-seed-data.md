# Curate Seed Data

Use this prompt when adding or updating curated SoundAtlas seed data.

Context to provide
- Route or topic to add, e.g. `birth-of-hip-hop`.
- Intended time range, places, events, and connections.
- Source material or known uncertainty.
- Related GitHub Issue number or URL, if this seed work belongs to broader approved work.
- Whether this is draft content or publication-ready content.

Task
- Add or update seed data under `data/seed/`.

Project constraints
- Follow `docs/data/seed-data-validation.md`.
- Preserve stable IDs once frontend or backend code may reference them.
- Use `review_status: "draft"` unless the user explicitly asks for reviewed content.
- Always model `source_urls` and `media_links` as arrays.
- Do not add local audio files, images, or scraped media.
- Be careful with contested historical claims; mark uncertainty in wording rather than overstating.

Process
- If the seed work is non-trivial, use `prompts/plan-feature.md` first and create or update a GitHub Issue Plan Update before multi-file data changes.
- Check the route content in `docs/content/routes/<route-id>/` for new route
  work, or the existing legacy concept in `docs/content/route-concepts/`, plus
  MVP scope in `docs/mvp-concept.md`.
- When the route folder has `pipeline.json`, inspect pipeline status and any
  `seed-transfer-report.md` or `validation-report.md` before editing seed data.
- Treat raw `*.ai-draft.*` files as local drafts. Use only reviewed
  route-folder variants as seed-authoring inputs.
- Update the smallest necessary set of seed files: routes, places, events, connections.
- Keep event wording concise: `summary` for what happened, `significance` for why it matters.
- Validate JSON syntax and cross-references if tooling is available.
- Capture new planned follow-up work in GitHub Issues. Leave legacy `TODO.md` entries alone unless the approved Issue or plan explicitly includes legacy backlog cleanup.

Deliverables
- Updated seed files.
- Any updated route or validation docs.
- Pipeline or reviewed-variant note when route-folder automation informed the
  seed changes.
- Related GitHub Issue note, when used.
- Validation run and outcome.
- Suggested commit message, usually `data: ...`.
- If implementing from an Issue, include a commit body footer such as `Issue: #123`.
