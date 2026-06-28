export type PlaceGeometryId = 'south-bronx' | 'cedar-park-bronx' | 'east-harlem-el-barrio';

export type PlaceGeometryKind = 'cultural_area' | 'site';
export type PlaceGeometryPrecision = 'interpretive' | 'site';
export type PlaceGeometrySource = 'curated' | 'openstreetmap';
export type PlaceGeometryRing = [number, number][];

export type PlaceGeometryFeature = {
  type: 'Feature';
  properties: {
    placeId: PlaceGeometryId;
    name: string;
    kind: PlaceGeometryKind;
    precision: PlaceGeometryPrecision;
    source: PlaceGeometrySource;
    sourceNote: string;
    label: {
      latitude: number;
      longitude: number;
    };
  };
  geometry: {
    type: 'Polygon';
    coordinates: PlaceGeometryRing[];
  };
};

export type PlaceGeometryFeatureCollection = {
  type: 'FeatureCollection';
  features: PlaceGeometryFeature[];
};

// These contextual place geometries are intentionally separate from event points.
// Cedar Park uses OpenStreetMap polygon output fetched through Nominatim on 2026-06-28.
// South Bronx and East Harlem are curated cultural-area polygons because OSM exposes
// them as neighborhood points rather than stable administrative boundaries.
export const nycPlaceGeometries: PlaceGeometryFeatureCollection = {
  type: 'FeatureCollection',
  features: [
    {
      type: 'Feature',
      properties: {
        placeId: 'south-bronx',
        name: 'South Bronx',
        kind: 'cultural_area',
        precision: 'interpretive',
        source: 'curated',
        sourceNote: 'Curated cultural-area outline, not an administrative boundary.',
        label: {
          latitude: 40.8176,
          longitude: -73.9182
        }
      },
      geometry: {
        type: 'Polygon',
        coordinates: [
          [
            [-73.9339, 40.7857],
            [-73.9306, 40.8045],
            [-73.9251, 40.826],
            [-73.9134, 40.846],
            [-73.8935, 40.8532],
            [-73.8664, 40.8484],
            [-73.8468, 40.829],
            [-73.8504, 40.8004],
            [-73.8736, 40.786],
            [-73.9008, 40.7902],
            [-73.9339, 40.7857]
          ]
        ]
      }
    },
    {
      type: 'Feature',
      properties: {
        placeId: 'cedar-park-bronx',
        name: 'Cedar Park',
        kind: 'site',
        precision: 'site',
        source: 'openstreetmap',
        sourceNote:
          'OpenStreetMap way 1105528044, Cedar Playground, ODbL 1.0: https://www.openstreetmap.org/copyright',
        label: {
          latitude: 40.855108,
          longitude: -73.91741
        }
      },
      geometry: {
        type: 'Polygon',
        coordinates: [
          [
            [-73.91813, 40.854744],
            [-73.917742, 40.854651],
            [-73.917643, 40.854754],
            [-73.917447, 40.854739],
            [-73.917084, 40.854648],
            [-73.916995, 40.854792],
            [-73.917013, 40.854834],
            [-73.91716, 40.854888],
            [-73.916893, 40.855328],
            [-73.916846, 40.85544],
            [-73.916832, 40.85552],
            [-73.916857, 40.85559],
            [-73.916933, 40.85568],
            [-73.91709, 40.855754],
            [-73.91721, 40.855739],
            [-73.91813, 40.854744]
          ]
        ]
      }
    },
    {
      type: 'Feature',
      properties: {
        placeId: 'east-harlem-el-barrio',
        name: 'East Harlem / El Barrio',
        kind: 'cultural_area',
        precision: 'interpretive',
        source: 'curated',
        sourceNote: 'Curated cultural-area outline, not an administrative boundary.',
        label: {
          latitude: 40.7947,
          longitude: -73.9425
        }
      },
      geometry: {
        type: 'Polygon',
        coordinates: [
          [
            [-73.957, 40.7847],
            [-73.952, 40.795],
            [-73.947, 40.807],
            [-73.939, 40.82],
            [-73.929, 40.819],
            [-73.925, 40.811],
            [-73.93, 40.799],
            [-73.936, 40.789],
            [-73.945, 40.784],
            [-73.957, 40.7847]
          ]
        ]
      }
    }
  ]
};

export const placeGeometryColors: Record<PlaceGeometryKind, string> = {
  cultural_area: '#8f7353',
  site: '#3b9468'
};

export const placeGeometryByPlaceId = new Map(
  nycPlaceGeometries.features.map((feature) => [feature.properties.placeId, feature])
);

export function getPlaceGeometriesForPlaceIds(placeIds: string[]): PlaceGeometryFeature[] {
  const seenPlaceIds = new Set<string>();
  const placeGeometries: PlaceGeometryFeature[] = [];

  for (const placeId of placeIds) {
    if (seenPlaceIds.has(placeId)) {
      continue;
    }

    seenPlaceIds.add(placeId);

    const geometry = placeGeometryByPlaceId.get(placeId as PlaceGeometryId);

    if (geometry) {
      placeGeometries.push(geometry);
    }
  }

  return placeGeometries;
}
