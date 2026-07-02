# Create Route

Use this prompt when creating a new curated SoundAtlas route from idea to route concept and seed data plan.

Context to provide
- Route topic, e.g. `Disco to Dance Music`, `Punk & New Wave`, or `Salsa & Migration`.
- Intended geography and time range.
- Why this route matters for the current SoundAtlas scope.
- Known source material, uncertainty, or contested claims.
- Known artists, groups, venues, influences, circumstances, or source leads.
- Related GitHub Issue number or URL, if this route work is part of broader approved work.
- Whether the output should be concept-only or should also update seed files.

Task
- Create a researched route concept that can become SoundAtlas seed data.
- For new route content, create or update a route folder under
  `docs/content/routes/<route-id>/`.
- Create or update a Route Research Dossier before seed transfer.
- If requested, add the route to `data/seed/` while preserving existing data contracts.

Project constraints
- Keep the MVP focused on `New York 1965-1985` unless explicitly requested.
- Follow `AGENTS.md` and `docs/data/seed-data-validation.md`.
- Preserve existing route, place, event, and connection IDs.
- Use stable, lowercase, URL-safe IDs with hyphens.
- Mark early editorial data with `review_status: "draft"`.
- Keep `source_urls` and `media_links` as arrays.
- Keep `media_links` as structured media objects when adding external media.
- Do not add local audio, video, image, or scraped media files.
- Avoid overstating disputed historical claims; phrase uncertainty clearly.
- Write all new route-facing content in English: route titles, UI copy, event titles, event summaries, significance text, tags, and related prompt output.
- If the existing documentation for the route is in another language, translate the route-facing parts to English before creating seed data.

Route concept requirements
- Follow `docs/content/route-editorial-quality-standards.md`.
- Use `docs/content/route-research-dossier-template.md` as the default Route
  Research Dossier format.
- Start new route work with a concise `brief.md` that frames the route idea,
  why it matters, the initial question, thesis hypothesis, research targets,
  candidate anchors, known risks, and dossier questions.
- Keep candidate anchors in `brief.md` clearly labeled as not-final seed
  events.
- Define a short route title and stable `id`.
- Define a route `creator`.
- Define the route's central question.
- Define a route thesis in one or two sentences.
- Split the route into 2-4 time phases.
- Add a Route Research Dossier section that identifies key artists, groups,
  places, venues, influences, circumstances, candidate events, and candidate
  connections.
- Include research into editorial sources, media sources, and image sources as
  separate dossier sections.
- Identify primary places and explain their role.
- Propose candidate events for the route, then identify the strongest seed
  candidates after dossier review.
- Propose candidate connections that explain influence, context, media spread,
  or scene formation, then narrow them during seed-transfer planning.
- Define useful tags for filtering and UI display.
- List content risks and claims that need source review.
- Identify likely sources for further editorial work.

Seed data requirements
- Add or update `data/seed/routes.json` for the route metadata.
- Set route `creator` explicitly.
- Add or reuse places in `data/seed/places.json`.
- Add events in `data/seed/events.json`.
- Add connections in `data/seed/connections.json`.
- Reuse existing places when the same real-world place already exists.
- Keep event `summary` focused on what happened.
- Keep event `significance` focused on why it matters for the route.
- Keep every new event title, summary, significance, and route description in English.
- Keep any route-specific interface labels, captions, and helper text in English when generating UI-facing copy.
- For event media, use structured entries with `provider`, `type`, `title`, `url`, `query`, `confidence`, and `review_status`.

Recommended workflow
- For non-trivial route creation or route reshaping, use `prompts/plan-feature.md` first and create or update a GitHub Issue Plan Update before broad seed edits.
- For new route content, first create or update
  `docs/content/routes/<route-id>/brief.md`.
- Keep later route-specific files in `docs/content/routes/<route-id>/`. A
  route folder may contain `brief.md`, a research dossier, a concept file, and
  route-specific notes.
- Existing route concepts in `docs/content/route-concepts/` remain valid
  legacy/current content until a separate migration.
- Add or revise the Route Research Dossier before selecting final event and
  connection candidates, using `docs/content/route-research-dossier-template.md`
  as the default structure.
- Then map the researched concept into seed data.
- Validate JSON syntax.
- Validate references between routes, places, events, and connections.
- Capture new planned follow-up work in GitHub Issues. Leave legacy `TODO.md` entries alone unless the approved Issue or plan explicitly includes legacy backlog cleanup.

Deliverables
- Route content folder under `docs/content/routes/<route-id>/` for new route
  content.
- `brief.md` for fresh route work, before dossier creation or seed transfer.
- Route concept document, either in the route folder for new work or under
  `docs/content/route-concepts/` for legacy/current concepts.
- Route Research Dossier section covering artists/groups, places/venues,
  influences, circumstances, event rationale, connection rationale, editorial
  source leads, media source leads, image source leads, and unresolved risks.
- Seed data changes if requested.
- Related GitHub Issue note, when used.
- Notes on unresolved source or content questions.
- Validation command run and outcome.
- Suggested commit grouping:
  - `docs: add <route> route concept`
  - `data: add <route> seed data`
  - `docs: update route workflow notes`
  - If implementing from an Issue, reference it in the commit body, for example `Issue: #123`

Acceptance criteria
- The route has a clear narrative thesis.
- The route has a research dossier that explains the artists, groups, places,
  influences, circumstances, source directions, and risks behind the route.
- The route can be explored chronologically and geographically.
- Every proposed event has a place, time range, summary, and significance.
- Every proposed event has an inclusion rationale before seed transfer.
- Every connection explains a useful relationship, not just adjacency.
- Editorial, media, and image source research are separated before seed
  transfer.
- Data can be consumed by the existing FastAPI and SvelteKit map flow without schema changes.
