# SoundAtlas

SoundAtlas ist ein MVP fuer eine interaktive Musikgeschichts-App. Der aktuelle Scope ist **New York 1965-1985** mit kuratierten Routen, Events, Places, Verbindungen und externen Medienlinks.

## Voraussetzungen

- Python `>=3.13`
- `uv`
- Node.js und npm
- PowerShell fuer das optionale Startskript

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

Erforderliche Env Vars je nach Provider:

- `YOUTUBE_API_KEY`
- `SPOTIFY_CLIENT_ID`
- `SPOTIFY_CLIENT_SECRET`
- `QOBUZ_APP_ID`
- `QOBUZ_USER_AUTH_TOKEN`

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
