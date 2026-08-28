# Step 10b — Presentation and visual claims

## Stage record

- Experiment ID: `underground-disco-interactive`
- Version ID: `disco-baseline-1.1-01`
- Method: `baseline-1.1`
- Stage: `10b`
- Status: `checkpointed`
- Named inputs: [`00-run-brief.md`](00-run-brief.md),
  [`07-cross-event-synthesis.md`](07-cross-event-synthesis.md),
  [`09-evidence-audit.md`](09-evidence-audit.md), and
  [`10a-final-route-copy.md`](10a-final-route-copy.md)
- Product evidence inspected:
  [`MapView.svelte`](../../../../../../frontend/src/lib/components/MapView.svelte),
  [`Timeline.svelte`](../../../../../../frontend/src/lib/components/Timeline.svelte),
  [`StoryPanel.svelte`](../../../../../../frontend/src/lib/components/StoryPanel.svelte),
  [`MediaEmbed.svelte`](../../../../../../frontend/src/lib/components/MediaEmbed.svelte),
  [`current-frontend-design.md`](../../../../../design/current-frontend-design.md),
  and [`seed-data-structure.md`](../../../../../data/seed-data-structure.md)
- Human decision carried forward: the step-10a reader copy is accepted for
  experimental continuation into this stage. Source, media, rights,
  route-version, canonical, editorial-review, and publication decisions remain
  unmade.

## Boundary and method

This document specifies how the accepted experimental copy can be presented
without changing its historical meaning. It distinguishes three states:

1. **Implemented capability:** behavior verified in current code and
   documentation.
2. **Baseline route need:** what this route must communicate if it later enters
   a separately approved canonical and runtime handoff.
3. **Unsupported future capability:** a possible product treatment that is not
   implemented or authorized here.

The experimental route is not canonical seed data and is not currently
available in the running explorer. Therefore every “implemented map state”
below names a supported product mechanism, not a claim that this route already
has runtime markers, connections, or media. Historical coordinates remain
`unknown` for all seven Events; the current point positions may be used only as
comparison aids after a separately reviewed data handoff.

## Current capability audit

| Surface | Observed implementation | Supported baseline use | Unsupported implication or behavior |
| --- | --- | --- | --- |
| Map | All Events of one active route receive markers; route selection fits their place bounds; selected Event/place state pans or fits and receives stronger marker/place emphasis. | Show the route's bounded geographic spread, then focus one Event at a time. | Marker proximity does not establish a network, influence, shared community, or verified historical coordinate. |
| Map place geometry | A selected Event may expose several ordered places, Polygon/MultiPolygon geometry, and sourced directional connectors between places owned by that one Event. | Use only when a future Event record contains reviewed multi-place evidence. | These connectors are not cross-Event relationship lines and cannot visualize the step-07 relationship records automatically. |
| Timeline | All active-route Events receive selectable ticks and cards by `year_start`; the selected Event range is highlighted and its card is centered. | Communicate dates, overlaps, and the currently selected Event. | Horizontal order alone does not communicate influence, narrative section, parallelism, or causality. |
| StoryPanel | One selected Event is shown at a time with story copy, places, Sources, previous/next navigation, Media, and Related tabs. | Preserve self-contained Event chapters and put qualifications in readable copy. | Previous/next navigation is exposition, not a historical chain. Related items require structured runtime connections not created here. |
| Media | Reviewed image links can show alt text; supported YouTube links can embed or remain external; other leads can be linked. | Present only Human-approved, stable, attributed, rights-compatible material with accessible alternatives. | A Source URL, online preview, playable link, or archive holding is not reuse permission or publication approval. |

The implementation does not currently supply narrative-section overlays,
simultaneous multi-Event focus, semantic clustering, cross-Event map lines,
route playback, or presentation-specific camera choreography.

## Route and section presentation records

### `moment-route-overview`

- Owning IDs: route `underground-disco-interactive`; sections
  `section-collective-rooms-and-practices`,
  `section-owning-nightlife-and-organizing-record-access`, and
  `section-building-and-testing-a-dance-institution`.
- Implemented map state: after a future approved runtime handoff, the existing
  active-route marker field and route-bounds fit can show all seven Events;
  today this experimental route has no runtime state.
- Historical claim communicated: the cohort contains one Bronx Event, one
  Midtown institution, and five lower-Manhattan Events within a 1970–1981
  route about overlapping forms of collective power.
- Evidence basis: step-07 geography audit and thesis; step-09
  `claim-route-01` and `claim-route-08`; accepted step-10a scope and
  introduction.
- Prohibited implication: do not call the cohort citywide, treat downtown
  density as one network, add Queens/Brooklyn context markers, or infer
  historical coordinate precision.
- Visual/media treatment, availability, and rights: use the existing route fit,
  normal route-colored markers, and text scope only. No media is needed for the
  overview; availability and rights are `not-assessed`.
- Copy/presentation consistency and accessibility: the title/scope and
  introduction must state the three-area distribution and reject a single
  lineage; route identity and selected state cannot rely on color or position.
- Baseline need: orient the reader to bounded place, time, and argument before
  individual selection.
- Unsupported future capability: an overview annotated by narrative section or
  relationship class. Any implementation belongs in separate Intake work.

### `moment-section-collective-rooms`

- Owning IDs: `section-collective-rooms-and-practices`; Events
  `loft-broadway-party-1970-1974`, `st-marys-dance-incubator-1974`, and
  `gallery-mercer-room-1974-1977`.
- Implemented map state: the three Event markers can remain visible as part of
  the full active-route field while selection focuses one Event; timeline ticks
  show their overlapping dates.
- Historical claim communicated: a private party, a Bronx community center,
  and a commercial downtown room organized collective dancing through
  different communities, hosts, and institutional forms.
- Evidence basis: the matching step-07 narrative-section record and step-10a
  section framing; step-09 `claim-section-01`–`claim-section-03`.
- Prohibited implication: the 1974 overlap does not establish a movement path,
  shared membership, or Loft-to-St. Mary's-to-Gallery succession.
- Visual/media treatment, availability, and rights: separate points and
  selected-Event focus; no cross-Event line. Event-specific leads remain
  unapproved in the media records below.
- Copy/presentation consistency and accessibility: the section text must name
  “separate settings” and “overlapping histories”; parallelism must be stated,
  not encoded only by simultaneous marker visibility.
- Baseline need: compare room-making and dance practice without collapsing the
  three social settings.
- Unsupported future capability: a three-Event comparison focus or section
  overlay. It must preserve separate identities and requires separate Intake.

### `moment-section-ownership-access`

- Owning IDs: `section-owning-nightlife-and-organizing-record-access`; Events
  `leviticus-opening-and-label-parties-1974-1976` and
  `new-york-record-pool-launch-1975`.
- Implemented map state: Midtown and Prince Street remain distinct markers;
  the timeline shows overlap and lets each Event be selected independently.
- Historical claim communicated: Black venue ownership and label promotion at
  Leviticus differed from working-DJ organization around distribution and
  requested critique in the Pool.
- Evidence basis: the matching step-07 section record and step-10a framing;
  step-09 `claim-section-04`–`claim-section-06`.
- Prohibited implication: proximity, overlapping years, or label contact does
  not establish a shared program, Pool membership, floor feedback, or a causal
  exchange.
- Visual/media treatment, availability, and rights: use separate markers and
  prose comparison only; no arrow or merged symbol. Document leads remain
  unapproved.
- Copy/presentation consistency and accessibility: promotion, distribution,
  critique, and represented-floor authority must stay textually distinct.
- Baseline need: let readers compare two institutional mechanisms without
  converting comparison into connection.
- Unsupported future capability: a labeled side-by-side section comparison;
  no current semantic comparison state exists.

### `moment-section-garage-heartbeat`

- Owning IDs: `section-building-and-testing-a-dance-institution`; Events
  `paradise-garage-buildout-opening-1977-1978` and
  `heartbeat-garage-vinylmania-1981`.
- Implemented map state: both Events may have markers in the route field, but
  the same Garage place should be revisited through sequential Event selection;
  the timeline differentiates 1977–78 from 1981.
- Historical claim communicated: institution-building established the Garage
  setting later revisited by one attributed record-reception account.
- Evidence basis: the matching step-07 section record and
  `rel-garage-heartbeat-setting`; step-09 `claim-section-07` and Heartbeat
  claims; step-10a section framing.
- Prohibited implication: do not show two simultaneous Garage states, imply
  the opening caused the later floor response, or turn Garage–Vinylmania into
  an unqualified causal chain.
- Visual/media treatment, availability, and rights: selected-Event focus at the
  reused place plus explicit date/copy change. Vinylmania geometry remains
  unavailable; all media remains unapproved.
- Copy/presentation consistency and accessibility: date, Event title, and
  attributed language must distinguish the two visits even when the place
  marker overlaps.
- Baseline need: communicate reuse of one setting across time without duplicate
  simultaneous historical presence.
- Unsupported future capability: time-aware same-place marker stacking or
  animated revisiting; separate Intake is required.

## Event presentation records

### `moment-event-loft-broadway`

- Owning IDs: Event `loft-broadway-party-1970-1974`; section
  `section-collective-rooms-and-practices`.
- Implemented map state: select the Broadway Event marker; the map pans to its
  current point and the timeline highlights 1970–74.
- Historical claim communicated: Mancuso organized a private, invitation-based
  party around dancers, full records, and careful sound at 645–647 Broadway.
- Evidence basis: step-09 `claim-loft-01`–`claim-loft-06` and the step-10a
  final-stop record, supported by the institutional Loft history and Mancuso
  and Siano oral histories linked there.
- Prohibited implication: the marker is not every later Loft address; the party
  is not the sole origin of Disco or every Gallery practice.
- Visual/media treatment, availability, and rights: single selected point and
  Event copy. Invitation, portrait, oral-history, and listening leads are
  online but reuse rights remain unresolved.
- Copy/presentation consistency and accessibility: Broadway, date boundary,
  private-party model, and attributed influence limits remain visible in text.
- Baseline need: establish one bounded room model and starting comparison.
- Unsupported future capability: a reviewed address-change visualization from
  Broadway to Prince Street; no movement line is authorized.

### `moment-event-stmarys`

- Owning IDs: Event `st-marys-dance-incubator-1974`; section
  `section-collective-rooms-and-practices`.
- Implemented map state: select the Bronx marker; the timeline shows the
  summer-1974 start while the unknown end remains copy, not false range detail.
- Historical claim communicated: Puerto Rican teenagers used recurring St.
  Mary's parties as a setting for Latin Hustle and Rocking practice.
- Evidence basis: step-09 `claim-stmarys-01`–`claim-stmarys-05` and step-10a
  final-stop record, supported by the Bronx County Historical Society sources.
- Prohibited implication: no downtown influence path, final party date, all-
  Bronx representativeness, or later participant destinations are established.
- Visual/media treatment, availability, and rights: selected Bronx point;
  photographs may be proposed only after item-level review. Reproduction
  permission is unknown.
- Copy/presentation consistency and accessibility: `summer 1974 onward` and
  the unknown end must remain explicit; photographs need participant-sensitive
  identification and alt text.
- Baseline need: make the route's geographically distinct dancer-led practice
  visible without using it as a token citywide claim.
- Unsupported future capability: sourced movement paths or dance-motion media;
  neither evidence nor product treatment is currently available.

### `moment-event-gallery`

- Owning IDs: Event `gallery-mercer-room-1974-1977`; section
  `section-collective-rooms-and-practices`.
- Implemented map state: select the Mercer Street marker and its 1974–77
  timeline range.
- Historical claim communicated: the Gallery coordinated a predominantly Black
  gay dance crowd, sound, lighting, labor, and label-supplied records in one
  commercial room.
- Evidence basis: step-09 `claim-gallery-01`–`claim-gallery-06` and step-10a
  final-stop record, supported by the institutional history and Siano oral
  history linked there.
- Prohibited implication: do not present the Gallery as a copy of the Loft, a
  formal label-feedback system, or a complete account of dancers and workers.
- Visual/media treatment, availability, and rights: selected point; dance-floor
  photographs and film are strong leads but layered rights and access remain
  unresolved.
- Copy/presentation consistency and accessibility: Siano-centered evidence and
  participant-representation limits stay visible; image descriptions cannot
  infer unnamed identities.
- Baseline need: show the route's richest room-level coordination example.
- Unsupported future capability: room-detail overlays, lighting animation, or
  a Loft–Gallery adaptation line; all need separate product and Human review.

### `moment-event-leviticus`

- Owning IDs: Event `leviticus-opening-and-label-parties-1974-1976`; section
  `section-owning-nightlife-and-organizing-record-access`.
- Implemented map state: select the West 33rd Street marker and show the
  bounded 1974–76 timeline range.
- Historical claim communicated: eight Black Best of Friends partners owned a
  Midtown venue that connected nightlife business to label promotion.
- Evidence basis: step-09 `claim-leviticus-01`–`claim-leviticus-05` and
  step-10a final-stop record, supported by the linked Cash Box, Billboard,
  Hankin, and Apple ROUTES sources.
- Prohibited implication: do not resolve the exact opening day, add Queens or
  Brooklyn Event markers, or infer floor-to-label feedback and label decisions.
- Visual/media treatment, availability, and rights: selected Midtown point;
  trade photograph, flyers, postcards, and oral history remain link or research
  leads until rights and item context are approved.
- Copy/presentation consistency and accessibility: the attributed date and
  conflicting contemporary/later year evidence remain textual; ownership must
  not be reduced to a color cue or generic “community” label.
- Baseline need: present Black ownership and promotion as a distinct form of
  institutional power.
- Unsupported future capability: contextual network places around Best of
  Friends; they are not accepted Events or verified route geometry.

### `moment-event-record-pool`

- Owning IDs: Event `new-york-record-pool-launch-1975`; section
  `section-owning-nightlife-and-organizing-record-access`.
- Implemented map state: select the Prince Street meeting marker and 1975
  timeline position; keep it separate from the earlier Broadway Loft Event.
- Historical claim communicated: working DJs organized distribution of
  promotional records and offered requested critiques to labels.
- Evidence basis: step-09 `claim-pool-01`–`claim-pool-04`,
  `claim-section-06`, and the step-10a final-stop record, supported by the
  linked Billboard, Business History, and Mancuso sources.
- Prohibited implication: do not merge Broadway and Prince Street, present the
  Pool as every dancer's voice, settle contested governance, or imply a proved
  record or label outcome.
- Visual/media treatment, availability, and rights: selected Prince Street
  point; contemporary articles and later mailer are document leads. Original
  minutes, Declaration, and feedback sheets remain unavailable or unresolved.
- Copy/presentation consistency and accessibility: address/function change and
  the difference between offered critique and proved influence must be stated.
- Baseline need: make formal organization around record access legible.
- Unsupported future capability: an organizational-flow diagram or feedback
  loop; current evidence and product behavior do not support one.

### `moment-event-paradise-garage`

- Owning IDs: Event `paradise-garage-buildout-opening-1977-1978`; section
  `section-building-and-testing-a-dance-institution`.
- Implemented map state: select 84 King Street and highlight the 1977–78 Event
  range.
- Historical claim communicated: construction parties developed into a
  membership club organized through ownership, finance, sound, staff,
  resident-DJ practice, and dancers.
- Evidence basis: step-09 `claim-garage-01`–`claim-garage-04` and step-10a
  final-stop record, supported by the Garage institutional history, NYU Fales
  finding aid, and Siano oral history.
- Prohibited implication: Black and Latino gay community centrality is not
  Black ownership; Gallery work continuity does not prove institutional
  succession or complete design authority.
- Visual/media treatment, availability, and rights: selected Garage point;
  archival photos, tickets, rules, flyers, sign, and oral histories are strong
  leads but require item access, rights-holder permission, attribution, and
  Human selection.
- Copy/presentation consistency and accessibility: name distinct roles and do
  not use one hero image as evidence for all members or workers.
- Baseline need: communicate institution-building without flattening authority.
- Unsupported future capability: room-buildout sequence, archive gallery, or
  Gallery-to-Garage line; none is authorized here.

### `moment-event-heartbeat`

- Owning IDs: Event `heartbeat-garage-vinylmania-1981`; section
  `section-building-and-testing-a-dance-institution`.
- Implemented map state: select the 1981 Event at the reused Garage place;
  timeline and Event title distinguish it from the opening. Do not add a
  Vinylmania marker because reviewed geometry is unavailable.
- Historical claim communicated: Llanos later recalled a resistant Garage
  floor, repeated Levan plays, and next-day Vinylmania demand; contemporary
  evidence corroborates circulation and later retail prominence, not the exact
  sequence.
- Evidence basis: step-09 `claim-heartbeat-01`–`claim-heartbeat-03` and the
  step-10a final-stop record, supported by the linked Record World, Time Out,
  Vinylmania, Billboard, and NYU sources.
- Prohibited implication: no arrow may imply that the floor caused release,
  remix, radio, sales, charts, hit status, or a verified next-day store line.
- Visual/media treatment, availability, and rights: selected Garage point and
  attributed copy; audio, label art, and store material remain external,
  unlicensed leads.
- Copy/presentation consistency and accessibility: “In Llanos's later account”
  and the corroboration limit must remain adjacent to any media or visual cue;
  audio requires captions/transcript context and a non-audio account.
- Baseline need: focus the route's named musical object while preserving
  fallible listener response and retrospective uncertainty.
- Unsupported future capability: a Garage-to-Vinylmania line, store marker,
  replay animation, or synchronized audio path.

## Relationship-mode treatment

| Mode | Baseline treatment | Prohibited implication | Current/future boundary |
| --- | --- | --- | --- |
| Parallel | State in section copy that St. Mary's, the Gallery, and Leviticus developed different forms of collective agency in overlapping 1974 time; retain separate markers and Event selections. | Simultaneity does not establish influence, shared participants, one community, or a causal sequence. | Current copy, markers, and timeline can communicate the baseline. Simultaneous multi-Event focus is unsupported future capability. |
| Sequential | Use timeline dates and one selected Event at a time for the Broadway-to-Prince Street context and the two Garage Events; name the changed address, function, date, or scale in copy. | Interface order and a reused place do not establish causality or simultaneous historical presence. | Current timeline and selection support the baseline. Time-aware marker stacking or playback is future capability. |
| Network | Use the route overview and Event prose to name only documented personal, organizational, and record-specific links; keep Queens/Brooklyn Best of Friends context and unknown St. Mary's paths off the map. | Downtown density, label contact, a shared person, or route membership does not make one citywide network. | No network graphic is needed. Cross-Event map geometry would be unsupported future capability and would require separate evidence and Intake. |
| Contrast | Use labeled prose for Loft/Garage room models, Leviticus/Gallery label interfaces, Leviticus/Pool institutional control, and Pool/“Heartbeat” circulation evidence. | A comparison is not an exchange, transformation, lineage, or proof that the paired Events shared a program. | Current StoryPanel and section copy support the baseline. Semantic side-by-side comparison is future capability. |
| Convergence | Describe three analytic concentrations in Event copy: the Gallery brings crowd, room design, labor, and label-supplied records into one setting; the Garage opening brings membership, community, construction, sound, staff, and resident-DJ practice into one institution; “Heartbeat” brings a named recording, reportedly fallible floor response, resident DJ, and specialist retail into one attributed account. | “Convergence” does not mean that earlier communities or networks merged, that one participant controlled every element, or that the “Heartbeat” sequence proves market causality. | Current single-Event copy can communicate each bounded convergence. A merged-network symbol, convergence animation, or multi-Event aggregation is unsupported future capability. |

## Relationship presentation records

Cross-Event map lines are unsupported. The baseline treatment for every record
is qualified StoryPanel or section prose; a future structured Related-tab item
would require a separate canonical data decision and must retain the basis and
prohibited implication below.

### `moment-rel-loft-gallery-adaptation`

- Owning IDs: relationship `rel-loft-gallery-adaptation`; Events
  `loft-broadway-party-1970-1974` → `gallery-mercer-room-1974-1977`.
- Implemented map state: separate Event markers and sequential selection; no
  cross-Event line.
- Historical claim communicated: Siano attributed selected Gallery dance-floor
  practices to adaptation from the Loft while stressing that the Gallery was
  not a copy.
- Evidence basis: documented-influence record in step 07, supported by the
  [Siano oral history](https://daily.redbullmusicacademy.com/2018/02/nicky-siano-interview-dj-history/).
- Prohibited implication: no universal lineage, sole origin, or transfer of
  every room practice.
- Visual/media treatment, availability, and rights: qualified prose contrast;
  oral-history transcript is available, reuse rights `unknown`.
- Copy/presentation consistency and accessibility: attribution and “not a
  copy” limit must accompany any relationship cue.
- Baseline need: preserve the route's one attributed adaptation link.
- Unsupported future capability: a labeled influence connector that can carry
  attribution and uncertainty; separate Intake required.

### `moment-rel-loft-pool-context`

- Owning IDs: relationship `rel-loft-pool-organizational-context`; Events
  `loft-broadway-party-1970-1974` → `new-york-record-pool-launch-1975`.
- Implemented map state: separate Broadway and Prince Street markers and Event
  selections; no continuous venue marker or route line.
- Historical claim communicated: Mancuso's party later used another address,
  and the temporarily closed Prince Street Loft hosted Pool organization.
- Evidence basis: documented structural-link record in step 07, supported by
  the linked Loft, Billboard, and Business History sources.
- Prohibited implication: the two Events are not the same place or period;
  Loft dancers do not automatically become Pool members or represented voices.
- Visual/media treatment, availability, and rights: address/function labels in
  copy only; media `not-assessed` for this relationship.
- Copy/presentation consistency and accessibility: both street addresses and
  distinct functions remain readable outside the map.
- Baseline need: prevent mistaken place merging while explaining the bounded
  organizational context.
- Unsupported future capability: a time-aware address-change connector.

### `moment-rel-gallery-garage-work`

- Owning IDs: relationship `rel-gallery-garage-work-continuity`; Events
  `gallery-mercer-room-1974-1977` →
  `paradise-garage-buildout-opening-1977-1978`.
- Implemented map state: separate markers and sequential selection; no
  cross-Event line.
- Historical claim communicated: Levan's documented Gallery work preceded his
  resident-DJ and sound-buildout role at the Garage.
- Evidence basis: documented-influence record in step 07, supported by the
  [Siano oral history](https://daily.redbullmusicacademy.com/2018/02/nicky-siano-interview-dj-history/)
  and [Garage institutional history](https://www.nyclgbtsites.org/site/paradise-garage/).
- Prohibited implication: person-centered continuity does not prove the
  Gallery caused the Garage's design, community, or membership model.
- Visual/media treatment, availability, and rights: qualified prose and
  separate Event media; rights remain unresolved.
- Copy/presentation consistency and accessibility: name Levan and the bounded
  roles; never label institutional succession.
- Baseline need: retain a documented personal continuity without flattening
  two institutions.
- Unsupported future capability: a person-centered, qualified relationship
  overlay.

### `moment-rel-garage-heartbeat-setting`

- Owning IDs: relationship `rel-garage-heartbeat-setting`; Events
  `paradise-garage-buildout-opening-1977-1978` →
  `heartbeat-garage-vinylmania-1981`.
- Implemented map state: sequentially revisit the same Garage place via Event
  and timeline selection; do not display simultaneous duplicate emphasis.
- Historical claim communicated: the earlier Event establishes the room,
  membership, sound, resident DJ, and dancer setting of the later account.
- Evidence basis: documented structural-link record in step 07, supported by
  the Garage history, Time Out oral history, and Record World evidence linked
  there.
- Prohibited implication: the club opening did not cause a particular floor
  response; the retrospective store sequence is not independently documented.
- Visual/media treatment, availability, and rights: same-place revisit and
  changed date/copy; media remains unapproved.
- Copy/presentation consistency and accessibility: the interface must announce
  the selected Event and date, not rely on marker replacement alone.
- Baseline need: distinguish setting continuity from causality.
- Unsupported future capability: same-place temporal stacking or playback.

### `moment-rel-stmarys-gallery-parallel`

- Owning IDs: relationship `rel-stmarys-gallery-parallel-dance-practice`;
  Events `st-marys-dance-incubator-1974` ↔
  `gallery-mercer-room-1974-1977`.
- Implemented map state: separate Bronx and downtown markers; overlapping
  timeline positions; no line.
- Historical claim communicated: distinct dance practices developed in
  overlapping years through a community center and commercial club room.
- Evidence basis: interpretive-synthesis record in step 07, supported by the
  Bronx County Historical Society and Gallery institutional sources linked
  there; no direct exchange was found.
- Prohibited implication: shared year and city do not prove influence, shared
  membership, or one dance community.
- Visual/media treatment, availability, and rights: juxtaposition in section
  prose; Event media remains separately unapproved.
- Copy/presentation consistency and accessibility: explicitly label the
  relationship `parallel`, not merely adjacent.
- Baseline need: correct single-file chronology.
- Unsupported future capability: simultaneous two-Event comparison focus.

### `moment-rel-loft-garage-contrast`

- Owning IDs: relationship `rel-loft-garage-room-model-contrast`; Events
  `loft-broadway-party-1970-1974` ↔
  `paradise-garage-buildout-opening-1977-1978`.
- Implemented map state: separate points and dates selected independently.
- Historical claim communicated: both organized membership, sound, and dancing,
  but one was a hosted domestic party and the other a purpose-built club.
- Evidence basis: interpretive-synthesis contrast in step 07 and the two
  accepted final stops.
- Prohibited implication: common components do not prove direct succession,
  scaled transformation, or equivalent ownership/community authority.
- Visual/media treatment, availability, and rights: labeled prose comparison;
  media `not-assessed` at relationship level.
- Copy/presentation consistency and accessibility: name both room models and
  dates; never use an unlabeled transformation arrow.
- Baseline need: compare institutional form across the route.
- Unsupported future capability: a side-by-side room-model comparison state.

### `moment-rel-leviticus-gallery-contrast`

- Owning IDs: relationship `rel-leviticus-gallery-label-interface-contrast`;
  Events `leviticus-opening-and-label-parties-1974-1976` ↔
  `gallery-mercer-room-1974-1977`.
- Implemented map state: separate markers; no exchange line.
- Historical claim communicated: Leviticus hosted label press parties while
  labels supplied records to the Gallery's DJ; neither documents formal dancer
  feedback.
- Evidence basis: interpretive-synthesis contrast in step 07 and the accepted
  Leviticus and Gallery evidence records.
- Prohibited implication: no shared label program, Pool participation, response
  channel, or label decision caused by either floor.
- Visual/media treatment, availability, and rights: prose comparison; Event
  artifact rights remain unresolved.
- Copy/presentation consistency and accessibility: use the distinct terms
  `promotion` and `record supply`; do not label `feedback`.
- Baseline need: differentiate two music-business interfaces.
- Unsupported future capability: semantic comparison overlay.

### `moment-rel-leviticus-pool-contrast`

- Owning IDs: relationship `rel-leviticus-pool-industry-interface-contrast`;
  Events `leviticus-opening-and-label-parties-1974-1976` ↔
  `new-york-record-pool-launch-1975`.
- Implemented map state: separate Midtown and Prince Street selections; no
  directional line.
- Historical claim communicated: Black-owned venue promotion and working-DJ
  distribution/requested critique were different answers to control over
  nightlife and record access.
- Evidence basis: interpretive-synthesis contrast in step 07 and the accepted
  Event evidence.
- Prohibited implication: no Best of Friends/Leviticus Pool participation,
  shared program, or equivalence among promotion, distribution, critique, and
  represented floor response.
- Visual/media treatment, availability, and rights: section prose and separate
  document leads; rights remain unresolved.
- Copy/presentation consistency and accessibility: the comparison label and
  institutional differences must be textual.
- Baseline need: make the section's central contrast explicit.
- Unsupported future capability: paired institutional comparison state.

### `moment-rel-pool-heartbeat-contrast`

- Owning IDs: relationship `rel-pool-heartbeat-circulation-contrast`; Events
  `new-york-record-pool-launch-1975` ↔
  `heartbeat-garage-vinylmania-1981`.
- Implemented map state: separate Event selections and dates; no feedback loop
  or lineage line.
- Historical claim communicated: the Pool documents a formal collective
  channel; “Heartbeat” supplies an attributed, record-specific floor-to-retail
  sequence.
- Evidence basis: interpretive-synthesis contrast in step 07, supported by the
  Pool sources, Llanos account, Vinylmania history, and trade evidence linked
  in the accepted records.
- Prohibited implication: the later episode is not a Pool result and does not
  prove that feedback changed release, mix, radio, sales, or charts.
- Visual/media treatment, availability, and rights: prose transition from
  organized infrastructure to situated listening; media remains unapproved.
- Copy/presentation consistency and accessibility: keep `formal channel` and
  `attributed sequence` visibly different.
- Baseline need: compare two bounded ways record response becomes legible.
- Unsupported future capability: animated circulation or feedback-loop diagram.

## Transition presentation records

### `moment-transition-rooms-to-access`

- Owning IDs: from `section-collective-rooms-and-practices` to
  `section-owning-nightlife-and-organizing-record-access`.
- Implemented map state: normal previous/next Event navigation moves from the
  Gallery to Leviticus while all route markers remain visible.
- Historical claim communicated: the route changes its question from how rooms
  and dancers shaped practice to who controlled ownership, promotion,
  distribution, and critique.
- Evidence basis: step-07 section transitions and step-09
  `claim-transition-01`; accepted step-10a transition.
- Prohibited implication: the Gallery did not produce Leviticus or the Pool;
  the transition is argumentative, not causal.
- Visual/media treatment, availability, and rights: copy-led transition; no
  special media, line, or animation. Availability/rights `not-assessed`.
- Copy/presentation consistency and accessibility: retain the explicit change
  of question; next navigation alone is insufficient.
- Baseline need: preserve argument-centric structure during nonlinear use.
- Unsupported future capability: section boundary cue in map/timeline.

### `moment-transition-access-to-garage`

- Owning IDs: from `section-owning-nightlife-and-organizing-record-access` to
  `section-building-and-testing-a-dance-institution`.
- Implemented map state: previous/next navigation moves from the Pool to the
  Garage opening; timeline advances from 1975 to 1977–78.
- Historical claim communicated: the route moves from distinct ownership and
  access mechanisms to a longer-lived club institution and then a contested
  record-reception episode.
- Evidence basis: step-07 section transitions and step-09
  `claim-transition-02`; accepted step-10a transition.
- Prohibited implication: the Pool did not cause the Garage and no earlier
  institution is absorbed into it.
- Visual/media treatment, availability, and rights: copy-led transition; no
  line, convergence animation, or media. Availability/rights `not-assessed`.
- Copy/presentation consistency and accessibility: the transition must state
  the changed institutional scale and continued contested authority.
- Baseline need: connect section questions without manufacturing lineage.
- Unsupported future capability: section-aware camera or playback transition.

## Media and artifact presentation records

Every item below is an unapproved lead. `Available` means it can currently be
viewed, read, requested, or linked; it does not mean stable delivery, reuse
permission, relevance approval, or publication authority.

### `moment-media-loft`

- Owning IDs: Event `loft-broadway-party-1970-1974`.
- Implemented map state: none; the current Media tab could present a separately
  approved image or external link for a selected Event.
- Historical claim communicated: invitation practice, Mancuso's testimony, or
  representative listening—not an undocumented Broadway dance-floor scene.
- Evidence basis: step-06 Loft media ledger: 1972 invitation and Mancuso/Siano
  oral histories at the [Loft institutional page](https://www.nyclgbtsites.org/site/david-mancuso-residence-the-loft/),
  [Mancuso interview](https://daily.redbullmusicacademy.com/2016/11/david-mancuso-dj-history-interview/),
  and [Siano interview](https://daily.redbullmusicacademy.com/2018/02/nicky-siano-interview-dj-history/).
- Prohibited implication: the circa-1975 portrait is not a Broadway party
  scene; representative records do not prove exact play dates.
- Visual/media treatment, availability, and rights: online images/transcripts
  are available; reproduction, audio, artwork, and recording rights are
  `unknown` or uncleared. Human relevance and stable-delivery review pending.
- Copy/presentation consistency and accessibility: invitation needs descriptive
  alt text; oral history should use transcript access and clear attribution.
- Baseline need: optional primary-adjacent orientation, not required factual
  content.
- Unsupported future capability: none required; existing image/external-link
  mechanisms suffice after approval.

### `moment-media-stmarys`

- Owning IDs: Event `st-marys-dance-incubator-1974`.
- Implemented map state: none; an approved image could appear in the selected
  Event's Media tab.
- Historical claim communicated: documented Hustle jams and girls dancing at
  St. Mary's around 1974–75.
- Evidence basis: step-06 media ledger and the [Bronx County Historical Society
  exhibit](https://bronxhistoricalsociety.org/dance/2); related ephemera appears
  in the [Rocking exhibit](https://bronxhistoricalsociety.org/dance/3), and
  participant material is described by [Latin Empire
  Productions](https://www.latinempireproductions.com/film-and-media).
- Prohibited implication: not every image or flyer is St. Mary's-specific; no
  unidentified person's later path or consent may be inferred.
- Visual/media treatment, availability, and rights: images and captions are
  online; reproduction permission and film access are unresolved. Human
  relevance, naming, rights, and stability review pending.
- Copy/presentation consistency and accessibility: item-level caption, date,
  participant-sensitive alt text, and nonvisual dance explanation required.
- Baseline need: strongest embodied-dance lead in the cohort, optional until
  approved.
- Unsupported future capability: film or motion annotation is not required.

### `moment-media-gallery`

- Owning IDs: Event `gallery-mercer-room-1974-1977`.
- Implemented map state: none; approved images or external film/oral-history
  links fit current Media-tab mechanisms.
- Historical claim communicated: the Mercer Street room, dance floor, light
  system, and first-person room account.
- Evidence basis: step-06 media ledger; [Gallery institutional
  page](https://www.nyclgbtsites.org/site/the-gallery/) and [Siano oral
  history](https://daily.redbullmusicacademy.com/2018/02/nicky-siano-interview-dj-history/).
- Prohibited implication: images do not establish identities, universal dancer
  experience, formal feedback, or every design contribution.
- Visual/media treatment, availability, and rights: photographs, a documentary
  still/film lead, transcript, and representative recordings are available or
  discoverable; layered photo, film, interview, recording, and artwork rights
  are unresolved.
- Copy/presentation consistency and accessibility: preserve photographer/source
  attribution, item dates, careful alt text, transcript/caption access, and the
  Siano-centered evidence limit.
- Baseline need: optional room-level context; no image is required to carry the
  historical claim.
- Unsupported future capability: lighting animation or immersive room view.

### `moment-media-leviticus`

- Owning IDs: Event `leviticus-opening-and-label-parties-1974-1976`.
- Implemented map state: none; approved document images or external links fit
  current Media-tab mechanisms.
- Historical claim communicated: early label-event evidence, Black ownership,
  promotional practice, and venue ephemera.
- Evidence basis: step-06 media ledger: [Cash Box](https://www.worldradiohistory.com/Archive-All-Music/Cash-Box/70s/1974/CB-1974-12-28.pdf),
  [Billboard](https://www.worldradiohistory.com/Archive-All-Music/Billboard/70s/1976/Billboard%201976-03-06a.pdf),
  [Smithsonian collection](https://americanhistory.si.edu/collections/archival-collection/sova-nmah-ac-1614),
  and [Hankin oral history](https://wfuv.org/content/celebrating-black-pride-through-disco-0).
- Prohibited implication: a promotional photograph does not prove floor
  response; archival holdings do not settle the exact opening day.
- Visual/media treatment, availability, and rights: scans and transcript are
  online; some ephemera requires appointment. Publication/photo, archival, and
  interview reuse rights remain unresolved.
- Copy/presentation consistency and accessibility: retain date conflict,
  caption provenance, readable document summary, and transcript path.
- Baseline need: optional documentary/business evidence.
- Unsupported future capability: none required beyond reviewed document image
  or external link.

### `moment-media-record-pool`

- Owning IDs: Event `new-york-record-pool-launch-1975`.
- Implemented map state: none; approved document images or external links fit
  current Media-tab mechanisms.
- Historical claim communicated: contemporary organizational claims and later
  material evidence of Pool practice.
- Evidence basis: step-06 media ledger: [Billboard launch
  report](https://www.worldradiohistory.com/Archive-All-Music/Billboard/70s/1975/Billboard%201975-06-21.pdf),
  [1976 mailer](https://waxpoetics.com/collections/arthur-baker-collection/products/mancuso-record-pool-inc-mailer-1976-prince-street-sheet),
  [Business History article](https://www.tandfonline.com/doi/full/10.1080/00076791.2017.1308485),
  and [Mancuso interview](https://daily.redbullmusicacademy.com/2016/11/david-mancuso-dj-history-interview/).
- Prohibited implication: the 1976 mailer is not the 1975 launch; no located
  original feedback sheet proves a specific response or label outcome.
- Visual/media treatment, availability, and rights: scans, seller images,
  article, and transcript are available; original-document access and all
  reproduction rights remain unresolved.
- Copy/presentation consistency and accessibility: state document date/type,
  summarize legibly, and avoid presenting seller imagery as reuse permission.
- Baseline need: optional document-led explanation of organization.
- Unsupported future capability: feedback-flow visualization is neither needed
  nor supported.

### `moment-media-paradise-garage`

- Owning IDs: Event `paradise-garage-buildout-opening-1977-1978`.
- Implemented map state: none; approved images or external oral-history/archive
  links fit current Media-tab mechanisms.
- Historical claim communicated: club-goers, performers, room, membership
  artifacts, and attributed accounts of construction and sound.
- Evidence basis: step-06 media ledger: [NYU Fales
  MSS.483](https://findingaids.library.nyu.edu/fales/mss_483/all/), [Garage
  institutional page](https://www.nyclgbtsites.org/site/paradise-garage/), and
  [Time Out oral history](https://www.timeout.com/newyork/nightlife/paradise-garage-the-oral-history-of-nycs-greatest-club).
- Prohibited implication: one image or speaker cannot represent all members,
  workers, performers, or design authority; an unidentified 1981 image is not
  suitable without resolution.
- Visual/media treatment, availability, and rights: archive holdings require
  appointment and item review; attributed photographs and transcript are
  online. NYU is not the copyright owner and rights-holder permission remains
  required.
- Copy/presentation consistency and accessibility: item-level attribution,
  date/context, alt text, transcripts, and distinct ownership/community roles
  are required.
- Baseline need: optional institution and community texture.
- Unsupported future capability: archive gallery or construction sequence.

### `moment-media-heartbeat`

- Owning IDs: Event `heartbeat-garage-vinylmania-1981`.
- Implemented map state: none; current MediaEmbed supports reviewed YouTube
  embeds/external links, but no specific playable link is approved here.
- Historical claim communicated: the named 1981 recording, attributed floor
  account, and separately supported retail context.
- Evidence basis: step-06 media ledger: [Record World
  listing](https://www.worldradiohistory.com/Archive-Record-World/80s/81/RW-1981-04-11.pdf),
  [Time Out account](https://www.timeout.com/newyork/nightlife/paradise-garage-the-oral-history-of-nycs-greatest-club),
  and [Vinylmania oral history](https://daily.redbullmusicacademy.com/2016/02/vinylmania-oral-history/).
- Prohibited implication: playback, record art, or store photographs cannot
  turn the retrospective sequence into contemporaneous proof or causal fact.
- Visual/media treatment, availability, and rights: external streaming/reissue,
  label image, transcript, and store-photo leads exist; playback, recording,
  artwork, seller-image, interview, and photo rights are uncleared. No audio
  file may enter the repository.
- Copy/presentation consistency and accessibility: attribution and
  corroboration boundary must precede or accompany playback; provide captions
  or transcript context and a complete non-audio explanation.
- Baseline need: optional focused listening object after Human and rights
  review.
- Unsupported future capability: synchronized playback, replay counter, or
  Garage-to-store animation.

## Coverage and conflict audit

| Audit | Result |
| --- | --- |
| Stable Event IDs | Pass — all seven step-07/09/10a Event IDs have one Event presentation record and one media record. |
| Stable section IDs | Pass — all three section IDs have one section presentation record. |
| Relationship IDs | Pass — all four documented and five interpretive-synthesis step-07 relationship IDs are represented; no relationship was added or renamed. |
| Transition coverage | Pass — both inter-section transitions preserve their argumentative, non-causal role. |
| Current capability | Pass — route marker field, route/Event/place framing, timeline selection/range, StoryPanel single-Event presentation, within-Event place connectors, Related items, and Media behavior match inspected code/docs. |
| Current-versus-future boundary | Pass — the experimental route has no runtime state; section overlays, simultaneous focus, semantic clusters, cross-Event lines, animation, and camera choreography are marked unsupported future capabilities. |
| Historical qualifications | Pass — separate communities, address/function boundaries, unknown coordinates and movement, representation limits, ownership/community distinction, and the attributed “Heartbeat” sequence remain visible. |
| Media approval | Pass — every lead remains unapproved unless a later Human decision resolves relevance, attribution, rights, stability, availability, and accessibility. |
| Accessibility | Pass — material claims require textual/programmatic equivalents; media and motion require nonvisual/non-motion alternatives. |

## Product gaps routed out of this stage

The following are route needs or possible treatments, not authorized product
requirements:

1. Compare several Events or one narrative section without making several
   Events simultaneously selected.
2. Represent a qualified cross-Event relationship without turning its geometry
   into an unsupported historical path or causal arrow.
3. Distinguish two Events at one reused place across time without implying
   simultaneous presence.
4. Provide section-aware map/timeline orientation and non-motion equivalents.
5. Present item-level media approval, rights, attribution, stability, captions,
   transcripts, and alt text consistently.

No linked Issue is created here. After Human review, any retained product gap
requires its own Intake, Concept/Plan gates as applicable, and implementation
authorization.

## Verdict and Human checkpoint

- Agent verdict: `ready-for-human-presentation-review`.
- Current supported baseline: the route can be expressed with the implemented
  one-route marker field, one selected Event at a time, timeline chronology,
  StoryPanel copy/Sources, and separately approved Media-tab items after a
  future canonical/runtime handoff.
- Historical presentation recommendation: accept the route, section, Event,
  relationship, and transition claims with their recorded prohibited
  implications; reject unqualified cross-Event lines, simultaneous Garage
  states, citywide/network framing, and invented movement or store geometry.
- Media recommendation: keep all leads pending. No item has complete Human
  relevance, attribution, rights, stability, availability, and accessibility
  approval.
- Human decision: `pending` — accept, reject, or request correction of the
  visual historical claims, media intent, and presentation intent.
- Next permitted stage: none until the Human accepts step 10b and separately
  authorizes step 11.
- Canonical, editorial-review, and publication status: `not-authorized`.
