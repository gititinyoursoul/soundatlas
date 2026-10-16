import { render } from 'svelte/server';
import { describe, expect, it } from 'vitest';
import { makeEvent } from '$lib/test/fixtures';
import Timeline from './Timeline.svelte';

function routeEventCards(body: string): string[] {
  const list =
    body.match(
      /<div\b[^>]*aria-label="Route events"[^>]*>([\s\S]*?)<\/div>/
    )?.[1] ?? '';
  return [...list.matchAll(/<button\b[^>]*>[\s\S]*?<\/button>/g)].map(
    ([card]) => card
  );
}

describe('Timeline route chronology', () => {
  it('explains an empty route without rendering event controls', () => {
    const { body } = render(Timeline, { props: { events: [] } });

    expect(body).toContain('No events for this route.');
    expect(body).not.toContain('aria-label="Route events"');
    expect(body).not.toContain('class="event-tick ');
  });

  it('shows route events in supplied sequence with their years', () => {
    const { body } = render(Timeline, {
      props: {
        events: [
          makeEvent({
            id: 'early',
            title: 'Early gathering',
            year_start: 1971,
            year_end: 1971
          }),
          makeEvent({
            id: 'later',
            title: 'Later party',
            year_start: 1973,
            year_end: 1974
          })
        ]
      }
    });

    const cards = routeEventCards(body);
    expect(cards).toHaveLength(2);
    expect(cards[0]).toMatch(/<span[^>]*>1971<\/span>/);
    expect(cards[0]).toMatch(/<strong[^>]*>Early gathering<\/strong>/);
    expect(cards[1]).toMatch(/<span[^>]*>1973-1974<\/span>/);
    expect(cards[1]).toMatch(/<strong[^>]*>Later party<\/strong>/);
  });

  it('marks the selected event in both the tick and event list', () => {
    const { body } = render(Timeline, {
      props: {
        events: [
          makeEvent({ id: 'first', title: 'First event' }),
          makeEvent({ id: 'selected', title: 'Selected event' })
        ],
        selectedEventId: 'selected'
      }
    });

    expect(body).toMatch(
      /aria-label="Select Selected event, 1973"[^>]*aria-pressed="true"/
    );
    expect(body).toMatch(
      /aria-label="Select First event, 1973"[^>]*aria-pressed="false"/
    );
    const cards = routeEventCards(body);
    expect(cards).toHaveLength(2);
    expect(cards[0]).toMatch(/<strong[^>]*>First event<\/strong>/);
    expect(cards[0]).not.toMatch(/<em[^>]*>Selected<\/em>/);
    expect(cards[1]).toMatch(/<strong[^>]*>Selected event<\/strong>/);
    expect(cards[1]).toMatch(/<em[^>]*>Selected<\/em>/);
  });

  it('identifies context events in accessible and visible labels', () => {
    const { body } = render(Timeline, {
      props: {
        events: [
          makeEvent({
            id: 'context',
            title: 'Earlier influence',
            year_start: 1967,
            year_end: 1968,
            route_entry_role: 'context'
          })
        ]
      }
    });

    expect(body).toContain(
      'aria-label="Select route context Earlier influence, 1967-1968"'
    );
    expect(body).toContain('Route context: Earlier influence');
  });

  it('renders the selected date range on the route axis', () => {
    const { body } = render(Timeline, {
      props: {
        routeStartYear: 1970,
        routeEndYear: 1980,
        eventStartYear: 1972,
        eventEndYear: 1975
      }
    });
    const withoutRange = render(Timeline, {
      props: { routeStartYear: 1970, routeEndYear: 1980 }
    });

    expect(body).toMatch(/class="highlight [^"]+"[^>]*left: 20%; width: 30%;/);
    expect(withoutRange.body).not.toContain('class="highlight ');
  });
});
