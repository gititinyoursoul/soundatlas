<script lang="ts">
  import type {
    Connection,
    Event,
    MediaProvider,
    MediaType,
    Place,
    Route
  } from '$lib/types/soundatlas';

  export let event: Event | null = null;
  export let place: Place | null = null;
  export let route: Route | null = null;
  export let connections: Connection[] = [];
  export let previousEvent: Event | null = null;
  export let nextEvent: Event | null = null;
  export let currentEventIndex = 0;
  export let eventCount = 0;
  export let isLoading = false;
  export let errorMessage: string | null = null;
  export let onNavigateEvent: (eventId: string) => void = () => {};

  const providerLabels: Record<MediaProvider, string> = {
    youtube: 'YouTube',
    spotify: 'Spotify',
    qobuz: 'Qobuz'
  };

  function formatMediaLinkLabel(provider: MediaProvider, type: MediaType): string {
    return `${providerLabels[provider]} ${type}`;
  }
</script>

<aside class="story-panel" aria-label="Event details">
  {#if isLoading}
    <div class="empty">
      <h2>Loading route events</h2>
      <p>Fetching curated places, events, sources, and media links.</p>
    </div>
  {:else if errorMessage}
    <div class="empty error">
      <h2>Event details unavailable</h2>
      <p>{errorMessage}</p>
    </div>
  {:else if event}
    <header class="inspector-header">
      <div class="eyebrow">
        <span>Selected event</span>
        <span>{currentEventIndex + 1} / {eventCount}</span>
      </div>

      <h2>{event.title}</h2>

      <dl class="event-meta">
        <div>
          <dt>Year</dt>
          <dd>{event.year_start}{event.year_start !== event.year_end ? `-${event.year_end}` : ''}</dd>
        </div>
        {#if place}
          <div>
            <dt>Place</dt>
            <dd>{place.name}, {place.borough}</dd>
          </div>
        {/if}
        {#if route}
          <div>
            <dt>Route</dt>
            <dd><span class="route-dot" style={`--route-color: ${route.color}`}></span>{route.title}</dd>
          </div>
        {/if}
      </dl>

      <nav class="event-nav" aria-label="Event navigation">
        <button
          type="button"
          disabled={!previousEvent}
          on:click={() => previousEvent && onNavigateEvent(previousEvent.id)}
        >
          Previous
        </button>
        <button
          type="button"
          disabled={!nextEvent}
          on:click={() => nextEvent && onNavigateEvent(nextEvent.id)}
        >
          Next
        </button>
      </nav>
    </header>

    <section class="detail-block">
      <h3>What happened</h3>
      <p>{event.summary}</p>
    </section>

    <section class="detail-block emphasis">
      <h3>Why it matters</h3>
      <p>{event.significance}</p>
    </section>

    {#if connections.length > 0}
      <details class="foldout">
        <summary>Connections</summary>
        <ul>
          {#each connections as connection}
            <li>{connection.summary}</li>
          {/each}
        </ul>
      </details>
    {/if}

    {#if event.source_urls.length > 0 || event.media_links.length > 0}
      <section class="resources">
        <h3>Sources and media</h3>
        <ul class="links">
          {#each event.source_urls as sourceUrl, index}
            <li><a href={sourceUrl} target="_blank" rel="noreferrer">Source {index + 1}</a></li>
          {/each}
          {#each event.media_links as mediaLink}
            <li>
              <a href={mediaLink.url} target="_blank" rel="noreferrer">
                {formatMediaLinkLabel(mediaLink.provider, mediaLink.type)}
              </a>
            </li>
          {/each}
        </ul>
      </section>
    {/if}
  {:else}
    <div class="empty">
      <h2>Select an event</h2>
      <p>Select a timeline item or map marker to see context, significance, and connections.</p>
    </div>
  {/if}
</aside>

<style>
  .story-panel {
    display: grid;
    align-content: start;
    gap: 0.85rem;
    min-height: 0;
    padding: 1rem;
    overflow: auto;
    border-left: 1px solid #d9e0e7;
    background: #fbfcfd;
  }

  .inspector-header,
  .detail-block,
  .foldout,
  .resources {
    border: 1px solid #e0e6ec;
    border-radius: 8px;
    background: #ffffff;
  }

  .inspector-header {
    display: grid;
    gap: 0.85rem;
    padding: 0.95rem;
  }

  .eyebrow {
    display: flex;
    flex-wrap: wrap;
    gap: 0.5rem;
    align-items: center;
    color: #6b7785;
    font-size: 0.75rem;
    font-weight: 700;
  }

  .route-dot {
    display: inline-block;
    width: 0.65rem;
    height: 0.65rem;
    margin-right: 0.35rem;
    border: 1px solid #17202a;
    border-radius: 999px;
    background: var(--route-color);
    vertical-align: -0.05rem;
  }

  h2,
  h3,
  p {
    margin: 0;
  }

  h2 {
    color: #17202a;
    font-size: clamp(1.1rem, 1.35vw, 1.45rem);
    line-height: 1.15;
  }

  h3 {
    color: #314151;
    font-size: 0.78rem;
    font-weight: 800;
    letter-spacing: 0.06em;
    text-transform: uppercase;
  }

  p,
  li {
    color: #536170;
    font-size: 0.9rem;
    line-height: 1.45;
  }

  .event-meta {
    display: grid;
    gap: 0.55rem;
    margin: 0;
  }

  .event-meta div {
    display: grid;
    gap: 0.1rem;
  }

  dt {
    color: #6b7785;
    font-size: 0.72rem;
    font-weight: 800;
    letter-spacing: 0.06em;
    text-transform: uppercase;
  }

  dd {
    margin: 0;
    color: #314151;
    font-size: 0.88rem;
    font-weight: 700;
    line-height: 1.3;
  }

  .detail-block {
    display: grid;
    gap: 0.4rem;
    padding: 0.85rem;
  }

  .detail-block.emphasis {
    border-color: #efc8be;
    background: #fff7f4;
  }

  .event-nav {
    display: flex;
    align-items: center;
    gap: 0.5rem;
  }

  .event-nav button {
    flex: 1 1 0;
    min-width: 0;
    padding: 0.5rem 0.6rem;
    border: 1px solid #cfd7df;
    border-radius: 8px;
    background: #ffffff;
    color: #314151;
    font-size: 0.85rem;
    font-weight: 700;
  }

  .event-nav button:not(:disabled):hover {
    border-color: #17202a;
  }

  .event-nav button:disabled {
    cursor: not-allowed;
    opacity: 0.45;
  }

  .foldout {
    padding: 0.8rem 0.85rem;
  }

  summary {
    cursor: pointer;
    color: #314151;
    font-size: 0.8rem;
    font-weight: 800;
    letter-spacing: 0.06em;
    text-transform: uppercase;
  }

  ul {
    display: grid;
    gap: 0.4rem;
    margin: 0;
    padding-left: 1.15rem;
  }

  .resources {
    display: grid;
    gap: 0.55rem;
    padding: 0.85rem;
  }

  .links {
    display: flex;
    flex-wrap: wrap;
    gap: 0.4rem;
    padding: 0;
    list-style: none;
  }

  a {
    display: inline-flex;
    align-items: center;
    min-height: 1.8rem;
    padding: 0.25rem 0.5rem;
    border: 1px solid #efc8be;
    border-radius: 999px;
    background: #fff7f4;
    color: #bb3f22;
    font-size: 0.78rem;
    font-weight: 700;
    text-decoration: none;
  }

  .empty {
    display: grid;
    gap: 0.5rem;
    color: #536170;
  }

  .empty.error h2,
  .empty.error p {
    color: #8f2d16;
  }
</style>
