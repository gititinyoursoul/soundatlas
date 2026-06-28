import { describe, expect, it } from 'vitest';
import {
  getPlaceGeometriesForPlaceIds,
  nycPlaceGeometries,
  placeGeometryByPlaceId,
  placeGeometryColors,
  type PlaceGeometryFeature,
  type PlaceGeometryId
} from './nyc-place-geometries';

const expectedPlaceIds: PlaceGeometryId[] = ['south-bronx', 'cedar-park-bronx', 'east-harlem-el-barrio'];

function getCoordinates(feature: PlaceGeometryFeature): [number, number][] {
  return feature.geometry.coordinates.flat();
}

function getBounds(coordinates: [number, number][]): {
  minLatitude: number;
  maxLatitude: number;
  minLongitude: number;
  maxLongitude: number;
} {
  const longitudes = coordinates.map(([longitude]) => longitude);
  const latitudes = coordinates.map(([, latitude]) => latitude);

  return {
    minLatitude: Math.min(...latitudes),
    maxLatitude: Math.max(...latitudes),
    minLongitude: Math.min(...longitudes),
    maxLongitude: Math.max(...longitudes)
  };
}

describe('NYC place geometries', () => {
  it('defines contextual geometries for current MVP area and site places', () => {
    expect(nycPlaceGeometries.features.map((feature) => feature.properties.placeId)).toEqual(expectedPlaceIds);
  });

  it('keeps a color for every place geometry kind', () => {
    expect(Object.keys(placeGeometryColors).sort()).toEqual(['cultural_area', 'site']);
  });

  it('indexes place geometries by place id', () => {
    for (const placeId of expectedPlaceIds) {
      expect(placeGeometryByPlaceId.get(placeId)?.properties.placeId).toBe(placeId);
    }
  });

  it('uses closed polygon rings with enough detail to read as spatial areas', () => {
    for (const feature of nycPlaceGeometries.features) {
      for (const ring of feature.geometry.coordinates) {
        expect(ring.at(0)).toEqual(ring.at(-1));
        expect(ring.length).toBeGreaterThanOrEqual(10);
      }
    }
  });

  it('places labels inside each geometry bounding box', () => {
    for (const feature of nycPlaceGeometries.features) {
      const bounds = getBounds(getCoordinates(feature));
      const { latitude, longitude } = feature.properties.label;

      expect(latitude).toBeGreaterThanOrEqual(bounds.minLatitude);
      expect(latitude).toBeLessThanOrEqual(bounds.maxLatitude);
      expect(longitude).toBeGreaterThanOrEqual(bounds.minLongitude);
      expect(longitude).toBeLessThanOrEqual(bounds.maxLongitude);
    }
  });

  it('marks cultural areas as interpretive and site geometry as site precision', () => {
    expect(placeGeometryByPlaceId.get('south-bronx')?.properties.precision).toBe('interpretive');
    expect(placeGeometryByPlaceId.get('east-harlem-el-barrio')?.properties.precision).toBe(
      'interpretive'
    );
    expect(placeGeometryByPlaceId.get('cedar-park-bronx')?.properties.precision).toBe('site');
  });

  it('returns visible geometries in first-seen place order without duplicates', () => {
    expect(
      getPlaceGeometriesForPlaceIds([
        'missing-place',
        'south-bronx',
        'cedar-park-bronx',
        'south-bronx',
        'east-harlem-el-barrio'
      ]).map((feature) => feature.properties.placeId)
    ).toEqual(['south-bronx', 'cedar-park-bronx', 'east-harlem-el-barrio']);
  });
});
