# Media Retrieval Query Planning

## Purpose

Query planning is the step between structured event search components and concrete YouTube API requests.

The planner should not call the YouTube API. It should produce reviewable request plans that explain:

- which provider is searched
- which media intent is searched
- why the intent fits the event
- which terms are used
- which false positives are likely
- what type of YouTube result is expected

## Workflow Position

```text
data/seed/events.json
→ data/enrichment/event-search-components/<event-id>.json
→ data/enrichment/youtube-search-requests/<event-id>.json
→ data/enrichment/youtube-search-results/<event-id>.json
→ selected draft media_links in data/seed/events.json
```

Input:

```text
data/enrichment/event-search-components/<event-id>.json
```

Output:

```text
data/enrichment/youtube-search-requests/<event-id>.json
```

Execution:

```powershell
cd backend
uv run python scripts/run_youtube_search_requests.py --event-id <event-id>
```

## Plan Shape

The query plan should stay close to the existing YouTube request-plan files. The important addition is that each candidate should explicitly record its media intent, query type, used terms, and review risks.

```json
{
  "provider": "youtube",
  "api_method": "search.list",
  "event_id": "grandmaster-flash-dj-techniques",
  "source_components": "event-search-components/grandmaster-flash-dj-techniques.json",
  "editorial_status": "draft",
  "query_candidates": [
    {
      "intent": "interview",
      "query_type": "context",
      "media_goal": "Find interview or oral-history material with Grandmaster Flash.",
      "youtube_type": "video",
      "priority": 1,
      "q": "Grandmaster Flash 1975 1977 interview",
      "used_terms": {
        "strong_terms": ["Grandmaster Flash"],
        "supporting_terms": ["1975 1977"],
        "omitted_terms": ["DJ techniques", "music history"]
      },
      "expected_result": "artist, DJ, producer, or oral-history interview",
      "likely_false_positives": [
        "modern fan commentary",
        "short reaction clips",
        "unrelated Grandmaster Flash references"
      ],
      "request_params": {
        "part": "snippet",
        "type": "video",
        "maxResults": 8,
        "order": "relevance",
        "safeSearch": "moderate",
        "relevanceLanguage": "en",
        "regionCode": "US",
        "q": "Grandmaster Flash 1975 1977 interview",
        "key": "YOUTUBE_API_KEY"
      },
      "confidence_hint": "high",
      "review_priority": 1,
      "reason": "Grandmaster Flash is a strong artist term and the event focuses on his technique development.",
      "review_risks": [
        "Verify that the interview discusses early DJ techniques or the relevant period.",
        "Reject reaction, tutorial, or unrelated documentary recap videos."
      ]
    }
  ],
  "omitted_intents": [
    {
      "intent": "official_track",
      "reason": "The event does not name a specific recording."
    }
  ],
  "review_notes": [
    "Keep all search results as draft.",
    "Review channel/source quality before promoting links."
  ]
}
```

## Query Types

Use a small set of query types:

- `precise`: targets a named artist, work, organization, place, or historical event.
- `context`: targets interviews, documentaries, scene history, or venue context.
- `discovery`: broad exploration such as playlists, DJ mixes, or scene overviews.

Default storage rule:

- `precise` and strong `context` queries can produce candidates for `media_links`.
- `discovery` queries should remain lower priority and require stricter review.

## Intent Selection

The planner should derive intents from `docs/media-retrieval-event-search-components.md`.

| Component | Eligible YouTube Intents | Default Priority |
| --- | --- | --- |
| `entities.artists` | `interview`, `artist_profile`, `live_performance`, `documentary` | 1 |
| `entities.places` | `venue_context`, `documentary`, `historical_context` | 1-2 |
| `entities.works` | `official_track`, `official_music_video`, `documentary`, `playlist_of_songs` | 1 |
| `entities.organizations` | `label_context`, `documentary`, `playlist_of_songs` | 2 |
| `entities.techniques` | `documentary`, `interview`, `dj_mix` | 1-2 |
| `entities.historical_events` | `historical_context`, `documentary` | 1 |
| `context.genres/scenes/practices` | `playlist_of_songs`, `documentary`, `dj_mix` | 2-3 |

Do not force every intent onto every event. Empty or weak components should lead to omitted intents.

## Supported YouTube Intents

- `official_track`
- `official_music_video`
- `live_performance`
- `interview`
- `documentary`
- `playlist_of_songs`
- `dj_mix`
- `artist_profile`
- `venue_context`
- `historical_context`
- `label_context`
- `album_or_film_context`

## Term Selection Rules

Use `search_control` explicitly:

- `strong_terms`: should anchor precise queries.
- `supporting_terms`: should enrich queries but not dominate them.
- `risky_terms`: should create `review_risks`.
- `avoid_terms`: should not be added to the query; use them later for result warnings or rejection.

Year handling:

- Include `time_context.query_year_phrase` when it improves specificity.
- Do not treat a year match as proof of relevance.
- For broad documentaries or playlists, a year range may be useful.
- For interviews, keep the query concise: artist plus year phrase plus `interview`.

## Example Mapping

Input component summary:

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
  "time_context": {
    "query_year_phrase": "1979"
  }
}
```

Recommended planned intents:

- Priority 1: `official_track`
- Priority 1: `official_music_video`
- Priority 2: `interview`
- Priority 2: `label_context`
- Omit: `venue_context`
- Omit: `historical_context`

Example queries:

- `The Sugarhill Gang Rapper's Delight 1979`
- `Rapper's Delight official video 1979`
- `The Sugarhill Gang 1979 interview`
- `Sugar Hill Records Rapper's Delight documentary`

## Non-Goals

- Query planning does not execute API requests.
- Query planning does not store final `media_links`.
- Query planning does not mark results as `reviewed`.
- Query planning does not decide final relevance.
- Query planning should not invent facts that are not present in the event components.
