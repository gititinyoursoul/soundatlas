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
- Follow `docs/content/event-editorial-quality-standards.md` before adding or
  revising event seed records.
- Preserve stable IDs once frontend or backend code may reference them.
- Use `review_status: "draft"` unless the user explicitly asks for reviewed content.
- Always model `source_urls` and `media_links` as arrays.
- Do not add local audio files, images, or scraped media.
- Be careful with contested historical claims; mark uncertainty in wording rather than overstating.

Process
- If the seed work is non-trivial, use `prompts/grill-me.md` first to check
  draft/publish boundaries, source risk, route fit, and data-shape risk, then
  use `soundatlas-implementation-planning` to create or update a GitHub Issue
  Plan Update before multi-file data changes.
- Check the route content in `docs/content/routes/<route-id>/` for new route
  work, or the existing legacy concept in `docs/content/route-concepts/`, plus
  MVP scope in `docs/mvp-concept.md`.
- When the route folder has `pipeline.json`, inspect pipeline status and any
  `seed-transfer-report.md` or `validation-report.md` before editing seed data.
- When the route folder has `accepted-events.md`, use it as the editorial
  handoff for seed-authoring inputs. Do not convert unresolved `maybe`,
  unresolved `merge`, or `reject` candidates into seed records.
- Use the editor-facing candidate review vocabulary: `keep`, `maybe`, `merge`,
  and `reject`. Treat older `develop`, `context`, and `defer` labels as draft
  labels only, not approval for seed authoring.
- Before adding or revising event seed records, run an event editorial quality
  pass. Confirm the event comes from an accepted-event dossier, reviewed route
  artifact, or explicit human instruction; has an inclusion rationale and route
  fit; has place and year specificity; uses `summary` for what happened and
  `significance` for why it matters here; and preserves cautious wording for
  contested or weakly sourced claims.
- Do not use seed authoring to resolve candidate review. If candidate status is
  unclear, stop at a proposal and ask for human review instead of editing
  `data/seed/`.
- Keep candidate decisions and seed `review_status` separate. A `keep` event
  can still become a seed record with `review_status: "draft"`; `review_status`
  does not replace `accepted-events.md`.
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
