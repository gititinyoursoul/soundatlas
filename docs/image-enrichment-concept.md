# Image Enrichment Concept

## Goal

SoundAtlas should contextualize events not only through text, map, timeline, and external music links, but also through curated image material. Images should make places, scenes, artists, releases, flyers, club culture, and urban history visible.

The goal is not an image database inside the repository, but an auditable link layer for external image sources.

## Core Principles

- Do not add image files to the repository.
- Do not automatically mark images as `reviewed`.
- Store only external URLs, metadata, rights information, and attribution.
- Prefer sources with clear license or rights information.
- Automatically found image candidates remain `review_status: "draft"`.
- Model images separately from audio, video, and playlist links.

## Data Model

Events receive their own `image_links` field. This field is an array of structured objects.

```json
{
  "provider": "wikimedia",
  "type": "venue_photo",
  "title": "CBGB exterior",
  "image_url": "https://example.org/image.jpg",
  "thumbnail_url": "https://example.org/thumb.jpg",
  "source_url": "https://example.org/source-page",
  "creator": "Photographer Name",
  "license": "CC BY-SA 4.0",
  "license_url": "https://creativecommons.org/licenses/by-sa/4.0/",
  "rights_status": "open_license",
  "alt_text": "Exterior view of CBGB in New York.",
  "query": "CBGB New York punk venue 1977",
  "confidence": 0.82,
  "review_status": "draft"
}
```

### Required Fields

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

### Optional Fields

- `thumbnail_url`
- `creator`
- `license`
- `license_url`

## Providers

These providers are useful for the MVP:

- `wikimedia`: Wikimedia Commons and Wikidata-adjacent image sources.
- `loc`: Library of Congress.
- `nypl`: NYPL Digital Collections.
- `internet_archive`: Internet Archive.
- `cover_art_archive`: Cover Art Archive for release covers.
- `manual`: Editorially added links.

Provider APIs are preferred. Scraping is not an MVP goal.

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

## Matching Rules

Search builds queries from existing event data:

- `event.title`
- `route.title`
- `place.name`
- `year_start` and `year_end`
- Event tags
- Known artist, venue, or label terms

Examples:

- Scene event: `CBGB New York punk venue 1977`
- Release event: `Blondie Parallel Lines album cover 1978`
- Club event: `Paradise Garage New York Larry Levan 1979`
- Neighborhood event: `Bronx block party hip hop 1970s`

High confidence requires:

- Exact or close match for venue, artist, release, or event title
- Plausible time period
- Appropriate source
- Existing rights or license information

Low confidence applies to:

- Generic city images
- Unclear time period
- Missing attribution
- Only indirect relationship to the event

## Automation

A later script can follow the pattern of `backend/scripts/enrich_media_links.py`:

```powershell
cd backend
uv run python scripts/enrich_image_links.py --dry-run
```

Planned flow:

1. Load `data/seed/events.json`, `routes.json`, and `places.json`.
2. Generate provider-specific queries for each event.
3. Fetch image candidates through official APIs.
4. Normalize and deduplicate candidates.
5. Calculate confidence.
6. Write only metadata and external URLs to `image_links`.
7. Store all new entries as `review_status: "draft"`.

## UX Concept

The story panel should show image material in a controlled way:

- Use the first `reviewed` image as a visual header.
- Show attribution directly below the image.
- Link the license or rights notice visibly.
- Optionally show additional images as a small gallery.
- Do not show `draft` images in the normal user view.
- Missing images must not break the layout.

## Non-Goals

- No automatic image downloads.
- No local image optimization in the MVP.
- No prominent display of unreviewed thumbnails.
- No use of images without source and rights notices.
- No complex admin interface in the first step.

## Implementation Steps

1. Define `image_links` in the event schema.
2. Add TypeScript types in the frontend.
3. Extend `docs/seed-validation.md` with image-link rules.
4. Initialize existing seed events with empty `image_links`.
5. Extend the story panel for reviewed image links.
6. Add tests for schema and seed validation.
7. Optionally implement an enrichment script for image candidates.
