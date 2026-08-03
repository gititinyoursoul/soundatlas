# Route Entry Spatial Presentation

## Purpose

This document is the authoritative MVP design for presenting one event across
one or more point and area places in SoundAtlas. It defines the minimum
conceptual data, coordinated selection behavior, and map semantics needed to
avoid forcing every route event into one marker.

Issue #81 implements this design across seed data, backend schemas, API/static
delivery, frontend selection, map presentation, StoryPanel access, and tests.
It does not change route-candidate decisions.

## Decision Summary

- Keep `Event` as the MVP story, route-membership, connection, source, media,
  review, timeline, and primary selection identity.
- Let an event reference one or more places. Each place keeps a focus coordinate
  and may provide optional `Polygon` or `MultiPolygon` geometry.
- Support any combination of point and area places, including several distinct
  areas. Do not merge separate areas merely to fit one event.
- Treat multi-location membership as grouping only. Add an explicit edge only
  when sources support a relationship between two referenced places.
- Keep one selected event plus an optional focused place within that event.
- Keep `year_start` and `year_end`; communicate uncertainty in prose for now.
- Do not add narrative-role taxonomy, animation, geometry editing, or a new
  `RouteEntry` entity for the MVP.

## Authority And Boundaries

This document owns the target spatial presentation and interaction rules for
heterogeneous event geography.

- `docs/design/current-frontend-design.md` remains the baseline for the current
  implemented frontend and links here for the target extension.
- `docs/data/seed-data-structure.md` describes the implemented seed boundary
  and links here for the presentation rules.
- `docs/content/routes/birth-of-hip-hop/event-list.json` remains authoritative
  for candidate status and human review state. The matrix below does not alter
  either field.
- `docs/content/content-pipeline-interaction-contract.md` owns pipeline review
  and publication interaction rather than public map presentation.

Issue #70 established this design. Issue #81 is the approved runtime
implementation authority.

## Why Composition Fits The MVP

The current `Event` model requires one `place_id`. That works for a bounded
event such as the 1973 Sedgwick party, but it creates false precision for a
neighborhood context, repeated activity across several sites, several distinct
areas, or circulation between locations.

Replacing `Event` with a generalized `RouteEntry` would also require decisions
and migrations across event endpoints, connection IDs, enrichment, review,
selection, URLs, and editorial artifacts. The MVP does not need that broader
lifecycle. It needs an event to compose several spatial references honestly.

The dimensions remain independent:

```text
Event identity and story
  + time range
  + one or more referenced places
      + point coordinate
      + optional area geometry
  + zero or more explicit relationships between those places
```

## Minimum Conceptual Data

The fields below are the implemented runtime contract.

### Place Geometry

A place remains the reusable geographic identity. Latitude and longitude remain
required as the label, map-focus, relationship-anchor, and point fallback. A
route-relevant place may additionally carry area geometry and its provenance.

```json
{
  "id": "south-bronx",
  "name": "South Bronx",
  "latitude": 40.8176,
  "longitude": -73.9182,
  "geometry": {
    "type": "Polygon",
    "coordinates": []
  },
  "geometry_precision": "interpretive",
  "geometry_source_type": "curated",
  "geometry_source_note": "SoundAtlas-curated cultural-area outline, not an administrative boundary."
}
```

Minimum geometry rules:

- Geometry is optional and limited to GeoJSON `Polygon` or `MultiPolygon` for
  the MVP.
- A place without geometry presents as a point at its latitude and longitude.
- A place with geometry presents as an area; its coordinate remains the label
  and focus anchor.
- `geometry_precision` distinguishes a sourced site boundary from an
  interpretive or approximate cultural area.
- Geometry provenance is distinct from historical claim sourcing. Existing
  place and event `source_urls` continue to support historical content.
- Borough polygons remain frontend basemap context. They do not move into seed
  data because events do not reference or select them as editorial places.

### Event Spatial Presentation

An event references at least one place. The default place supplies focus only
when the event does not already have a valid focused place.

```json
{
  "place_ids": [
    "1520-sedgwick-avenue",
    "cedar-park-bronx",
    "bronx-river-houses"
  ],
  "default_place_id": "1520-sedgwick-avenue",
  "place_relationships": []
}
```

Rules:

- `place_ids` contains unique, existing place IDs and preserves editorial
  order.
- `default_place_id` must appear in `place_ids`.
- Legacy `place_id` is a temporary alias equal to `default_place_id`.
- Membership says only that the places participate in the same event story. It
  does not imply that every place connects to every other place.
- One event may reference points, areas, several areas, or a mixture.
- Existing `place_id` behaves as a compatibility form of a single-item
  `place_ids` list until an approved implementation migrates it.

### Explicit Place Relationships

An edge records a reviewed relationship between two places already referenced
by the event.

```json
{
  "from_place_id": "south-bronx",
  "to_place_id": "downtown-manhattan",
  "directionality": "forward",
  "context_label": "Local practices enter wider club and media circulation",
  "source_urls": ["https://example.org/source"]
}
```

`directionality` has three MVP meanings:

- `undirected`: the sources support a connection but not a direction.
- `forward`: the sources support movement or circulation from `from_place_id`
  toward `to_place_id`.
- `reciprocal`: the sources support exchange in both directions.

There is no `grouped` edge. An event's `place_ids` already group its locations.
An absent edge means no pairwise relationship is claimed. Context labels and
sources carry meaning; connector graphics never establish evidence or imply
causation on their own.

## Supported Spatial Footprints

| Footprint | Data composition | Map behavior | Selection behavior |
| --- | --- | --- | --- |
| One point | One place without area geometry | One event marker | Marker selects event and focuses place |
| One area | One place with area geometry | One interactive polygon plus label/focus anchor | Polygon or label selects event and focuses place |
| Multiple points | Several point places | All markers render as one event group | Any marker selects event and focuses that place |
| Multiple areas | Several places with area geometry | Each polygon remains distinct; no forced union | Any polygon selects event and focuses that area place |
| Mixed point/area | Point and area places together | Markers and polygons render concurrently | Clicked location becomes focused while the event remains selected |

When an event is selected, every referenced location uses the selected-event
visual treatment. The focused place receives a stronger, non-color-only cue.
Selecting a different location within the same event changes place focus but not
timeline position, story identity, media, sources, or previous/next navigation.

## Relationship Presentation

Relationship graphics form a separate layer above place geometry and below
labels and selected controls.

| Meaning | Graphic | Text requirement |
| --- | --- | --- |
| Group membership only | Shared event highlight; no connector required | Place list states that all locations belong to the event |
| Undirected edge | Static line or band without arrowheads | Context label explains the supported relationship |
| Forward edge | Static line, band, or arrow with one directional cue | Context label describes movement or circulation without unsupported causal wording |
| Reciprocal edge | Static two-ended or otherwise bidirectional cue | Context label describes exchange in both directions |

Connectors use each place's latitude and longitude as their anchors, including
when an endpoint is an area. The MVP does not calculate paths along streets,
transit lines, coastlines, or polygon boundaries. It also does not animate
movement.

The map should use cautious labels such as “circulates toward,” “exchange
between,” or “connected sites” when supported. It should not convert proximity,
sequence, or visual direction into claims such as “caused,” “invented,” or
“originated.”

## Coordinated Interaction

### Shared State

The target state adds focused place identity without replacing selected event
identity:

```text
selectedRouteId
selectedEventId
selectedPlaceId  optional and constrained to the selected event
```

State rules:

1. Clicking a point, polygon, or relationship endpoint selects its event and
   focuses that place.
2. Clicking another location in the same event changes only
   `selectedPlaceId`.
3. Timeline, related-event, previous/next, or route navigation selects the
   event, preserves an already valid focused place, and otherwise focuses its
   `default_place_id`.
4. Changing events resets stale place focus.
5. The map frames all event locations after event-level navigation. A direct
   map location click may retain the user's zoom while emphasizing the focused
   place.

### Map

- All locations for visible route events render from shared seed/API data.
- Selected-event styling applies to the full spatial footprint; focused-place
  styling is stronger.
- Area precision remains visible. Interpretive boundaries use a distinguishable
  stroke pattern and explanatory text rather than appearing cadastral.
- Multiple polygons remain separate unless the underlying place geometry is a
  sourced `MultiPolygon`.
- Connector styling derives from relationship directionality. Events do not
  store arbitrary graphic instructions.
- Route color remains an accent on outlines and selected states rather than a
  dominant fill over large areas.

### Timeline

- Each event remains one timeline entry regardless of its location count.
- `year_start` and `year_end` continue to control ordering, ticks, and range
  highlighting.
- Selecting a timeline entry selects the event as a whole, preserves a focus
  that belongs to the event, and otherwise initializes focus from
  `default_place_id`.
- Approximate time remains explained in event prose for this MVP; the timeline
  does not invent new temporal precision fields.

### StoryPanel

- The story, significance, sources, media, and event-to-event connections remain
  event-level.
- A compact “Places in this event” list exposes every referenced place in
  editorial order.
- The focused place is announced and visually marked in that list.
- Selecting a place in the list focuses the matching marker or polygon without
  replacing the event story.
- Relationship context labels and accessible direction text appear with the
  relevant places. They are not hidden exclusively in map graphics.

## Accessibility And Mobile

- Every point, area, and relationship visible on the map has a textual
  equivalent in the StoryPanel place list.
- Place controls use place names and event titles rather than visual-shape-only
  labels.
- `aria-current` or an equivalent state identifies the focused place, while the
  event control retains its selected/pressed state.
- Directional graphics include text such as “from South Bronx toward Downtown
  Manhattan”; arrow orientation and color are never the only cues.
- Area precision appears in text, for example “interpretive cultural area” or
  “sourced site boundary.”
- Keyboard users can focus every event place through normal controls without
  operating the Leaflet canvas.
- On mobile, the StoryPanel place list is the reliable location selector. Map
  gestures remain optional, and focusing a place must not unexpectedly replace
  the event or reorder the page.
- Touch targets and selected/focused states follow the existing frontend's
  accessible control sizing and contrast expectations.

## Implemented System Boundary

| Surface | Previous assumption | Implemented behavior |
| --- | --- | --- |
| `data/seed/events.json` | One required `place_id` | Ordered `place_ids`, `default_place_id`, optional place relationships, and a temporary matching `place_id` alias |
| `data/seed/places.json` | Every place is only a latitude/longitude point | Optional area geometry, precision, and conditional external/curated provenance |
| Backend `Event` schema | One `place_id` | Normalizes legacy input and validates collection, default membership, edge endpoints, directionality, labels, and sources |
| Backend `Place` schema | Coordinates only | Types and validates optional Polygon/MultiPolygon geometry and provenance |
| Event connections | `from_event_id` and `to_event_id` relate events | Remain unchanged; place relationships are event-internal spatial presentation, not event-to-event influence |
| Frontend `Event`/`Place` types | Mirrored point-only backend shapes | Match composition, geometry, provenance, and relationship types and normalize legacy static input |
| Shared page state | `selectedPlace` was derived from one event place | Own `selectedPlaceId`, preserve valid focus, and otherwise use the events default |
| `MapView` | One marker per event; contextual areas came from a frontend lookup | Render points, shared areas, relationship layers, and shared-place choice from API/static data |
| `Timeline` | One event equals one timeline entry | Remain event-based; initialize focused place on selection |
| `StoryPanel` | Showed one place in event metadata | Provides accessible event-place focus controls and relationship/precision text |
| Static public data | Mirrored the four point-only seed collections | Carries the same compositional fields as the API with no frontend-only route geometry lookup |
| Enrichment and review | Media/source work keys on event ID | Remain unchanged because `Event` identity remains stable |

## Birth Of Hip-Hop Candidate Presentation Fit

This matrix is a presentation-fit audit of all 23 current candidates in
`event-list.json`. `Status` and `review_state` are copied unchanged. “Likely”
describes what the candidate would need if later approved and sourced; it is not
an editorial decision, geometry approval, historical rewrite, or seed-promotion
instruction.

| Candidate | Status / review | Time shape | Likely spatial footprint | Relationship and coordinated presentation need |
| --- | --- | --- | --- | --- |
| `caribbean-soundsystem-context-nyc` | `maybe` / `pending` | Approximate range | Multiple areas or mixed locations across Bronx and New York contexts | Group locations by default; add directional edges only for source-backed movement. One timeline entry and source-aware relationship text. |
| `bronx-record-and-party-culture-before-1973` | `maybe` / `pending` | Approximate range | One interpretive Bronx area or later mixed examples | No connector without concrete sites. Area selection focuses Bronx context while prose carries uncertainty. |
| `kool-herc-cindy-campbell-sedgwick-party` | `keep` / `pending` | Moment | One point at 1520 Sedgwick Avenue | Standard marker, timeline moment, and one focused place. Public-memory caveats remain prose. |
| `mobile-sound-and-breakbeat-practice` | `keep` / `pending` | Approximate range | Multiple points/areas if specific party sites are sourced; otherwise one interpretive Bronx area | Group sourced examples; explicit edges only for documented equipment/practice circulation. One event story across all locations. |
| `bronx-schools-parks-community-centers-parties` | `keep` / `pending` | Approximate range | Mixed multi-location footprint of point institutions and park/area places | Group membership is central. Optional undirected edges may express a sourced local circuit; every place remains individually focusable. |
| `cedar-park-outdoor-party-culture` | `maybe` / `pending` | Approximate range | One park area, with point fallback until boundary and claims are approved | Interactive area plus focus anchor; no relationship required unless combined with sourced party sites. |
| `grandmaster-flash-turntable-technique` | `keep` / `pending` | Approximate range | One or more sourced Bronx sites; otherwise one interpretive area | Group sites without implying invention at each place. Timeline and story remain event-level. |
| `scratching-and-dj-technique-attribution` | `maybe` / `pending` | Approximate range | Multiple sourced sites or one interpretive Bronx area | Grouped presentation avoids assigning one unsupported invention point; relationship edges require claim-level evidence. |
| `mc-crew-and-party-hosting-practices` | `keep` / `pending` | Approximate range | Multiple party sites and possibly areas | Group locations; use undirected edges only for documented crew/party relationships. Story place list keeps named examples accessible. |
| `dance-crews-and-party-floor-culture` | `maybe` / `pending` | Approximate range | Mixed points/areas across Bronx and wider New York | Group representative sites. Explicit circulation edges only when evidence and route fit are approved. |
| `graffiti-trains-and-visual-culture` | `maybe` / `pending` | Approximate range | Mixed station points, corridor/yard areas, or several distinct areas | Directional or reciprocal edges may describe sourced circulation; the MVP does not draw literal train paths or animate movement. |
| `bronx-river-crews-community-organization` | `maybe` / `pending` | Approximate range | One point or sourced site area at Bronx River Houses | Standard point/area selection; additional locations remain grouped unless sensitive relationship claims pass review. |
| `blackout-1977-context-and-myth` | `maybe` / `pending` | Moment | One citywide interpretive area or several distinct affected/context areas | Multiple areas remain separate. Do not use a connector to imply causal impact on hip-hop; context and myth stay explicit in prose. |
| `bronx-clubs-and-local-performance-circuit` | `maybe` / `pending` | Approximate range | Multiple venue points and possible neighborhood areas | Group venues; use undirected edges for a sourced circuit. Any direction must describe documented circulation, not assumed sequence. |
| `rappers-delight-commercial-visibility` | `keep` / `pending` | Moment | Multiple New York/New Jersey points or areas | A forward edge may express sourced production/distribution circulation. Timeline remains one 1979 event; external geography must preserve route focus. |
| `early-rap-records-and-independent-labels` | `maybe` / `pending` | Range | Multiple label, studio, distribution, or regional places | Group industry nodes; explicit undirected/directional edges require sourced relationships and labels. |
| `radio-djs-and-broadcast-circulation` | `maybe` / `pending` | Approximate range | Mixed station points and one or more broadcast/listening areas | Directional edges or bands may express sourced circulation; broadcast reach cannot be inferred from a station coordinate alone. |
| `the-message-social-commentary` | `maybe` / `pending` | Moment | One or several New York/Bronx context places or areas | Group only source-backed locations. Urban context must not become a visual causal edge to the record. |
| `downtown-clubs-art-and-hip-hop-exchange` | `maybe` / `pending` | Approximate range | Multiple downtown venue points plus possible Bronx places/areas | Reciprocal edges may express sourced exchange; avoid one-way validation framing. Place focus supports inspection of each venue/context. |
| `wild-style-film-documentation` | `keep` / `pending` | Range | Multiple production, performance, or depicted locations if sourced; otherwise one New York context area | Group locations; directional edges only for documented circulation rather than fictional narrative movement. |
| `style-wars-and-television-documentation` | `maybe` / `pending` | Moment | Mixed production/broadcast points and represented areas | Group production and represented places; directional broadcast presentation requires sourced reach/context and accessible text. |
| `beat-street-breakin-and-mainstream-film` | `reject` / `pending` | Moment | Potential mixed production, venue, and circulation locations | Presentation fit only: grouping or directional media circulation could apply if separately reconsidered. Current reject/pending state is unchanged. |
| `international-tours-records-and-media-spread` | `reject` / `pending` | Approximate range | Multiple external points/areas beyond New York | Presentation fit only: directional multi-area circulation would be possible, but it exceeds the current map focus and remains reject/pending. |

## MVP And Later Boundary

### MVP Proposal

- Event composition from point and area places.
- Several distinct areas and mixed point/area footprints.
- Optional explicit undirected, forward, or reciprocal place relationships.
- Static connectors and reviewed context labels.
- Event selection plus focused place selection.
- Timeline and StoryPanel coordination.
- Text-equivalent, keyboard, screen-reader, and mobile access.
- Geometry precision and provenance.
- Backward-compatible interpretation of existing `place_id`.

### Later Only

- Animated flows, route playback, or time-varying geometry.
- Street-, rail-, or transit-path routing.
- Arbitrary overlay artwork or per-event graphic authoring.
- Geometry drawing, editing, simplification, or topology tools.
- Automatic relationship, direction, causality, or geometry inference.
- Generalized `RouteEntry` identity or independent lifecycle.
- Rich temporal precision beyond current year ranges and prose.

## Implementation Boundary

Issue #81 implements the following layers in this order:

1. Shared seed/Pydantic/TypeScript shapes and validation.
2. API and static-data compatibility.
3. Shared selected-event/focused-place state.
4. Map point, area, multi-location, and relationship rendering.
5. Timeline and StoryPanel coordination.
6. Accessibility, mobile, fixtures, and regression tests.

No route candidate should be promoted or rewritten merely to exercise the
model. Deterministic test fixtures can cover every footprint before editorial
data adopts it.

The remaining compatibility boundary is the legacy `place_id` alias. Its
removal is not part of Issue #81 and requires separately approved work.
