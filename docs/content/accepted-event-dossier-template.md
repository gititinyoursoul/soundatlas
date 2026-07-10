# Accepted Event Dossier Template

## Purpose

An accepted-event dossier is the route-level editorial handoff after candidate
review and before source or media enrichment.

For the MVP, keep accepted-event dossiers as one route-level file:

```text
docs/content/routes/<route-id>/accepted-events.md
```

The file is enrichment-ready, not publication-ready. It helps editors collect
the accepted event set, source leads, media leads, claim risks, and unresolved
questions before any event becomes seed-shaped or enters enrichment planning.

## Inclusion Rule

Accepted-event dossiers may include only:

- candidates marked `keep`
- `merge` candidates after a human editor has resolved the merge target

Do not include:

- unresolved `maybe` candidates
- unresolved `merge` candidates
- `reject` candidates

`maybe` candidates can remain in the route event longlist or research backlog.
Rejected candidates should not continue into accepted-event dossiers,
enrichment, seed framing, or publication review.

## AI Boundary

AI may draft accepted-event dossier content and suggest draft source statuses.
AI output remains review material.

AI must not:

- confirm source status
- approve source quality
- approve media links
- resolve contested historical claims
- mark an event as publication-ready

Human editors confirm or revise source status before it is treated as
editorially approved.

## Source Status

Source status describes the quality of a source or claim relationship. It does
not describe whether the event is important.

| Status | Meaning | Example use |
| --- | --- | --- |
| `strong` | The source directly supports the claim with specific event, date, place, participant, or artifact evidence. | A primary archive item, interview, preservation record, or well-cited historical source directly supports the event. |
| `medium` | The source supports the claim, but with some distance, interpretation, or missing detail. | A reliable secondary history supports the broader event but not every place/date detail. |
| `weak` | The source is relevant but too general, vague, or indirect to carry the claim alone. | A scene overview mentions the topic but does not verify the specific event framing. |
| `mythologized` | The source reflects public memory, origin storytelling, or contested retrospective framing. | Anniversary coverage or oral history gives a useful account but risks sole-origin, first, or invented claims. |
| `needs_review` | The source lead has not been evaluated enough to assign a stronger status. | A candidate article, archive collection, or media lead needs human inspection. |

Use separate fields for AI suggestion and human confirmation:

```text
AI-suggested status: strong | medium | weak | mythologized | needs_review
Human-confirmed status: strong | medium | weak | mythologized | needs_review | unset
```

When unsure, keep the human-confirmed status unset or `needs_review`.

## Template

```md
# Accepted Events: <Route Title>

Status: Draft accepted-event dossier for enrichment planning. Not seed-ready or publication-ready.
Route: `<route-id>`
Source candidate list: `<event-list filename>`
Editor/date:

## Review Boundary

This file includes only human-selected `keep` candidates and resolved `merge`
outcomes. It excludes unresolved `maybe`, unresolved `merge`, and `reject`
candidates.

AI may draft event notes and suggest source statuses, but source and media
approval remain human-reviewed.

## Accepted Event Index

| Event ID | Decision | Merge target | Working title | Years | Place | Enrichment-ready? | Notes |
| --- | --- | --- | --- | --- | --- | --- | --- |
| `<event-id>` | `keep` |  | `<title>` | `<year or range>` | `<place>` | `no` | `<main unresolved issue>` |
| `<merged-event-id>` | `merge` | `<target-event-id>` | `<title>` | `<year or range>` | `<place>` | `no` | `<merge rationale>` |

## Event Dossiers

### `<event-id>`: <Working Title>

Candidate decision: `keep | merge`
Merge target: `<target-event-id or blank>`
Enrichment-ready: `yes | no`

#### Core Framing

- Working title:
- Year range:
- Place:
- Route rationale:
- Candidate source:
- Related route phase:

#### Claim And Risk Notes

- Core claim:
- Claim risks:
- Contested or mythologized language to avoid:
- Unresolved questions:

#### Source Leads

| Source lead | Claim supported | AI-suggested status | Human-confirmed status | Notes |
| --- | --- | --- | --- | --- |
| `<source>` | `<claim>` | `needs_review` | `unset` | `<review note>` |

#### Media And Image Leads

| Lead | Type | Search/use intent | Review risk |
| --- | --- | --- | --- |
| `<lead>` | `media | image | source` | `<intent>` | `<risk>` |

#### Enrichment Handoff

- Recommended media search intents:
- Recommended image/source search directions:
- Do not search/enrich yet because:
- Ready for enrichment after:
```

## Relationship To Other Editorial Work

- Use route and event quality standards from `docs/content/` for prose quality,
  event-to-route fit, and source discipline.
- Use `docs/content/editorial-process-alignment.md` for the overall simplified
  editorial process.
- Use publication readiness guidance only after enrichment and final review.
  Accepted-event dossiers do not make an event publication-ready.
