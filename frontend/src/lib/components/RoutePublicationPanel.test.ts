import { render } from 'svelte/server';
import { describe, expect, it } from 'vitest';
import RoutePublicationPanel from './RoutePublicationPanel.svelte';

describe('RoutePublicationPanel', () => {
  it('labels route readiness and separates non-blocking warnings', () => {
    const { body } = render(RoutePublicationPanel, {
      props: {
        summary: {
          route_id: 'birth-of-hip-hop',
          revision_id: 'revision-1',
          source: 'complete-draft.json',
          included_events: [
            {
              candidate_id: 'review-event',
              title: 'Review event',
              editorial_state: 'draft',
              included: true
            }
          ],
          excluded_event_ids: ['excluded-event'],
          warnings: ['Check the historical wording.'],
          technical_errors: [],
          route_warnings: ['Check the route chronology.'],
          route_technical_errors: [],
          included_event_warning_count: 1,
          included_event_technical_error_count: 0,
          technical_ready: true,
          published_revision_id: null
        }
      }
    });

    expect(body).toContain('Route action');
    expect(body).toContain('Ready to publish');
    expect(body).toContain('Included events');
    expect(body).toContain('Excluded events');
    expect(body).toContain('Event warnings');
    expect(body).toContain('Route editorial warnings (1)');
    expect(body).toContain('Check the route chronology.');
    expect(body).not.toContain('Check the historical wording.');
    expect(body).toContain('Publish exact reviewed route');
  });

  it('labels blocking errors and disables publication', () => {
    const { body } = render(RoutePublicationPanel, {
      props: {
        summary: {
          route_id: 'birth-of-hip-hop',
          revision_id: 'revision-1',
          source: 'complete-draft.json',
          included_events: [],
          excluded_event_ids: [],
          warnings: [],
          technical_errors: [
            'Route reference is unresolved.',
            'review-event: Event story is incomplete.'
          ],
          route_warnings: [],
          route_technical_errors: ['Route reference is unresolved.'],
          included_event_warning_count: 0,
          included_event_technical_error_count: 1,
          technical_ready: false,
          published_revision_id: null
        }
      }
    });

    expect(body).toContain('Publication blocked');
    expect(body).toContain('Route blocking errors');
    expect(body).toContain('Route reference is unresolved.');
    expect(body).toContain('Event blocking errors');
    expect(body).not.toContain('Event story is incomplete.');
    expect(body).toContain('disabled');
  });
});
