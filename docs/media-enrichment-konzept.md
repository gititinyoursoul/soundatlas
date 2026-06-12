# Media Enrichment Konzept

## Ziel

SoundAtlas soll Events mit externen Musik-, Video- und Playlist-Links anreichern. Diese Links helfen Nutzerinnen und Nutzern, ein Event nicht nur historisch, sondern auch klanglich einzuordnen.

Der MVP speichert keine Audio- oder Videodateien. Es werden nur externe URLs und Metadaten gespeichert.

## Scope

Das Media Enrichment konzentriert sich auf:

- YouTube fuer Videos, Performances, Interviews, Dokumentationsausschnitte und Suchtreffer.
- Spotify fuer Tracks, Alben und Playlists.
- Qobuz fuer Tracks und Alben mit kuratiertem Musikfokus.

Die Links sind Hilfsmittel fuer Exploration, keine redaktionell vollstaendige Diskografie.

## Datenmodell

Events verwenden das Feld `media_links`. Jeder Eintrag ist ein strukturiertes Objekt.

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

### Pflichtfelder

- `provider`
- `type`
- `title`
- `url`
- `query`
- `confidence`
- `review_status`

### Provider

- `youtube`
- `spotify`
- `qobuz`

### Typen

- `track`
- `album`
- `playlist`
- `video`
- `search`

## Review-Status

Alle automatisch erzeugten Links werden mit `review_status: "draft"` gespeichert.

- `draft`: automatisch erzeugt oder noch nicht redaktionell geprueft.
- `reviewed`: redaktionell geprueft und fuer die normale UX geeignet.

Der Review-Status ist die zentrale Sicherheitsgrenze. Automatisierung darf Links schreiben, aber nicht als geprueft markieren.

## Matching-Regeln

Queries werden aus bestehenden Event-Daten gebaut:

- `event.title`
- `route.title`
- `year_start` und `year_end`
- Event-Tags
- bekannten Artist-, Venue-, Label- oder Release-Begriffen

Beispiele:

- `Grandmaster Flash Bronx hip hop 1977`
- `CBGB punk new wave New York 1975`
- `Paradise Garage Larry Levan disco 1979`
- `Fania All-Stars salsa New York 1973`

## Confidence

`confidence` ist ein Wert zwischen `0` und `1`.

Hohe Confidence:

- exakte oder nahe Uebereinstimmung mit Artist, Release, Venue oder Event-Titel
- passender Zeitraum
- Provider-Ergebnis hat eindeutigen Titel und stabile URL
- Typ passt zum Event-Kontext

Mittlere Confidence:

- Szene- oder Routenbezug ist plausibel, aber nicht exakt
- Playlist passt thematisch, aber nicht eindeutig zum konkreten Event

Niedrige Confidence:

- nur generische Genre- oder Stadtbezeichnung
- unklarer Artist-/Release-Bezug
- Ergebnis wirkt modern oder zeitlich unpassend

## Provider-Strategie

### YouTube

Geeignet fuer:

- historische Videos
- Interviews
- TV-Auftritte
- Konzertmitschnitte
- Dokumentationsausschnitte
- Suchlinks, wenn kein eindeutiges Video sicher ist

Risiko:

- Uploads koennen verschwinden.
- Rechte- und Kanalqualitaet sind unterschiedlich.
- Hohe Trefferzahl erfordert Review.

### Spotify

Geeignet fuer:

- Tracks
- Alben
- kuratierte oder algorithmische Playlists

Risiko:

- Verfuegbarkeit ist laenderabhaengig.
- Playlists koennen sich aendern.
- Historische Szenen werden oft nur indirekt abgebildet.

### Qobuz

Geeignet fuer:

- Alben
- Tracks
- redaktionell stabilere Katalogeintraege

Risiko:

- API/Auth kann je nach Account-Setup variieren.
- Katalogabdeckung ist nicht fuer alle Genres gleich stark.

## Automatisierung

Das aktuelle Skript liegt unter:

```powershell
backend/scripts/enrich_media_links.py
```

Ausfuehrung:

```powershell
cd backend
uv run python scripts/enrich_media_links.py
```

Dry Run:

```powershell
cd backend
uv run python scripts/enrich_media_links.py --dry-run
```

Ein einzelnes Event:

```powershell
cd backend
uv run python scripts/enrich_media_links.py --event-id grandmaster-flash
```

Das Skript:

1. liest `data/seed/events.json`
2. liest `data/seed/routes.json`
3. erzeugt Queries aus Event- und Routendaten
4. ruft konfigurierte Provider-APIs ab
5. normalisiert Treffer in das `media_links`-Schema
6. dedupliziert Links anhand der URL
7. schreibt neue Links als `review_status: "draft"`

## Env Vars

Die Beispielwerte stehen in `.env.example`.

```powershell
YOUTUBE_API_KEY=
SPOTIFY_CLIENT_ID=
SPOTIFY_CLIENT_SECRET=
QOBUZ_APP_ID=
QOBUZ_USER_AUTH_TOKEN=
```

Provider ohne gesetzte Zugangsdaten werden uebersprungen.

## UX-Konzept

Das Story Panel zeigt Medienlinks provider-bewusst an:

- `YouTube video`
- `Spotify track`
- `Spotify playlist`
- `Qobuz album`

Fuer die normale Nutzeransicht sollten perspektivisch nur `reviewed` Links prominent erscheinen. `draft` Links koennen fuer interne Review-Ansichten sichtbar sein.

## Nicht-Ziele

- Keine Audio- oder Videodownloads.
- Keine lokalen Medien-Caches.
- Keine Provider-Scraper.
- Keine automatische redaktionelle Freigabe.
- Keine Garantie, dass externe Links dauerhaft verfuegbar bleiben.

## Umsetzungsschritte

Bereits umgesetzt:

- Strukturiertes `media_links`-Schema im Backend.
- TypeScript-Typen fuer `media_links`.
- Story Panel mit Provider-/Typ-Labels.
- Enrichment-Skript fuer YouTube, Spotify und Qobuz.
- Tests fuer Medienlink-Schema.
- Seed-Validierungsdokumentation.

Noch sinnvoll:

- Review-Workflow fuer `draft` zu `reviewed` definieren.
- Frontend-Filter fuer ungepruefte Medienlinks pruefen.
- Logging/Reporting fuer Enrichment-Laeufe verbessern.
- Quellenqualitaet pro Provider messbar machen.
