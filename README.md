# SoundAtlas

Explore New York's music history through places, events, and narrative routes, with a focus on 1965–1985.

Explore the live site at [gititinyoursoul.github.io/soundatlas](https://gititinyoursoul.github.io/soundatlas/).

SoundAtlas connects a map and timeline with stories about the communities, venues, DJs, musicians, and record networks that shaped the city's music. Event details include historical context, sources, and media where available.

## Explore

- Choose a route to follow a musical scene through time and across the city.
- Select events on the map or timeline to read their stories.
- Explore the places associated with an event and follow its source and media links.
- Move between events with the previous/next controls or left/right arrow keys.

The current dataset contains **6 routes, 67 events, and 39 places**:

| Route | Events |
| --- | ---: |
| Birth of Hip-Hop | 12 |
| Disco To Dance Music | 12 |
| New York Builds the Dance Floor | 7 |
| Punk & New Wave Downtown | 12 |
| Salsa & Latin New York | 12 |
| Downtown Experiment / No Wave / Loft Jazz | 12 |

## What this repository contains

This repository holds a generated static site: a compiled SvelteKit frontend and exported JSON data. It can be served directly by a static web server. The application source, package manifest, backend, and build scripts are not included in this checkout.

```text
index.html                         Site entry point
_app/                              Generated JavaScript, CSS, and version metadata
soundatlas-data/
  routes.json                      Route descriptions, date ranges, tags, and sources
  places.json                      Places, coordinates, geometry, and sources
  events.json                      Events, place references, stories, and media
  route-navigation.json            Route metadata and navigation/publication flags
.nojekyll                          Disables Jekyll processing on GitHub Pages
```

The public explorer reads the JSON files directly and does not require a backend. Editorial and publication API helpers remain in the bundle, but their controls are disabled in this static build.

## Preview locally

The generated site expects to be hosted at **`/soundatlas/`**. Serve the directory containing this checkout so that its folder name supplies that URL path.

With Python 3 installed, run this from the repository root, assuming the checkout directory is named `soundatlas`:

```sh
python -m http.server 8080 --bind 127.0.0.1 --directory ..
```

Open <http://127.0.0.1:8080/soundatlas/>. Stop the server with `Ctrl+C`.

If the checkout has a different name, place it under a static server's `soundatlas` path. Opening `index.html` directly or serving this checkout at `/` will not match the generated asset paths.

Map tiles are requested from OpenStreetMap, and some media uses external services such as YouTube. Those features need an internet connection.

## Working with the data

Each data file exposes a top-level collection (`routes`, `places`, or `events`). The route, place, and event exports also include `_meta` information.

- Routes define an `id`, title, summary, thesis, date range, and source URLs.
- Places define an `id`, name, coordinates, and optional geometry with provenance fields.
- Events link to a route through `route_id` and to places through `place_ids` and `default_place_id`. They also retain a `place_id` field.
- Navigation entries contain a nested route object and flags such as `appears_in_routes` and `appears_in_published_routes`.

Durable changes to this README and the data are maintained in the private source project and delivered by regenerating the checked site. Direct edits in this generated repository may be overwritten by the next publication.

Source updates preserve stable IDs and valid references, keep duplicated route metadata in `route-navigation.json` consistent with `routes.json`, and validate the JSON and affected route, event, and map location. Hashed files in `_app/immutable/` are regenerated through the original build process.

## Content and attribution

All current route, place, and event records have `content_review_status: "draft"`. Some routes identify an AI model as their creator. Treat the dataset as work in progress and consult the linked sources when assessing historical claims.

Publication flags and editorial review status are separate: the navigation export marks “New York Builds the Dance Floor” as appearing in published routes, while its route record remains marked as draft.

Some geographic outlines are interpretive cultural areas. Check each place's geometry precision, provenance, and license fields before reuse. Source URLs and media links point to third-party material; their inclusion does not grant reuse rights.

This checkout does not include a repository-wide license file. Confirm licensing before redistributing code or data.
