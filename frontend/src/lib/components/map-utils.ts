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

export type EventMarkerPlacement = {
  event: Event;
  place: Place;
  route: Route;
  position: [number, number];
};

export function getEventMarkerPlacements(
  eventsToPlace: Event[],
  currentPlaces: Place[],
  currentRoutes: Route[]
): EventMarkerPlacement[] {
  const eventsByPlaceId = groupEventsByPlaceId(eventsToPlace);
  const currentPlaceById = new Map(currentPlaces.map((place) => [place.id, place]));
  const currentRouteById = new Map(currentRoutes.map((route) => [route.id, route]));
  const placements: EventMarkerPlacement[] = [];

  for (const event of eventsToPlace) {
    const place = currentPlaceById.get(event.place_id);
    const route = currentRouteById.get(event.route_id);

    if (!place || !route) {
      continue;
    }

    const colocatedEvents = eventsByPlaceId.get(event.place_id) ?? [event];
    const eventIndex = colocatedEvents.findIndex((colocatedEvent) => colocatedEvent.id === event.id);
    const position = getMarkerPosition(place, eventIndex, colocatedEvents.length);

    placements.push({
      event,
      place,
      route,
      position
    });
  }

  return placements;
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
    radius: isSelected ? 12 : 7,
    color: isSelected ? '#101820' : '#24313d',
    weight: isSelected ? 3 : 1.5,
    fillColor: isSelected ? '#2e7d32' : routeColor,
    fillOpacity: isSelected ? 0.98 : 0.82
  };
}
