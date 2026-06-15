# YouTube MVP Retrieval Workflow

## Goal

The MVP should improve YouTube media suggestions without overbuilding the retrieval system.

The goal is not automatic correctness. The goal is to produce useful YouTube candidates for editorial review.

## Simplified Pipeline

```text
event
→ event search components
→ YouTube query plan
→ YouTube search results
→ draft media_links
→ manual review
```

## Keep For MVP

- `event-search-components` as a small structured retrieval layer.
- YouTube-only query plans under `data/enrichment/youtube-search-requests/`.
- YouTube search results under `data/enrichment/youtube-search-results/`.
- `review_status: "draft"` for all generated media links.
- Manual promotion to `review_status: "reviewed"`.
- URL-based deduplication.

## Minimal Event Search Components

Use the simplified schema from `docs/media-retrieval/event-search-components.md`.

For MVP query planning, the most important fields are:

- `entities.artists`
- `entities.places`
- `entities.works`
- `entities.organizations`
- `entities.techniques`
- `entities.historical_events`
- `context.genres`
- `context.scenes`
- `context.practices`
- `time_context.query_year_phrase`
- `search_control.strong_terms`
- `search_control.supporting_terms`
- `search_control.avoid_terms`

## Minimal YouTube Intents

Use only these intents for now:

- `song`
- `interview`
- `documentary`
- `playlist`
- `dj_mix`
- `venue_context`
- `historical_context`

## Intent Rules

- `entities.works` present: prefer `song`.
- `entities.artists` present: prefer `interview` and `documentary`.
- `entities.places` present: prefer `venue_context` and `documentary`.
- `entities.techniques` present: prefer `documentary` or `dj_mix`; avoid generic tutorials.
- `entities.historical_events` present: prefer `historical_context` and `documentary`.
- `context.genres`, `context.scenes`, or `context.practices` present: consider `playlist`, `documentary`, or `dj_mix`.

Do not force every intent into every event.

## Minimal Query Plan Shape

```json
{
  "provider": "youtube",
  "api_method": "search.list",
  "event_id": "kool-herc-back-to-school-jam",
  "editorial_status": "draft",
  "query_candidates": [
    {
      "intent": "documentary",
      "priority": 1,
      "youtube_type": "video",
      "q": "DJ Kool Herc 1520 Sedgwick Avenue 1973 documentary",
      "request_params": {
        "part": "snippet",
        "type": "video",
        "maxResults": 8,
        "order": "relevance",
        "safeSearch": "moderate",
        "relevanceLanguage": "en",
        "regionCode": "US",
        "q": "DJ Kool Herc 1520 Sedgwick Avenue 1973 documentary",
        "key": "YOUTUBE_API_KEY"
      },
      "review_priority": 1,
      "confidence_hint": "high",
      "reason": "The event has a named artist, place, and year that are useful for documentary context.",
      "review_risks": [
        "Check historical relevance.",
        "Reject reaction, recap, or generic explainer videos."
      ]
    }
  ],
  "omitted_intents": [
    {
      "intent": "song",
      "reason": "The event does not name a specific recording."
    }
  ]
}
```

## Script Responsibilities

### `run_youtube_search_requests.py`

- Reads YouTube query plans.
- Injects the real YouTube API key at runtime.
- Calls YouTube `search.list`.
- Writes normalized draft results.
- Redacts secrets from result files.

### `enrich_media_links.py`

- Reads normalized YouTube result files.
- Extracts video and playlist candidates.
- Deduplicates by URL.
- Merges candidates into `data/seed/events.json`.
- Keeps all generated links as `review_status: "draft"`.

## Review Rule

Generated links are candidates, not accepted content.

An editor should check:

- Is the result historically relevant?
- Does the title match the intended artist, work, place, or context?
- Is the channel/source acceptable?
- Is it a reaction, cover, recap, tutorial, or unrelated modern video?
- Should it remain `draft`, be promoted to `reviewed`, or be removed?

## Success Criteria

The MVP workflow is good enough when:

- query plans are understandable without reading code
- bad queries can be fixed manually
- YouTube results remain auditable
- generated links never bypass review
- seed data stays clean and human-readable

## Guiding Principle

Do not build an automatic media truth engine.

Build a controlled YouTube candidate pipeline that helps editorial review move faster.
