# Route Editorial Quality Standards

## Purpose

SoundAtlas routes should be researched editorial arguments, not flat lists of
related events. A route is ready for seed transfer only when it explains why the
selected people, places, events, influences, and circumstances belong together.

These standards apply before new or heavily revised route concepts are mapped
into `data/seed/`.

## Route Research Dossier

Every non-trivial route concept should include a route research dossier before
seed data is added or revised. For new route content, keep the dossier in the
route folder under `docs/content/routes/<route-id>/`. A route folder may contain
`brief.md`, a research dossier, a concept file, and route-specific notes.

Existing route concepts under `docs/content/route-concepts/` may keep an
embedded dossier until a separate migration moves legacy concepts into
per-route folders.

Use `docs/content/route-research-dossier-template.md` as the default format for
new route dossiers.

The dossier should cover:

- Route question and thesis: the question the route answers and the argument it
  makes.
- Artists and groups: key artists, DJs, producers, bands, labels,
  institutions, communities, or organizers that shape the route.
- Places and venues: important rooms, neighborhoods, labels, stations,
  institutions, and external nodes, with each place's route function.
- Influences: musical, cultural, regional, media, and scene influences that
  explain how the route develops.
- Circumstances: political, social, economic, technical, urban, migration,
  media, or industry conditions that make the route historically legible.
- Candidate events: possible route events with inclusion rationale, not just
  chronology.
- Candidate connections: relationships between events, with the relationship
  type and narrative purpose.
- Editorial source research: likely sources for route claims, event framing,
  contested claims, chronology, and further reading.
- Media source research: likely listening, video, interview, documentary,
  playlist, performance, or broadcast references to investigate later.
- Image source research: likely venue photos, artist photos, flyers, posters,
  archive images, maps, press scans, album covers, or other visual material to
  investigate later.
- Risks and open claims: weakly sourced claims, contested origin stories,
  uncertain dates, rights risks, attribution gaps, or material that should stay
  `review_status: "draft"`.

## Draft Source Standard

The dossier uses a draft source standard. It does not need to prove every claim
at publication level before seed transfer, but it must identify plausible source
directions and claim risks.

Use this bar before seed transfer:

- Major route claims have at least likely editorial sources or named source
  categories.
- Contested or uncertain claims are named as risks instead of written as settled
  fact.
- Media and image research identifies likely source categories or candidate
  directions, but does not need to add links to `events.json`.
- Rights, availability, and attribution concerns for media and images are
  carried forward as review risks.

## Route Quality Rubric

A strong route should meet these checks:

- Thesis strength: the route makes a clear historical or cultural argument.
- Narrative arc: the route has phases that show development over time.
- Research coverage: artists, groups, places, influences, circumstances, and
  sources are visible before event selection is finalized.
- Event selection: every candidate event reveals something about the thesis.
- Place logic: places explain community, infrastructure, industry, media, or
  scene formation, not only coordinates.
- Sound and culture logic: the route explains practices, genres, technologies,
  audiences, institutions, or media circulation.
- Connection quality: each connection explains influence, context,
  transmission, contrast, media spread, or scene formation.
- Source-risk handling: origin stories, disputed claims, uncertain dates, and
  sensitive historical claims are marked clearly.
- Seed-transfer readiness: route, place, event, and connection candidates can be
  mapped into the current seed schema without adding fields.

## Seed-Transfer Checklist

Before route content is transferred into `data/seed/`, check that:

- The route has a central question and thesis.
- The route has two to four narrative phases with clear functions.
- The dossier names the key artists, groups, places, influences,
  circumstances, and source directions.
- Each candidate event has an inclusion rationale.
- Each primary place has a route function.
- Each candidate connection has a relationship type and narrative purpose.
- Editorial, media, and image source research are separated.
- Uncertain claims and source risks are explicit.
- Seed changes can be made without changing the current data model.

## Editorial Smell Tests

Rework the route concept before seed transfer when:

- The route is only a timeline of famous moments.
- Events are included only because they share a genre or neighborhood.
- Places are only map pins, with no interpretive role.
- The thesis could describe any route in the app.
- The route depends on a single origin myth.
- Media or image ideas are invented without a likely source direction.
- Connections only express adjacency instead of a meaningful relationship.
