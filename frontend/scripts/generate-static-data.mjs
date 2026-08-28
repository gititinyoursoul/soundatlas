import { copyFile, mkdir, readFile, writeFile } from 'node:fs/promises';
import path from 'node:path';
import { fileURLToPath } from 'node:url';

const scriptDir = path.dirname(fileURLToPath(import.meta.url));
const repoRoot = path.resolve(scriptDir, '..', '..');
const sourceDir = path.join(repoRoot, 'data', 'seed');
const contentDir = path.join(repoRoot, 'docs', 'content', 'routes');
const targetDir = path.join(repoRoot, 'frontend', 'static', 'soundatlas-data');
const seedFiles = [
  'routes.json',
  'places.json',
  'events.json',
  'connections.json'
];

await mkdir(targetDir, { recursive: true });

await Promise.all(
  seedFiles.map((fileName) =>
    copyFile(path.join(sourceDir, fileName), path.join(targetDir, fileName))
  )
);

const routesDocument = JSON.parse(
  await readFile(path.join(sourceDir, 'routes.json'), 'utf8')
);
const entries = await Promise.all(
  routesDocument.routes.map(async (route) => {
    const readArtifact = async (name) => {
      try {
        return JSON.parse(
          await readFile(path.join(contentDir, route.id, name), 'utf8')
        );
      } catch {
        return null;
      }
    };
    const [review, publication] = await Promise.all([
      readArtifact('route-review.json'),
      readArtifact('route-publication.json')
    ]);
    const review_revision_id = review?.revision_id ?? null;
    const published_revision_id = publication?.revision_id ?? null;
    return {
      route,
      review_revision_id,
      published_revision_id,
      appears_in_routes: true,
      appears_in_published_routes: published_revision_id !== null,
      appears_in_routes_to_review:
        review_revision_id !== null &&
        review_revision_id !== published_revision_id
    };
  })
);

const publishedRouteIds = new Set(
  entries
    .filter((entry) => entry.appears_in_routes)
    .map((entry) => entry.route.id)
);
const eventsDocument = JSON.parse(
  await readFile(path.join(sourceDir, 'events.json'), 'utf8')
);
const publishedEvents = eventsDocument.events.filter((event) =>
  publishedRouteIds.has(event.route_id)
);
const publishedPlaceIds = new Set(
  publishedEvents.flatMap((event) => event.place_ids)
);
const placesDocument = JSON.parse(
  await readFile(path.join(sourceDir, 'places.json'), 'utf8')
);
const connectionsDocument = JSON.parse(
  await readFile(path.join(sourceDir, 'connections.json'), 'utf8')
);
const publishedEventIds = new Set(publishedEvents.map((event) => event.id));

await Promise.all([
  writeFile(
    path.join(targetDir, 'route-navigation.json'),
    JSON.stringify({ routes: entries }, null, 2)
  ),
  writeFile(
    path.join(targetDir, 'routes.json'),
    JSON.stringify(
      {
        ...routesDocument,
        routes: routesDocument.routes.filter((route) =>
          publishedRouteIds.has(route.id)
        )
      },
      null,
      2
    )
  ),
  writeFile(
    path.join(targetDir, 'events.json'),
    JSON.stringify({ ...eventsDocument, events: publishedEvents }, null, 2)
  ),
  writeFile(
    path.join(targetDir, 'places.json'),
    JSON.stringify(
      {
        ...placesDocument,
        places: placesDocument.places.filter((place) =>
          publishedPlaceIds.has(place.id)
        )
      },
      null,
      2
    )
  ),
  writeFile(
    path.join(targetDir, 'connections.json'),
    JSON.stringify(
      {
        ...connectionsDocument,
        connections: connectionsDocument.connections.filter(
          (connection) =>
            publishedEventIds.has(connection.from_event_id) &&
            publishedEventIds.has(connection.to_event_id)
        )
      },
      null,
      2
    )
  )
]);

console.log(
  `Generated static SoundAtlas data in ${path.relative(repoRoot, targetDir)}`
);
