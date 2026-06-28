import { describe, expect, it } from 'vitest';
import { makeEvent, makePlace, makeRoute } from '$lib/test/fixtures';
import {
  getEventMarkerPlacements,
  getMarkerOptions,
  getMarkerPosition,
  getVisibleRoutes,
  groupEventsByPlaceId
} from './map-utils';

describe('map utils', () => {
  it('returns only routes that have visible events', () => {
    const routes = [
      makeRoute({ id: 'birth-of-hip-hop' }),
      makeRoute({ id: 'downtown-experiment', title: 'Downtown Experiment' })
    ];
    const events = [makeEvent({ id: 'early-event', route_id: 'birth-of-hip-hop' })];

    expect(getVisibleRoutes(routes, events).map((route) => route.id)).toEqual(['birth-of-hip-hop']);
  });

  it('groups colocated events by place in insertion order', () => {
    const events = [
      makeEvent({ id: 'first', place_id: 'same-place' }),
      makeEvent({ id: 'second', place_id: 'other-place' }),
      makeEvent({ id: 'third', place_id: 'same-place' })
    ];

    expect(
      Array.from(groupEventsByPlaceId(events).entries()).map(([placeId, groupedEvents]) => [
        placeId,
        groupedEvents.map((event) => event.id)
      ])
    ).toEqual([
      ['same-place', ['first', 'third']],
      ['other-place', ['second']]
    ]);
  });

  it('keeps a single event on the place coordinate and offsets colocated events', () => {
    const place = makePlace({ id: 'same-place', latitude: 40.82, longitude: -73.93 });

    expect(getMarkerPosition(place, 0, 1)).toEqual([40.82, -73.93]);

    const firstOffset = getMarkerPosition(place, 0, 2);
    const secondOffset = getMarkerPosition(place, 1, 2);

    expect(firstOffset).not.toEqual([40.82, -73.93]);
    expect(secondOffset).not.toEqual([40.82, -73.93]);
    expect(firstOffset).not.toEqual(secondOffset);
  });

  it('gives the selected marker stronger visual emphasis', () => {
    expect(getMarkerOptions(false, '#e4572e')).toEqual({
      radius: 7,
      color: '#24313d',
      weight: 1.5,
      fillColor: '#e4572e',
      fillOpacity: 0.82
    });

    expect(getMarkerOptions(true, '#e4572e')).toEqual({
      radius: 12,
      color: '#101820',
      weight: 3,
      fillColor: '#2e7d32',
      fillOpacity: 0.98
    });
  });

  it('builds marker placements only for events with known places and routes', () => {
    const routes = [makeRoute({ id: 'birth-of-hip-hop' })];
    const places = [makePlace({ id: 'same-place', latitude: 40.82, longitude: -73.93 })];
    const events = [
      makeEvent({ id: 'first', place_id: 'same-place' }),
      makeEvent({ id: 'second', place_id: 'same-place' }),
      makeEvent({ id: 'missing-place', place_id: 'unknown-place' }),
      makeEvent({ id: 'missing-route', route_id: 'downtown-experiment' })
    ];

    expect(getEventMarkerPlacements(events, places, routes).map((placement) => placement.event.id)).toEqual([
      'first',
      'second'
    ]);
    expect(getEventMarkerPlacements(events, places, routes)[0].position).not.toEqual([
      40.82,
      -73.93
    ]);
  });
});
