# Image Enrichment Konzept

## Ziel

SoundAtlas soll Events nicht nur ueber Text, Karte, Timeline und externe Musiklinks vermitteln, sondern auch mit kuratiertem Bildmaterial kontextualisieren. Bilder sollen Orte, Szenen, Kuenstlerinnen und Kuenstler, Releases, Flyer, Clubkultur und Stadtgeschichte sichtbar machen.

Das Ziel ist keine Bilddatenbank im Repository, sondern ein auditierbarer Link-Layer fuer externe Bildquellen.

## Grundprinzipien

- Keine Bilddateien ins Repository laden.
- Keine Bilder automatisch als `reviewed` markieren.
- Nur externe URLs, Metadaten, Rechteinformationen und Attribution speichern.
- Quellen mit klarer Lizenz- oder Rechteinformation bevorzugen.
- Automatisch gefundene Bildkandidaten bleiben `review_status: "draft"`.
- Bilder werden separat von Audio-, Video- und Playlist-Links modelliert.

## Datenmodell

Events erhalten ein eigenes Feld `image_links`. Dieses Feld ist ein Array strukturierter Objekte.

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

### Pflichtfelder

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

### Optionale Felder

- `thumbnail_url`
- `creator`
- `license`
- `license_url`

## Provider

Fuer den MVP sind diese Provider sinnvoll:

- `wikimedia`: Wikimedia Commons und Wikidata-nahe Bildquellen.
- `loc`: Library of Congress.
- `nypl`: NYPL Digital Collections.
- `internet_archive`: Internet Archive.
- `cover_art_archive`: Cover Art Archive fuer Release-Cover.
- `manual`: redaktionell manuell ergaenzte Links.

Provider-APIs sind zu bevorzugen. Scraping ist kein MVP-Ziel.

## Bildtypen

- `venue_photo`: Club, Venue, Gebaeude, Strasse oder Stadtteil.
- `artist_photo`: Kuenstlerin, Kuenstler, Band oder DJ.
- `album_cover`: Cover einer relevanten Veroeffentlichung.
- `flyer_poster`: Konzertflyer, Clubposter oder Eventgrafik.
- `archive_photo`: historisches Archivfoto.
- `map_image`: historische Karte oder Stadtplan-Ausschnitt.
- `press_scan`: Presse- oder Magazinbezug, nur mit klarer Rechtebewertung.

## Rechte- und Review-Status

`rights_status` beschreibt die Nutzbarkeit:

- `open_license`: offene Lizenz mit Attribution.
- `public_domain`: gemeinfrei oder public domain.
- `provider_restricted`: sichtbar beim Provider, aber nicht frei weiterverwendbar.
- `unknown`: Rechte unklar, nicht prominent anzeigen.

`review_status` beschreibt den redaktionellen Zustand:

- `draft`: automatisch oder ungeprueft hinzugefuegt.
- `reviewed`: redaktionell geprueft und fuer UX geeignet.

## Matching-Regeln

Die Suche baut Queries aus bestehenden Event-Daten:

- `event.title`
- `route.title`
- `place.name`
- `year_start` und `year_end`
- Event-Tags
- bekannte Artist-, Venue- oder Label-Begriffe

Beispiele:

- Szene-Event: `CBGB New York punk venue 1977`
- Release-Event: `Blondie Parallel Lines album cover 1978`
- Club-Event: `Paradise Garage New York Larry Levan 1979`
- Stadtteil-Event: `Bronx block party hip hop 1970s`

Hohe Confidence erfordert:

- exakten oder nahen Match bei Venue, Artist, Release oder Event-Titel
- plausiblen Zeitraum
- passende Quelle
- vorhandene Rechte- oder Lizenzinformation

Niedrige Confidence gilt bei:

- generischen Stadtbildern
- unklarem Zeitraum
- fehlender Attribution
- nur indirektem Bezug zum Event

## Automatisierung

Ein spaeteres Skript kann analog zu `backend/scripts/enrich_media_links.py` aufgebaut werden:

```powershell
cd backend
uv run python scripts/enrich_image_links.py --dry-run
```

Geplanter Ablauf:

1. `data/seed/events.json`, `routes.json` und `places.json` laden.
2. Pro Event provider-spezifische Queries erzeugen.
3. Bildkandidaten ueber offizielle APIs abrufen.
4. Kandidaten normalisieren und deduplizieren.
5. Confidence berechnen.
6. Nur Metadaten und externe URLs in `image_links` schreiben.
7. Alle neuen Eintraege als `review_status: "draft"` speichern.

## UX-Konzept

Das Story Panel sollte Bildmaterial kontrolliert anzeigen:

- Erstes `reviewed` Bild als visueller Header.
- Attribution direkt unter dem Bild anzeigen.
- Lizenz oder Rechtehinweis sichtbar verlinken.
- Weitere Bilder optional als kleine Gallery anzeigen.
- `draft`-Bilder nicht in der normalen Nutzeransicht anzeigen.
- Fehlende Bilder duerfen kein Layout brechen.

## Nicht-Ziele

- Keine automatische Bilddownloads.
- Keine lokale Bildoptimierung im MVP.
- Keine ungeprueften Thumbnails prominent anzeigen.
- Keine Nutzung von Bildern ohne Quellen- und Rechtehinweis.
- Keine komplexe Admin-Oberflaeche im ersten Schritt.

## Umsetzungsschritte

1. `image_links` im Event-Schema definieren.
2. TypeScript-Typen im Frontend ergaenzen.
3. `docs/seed-validation.md` um Bildlink-Regeln erweitern.
4. Bestehende Seed-Events mit leeren `image_links` initialisieren.
5. Story Panel fuer reviewed image links erweitern.
6. Tests fuer Schema und Seed-Validierung ergaenzen.
7. Optionales Enrichment-Skript fuer Bildkandidaten implementieren.
