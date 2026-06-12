# Seed-Daten Validierung

Diese Datei definiert die minimale Validierungsregel fuer die kuratierten MVP-Seed-Daten unter `data/seed/`.

## Grundregeln

- Jede Seed-Datei enthaelt ein `_meta`-Objekt mit `description` und `schema_version`.
- Jede fachliche Entity braucht eine stabile, URL-taugliche `id`.
- IDs sind klein geschrieben und verwenden Bindestriche, z. B. `birth-of-hip-hop`.
- Referenzen muessen auf existierende IDs zeigen.
- `source_urls`, `media_links` und `image_links` sind immer Arrays, auch wenn sie leer sind.
- Draft-Daten verwenden `review_status: "draft"`.

## `routes.json`

Pflichtfelder pro Route:

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

Validierungsregeln:

- `year_start` ist kleiner oder gleich `year_end`.
- `tags` ist ein Array aus Strings.
- `source_urls` ist ein Array aus Strings.

## `places.json`

Pflichtfelder pro Place:

- `id`
- `name`
- `borough`
- `place_type`
- `latitude`
- `longitude`
- `summary`
- `review_status`
- `source_urls`

Validierungsregeln:

- `latitude` ist eine Zahl zwischen `-90` und `90`.
- `longitude` ist eine Zahl zwischen `-180` und `180`.
- `source_urls` ist ein Array aus Strings.

## `events.json`

Pflichtfelder pro Event:

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

`media_links` enthaelt strukturierte Medienlinks:

- `provider`: `youtube`, `spotify` oder `qobuz`
- `type`: `track`, `album`, `playlist`, `video` oder `search`
- `title`
- `url`
- `query`
- `confidence`: Zahl zwischen `0` und `1`
- `review_status`

`image_links` enthaelt strukturierte Bildlinks:

- `provider`: `wikimedia`, `loc`, `nypl`, `internet_archive`, `cover_art_archive` oder `manual`
- `type`: `venue_photo`, `artist_photo`, `album_cover`, `flyer_poster`, `archive_photo`, `map_image` oder `press_scan`
- `title`
- `image_url`
- `thumbnail_url` optional
- `source_url`
- `creator` optional
- `license` optional
- `license_url` optional
- `rights_status`: `open_license`, `public_domain`, `provider_restricted` oder `unknown`
- `alt_text`
- `query`
- `confidence`: Zahl zwischen `0` und `1`
- `review_status`

Validierungsregeln:

- `route_id` referenziert eine Route aus `routes.json`.
- `place_id` referenziert einen Place aus `places.json`.
- `year_start` ist kleiner oder gleich `year_end`.
- `tags` und `source_urls` sind Arrays aus Strings.
- `media_links` ist ein Array aus Medienlink-Objekten.
- `image_links` ist ein Array aus Bildlink-Objekten.

## `connections.json`

Pflichtfelder pro Connection:

- `id`
- `from_event_id`
- `to_event_id`
- `type`
- `summary`
- `review_status`

Validierungsregeln:

- `from_event_id` referenziert ein Event aus `events.json`.
- `to_event_id` referenziert ein Event aus `events.json`.
- `from_event_id` und `to_event_id` duerfen nicht identisch sein.
- `type` ist ein kurzer maschinenlesbarer String, z. B. `influence`, `context` oder `media_transition`.

## MVP-Pruefung

Der erste Seed-Datensatz gilt als technisch brauchbar, wenn:

- mindestens eine Route existiert
- jede Route mindestens ein Event hat
- jedes Event einen gueltigen Place hat
- jede Connection auf existierende Events zeigt
- alle Pflichtfelder vorhanden sind
