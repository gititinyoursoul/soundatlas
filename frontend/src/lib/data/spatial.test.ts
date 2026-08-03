import { describe, expect, it } from 'vitest';
import { makeEvent, makePlace } from '$lib/test/fixtures';
import {
  formatRelationshipDirection,
  getEventPlaces,
  normalizeEvent,
  resolveFocusedPlaceId,
  resolvePlaceSelection
} from './spatial';

describe('spatial event helpers', () => {
  it('normalizes legacy single-place events', () => {
    const canonical = makeEvent({ id: 'legacy' });

    expect(
      normalizeEvent({
        ...canonical,
        place_ids: undefined,
        default_place_id: undefined,
        place_relationships: undefined
      })
    ).toMatchObject({
      place_id: '1520-sedgwick-avenue',
      place_ids: ['1520-sedgwick-avenue'],
      default_place_id: '1520-sedgwick-avenue',
      place_relationships: []
    });
  });

  it('preserves a valid focus and otherwise uses the default place', () => {
    const event = makeEvent({
      id: 'multi',
      place_id: 'place-a',
      place_ids: ['place-a', 'place-b'],
      default_place_id: 'place-a'
    });

    expect(resolveFocusedPlaceId(event, 'place-b')).toBe('place-b');
    expect(resolveFocusedPlaceId(event, 'other')).toBe('place-a');
  });

  it('resolves event places in editorial order', () => {
    const event = makeEvent({
      id: 'multi',
      place_id: 'place-b',
      place_ids: ['place-b', 'place-a'],
      default_place_id: 'place-b'
    });
    const places = [makePlace({ id: 'place-a' }), makePlace({ id: 'place-b' })];

    expect(getEventPlaces(event, places).map((place) => place.id)).toEqual([
      'place-b',
      'place-a'
    ]);
  });

  it('preserves an applicable selected event for shared geography', () => {
    const events = [
      makeEvent({ id: 'first', place_id: 'shared' }),
      makeEvent({ id: 'second', place_id: 'shared' })
    ];

    expect(resolvePlaceSelection(events, 'second', 'shared')).toEqual({
      placeId: 'shared',
      eventId: 'second',
      eventIds: ['second'],
      needsChoice: false
    });
  });

  it('selects a sole event and requires a choice for several events', () => {
    const single = [makeEvent({ id: 'only', place_id: 'place-a' })];
    expect(resolvePlaceSelection(single, null, 'place-a').eventId).toBe('only');

    const shared = [
      makeEvent({ id: 'first', place_id: 'shared' }),
      makeEvent({ id: 'second', place_id: 'shared' })
    ];
    expect(resolvePlaceSelection(shared, null, 'shared')).toEqual({
      placeId: 'shared',
      eventId: null,
      eventIds: ['first', 'second'],
      needsChoice: true
    });
  });

  it('formats every relationship direction as text', () => {
    const places = new Map([
      ['place-a', makePlace({ id: 'place-a', name: 'The Bronx' })],
      ['place-b', makePlace({ id: 'place-b', name: 'Downtown' })]
    ]);
    const base = {
      from_place_id: 'place-a',
      to_place_id: 'place-b',
      context_label: 'Context',
      source_urls: ['https://example.org']
    };

    expect(
      formatRelationshipDirection(
        { ...base, directionality: 'undirected' },
        places
      )
    ).toBe('Connection between The Bronx and Downtown');
    expect(
      formatRelationshipDirection({ ...base, directionality: 'forward' }, places)
    ).toBe('From The Bronx toward Downtown');
    expect(
      formatRelationshipDirection(
        { ...base, directionality: 'reciprocal' },
        places
      )
    ).toBe('Exchange between The Bronx and Downtown');
  });

  it.each([
    ['one point', ['point-a'], 1, 0],
    ['one area', ['area-a'], 0, 1],
    ['multiple points', ['point-a', 'point-b'], 2, 0],
    ['multiple areas', ['area-a', 'area-b'], 0, 2],
    ['mixed', ['point-a', 'area-a'], 1, 1]
  ])(
    'resolves the %s footprint without merging places',
    (_label, placeIds, pointCount, areaCount) => {
      const pointA = makePlace({ id: 'point-a' });
      const pointB = makePlace({ id: 'point-b' });
      const makeArea = (id: string) =>
        makePlace({
          id,
          geometry: {
            type: 'Polygon',
            coordinates: [
              [
                [-73.94, 40.81],
                [-73.93, 40.81],
                [-73.93, 40.82],
                [-73.94, 40.81]
              ]
            ]
          },
          geometry_precision: 'interpretive',
          geometry_source_type: 'curated',
          geometry_source_note: 'Fixture'
        });
      const places = [pointA, pointB, makeArea('area-a'), makeArea('area-b')];
      const event = makeEvent({
        id: 'footprint',
        place_id: placeIds[0],
        place_ids: placeIds,
        default_place_id: placeIds[0]
      });
      const resolved = getEventPlaces(event, places);

      expect(resolved).toHaveLength(placeIds.length);
      expect(resolved.filter((place) => !place.geometry)).toHaveLength(
        pointCount
      );
      expect(resolved.filter((place) => place.geometry)).toHaveLength(
        areaCount
      );
    }
  );
});
