# Media Retrieval Event Search Components

## Purpose

This document defines a stable conceptual schema for deriving YouTube search input from SoundAtlas events.

The schema is intentionally separate from `data/seed/events.json`. Core event data should remain editorial product content, while retrieval metadata can evolve as the media pipeline improves.

## Placement

Use this document as the schema reference first:

```text
docs/media-retrieval-event-search-components.md
```

Once the structure is stable, generated or curated component files can live under:

```text
data/enrichment/event-search-components/<event-id>.json
```

If validation becomes necessary, add a machine-readable schema later:

```text
data/enrichment/schemas/event-search-components.schema.json
```

## Workflow Position

```text
data/seed/events.json
→ data/enrichment/event-search-components/<event-id>.json
→ data/enrichment/youtube-search-requests/<event-id>.json
→ data/enrichment/youtube-search-results/<event-id>.json
→ selected draft media_links in data/seed/events.json
```

Only selected media links are merged back into `events.json`. Intermediate search components, request plans, and search results stay in `data/enrichment/`.

## Stable Schema

The object shape should stay stable across events. Individual arrays may be empty when a category does not apply.

```json
{
  "event_id": "grandmaster-flash-dj-techniques",
  "event_type": "technique_development",
  "primary_entities": {
    "artists": ["Grandmaster Flash"],
    "groups": [],
    "labels": [],
    "tracks": [],
    "albums": [],
    "films": [],
    "techniques": ["backspin", "punch phrasing", "precise mixing"],
    "historical_events": []
  },
  "geo_entities": {
    "cities": ["New York"],
    "boroughs": ["Bronx"],
    "neighborhoods": ["South Bronx"],
    "venues": [],
    "addresses": []
  },
  "associated_entities": {
    "genres": ["hip hop"],
    "scenes": ["Bronx hip-hop"],
    "communities": [],
    "practices": ["DJing", "turntablism", "breakbeat practice"],
    "industry_terms": [],
    "route_terms": ["Birth of Hip-Hop"]
  },
  "time_context": {
    "year_start": 1975,
    "year_end": 1977,
    "query_year_phrase": "1975 1977"
  },
  "search_reliability": {
    "high_confidence_terms": ["Grandmaster Flash", "turntablism"],
    "context_terms": ["South Bronx", "hip hop", "Birth of Hip-Hop"],
    "risky_terms": ["DJ techniques", "music history"],
    "avoid_terms": ["reaction", "tutorial", "karaoke", "cover", "AI cover"]
  },
  "review_notes": [
    "Prefer interview and documentary intents over generic technique videos.",
    "Check whether technique demonstrations are historically related to Grandmaster Flash."
  ]
}
```

## Event Types

Recommended initial values:

- `scene_context`
- `technique_development`
- `symbolic_event`
- `scene_organization`
- `historical_context`
- `release`
- `venue_crossover`

These values are retrieval hints, not user-facing taxonomy.

## Entity Semantics

### `primary_entities`

Use for terms that should drive high-priority queries:

- `artists`: individual artists, DJs, producers, organizers.
- `groups`: bands, crews, collectives, ensembles.
- `labels`: labels or industry organizations.
- `tracks`: specific songs or recordings.
- `albums`: specific albums or releases.
- `films`: specific films or documentaries.
- `techniques`: musical, DJ, production, or performance techniques.
- `historical_events`: named non-musical events relevant to the event context.

### `geo_entities`

Use for place information with different search weights:

- `cities`: broad city context, for example `New York`.
- `boroughs`: stronger than city context, for example `Bronx`.
- `neighborhoods`: stronger again, for example `South Bronx`.
- `venues`: specific clubs, parks, community rooms, studios, or cultural spaces.
- `addresses`: exact addresses when historically meaningful.

This separation matters because `New York` is broad, while `1520 Sedgwick Avenue` is a precise search anchor.

### `associated_entities`

Use for secondary context:

- `genres`: music genres.
- `scenes`: named scenes or cultural formations.
- `communities`: social, migrant, ethnic, youth, or neighborhood communities.
- `practices`: scene practices such as block parties, DJing, MCing, b-boying.
- `industry_terms`: charts, records, labels, mainstream, media, distribution.
- `route_terms`: terms inherited from the route.

### `time_context`

Use event years as query context, not proof of relevance.

- Single year: `query_year_phrase` should be `"1973"`.
- Range: `query_year_phrase` should be `"1975 1977"`.

### `search_reliability`

Use to make query planning safer:

- `high_confidence_terms`: precise terms likely to identify relevant material.
- `context_terms`: useful context, but not enough for exact matching.
- `risky_terms`: broad or ambiguous terms that may create false positives.
- `avoid_terms`: terms that often indicate poor YouTube results.

## Examples From First Ten Events

### Scene Context

```json
{
  "event_id": "caribbean-soundsystem-influences",
  "event_type": "scene_context",
  "primary_entities": {
    "artists": [],
    "groups": [],
    "labels": [],
    "tracks": [],
    "albums": [],
    "films": [],
    "techniques": [],
    "historical_events": []
  },
  "geo_entities": {
    "cities": ["New York"],
    "boroughs": ["Bronx"],
    "neighborhoods": ["South Bronx"],
    "venues": [],
    "addresses": []
  },
  "associated_entities": {
    "genres": ["hip hop"],
    "scenes": ["Caribbean sound system culture", "early Bronx hip-hop"],
    "communities": ["Caribbean", "African American", "Latino"],
    "practices": ["sound systems", "neighborhood parties", "DJ culture"],
    "industry_terms": [],
    "route_terms": ["Birth of Hip-Hop"]
  }
}
```

### Symbolic Event

```json
{
  "event_id": "kool-herc-back-to-school-jam",
  "event_type": "symbolic_event",
  "primary_entities": {
    "artists": ["DJ Kool Herc"],
    "groups": [],
    "labels": [],
    "tracks": [],
    "albums": [],
    "films": [],
    "techniques": [],
    "historical_events": []
  },
  "geo_entities": {
    "cities": ["New York"],
    "boroughs": ["Bronx"],
    "neighborhoods": [],
    "venues": ["1520 Sedgwick Avenue community room"],
    "addresses": ["1520 Sedgwick Avenue"]
  },
  "associated_entities": {
    "genres": ["hip hop"],
    "scenes": ["early Bronx hip-hop"],
    "communities": ["youth culture"],
    "practices": ["block party", "DJing"],
    "industry_terms": [],
    "route_terms": ["Birth of Hip-Hop"]
  }
}
```

### Release

```json
{
  "event_id": "rappers-delight-mainstream-breakthrough",
  "event_type": "release",
  "primary_entities": {
    "artists": [],
    "groups": ["The Sugarhill Gang"],
    "labels": ["Sugar Hill Records"],
    "tracks": ["Rapper's Delight"],
    "albums": [],
    "films": [],
    "techniques": [],
    "historical_events": []
  },
  "geo_entities": {
    "cities": ["New York", "Englewood"],
    "boroughs": [],
    "neighborhoods": [],
    "venues": [],
    "addresses": []
  },
  "associated_entities": {
    "genres": ["rap", "hip hop"],
    "scenes": ["mainstream rap"],
    "communities": [],
    "practices": ["recording", "radio circulation"],
    "industry_terms": ["charts", "records", "industry", "mainstream"],
    "route_terms": ["Birth of Hip-Hop"]
  }
}
```

### Historical Context

```json
{
  "event_id": "nyc-blackout-1977",
  "event_type": "historical_context",
  "primary_entities": {
    "artists": [],
    "groups": [],
    "labels": [],
    "tracks": [],
    "albums": [],
    "films": [],
    "techniques": [],
    "historical_events": ["1977 New York City blackout"]
  },
  "geo_entities": {
    "cities": ["New York"],
    "boroughs": [],
    "neighborhoods": [],
    "venues": [],
    "addresses": []
  },
  "associated_entities": {
    "genres": [],
    "scenes": ["urban crisis context"],
    "communities": [],
    "practices": [],
    "industry_terms": [],
    "route_terms": ["Birth of Hip-Hop"]
  }
}
```

## Query Planning Implications

- Artist or group present: consider `interview`, `documentary`, `live`, or `official_video`.
- Track present: consider `song_or_track`, `official_video`, `live`, or `playlist`.
- Venue or address present: consider `documentary`, `footage`, or `venue_context`.
- Technique present: consider `documentary`, `interview`, or `demonstration`, but watch for tutorials.
- Historical event present: consider `documentary` or archival context, not song search.
- Only broad city context present: use it as a secondary term, not the query anchor.

## Non-Goals

- This schema does not replace `events.json`.
- This schema does not mark links as reviewed.
- This schema does not store API results.
- This schema does not decide final relevance; it prepares better search plans.
