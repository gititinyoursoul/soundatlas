import type { Event, TimelineRange } from '$lib/types/soundatlas';

export function filterEvents(
  events: Event[],
  activeRouteIds: Set<string>,
  range: TimelineRange
): Event[] {
  return events.filter((event) => {
    const routeMatches = activeRouteIds.size === 0 || activeRouteIds.has(event.route_id);
    const timeMatches = event.year_end >= range.fromYear && event.year_start <= range.toYear;

    return routeMatches && timeMatches;
  });
}
