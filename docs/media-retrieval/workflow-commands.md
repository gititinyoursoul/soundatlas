# Media Retrieval Workflow Commands

## Purpose

This document describes the practical command sequence for the YouTube-only media retrieval MVP.

Use it when you want to enrich one or more SoundAtlas events with draft YouTube `media_links`.

## Workflow Overview

```text
Codex creates or reviews a query plan
→ CLI validates the query plan
→ CLI runs YouTube search.list
→ CLI merges normalized results into event media_links
→ editor reviews generated draft links
```

## 1. Choose An Event

Pick an event ID from:

```text
data/seed/events.json
```

Example:

```text
kool-herc-back-to-school-jam
```

## 2. Use Codex To Create A Query Plan

Use the prompt:

```text
prompts/generate-youtube-search-queries.md
```

Ask Codex to create or update:

```text
data/enrichment/youtube-search-requests/<event-id>.json
```

Example instruction:

```text
Use prompts/generate-youtube-search-queries.md for event kool-herc-back-to-school-jam.
Create a YouTube request plan only. Do not edit data/seed/events.json.
```

Review the generated request plan before running API calls.

## 3. Validate The Query Plan Without API Calls

Run a dry run:

```powershell
cd backend
uv run python scripts/run_youtube_search_requests.py --event-id kool-herc-back-to-school-jam --dry-run
```

Expected result:

- the command prints planned YouTube requests
- no API call is made
- no result file is written

If this fails, fix the request plan JSON first.

## 4. Run The Live YouTube Search

Live search requires a real `YOUTUBE_API_KEY` configured through `SOUNDATLAS_ENV_FILE`.

Example:

```powershell
cd backend
$env:SOUNDATLAS_ENV_FILE='C:\Users\*\secrets\soundatlas\.env'
uv run python scripts/run_youtube_search_requests.py --event-id kool-herc-back-to-school-jam
```

Expected output file:

```text
data/enrichment/youtube-search-results/kool-herc-back-to-school-jam.json
```

The output file contains normalized draft results. It should not contain a real API key.

## 5. Preview The Merge Into `media_links`

Run a merge dry run:

```powershell
cd backend
uv run python scripts/enrich_media_links.py --event-id kool-herc-back-to-school-jam --dry-run
```

Expected result:

- the command prints the changed event payload
- no seed file is written
- generated links have `review_status: "draft"`

If the command prints `No YouTube search results found.`, create or fetch the normalized result file first.

## 6. Write Draft Links To Seed Data

After reviewing the dry-run output, write the merge:

```powershell
cd backend
uv run python scripts/enrich_media_links.py --event-id kool-herc-back-to-school-jam
```

This updates:

```text
data/seed/events.json
```

Rejected media links are also added to the top-level `ignored_links` collection
in the same seed file. That keeps future enrichment runs from re-adding the same
event-specific URL after it has been rejected.

## 7. Review Generated Links

Manually review every generated link before treating it as accepted content.

Check:

- historical relevance
- title and channel/source quality
- whether it is a YouTube Short, teaser, reaction, cover, or unrelated modern clip
- whether the link should stay `draft`, be promoted to `reviewed`, or be removed

Only set:

```json
"review_status": "reviewed"
```

after editorial review.

If you reject a media item, the UI removes it from the event and stores the
ignored URL for the same event and media kind. That suppression applies to later
reruns of the YouTube enrichment workflow.

## Useful Variants

Validate all request plans without API calls:

```powershell
cd backend
uv run python scripts/run_youtube_search_requests.py --dry-run
```

Run all live YouTube searches:

```powershell
cd backend
$env:SOUNDATLAS_ENV_FILE='C:\Users\*\secrets\soundatlas\.env'
uv run python scripts/run_youtube_search_requests.py
```

Preview merge for all available result files:

```powershell
cd backend
uv run python scripts/enrich_media_links.py --dry-run
```

Limit generated links per event:

```powershell
cd backend
uv run python scripts/enrich_media_links.py --event-id kool-herc-back-to-school-jam --limit 2 --dry-run
```

## Safety Rules

- Do not commit API keys or local secret paths.
- Do not store audio or video files in the repository.
- Keep generated links as `draft` until manual review.
- Do not use Codex to invent video IDs, playlist IDs, source URLs, or API results.
- Prefer fixing query plans over accepting weak search results.
