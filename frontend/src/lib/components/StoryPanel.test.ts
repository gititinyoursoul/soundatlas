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

  it('renders event review controls after the exact reader-facing story', () => {
    const event = makeEvent({
      id: 'review-event',
      title: 'Exact generated title',
      summary: 'Exact generated summary',
      significance: 'Exact generated significance'
    });
    const { body } = render(StoryPanel, {
      props: {
        event,
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
          proposal: { working_title: 'Planning-only title' },
          event
        }
      }
    });

    expect(body).toContain('Exact generated title');
    expect(body).toContain('Exact generated summary');
    expect(body).toContain('Exact generated significance');
    expect(body.indexOf('Exact generated summary')).toBeLessThan(
      body.indexOf('Event review')
    );
    expect(body).not.toContain('What happened');
    expect(body).not.toContain('Why it matters');
    expect(body).not.toContain('Planning-only title');
    expect(body).not.toContain('Publish exact reviewed route');
  });

  it('shows an explicit error when reader-facing event content is missing', () => {
    const { body } = render(StoryPanel, {
      props: {
        editorialMode: true,
        editorialContentError: 'summary: Field required',
        editorialProposal: {
          candidate_id: 'broken-event',
          editorial_state: 'draft',
          active: true,
          included: false,
          renderable: false,
          agent_recommendation: null,
          warnings: [],
          technical_errors: ['summary: Field required'],
          material_signature: 'signature',
          proposal: {},
          event: null
        }
      }
    });

    expect(body).toContain('Reader-facing story incomplete');
    expect(body).toContain('summary: Field required');
    expect(body).toContain('Event review');
  });
});
