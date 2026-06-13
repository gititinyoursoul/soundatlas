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
- [x] Media-Enrichment-Konzept dokumentieren
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
- [x] Sichere Media-Enrichment-Settings mit externem Secret-Pfad einfuehren
- [x] Mockbare YouTube-Analyse-/Search-/Ranking-Pipeline fuer Content Pages umsetzen

## 4. Frontend

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

## 5. UX und Design

- [x] Erste Bildschirmaufteilung festlegen: Karte, Timeline, Side Panel
- [x] Farbcode pro Route definieren
- [x] Marker-Zustaende definieren: default, hover, selected
- [x] 1977 als dramaturgischen Fokus sichtbar machen
- [x] Mobile Layout grob pruefen
- [x] Quellen und Medienlinks im Story Panel darstellen
- [x] Verbindungen zwischen Events visuell oder textlich anzeigen
- [x] Frontend-Akzeptanzkriterien pruefen: Karte zeigt Hip-Hop-Events, Timeline filtert, Story Panel reagiert auf Markerauswahl

## 5.1 Bildmaterial

- [x] Konzept fuer Event-Bildmaterial dokumentieren
- [x] `image_links` im Event-Schema definieren
- [x] Seed-Validierungsregeln fuer Bildlinks dokumentieren
- [x] Bestehende Events mit leeren `image_links` initialisieren
- [x] Story Panel fuer reviewed Bildmaterial erweitern
- [x] Tests fuer Bildlink-Schema und Seed-Daten ergaenzen
- [x] Optionales Skript fuer automatische Bildkandidaten planen

## 6. Infrastruktur

- [x] Root-README fuer Projektstart anlegen
- [x] Backend-Startbefehl dokumentieren
- [x] Frontend-Startbefehl dokumentieren
- [x] Gemeinsame Entwicklungsbefehle definieren
- [ ] Entscheiden, ob ein Root-Task-Runner noetig ist
- [ ] Git-Status vor dem naechsten Commit pruefen

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
