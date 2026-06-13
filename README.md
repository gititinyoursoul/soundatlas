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
$env:SOUNDATLAS_ENV_FILE='C:\Users\Marius\secrets\soundatlas\.env'
```

Reale Secrets gehoeren nicht in dieses Repository. Lege sie stattdessen ausserhalb des Workspaces ab, zum Beispiel unter `C:\Users\Marius\secrets\soundatlas\.env`, und setze nur den Zeiger `SOUNDATLAS_ENV_FILE` in deiner Shell. Wenn der Zeiger fehlt, faellt das Media-Enrichment sicher auf Dummy-/Testmodus zurueck oder bricht ohne externe Requests ab.

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
# C:\Users\Marius\secrets\soundatlas\.env
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
