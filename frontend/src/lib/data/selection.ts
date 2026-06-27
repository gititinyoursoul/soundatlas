import { filterEvents } from '$lib/data/filters';
import type { Event, Route } from '$lib/types/soundatlas';

export const DEFAULT_ROUTE_ID = 'birth-of-hip-hop';

export function getInitialRouteId(routes: Route[]): string | null {
  return routes.find((route) => route.id === DEFAULT_ROUTE_ID)?.id ?? routes[0]?.id ?? null;
}

export function getFirstEventIdForRoute(events: Event[], routeId: string | null): string | null {
  return getOrderedEventsForRoute(events, routeId)[0]?.id ?? null;
}

export function getOrderedEventsForRoute(events: Event[], routeId: string | null): Event[] {
  return [...filterEvents(events, routeId)].sort(compareEvents);
}

export function compareEvents(left: Event, right: Event): number {
  return (
    left.year_start - right.year_start ||
    left.year_end - right.year_end ||
    left.title.localeCompare(right.title)
  );
}
