# Step 10b — Presentation and visual claims

## Stage record

- Experiment ID: `underground-disco-interactive`
- Version ID: `disco-baseline-1.1-02`
- Method: `baseline-1.1`
- Stage: `10b`
- Status: `checkpointed`
- Named inputs:
  - [`00-run-brief.md`](00-run-brief.md)
  - [`07-cross-event-synthesis.md`](07-cross-event-synthesis.md)
  - [`09-evidence-audit.md`](09-evidence-audit.md)
  - [`10a-final-route-copy.md`](10a-final-route-copy.md)
  - current frontend architecture, design, spatial-presentation documentation,
    data-model types, and `MapView`, `Timeline`, `StoryPanel`, and `MediaEmbed`
    implementation
- Prior Human decision: Step-10a copy accepted in
  [Issue #183](https://github.com/gititinyoursoul/soundatlas/issues/183#issuecomment-5457177964).
- Authority: proposed presentation evidence for this experimental route version;
  not canonical data, a review revision, media approval, or publication
  authority

## Observed current product capability

| Surface | Observed implementation | Consequence for this route |
| --- | --- | --- |
| Map | `MapView` renders event point markers, optional point/area place geometry, selected-event styling, focused-place styling, and bounds framing from shared event/place data. | A later approved Disco route can use ordinary Event selection and place focus; this experimental version supplies no coordinates or seed data. |
| Map relationships | `MapView` renders only `place_relationships` inside the currently selected Event. It has no layer for cross-Event `Connection` records. | No map line, arrow, or network graphic may communicate this route's cross-Event relationships. |
| Timeline | `Timeline` renders one selectable entry per Event from `year_start`/`year_end`, highlights the selected range, and keeps the selected card centered. | The seven Events can be presented in their reader order without treating chronology as influence. |
| StoryPanel | The Story tab renders ordered story sections, source links, and accessible Event-place controls; its Related tab lists existing Event connections. | Reader copy and textual limits remain the primary relationship treatment; any future connection must be textual and source-backed. |
| Media | `StoryPanel` can preview images and playable or external media links; `MediaEmbed` embeds supported YouTube links and offers review controls outside public mode. | The route has no approved media or image asset. No preview, embed, poster, or autoplay treatment is authorized. |
| Data boundary | Event identity, dates, places, sources, story sections, media, images, and place relationships are seed/API/static-data fields. | This authoring-only output does not create a map marker, timeline item, source card, media item, or relationship at runtime. |

Observed implementation evidence: [frontend architecture](../../../../../architecture/frontend.md),
[current frontend design](../../../../../design/current-frontend-design.md),
[route-entry spatial presentation](../../../../../design/route-entry-spatial-presentation.md),
[`MapView.svelte`](../../../../../../frontend/src/lib/components/MapView.svelte),
[`Timeline.svelte`](../../../../../../frontend/src/lib/components/Timeline.svelte),
[`StoryPanel.svelte`](../../../../../../frontend/src/lib/components/StoryPanel.svelte),
and [`MediaEmbed.svelte`](../../../../../../frontend/src/lib/components/MediaEmbed.svelte).

## Baseline presentation position

The supported baseline is an Event-by-Event map and timeline experience. Each
approved Event would be selected through one marker or documented multi-place
footprint, one Timeline entry, and its complete StoryPanel chapter. The map
does not show a route path, a citywide network, or a historical flow. The
Timeline orders Events for orientation; it does not prove transmission.

All historical coordinate provenance in the fixed dossier remains `unknown`.
Accordingly, this output does not propose actual Disco marker coordinates,
areas, route bounds, zoom targets, or spatial edits. A later approved canonical
data handoff would need to resolve those records independently.

## Presentation records

### `moment-route-orientation`

- Owning section/Event/relationship IDs: all four section IDs; no Event or
  relationship is privileged.
- Implemented map state: selected route context, visible Event markers when
  later data exists, one selected Event, and a focused place inside that Event.
- Historical claim communicated: the route studies several differently governed
  forms of collective listening in New York; it does not depict one seamless
  citywide scene.
- Evidence basis: the Step-10a introduction and thesis; all fixed Sources
  `S01`–`S16` as mapped in [`09-evidence-audit.md`](09-evidence-audit.md).
- Prohibited implication: one map extent, common color, marker order, or shared
  city label proves direct influence, common membership, or a single origin.
- Visual/media treatment: restrained route-color selection accent only; no
  background image, route line, animated replay, or decorative network.
  Availability and rights: `not-assessed`; no asset selected.
- Copy/presentation consistency and accessibility: the route thesis and the
  selected Event title/year must remain textually available; color cannot be
  the only selected-state signal.
- Unsupported future capability: a route-level explanatory overlay would need
  separate product and content approval; it is not a baseline need.

### `moment-making-collective-floors`

- Owning section/Event/relationship IDs: `section-making-collective-floors`,
  `loft-broadway-party-1970-1974`, `st-marys-dance-incubator-1974`, and
  `rel-loft-stmarys-parallel-practice`.
- Implemented map state: select either Event marker and use the Timeline to
  orient its bounded date/range; do not draw a connector between the two places.
- Historical claim communicated: distinct communities assembled recurring
  floors in a Manhattan home and a Bronx recreation center.
- Evidence basis: `S01`–`S05` in the fixed Source register; the relationship is
  `interpretive-synthesis` with no direct-exchange Source.
- Prohibited implication: the Loft taught, enabled, geographically fed, or
  otherwise caused St. Mary's; neither marker is an origin symbol.
- Visual/media treatment: equal standard Event treatment; an optional later
  sourced photo may belong only to its Event chapter. Availability and rights:
  `not-assessed`.
- Copy/presentation consistency and accessibility: StoryPanel must retain the
  parallel-development wording and each Event's date/place context; no visual
  comparison may be the sole explanation.
- Unsupported future capability: simultaneous split-screen comparison is a
  future proposal, not current behavior or a baseline requirement.

### `moment-loft-gallery-adaptation`

- Owning section/Event/relationship IDs: `loft-broadway-party-1970-1974`,
  `gallery-mercer-room-1974-1977`, and `rel-loft-gallery-adaptation`.
- Implemented map state: independent marker selection and Event-by-Event
  Timeline orientation; no cross-Event connector is implemented.
- Historical claim communicated: Siano later described a commercial,
  dance-focused Gallery adaptation of Mancuso's model.
- Evidence basis: `S03` — [Nicky Siano oral history](https://daily.redbullmusicacademy.com/2018/02/nicky-siano-interview-dj-history/), as qualified in the Step-09 audit.
- Prohibited implication: the Loft caused the Gallery's complete room, crowd,
  business model, or later influence; do not draw a general influence arrow.
- Visual/media treatment: if the Related tab is later populated with a reviewed
  Event connection, it may use the qualified textual summary. No map arrow,
  imagery, or audio is selected. Availability and rights: `not-assessed`.
- Copy/presentation consistency and accessibility: the adaptation remains
  attributed and its limits remain readable outside any visual cue.
- Unsupported future capability: cross-Event map relationship rendering is a
  separate Intake need, not implemented behavior.

### `moment-building-rooms-and-interfaces`

- Owning section/Event/relationship IDs:
  `section-building-rooms-and-interfaces`,
  `leviticus-opening-and-label-parties-1974-1976`,
  `gallery-mercer-room-1974-1977`,
  `rel-leviticus-gallery-label-interface`, and
  `rel-leviticus-pool-exchange-contrast`.
- Implemented map state: select Leviticus or Gallery independently; their
  event chapters, rather than map geometry, communicate ownership, room labor,
  press events, and supplied records.
- Historical claim communicated: Black ownership/promotion and commercial room
  coordination were distinct institutional interfaces, neither a documented
  return channel from dancers to labels.
- Evidence basis: `S06`–`S10`, with the contrast records in Step 07 and the
  wording limits in Step 09.
- Prohibited implication: shared time, nearby downtown locations, label events,
  or supplied records prove venue contact, Pool participation, feedback,
  release influence, or sales causality.
- Visual/media treatment: ordinary selected-marker treatment; no label arrow,
  feedback loop, or image intended to stand for dancers' unrecorded testimony.
  Availability and rights: `not-assessed`.
- Copy/presentation consistency and accessibility: ownership, date dispute,
  and representation limits remain in StoryPanel prose and source links.
- Unsupported future capability: an institution-comparison surface requires a
  separate Intake; it is not needed to render the route faithfully now.

### `moment-record-pool-infrastructure`

- Owning section/Event/relationship IDs: `section-organizing-record-exchange`,
  `new-york-record-pool-launch-1975`, and
  `rel-loft-pool-organizer-place-change`.
- Implemented map state: one Event marker/Timeline entry when place data is
  approved; StoryPanel carries the distinction between 99 Prince Street and
  Mancuso's earlier Broadway residence.
- Historical claim communicated: working DJs organized access, distribution,
  and requested critique through a nonprofit Pool.
- Evidence basis: `S11` — [Billboard, June 21, 1975](https://www.worldradiohistory.com/Archive-All-Music/Billboard/70s/1975/Billboard%201975-06-21.pdf) and `S12` — [Business History article](https://www.tandfonline.com/doi/full/10.1080/00076791.2017.1308485).
- Prohibited implication: a continuous movement line joins the Broadway Loft to
  the later Prince Street Loft; all DJs organized it, the scheduled meeting is
  proven completed, or Pool critique dictated label decisions.
- Visual/media treatment: infrastructure is a narrative role, not a map icon;
  no document scan is selected. Availability, attribution, and rights:
  `not-assessed`.
- Copy/presentation consistency and accessibility: Timeline chronology and the
  source list must not collapse the two Loft addresses or replace the written
  qualification.
- Unsupported future capability: document-viewer treatment is a future product
  proposal and requires separate media/rights review.

### `moment-gallery-garage-work-continuity`

- Owning section/Event/relationship IDs: `gallery-mercer-room-1974-1977`,
  `paradise-garage-buildout-opening-1977-1978`, and
  `rel-gallery-garage-work-continuity`.
- Implemented map state: two independent Event selections, with chronological
  orientation in the Timeline; no implemented cross-Event line.
- Historical claim communicated: Levan's work links the Gallery and Garage,
  while the Garage remains a separately built institution.
- Evidence basis: `S03` and `S13` — [NYC LGBTQ Historic Sites Project: Paradise Garage](https://www.nyclgbtsites.org/site/paradise-garage/).
- Prohibited implication: one venue caused the other, Levan alone designed
  either, or their communities were interchangeable.
- Visual/media treatment: no universal influence arrow, lineage graphic, or
  person-avatar treatment. Availability and rights: `not-assessed`.
- Copy/presentation consistency and accessibility: the qualified relationship
  can appear only as readable text in a reviewed Related-event summary; no map
  graphic may carry the claim alone.
- Unsupported future capability: a cross-Event relation layer with source-aware
  labels is separate Intake work.

### `moment-garage-through-time`

- Owning section/Event/relationship IDs:
  `section-building-and-testing-the-garage-floor`,
  `paradise-garage-buildout-opening-1977-1978`,
  `heartbeat-garage-vinylmania-1981`, and
  `rel-garage-heartbeat-place-practice`.
- Implemented map state: the same later-approved Garage place may be selected
  in two distinct Events; the Timeline differentiates the 1977–78 buildout
  from the 1981 record episode.
- Historical claim communicated: one place has different historical work at
  different times—first institution-building, later a qualified test of record
  reception.
- Evidence basis: `S13`, `S14` — [Record World, April 11, 1981](https://www.worldradiohistory.com/Archive-Record-World/80s/81/RW-1981-04-11.pdf), `S15`, and `S16`, as bounded in Step 09.
- Prohibited implication: two simultaneous Garage sites, that the buildout
  caused the record's release or success, or that the floor alone made a hit.
- Visual/media treatment: reuse one place over time through separate Event
  selection; no timeline animation, duplicate simultaneous marker, or causal
  arrow to Vinylmania. Availability and rights: `not-assessed`.
- Copy/presentation consistency and accessibility: selected Event title/year
  must distinguish the two Garage chapters; the 1981 recollection remains
  visibly attributed.
- Unsupported future capability: time-scrubbed marker states or route playback
  are later-only capabilities.

### `moment-heartbeat-circulation-limit`

- Owning section/Event/relationship IDs: `heartbeat-garage-vinylmania-1981`
  and `rel-pool-heartbeat-circulation-contrast`.
- Implemented map state: one selected Event with its approved place footprint;
  no Pool-to-Garage, Garage-to-store, or record-flow connector exists.
- Historical claim communicated: an attributed account of a changing floor
  response sits beside separately documented wider circulation, without proving
  a single causal sequence.
- Evidence basis: `S14`, `S15` — [Time Out oral history](https://www.timeout.com/newyork/nightlife/paradise-garage-the-oral-history-of-nycs-greatest-club), and `S16` — [Vinylmania oral history](https://daily.redbullmusicacademy.com/2016/02/vinylmania-oral-history/).
- Prohibited implication: the Pool participated, Garage caused retail success,
  Vinylmania's line is contemporary proof, or the Event establishes radio,
  national sales, sampling, or genre influence.
- Visual/media treatment: no directional arrow, animated record path, sales
  graphic, “hit” badge, or unreviewed recording. Availability and rights:
  `not-assessed`.
- Copy/presentation consistency and accessibility: the StoryPanel must keep
  the oral-history attribution and absence of contemporary confirmation in the
  Event text; a map cannot replace those words.
- Unsupported future capability: source-layer comparison or annotated record
  circulation is future product/content work, not an MVP baseline need.

## Relationship treatment matrix

| Relationship type and IDs | Baseline treatment | Prohibited visual implication |
| --- | --- | --- |
| Documented/structural: `rel-loft-gallery-adaptation`, `rel-loft-pool-organizer-place-change`, `rel-gallery-garage-work-continuity`, `rel-garage-heartbeat-place-practice` | Preserve as qualified prose and, only if separately reviewed canonical connections exist, textual Related-tab summaries. | General influence arrow, continuous route path, merged Loft marker, or causal lineage. |
| Parallel/contrast: `rel-loft-stmarys-parallel-practice`, `rel-stmarys-gallery-agency-contrast`, `rel-leviticus-gallery-label-interface`, `rel-leviticus-pool-exchange-contrast`, `rel-pool-heartbeat-circulation-contrast` | Sequential Event selection and section framing only. | Any connector, migration path, feedback loop, Pool-to-Garage line, or diagram of a unified network. |

## Media and artifact position

No image, audio, video, document scan, flyer, record art, or map image is
selected for this version. The historical Sources above are research evidence,
not approved display assets. For every possible media lead, relevance,
Event linkage, availability, attribution, rights, stability, accessibility, and
experience readiness are `not-assessed` until a later Human review.

The current product can display a reviewed image or playable/external media
link within a selected Event's Media tab. It does not make a Source URL an
asset, establish rights, or supply a historical visual claim. A later media
proposal must name one Event, an exact asset URL, provider, type, relevance,
attribution, rights status, and accessible text before it may enter review.

## Accessibility and consistency requirements

- Use map selection, Timeline selection, and StoryPanel navigation as one
  shared Event state; do not create a second visual-only route state.
- Keep event title, date/range, place, route context, selection, focused-place
  state, source links, and all historical qualifications available as text.
- Do not rely on marker color, an arrow direction, a spatial arrangement, or a
  media thumbnail to communicate an historical relationship or uncertainty.
- If a later Event uses multiple places, use the current accessible “Places in
  this event” controls and state any place relationship label and source in
  text. Group membership alone does not authorize a connector.
- Keep selected Garage Events distinguishable by Event title and date; repeated
  place identity must not appear as duplicate simultaneous geography.

## Future capability proposals — outside this baseline

- Cross-Event relationship rendering with source-aware textual labels and
  explicit uncertainty treatment.
- A non-causal side-by-side section comparison surface.
- A reviewed document/image viewer for primary-source scans.
- Time-scrubbed markers, animated circulation, route playback, and record-flow
  diagrams.

None is required to present the approved baseline faithfully. If pursued, each
requires a separate Intake Issue; this route experiment neither implements nor
authorizes it.

## Human checkpoint and stop condition

Recommendation: accept the conservative baseline—Event-by-Event selection,
Timeline sequence, and StoryPanel prose/source treatment, with no cross-Event
map connectors and no media asset—for the purposes of this experimental route
version.

Verdict: `awaiting-human-presentation-decision`.

The run is `checkpointed`. The Human must accept, correct, or reject the visual
historical claims, media treatment, and presentation intent in this file before
Step 11 may run. That decision does not approve Sources, media rights,
editorial-review state, canonical data, seed promotion, publication, push, or
integration.
