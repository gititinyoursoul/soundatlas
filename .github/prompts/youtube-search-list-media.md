# YouTube Search List Media Queries

Use this prompt to generate intent-based YouTube Data API `search.list` requests for SoundAtlas media enrichment.

```text
You are helping curate YouTube media candidates for SoundAtlas, an interactive music history app.
The current MVP scope is New York 1965-1985. Treat all suggestions as editorial drafts,
not verified facts.

Task:
Analyze the SoundAtlas event below and create multiple YouTube Data API v3 search.list
query candidates. Each query candidate should target one specific media intent that
fits the event.

Output file:
Create or update this file in the workspace:

data/enrichment/youtube-search-requests/<event-id>.json

Use the input event `id` as `<event-id>`. Keep the filename lowercase and URL-safe.
Do not modify `data/seed/events.json`.

API target:
GET https://www.googleapis.com/youtube/v3/search

Supported query intents:
- song: concrete songs, recordings, music videos, live clips, or performance-related uploads.
- playlist: YouTube playlists, mixes, or curated song collections that match the event context.
- dj_mix: DJ sets, break mixes, party mixes, turntablism demonstrations, or historically framed mixes.
- documentary: explanatory videos, documentary excerpts, archival context, scene histories, or footage.
- interview: artist, DJ, producer, venue, or oral-history interviews.
- venue_context: videos that explain or document a historically relevant venue, club, block, park, neighborhood, or performance space.
- historical_context: videos that explain or document a named historical event, scene shift, cultural moment, or local context.

Intent selection rules:
- Include only intents that plausibly fit the event.
- If the event has a specific artist, DJ, group, release, label, or track, prefer song and interview when relevant.
- If the event is a broader scene, technique, neighborhood, venue, or context event, prefer documentary and playlist.
- If the event is about DJ practice, sound systems, breaks, parties, clubs, or turntablism, consider dj_mix when a mix could represent the sound-world without claiming to document the exact event.
- If the event is about a specific release, prioritize song and use the release title in the query.
- If the event has a strong place, venue, or neighborhood component, consider venue_context.
- If the event depends on a broader historical moment or named scene shift, consider historical_context.
- If the event has no clear person to interview, omit interview or set confidence_hint to "low".
- Do not force every intent into every event.

Required API behavior per query candidate:
- Use the YouTube Data API v3 search.list endpoint.
- Use part=snippet.
- Use type=video for song, dj_mix, documentary, interview, venue_context, and historical_context.
- Use type=playlist for playlist.
- Use maxResults between 5 and 10.
- Use order=relevance unless there is a clear reason to prefer date or viewCount.
- Use safeSearch=moderate.
- Use relevanceLanguage=en.
- Use regionCode=US.
- Use key=YOUTUBE_API_KEY as a placeholder only.
- URL-encode all query parameters in get_request.
- Do not use videoDuration=short. The MVP should prefer full videos and playlists over Shorts.

Search quality rules:
- Build precise q values from historically meaningful terms.
- Prefer artists, DJs, groups, venues, labels, releases, years, boroughs, route terms, and scene terms.
- Always include the event year or year range in every q value.
- Use words such as interview, documentary, live, performance, footage, playlist, or mix only when they fit the selected intent.
- Avoid repeating the same qualifier, such as interview, across unrelated intents.
- For interview queries, use only the explicit artist, DJ, producer, venue, or group plus the event year or year range plus the word "interview". Do not add extra scene, technique, genre, or context keywords to interview queries.
- Avoid generic queries like "hip hop music" unless the event itself is generic.
- Do not create queries that target Shorts, short-form clips, reaction shorts, teaser clips, or hashtag-based short videos.
- Do not include `shorts`, `short`, `#shorts`, `clip`, or `reaction` as positive search terms unless the historical event explicitly requires that term.
- Do not invent video IDs, playlist IDs, channel IDs, source URLs, or search results.
- Do not include real API keys, secrets, local paths, or credentials.
- Do not mark anything as reviewed.

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
      "places": ["<place or venue>"],
      "works": ["<song, album, film, or release>"],
      "organizations": ["<label, institution, crew, or club>"],
      "techniques": ["<technique or practice>"],
      "historical_events": ["<historical event or scene shift>"]
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

Write only this JSON shape to the output file:
{
  "provider": "youtube",
  "api_method": "search.list",
  "event_id": "<event-id>",
  "editorial_status": "draft",
  "query_candidates": [
    {
      "intent": "song",
      "media_goal": "Find a concrete song, recording, music video, live clip, or performance-related upload.",
      "priority": 1,
      "youtube_type": "video",
      "q": "<plain text query before URL encoding>",
      "get_request": "https://www.googleapis.com/youtube/v3/search?part=snippet&type=video&maxResults=8&order=relevance&safeSearch=moderate&relevanceLanguage=en&regionCode=US&q=<url-encoded-query>&key=YOUTUBE_API_KEY",
      "request_params": {
        "part": "snippet",
        "type": "video",
        "maxResults": 8,
        "order": "relevance",
        "safeSearch": "moderate",
        "relevanceLanguage": "en",
        "regionCode": "US",
        "q": "<plain text query before URL encoding>",
        "key": "YOUTUBE_API_KEY"
      },
      "confidence_hint": "high | medium | low",
      "review_priority": 1,
      "reason": "Why this query fits the event and intent.",
      "review_risks": [
        "Specific checks an editor should perform for this query."
      ]
    },
    {
      "intent": "playlist",
      "media_goal": "Find a YouTube playlist, mix, or curated song collection that matches the event context.",
      "priority": 2,
      "youtube_type": "playlist",
      "q": "<plain text query before URL encoding>",
      "get_request": "https://www.googleapis.com/youtube/v3/search?part=snippet&type=playlist&maxResults=8&order=relevance&safeSearch=moderate&relevanceLanguage=en&regionCode=US&q=<url-encoded-query>&key=YOUTUBE_API_KEY",
      "request_params": {
        "part": "snippet",
        "type": "playlist",
        "maxResults": 8,
        "order": "relevance",
        "safeSearch": "moderate",
        "relevanceLanguage": "en",
        "regionCode": "US",
        "q": "<plain text query before URL encoding>",
        "key": "YOUTUBE_API_KEY"
      },
      "confidence_hint": "high | medium | low",
      "review_priority": 2,
      "reason": "Why this query fits the event and intent.",
      "review_risks": [
        "Specific checks an editor should perform for this query."
      ]
    },
    {
      "intent": "dj_mix",
      "media_goal": "Find a DJ set, break mix, party mix, turntablism demonstration, or historically framed mix.",
      "priority": 2,
      "youtube_type": "video",
      "q": "<plain text query before URL encoding>",
      "get_request": "https://www.googleapis.com/youtube/v3/search?part=snippet&type=video&maxResults=8&order=relevance&safeSearch=moderate&relevanceLanguage=en&regionCode=US&q=<url-encoded-query>&key=YOUTUBE_API_KEY",
      "request_params": {
        "part": "snippet",
        "type": "video",
        "maxResults": 8,
        "order": "relevance",
        "safeSearch": "moderate",
        "relevanceLanguage": "en",
        "regionCode": "US",
        "q": "<plain text query before URL encoding>",
        "key": "YOUTUBE_API_KEY"
      },
      "confidence_hint": "high | medium | low",
      "review_priority": 2,
      "reason": "Why this query fits the event and intent.",
      "review_risks": [
        "Specific checks an editor should perform for this query."
      ]
    },
    {
      "intent": "documentary",
      "media_goal": "Find explanatory video, documentary context, archival footage, or scene history.",
      "priority": 1,
      "youtube_type": "video",
      "q": "<plain text query before URL encoding>",
      "get_request": "https://www.googleapis.com/youtube/v3/search?part=snippet&type=video&maxResults=8&order=relevance&safeSearch=moderate&relevanceLanguage=en&regionCode=US&q=<url-encoded-query>&key=YOUTUBE_API_KEY",
      "request_params": {
        "part": "snippet",
        "type": "video",
        "maxResults": 8,
        "order": "relevance",
        "safeSearch": "moderate",
        "relevanceLanguage": "en",
        "regionCode": "US",
        "q": "<plain text query before URL encoding>",
        "key": "YOUTUBE_API_KEY"
      },
      "confidence_hint": "high | medium | low",
      "review_priority": 1,
      "reason": "Why this query fits the event and intent.",
      "review_risks": [
        "Specific checks an editor should perform for this query."
      ]
    },
    {
      "intent": "interview",
      "media_goal": "Find artist, DJ, producer, venue, or oral-history interview material.",
      "priority": 2,
      "youtube_type": "video",
      "q": "<plain text query before URL encoding>",
      "get_request": "https://www.googleapis.com/youtube/v3/search?part=snippet&type=video&maxResults=8&order=relevance&safeSearch=moderate&relevanceLanguage=en&regionCode=US&q=<url-encoded-query>&key=YOUTUBE_API_KEY",
      "request_params": {
        "part": "snippet",
        "type": "video",
        "maxResults": 8,
        "order": "relevance",
        "safeSearch": "moderate",
        "relevanceLanguage": "en",
        "regionCode": "US",
        "q": "<plain text query before URL encoding>",
        "key": "YOUTUBE_API_KEY"
      },
      "confidence_hint": "high | medium | low",
      "review_priority": 2,
      "reason": "Why this query fits the event and intent.",
      "review_risks": [
        "Specific checks an editor should perform for this query."
      ]
    },
    {
      "intent": "venue_context",
      "media_goal": "Find context about a relevant venue, club, block, park, neighborhood, or performance space.",
      "priority": 2,
      "youtube_type": "video",
      "q": "<plain text query before URL encoding>",
      "get_request": "https://www.googleapis.com/youtube/v3/search?part=snippet&type=video&maxResults=8&order=relevance&safeSearch=moderate&relevanceLanguage=en&regionCode=US&q=<url-encoded-query>&key=YOUTUBE_API_KEY",
      "request_params": {
        "part": "snippet",
        "type": "video",
        "maxResults": 8,
        "order": "relevance",
        "safeSearch": "moderate",
        "relevanceLanguage": "en",
        "regionCode": "US",
        "q": "<plain text query before URL encoding>",
        "key": "YOUTUBE_API_KEY"
      },
      "confidence_hint": "high | medium | low",
      "review_priority": 2,
      "reason": "Why this query fits the event and intent.",
      "review_risks": [
        "Specific checks an editor should perform for this query."
      ]
    },
    {
      "intent": "historical_context",
      "media_goal": "Find context about a named historical event, scene shift, cultural moment, or local history.",
      "priority": 2,
      "youtube_type": "video",
      "q": "<plain text query before URL encoding>",
      "get_request": "https://www.googleapis.com/youtube/v3/search?part=snippet&type=video&maxResults=8&order=relevance&safeSearch=moderate&relevanceLanguage=en&regionCode=US&q=<url-encoded-query>&key=YOUTUBE_API_KEY",
      "request_params": {
        "part": "snippet",
        "type": "video",
        "maxResults": 8,
        "order": "relevance",
        "safeSearch": "moderate",
        "relevanceLanguage": "en",
        "regionCode": "US",
        "q": "<plain text query before URL encoding>",
        "key": "YOUTUBE_API_KEY"
      },
      "confidence_hint": "high | medium | low",
      "review_priority": 2,
      "reason": "Why this query fits the event and intent.",
      "review_risks": [
        "Specific checks an editor should perform for this query."
      ]
    }
  ],
  "omitted_intents": [
    {
      "intent": "interview",
      "reason": "Why this intent was omitted for this event."
    }
  ],
  "review_notes": [
    "Check whether results are historically relevant before adding links.",
    "Reject YouTube Shorts, reaction shorts, teaser clips, and unrelated short-form uploads.",
    "Keep all automatically found links as draft until editorial review.",
    "Verify channel/source quality before promoting any media link to reviewed."
  ]
}

Only include query_candidates whose intents fit the event. If an intent does not fit,
move it to omitted_intents with a short reason. After writing the file, respond with
only the output file path.
```
