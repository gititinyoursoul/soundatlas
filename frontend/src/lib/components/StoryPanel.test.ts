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
});
