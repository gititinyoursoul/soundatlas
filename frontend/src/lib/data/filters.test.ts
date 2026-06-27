import { describe, expect, it } from 'vitest';
import { makeEvent } from '$lib/test/fixtures';
import { filterEvents } from './filters';

describe('filterEvents', () => {
  const events = [
    makeEvent({ id: 'first-bronx-party', route_id: 'birth-of-hip-hop' }),
    makeEvent({ id: 'downtown-loft-scene', route_id: 'downtown-experiment' })
  ];

  it('returns every event when no route is selected', () => {
    expect(filterEvents(events, null).map((event) => event.id)).toEqual([
      'first-bronx-party',
      'downtown-loft-scene'
    ]);
  });

  it('returns only events for the selected route', () => {
    expect(filterEvents(events, 'birth-of-hip-hop').map((event) => event.id)).toEqual([
      'first-bronx-party'
    ]);
  });
});
