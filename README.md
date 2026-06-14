# SoundAtlas

SoundAtlas ist ein MVP fuer eine interaktive Musikgeschichts-App. Der aktuelle Scope ist **New York 1965-1985** mit kuratierten Routen, Events, Places, Verbindungen und externen Medienlinks.

## Voraussetzungen

- Python `>=3.13`
- `uv`
- Node.js und npm
- PowerShell fuer das optionale Startskript

## Environment

Eine Beispielkonfiguration liegt in `.env.example`. Fuer lokale Codex-/Testlaeufe gibt es zusaetzlich `.env.codex` mit reinen Dummy-Werten.

```powershell
$env:SOUNDATLAS_ENV_FILE='C:\Users\*\secrets\soundatlas\.env'
```

Reale Secrets gehoeren nicht in dieses Repository. Lege sie stattdessen ausserhalb des Workspaces ab, zum Beispiel unter `C:\Users\*\secrets\soundatlas\.env`, und setze nur den Zeiger `SOUNDATLAS_ENV_FILE` in deiner Shell. Wenn der Zeiger fehlt, faellt das Media-Enrichment sicher auf Dummy-/Testmodus zurueck oder bricht ohne externe Requests ab.

## Lokaler Start

### Schnellstart mit Skript

```powershell
.\scripts\start-dev.ps1
```

Das Skript startet:

- Backend: `http://127.0.0.1:8000`
- Frontend: `http://127.0.0.1:5173`

Optional koennen Ports gesetzt werden:

```powershell
.\scripts\start-dev.ps1 -BackendPort 8001 -FrontendPort 5174
```

### Backend manuell starten

```powershell
cd backend
uv run uvicorn app.main:app --reload --host 127.0.0.1 --port 8000
```

Wichtige API-Endpunkte:

- `GET /health`
- `GET /routes`
- `GET /events`
- `GET /events?route_id=birth-of-hip-hop`
- `GET /events?from_year=1970&to_year=1985`
- `GET /events/{event_id}`
- `GET /places`
- `GET /connections`
- `GET /connections?route_id=birth-of-hip-hop`

### Frontend manuell starten

```powershell
cd frontend
$env:VITE_API_BASE_URL='http://127.0.0.1:8000'
npm run dev -- --host 127.0.0.1 --port 5173
```

Danach die App unter `http://127.0.0.1:5173` oeffnen.

## Tests und Checks

Backend:

```powershell
cd backend
uv run pytest
```

Frontend:

```powershell
cd frontend
npm run check
```

## Seed-Daten

Die MVP-Daten liegen in:

- `data/seed/routes.json`
- `data/seed/places.json`
- `data/seed/events.json`
- `data/seed/connections.json`

Die Validierungsregeln sind in `docs/seed-validation.md` dokumentiert. Events verwenden strukturierte `media_links` fuer externe Links zu YouTube, Spotify und Qobuz. Es werden keine Audio- oder Videodateien im Repository gespeichert.

## Medienlinks automatisch anreichern

Das Enrichment-Skript liest `data/seed/events.json`, sucht passende Medienlinks ueber Provider-APIs und schreibt strukturierte `media_links` zurueck.

Erforderliche Env Vars in der externen Secret-Datei je nach Provider:

- `YOUTUBE_API_KEY`
- `SOUNDATLAS_OPENAI_API_KEY`
- `SOUNDATLAS_OPENAI_MODEL`
- `SPOTIFY_CLIENT_ID`
- `SPOTIFY_CLIENT_SECRET`
- `QOBUZ_APP_ID`
- `QOBUZ_USER_AUTH_TOKEN`

Empfohlene Secret-Datei ausserhalb des Repos:

```powershell
# C:\Users\*\secrets\soundatlas\.env
YOUTUBE_API_KEY=your-real-youtube-key
SOUNDATLAS_OPENAI_API_KEY=your-real-openai-key
SOUNDATLAS_OPENAI_MODEL=gpt-4.1-mini
SPOTIFY_CLIENT_ID=your-real-spotify-client-id
SPOTIFY_CLIENT_SECRET=your-real-spotify-client-secret
QOBUZ_APP_ID=your-real-qobuz-app-id
QOBUZ_USER_AUTH_TOKEN=your-real-qobuz-user-token
```

Ausfuehren:

```powershell
cd backend
uv run python scripts/enrich_media_links.py
```

Dry Run ohne Schreibzugriff:

```powershell
cd backend
uv run python scripts/enrich_media_links.py --dry-run
```

Ein einzelnes Event anreichern:

```powershell
cd backend
uv run python scripts/enrich_media_links.py --event-id grandmaster-flash
```

Alle automatisch erzeugten Medienlinks bleiben `review_status: "draft"` und muessen redaktionell geprueft werden.

Die YouTube-Suche laeuft ueber eine getrennte Content-Analyse-, Such- und Ranking-Pipeline. Der YouTube-Key wird nur im YouTube-Service verwendet; GPT-/LLM-Komponenten erhalten ausschliesslich Seitentext, Suchbegriffe und Video-Metadaten.

### Kuratierte YouTube-Search-Requests ausfuehren

Die Dateien unter `data/enrichment/youtube-search-requests/` sind kuratierte Request-Plaene fuer die YouTube Data API. Sie enthalten nur den Platzhalter `YOUTUBE_API_KEY`. Das Ausfuehrungsskript laedt den echten Key ueber `SOUNDATLAS_ENV_FILE`, ruft `youtube.search.list` auf und schreibt normalisierte Draft-Ergebnisse nach `data/enrichment/youtube-search-results/`.

Dry Run ohne API-Call:

```powershell
cd backend
uv run python scripts/run_youtube_search_requests.py --dry-run
```

Ein einzelnes Event gegen die YouTube API ausfuehren:

```powershell
cd backend
$env:SOUNDATLAS_ENV_FILE='C:\Users\*\secrets\soundatlas\.env'
uv run python scripts/run_youtube_search_requests.py --event-id grandmaster-flash-dj-techniques
```

Die Ergebnisdateien sind generiert und bleiben aus Git ausgeschlossen. Uebernehme passende Treffer erst nach Review in `data/seed/events.json`.

### Medienlinks mit ChatGPT Plus und Codex Extension kuratieren

Ein ChatGPT Plus Account ist kein API-Key fuer lokale Python-Skripte. Wenn du nur ChatGPT Plus ueber die VS Code Codex Extension verwendest, bleibt GPT ein interaktives Review- und Kurationswerkzeug. Das Enrichment-Skript kann dann weiterhin YouTube, Spotify und Qobuz ueber deren Provider-APIs abfragen, aber es nutzt deinen Plus-Account nicht automatisch als lokale GPT-Schnittstelle.

Empfohlener Plus-only Ablauf:

1. Event im Seed-Datensatz auswaehlen, zum Beispiel aus `data/seed/events.json`.
2. Codex in VS Code bitten, aus `title`, `summary`, `significance`, `tags`, Route und Jahr passende Suchqueries vorzuschlagen.
3. Queries redaktionell pruefen und bei Bedarf in den Skript- oder Datenworkflow uebernehmen.
4. Provider-Enrichment mit echten YouTube-/Spotify-/Qobuz-Keys aus der externen Secret-Datei als Dry Run ausfuehren.
5. Die erzeugten `draft`-Links mit Codex/ChatGPT Plus bewerten lassen.
6. Geeignete Links manuell auf `review_status: "reviewed"` setzen oder ungeeignete Links entfernen.

Beispielprompt fuer Codex in VS Code:

```text
You are helping curate media links for SoundAtlas, an interactive music history app.
The current MVP scope is New York 1965-1985. Treat all suggestions as editorial
drafts, not verified facts.

Task:
Analyze the SoundAtlas event below and propose search queries for YouTube,
Spotify, and Qobuz. Focus on historically plausible media that could help users
understand the event through sound, scene context, interviews, performances,
documentary clips, artists, venues, years, labels, and related cultural terms.

Safety and quality rules:
- Do not invent media links, source URLs, video IDs, album IDs, or API results.
- Do not mark anything as reviewed.
- Do not include API keys, local paths, or secrets.
- Prefer precise historical queries over generic genre queries.
- Include the year or year range when it improves the query.
- Use provider-specific intent: YouTube for video/interview/documentary/performance,
  Spotify for tracks/albums/playlists, Qobuz for tracks/albums.
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
      "intent": "video | interview | documentary | performance | track | album | playlist",
      "reason": "why this query fits the event",
      "confidence_hint": "high | medium | low"
    }
  ],
  "review_notes": [
    "specific risks or checks an editor should perform"
  ]
}
```

## Projektstruktur

- `backend/`: FastAPI-App, Pydantic-Schemas, Tests und Media-Enrichment-Skript
- `frontend/`: SvelteKit-App mit Karte, Timeline, Route Filter und Story Panel
- `data/seed/`: kuratierte JSON-Daten fuer den MVP
- `docs/`: Produkt-, Routen- und Datenvalidierungsdokumentation
- `scripts/`: lokale Hilfsskripte

## Arbeitsregeln

- Keine Secrets oder lokalen Pfade committen.
- Keine Audio- oder Videodateien ins Repository legen.
- Datenquellen und Medienlinks als externe URLs pflegen.
- Neue Routen und Daten immer gegen `docs/seed-validation.md` pruefen.
