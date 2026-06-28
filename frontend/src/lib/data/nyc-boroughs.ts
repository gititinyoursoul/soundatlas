export type BoroughName = 'Bronx' | 'Manhattan' | 'Brooklyn' | 'Queens' | 'Staten Island';

export type BoroughFeature = {
  type: 'Feature';
  properties: {
    name: BoroughName;
    label: {
      latitude: number;
      longitude: number;
    };
  };
  geometry: {
    type: 'Polygon';
    coordinates: [number, number][][];
  };
};

export type BoroughFeatureCollection = {
  type: 'FeatureCollection';
  features: BoroughFeature[];
};

// Lightweight visual borough regions for the map design spike. These are simplified
// contextual polygons, not survey-grade administrative boundaries.
export const nycBoroughs: BoroughFeatureCollection = {
  type: 'FeatureCollection',
  features: [
    {
      type: 'Feature',
      properties: {
        name: 'Bronx',
        label: {
          latitude: 40.85,
          longitude: -73.865
        }
      },
      geometry: {
        type: 'Polygon',
        coordinates: [
          [
            [-73.933, 40.785],
            [-73.924, 40.827],
            [-73.927, 40.872],
            [-73.897, 40.911],
            [-73.832, 40.905],
            [-73.785, 40.889],
            [-73.765, 40.856],
            [-73.772, 40.815],
            [-73.815, 40.793],
            [-73.872, 40.785],
            [-73.933, 40.785]
          ]
        ]
      }
    },
    {
      type: 'Feature',
      properties: {
        name: 'Manhattan',
        label: {
          latitude: 40.77,
          longitude: -73.965
        }
      },
      geometry: {
        type: 'Polygon',
        coordinates: [
          [
            [-74.019, 40.701],
            [-74.012, 40.735],
            [-73.999, 40.772],
            [-73.976, 40.82],
            [-73.943, 40.872],
            [-73.921, 40.879],
            [-73.909, 40.863],
            [-73.931, 40.799],
            [-73.951, 40.75],
            [-73.972, 40.706],
            [-74.006, 40.696],
            [-74.019, 40.701]
          ]
        ]
      }
    },
    {
      type: 'Feature',
      properties: {
        name: 'Brooklyn',
        label: {
          latitude: 40.65,
          longitude: -73.95
        }
      },
      geometry: {
        type: 'Polygon',
        coordinates: [
          [
            [-74.041, 40.571],
            [-74.034, 40.626],
            [-74.017, 40.682],
            [-73.962, 40.728],
            [-73.908, 40.735],
            [-73.855, 40.708],
            [-73.845, 40.647],
            [-73.861, 40.591],
            [-73.916, 40.565],
            [-73.983, 40.552],
            [-74.041, 40.571]
          ]
        ]
      }
    },
    {
      type: 'Feature',
      properties: {
        name: 'Queens',
        label: {
          latitude: 40.7,
          longitude: -73.815
        }
      },
      geometry: {
        type: 'Polygon',
        coordinates: [
          [
            [-73.949, 40.545],
            [-73.931, 40.609],
            [-73.911, 40.682],
            [-73.866, 40.737],
            [-73.804, 40.789],
            [-73.739, 40.786],
            [-73.702, 40.735],
            [-73.702, 40.627],
            [-73.735, 40.555],
            [-73.829, 40.535],
            [-73.949, 40.545]
          ]
        ]
      }
    },
    {
      type: 'Feature',
      properties: {
        name: 'Staten Island',
        label: {
          latitude: 40.575,
          longitude: -74.155
        }
      },
      geometry: {
        type: 'Polygon',
        coordinates: [
          [
            [-74.251, 40.506],
            [-74.229, 40.59],
            [-74.161, 40.646],
            [-74.082, 40.629],
            [-74.055, 40.563],
            [-74.07, 40.502],
            [-74.141, 40.47],
            [-74.218, 40.467],
            [-74.251, 40.506]
          ]
        ]
      }
    }
  ]
};

export const boroughColors: Record<BoroughName, string> = {
  Bronx: '#c85c3a',
  Manhattan: '#4e7fa7',
  Brooklyn: '#4f9a73',
  Queens: '#d4a62f',
  'Staten Island': '#8a6faf'
};
