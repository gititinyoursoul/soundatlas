import { describe, expect, it } from 'vitest';
import { makePlace } from '$lib/test/fixtures';
import type { RouteReviewResult } from '$lib/types/soundatlas';
import { projectRouteReview } from './editorial-review';

function makeReview(
  overrides: Partial<RouteReviewResult> = {}
): RouteReviewResult {
  return {
    route_id: 'birth-of-hip-hop',
    revision_id: 'revision-1',
    source: 'event-list.json',
    proposals: [],
    dormant_proposals: [],
    warnings: [],
    technical_ready: true,
    ...overrides
  };
}

describe('editorial review projection', () => {
  it('maps a stable place id and a year range into a temporary event', () => {
    const review = makeReview({
      proposals: [
        {
          candidate_id: 'sedgwick-party',
          editorial_state: 'draft',
          active: true,
          included: true,
          renderable: true,
          agent_recommendation: 'Keep',
          warnings: [],
          technical_errors: [],
          material_signature: 'signature',
          proposal: {
            working_title: 'Sedgwick party',
            years: '1973',
            place_id: 'sedgwick'
          }
        }
      ]
    });

    const [projection] = projectRouteReview(review, [
      makePlace({ id: 'sedgwick', name: '1520 Sedgwick Avenue' })
    ]);
    expect(projection.event.id).toBe('sedgwick-party');
    expect(projection.event.place_ids).toEqual(['sedgwick']);
    expect(projection.event.year_start).toBe(1973);
    expect(projection.renderOnMap).toBe(true);
    expect(projection.renderOnTimeline).toBe(true);
  });

  it('keeps ambiguous places list-only and preserves warnings', () => {
    const review = makeReview({
      proposals: [
        {
          candidate_id: 'bronx-context',
          editorial_state: 'draft',
          active: true,
          included: true,
          renderable: true,
          agent_recommendation: null,
          warnings: ['Needs place review'],
          technical_errors: [],
          material_signature: 'signature',
          proposal: {
            working_title: 'Bronx context',
            years: '1970s',
            place: 'Bronx'
          }
        }
      ]
    });

    const [projection] = projectRouteReview(review, [
      makePlace({ id: 'bronx-a', name: 'Bronx' }),
      makePlace({ id: 'bronx-b', name: 'Bronx' })
    ]);
    expect(projection.event.place_ids).toEqual([]);
    expect(projection.renderOnMap).toBe(false);
    expect(projection.renderOnTimeline).toBe(true);
    expect(projection.warnings).toContain('Needs place review');
  });

  it('does not project excluded candidates into map or timeline', () => {
    const proposal = {
      candidate_id: 'excluded',
      editorial_state: 'dont_use' as const,
      active: true,
      included: false,
      renderable: true,
      agent_recommendation: null,
      warnings: [],
      technical_errors: [],
      material_signature: 'signature',
      proposal: { working_title: 'Excluded', years: '1973', place_id: 'place' }
    };
    const [projection] = projectRouteReview(
      makeReview({ proposals: [proposal] }),
      [makePlace({ id: 'place' })]
    );
    expect(projection).toBeDefined();
    expect(projection.renderOnMap).toBe(false);
    expect(projection.renderOnTimeline).toBe(false);
  });
});
