import { describe, expect, it } from 'vitest';
import { boroughColors, nycBoroughs, type BoroughName } from './nyc-boroughs';

const expectedBoroughs: BoroughName[] = ['Bronx', 'Manhattan', 'Brooklyn', 'Queens', 'Staten Island'];

function getOuterRing(boroughName: BoroughName): [number, number][] {
  const borough = nycBoroughs.features.find((feature) => feature.properties.name === boroughName);

  if (!borough) {
    throw new Error(`Missing borough: ${boroughName}`);
  }

  return borough.geometry.coordinates[0];
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

describe('NYC borough map data', () => {
  it('exposes exactly the five NYC boroughs', () => {
    expect(nycBoroughs.features.map((feature) => feature.properties.name)).toEqual(expectedBoroughs);
  });

  it('defines one unique color for every borough', () => {
    expect(Object.keys(boroughColors).sort()).toEqual([...expectedBoroughs].sort());
    expect(new Set(Object.values(boroughColors)).size).toBe(expectedBoroughs.length);
  });

  it('defines label coordinates for every borough', () => {
    for (const feature of nycBoroughs.features) {
      expect(Number.isFinite(feature.properties.label.latitude)).toBe(true);
      expect(Number.isFinite(feature.properties.label.longitude)).toBe(true);
    }
  });

  it('uses closed polygon rings for every borough', () => {
    for (const boroughName of expectedBoroughs) {
      const coordinates = getOuterRing(boroughName);

      expect(coordinates.at(0)).toEqual(coordinates.at(-1));
    }
  });

  it('keeps borough shapes more detailed than simple boxes', () => {
    for (const boroughName of expectedBoroughs) {
      const coordinates = getOuterRing(boroughName);

      expect(coordinates.length).toBeGreaterThanOrEqual(9);
    }
  });

  it('places borough labels inside each polygon bounding box', () => {
    for (const feature of nycBoroughs.features) {
      const bounds = getBounds(feature.geometry.coordinates[0]);
      const { latitude, longitude } = feature.properties.label;

      expect(latitude).toBeGreaterThanOrEqual(bounds.minLatitude);
      expect(latitude).toBeLessThanOrEqual(bounds.maxLatitude);
      expect(longitude).toBeGreaterThanOrEqual(bounds.minLongitude);
      expect(longitude).toBeLessThanOrEqual(bounds.maxLongitude);
    }
  });

  it('keeps all borough features as GeoJSON polygons', () => {
    expect(nycBoroughs.type).toBe('FeatureCollection');

    for (const feature of nycBoroughs.features) {
      expect(feature.type).toBe('Feature');
      expect(feature.geometry.type).toBe('Polygon');
      expect(feature.geometry.coordinates).toHaveLength(1);
    }
  });
});
