import type { Connection, Event, Place, Route } from '$lib/types/soundatlas';

export function makeRoute(overrides: Partial<Route> & Pick<Route, 'id'>): Route {
  const { id, ...routeOverrides } = overrides;

  return {
    title: 'Route title',
    color: '#e4572e',
    creator: 'SoundAtlas',
    year_start: 1970,
    year_end: 1985,
    summary: 'Route summary',
    thesis: 'Route thesis',
    tags: [],
    review_status: 'draft',
    source_urls: [],
    ...routeOverrides,
    id
  };
}

export function makePlace(overrides: Partial<Place> & Pick<Place, 'id'>): Place {
  const { id, ...placeOverrides } = overrides;

  return {
    name: 'Place name',
    borough: 'Bronx',
    place_type: 'venue',
    latitude: 40.82,
    longitude: -73.93,
    summary: 'Place summary',
    review_status: 'draft',
    source_urls: [],
    ...placeOverrides,
    id
  };
}

export function makeEvent(overrides: Partial<Event> & Pick<Event, 'id'>): Event {
  const { id, ...eventOverrides } = overrides;

  return {
    route_id: 'birth-of-hip-hop',
    place_id: '1520-sedgwick-avenue',
    title: 'Event title',
    year_start: 1973,
    year_end: 1973,
    summary: 'Event summary',
    significance: 'Event significance',
    tags: [],
    review_status: 'draft',
    source_urls: [],
    media_links: [],
    image_links: [],
    ...eventOverrides,
    id
  };
}

export function makeConnection(
  overrides: Partial<Connection> & Pick<Connection, 'id'>
): Connection {
  const { id, ...connectionOverrides } = overrides;

  return {
    from_event_id: 'event-a',
    to_event_id: 'event-b',
    type: 'influence',
    summary: 'Connection summary',
    review_status: 'draft',
    ...connectionOverrides,
    id
  };
}
