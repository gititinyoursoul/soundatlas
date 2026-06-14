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
- song_or_track: concrete songs, recordings, music videos, live clips, or performance-related uploads.
- playlist_of_songs: YouTube playlists, mixes, or curated song collections that match the event context.
- dj_mix: DJ sets, break mixes, party mixes, turntablism demonstrations, or historically framed mixes.
- documentary: explanatory videos, documentary excerpts, archival context, scene histories, or footage.
- interview: artist, DJ, producer, venue, or oral-history interviews.

Intent selection rules:
- Include only intents that plausibly fit the event.
- If the event has a specific artist, DJ, group, release, label, or track, prefer song_or_track and interview when relevant.
- If the event is a broader scene, technique, neighborhood, venue, or context event, prefer documentary and playlist_of_songs.
- If the event is about DJ practice, sound systems, breaks, parties, clubs, or turntablism, consider dj_mix when a mix could represent the sound-world without claiming to document the exact event.
- If the event is about a specific release, prioritize song_or_track and use the release title in the query.
- If the event has no clear person to interview, omit interview or set confidence_hint to "low".
- Do not force every intent into every event.

Required API behavior per query candidate:
- Use the YouTube Data API v3 search.list endpoint.
- Use part=snippet.
- Use type=video for song_or_track, dj_mix, documentary, and interview.
- Use type=playlist for playlist_of_songs.
- Use maxResults between 5 and 10.
- Use order=relevance unless there is a clear reason to prefer date or viewCount.
- Use safeSearch=moderate.
- Use relevanceLanguage=en.
- Use regionCode=US.
- Use key=YOUTUBE_API_KEY as a placeholder only.
- URL-encode all query parameters in get_request.

Search quality rules:
- Build precise q values from historically meaningful terms.
- Prefer artists, DJs, groups, venues, labels, releases, years, boroughs, route terms, and scene terms.
- Always include the event year or year range in every q value.
- Use words such as interview, documentary, live, performance, footage, playlist, or mix only when they fit the selected intent.
- Avoid repeating the same qualifier, such as interview, across unrelated intents.
- For interview queries, use only the explicit artist, DJ, producer, venue, or group plus the event year or year range plus the word "interview". Do not add extra scene, technique, genre, or context keywords to interview queries.
- Avoid generic queries like "hip hop music" unless the event itself is generic.
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
  "known_terms": ["<artist>", "<venue>", "<label>", "<release>"]
}

Write only this JSON shape to the output file:
{
  "provider": "youtube",
  "api_method": "search.list",
  "event_id": "<event-id>",
  "editorial_status": "draft",
  "query_candidates": [
    {
      "intent": "song_or_track",
      "media_goal": "Find a concrete song, recording, music video, live clip, or performance-related upload.",
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
      "intent": "playlist_of_songs",
      "media_goal": "Find a YouTube playlist, mix, or curated song collection that matches the event context.",
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
    "Keep all automatically found links as draft until editorial review.",
    "Verify channel/source quality before promoting any media link to reviewed."
  ]
}

Only include query_candidates whose intents fit the event. If an intent does not fit,
move it to omitted_intents with a short reason. After writing the file, respond with
only the output file path.
```
