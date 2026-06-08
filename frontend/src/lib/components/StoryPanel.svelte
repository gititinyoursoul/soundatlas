<script lang="ts">
  import type { Connection, Event, Place, Route } from '$lib/types/soundatlas';

  export let event: Event | null = null;
  export let place: Place | null = null;
  export let route: Route | null = null;
  export let connections: Connection[] = [];
</script>

<aside class="story-panel" aria-label="Eventdetails">
  {#if event}
    <div class="eyebrow">
      <span>{event.year_start}{event.year_start !== event.year_end ? `-${event.year_end}` : ''}</span>
      {#if route}
        <span class="route" style={`--route-color: ${route.color}`}>{route.title}</span>
      {/if}
    </div>

    <h2>{event.title}</h2>

    {#if place}
      <p class="place">{place.name}, {place.borough}</p>
    {/if}

    <section>
      <h3>Was passiert?</h3>
      <p>{event.summary}</p>
    </section>

    <section>
      <h3>Warum wichtig?</h3>
      <p>{event.significance}</p>
    </section>

    {#if connections.length > 0}
      <section>
        <h3>Verbindungen</h3>
        <ul>
          {#each connections as connection}
            <li>{connection.summary}</li>
          {/each}
        </ul>
      </section>
    {/if}

    {#if event.source_urls.length > 0 || event.media_links.length > 0}
      <section>
        <h3>Quellen und Medien</h3>
        <ul class="links">
          {#each event.source_urls as sourceUrl}
            <li><a href={sourceUrl} target="_blank" rel="noreferrer">Quelle</a></li>
          {/each}
          {#each event.media_links as mediaLink}
            <li><a href={mediaLink} target="_blank" rel="noreferrer">Medium</a></li>
          {/each}
        </ul>
      </section>
    {/if}
  {:else}
    <div class="empty">
      <h2>Event auswählen</h2>
      <p>Klicke einen Marker auf der Karte, um Kontext, Bedeutung und Verbindungen zu sehen.</p>
    </div>
  {/if}
</aside>

<style>
  .story-panel {
    display: grid;
    align-content: start;
    gap: 1rem;
    min-height: 0;
    padding: 1.25rem;
    overflow: auto;
    border-left: 1px solid #d9e0e7;
    background: #ffffff;
  }

  .eyebrow {
    display: flex;
    flex-wrap: wrap;
    gap: 0.5rem;
    align-items: center;
    color: #6b7785;
    font-size: 0.82rem;
    font-weight: 700;
  }

  .route {
    padding: 0.15rem 0.45rem;
    border-radius: 999px;
    background: var(--route-color);
    color: #ffffff;
  }

  h2,
  h3,
  p {
    margin: 0;
  }

  h2 {
    color: #17202a;
    font-size: clamp(1.4rem, 2vw, 2rem);
    line-height: 1.1;
  }

  h3 {
    margin-bottom: 0.35rem;
    color: #314151;
    font-size: 0.9rem;
  }

  p,
  li {
    color: #536170;
    line-height: 1.5;
  }

  .place {
    color: #314151;
    font-weight: 700;
  }

  ul {
    display: grid;
    gap: 0.4rem;
    margin: 0;
    padding-left: 1.15rem;
  }

  .links {
    display: flex;
    flex-wrap: wrap;
    gap: 0.5rem;
    padding: 0;
    list-style: none;
  }

  a {
    color: #bb3f22;
    font-weight: 700;
  }

  .empty {
    display: grid;
    gap: 0.5rem;
    color: #536170;
  }
</style>
