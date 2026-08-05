import { render } from 'svelte/server';
import { describe, expect, it } from 'vitest';
import { makeEvent, makePlace, makeRoute } from '$lib/test/fixtures';
import StoryPanel from './StoryPanel.svelte';

describe('StoryPanel spatial access', () => {
  it('renders every event place as a focus control with textual geography', () => {
    const point = makePlace({ id: 'point', name: 'Point Place' });
    const area = makePlace({
      id: 'area',
      name: 'Area Place',
      geometry: {
        type: 'Polygon',
        coordinates: [
          [
            [-73.94, 40.81],
            [-73.93, 40.81],
            [-73.93, 40.82],
            [-73.94, 40.81]
          ]
        ]
      },
      geometry_precision: 'interpretive',
      geometry_source_type: 'curated',
      geometry_source_note: 'Fixture'
    });
    const event = makeEvent({
      id: 'multi-place-event',
      place_id: 'point',
      place_ids: ['point', 'area'],
      default_place_id: 'point',
      place_relationships: [
        {
          from_place_id: 'point',
          to_place_id: 'area',
          directionality: 'forward',
          context_label: 'Practice circulates toward the area.',
          source_urls: ['https://example.org/relationship']
        }
      ]
    });

    const { body } = render(StoryPanel, {
      props: {
        event,
        place: area,
        places: [point, area],
        selectedPlaceId: 'area',
        route: makeRoute({ id: 'birth-of-hip-hop' })
      }
    });

    expect(body).toContain('Places in this event');
    expect(body).toContain('Point Place');
    expect(body).toContain('Area Place');
    expect(body).toContain('aria-current="location"');
    expect(body).toContain('Interpretive cultural area');
    expect(body).toContain('From Point Place toward Area Place');
    expect(body).toContain('Practice circulates toward the area.');
  });

  it('renders the exact-route publication summary in editorial mode', () => {
    const { body } = render(StoryPanel, {
      props: {
        event: makeEvent({ id: 'review-event' }),
        place: makePlace({ id: 'review-place' }),
        route: makeRoute({ id: 'birth-of-hip-hop' }),
        editorialMode: true,
        editorialProposal: {
          candidate_id: 'review-event',
          editorial_state: 'draft',
          active: true,
          included: true,
          renderable: true,
          agent_recommendation: 'keep',
          warnings: ['Review the source.'],
          technical_errors: [],
          material_signature: 'signature',
          proposal: { working_title: 'Review event' }
        },
        publicationSummary: {
          route_id: 'birth-of-hip-hop',
          revision_id: 'revision-1',
          source: 'event-list.json',
          included_events: [
            {
              candidate_id: 'review-event',
              title: 'Review event',
              editorial_state: 'draft',
              included: true
            }
          ],
          excluded_event_ids: ['excluded-event'],
          warnings: ['Route warning.'],
          technical_errors: [],
          technical_ready: true,
          published_revision_id: null
        }
      }
    });

    expect(body).toContain('Route publication');
    expect(body).toContain('1 included');
    expect(body).toContain('1 excluded');
    expect(body).toContain('Publish exact reviewed route');
    expect(body).toContain('Route warning.');
  });
});
