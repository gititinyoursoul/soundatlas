# Media Enrichment Concept

## Goal

SoundAtlas should enrich events with external music, video, and playlist links. These links help users understand an event not only historically, but also through sound and culture.

The MVP does not store audio or video files. It stores only external URLs and metadata.

## Scope

Media enrichment currently focuses on:

- YouTube for videos, performances, interviews, documentary excerpts, and search matches.
- Spotify for tracks, albums, and playlists.
- Qobuz for tracks and albums with a more curated music focus.

These links are meant as exploration aids, not as a complete editorial discography.

## Data Model

Events use the `media_links` field. Each entry is a structured object.

```json
{
  "provider": "youtube",
  "type": "video",
  "title": "Grandmaster Flash DJ set",
  "url": "https://www.youtube.com/watch?v=example",
  "query": "Grandmaster Flash Bronx hip hop 1977",
  "confidence": 0.78,
  "review_status": "draft"
}
```

### Required Fields

- `provider`
- `type`
- `title`
- `url`
- `query`
- `confidence`
- `review_status`

### Providers

- `youtube`
- `spotify`
- `qobuz`

### Types

- `track`
- `album`
- `playlist`
- `video`
- `search`

## Review Status

All automatically generated links are stored with `review_status: "draft"`.

- `draft`: generated automatically or not yet reviewed editorially.
- `reviewed`: editorially reviewed and suitable for the normal user experience.

The review status is the primary safety boundary. Automation may write links, but it may not mark them as reviewed.

## Matching Rules

Queries are built from existing event data:

- `event.title`
- `route.title`
- `year_start` and `year_end`
- event tags
- known artist, venue, label, or release terms

Examples:

- `Grandmaster Flash Bronx hip hop 1977`
- `CBGB punk new wave New York 1975`
- `Paradise Garage Larry Levan disco 1979`
- `Fania All-Stars salsa New York 1973`

## Confidence

`confidence` is a value between `0` and `1`.

High confidence:

- exact or close match with artist, release, venue, or event title
- appropriate historical timeframe
- provider result has a clear title and stable URL
- media type fits the event context

Medium confidence:

- scene or route match is plausible, but not exact
- playlist is thematically relevant, but not clearly tied to the specific event

Low confidence:

- only generic genre or city wording
- unclear artist or release match
- result feels modern or historically mismatched

## Provider Strategy

### YouTube

Useful for:

- historical videos
- interviews
- TV appearances
- concert footage
- documentary excerpts
- search links when no clearly reliable single video is available

Risks:

- uploads may disappear
- rights status and channel quality vary
- a high number of results requires review

### Spotify

Useful for:

- tracks
- albums
- curated or algorithmic playlists

Risks:

- availability varies by country
- playlists may change over time
- historical scenes are often represented only indirectly

### Qobuz

Useful for:

- albums
- tracks
- more editorially stable catalog entries

Risks:

- API and auth behavior may vary by account setup
- catalog coverage is not equally strong across all genres

## Automation

The current script is located at:

```powershell
backend/scripts/enrich_media_links.py
```

Run:

```powershell
cd backend
uv run python scripts/enrich_media_links.py
```

Dry run:

```powershell
cd backend
uv run python scripts/enrich_media_links.py --dry-run
```

Single event:

```powershell
cd backend
uv run python scripts/enrich_media_links.py --event-id grandmaster-flash
```

The script:

1. reads `data/seed/events.json`
2. reads `data/seed/routes.json`
3. builds a content-page-like input from event and route data
4. analyzes that content into keywords, genres, and provider-agnostic search queries
5. uses those queries across configured provider APIs
6. applies provider-specific normalization and ranking
7. deduplicates links by URL
8. writes new links with `review_status: "draft"`

## Environment Variables

Example values are documented in `.env.example`. For local Codex and test runs, `.env.codex` is also included in the repository with dummy values only.

```powershell
SOUNDATLAS_USE_DUMMY_SERVICES=false
SOUNDATLAS_OPENAI_MODEL=gpt-4.1-mini
YOUTUBE_API_KEY=
SOUNDATLAS_OPENAI_API_KEY=
SPOTIFY_CLIENT_ID=
SPOTIFY_CLIENT_SECRET=
QOBUZ_APP_ID=
QOBUZ_USER_AUTH_TOKEN=
```

Real secrets must not live in the repository. Instead, an external file path is provided through `SOUNDATLAS_ENV_FILE`, for example `C:\Users\Marius\secrets\soundatlas\.env`.

Providers without live credentials are skipped. In dummy or test mode, mocks may be used without making real network requests.

## Secure Multi-Provider Recommendation Pipeline

For content-page-based media recommendations, the following rules apply:

1. Content text is analyzed and converted into topic, mood, keywords, genres, and search queries.
2. The resulting search queries are reused across YouTube, Spotify, and Qobuz, instead of maintaining a separate content understanding step per provider.
3. Only content text, generated search queries, and normalized media metadata are passed to GPT or other LLM components, never provider secrets.
4. The YouTube API key is used only inside the YouTube search service. Spotify and Qobuz credentials stay inside their respective provider services.
5. Search results are normalized into the shared `media_links` structure, with provider-specific metadata where available.
6. Ranking can be heuristic or optionally handled through a mockable GPT or OpenAI-compatible interface.

### Provider Behavior

- `YouTube`: uses the shared content analysis, searches across multiple generated queries, normalizes richer video metadata, and applies explicit ranking with reasons.
- `Spotify`: uses the same analyzed query set, searches tracks, albums, and playlists, and keeps only the strongest normalized candidates.
- `Qobuz`: uses the same analyzed query set, searches tracks, albums, and playlists, and keeps only the strongest normalized candidates.

## UX Concept

The story panel displays media links with provider-aware labeling:

- `YouTube video`
- `Spotify track`
- `Spotify playlist`
- `Qobuz album`

In the normal user-facing experience, only `reviewed` links should eventually appear prominently. `draft` links may remain visible in internal review views.

## Non-Goals

- no audio or video downloads
- no local media caches
- no provider scrapers
- no automatic editorial approval
- no guarantee that external links remain available permanently

## Implementation Status

Already implemented:

- structured `media_links` schema in the backend
- TypeScript types for `media_links`
- story panel labels by provider and media type
- provider-agnostic content analysis pipeline for YouTube, Spotify, and Qobuz
- tests for the media link schema
- seed validation documentation

Still useful:

- define a review workflow from `draft` to `reviewed`
- evaluate frontend filtering for unreviewed media links
- improve logging and reporting for enrichment runs
- make source quality measurable per provider
