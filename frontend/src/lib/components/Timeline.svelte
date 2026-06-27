<script lang="ts">
  import { browser } from '$app/environment';
  import { afterUpdate, onMount } from 'svelte';
  import type { Event } from '$lib/types/soundatlas';

  export let routeStartYear = 1965;
  export let routeEndYear = 1985;
  export let eventStartYear: number | null = null;
  export let eventEndYear: number | null = null;
  export let events: Event[] = [];
  export let selectedEventId: string | null = null;
  export let onSelectEvent: (eventId: string) => void = () => {};

  let eventListElement: HTMLDivElement | null = null;
  let eventListResizeVersion = 0;
  let lastCenteredKey: string | null = null;
  let centerAnimationFrame: number | null = null;

  $: axisStart = Math.min(routeStartYear, routeEndYear);
  $: axisEnd = Math.max(routeStartYear, routeEndYear);
  $: axisSpan = Math.max(axisEnd - axisStart, 1);
  $: hasEventRange = eventStartYear !== null && eventEndYear !== null;
  $: highlightedStartYear = hasEventRange
    ? Math.max(axisStart, Math.min(eventStartYear, eventEndYear))
    : axisStart;
  $: highlightedEndYear = hasEventRange
    ? Math.min(axisEnd, Math.max(eventStartYear, eventEndYear))
    : axisStart;
  $: highlightedStart = ((highlightedStartYear - axisStart) / axisSpan) * 100;
  $: highlightedWidth = Math.max(((highlightedEndYear - highlightedStartYear) / axisSpan) * 100, 0);
  $: selectedEventCenteringKey = selectedEventId
    ? `${selectedEventId}:${events.length}:${eventListResizeVersion}`
    : '';
  onMount(() => {
    if (!eventListElement || typeof ResizeObserver === 'undefined') {
      return;
    }

    const observer = new ResizeObserver(() => {
      eventListResizeVersion += 1;
    });

    observer.observe(eventListElement);

    return () => {
      if (centerAnimationFrame !== null) {
        cancelAnimationFrame(centerAnimationFrame);
      }
      observer.disconnect();
    };
  });

  afterUpdate(() => {
    if (!browser || !eventListElement || !selectedEventCenteringKey) {
      return;
    }

    if (selectedEventCenteringKey === lastCenteredKey) {
      return;
    }

    if (centerAnimationFrame !== null) {
      cancelAnimationFrame(centerAnimationFrame);
    }

    const centeringKey = selectedEventCenteringKey;
    centerAnimationFrame = requestAnimationFrame(() => {
      centerAnimationFrame = null;
      void centerSelectedEvent(centeringKey);
    });
  });

  function toPercent(year: number): number {
    return ((year - axisStart) / axisSpan) * 100;
  }

  function formatEventYears(event: Event): string {
    return event.year_start === event.year_end
      ? `${event.year_start}`
      : `${event.year_start}-${event.year_end}`;
  }

  async function centerSelectedEvent(centeringKey: string): Promise<void> {
    if (!selectedEventId || !eventListElement) {
      return;
    }

    const selectedButton = eventListElement.querySelector<HTMLButtonElement>(
      `button[data-event-id="${selectedEventId}"]`
    );

    if (!selectedButton) {
      return;
    }

    const containerRect = eventListElement.getBoundingClientRect();
    const buttonRect = selectedButton.getBoundingClientRect();
    const desiredScrollLeft =
      eventListElement.scrollLeft +
      (buttonRect.left - containerRect.left) -
      (containerRect.width - buttonRect.width) / 2;
    const maxScrollLeft = eventListElement.scrollWidth - eventListElement.clientWidth;

    eventListElement.scrollLeft = Math.max(0, Math.min(maxScrollLeft, desiredScrollLeft));
    lastCenteredKey = centeringKey;
  }
</script>

<section class="timeline" aria-label="Timeline">
  <div class="track">
    <div class="axis">
      <div class="line"></div>
      {#if hasEventRange}
        <div
          class="highlight"
          style:left={`${Math.max(0, Math.min(100, highlightedStart))}%`}
          style:width={`${Math.max(0, Math.min(100, highlightedWidth))}%`}
        ></div>
      {/if}
      <div class="tick start" style:left={`${toPercent(axisStart)}%`} aria-hidden="true"></div>
      <div class="tick end" style:left={`${toPercent(axisEnd)}%`} aria-hidden="true"></div>

      <!-- @todo Switch to clustered or compact ticks when route event density makes labels overlap. -->
      {#each events as event}
        <button
          class:active={selectedEventId === event.id}
          class="event-tick"
          type="button"
          style:left={`${Math.max(0, Math.min(100, toPercent(event.year_start)))}%`}
          aria-label={`Select ${event.title}, ${formatEventYears(event)}`}
          aria-pressed={selectedEventId === event.id}
          title={`${event.title} (${formatEventYears(event)})`}
          on:click={() => onSelectEvent(event.id)}
        >
          <span>{event.year_start}</span>
        </button>
      {/each}
    </div>

    <div class="labels" aria-hidden="true">
      <span>{axisStart}</span>
      <span>{axisEnd}</span>
    </div>

    {#if events.length > 0}
      <!-- @todo Revisit this horizontal list when future routes contain many more events. -->
      <div bind:this={eventListElement} class="event-list" aria-label="Route events">
        {#each events as event}
          <button
            class:active={selectedEventId === event.id}
            data-event-id={event.id}
            type="button"
            on:click={() => onSelectEvent(event.id)}
          >
            <span>{formatEventYears(event)}</span>
            <strong>{event.title}</strong>
            {#if selectedEventId === event.id}
              <em>Selected</em>
            {/if}
          </button>
        {/each}
      </div>
    {:else}
      <p class="empty">No events for this route.</p>
    {/if}
  </div>

</section>

<style>
  .timeline {
    display: grid;
    gap: 0.65rem;
    padding: 0.85rem 1rem;
    border-top: 1px solid #d9e0e7;
    background: linear-gradient(180deg, #ffffff 0%, #f9fbfc 100%);
  }

  .track {
    display: grid;
    gap: 0.55rem;
  }

  .axis {
    position: relative;
    height: 3rem;
  }

  .line {
    position: absolute;
    inset: 50% 0 auto;
    height: 0.25rem;
    transform: translateY(-50%);
    border-radius: 999px;
    background: linear-gradient(90deg, #d3dce5 0%, #b8c5d1 100%);
  }

  .highlight {
    position: absolute;
    inset: 50% auto auto;
    height: 0.75rem;
    min-width: 0.85rem;
    transform: translateY(-50%);
    border-radius: 999px;
    background: linear-gradient(90deg, #e4572e 0%, #ef8c63 100%);
    box-shadow: 0 0 0 1px rgba(228, 87, 46, 0.15);
  }

  .tick {
    position: absolute;
    top: 50%;
    width: 0.7rem;
    height: 0.7rem;
    transform: translate(-50%, -50%);
    border: 2px solid #17202a;
    border-radius: 999px;
    background: #ffffff;
  }

  .event-tick {
    position: absolute;
    top: 50%;
    display: grid;
    place-items: center;
    width: 1.65rem;
    height: 1.65rem;
    padding: 0;
    transform: translate(-50%, -50%);
    border: 2px solid #ffffff;
    border-radius: 999px;
    background: #314151;
    color: #ffffff;
    box-shadow: 0 0 0 1px rgba(23, 32, 42, 0.22);
  }

  .event-tick:hover,
  .event-tick:focus-visible {
    background: #17202a;
    outline: none;
  }

  .event-tick.active {
    z-index: 2;
    width: 2.1rem;
    height: 2.1rem;
    background: #e4572e;
    box-shadow:
      0 0 0 3px rgba(228, 87, 46, 0.22),
      0 6px 18px rgba(23, 32, 42, 0.18);
  }

  .event-tick span {
    font-size: 0.58rem;
    font-weight: 800;
    line-height: 1;
  }

  .labels {
    display: flex;
    align-items: center;
    justify-content: space-between;
    color: #536170;
    font-size: 0.8rem;
  }

  .event-list {
    display: flex;
    gap: 0.45rem;
    overflow-x: auto;
    padding-bottom: 0.15rem;
  }

  .event-list button {
    flex: 0 0 12rem;
    display: grid;
    gap: 0.15rem;
    min-height: 3.1rem;
    padding: 0.55rem 0.65rem;
    border: 1px solid #d9e0e7;
    border-radius: 8px;
    background: #ffffff;
    color: #314151;
    text-align: left;
  }

  .event-list button:hover,
  .event-list button:focus-visible {
    border-color: #17202a;
    outline: none;
  }

  .event-list button.active {
    border-color: #e4572e;
    background: #fff7f4;
    box-shadow: inset 0 0 0 1px rgba(228, 87, 46, 0.24);
  }

  .event-list span {
    color: #6b7785;
    font-size: 0.72rem;
    font-weight: 800;
  }

  .event-list strong {
    color: #17202a;
    font-size: 0.82rem;
    line-height: 1.25;
  }

  .event-list em {
    width: max-content;
    color: #bb3f22;
    font-size: 0.68rem;
    font-style: normal;
    font-weight: 800;
    letter-spacing: 0.06em;
    text-transform: uppercase;
  }

  .empty {
    margin: 0;
    color: #6b7785;
    font-size: 0.85rem;
  }

</style>
