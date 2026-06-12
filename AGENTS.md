# AGENTS.md

## Scope

Diese Anweisungen gelten fuer das gesamte Repository.

## Projektkontext

SoundAtlas ist ein MVP fuer eine interaktive Musikgeschichts-App. Der erste Produkt-Scope ist **New York 1965-1985** mit dem vertikalen Slice **Birth of Hip-Hop: Bronx 1970-1985**.

Die App soll Musikgeschichte ueber drei Achsen erfahrbar machen:

- Ort: Karte und Places
- Zeit: Timeline und Zeitraeume
- Klang/Kultur: Events, Routen, Verbindungen und Quellen

## Technischer Stack

- Frontend: SvelteKit, TypeScript, Leaflet
- Backend: Python, `uv`, FastAPI
- Daten im MVP: kuratierte JSON-Seed-Dateien unter `data/seed/`
- Spaeter optional: SQLite oder PostgreSQL/PostGIS

## Arbeitsprinzipien

- Halte Aenderungen klein, nachvollziehbar und am MVP-Scope orientiert.
- Baue zuerst den vertikalen Slice sauber, bevor weitere Routen erweitert werden.
- Bevorzuge kuratierte, nachvollziehbare Daten gegenueber automatischer Aggregation.
- Quellenfelder im Datenmodell immer vorsehen, auch wenn sie im internen MVP noch leer sind.
- Keine Audio-Dateien ins Repo legen; im MVP nur externe Medienlinks verwenden.
- Keine Secrets, Tokens oder lokalen Pfade committen.

## Datenregeln

Seed-Daten liegen unter `data/seed/` und sollten stabil strukturiert bleiben:

- `routes.json`: narrative Routen
- `places.json`: Orte mit Koordinaten
- `events.json`: historische Ereignisse
- `connections.json`: Einfluesse und Verbindungen zwischen Events

IDs sollten klein geschrieben, stabil und URL-tauglich sein, z. B. `birth-of-hip-hop` oder `1520-sedgwick-avenue`.

Events sollten mindestens enthalten:

- `id`
- `route_id`
- `place_id`
- `title`
- `year_start`
- `year_end`
- `summary`
- `significance`
- `source_urls`
- `media_links`

## Backend-Regeln

- FastAPI-Code gehoert perspektivisch unter `backend/app/`.
- API-Responses sollen ueber Pydantic-Schemas typisiert werden.
- Endpunkte sollen datengetrieben aus den Seed-Dateien lesen, bis eine Datenbank eingefuehrt wird.
- Tests, wenn vorhanden, mit `uv run pytest` ausfuehren.

## Frontend-Regeln

- UI-Komponenten sollen klein und fachlich benannt sein, z. B. `MapView`, `Timeline`, `RouteFilter`, `StoryPanel`.
- Die Karte ist die primaere Oberflaeche des MVP.
- Timeline, Route-Filter und Story Panel sollen denselben zentralen Datenzustand verwenden.
- Keine UI bauen, die nur mit Mock-Daten funktioniert, wenn Seed-Daten bereits existieren.

## Dokumentation

- Produkt- und Architekturentscheidungen in `docs/` dokumentieren.
- Die aktuelle Aufgabenliste liegt in `TODO.md`.
- Wenn sich der Scope aendert, zuerst `docs/mvp-konzept.md` und danach `TODO.md` aktualisieren.

## Git-Konventionen

- Keine Commits ohne expliziten Nutzerauftrag.
- Sinnvolle Commit-Gruppen bevorzugen: Doku, Daten, Backend, Frontend getrennt.
- Lokale Ordner wie `.venv/`, `node_modules/`, `.vscode/` und `.github/` bleiben ignoriert.

## Commit Messages

- Verwende Conventional Commits: `type(scope): subject`
- Erlaubte Typen: `feat`, `fix`, `refactor`, `perf`, `test`, `docs`, `build`, `ci`, `chore`, `revert`
- Der Scope ist empfohlen, aber optional; falls verwendet, kurz und stabil halten
- Subjekte im Imperativ formulieren und moeglichst unter 72 Zeichen halten
- Keine abschliessenden Punkte im Subject
- Bei Breaking Changes `!` verwenden, z. B. `feat(api)!: remove legacy endpoint`
- Einen kurzen Body ergaenzen, wenn der Grund nicht klar ist

## Working Defaults

- Bevorzuge kleine, reviewbare Aenderungen statt grosser Spruenge
- Wenn Frontend-Code geaendert wird, `npm run check` und bei grösseren Aenderungen `npm run build` ausfuehren
- Wenn Backend-Code geaendert wird, `uv run pytest` ausfuehren
- Wenn Daten oder Seed-Dateien geaendert werden, die JSON-Struktur und Referenzen pruefen
- Wenn neue Arbeitspakete entstehen, `TODO.md` aktualisieren
