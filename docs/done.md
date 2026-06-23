# SoundAtlas Done

Archiv abgeschlossener Arbeitspakete. Die aktuelle Arbeitsliste liegt in `TODO.md`.

## Produkt und Content

- [x] Leitfrage fuer den MVP finalisieren
- [x] Route `Birth of Hip-Hop` redaktionell ausarbeiten
- [x] 8-12 Events fuer die Hip-Hop-Route definieren
- [x] 5-8 Places mit Koordinaten erfassen
- [x] 8-12 Influence Connections definieren
- [x] Quellenstruktur fuer Events festlegen
- [x] Medienlink-Regeln klaeren: YouTube, Spotify, Internet Archive oder externe Links
- [x] Media-Enrichment-Konzept dokumentieren
- [x] Offene historische Unsicherheiten markieren

## Seed-Daten

- [x] Datenformat fuer Routes, Events, Places und Connections festlegen
- [x] `data/seed/routes.json` anlegen
- [x] `data/seed/places.json` anlegen
- [x] `data/seed/events.json` anlegen
- [x] `data/seed/connections.json` anlegen
- [x] Beispiel-Daten fuer `Birth of Hip-Hop` eintragen
- [x] Einfache Validierung fuer Pflichtfelder definieren
- [x] Quellen- und Medienlinks als Arrays modellieren

## Backend

- [x] Backend-Projektbeschreibung in `backend/pyproject.toml` aktualisieren
- [x] FastAPI-App-Struktur unter `backend/app/` anlegen
- [x] Pydantic-Schemas fuer API-Responses definieren
- [x] JSON-Seed-Dateien im Backend laden
- [x] Seed-Daten gegen `docs/seed-validation.md` validieren
- [x] `GET /health` implementieren
- [x] `GET /routes` implementieren
- [x] `GET /events` mit `from_year`, `to_year` und `route_id` implementieren
- [x] `GET /events/{event_id}` implementieren
- [x] `GET /places` implementieren
- [x] `GET /connections` mit `route_id` implementieren
- [x] Fehlerverhalten fuer unbekannte IDs und leere Filterergebnisse definieren
- [x] Lokale CORS-Konfiguration fuer das Frontend ergaenzen
- [x] Minimale Backend-Tests fuer Health und Events ergaenzen
- [x] Sichere Media-Enrichment-Settings mit externem Secret-Pfad einfuehren
- [x] Mockbare YouTube-Analyse-/Search-/Ranking-Pipeline fuer Content Pages umsetzen
- [x] YouTube-Search-Prompt `prompts/generate-youtube-search-queries.md` so anpassen, dass Shorts ausgeschlossen werden
- [x] Pruefen, ob `backend/scripts/enrich_media_links.py` mit dem Plus-only Workflow kompatibel ist

## Frontend

- [x] Bestehendes `frontend/` auf SvelteKit migrieren
- [x] TypeScript-Konfiguration und SvelteKit-Scripts einrichten
- [x] Frontend-Dependencies pruefen: SvelteKit, Vite, TypeScript, Leaflet
- [x] API-Basis-URL fuer lokale Entwicklung definieren
- [x] TypeScript-Typen fuer `Route`, `Place`, `Event` und `Connection` anlegen
- [x] API-Client fuer `/routes`, `/events`, `/places` und `/connections` bauen
- [x] Erste Seite als App-Shell mit Karte, Timeline und Side Panel aufbauen
- [x] Leaflet browser-sicher in Svelte einbinden
- [x] `MapView`-Komponente mit Event-Markern erstellen
- [x] `Timeline`-Komponente fuer Zeitraum `1965-1985` erstellen
- [x] `RouteFilter`-Komponente fuer aktive Routen erstellen
- [x] `StoryPanel`-Komponente fuer ausgewähltes Event erstellen
- [x] Gemeinsamen Frontend-State fuer Route, Zeitraum und ausgewähltes Event definieren
- [x] Event-Marker nach aktivem Zeitraum und Route filtern
- [x] Route-Farben konsistent aus API-Daten darstellen
- [x] Loading-, Error- und Empty-States anzeigen
- [x] Frontend-Smoke-Check oder Build-Check definieren und ausfuehren

## UX und Design

- [x] Erste Bildschirmaufteilung festlegen: Karte, Timeline, Side Panel
- [x] Farbcode pro Route definieren
- [x] Marker-Zustaende definieren: default, hover, selected
- [x] 1977 als dramaturgischen Fokus sichtbar machen
- [x] Mobile Layout grob pruefen
- [x] Quellen und Medienlinks im Story Panel darstellen
- [x] Verbindungen zwischen Events visuell oder textlich anzeigen
- [x] Frontend-Akzeptanzkriterien pruefen: Karte zeigt Hip-Hop-Events, Timeline filtert, Story Panel reagiert auf Markerauswahl

## Bildmaterial

- [x] Konzept fuer Event-Bildmaterial dokumentieren
- [x] `image_links` im Event-Schema definieren
- [x] Seed-Validierungsregeln fuer Bildlinks dokumentieren
- [x] Bestehende Events mit leeren `image_links` initialisieren
- [x] Story Panel fuer reviewed Bildmaterial erweitern
- [x] Tests fuer Bildlink-Schema und Seed-Daten ergaenzen
- [x] Optionales Skript fuer automatische Bildkandidaten planen

## Infrastruktur

- [x] Root-README fuer Projektstart anlegen
- [x] Backend-Startbefehl dokumentieren
- [x] Frontend-Startbefehl dokumentieren
- [x] Gemeinsame Entwicklungsbefehle definieren
- [x] Containerisierte lokale Entwicklungsumgebung fuer Backend und Frontend mit Docker Compose definieren

## Docker Compose Run Checklist

- [x] Zielmodus festlegen: lokale Development-Container mit Hot Reload fuer Backend und Frontend
- [x] Backend-Container planen: Python `>=3.13`, `uv`, Arbeitsverzeichnis `/workspace/backend`
- [x] Backend-`Dockerfile` unter `backend/Dockerfile` anlegen
- [x] Backend-Abhaengigkeiten ueber `uv sync` oder `uv run` reproduzierbar installieren
- [x] Backend-Startkommando im Container definieren: `uv run uvicorn app.main:app --reload --host 0.0.0.0 --port 8000`
- [x] Sicherstellen, dass der Backend-Container Zugriff auf `data/seed/` aus dem Repo-Root hat
- [x] Frontend-Container planen: Node.js LTS, npm, Arbeitsverzeichnis `/workspace/frontend`
- [x] Frontend-`Dockerfile` unter `frontend/Dockerfile` anlegen
- [x] Frontend-Abhaengigkeiten ueber `npm ci` aus `package-lock.json` installieren
- [x] Frontend-Startkommando im Container definieren: `npm run dev -- --host 0.0.0.0 --port 5173`
- [x] Frontend-Env im Compose-Setup setzen: `VITE_API_BASE_URL=http://localhost:8000`
- [x] Root-`docker-compose.yml` mit Services `backend` und `frontend` anlegen
- [x] Ports mappen: Backend `8000:8000`, Frontend `5173:5173`
- [x] Bind Mounts fuer Development definieren: `./backend`, `./frontend` und `./data`
- [x] Bind Mounts auf Repo-Pfade begrenzen; keine Host-Home-, SSH-, Cloud- oder globalen Config-Verzeichnisse mounten
- [x] Container-interne Dependency-Ordner gegen Host-Konflikte schuetzen, z. B. eigene Volumes fuer `node_modules` und Python-Umgebung
- [x] Container als Non-Root-User ausfuehren und Dateirechte fuer gemountete Repo-Pfade pruefen
- [x] Secrets kontrollieren: keine Secrets ins Image kopieren, nur explizite Env-Dateien oder Docker-Secrets verwenden
- [x] `.env.example` fuer Container-Variablen aktualisieren, ohne echte Tokens oder lokale Pfade einzutragen
- [x] Allgemeines ausgehendes HTTPS fuer Dependency-Install und API-Nutzung erlauben
- [x] Zugriff auf private/interne Netzbereiche und Cloud-Metadata-IPs blockieren, z. B. `169.254.169.254`, RFC1918-Netze und lokale Host-Services, soweit fuer die App nicht noetig
- [x] `depends_on` fuer Frontend auf Backend ergaenzen
- [x] Optionalen Backend-Healthcheck fuer `GET /health` im Compose-File definieren
- [x] VS Code Dev Containers konfigurieren, z. B. `.devcontainer/devcontainer.json` mit Docker-Compose-Anbindung
- [x] Dev-Container-Workspace auf das Repo begrenzen und keine zusaetzlichen Host-Verzeichnisse automatisch mounten
- [x] Dev-Container-Extensions nur minimal fuer Python, Svelte/TypeScript und Docker definieren
- [x] `.dockerignore` fuer Root, Backend und Frontend pruefen oder anlegen
- [x] Docker Compose Start dokumentieren: `docker compose up --build`
- [x] Docker Compose Stop dokumentieren: `docker compose down`
- [x] Smoke-Test dokumentieren: `http://localhost:8000/health` und `http://localhost:5173` im Browser pruefen
- [x] Backend-Tests im Container dokumentieren: `docker compose run --rm backend uv run pytest`
- [x] Frontend-Check im Container dokumentieren: `docker compose run --rm frontend npm run check`
- [x] README um den Docker-Compose-Startweg ergaenzen, sobald die Container lauffaehig sind

## Naechster konkreter Schritt

- [x] Seed-Datenstruktur fuer `Birth of Hip-Hop` anlegen und mit den ersten Events befuellen
- [x] FastAPI-App-Struktur anlegen und Seed-Daten laden
- [x] Frontend-Grundstruktur auf SvelteKit migrieren und API-Client anbinden

## Frontend-Akzeptanzkriterien fuer den naechsten Slice

- [x] App startet lokal mit SvelteKit
- [x] Backend-Daten werden ueber die FastAPI-Endpunkte geladen
- [x] Karte zeigt Marker fuer `birth-of-hip-hop`
- [x] Timeline filtert sichtbare Events nach Zeitraum
- [x] Route Filter kann `Birth of Hip-Hop` ein- und ausblenden
- [x] Klick auf Marker oeffnet Eventdetails im Story Panel
- [x] Leere und fehlerhafte API-Zustaende sind sichtbar behandelt
