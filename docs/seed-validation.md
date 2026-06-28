# Seed Data Validation

This file defines the minimum validation rules for the curated MVP seed data under `data/seed/`.

## Core Rules

- Every seed file contains a `_meta` object with `description` and `schema_version`.
- Every domain entity needs a stable, URL-safe `id`.
- IDs are lowercase and use hyphens, for example `birth-of-hip-hop`.
- References must point to existing IDs.
- `source_urls`, `media_links`, and `image_links` are always arrays, even when empty.
- Draft data uses `review_status: "draft"`.

## `routes.json`

Required fields per route:

- `id`
- `title`
- `color`
- `creator`
- `year_start`
- `year_end`
- `summary`
- `thesis`
- `tags`
- `review_status`
- `source_urls`

Validation rules:

- `year_start` is less than or equal to `year_end`.
- `tags` is an array of strings.
- `source_urls` is an array of strings.

## `places.json`

Required fields per place:

- `id`
- `name`
- `borough`
- `place_type`
- `latitude`
- `longitude`
- `summary`
- `review_status`
- `source_urls`

Validation rules:

- `latitude` is a number between `-90` and `90`.
- `longitude` is a number between `-180` and `180`.
- `source_urls` is an array of strings.

## `events.json`

Required fields per event:

- `id`
- `route_id`
- `place_id`
- `title`
- `year_start`
- `year_end`
- `summary`
- `significance`
- `tags`
- `review_status`
- `source_urls`
- `media_links`
- `image_links`

`media_links` contains structured media links:

- `provider`: `youtube`, `spotify`, or `qobuz`
- `type`: `track`, `album`, `playlist`, `video`, or `search`
- `title`
- `url`
- `query`
- `confidence`: number between `0` and `1`
- optional `playback_mode`: `embed` or `external`
- `review_status`

`image_links` contains structured image links:

- `provider`: `wikimedia`, `loc`, `nypl`, `internet_archive`, `cover_art_archive`, or `manual`
- `type`: `venue_photo`, `artist_photo`, `album_cover`, `flyer_poster`, `archive_photo`, `map_image`, or `press_scan`
- `title`
- `image_url`
- optional `thumbnail_url`
- `source_url`
- optional `creator`
- optional `license`
- optional `license_url`
- `rights_status`: `open_license`, `public_domain`, `provider_restricted`, or `unknown`
- `alt_text`
- `query`
- `confidence`: number between `0` and `1`
- `review_status`

Validation rules:

- `route_id` references a route from `routes.json`.
- `place_id` references a place from `places.json`.
- `year_start` is less than or equal to `year_end`.
- `tags` and `source_urls` are arrays of strings.
- `media_links` is an array of media-link objects.
- `image_links` is an array of image-link objects.

## `connections.json`

Required fields per connection:

- `id`
- `from_event_id`
- `to_event_id`
- `type`
- `summary`
- `review_status`

Validation rules:

- `from_event_id` references an event from `events.json`.
- `to_event_id` references an event from `events.json`.
- `from_event_id` and `to_event_id` must not be identical.
- `type` is a short machine-readable string, for example `influence`, `context`, or `media_transition`.

## MVP Check

The first seed dataset is technically usable when:

- at least one route exists
- every route has at least one event
- every event has a valid place
- every connection points to existing events
- all required fields are present
