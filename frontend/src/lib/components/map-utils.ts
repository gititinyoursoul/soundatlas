import type { Event, Place, Route } from '$lib/types/soundatlas';

export type MarkerOptions = {
  className: string;
  iconSize: [number, number];
  iconAnchor: [number, number];
  html: string;
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
  const radiusInMeters = 170;
  const latitudeOffset = (Math.sin(angle) * radiusInMeters) / 111_320;
  const longitudeOffset =
    (Math.cos(angle) * radiusInMeters) / (111_320 * Math.cos((place.latitude * Math.PI) / 180));

  return [place.latitude + latitudeOffset, place.longitude + longitudeOffset];
}

export function getMarkerOptions(isSelected: boolean, routeColor: string, event: Event): MarkerOptions {
  const size = isSelected ? 44 : 32;
  const initials = getEventInitials(event.title);
  const accentColor = getAccentColor(event.id);
  const avatarUrl = getEventAvatarUrl(event, accentColor, initials);

  return {
    className: `event-avatar-marker${isSelected ? ' selected' : ''}`,
    iconSize: [size, size],
    iconAnchor: [Math.round(size / 2), Math.round(size / 2)],
    html: `<div class="event-avatar" style="--route-color: ${routeColor}">
      <img class="event-avatar-image" src="${escapeHtmlAttribute(avatarUrl)}" alt="" aria-hidden="true" />
    </div>`
  };
}

function getEventAvatarUrl(
  event: Event,
  accentColor: string,
  initials: string
): string {
  const imageLink = event.image_links.find((link) => link.thumbnail_url || link.image_url);

  if (imageLink) {
    return imageLink.thumbnail_url ?? imageLink.image_url;
  }

  return getEventAvatarDataUrl(accentColor, initials);
}

function getEventInitials(title: string): string {
  const words = title
    .split(/[^A-Za-z0-9]+/)
    .map((word) => word.trim())
    .filter(Boolean);

  const initials = words
    .slice(0, 2)
    .map((word) => word[0]?.toUpperCase() ?? '')
    .join('');

  return initials || 'SA';
}

function getAccentColor(eventId: string): string {
  const accents = ['#365f6b', '#8b5e3c', '#4f6f52', '#7b5167', '#6b6d42', '#566a8f'];
  let hash = 0;

  for (const character of eventId) {
    hash = (hash * 31 + character.charCodeAt(0)) | 0;
  }

  return accents[Math.abs(hash) % accents.length];
}

function getEventAvatarDataUrl(accentColor: string, initials: string): string {
  const svg = `
    <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 120 120" role="img" aria-label="${escapeHtmlAttribute(
      initials
    )}">
      <defs>
        <linearGradient id="bg" x1="0%" y1="0%" x2="100%" y2="100%">
          <stop offset="0%" stop-color="#eef2f4" />
          <stop offset="48%" stop-color="${escapeHtmlAttribute(accentColor)}" />
          <stop offset="100%" stop-color="#19242e" />
        </linearGradient>
      </defs>
      <circle cx="60" cy="60" r="60" fill="url(#bg)" />
      <circle cx="40" cy="42" r="22" fill="#ffffff" opacity="0.22" />
      <circle cx="78" cy="80" r="30" fill="#ffffff" opacity="0.16" />
      <circle cx="68" cy="36" r="11" fill="#ffffff" opacity="0.18" />
      <text
        x="60"
        y="72"
        text-anchor="middle"
        font-family="Arial, Helvetica, sans-serif"
        font-size="32"
        font-weight="800"
        fill="#ffffff"
        opacity="0.96"
        letter-spacing="1"
      >${escapeHtml(initials)}</text>
    </svg>
  `;

  return `data:image/svg+xml;charset=UTF-8,${encodeURIComponent(svg.trim())}`;
}

function escapeHtml(value: string): string {
  return value
    .replaceAll('&', '&amp;')
    .replaceAll('<', '&lt;')
    .replaceAll('>', '&gt;')
    .replaceAll('"', '&quot;')
    .replaceAll("'", '&#39;');
}

function escapeHtmlAttribute(value: string): string {
  return escapeHtml(value);
}
