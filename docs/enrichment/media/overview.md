# Media Enrichment Overview

## Goal

SoundAtlas should enrich events with external music, video, and playlist links. These links help users understand an event not only historically, but also through sound and culture.

The MVP does not store audio or video files. It stores only external URLs and metadata.

## Scope

Media enrichment currently uses a YouTube-only MVP workflow:

- YouTube for videos, performances, interviews, documentary excerpts, playlists, and search matches.

These links are meant as exploration aids, not as a complete editorial discography.

The shared enrichment workflow is documented in `docs/enrichment/workflow.md`.
Image enrichment follows the same shared pipeline, but writes to `image_links`
instead of `media_links`. The image-specific branch is documented in
`docs/enrichment/image/overview.md`.

Media enrichment should start only after an event has been accepted for the
route. When route-folder editorial artifacts are available, use
`docs/content/routes/<route-id>/accepted-events.md` as the human-reviewed
handoff before planning YouTube requests. Do not plan media enrichment for
unresolved `maybe`, unresolved `merge`, or `reject` candidates.

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

### Types

- `playlist`
- `video`
- `search`

## Review Status

All automatically generated links are stored with `review_status: "draft"`.

- `draft`: generated automatically or not yet reviewed editorially.
- `reviewed`: editorially reviewed and suitable for the normal user experience.

The review status is the primary safety boundary. Automation may write links, but it may not mark them as reviewed.

## Matching Rules

Queries should be planned from structured event search components, not directly
from raw event text. The reference schema is documented in
`docs/enrichment/upstream/event-search-components.md`.

Search components are derived from existing event data:

- `event.title`
- `route.title`
- `year_start` and `year_end`
- event tags
- known artist, venue, label, or release terms
- accepted-event dossier source and media leads, when available

Examples:

- `Grandmaster Flash Bronx hip hop 1977`
- `CBGB punk new wave New York 1975`
- `Paradise Garage Larry Levan disco 1979`
- `Fania All-Stars salsa New York 1973`

## Confidence

`confidence` remains a compatibility field in `media_links`, but it should not be treated as editorial truth.

For the YouTube MVP, request plans use `confidence_hint`:

- `high`
- `medium`
- `low`

The merge script maps these hints to numeric values only because the current seed schema still requires `confidence`.

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

## Automation

The current automated workflow has two separate scripts:

1. `backend/scripts/run_youtube_search_requests.py` executes curated YouTube `search.list` request plans.
2. `backend/scripts/enrich_media_links.py` merges normalized YouTube result files into event `media_links`.

The merge script is located at:

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

The merge script:

1. reads `data/seed/events.json`
2. reads normalized YouTube result files from `data/enrichment/youtube-search-results/`
3. extracts YouTube video and playlist candidates
4. sorts candidates by `review_priority`
5. maps `confidence_hint` to the existing numeric `confidence` field
6. deduplicates links by URL
7. writes new links with `review_status: "draft"`

It does not call provider APIs directly. YouTube API interaction happens only in `run_youtube_search_requests.py`.

## Environment Variables

Example values are documented in `.env.example`. For local Codex and test runs, `.env.codex` is also included in the repository with dummy values only.

```powershell
SOUNDATLAS_USE_DUMMY_SERVICES=false
YOUTUBE_API_KEY=
```

Real secrets must not live in the repository. Instead, an external file path is provided through `SOUNDATLAS_ENV_FILE`.

The merge script does not need provider credentials. The YouTube request runner needs a live YouTube key unless it is run in dry-run mode.

## YouTube Request Pipeline

For YouTube search requests, the following rules apply:

1. The simplified MVP workflow is documented in `docs/enrichment/media/youtube-mvp-workflow.md`.
2. Event search components are documented in `docs/enrichment/upstream/event-search-components.md`.
3. Query planning is documented in `docs/enrichment/media/youtube-query-planning.md`.
4. Query plans are stored as JSON request plans under `data/enrichment/youtube-search-requests/`.
5. Request plans use `YOUTUBE_API_KEY` only as a placeholder.
6. `run_youtube_search_requests.py` injects the real key at runtime and redacts it from written result files.
7. Raw YouTube results are normalized into draft result files under `data/enrichment/youtube-search-results/`.
8. `enrich_media_links.py` merges selected video and playlist candidates into `media_links`.
9. Generated links remain `review_status: "draft"` until editorial review.

### Provider Behavior

- `YouTube`: uses curated request plans, supports video and playlist searches, normalizes search results, and keeps review metadata from the request plan.

## ChatGPT Plus-Only Workflow

A ChatGPT Plus account does not provide a local API key for Python scripts. If the project is used only through ChatGPT Plus and Codex CLI, GPT should be treated as an interactive editorial assistant, not as an automated backend service.

In this mode, GPT/Codex is used to prepare and review YouTube request plans. The actual YouTube API call still requires a real `YOUTUBE_API_KEY`:

1. Select an event or content page from the curated seed data.
2. Ask Codex CLI to analyze the title, summary, significance, route, tags, years, and known scene terms.
3. Let Codex propose intent-based YouTube request-plan entries.
4. Review those request plans manually before running the YouTube API.
5. Run `backend/scripts/run_youtube_search_requests.py --dry-run` to inspect planned API calls.
6. Run `backend/scripts/enrich_media_links.py --dry-run` to inspect the seed merge.
7. Keep only plausible links, remove weak matches, and promote links to `reviewed` only after editorial review.

For the MVP, prefer the dedicated prompt in `prompts/generate-youtube-search-queries.md` over ad-hoc prompts.

Example minimal Codex prompt:

```text
You are helping curate media links for SoundAtlas, an interactive music history app.
The current MVP scope is New York 1965-1985. Treat all suggestions as editorial
drafts, not verified facts.

Task:
Analyze the SoundAtlas event below and propose YouTube search queries. Use only these MVP intents:
song, interview, documentary, playlist, dj_mix, venue_context, historical_context.

Safety and quality rules:
- Do not invent media links, source URLs, video IDs, playlist IDs, or API results.
- Do not mark anything as reviewed.
- Do not include API keys, local paths, or secrets.
- Prefer precise historical queries over generic genre queries.
- Include the year or year range when it improves the query.
- Use YouTube-specific intent: song, interview, documentary, playlist, dj_mix, venue_context, or historical_context.
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
  "known_terms": ["<artist>", "<venue>", "<label>", "<release>"]
}

Return this JSON shape:
{
  "topic": "short topic label",
  "mood": "short mood or scene description",
  "target_audience": "who this media helps",
  "keywords": ["keyword"],
  "music_genres": ["genre"],
  "queries": [
    {
      "provider": "youtube",
      "query": "search query",
      "intent": "song | interview | documentary | playlist | dj_mix | venue_context | historical_context",
      "reason": "why this query fits the event",
      "confidence_hint": "high | medium | low"
    }
  ],
  "review_notes": [
    "specific risks or checks an editor should perform"
  ]
}
```

The Plus-only workflow is useful for editorial curation, but it is intentionally not a fully automated ranking system. That boundary keeps secrets out of the chat context and prevents automated links from becoming reviewed content without human approval.

## UX Concept

The story panel displays media links with provider-aware labeling:

- `YouTube video`

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
- simplified YouTube MVP workflow documentation
- curated YouTube request runner
- YouTube result merge into event `media_links`
- tests for the media link schema
- seed validation documentation

Still useful:

- define a review workflow from `draft` to `reviewed`
- evaluate frontend filtering for unreviewed media links
- improve logging and reporting for enrichment runs
- make YouTube source/channel quality easier to review
