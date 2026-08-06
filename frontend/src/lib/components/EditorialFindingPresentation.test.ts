import { render } from 'svelte/server';
import { describe, expect, it } from 'vitest';
import { makeEvent } from '$lib/test/fixtures';
import type { RouteReviewProposal } from '$lib/types/soundatlas';
import EditorialEventList from './EditorialEventList.svelte';
import EditorialReviewTools from './EditorialReviewTools.svelte';

function proposal(
  overrides: Partial<RouteReviewProposal> = {}
): RouteReviewProposal {
  const event = makeEvent({ id: 'review-event', title: 'Exact event title' });
  return {
    candidate_id: 'review-event',
    editorial_state: 'draft',
    active: true,
    included: true,
    renderable: true,
    agent_recommendation: 'Keep this event.',
    warnings: ['Verify the event date.', 'Compare the source wording.'],
    technical_errors: ['Reader-facing summary is missing.'],
    material_signature: 'signature',
    proposal: { working_title: 'Planning title' },
    event,
    ...overrides
  };
}

describe('editorial finding presentation', () => {
  it('shows compact non-zero counts and editorial state on every event row', () => {
    const { body } = render(EditorialEventList, {
      props: {
        proposals: [
          proposal(),
          proposal({
            candidate_id: 'excluded-event',
            editorial_state: 'dont_use',
            included: false,
            warnings: ['Excluded warning.'],
            technical_errors: [],
            event: makeEvent({ id: 'excluded-event', title: 'Excluded event' })
          })
        ]
      }
    });

    expect(body).toContain('Exact event title');
    expect(body).toContain('>draft<');
    expect(body).toContain('2 warnings');
    expect(body).toContain('1 blocking error');
    expect(body).toContain('Excluded event');
    expect(body).toContain('>dont use<');
    expect(body).toContain('1 warning');
    expect(body).not.toContain('State:');
    expect(body).not.toContain('0 blocking errors');
  });

  it('separates recommendation, warning rows, and blocking-error rows', () => {
    const { body } = render(EditorialReviewTools, {
      props: { proposal: proposal() }
    });

    expect(body).toContain('Event review');
    expect(body).toContain('Suggested:');
    expect(body).toContain('Keep this event.');
    expect(body).toContain('2 warnings');
    expect(body).toContain('1 blocking error');
    expect(body).not.toContain('Agent recommendation');
    expect(body).not.toContain('>Warning<');
    expect(body).not.toContain('>Blocking error<');
    expect(body).toContain('Verify the event date.');
    expect(body).toContain('Reader-facing summary is missing.');
  });
});
