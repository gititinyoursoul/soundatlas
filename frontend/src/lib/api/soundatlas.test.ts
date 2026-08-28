import { describe, expect, it, vi } from 'vitest';
import { base } from '$app/paths';
import { makeEvent, makePlace, makeRoute } from '$lib/test/fixtures';
import {
  API_BASE_URL,
  loadApiSoundAtlasData,
  loadStaticSoundAtlasData,
  reviewEventLink,
  loadRoutePublication,
  loadRouteNavigation,
  loadRouteReview,
  publishRoute,
  updateRouteReviewState
} from './soundatlas';

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
  it('loads MVP routes, places, and events without a Connection dependency', async () => {
    const routes = [makeRoute({ id: 'birth-of-hip-hop' })];
    const places = [makePlace({ id: '1520-sedgwick-avenue' })];
    const events = [makeEvent({ id: 'kool-herc-back-to-school-jam' })];
    const fetcher = vi
      .fn<typeof fetch>()
      .mockResolvedValueOnce(jsonResponse(routes))
      .mockResolvedValueOnce(jsonResponse(places))
      .mockResolvedValueOnce(jsonResponse(events));

    await expect(loadApiSoundAtlasData(fetcher)).resolves.toEqual({
      routes,
      places,
      events,
      connections: []
    });

    expect(fetcher).toHaveBeenCalledTimes(3);
    expect(fetcher).toHaveBeenNthCalledWith(1, `${API_BASE_URL}/routes`);
    expect(fetcher).toHaveBeenNthCalledWith(2, `${API_BASE_URL}/places`);
    expect(fetcher).toHaveBeenNthCalledWith(3, `${API_BASE_URL}/events`);
  });

  it('handles empty collection responses', async () => {
    const fetcher = vi
      .fn<typeof fetch>()
      .mockResolvedValueOnce(jsonResponse([]))
      .mockResolvedValueOnce(jsonResponse([]))
      .mockResolvedValueOnce(jsonResponse([]));

    await expect(loadApiSoundAtlasData(fetcher)).resolves.toEqual({
      routes: [],
      places: [],
      events: [],
      connections: []
    });
  });

  it('normalizes section-based API events without legacy prose fields', async () => {
    const routes = [makeRoute({ id: 'birth-of-hip-hop' })];
    const places = [makePlace({ id: '1520-sedgwick-avenue' })];
    const baseEvent = makeEvent({ id: 'section-event' });
    const input = {
      ...baseEvent,
      summary: undefined,
      significance: undefined,
      story_sections: [
        { heading: 'The room opens', body: 'Reviewed section prose.' }
      ]
    };
    const fetcher = vi
      .fn<typeof fetch>()
      .mockResolvedValueOnce(jsonResponse(routes))
      .mockResolvedValueOnce(jsonResponse(places))
      .mockResolvedValueOnce(jsonResponse([input]));

    const result = await loadApiSoundAtlasData(fetcher);

    expect(result.events[0]).toMatchObject({
      id: 'section-event',
      summary: null,
      significance: null,
      story_sections: input.story_sections
    });
  });

  it('surfaces collection request failures', async () => {
    const fetcher = vi
      .fn<typeof fetch>()
      .mockResolvedValueOnce(
        jsonResponse([], { status: 503, statusText: 'Service Unavailable' })
      )
      .mockResolvedValueOnce(jsonResponse([]))
      .mockResolvedValueOnce(jsonResponse([]));

    await expect(loadApiSoundAtlasData(fetcher)).rejects.toThrow(
      'API request failed: 503 Service Unavailable'
    );
  });

  it('loads static public data from generated assets', async () => {
    const routes = [makeRoute({ id: 'birth-of-hip-hop' })];
    const places = [makePlace({ id: '1520-sedgwick-avenue' })];
    const canonicalEvent = makeEvent({ id: 'kool-herc-back-to-school-jam' });
    const events = [{ ...canonicalEvent, story_sections: undefined }];
    const fetcher = vi
      .fn<typeof fetch>()
      .mockResolvedValueOnce(jsonResponse({ _meta: {}, routes }))
      .mockResolvedValueOnce(jsonResponse({ _meta: {}, places }))
      .mockResolvedValueOnce(
        jsonResponse({ _meta: {}, events, ignored_links: [] })
      );

    await expect(loadStaticSoundAtlasData(fetcher)).resolves.toEqual({
      routes,
      places,
      events: [canonicalEvent],
      connections: []
    });

    expect(fetcher).toHaveBeenCalledTimes(3);
    expect(fetcher).toHaveBeenNthCalledWith(
      1,
      `${base}/soundatlas-data/routes.json`
    );
    expect(fetcher).toHaveBeenNthCalledWith(
      2,
      `${base}/soundatlas-data/places.json`
    );
    expect(fetcher).toHaveBeenNthCalledWith(
      3,
      `${base}/soundatlas-data/events.json`
    );
  });

  it('surfaces malformed static public data', async () => {
    const fetcher = vi
      .fn<typeof fetch>()
      .mockResolvedValueOnce(jsonResponse({ _meta: {}, route_entries: [] }))
      .mockResolvedValueOnce(jsonResponse({ _meta: {}, places: [] }))
      .mockResolvedValueOnce(jsonResponse({ _meta: {}, events: [] }))
      .mockResolvedValueOnce(jsonResponse({ _meta: {}, connections: [] }));

    await expect(loadStaticSoundAtlasData(fetcher)).rejects.toThrow(
      "Static data file 'routes.json' is missing 'routes' collection."
    );
  });

  it('sends media review updates and returns the updated event', async () => {
    const updatedEvent = makeEvent({
      id: 'kool-herc-back-to-school-jam',
      content_review_status: 'reviewed'
    });
    const fetcher = vi
      .fn<typeof fetch>()
      .mockResolvedValueOnce(jsonResponse(updatedEvent));

    await expect(
      reviewEventLink(
        'kool-herc-back-to-school-jam',
        'media',
        'https://www.youtube.com/watch?v=example',
        'reviewed',
        fetcher
      )
    ).resolves.toEqual(updatedEvent);

    expect(fetcher).toHaveBeenCalledWith(
      `${API_BASE_URL}/events/kool-herc-back-to-school-jam/links`,
      {
        method: 'PATCH',
        headers: {
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({
          kind: 'media',
          url: 'https://www.youtube.com/watch?v=example',
          action: 'reviewed'
        })
      }
    );
  });

  it('loads and updates a route review with its revision', async () => {
    const review = {
      route_id: 'birth-of-hip-hop',
      revision_id: 'revision-1',
      source: 'event-list.json',
      proposals: [],
      dormant_proposals: [],
      warnings: [],
      technical_ready: true
    };
    const fetcher = vi
      .fn<typeof fetch>()
      .mockResolvedValueOnce(jsonResponse(review))
      .mockResolvedValueOnce(jsonResponse(review));
    await expect(loadRouteReview('birth-of-hip-hop', fetcher)).resolves.toEqual(
      review
    );
    await expect(
      updateRouteReviewState(
        'birth-of-hip-hop',
        'candidate',
        'revision-1',
        'approved',
        fetcher
      )
    ).resolves.toEqual(review);
    expect(fetcher).toHaveBeenLastCalledWith(
      `${API_BASE_URL}/editorial/routes/birth-of-hip-hop/review/events/candidate`,
      expect.objectContaining({
        method: 'PATCH',
        body: JSON.stringify({
          revision_id: 'revision-1',
          editorial_state: 'approved'
        })
      })
    );
  });

  it('loads a publication summary and publishes the exact revision', async () => {
    const summary = {
      route_id: 'birth-of-hip-hop',
      revision_id: 'revision-1',
      source: 'event-list.json',
      included_events: [],
      excluded_event_ids: [],
      warnings: ['Source review remains open.'],
      technical_errors: [],
      technical_ready: true,
      published_revision_id: null
    };
    const result = { ...summary, published: true };
    const fetcher = vi
      .fn<typeof fetch>()
      .mockResolvedValueOnce(jsonResponse(summary))
      .mockResolvedValueOnce(jsonResponse(result));

    await expect(
      loadRoutePublication('birth-of-hip-hop', fetcher)
    ).resolves.toEqual(summary);
    await expect(
      publishRoute('birth-of-hip-hop', 'revision-1', fetcher)
    ).resolves.toEqual(result);
    expect(fetcher).toHaveBeenLastCalledWith(
      `${API_BASE_URL}/editorial/routes/birth-of-hip-hop/publication`,
      {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ revision_id: 'revision-1' })
      }
    );
  });

  it('loads the route-navigation summary for the active data mode', async () => {
    const summary = {
      routes: [
        {
          route: makeRoute({ id: 'published-route' }),
          review_revision_id: 'review-2',
          published_revision_id: 'published-1',
          appears_in_routes: true,
          appears_in_published_routes: true,
          appears_in_routes_to_review: true
        }
      ]
    };
    const fetcher = vi
      .fn<typeof fetch>()
      .mockResolvedValueOnce(jsonResponse(summary));

    await expect(loadRouteNavigation(fetcher)).resolves.toEqual(summary);
    expect(fetcher).toHaveBeenCalledWith(
      import.meta.env.VITE_DATA_MODE === 'static'
        ? `${base}/soundatlas-data/route-navigation.json`
        : `${API_BASE_URL}/editorial/route-navigation`
    );
  });
});
