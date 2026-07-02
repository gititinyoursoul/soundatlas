# Route Research Dossier Template

Copy this template into `docs/content/routes/<route-id>/research-dossier.md`
for new route content before selecting final seed events or transferring route
data into `data/seed/`.

Existing route concepts under `docs/content/route-concepts/` may keep an
embedded dossier until a separate migration moves legacy concepts into
per-route folders.

Use the template as draft research scaffolding. It should identify source
directions and editorial risks, but it does not need publication-grade
verification before seed transfer.

## Route Working Frame

- Working title:
- Stable route ID:
- Geography:
- Time range:
- Current MVP fit:
- Central question:
- Draft thesis:

Mini example:

```md
Central question: How did local Bronx party culture become a global cultural
form between 1970 and 1985?
Draft thesis: Hip-hop emerged from DJ technique, community spaces, urban
conditions, and media circulation rather than from one isolated origin point.
```

## Artists, Groups, And Communities

List the artists, DJs, producers, bands, labels, institutions, communities, or
organizers that shape the route.

| Name | Role in route | Why they matter | Source leads | Risk notes |
| --- | --- | --- | --- | --- |
| `<name>` | `<artist / DJ / label / community / institution>` | `<route function>` | `<books, archives, articles, interviews>` | `<uncertain, contested, sensitive, or missing source>` |

Mini example:

```md
Role in route: DJ and technique node
Why they matter: Makes the route's technical argument visible, not just its
chronology.
```

## Places And Venues

List places as interpretive route nodes, not only map coordinates.

| Place | Place type | Route function | Possible seed place | Source leads | Risk notes |
| --- | --- | --- | --- | --- | --- |
| `<place>` | `<venue / neighborhood / label / station / institution / external node>` | `<community space / industry node / crossover point / media node>` | `<new or existing place ID>` | `<source leads>` | `<date, address, role, or geocoding risk>` |

Mini example:

```md
Route function: Community space where the route's social conditions become
visible.
Risk notes: Exact address and active years vary by source.
```

## Influences And Circumstances

Identify the musical, cultural, technical, social, political, economic, urban,
migration, media, or industry conditions that make the route legible.

| Topic | Type | Route function | Candidate events affected | Source leads | Risk notes |
| --- | --- | --- | --- | --- | --- |
| `<topic>` | `<musical / cultural / technical / social / political / economic / urban / media / industry>` | `<what this explains>` | `<event IDs or candidate titles>` | `<source leads>` | `<claim risk>` |

Mini example:

```md
Type: technical / media
Route function: Explains why a new format changed DJ practice and club
circulation.
```

## Candidate Events

Use this table before deciding which events belong in `events.json`. Every event
needs an inclusion rationale.

| Candidate ID | Years | Place | Working title | Inclusion rationale | Source leads | Risk notes |
| --- | --- | --- | --- | --- | --- | --- |
| `<url-safe-id>` | `<year or range>` | `<place>` | `<title>` | `<what this event reveals about the route thesis>` | `<source leads>` | `<uncertain date, contested claim, weak source, or sensitivity>` |

Mini example:

```md
Inclusion rationale: Shows the route moving from local practice into media
circulation.
Risk notes: Avoid calling it the first unless sources support that exact claim.
```

## Candidate Connections

Use this table before deciding which relationships belong in
`connections.json`.

| From event | To event | Relationship type | Narrative purpose | Source leads | Risk notes |
| --- | --- | --- | --- | --- | --- |
| `<event>` | `<event>` | `<influence / context / transmission / contrast / media_transition / scene_formation>` | `<why users should see these together>` | `<source leads>` | `<weak link, overclaim, or chronology risk>` |

Mini example:

```md
Narrative purpose: Shows a venue network turning a local practice into a
recognizable scene.
```

## Editorial Source Research

Track source directions for route claims, event framing, chronology, contested
claims, and further reading.

| Source lead | Source type | Supports | Reliability notes | Follow-up |
| --- | --- | --- | --- | --- |
| `<book / archive / article / interview / museum / documentary>` | `<primary / secondary / reference / journalism>` | `<route claim, event, place, or connection>` | `<strengths and limits>` | `<verify date, quote, address, claim, or attribution>` |

## Media Source Research

Track likely listening, video, interview, documentary, playlist, performance, or
broadcast references. Do not add generated or unreviewed links directly to
`events.json` from this section.

| Media lead | Type | Related event or route point | Why it may help | Rights or availability risk |
| --- | --- | --- | --- | --- |
| `<recording / video / interview / documentary / playlist / broadcast>` | `<track / album / video / playlist / interview / documentary>` | `<event or theme>` | `<listening, context, performance, or explanation value>` | `<availability, copyright, embedding, attribution, or weak match>` |

## Image Source Research

Track likely venue photos, artist photos, flyers, posters, archive images, maps,
press scans, album covers, or other visual material. Do not treat this as rights
approval.

| Image lead | Type | Related event or route point | Why it may help | Rights or attribution risk |
| --- | --- | --- | --- | --- |
| `<archive, collection, or image candidate>` | `<venue_photo / artist_photo / flyer_poster / archive_photo / map_image / press_scan / album_cover>` | `<event or theme>` | `<visual context value>` | `<license, attribution, date, identity, or source risk>` |

## Risks And Open Claims

List claims that should stay cautious until reviewed.

| Claim or risk | Affected route content | Current wording guidance | Review need |
| --- | --- | --- | --- |
| `<claim or risk>` | `<route, event, place, connection, media, or image>` | `<how to phrase cautiously>` | `<source, rights, date, attribution, or sensitivity review>` |

Mini example:

```md
Current wording guidance: Use "symbolic origin point" instead of "the sole
birthplace" unless the route explicitly discusses why the phrase is contested.
```

## Route Quality Review

- [ ] The route has a central question and thesis.
- [ ] The route has two to four narrative phases with clear functions.
- [ ] The dossier identifies key artists, groups, places, influences,
  circumstances, and source directions.
- [ ] Every candidate event has an inclusion rationale.
- [ ] Every primary place has a route function.
- [ ] Every candidate connection has a relationship type and narrative purpose.
- [ ] Editorial, media, and image source research are separated.
- [ ] Uncertain claims and source risks are explicit.
- [ ] The selected route, place, event, and connection candidates can be mapped
  into the current seed schema without adding fields.
