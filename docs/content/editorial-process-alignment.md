# Editorial Process Alignment

## Purpose

This note records how the current SoundAtlas editorial system aligns with a
simpler route-centered editorial process.

The intended process is:

```text
route idea
-> route brief
-> candidate event longlist
-> complete route draft
-> private human route review
-> source and media enrichment
-> exact-result publication
-> publishable event cards
-> map, timeline, route, and story panel
```

For the current MVP, a route and a cultural theme are treated as the same
working unit. A route is the cultural theme plus its editorial argument,
geography, time range, candidate events, and eventual publishable path through
the app. A separate `Theme` object is not needed until the product needs
multiple routes under one broader umbrella.

## Current Workflow

SoundAtlas currently uses a route-first workflow:

1. Route scope starts in `docs/mvp-concept.md`, legacy route concepts under
   `docs/content/route-concepts/`, or a route folder under
   `docs/content/routes/<route-id>/`.
2. New route work begins with `brief.md`, which works as the route/theme brief.
3. A route research dossier gathers artists, places, influences, candidate
   events, candidate connections, source leads, media leads, image leads, and
   editorial risks.
4. `candidate-outline.json` preserves the agent-generated candidate outline;
   `complete-draft.json` holds one coherent generated route result that may
   revise roster membership and sequence.
5. `event-list.md` and `event-list.json` expose the active complete-draft
   proposals for review.
6. `route-review.json` holds one exact private review result with the active
   seed-shaped event, place, and connection bundle; Draft, Approved, and Don’t
   use state; technical readiness; and minimal dormant decisions across
   regeneration. The editorial StoryPanel renders this event content directly,
   while candidate planning fields and findings remain separate review context.
   Event rows show warning and blocking-error counts, selected-event review
   shows each full finding, and the route publication summary counts findings
   only from included Draft or Approved events. Don’t use events remain visible
   for review without affecting those route counts.
7. `accepted-events.json` and `accepted-events.md` remain legacy deterministic
   handoff artifacts and do not determine private route state.
8. `route-concept.md`, `event-framing.*`, `place-framing.json`, and
   `connection-framing.json` materialize the active complete draft.
9. `seed-transfer-report.md` and `validation-report.md` preview structural
   seed changes before promotion.
10. `data/seed/` is the runtime source for the map, timeline, route switching,
   event inspector, sources, media links, and image links. Existing
   Connections remain readable as compatibility data but are deferred from the
   supported MVP experience.
11. Enrichment scripts can create event-search components, media query plans,
   YouTube result files, draft `media_links`, and draft `image_links`.
12. The app has an internal media/image review queue for marking draft links as
   reviewed or rejecting them.

The documentation consistently says generated route artifacts are drafts and
that human editorial review decides which claims, events, places, and links
are ready for seed promotion. Connections are currently deferred because their
implementation adds complexity without enough developed user value.

`soundatlas-grill-me` is the recommended critique gate before non-trivial
editorial planning, candidate selection, enrichment, or seed promotion. It
supports human review by surfacing weak claims, unclear candidate boundaries,
source risks, premature automation, and missing acceptance criteria. It does
not replace the human editor or authorize publication.

## Alignment Table

| Simplified process step | Current system support | Alignment status | Notes |
| --- | --- | --- | --- |
| Choose a cultural theme | Route topic, route concept, or route folder | Aligned | Route is the current theme unit. |
| Generate a theme brief | `brief.md` in a route folder | Aligned | Keep calling this a route brief for now. |
| Generate candidate events | Dossier candidate table and `event-list.json` | Aligned | Candidate events are visible before seed promotion. |
| Review candidates manually | Docs require artifact inspection | Partial | The review point exists, but it is not strongly modeled. |
| Suggest Keep / Maybe / Merge / Reject | `event-list.json` candidate recommendations | Aligned | The current pipeline records the agent proposal separately from human review state. |
| Set private Draft / Approved / Don’t use state | `route-review.json` and private backend API | Partial | State persistence is implemented; explorer controls remain in #72. |
| Generate a complete route result | `complete-draft.json` and materialized framing artifacts | Aligned | The active result may revise candidate roster and sequence before human review. |
| Enrich accepted events with sources and media | Enrichment can use accepted-event handoff files as the editorial boundary | Partial | Current scripts still run from seed data; docs now define the accepted-event boundary. |
| Human reviews final output | Seed preview, validation report, and link review exist | Partial | There is no single final event-card approval gate. |
| Publish as map, timeline, route, or event cards | Seed data powers runtime app | Partial | Draft seed records can still appear in the explorer. |

## Complexity Risks

The main complexity risk is that enrichment is more mature than candidate
selection. The media and image workflows have query components, planners,
provider calls, confidence hints, review priorities, quality reports, ignore
lists, and review actions. These are useful, but they should not get ahead of
the basic editorial decision about which events belong in a route.

The route pipeline now creates a complete draft and private route-review result
without requiring the legacy accepted-events gate. The deterministic accepted-
events path remains available for compatibility. The target interaction reduces
the remaining editorial friction by letting the editor inspect the route visually
and set private route state without reviewing raw structured files.

The current seed `review_status` values, `draft` and `reviewed`, are too broad
for the full editorial lifecycle. They remain compatibility data and link-review
state, not the target route-scoped Draft, Approved, and Don’t use controls and
not a public-page badge.

Numeric `confidence` is also a weak editorial signal. It is acceptable as an
internal sorting or compatibility field for generated links, but it should not
be treated as historical or curatorial truth.

## Concept Coverage

| Concept | Current support | Notes |
| --- | --- | --- |
| Theme | Partial | Covered by route topic and route concept. No separate object needed now. |
| Theme brief | Exists | Implemented as route `brief.md`. |
| Candidate event | Exists | Dossier tables and `event-list.json`. |
| Candidate recommendation | Exists | Uses `keep`, `maybe`, `merge`, and `reject`. |
| Private route-review state | Partial | Typed route-folder persistence and private API exist; #72 owns the explorer surface. |
| Accepted event | Exists | Represented by `accepted-events.json`. |
| Event dossier | Exists | Implemented as `accepted-events.md`, a readable companion view for the JSON handoff. |
| Source status | Exists | Source status vocabulary is documented for accepted-event handoff notes. |
| Media search queries | Exists | YouTube request plans and image query ladders. |
| Human review before publishing | Partial | Link review and seed preview exist, but no final event-card gate. |

## Suggested Simplification

Keep `route` as the central editorial object. Do not add a separate `Theme`
entity yet.

Use a simple candidate recommendation vocabulary in the current pipeline:

- `keep`: develop into an accepted event.
- `maybe`: preserve as a research lead, but do not enrich yet.
- `merge`: combine into another accepted event or route context.
- `reject`: do not continue for this route.

The complete-draft result, not an early accepted-events handoff, enters the
target explorer review. Agent recommendations remain advisory while Draft,
Approved, and Don’t use become the human controls. The accepted-events files
remain a deterministic compatibility path.

The complete-draft step creates seed-shaped event, place, and connection drafts
for the active result before human review, while keeping all records in draft
state and preserving warnings. Publication remains blocked by technical errors
and still requires explicit human action.

Separate the working layers:

- Candidate layer: route brief, dossier, and `candidate-outline.json`.
- Complete-draft layer: `complete-draft.json` and its materialized framing files.
- Review layer: `route-review.json`, with agent recommendations separate from
  human state.
- Enrichment layer: source checks, media search queries, draft media, and draft
  images.
- Publish layer: final event cards promoted into `data/seed/`.

For sources, prefer simple source status values over numeric confidence:

- `strong`
- `medium`
- `weak`
- `mythologized`
- `needs_review`

These should describe source and claim quality, not whether an event is
important.

AI may suggest draft source statuses, but human editors confirm or revise them
before the status is treated as editorially approved.

## Smallest Useful MVP Workflow

The smallest useful target editorial MVP is:

```text
route input
-> AI route brief
-> AI candidate event longlist
-> CLI complete route draft
-> visual review in the existing explorer
-> human state: Draft / Approved / Don’t use
-> warnings and technical readiness
-> publish the exact Draft-plus-Approved result
-> canonical runtime data
```

Include:

- Route brief with question, thesis hypothesis, geography, time range, source
  leads, and risks.
- Candidate event longlist with rationale, source leads, and risk notes.
- Agent recommendations and merge targets that remain visibly advisory.
- Private route-scoped Draft, Approved, and Don’t use controls.
- Coordinated review through the existing map, timeline, and StoryPanel.
- Media search query planning for accepted events only.
- Draft source, media, and image enrichment.
- One explicit human publication decision over the exact reviewed result.
- Publishable event-card text: title, years, place, summary, significance,
  source URLs, media links, image links, and connection notes.

Postpone:

- Separate `Theme` schema.
- Automatic event acceptance.
- AI source-quality final judgment.
- Admin/editor UI beyond the thin explorer review surface.
- Canonical media-item modeling across providers.
- Database-backed editorial workflow.
- Fully automated source, media, or publication approval.

## Things Not To Automate Yet

- Deciding which events are historically important enough for a route.
- Resolving contested origin stories or first/invented claims.
- Marking sources or media as publication-ready.
- Merging weak candidates into canonical events without editor approval.
- Publishing or replacing route content without the explicit route-level human
  publication decision.

## Recommended Workflow Diagram

```text
Route idea
  |
  v
Route brief
  |
  v
Generated route result
  |
  v
Explorer editorial review
  |-- Draft     --> include
  |-- Approved  --> include
  |-- Don’t use --> exclude without deletion
  |
  v
Warnings and technical readiness
  |
  v
Publish exact reviewed result
  |
  v
Publishable event cards
  |
  v
data/seed/
  |
  v
Map, timeline, route, and story panel
```
