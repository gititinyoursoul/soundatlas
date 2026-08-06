import { describe, expect, it } from 'vitest';
import { makeEvent } from '$lib/test/fixtures';
import type { RouteReviewProposal, RouteReviewResult } from '$lib/types/soundatlas';
import { projectRouteReview } from './editorial-review';

function makeProposal(
  overrides: Partial<RouteReviewProposal> = {}
): RouteReviewProposal {
  return {
    candidate_id: 'sedgwick-party',
    editorial_state: 'draft',
    active: true,
    included: true,
    renderable: true,
    agent_recommendation: 'Keep',
    warnings: [],
    technical_errors: [],
    material_signature: 'signature',
    proposal: { working_title: 'Planning-only title', years: 'around 1973' },
    event: makeEvent({
      id: 'sedgwick-party',
      title: 'Back-to-school party at 1520 Sedgwick Avenue',
      summary: 'The exact generated reader-facing summary.',
      significance: 'The exact generated significance.',
      source_urls: ['https://example.com/source']
    }),
    ...overrides
  };
}

function makeReview(
  overrides: Partial<RouteReviewResult> = {}
): RouteReviewResult {
  return {
    route_id: 'birth-of-hip-hop',
    revision_id: 'revision-1',
    source: 'complete-draft.json',
    proposals: [],
    dormant_proposals: [],
    places: [],
    connections: [],
    warnings: [],
    technical_errors: [],
    technical_ready: true,
    ...overrides
  };
}

describe('editorial review projection', () => {
  it('passes the generated event through without rebuilding it from planning fields', () => {
    const proposal = makeProposal();
    const [projection] = projectRouteReview(
      makeReview({ proposals: [proposal] })
    );

    expect(projection.event).toBe(proposal.event);
    expect(projection.event?.title).toBe(
      'Back-to-school party at 1520 Sedgwick Avenue'
    );
    expect(projection.event?.summary).toBe(
      'The exact generated reader-facing summary.'
    );
    expect(projection.renderOnMap).toBe(true);
    expect(projection.renderOnTimeline).toBe(true);
  });

  it('keeps a missing generated story list-only and exposes its technical error', () => {
    const [projection] = projectRouteReview(
      makeReview({
        proposals: [
          makeProposal({
            event: null,
            renderable: false,
            technical_errors: ['Generated event is invalid.']
          })
        ]
      })
    );

    expect(projection.event).toBeNull();
    expect(projection.renderOnMap).toBe(false);
    expect(projection.renderOnTimeline).toBe(false);
    expect(projection.warnings).toContain('Generated event is invalid.');
  });

  it('does not project excluded candidates into the map or timeline', () => {
    const [projection] = projectRouteReview(
      makeReview({
        proposals: [
          makeProposal({ editorial_state: 'dont_use', included: false })
        ]
      })
    );

    expect(projection.renderOnMap).toBe(false);
    expect(projection.renderOnTimeline).toBe(false);
  });
});
