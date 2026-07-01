# Image Enrichment Overview

## Goal

SoundAtlas should automatically collect draft image candidates for events, then
let the editor review them before they become accepted content.

The first automation pass should target 3-5 draft image candidates per event.
Images are not downloaded into the repository. The seed data stores only external
URLs, source URLs, attribution, rights metadata, and review state.

Images should contextualize events through places, scenes, artists, releases,
flyers, club culture, urban history, and archival material. The goal is an
auditable external link layer, not an image database inside the repository.

The shared enrichment workflow is documented in
`docs/enrichment/workflow.md`. This concept focuses on the image-specific
branch of that pipeline.

## Core Principles

- Do not add image files to the repository.
- Do not automatically mark generated images as `reviewed`.
- Store only external URLs, metadata, rights information, and attribution.
- Prefer sources with clear license or rights information.
- Model images separately from audio, video, and playlist links.
- Provider APIs are preferred. Scraping is not an MVP goal.

## Data Model

Events use the `image_links` field. Each entry is a structured object.

Required fields:

- `provider`
- `type`
- `title`
- `image_url`
- `source_url`
- `rights_status`
- `alt_text`
- `query`
- `confidence`
- `review_status`

Optional fields:

- `thumbnail_url`
- `creator`
- `license`
- `license_url`

## Source Strategy

Start with public sources that do not require an API key:

- `wikimedia`: Wikimedia Commons and related MediaWiki image metadata.
- `loc`: Library of Congress public JSON search.
- `internet_archive`: Internet Archive public search and item metadata.

Defer sources that add setup or matching complexity:

- `nypl`: requires authentication and has API deprecation risk.
- `cover_art_archive`: useful for release-centered events, but needs
  MusicBrainz release or release-group matching first.
- General web image search: avoid because rights, attribution, and provenance
  are weak for the MVP.
- `manual`: editorially added links remain valid but are outside the automated
  no-key enrichment pass.

## Image Types

- `venue_photo`: Club, venue, building, street, or neighborhood.
- `artist_photo`: Artist, band, or DJ.
- `album_cover`: Cover of a relevant release.
- `flyer_poster`: Concert flyer, club poster, or event graphic.
- `archive_photo`: Historical archive photo.
- `map_image`: Historical map or city-map excerpt.
- `press_scan`: Press or magazine reference, only with clear rights review.

## Rights and Review Status

`rights_status` describes usability:

- `open_license`: open license with attribution.
- `public_domain`: public domain.
- `provider_restricted`: visible at the provider, but not freely reusable.
- `unknown`: unclear rights; do not show prominently.

`review_status` describes the editorial state:

- `draft`: automatically added or not yet reviewed.
- `reviewed`: editorially checked and suitable for the UX.

## Provider Handling

Each source should have its own provider module or function. Provider-specific
code owns search URLs, pagination, response parsing, thumbnail extraction,
source-page extraction, and rights mapping.

All providers should return the same normalized candidate shape:

```json
{
  "provider": "wikimedia",
  "type": "archive_photo",
  "title": "Example image title",
  "image_url": "https://example.org/image.jpg",
  "thumbnail_url": "https://example.org/thumb.jpg",
  "source_url": "https://example.org/source-page",
  "creator": "Creator name",
  "license": "License label",
  "license_url": "https://example.org/license",
  "rights_status": "open_license",
  "alt_text": "Short description of the image.",
  "query": "CBGB New York punk venue 1977",
  "confidence": 0.62,
  "review_status": "draft"
}
```

Provider defaults:

- Wikimedia: prefer `open_license` or `public_domain` when metadata supports it.
- Library of Congress: use `public_domain` only for clear public-domain or
  no-known-restrictions records; otherwise use `provider_restricted` or
  `unknown`.
- Internet Archive: default to `unknown` unless metadata includes a usable
  license or public-domain signal.

## Query Strategy

For each event, generate a small set of provider-neutral queries from existing
seed data:

- event title
- place name
- route title
- `year_start` and `year_end`
- event tags
- known artist, venue, label, release, film, or organization terms already
  present in the event text

The current v2 planner turns that input into a retrieval brief, then builds
short query ladders around a strong identity term and the smallest useful
supporting context.

Query ordering rules:

- Venue and concrete-place queries must include city or borough context, such as
  `Bronx` or `New York`, before any time term.
- Artist queries start with the artist or group name plus the event year/range,
  then try decade and individual-year variants for short ranges.
- Work queries start with the title plus the strongest time term, for example
  `Wild Style 1983`; film works add `film` or scene context as fallback variants.
- Event-title archive queries remain broad fallbacks after place, artist, and
  work-specific searches.
- Broad region-only queries, such as `South Bronx` alone, are skipped.

For short year ranges, the planner uses range, decade, and individual-year
variants. For example, an event from 1975 to 1977 can produce `1975 1977`,
`1970s`, `1975`, `1976`, and `1977` as supporting time context.

The target candidate mix per event is:

- one specific event, artist, venue, release, film, label, or organization image
- one place or urban-context image
- one route/theme image
- one archive, flyer, press, or map candidate where available
- one additional high-confidence candidate if the first four are strong

The script should keep 3-5 candidates per event after deduplication and scoring.
Weak generic city images should be skipped rather than filling the quota.

## Enrichment Pipeline

Add an image enrichment script modeled after `backend/scripts/enrich_media_links.py`.

Expected command shape:

```powershell
cd backend
uv run python scripts/enrich_image_links.py --event-id kool-herc-back-to-school-jam --dry-run
uv run python scripts/enrich_image_links.py --event-id kool-herc-back-to-school-jam
```

The script should:

1. Load `data/seed/events.json`, `routes.json`, and `places.json`.
2. Build provider-neutral search queries per event.
3. Call enabled no-key providers.
4. Normalize provider responses into `image_links`.
5. Drop invalid candidates missing required fields.
6. Deduplicate by `image_url`, `thumbnail_url`, and `source_url`.
7. Apply simple heuristic confidence scores.
8. Keep 3-5 candidates per event.
9. Merge without duplicating existing event image links.
10. Write every generated candidate with `review_status: "draft"`.

Required CLI behavior:

- `--dry-run`: print the changed payload without writing seed data.
- `--event-id`: limit enrichment to one event.
- `--route-id`: optional route-level targeting.
- `--limit`: maximum candidates per event, default 5.
- `--provider`: optional repeatable provider filter.

## Review Boundary

Automation may add draft image links, but it must never mark a candidate as
`reviewed`.

Rejected image links are added to an event-level ignore list in
`data/seed/events.json`. Rerunning enrichment skips ignored image URLs, source
pages, and thumbnail URLs for the same event and provider kind, so a rejected
candidate does not immediately come back on the next pass.

The existing media/image review drawer is the intended review surface. The
editor should inspect relevance, rights, attribution, source quality, and image
fit before accepting or rejecting candidates.

Current public-mode gating is still a TODO. Until that boundary is implemented,
generated images may be visible in internal explorer surfaces. That is acceptable
for local review, but the public UI should eventually render only reviewed image
links.

## UX Concept

The story panel should show image material in a controlled way:

- Use the first `reviewed` image as a visual header when the public display
  boundary exists.
- Show attribution directly below the image.
- Link the license or rights notice visibly.
- Optionally show additional images as a small gallery.
- Do not show `draft` images in the public user view.
- Missing images must not break the layout.

## Non-Goals

- No automatic image downloads.
- No local image optimization in the MVP.
- No prominent public display of unreviewed thumbnails.
- No use of images without source and rights notices.
- No complex admin interface in the first automation step.

## Acceptance Criteria

- Running the script with `--dry-run` does not edit `data/seed/events.json`.
- Running the script for one event adds up to 3-5 draft image candidates.
- Generated candidates validate against the existing `ImageLink` schema.
- Existing image links are preserved and not duplicated.
- Rejected image links are added to the ignore list and skipped on rerun.
- Provider failures do not abort the whole enrichment run when another provider
  can still return candidates.
- No API keys, image files, or local machine paths are written to the repository.
