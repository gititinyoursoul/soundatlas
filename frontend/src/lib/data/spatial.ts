import type {
  Event,
  EventInput,
  Place,
  PlaceRelationship
} from '$lib/types/soundatlas';

export type PlaceSelectionResolution = {
  placeId: string;
  eventId: string | null;
  eventIds: string[];
  needsChoice: boolean;
};

export function normalizeEvent(event: EventInput): Event {
  const placeIds =
    event.place_ids && event.place_ids.length > 0
      ? [...event.place_ids]
      : [event.place_id];
  const defaultPlaceId = event.default_place_id ?? event.place_id;

  return {
    ...event,
    place_id: event.place_id ?? defaultPlaceId,
    place_ids: placeIds,
    default_place_id: defaultPlaceId,
    place_relationships: event.place_relationships ?? [],
    summary: event.summary ?? null,
    significance: event.significance ?? null,
    story_sections: event.story_sections ?? []
  };
}

export function resolveFocusedPlaceId(
  event: Event | null,
  focusedPlaceId: string | null
): string | null {
  if (!event) {
    return null;
  }

  return focusedPlaceId && event.place_ids.includes(focusedPlaceId)
    ? focusedPlaceId
    : event.default_place_id;
}

export function getEventPlaces(event: Event | null, places: Place[]): Place[] {
  if (!event) {
    return [];
  }

  const placeById = new Map(places.map((place) => [place.id, place]));
  return event.place_ids.flatMap((placeId) => {
    const place = placeById.get(placeId);
    return place ? [place] : [];
  });
}

export function getEventsForPlace(events: Event[], placeId: string): Event[] {
  return events.filter((event) => event.place_ids.includes(placeId));
}

export function resolvePlaceSelection(
  events: Event[],
  selectedEventId: string | null,
  placeId: string
): PlaceSelectionResolution {
  const matchingEvents = getEventsForPlace(events, placeId);
  const selectedEvent = matchingEvents.find(
    (event) => event.id === selectedEventId
  );

  if (selectedEvent) {
    return {
      placeId,
      eventId: selectedEvent.id,
      eventIds: [selectedEvent.id],
      needsChoice: false
    };
  }

  if (matchingEvents.length === 1) {
    return {
      placeId,
      eventId: matchingEvents[0].id,
      eventIds: [matchingEvents[0].id],
      needsChoice: false
    };
  }

  return {
    placeId,
    eventId: null,
    eventIds: matchingEvents.map((event) => event.id),
    needsChoice: matchingEvents.length > 1
  };
}

export function formatRelationshipDirection(
  relationship: PlaceRelationship,
  placeById: Map<string, Place>
): string {
  const fromName =
    placeById.get(relationship.from_place_id)?.name ??
    relationship.from_place_id;
  const toName =
    placeById.get(relationship.to_place_id)?.name ?? relationship.to_place_id;

  if (relationship.directionality === 'forward') {
    return `From ${fromName} toward ${toName}`;
  }
  if (relationship.directionality === 'reciprocal') {
    return `Exchange between ${fromName} and ${toName}`;
  }
  return `Connection between ${fromName} and ${toName}`;
}
