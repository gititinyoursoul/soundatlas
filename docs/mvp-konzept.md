# SoundAtlas MVP-Konzept

## Arbeitstitel

**SoundAtlas: New York 1965-1985**

Eine interaktive Musikgeschichts-App, die zeigt, wie sich musikalische Szenen in New York räumlich, zeitlich und kulturell gegenseitig beeinflusst haben. Der dramaturgische Mittelpunkt ist New York um 1977, aber der MVP erklärt bewusst auch die Vorgeschichte und die spätere Entwicklung.

## Produktvision

SoundAtlas macht Musikgeschichte als erkundbare Karte mit Zeitstrahl erfahrbar. Nutzerinnen und Nutzer sehen nicht nur einzelne Ereignisse, sondern verstehen Zusammenhänge: Orte, Clubs, Communities, technische Entwicklungen, soziale Umstände und musikalische Einflüsse.

Der erste MVP konzentriert sich auf New York zwischen 1965 und 1985. Dieser Zeitraum ist klein genug für einen kuratierten Prototypen und dicht genug, um das zentrale Produktversprechen zu zeigen.

## Leitfrage

Wie wurde New York zwischen 1965 und 1985 zu einem musikalischen Knotenpunkt, und warum verdichtet sich diese Entwicklung um 1977?

## Zielgruppe

- Musikinteressierte, die Zusammenhänge zwischen Genres verstehen wollen
- Lehrende und Lernende im Bereich Musik, Kulturgeschichte und Stadtgeschichte
- Kulturjournalismus, Museen, Archive und kuratierte digitale Ausstellungen
- Nutzerinnen und Nutzer, die lieber explorativ als linear lernen

## MVP-Scope

Der MVP bildet fünf kuratierte Routen ab:

1. **Birth of Hip-Hop**
   - Zeitraum: ca. 1970-1985
   - Orte: Bronx, Harlem, Manhattan
   - Fokus: Soundsystem-Kultur, Funk-Breaks, Block Parties, DJing, MCing, Graffiti, frühe Rap-Platten

2. **Disco to Dance Music**
   - Zeitraum: ca. 1973-1985
   - Orte: Manhattan, Brooklyn, Queens
   - Fokus: Clubkultur, queere Räume, DJ-Technik, Extended Mixes, Paradise Garage, Post-Disco, Garage

3. **Punk & New Wave**
   - Zeitraum: ca. 1973-1982
   - Orte: Bowery, Lower East Side, Downtown Manhattan
   - Fokus: CBGB, DIY-Kultur, Punk, No Wave, New Wave, spätere Pop-Ästhetiken

4. **Salsa & Migration**
   - Zeitraum: ca. 1965-1980
   - Orte: Spanish Harlem, Bronx, Manhattan
   - Fokus: Puerto-ricanische und karibische Communities, Fania-Umfeld, Latin Music als transnationale Stadtkultur

5. **Downtown Experiment**
   - Zeitraum: ca. 1970-1985
   - Orte: SoHo, Lower East Side, Tribeca
   - Fokus: Loft Jazz, Minimalismus, Performance Art, No Wave, Club- und Kunstszene

## Nicht-Ziele im MVP

- Keine vollständige Musik-Enzyklopädie
- Keine globale Weltkarte im ersten Schritt
- Keine eigene Audio- oder Streaming-Infrastruktur
- Keine User-Accounts, Playlists oder Social Features
- Keine automatisierte Datenaggregation ohne redaktionelle Prüfung

## Kern-Erlebnis

Die erste Ansicht zeigt eine Karte von New York und einen Zeitstrahl von 1965 bis 1985. Nutzerinnen und Nutzer können eine Route auswählen, durch die Zeit navigieren und Ereignisse auf der Karte anklicken.

Beim Klick auf einen Punkt öffnet sich ein Story Panel mit:

- Titel und Jahr
- Ort und Szene
- kurzer erzählerischer Zusammenfassung
- Bedeutung für die Route
- Verbindungen zu früheren und späteren Ereignissen
- Quellenlinks
- optionalen Hörbeispielen als externe Links

## Hauptansichten

### Map View

Die Karte ist die primäre Oberfläche. Alle Events besitzen Koordinaten und sind farblich einer Route zugeordnet. Bei größeren Zeiträumen werden Events sichtbar, wenn ihr Zeitraum mit dem aktiven Timeline-Fenster überlappt.

Wichtige Funktionen:

- Marker pro Event
- Farben pro Route
- Hover- oder Klick-Zustand
- optional: Linien für direkte Einflüsse
- Fokus auf New York statt Weltkarte im MVP

### Timeline View

Der Zeitstrahl steuert, welche Ereignisse sichtbar sind. Für den MVP reicht ein Zeitraum-Slider mit Start- und Endjahr.

Wichtige Funktionen:

- Bereich 1965-1985
- Standardfenster: 1973-1980
- Hervorhebung von 1977 als Verdichtungsjahr
- Filterung der Kartenpunkte nach Zeitraum

### Story Panel

Das Story Panel erklärt ein ausgewähltes Event und macht Zusammenhänge sichtbar.

Wichtige Funktionen:

- Event-Zusammenfassung
- Abschnitt "Warum wichtig?"
- Quellen
- Medienlinks
- eingehende und ausgehende Verbindungen

### Route Filter

Nutzerinnen und Nutzer können eine oder mehrere Routen aktivieren. Im MVP sollte eine Route standardmäßig vorausgewählt sein, damit die erste Nutzung nicht leer oder unklar wirkt.

## Erster vertikaler Slice

Der erste vollständig umgesetzte Slice ist:

**Birth of Hip-Hop: Bronx 1970-1985**

Diese Route eignet sich gut, weil sie das Grundprinzip der App klar zeigt:

`Jamaican soundsystems -> Bronx DJ culture -> breakbeats -> block parties -> rap records -> film/radio/global spread`

Der Slice enthält:

- 8-12 kuratierte Events
- 5-8 Orte
- 8-12 Verbindungen
- Karte, Timeline, Route Filter und Story Panel
- Daten aus lokaler Seed-Datei oder SQLite

## Beispiel-Events für den ersten Slice

| Jahr | Ort | Titel | Route |
| --- | --- | --- | --- |
| ca. 1967-1972 | Bronx | Karibische Soundsystem-Einflüsse in New York | Birth of Hip-Hop |
| 1973 | 1520 Sedgwick Avenue | Kool Hercs Back-to-School Jam | Birth of Hip-Hop |
| 1974-1976 | Bronx Parks und Community Centers | Block Parties verbreiten DJ-Techniken | Birth of Hip-Hop |
| 1976-1977 | Bronx | Grandmaster Flash verfeinert DJ-Techniken | Birth of Hip-Hop |
| 1977 | New York City | Blackout als urbaner Einschnitt | Birth of Hip-Hop |
| 1979 | New York / New Jersey | Rapper's Delight macht Rap als Platte sichtbar | Birth of Hip-Hop |
| 1981 | Manhattan / Bronx | Hip-Hop erreicht Downtown Clubs und Kunstszene | Birth of Hip-Hop |
| 1982 | New York | Wild Style dokumentiert frühe Hip-Hop-Kultur | Birth of Hip-Hop |
| 1983-1984 | NYC / global | Hip-Hop verbreitet sich über Film, TV und Platten | Birth of Hip-Hop |

## Datenmodell

Der MVP sollte datengetrieben aufgebaut werden. Das Frontend rendert nur, was das Backend liefert.

### Route

```json
{
  "id": "birth-of-hip-hop",
  "title": "Birth of Hip-Hop",
  "color": "#e4572e",
  "year_start": 1970,
  "year_end": 1985,
  "summary": "How Bronx block parties, DJ techniques and urban culture shaped hip-hop."
}
```

### Place

```json
{
  "id": "1520-sedgwick-avenue",
  "name": "1520 Sedgwick Avenue",
  "borough": "Bronx",
  "latitude": 40.8459,
  "longitude": -73.9230,
  "summary": "Apartment building associated with an early Kool Herc party."
}
```

### Event

```json
{
  "id": "kool-herc-back-to-school-jam",
  "route_id": "birth-of-hip-hop",
  "place_id": "1520-sedgwick-avenue",
  "title": "Kool Herc's Back-to-School Jam",
  "year_start": 1973,
  "year_end": 1973,
  "summary": "A party often cited as a symbolic origin point for hip-hop culture.",
  "significance": "Shows how DJ practice, community space and youth culture converged in the Bronx.",
  "source_urls": [],
  "media_links": []
}
```

### Connection

```json
{
  "id": "soundsystems-to-kool-herc",
  "from_event_id": "caribbean-soundsystem-influences",
  "to_event_id": "kool-herc-back-to-school-jam",
  "type": "influence",
  "summary": "Connects Jamaican soundsystem practice with early Bronx DJ culture."
}
```

## Backend-Konzept

Technologie:

- Python
- `uv`
- FastAPI
- SQLite für den MVP
- später optional PostgreSQL/PostGIS

Geplante Struktur:

```text
backend/
  app/
    main.py
    api/
      routes.py
      events.py
      places.py
      connections.py
    models/
    repositories/
    schemas/
  pyproject.toml
  uv.lock
```

MVP-Endpunkte:

```text
GET /health
GET /routes
GET /events?from_year=1965&to_year=1985&route_id=birth-of-hip-hop
GET /events/{event_id}
GET /places
GET /connections?route_id=birth-of-hip-hop
```

Für den ersten Prototypen kann das Backend die Daten aus statischen JSON-Dateien laden. SQLite lohnt sich, sobald Bearbeitung, Imports, Quellenpflege oder komplexere Filter gebraucht werden.

## Frontend-Konzept

Technologie:

- SvelteKit
- Leaflet im MVP
- TypeScript empfohlen
- später optional MapLibre GL, falls Vektorkarten, Layer-Styling oder komplexere Karteninteraktionen wichtiger werden

Geplante Struktur:

```text
frontend/
  src/
    lib/
      api/
      components/
        MapView.svelte
        Timeline.svelte
        RouteFilter.svelte
        StoryPanel.svelte
      types/
    routes/
      +page.svelte
```

Frontend-State:

- aktive Route(n)
- aktiver Zeitraum
- ausgewähltes Event
- geladene Events, Places und Connections

## UX-Prinzipien

- Die Karte ist das Hauptprodukt, nicht ein Zusatz zur Timeline.
- 1977 wird als Knotenpunkt markiert, aber nicht isoliert.
- Jede Route braucht eine klare These, sonst wird sie zur Eventliste.
- Quellen und Unsicherheiten werden sichtbar gemacht.
- Audio ist Kontext, nicht Voraussetzung für die Nutzung.

## Content-Regeln

Jeder Event braucht mindestens:

- Jahr oder Zeitraum
- konkreten Ort oder begründete Region
- Route
- kurze Zusammenfassung
- Bedeutung innerhalb der Route
- mindestens eine Quelle vor Veröffentlichung

Für den internen MVP dürfen Quellen noch leer sein, aber das Datenmodell muss sie von Anfang an vorsehen.

## Erfolgsmaßstab für den MVP

Der MVP ist erfolgreich, wenn eine Nutzerin oder ein Nutzer innerhalb von 5 Minuten versteht:

- warum New York 1965-1985 musikalisch relevant ist
- wie mindestens eine Szene aus mehreren Einflüssen entstanden ist
- welche Orte, Personen und Technologien dabei eine Rolle gespielt haben
- wie sich die Entwicklung nach 1977 fortsetzt

## Umsetzungsplan

### Phase 1: Konzept und Daten

- dieses Konzept finalisieren
- Route "Birth of Hip-Hop" mit 8-12 Events ausarbeiten
- Orte und Koordinaten erfassen
- Quellenstruktur definieren

### Phase 2: Backend-Slice

- FastAPI-App strukturieren
- JSON-Seed-Daten anlegen
- Endpunkte für Routes, Events, Places und Connections bereitstellen
- einfache Validierung der Seed-Daten ergänzen

### Phase 3: Frontend-Slice

- SvelteKit-Grundstruktur prüfen oder initialisieren
- Leaflet-Karte einbauen
- Timeline-Filter bauen
- Story Panel anbinden
- Route Filter ergänzen

### Phase 4: Redaktionelle Erweiterung

- vier weitere Routen mit je 8-12 Events ergänzen
- Verbindungen zwischen Routen sichtbar machen
- Quellen vervollständigen
- erstes Review des Nutzerflusses durchführen

## Offene Entscheidungen

- Sollen Events eher punktgenau oder als Zeiträume erzählt werden?
- Soll der MVP mit statischen JSON-Dateien starten oder direkt SQLite nutzen?
- Wie streng müssen Quellen schon im ersten internen Prototypen sein?
- Welche Kartenbasis wird verwendet: OpenStreetMap-Tiles, MapLibre oder ein eigener Stil?
- Soll Audio zunächst nur als externer Link erscheinen oder direkt eingebettet werden?

## Nächster konkreter Schritt

Als nächstes sollte die Route **Birth of Hip-Hop** als Seed-Datensatz angelegt werden. Dafür reichen zunächst 8-12 Events, 5-8 Places und die wichtigsten Influence Connections. Danach kann der erste klickbare Prototyp gebaut werden.
