import type {
  Connection,
  Event,
  Place,
  ReviewAction,
  ReviewLinkKind,
  Route,
  SoundAtlasData
} from '$lib/types/soundatlas';
import { base } from '$app/paths';

const DEFAULT_API_BASE_URL = 'http://127.0.0.1:8000';
const STATIC_DATA_BASE_PATH = `${base}/soundatlas-data`;

export const API_BASE_URL =
  import.meta.env.VITE_API_BASE_URL?.replace(/\/$/, '') ?? DEFAULT_API_BASE_URL;

export const DATA_MODE = import.meta.env.VITE_DATA_MODE === 'static' ? 'static' : 'api';

export const IS_PUBLIC_STATIC_MODE = DATA_MODE === 'static';

export async function loadSoundAtlasData(fetcher: typeof fetch = fetch): Promise<SoundAtlasData> {
  if (DATA_MODE === 'static') {
    return loadStaticSoundAtlasData(fetcher);
  }

  return loadApiSoundAtlasData(fetcher);
}

export async function loadApiSoundAtlasData(fetcher: typeof fetch = fetch): Promise<SoundAtlasData> {
  const [routes, places, events, connections] = await Promise.all([
    requestJson<Route[]>('/routes', fetcher),
    requestJson<Place[]>('/places', fetcher),
    requestJson<Event[]>('/events', fetcher),
    requestJson<Connection[]>('/connections', fetcher)
  ]);

  return {
    routes,
    places,
    events,
    connections
  };
}

export async function loadStaticSoundAtlasData(fetcher: typeof fetch = fetch): Promise<SoundAtlasData> {
  const [routes, places, events, connections] = await Promise.all([
    requestStaticJson<Route[]>('routes.json', fetcher),
    requestStaticJson<Place[]>('places.json', fetcher),
    requestStaticJson<Event[]>('events.json', fetcher),
    requestStaticJson<Connection[]>('connections.json', fetcher)
  ]);

  return {
    routes,
    places,
    events,
    connections
  };
}

export async function reviewEventMediaLink(
  eventId: string,
  url: string,
  action: ReviewAction,
  fetcher: typeof fetch = fetch
): Promise<Event> {
  return reviewEventLink(eventId, 'media', url, action, fetcher);
}

export async function reviewEventLink(
  eventId: string,
  kind: ReviewLinkKind,
  url: string,
  action: ReviewAction,
  fetcher: typeof fetch = fetch
): Promise<Event> {
  const response = await fetcher(`${API_BASE_URL}/events/${eventId}/links`, {
    method: 'PATCH',
    headers: {
      'Content-Type': 'application/json'
    },
    body: JSON.stringify({ kind, url, action })
  });

  if (!response.ok) {
    throw new Error(`API request failed: ${response.status} ${response.statusText}`);
  }

  return (await response.json()) as Event;
}

async function requestJson<T>(path: string, fetcher: typeof fetch): Promise<T> {
  const response = await fetcher(`${API_BASE_URL}${path}`);

  if (!response.ok) {
    throw new Error(`API request failed: ${response.status} ${response.statusText}`);
  }

  return (await response.json()) as T;
}

async function requestStaticJson<T>(fileName: string, fetcher: typeof fetch): Promise<T> {
  const response = await fetcher(`${STATIC_DATA_BASE_PATH}/${fileName}`);

  if (!response.ok) {
    throw new Error(`Static data request failed: ${response.status} ${response.statusText}`);
  }

  return (await response.json()) as T;
}
