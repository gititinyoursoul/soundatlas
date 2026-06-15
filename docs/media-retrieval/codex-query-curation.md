# Codex Query Curation

## Purpose

Use Codex as an editorial helper for creating YouTube query plans.

Codex should not invent media links, video IDs, playlist IDs, source URLs, or API results. It only helps turn event metadata and event search components into reviewable YouTube request plans.

## Recommended Workflow

1. Pick an event from `data/seed/events.json`.
2. Derive or review event search components with `docs/media-retrieval/event-search-components.md`.
3. Ask Codex to create a YouTube request plan using `.github/prompts/youtube-search-list-media.md`.
4. Save the reviewed plan under `data/enrichment/youtube-search-requests/<event-id>.json`.
5. Validate the plan with:

```powershell
cd backend
uv run python scripts/run_youtube_search_requests.py --event-id <event-id> --dry-run
```

6. Run the live YouTube request only after the plan looks correct.
7. Merge results with `enrich_media_links.py --dry-run` before writing seed changes.

## Prompt Template

```text
You are helping curate media links for SoundAtlas, an interactive music history app.
The current MVP scope is New York 1965-1985. Treat all suggestions as editorial
drafts, not verified facts.

Task:
Analyze the SoundAtlas event below and propose a YouTube search request plan.
Focus on historically plausible videos or playlists that could help users
understand the event through scene context, interviews, performances,
documentary clips, artists, venues, years, labels, and related cultural terms.

Safety and quality rules:
- Do not invent media links, source URLs, video IDs, playlist IDs, or API results.
- Do not mark anything as reviewed.
- Do not include API keys, local paths, or secrets.
- Prefer precise historical queries over generic genre queries.
- Include the year or year range when it improves the query.
- Use only the MVP YouTube intents:
  song, interview, documentary, playlist, dj_mix, venue_context, historical_context.
- If a query is speculative, set confidence_hint to "low".
- Return only JSON. Do not add prose outside the JSON.

Input event:
{
  "id": "<event-id>",
  "route_title": "<route title>",
  "title": "<event title>",
  "year_start": <year>,
  "year_end": <year>,
  "summary": "<event summary>",
  "significance": "<why this matters>",
  "tags": ["<tag>", "<tag>"],
  "event_search_components": {
    "entities": {
      "artists": ["<artist>"],
      "places": ["<place>"],
      "works": ["<song or release>"],
      "organizations": ["<label or institution>"],
      "techniques": ["<technique>"],
      "historical_events": ["<historical event>"]
    },
    "context": {
      "genres": ["<genre>"],
      "scenes": ["<scene>"],
      "practices": ["<practice>"]
    },
    "time_context": {
      "query_year_phrase": "<year or year range>"
    },
    "search_control": {
      "strong_terms": ["<must-use term>"],
      "supporting_terms": ["<useful term>"],
      "avoid_terms": ["<term to avoid>"]
    }
  }
}

Return this JSON shape:
{
  "provider": "youtube",
  "api_method": "search.list",
  "event_id": "<event-id>",
  "editorial_status": "draft",
  "query_candidates": [
    {
      "intent": "documentary",
      "priority": 1,
      "youtube_type": "video",
      "q": "search query",
      "request_params": {
        "part": "snippet",
        "type": "video",
        "maxResults": 8,
        "order": "relevance",
        "safeSearch": "moderate",
        "relevanceLanguage": "en",
        "regionCode": "US",
        "q": "search query",
        "key": "YOUTUBE_API_KEY"
      },
      "review_priority": 1,
      "confidence_hint": "high",
      "reason": "why this query fits the event",
      "review_risks": [
        "specific risks or checks an editor should perform"
      ]
    }
  ],
  "omitted_intents": [
    {
      "intent": "song",
      "reason": "why this intent was not useful for this event"
    }
  ]
}
```

## Review Rule

All Codex output remains draft material. Only promote generated `media_links` to `reviewed` after manual source and relevance checks.
