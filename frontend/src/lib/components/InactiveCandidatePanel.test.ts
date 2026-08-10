import { render } from 'svelte/server';
import { describe, expect, it } from 'vitest';
import type { ConsideredCandidateProjection } from '$lib/data/editorial-review';
import InactiveCandidatePanel from './InactiveCandidatePanel.svelte';

function candidate(
  overrides: Partial<ConsideredCandidateProjection> = {}
): ConsideredCandidateProjection {
  return {
    title: 'Outline context event',
    summary: 'Context that remains reviewable.',
    significance: 'It explains the wider route setting.',
    years: '1973',
    place: '1520 Sedgwick Avenue',
    account: {
      candidate_id: 'outline-context-event',
      outcome: 'omitted',
      reason: 'Covered by the active route sequence.',
      related_candidate_ids: ['kool-herc-sedgwick-party'],
      active: false,
      preview: {},
      context: {
        route_function: 'Context',
        decision_rationale: 'Preserves chronology.',
        status: 'maybe',
        source_leads: ['Interview archive'],
        risk_notes: ['Compare source dates.'],
        claims: ['The setting shaped later parties.']
      },
      findings: [
        {
          owner: 'candidate_composition',
          message: 'Retained as inactive context.',
          blocking: false
        }
      ]
    },
    ...overrides
  };
}

describe('InactiveCandidatePanel', () => {
  it('renders read-only inactive Candidate content and composition context', () => {
    const { body } = render(InactiveCandidatePanel, {
      props: { candidate: candidate() }
    });

    expect(body).toContain('Other considered candidate · Not in current route');
    expect(body).toContain('Outline context event');
    expect(body).toContain('Context that remains reviewable.');
    expect(body).toContain('Covered by the active route sequence.');
    expect(body).toContain('Retained as inactive context.');
    expect(body).toContain('revision request boundary in #85');
    expect(body).not.toContain('Draft');
    expect(body).not.toContain('Approved');
    expect(body).not.toContain('Don’t use');
  });

  it('states unresolved time and place without fabricating values', () => {
    const { body } = render(InactiveCandidatePanel, {
      props: {
        candidate: candidate({ years: null, place: null })
      }
    });

    expect(body).toContain('Timeframe: Unresolved · Place: Unresolved');
  });
});
