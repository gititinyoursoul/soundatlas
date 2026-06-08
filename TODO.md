# SoundAtlas TODO

## Aktueller Fokus

Ziel des ersten MVP ist ein vertikaler Slice fuer **Birth of Hip-Hop: Bronx 1970-1985**. Dieser Slice soll Karte, Timeline, Story Panel, Route Filter und Backend-Datenfluss einmal vollstaendig demonstrieren.

## 1. Produkt und Content

- [x] Leitfrage fuer den MVP finalisieren
- [x] Route `Birth of Hip-Hop` redaktionell ausarbeiten
- [x] 8-12 Events fuer die Hip-Hop-Route definieren
- [x] 5-8 Places mit Koordinaten erfassen
- [x] 8-12 Influence Connections definieren
- [x] Quellenstruktur fuer Events festlegen
- [x] Medienlink-Regeln klaeren: YouTube, Spotify, Internet Archive oder externe Links
- [x] Offene historische Unsicherheiten markieren

## 2. Seed-Daten

- [x] Datenformat fuer Routes, Events, Places und Connections festlegen
- [x] `data/seed/routes.json` anlegen
- [x] `data/seed/places.json` anlegen
- [x] `data/seed/events.json` anlegen
- [x] `data/seed/connections.json` anlegen
- [x] Beispiel-Daten fuer `Birth of Hip-Hop` eintragen
- [x] Einfache Validierung fuer Pflichtfelder definieren
- [x] Quellen- und Medienlinks als Arrays modellieren

## 3. Backend

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

## 4. Frontend

- [ ] SvelteKit-Grundstruktur initialisieren oder bestehendes Frontend migrieren
- [ ] TypeScript aktivieren
- [ ] Leaflet sauber in Svelte einbinden
- [ ] `MapView`-Komponente erstellen
- [ ] `Timeline`-Komponente erstellen
- [ ] `RouteFilter`-Komponente erstellen
- [ ] `StoryPanel`-Komponente erstellen
- [ ] API-Client fuer Backend-Endpunkte bauen
- [ ] Event-Marker nach aktivem Zeitraum filtern
- [ ] Route-Farben konsistent darstellen
- [ ] Leeren Zustand anzeigen, wenn keine Events sichtbar sind

## 5. UX und Design

- [ ] Erste Bildschirmaufteilung festlegen: Karte, Timeline, Side Panel
- [ ] Farbcode pro Route definieren
- [ ] Marker-Zustaende definieren: default, hover, selected
- [ ] 1977 als dramaturgischen Fokus sichtbar machen
- [ ] Mobile Layout grob pruefen
- [ ] Quellen und Medienlinks im Story Panel darstellen
- [ ] Verbindungen zwischen Events visuell oder textlich anzeigen

## 6. Infrastruktur

- [ ] Root-README fuer Projektstart anlegen
- [ ] Backend-Startbefehl dokumentieren
- [ ] Frontend-Startbefehl dokumentieren
- [ ] Gemeinsame Entwicklungsbefehle definieren
- [ ] Entscheiden, ob ein Root-Task-Runner noetig ist
- [ ] Git-Status vor dem naechsten Commit pruefen

## Naechster konkreter Schritt

- [x] Seed-Datenstruktur fuer `Birth of Hip-Hop` anlegen und mit den ersten Events befuellen
- [x] FastAPI-App-Struktur anlegen und Seed-Daten laden
- [ ] Frontend-Grundstruktur auf SvelteKit migrieren und API-Client anbinden
