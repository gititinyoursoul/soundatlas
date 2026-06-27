import { describe, expect, it } from 'vitest';
import { makeEvent, makeRoute } from '$lib/test/fixtures';
import { getFirstEventIdForRoute, getInitialRouteId, getOrderedEventsForRoute } from './selection';

describe('route and event selection', () => {
  it('chooses the birth of hip-hop route by default when available', () => {
    const routes = [
      makeRoute({ id: 'downtown-experiment', title: 'Downtown Experiment' }),
      makeRoute({ id: 'birth-of-hip-hop', title: 'Birth of Hip-Hop' })
    ];

    expect(getInitialRouteId(routes)).toBe('birth-of-hip-hop');
  });

  it('falls back to the first route when the default route is unavailable', () => {
    const routes = [
      makeRoute({ id: 'downtown-experiment' }),
      makeRoute({ id: 'salsa-latin-new-york' })
    ];

    expect(getInitialRouteId(routes)).toBe('downtown-experiment');
  });

  it('returns null when there are no routes', () => {
    expect(getInitialRouteId([])).toBeNull();
  });

  it('selects the first event in route chronology', () => {
    const events = [
      makeEvent({ id: 'later-event', year_start: 1977, year_end: 1977 }),
      makeEvent({ id: 'early-event', year_start: 1973, year_end: 1973 }),
      makeEvent({
        id: 'other-route-event',
        route_id: 'downtown-experiment',
        year_start: 1971,
        year_end: 1971
      })
    ];

    expect(getFirstEventIdForRoute(events, 'birth-of-hip-hop')).toBe('early-event');
  });

  it('uses end year and title to keep same-start-year events deterministic', () => {
    const events = [
      makeEvent({ id: 'z-title', title: 'Zulu Nation', year_start: 1973, year_end: 1975 }),
      makeEvent({ id: 'a-title', title: 'Apartment Jam', year_start: 1973, year_end: 1973 }),
      makeEvent({ id: 'b-title', title: 'Block Party', year_start: 1973, year_end: 1973 })
    ];

    expect(getOrderedEventsForRoute(events, 'birth-of-hip-hop').map((event) => event.id)).toEqual([
      'a-title',
      'b-title',
      'z-title'
    ]);
  });

  it('returns null when the selected route has no events', () => {
    const events = [makeEvent({ id: 'bronx-event', route_id: 'birth-of-hip-hop' })];

    expect(getFirstEventIdForRoute(events, 'downtown-experiment')).toBeNull();
  });
});
