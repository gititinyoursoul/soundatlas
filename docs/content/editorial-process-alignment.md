# Editorial Process Alignment

## Purpose

This note records how the current SoundAtlas editorial system aligns with a
simpler route-centered editorial process.

The intended process is:

```text
route idea
-> route brief
-> candidate event longlist
-> human candidate review
-> accepted event dossiers
-> source and media enrichment
-> human final review
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
4. `event-list.md` and `event-list.json` hold candidate events for review.
5. `route-concept.md` turns reviewed candidates into a route argument and phase
   draft.
6. `accepted-events.md` is the route-level accepted-event dossier to create
   after human candidate review. It includes only `keep` candidates and
   human-resolved `merge` outcomes.
7. `event-framing.*`, `place-framing.json`, and `connection-framing.json`
   create seed-shaped drafts.
8. `seed-transfer-report.md` and `validation-report.md` preview structural
   seed changes before promotion.
9. `data/seed/` is the runtime source for the map, timeline, route switching,
   event inspector, sources, connections, media links, and image links.
10. Enrichment scripts can create event-search components, media query plans,
   YouTube result files, draft `media_links`, and draft `image_links`.
11. The app has an internal media/image review queue for marking draft links as
    reviewed or rejecting them.

The documentation consistently says generated route artifacts are drafts and
that human editorial review decides which claims, events, places, connections,
and links are ready for seed promotion.

`prompts/grill-me.md` is the recommended critique gate before non-trivial
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
| Mark Keep / Maybe / Merge / Reject | Current statuses are `develop`, `context`, `defer`, and `reject` | Partial | The vocabulary should be simplified to editor-facing decisions. |
| Create dossiers only for accepted events | `accepted-events.md` route-level dossier template | Aligned | Dossier is documented as enrichment-ready, not publication-ready. |
| Enrich accepted events with sources and media | Enrichment can use accepted-event dossiers as the editorial handoff | Partial | Current scripts still run from seed data; docs now define the accepted-event boundary. |
| Human reviews final output | Seed preview, validation report, and link review exist | Partial | There is no single final event-card approval gate. |
| Publish as map, timeline, route, or event cards | Seed data powers runtime app | Partial | Draft seed records can still appear in the explorer. |

## Complexity Risks

The main complexity risk is that enrichment is more mature than candidate
selection. The media and image workflows have query components, planners,
provider calls, confidence hints, review priorities, quality reports, ignore
lists, and review actions. These are useful, but they should not get ahead of
the basic editorial decision about which events belong in a route.

The current route pipeline can also over-produce seed-shaped drafts. The
deterministic event-list step defaults extracted candidates to `develop`, and
later steps can create event, place, and connection drafts for many weak or
context-only candidates. That makes candidates look closer to accepted events
than they really are.

The current `review_status` values, `draft` and `reviewed`, are too broad for
the full editorial lifecycle. They are useful for runtime data and link review,
but they do not distinguish candidate events, accepted events, enriched events,
final-reviewed event cards, and published event cards.

Numeric `confidence` is also a weak editorial signal. It is acceptable as an
internal sorting or compatibility field for generated links, but it should not
be treated as historical or curatorial truth.

## Concept Coverage

| Concept | Current support | Notes |
| --- | --- | --- |
| Theme | Partial | Covered by route topic and route concept. No separate object needed now. |
| Theme brief | Exists | Implemented as route `brief.md`. |
| Candidate event | Exists | Dossier tables and `event-list.json`. |
| Candidate review status | Partial | Current statuses are not the desired editor vocabulary. |
| Accepted event | Partial | Approximated by `develop` candidates and seed events, but not explicit. |
| Event dossier | Exists | Implemented as route-level `accepted-events.md` guidance. |
| Source status | Exists | Source status vocabulary is documented for accepted-event dossiers. |
| Media search queries | Exists | YouTube request plans and image query ladders. |
| Human review before publishing | Partial | Link review and seed preview exist, but no final event-card gate. |

## Suggested Simplification

Keep `route` as the central editorial object. Do not add a separate `Theme`
entity yet.

Use a simpler candidate review vocabulary:

- `keep`: develop into an accepted event.
- `maybe`: preserve as a research lead, but do not enrich yet.
- `merge`: combine into another accepted event or route context.
- `reject`: do not continue for this route.

Only `keep` candidates and resolved `merge` outcomes should move into accepted
event dossiers.

Do not create seed-shaped event, place, and connection drafts for every
candidate. Create seed-shaped records only after the candidate review pass.

Separate the working layers:

- Candidate layer: route brief, dossier, and longlist.
- Accepted layer: accepted event dossiers.
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

The smallest useful editorial MVP is:

```text
route input
-> AI route brief
-> AI candidate event longlist
-> human selection: keep / maybe / merge / reject
-> accepted event dossiers
-> media search queries
-> source and media enrichment
-> human final review
-> publishable event cards
```

Include:

- Route brief with question, thesis hypothesis, geography, time range, source
  leads, and risks.
- Candidate event longlist with rationale, source leads, and risk notes.
- Human candidate decision field.
- Route-level accepted-event dossier covering each kept candidate and resolved
  merge outcome.
- Media search query planning for accepted events only.
- Draft source, media, and image enrichment.
- Final human review before seed promotion.
- Publishable event-card text: title, years, place, summary, significance,
  source URLs, media links, image links, and connection notes.

Postpone:

- Separate `Theme` schema.
- Automatic event acceptance.
- AI source-quality final judgment.
- Public admin/editor UI beyond lightweight review needs.
- Canonical media-item modeling across providers.
- Database-backed editorial workflow.
- Fully automated source, media, or publication approval.

## Things Not To Automate Yet

- Deciding which events are historically important enough for a route.
- Resolving contested origin stories or first/invented claims.
- Marking sources or media as publication-ready.
- Merging weak candidates into canonical events without editor approval.
- Publishing draft events to the public experience.

## Recommended Workflow Diagram

```text
Route idea
  |
  v
Route brief
  |
  v
Candidate event longlist
  |
  v
Human candidate review
  |-- keep  --> accepted event dossier
  |-- merge --> accepted event dossier or route context
  |-- maybe --> research backlog
  |-- reject -> stop
  |
  v
Source and media enrichment for accepted events
  |
  v
Human final review
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
