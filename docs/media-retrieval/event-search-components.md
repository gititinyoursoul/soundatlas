# Media Retrieval Event Search Components

## Purpose

This document defines a simple, stable schema for deriving YouTube search input from SoundAtlas events.

The schema is intentionally separate from `data/seed/events.json`. Core event data should remain editorial product content, while retrieval metadata can evolve as the media pipeline improves.

## Placement

Use this document as the schema reference first:

```text
docs/media-retrieval/event-search-components.md
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

The next conceptual step is query planning, documented in `docs/media-retrieval/query-planning.md`.

## Stable Schema

The object shape should stay stable across events. Individual arrays may be empty when a category does not apply.

```json
{
  "event_id": "grandmaster-flash-dj-techniques",
  "event_type": "technique_development",
  "entities": {
    "artists": ["Grandmaster Flash"],
    "places": ["South Bronx", "Bronx", "New York"],
    "works": [],
    "organizations": [],
    "techniques": ["backspin", "punch phrasing", "precise mixing"],
    "historical_events": []
  },
  "context": {
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
  "search_control": {
    "strong_terms": ["Grandmaster Flash", "turntablism"],
    "supporting_terms": ["South Bronx", "hip hop", "Birth of Hip-Hop"],
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

### `entities`

Use for concrete terms that can anchor YouTube queries:

- `artists`: individual artists, DJs, producers, organizers, bands, groups, crews, collectives, or ensembles.
- `places`: cities, boroughs, neighborhoods, venues, parks, clubs, studios, community rooms, or exact addresses.
- `works`: tracks, albums, releases, films, documentaries, or other named works.
- `organizations`: labels, institutions, crews, collectives, venues-as-organizations, media outlets, or industry entities.
- `techniques`: musical, DJ, production, or performance techniques.
- `historical_events`: named non-musical events relevant to the event context.

This intentionally avoids over-modeling early. For YouTube search, `DJ Kool Herc` and `The Sugarhill Gang` often trigger similar intents, so both belong in `artists`. Likewise, `New York`, `Bronx`, and `1520 Sedgwick Avenue` can all be handled as `places`; query planning can still choose which terms are strong or supporting.

### `context`

Use for secondary terms that describe why an event matters:

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

### `search_control`

Use to make query planning safer:

- `strong_terms`: precise terms likely to identify relevant material.
- `supporting_terms`: useful context, but not enough for exact matching.
- `risky_terms`: broad or ambiguous terms that may create false positives.
- `avoid_terms`: terms that often indicate poor YouTube results.

## Examples From First Ten Events

### Scene Context

```json
{
  "event_id": "caribbean-soundsystem-influences",
  "event_type": "scene_context",
  "entities": {
    "artists": [],
    "places": ["South Bronx", "Bronx", "New York"],
    "works": [],
    "organizations": [],
    "techniques": [],
    "historical_events": []
  },
  "context": {
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
  "entities": {
    "artists": ["DJ Kool Herc"],
    "places": ["1520 Sedgwick Avenue", "1520 Sedgwick Avenue community room", "Bronx", "New York"],
    "works": [],
    "organizations": [],
    "techniques": [],
    "historical_events": []
  },
  "context": {
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
  "entities": {
    "artists": ["The Sugarhill Gang"],
    "places": ["New York", "Englewood"],
    "works": ["Rapper's Delight"],
    "organizations": ["Sugar Hill Records"],
    "techniques": [],
    "historical_events": []
  },
  "context": {
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
  "entities": {
    "artists": [],
    "places": ["New York"],
    "works": [],
    "organizations": [],
    "techniques": [],
    "historical_events": ["1977 New York City blackout"]
  },
  "context": {
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

- `artists` present: consider `interview`, `documentary`, `artist_profile`, `live_performance`, or `official_music_video`.
- `places` present: consider `venue_context`, `documentary`, `historical_context`, or archival footage.
- `works` present: consider `official_track`, `official_music_video`, `album_or_film_context`, or `playlist_of_songs`.
- `organizations` present: consider `documentary`, `label_context`, `scene_context`, or `playlist_of_songs`.
- `techniques` present: consider `documentary`, `interview`, `dj_mix`, or demonstration-style queries, but watch for tutorials.
- `historical_events` present: consider `historical_context` or `documentary`, not song search.
- `context.genres`, `context.scenes`, and `context.practices` present: consider `playlist_of_songs`, `documentary`, or `dj_mix`.
- `search_control.strong_terms` should anchor precise queries.
- `search_control.supporting_terms` should enrich queries but not dominate them.
- `search_control.risky_terms` should create review warnings.
- `search_control.avoid_terms` should create negative-result checks.

## Non-Goals

- This schema does not replace `events.json`.
- This schema does not mark links as reviewed.
- This schema does not store API results.
- This schema does not decide final relevance; it prepares better search plans.
