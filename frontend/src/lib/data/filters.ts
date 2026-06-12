import type { Event } from '$lib/types/soundatlas';

export function filterEvents(events: Event[], activeRouteIds: Set<string>): Event[] {
  return events.filter((event) => activeRouteIds.size === 0 || activeRouteIds.has(event.route_id));
}
