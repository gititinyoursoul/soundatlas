import type { Connection, Event, Place, Route, SoundAtlasData } from '$lib/types/soundatlas';

const DEFAULT_API_BASE_URL = 'http://127.0.0.1:8000';

export const API_BASE_URL =
  import.meta.env.VITE_API_BASE_URL?.replace(/\/$/, '') ?? DEFAULT_API_BASE_URL;

export async function loadSoundAtlasData(fetcher: typeof fetch = fetch): Promise<SoundAtlasData> {
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

async function requestJson<T>(path: string, fetcher: typeof fetch): Promise<T> {
  const response = await fetcher(`${API_BASE_URL}${path}`);

  if (!response.ok) {
    throw new Error(`API request failed: ${response.status} ${response.statusText}`);
  }

  return (await response.json()) as T;
}
