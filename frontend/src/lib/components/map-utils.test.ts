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

  it('builds a generated avatar marker with route color and initials', () => {
    const avatar = getMarkerOptions(false, '#e4572e', makeEvent({ id: 'first-event', title: 'Grand Opening' }));

    expect(avatar.className).toBe('event-avatar-marker');
    expect(avatar.iconSize).toEqual([32, 32]);
    expect(avatar.iconAnchor).toEqual([16, 16]);
    expect(avatar.html).toContain('--route-color: #e4572e');
    expect(avatar.html).toContain('data:image/svg+xml');
    expect(avatar.html).toContain('GO');
  });

  it('prefers a provided image link over a generated avatar', () => {
    const avatar = getMarkerOptions(
      false,
      '#e4572e',
      makeEvent({
        id: 'first-event',
        title: 'Grand Opening',
        image_links: [
          {
            provider: 'wikimedia',
            type: 'archive_photo',
            title: 'Archive photo',
            image_url: 'https://example.com/avatar.jpg',
            thumbnail_url: 'https://example.com/avatar-thumb.jpg',
            source_url: 'https://example.com/source',
            rights_status: 'unknown',
            alt_text: 'Avatar image',
            query: 'Grand Opening',
            confidence: 0.9,
            review_status: 'draft'
          }
        ]
      })
    );

    expect(avatar.html).toContain('https://example.com/avatar-thumb.jpg');
    expect(avatar.html).not.toContain('data:image/svg+xml');
  });

  it('grows the selected avatar marker', () => {
    const avatar = getMarkerOptions(true, '#e4572e', makeEvent({ id: 'first-event', title: 'Grand Opening' }));

    expect(avatar.className).toBe('event-avatar-marker selected');
    expect(avatar.iconSize).toEqual([44, 44]);
    expect(avatar.iconAnchor).toEqual([22, 22]);
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
