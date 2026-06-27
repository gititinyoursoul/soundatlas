import { describe, expect, it, vi } from 'vitest';
import { makeConnection, makeEvent, makePlace, makeRoute } from '$lib/test/fixtures';
import { API_BASE_URL, loadSoundAtlasData, reviewEventMediaLink } from './soundatlas';

function jsonResponse(body: unknown, init: ResponseInit = {}): Response {
  return new Response(JSON.stringify(body), {
    status: 200,
    headers: {
      'Content-Type': 'application/json'
    },
    ...init
  });
}

describe('SoundAtlas API client', () => {
  it('loads routes, places, events, and connections', async () => {
    const routes = [makeRoute({ id: 'birth-of-hip-hop' })];
    const places = [makePlace({ id: '1520-sedgwick-avenue' })];
    const events = [makeEvent({ id: 'kool-herc-back-to-school-jam' })];
    const connections = [makeConnection({ id: 'breakbeat-influence' })];
    const fetcher = vi
      .fn<typeof fetch>()
      .mockResolvedValueOnce(jsonResponse(routes))
      .mockResolvedValueOnce(jsonResponse(places))
      .mockResolvedValueOnce(jsonResponse(events))
      .mockResolvedValueOnce(jsonResponse(connections));

    await expect(loadSoundAtlasData(fetcher)).resolves.toEqual({
      routes,
      places,
      events,
      connections
    });

    expect(fetcher).toHaveBeenCalledTimes(4);
    expect(fetcher).toHaveBeenNthCalledWith(1, `${API_BASE_URL}/routes`);
    expect(fetcher).toHaveBeenNthCalledWith(2, `${API_BASE_URL}/places`);
    expect(fetcher).toHaveBeenNthCalledWith(3, `${API_BASE_URL}/events`);
    expect(fetcher).toHaveBeenNthCalledWith(4, `${API_BASE_URL}/connections`);
  });

  it('handles empty collection responses', async () => {
    const fetcher = vi
      .fn<typeof fetch>()
      .mockResolvedValueOnce(jsonResponse([]))
      .mockResolvedValueOnce(jsonResponse([]))
      .mockResolvedValueOnce(jsonResponse([]))
      .mockResolvedValueOnce(jsonResponse([]));

    await expect(loadSoundAtlasData(fetcher)).resolves.toEqual({
      routes: [],
      places: [],
      events: [],
      connections: []
    });
  });

  it('surfaces collection request failures', async () => {
    const fetcher = vi
      .fn<typeof fetch>()
      .mockResolvedValueOnce(jsonResponse([], { status: 503, statusText: 'Service Unavailable' }))
      .mockResolvedValueOnce(jsonResponse([]))
      .mockResolvedValueOnce(jsonResponse([]))
      .mockResolvedValueOnce(jsonResponse([]));

    await expect(loadSoundAtlasData(fetcher)).rejects.toThrow(
      'API request failed: 503 Service Unavailable'
    );
  });

  it('sends media review updates and returns the updated event', async () => {
    const updatedEvent = makeEvent({ id: 'kool-herc-back-to-school-jam', review_status: 'reviewed' });
    const fetcher = vi.fn<typeof fetch>().mockResolvedValueOnce(jsonResponse(updatedEvent));

    await expect(
      reviewEventMediaLink(
        'kool-herc-back-to-school-jam',
        'https://www.youtube.com/watch?v=example',
        'reviewed',
        fetcher
      )
    ).resolves.toEqual(updatedEvent);

    expect(fetcher).toHaveBeenCalledWith(
      `${API_BASE_URL}/events/kool-herc-back-to-school-jam/media-links`,
      {
        method: 'PATCH',
        headers: {
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({
          url: 'https://www.youtube.com/watch?v=example',
          action: 'reviewed'
        })
      }
    );
  });
});
