# Shared Media and Image Enrichment Workflow

## Purpose

This document describes the common enrichment pipeline for SoundAtlas external
media links and image links.

The current implementations differ by provider and target field:

- media enrichment writes `media_links`
- image enrichment writes `image_links`

The workflow is shared until the provider/type-specific branch. After that
split, each provider module owns its own search, parsing, rights mapping, and
candidate normalization.

## Shared Workflow

```text
seed data selection
-> retrieval brief generation
-> query planning
-> provider execution
-> candidate normalization
-> deduplication and ranking
-> merge into seed data
-> editorial review
```

## Shared Inputs

Both workflows start from the same curated seed data:

- `data/seed/events.json`
- `data/seed/routes.json`
- `data/seed/places.json`

The shared retrieval brief can use:

- event title
- route title
- place name
- year range
- tags
- summary
- significance
- other known scene terms already present in the event text

## Split Point

The process splits after query planning and before provider execution.

At that point:

- image enrichment selects image providers and image-specific query ladders
- media enrichment selects media providers and media-specific request plans

Provider code then owns:

- search URLs or request calls
- pagination
- response parsing
- thumbnail or preview extraction
- source-page extraction
- rights or license mapping
- provider-specific normalization into the shared link shape

## Shared Candidate Rules

Both workflows should follow the same candidate rules:

- keep generated links as `draft`
- never mark generated candidates as `reviewed`
- preserve existing accepted links
- deduplicate by stable external URLs or equivalent provider identifiers
- skip rejected items through the event-level ignore list
- prefer no result over padding an event with weak generic matches

## Shared Review Boundary

Automation may write draft links, but editorial review decides what becomes
`reviewed`.

The review surface should:

- inspect historical relevance
- inspect source quality
- inspect attribution and rights metadata
- inspect whether the item belongs with the specific event

Rejected links are recorded in the event-level ignore list so reruns do not
immediately re-add the same item.

## Image Workflow

Image enrichment currently uses a Wikimedia-first pass and plans queries from a
retrieval brief built from the event, route, and place data.

The image-specific docs are:

- `docs/image-retrieval/image-enrichment-concept.md`
- `docs/image-retrieval/workflow-commands.md`

## Media Workflow

Media enrichment currently uses a YouTube-only MVP flow with curated request
plans and normalized result files.

The media-specific docs are:

- `docs/media-retrieval/media-enrichment-concept.md`
- `docs/media-retrieval/workflow-commands.md`

## Practical Rule

If a step applies to both image and media enrichment, document it here once.
If a step only applies to one provider family or one target type, document it in
the relevant image or media doc instead.
