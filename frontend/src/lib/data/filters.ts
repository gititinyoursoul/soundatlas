import type { Event } from '$lib/types/soundatlas';

export function filterEvents(events: Event[], selectedRouteId: string | null): Event[] {
  return events.filter((event) => !selectedRouteId || event.route_id === selectedRouteId);
}
