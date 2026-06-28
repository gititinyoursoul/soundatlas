import type { Event, Place, Route } from '$lib/types/soundatlas';

export type MarkerOptions = {
  radius: number;
  color: string;
  weight: number;
  fillColor: string;
  fillOpacity: number;
};

export function getVisibleRoutes(routes: Route[], events: Event[]): Route[] {
  const visibleRouteIds = new Set(events.map((event) => event.route_id));

  return routes.filter((route) => visibleRouteIds.has(route.id));
}

export function groupEventsByPlaceId(eventsToGroup: Event[]): Map<string, Event[]> {
  const groupedEvents = new Map<string, Event[]>();

  for (const event of eventsToGroup) {
    groupedEvents.set(event.place_id, [...(groupedEvents.get(event.place_id) ?? []), event]);
  }

  return groupedEvents;
}

export function getMarkerPosition(
  place: Place,
  eventIndex: number,
  colocatedEventCount: number
): [number, number] {
  if (colocatedEventCount <= 1 || eventIndex < 0) {
    return [place.latitude, place.longitude];
  }

  const angle = (2 * Math.PI * eventIndex) / colocatedEventCount;
  const radiusInMeters = 70;
  const latitudeOffset = (Math.sin(angle) * radiusInMeters) / 111_320;
  const longitudeOffset =
    (Math.cos(angle) * radiusInMeters) / (111_320 * Math.cos((place.latitude * Math.PI) / 180));

  return [place.latitude + latitudeOffset, place.longitude + longitudeOffset];
}

export function getMarkerOptions(isSelected: boolean, routeColor: string): MarkerOptions {
  return {
    radius: isSelected ? 13 : 7,
    color: '#17202a',
    weight: isSelected ? 3 : 1,
    fillColor: isSelected ? '#2e7d32' : routeColor,
    fillOpacity: isSelected ? 1 : 0.75
  };
}
