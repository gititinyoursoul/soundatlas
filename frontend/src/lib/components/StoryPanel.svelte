<script lang="ts">
  import Icon from '$lib/components/Icon.svelte';
  import MediaEmbed from '$lib/components/MediaEmbed.svelte';
  import { resolvePreviewItemId } from '$lib/components/story-preview';
  import { parseYouTubeEmbed, type YouTubeEmbed } from '$lib/media/youtube';
  import type {
    Event,
    ImageLink,
    MediaLink,
    MediaProvider,
    MediaType,
    Place,
    Route,
    StoryConnectionItem
  } from '$lib/types/soundatlas';

  type InspectorTab = 'story' | 'media' | 'related';

  type PreviewItem =
    | {
        id: string;
        kind: 'image';
        title: string;
        subtitle: string;
        selectionUrl: string;
        previewUrl: string;
        imageLink: ImageLink;
      }
    | {
        id: string;
        kind: 'media';
        title: string;
        subtitle: string;
        selectionUrl: string;
        previewUrl?: string | null;
        mediaLink: MediaLink;
        embed: YouTubeEmbed | null;
      };

  export let event: Event | null = null;
  export let place: Place | null = null;
  export let route: Route | null = null;
  export let connections: StoryConnectionItem[] = [];
  export let previousEvent: Event | null = null;
  export let nextEvent: Event | null = null;
  export let isLoading = false;
  export let errorMessage: string | null = null;
  export let onNavigateEvent: (eventId: string, routeId?: string) => void = () => {};
  export let initialTab: InspectorTab = 'story';
  export let selectedPreviewUrl: string | null = null;
  export let showReviewActions = true;

  const mediaProviderLabels: Record<MediaProvider, string> = {
    youtube: 'YouTube',
    spotify: 'Spotify',
    qobuz: 'Qobuz'
  };

  const imageProviderLabels: Record<string, string> = {
    wikimedia: 'Wikimedia Commons',
    loc: 'Library of Congress',
    nypl: 'NYPL',
    internet_archive: 'Internet Archive',
    cover_art_archive: 'Cover Art Archive',
    manual: 'Manual'
  };

  const sourceHostLabels: Record<string, string> = {
    'americanhistory.si.edu': 'Smithsonian National Museum of American History',
    'arts.gov': 'National Endowment for the Arts',
    'britannica.com': 'Britannica',
    'bronxriver.org': 'Bronx River Alliance',
    'cinema.cornell.edu': 'Cornell Cinema',
    'citylore.org': 'City Lore',
    'en.wikipedia.org': 'Wikipedia',
    'filmlinc.org': 'Film at Lincoln Center',
    'history.com': 'History',
    'latimes.com': 'Los Angeles Times',
    'museumofplay.org': 'The Strong National Museum of Play',
    'namm.org': 'NAMM Oral History',
    'osti.gov': 'OSTI',
    'pbs.org': 'PBS',
    'pitchfork.com': 'Pitchfork',
    'rockhall.com': 'Rock & Roll Hall of Fame',
    'si.edu': 'Smithsonian',
    'soundonsound.com': 'Sound on Sound'
  };

  let activeTab: InspectorTab = 'story';
  let selectedPreviewId = '';
  let lastEventId: string | null = null;

  $: previewItems = buildPreviewItems(event);
  $: if (event?.id !== lastEventId) {
    lastEventId = event?.id ?? null;
    activeTab = initialTab;
    selectedPreviewId = resolvePreviewItemId(previewItems, selectedPreviewUrl);
  }
  $: if (event?.id === lastEventId && activeTab !== initialTab && initialTab !== 'story') {
    activeTab = initialTab;
  }
  $: if (selectedPreviewUrl) {
    const resolvedPreviewItemId = resolvePreviewItemId(previewItems, selectedPreviewUrl);
    if (resolvedPreviewItemId && resolvedPreviewItemId !== selectedPreviewId) {
      selectedPreviewId = resolvedPreviewItemId;
    }
  }
  $: if (previewItems.length > 0 && !previewItems.some((item) => item.id === selectedPreviewId)) {
    selectedPreviewId = previewItems[0].id;
  }
  $: selectedPreviewItem = previewItems.find((item) => item.id === selectedPreviewId) ?? null;
  $: mediaCount = event?.media_links.length ?? 0;
  $: imageCount = event?.image_links.length ?? 0;
  $: connectionCount = connections.length;

  function buildPreviewItems(currentEvent: Event | null): PreviewItem[] {
    if (!currentEvent) {
      return [];
    }

    const imageItems = currentEvent.image_links.map<PreviewItem>((imageLink) => ({
      id: `image:${imageLink.image_url}`,
      kind: 'image',
      title: imageLink.title,
      subtitle: formatImageDescriptor(imageLink.provider, imageLink.type),
      selectionUrl: imageLink.image_url,
      previewUrl: imageLink.thumbnail_url ?? imageLink.image_url,
      imageLink
    }));

    const mediaItems = currentEvent.media_links.map<PreviewItem>((mediaLink) => ({
      id: `media:${mediaLink.url}`,
      kind: 'media',
      title: mediaLink.title,
      subtitle: formatMediaDescriptor(mediaLink.provider, mediaLink.type),
      selectionUrl: mediaLink.url,
      previewUrl: mediaLink.url,
      mediaLink,
      embed: mediaLink.playback_mode === 'external' ? null : parseYouTubeEmbed(mediaLink.url)
    }));

    return [...imageItems, ...mediaItems];
  }

  function formatMediaDescriptor(provider: MediaProvider, type: MediaType): string {
    return `${mediaProviderLabels[provider]} ${humanize(type)}`;
  }

  function formatImageDescriptor(provider: string, type: string): string {
    return `${imageProviderLabels[provider] ?? humanize(provider)} ${humanize(type)}`;
  }

  function humanize(value: string): string {
    return value
      .split('_')
      .filter(Boolean)
      .map((part) => part.charAt(0).toUpperCase() + part.slice(1))
      .join(' ');
  }

  function formatEventYears(currentEvent: Event): string {
    return currentEvent.year_start === currentEvent.year_end
      ? `${currentEvent.year_start}`
      : `${currentEvent.year_start}-${currentEvent.year_end}`;
  }

  function selectTab(tab: InspectorTab): void {
    activeTab = tab;
  }

  function formatConnectionMeta(connection: StoryConnectionItem): string {
    const parts = [formatEventYears(connection.event)];

    if (connection.place) {
      parts.push(connection.place.name);
    }

    if (connection.route) {
      parts.push(connection.route.title);
    }

    return parts.join(' • ');
  }

  function formatConnectionType(connection: StoryConnectionItem): string {
    return humanize(connection.type);
  }

  function formatSourceLabel(sourceUrl: string): string {
    try {
      const url = new URL(sourceUrl);
      const host = url.hostname.replace(/^www\./, '');
      const hostLabel = sourceHostLabels[host] ?? sourceHostLabels[getBaseHost(host)];

      if (hostLabel) {
        return hostLabel;
      }

      return getBaseHost(host)
        .split('.')
        .filter((part) => part !== 'com' && part !== 'org' && part !== 'gov' && part !== 'edu')
        .map((part) => humanize(part.replace(/-/g, '_')))
        .join(' ');
    } catch {
      return sourceUrl;
    }
  }

  function getBaseHost(host: string): string {
    const parts = host.split('.');

    if (parts.length <= 2) {
      return host;
    }

    return parts.slice(-2).join('.');
  }

  function formatEventMeta(currentEvent: Event, currentPlace: Place | null, currentRoute: Route | null): string {
    const parts = [formatEventYears(currentEvent)];

    if (currentPlace) {
      parts.push(`${currentPlace.name}, ${currentPlace.borough}`);
    }

    if (currentRoute) {
      parts.push(currentRoute.title);
    }

    return parts.join(' • ');
  }
</script>

<aside class="story-panel" aria-label="Event inspector">
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
      <div class="header-top">
        <div class="title-block">
          <h2>{event.title}</h2>
          <p class="event-meta-line">
            {#if route}
              <span class="meta-route">
                <span class="route-dot" style={`--route-color: ${route.color}`}></span>
                {formatEventMeta(event, place, route)}
              </span>
            {:else}
              {formatEventMeta(event, place, route)}
            {/if}
          </p>
        </div>
      </div>

      <div class="header-controls">
        <div class="inspector-tabs" role="tablist" aria-label="Inspector sections">
          <button
            id="inspector-tab-story"
            type="button"
            role="tab"
            class:active={activeTab === 'story'}
            aria-selected={activeTab === 'story'}
            aria-controls="inspector-panel-story"
            on:click={() => selectTab('story')}
          >
            Story
          </button>
          <button
            id="inspector-tab-media"
            type="button"
            role="tab"
            class:active={activeTab === 'media'}
            aria-selected={activeTab === 'media'}
            aria-controls="inspector-panel-media"
            on:click={() => selectTab('media')}
          >
            Media
            <span>{mediaCount + imageCount}</span>
          </button>
          <button
            id="inspector-tab-related"
            type="button"
            role="tab"
            class:active={activeTab === 'related'}
            aria-selected={activeTab === 'related'}
            aria-controls="inspector-panel-related"
            on:click={() => selectTab('related')}
          >
            Related
            <span>{connectionCount}</span>
          </button>
        </div>

        <nav class="event-nav" aria-label="Event navigation">
          <button
            type="button"
            disabled={!previousEvent}
            aria-label="Previous event"
            data-tooltip={previousEvent?.title}
            on:click={() => previousEvent && onNavigateEvent(previousEvent.id, previousEvent.route_id)}
          >
            <Icon name="chevron-left" />
            <span class="sr-only">Previous event</span>
          </button>
          <button
            type="button"
            disabled={!nextEvent}
            aria-label="Next event"
            data-tooltip={nextEvent?.title}
            on:click={() => nextEvent && onNavigateEvent(nextEvent.id, nextEvent.route_id)}
          >
            <Icon name="chevron-right" />
            <span class="sr-only">Next event</span>
          </button>
        </nav>
      </div>

    </header>

    <div class="inspector-body">
      {#if activeTab === 'story'}
        <div
          id="inspector-panel-story"
          role="tabpanel"
          aria-labelledby="inspector-tab-story"
          class="tab-panel"
        >
          <section class="story-reading">
            <div class="story-copy">
              <h3>What happened</h3>
              <p>{event.summary}</p>
            </div>

            <aside class="significance-note" aria-label="Why it matters">
              <h3>Why it matters</h3>
              <p>{event.significance}</p>
            </aside>
          </section>

          <section class="story-sources">
            <h3>Sources</h3>
            {#if event.source_urls.length > 0}
              <ul class="source-list compact">
                {#each event.source_urls as sourceUrl}
                  <li>
                    <a href={sourceUrl} target="_blank" rel="noreferrer">
                      {formatSourceLabel(sourceUrl)}
                    </a>
                  </li>
                {/each}
              </ul>
            {:else}
              <p class="empty-inline">No source URLs have been added for this event yet.</p>
            {/if}
          </section>
        </div>
      {:else if activeTab === 'media'}
        <div
          id="inspector-panel-media"
          role="tabpanel"
          aria-labelledby="inspector-tab-media"
          class="tab-panel"
        >
          <section class="preview-shell" aria-label="Featured media preview">
            {#if selectedPreviewItem?.kind === 'image'}
              <figure class="image-preview">
                <div class="image-frame">
                  <img
                    src={selectedPreviewItem.previewUrl}
                    alt={selectedPreviewItem.imageLink.alt_text}
                    loading="lazy"
                  />
                </div>
                <figcaption>
                  <strong>{selectedPreviewItem.title}</strong>
                  <span>{selectedPreviewItem.subtitle}</span>
                </figcaption>
              </figure>
            {:else if selectedPreviewItem?.kind === 'media' && selectedPreviewItem.embed}
              <div class="embedded-media">
                <MediaEmbed
                  mediaLinks={[selectedPreviewItem.mediaLink]}
                  eventId={event.id}
                  {showReviewActions}
                />
              </div>
            {:else if selectedPreviewItem?.kind === 'media' && selectedPreviewItem.mediaLink.playback_mode === 'external'}
              <div class="external-media">
                <span class="external-media-badge">
                  {selectedPreviewItem.mediaLink.provider === 'youtube'
                    ? 'YouTube'
                    : selectedPreviewItem.subtitle}
                </span>
                <div>
                  <h3>{selectedPreviewItem.title}</h3>
                  <p>{selectedPreviewItem.subtitle}</p>
                </div>
                <a href={selectedPreviewItem.mediaLink.url} target="_blank" rel="noreferrer">
                  {selectedPreviewItem.mediaLink.provider === 'youtube'
                    ? 'Open on YouTube'
                    : 'Open media link'}
                </a>
              </div>
            {:else if selectedPreviewItem?.kind === 'media'}
              <div class="media-placeholder">
                <h3>{selectedPreviewItem.title}</h3>
                <p>{selectedPreviewItem.subtitle}</p>
                <a href={selectedPreviewItem.mediaLink.url} target="_blank" rel="noreferrer">
                  {selectedPreviewItem.mediaLink.provider === 'youtube'
                    ? 'Open on YouTube'
                    : 'Open media link'}
                </a>
              </div>
            {:else}
              <div class="media-placeholder">
                <h3>No media selected</h3>
                <p>Pick an image or media link below to inspect it here.</p>
              </div>
            {/if}
          </section>

          <section class="detail-block">
            <h3>Media to explore</h3>
            {#if previewItems.length > 0}
              <div class="preview-list" aria-label="Media thumbnails">
                {#each previewItems as previewItem}
                  <button
                    type="button"
                    class:active={selectedPreviewItem?.id === previewItem.id}
                    class="preview-chip"
                    on:click={() => (selectedPreviewId = previewItem.id)}
                  >
                    {#if previewItem.kind === 'image'}
                      <img src={previewItem.previewUrl} alt="" aria-hidden="true" loading="lazy" />
                    {:else}
                      <span class="preview-badge">{previewItem.embed ? 'Play' : 'Open'}</span>
                    {/if}
                    <span class="preview-text">
                      <strong>{previewItem.title}</strong>
                      <small>{previewItem.subtitle}</small>
                    </span>
                  </button>
                {/each}
              </div>
            {:else}
              <p class="empty-inline">No media has been added for this event yet.</p>
            {/if}
          </section>
        </div>
      {:else}
        <div
          id="inspector-panel-related"
          role="tabpanel"
          aria-labelledby="inspector-tab-related"
          class="tab-panel"
        >
          <section class="detail-block">
            <h3>Related events</h3>
            {#if connections.length > 0}
              <ul class="connection-list compact">
                {#each connections as connection}
                  <li>
                    <button
                      type="button"
                      class="connection-row"
                      on:click={() => onNavigateEvent(connection.event.id, connection.event.route_id)}
                    >
                      <span class="connection-kicker">
                        <span>{connection.directionLabel}</span>
                        <span>{formatConnectionType(connection)}</span>
                      </span>
                      <span class="connection-title">{connection.event.title}</span>
                      <span class="connection-meta">
                        {#if connection.route}
                          <span class="route-dot" style={`--route-color: ${connection.route.color}`}></span>
                        {/if}
                        {formatConnectionMeta(connection)}
                      </span>
                      <span class="connection-summary">{connection.summary}</span>
                    </button>
                  </li>
                {/each}
              </ul>
            {:else}
              <p class="empty-inline">No related events are attached to this event yet.</p>
            {/if}
          </section>
        </div>
      {/if}
    </div>
  {:else}
    <div class="empty">
      <h2>Select an event</h2>
      <p>Select a timeline item or map marker to see context, significance, media, and sources.</p>
    </div>
  {/if}
</aside>

<style>
  .story-panel {
    display: grid;
    align-content: start;
    min-height: 0;
    overflow: auto;
    border-left: 1px solid #d9e0e7;
    background: #fbfcfd;
  }

  .inspector-header {
    position: sticky;
    top: 0;
    z-index: 1;
    display: grid;
    gap: 0.6rem;
    padding: 0.9rem 1rem 0.7rem;
    border-bottom: 1px solid #d9e0e7;
    background: linear-gradient(180deg, #ffffff 0%, #fbfcfd 100%);
  }

  .header-top {
    display: grid;
    grid-template-columns: minmax(0, 1fr);
    align-items: start;
    gap: 0.4rem;
  }

  .header-controls {
    display: grid;
    grid-template-columns: minmax(0, 1fr) auto;
    align-items: center;
    gap: 0.65rem;
  }

  .inspector-body {
    display: grid;
    gap: 0.8rem;
    padding: 0.95rem 1rem 1rem;
  }

  .title-block {
    display: grid;
    gap: 0.18rem;
    min-width: 0;
  }

  .title-block h2,
  .title-block p,
  .detail-block h3,
  .detail-block p,
  .empty h2,
  .empty p {
    margin: 0;
  }

  .title-block h2 {
    color: #17202a;
    font-size: clamp(1.1rem, 1.35vw, 1.45rem);
    line-height: 1.15;
  }

  .title-block p {
    color: #6b7785;
    font-size: 0.8rem;
    font-weight: 600;
  }

  .event-meta-line,
  .meta-route {
    display: flex;
    flex-wrap: wrap;
    align-items: center;
    gap: 0.35rem;
  }

  .route-dot {
    display: inline-block;
    width: 0.65rem;
    height: 0.65rem;
    border: 1px solid #17202a;
    border-radius: 999px;
    background: var(--route-color);
    flex: 0 0 auto;
  }

  .inspector-tabs {
    display: grid;
    grid-template-columns: repeat(3, minmax(0, 1fr));
    gap: 0.3rem;
  }

  .inspector-tabs button {
    display: inline-flex;
    align-items: center;
    justify-content: space-between;
    gap: 0.5rem;
    min-width: 0;
    padding: 0.48rem 0.62rem;
    border: 1px solid #dde4eb;
    border-radius: 8px;
    background: #f7f9fb;
    color: #536170;
    font: inherit;
    font-size: 0.82rem;
    font-weight: 650;
  }

  .inspector-tabs button span {
    color: #6b7785;
    font-size: 0.72rem;
    font-weight: 800;
  }

  .inspector-tabs button.active,
  .inspector-tabs button[aria-selected='true'] {
    border-color: #17202a;
    background: #17202a;
    color: #ffffff;
  }

  .inspector-tabs button.active span,
  .inspector-tabs button[aria-selected='true'] span {
    color: #dbe5ee;
  }

  .event-nav {
    display: grid;
    grid-template-columns: repeat(2, 2.35rem);
    align-items: center;
    gap: 0.35rem;
  }

  .event-nav button {
    position: relative;
    display: grid;
    place-items: center;
    width: 2.35rem;
    min-width: 2.35rem;
    min-height: 2.1rem;
    padding: 0;
    border: 1px solid #dde4eb;
    border-radius: 8px;
    background: #f7f9fb;
    color: #536170;
    font: inherit;
    font-size: 0.8rem;
    font-weight: 700;
  }

  .event-nav button :global(.icon) {
    width: 0.95rem;
    height: 0.95rem;
  }

  .event-nav button[data-tooltip]:not(:disabled)::after {
    position: absolute;
    right: 0;
    bottom: calc(100% + 0.45rem);
    z-index: 2;
    width: max-content;
    max-width: min(18rem, 70vw);
    padding: 0.4rem 0.55rem;
    border: 1px solid #d7dfe7;
    border-radius: 6px;
    background: #17202a;
    color: #ffffff;
    content: attr(data-tooltip);
    font-size: 0.74rem;
    font-weight: 700;
    line-height: 1.25;
    opacity: 0;
    pointer-events: none;
    transform: translateY(0.2rem);
    transition:
      opacity 120ms ease,
      transform 120ms ease;
    white-space: normal;
  }

  .event-nav button[data-tooltip]:not(:disabled):hover::after,
  .event-nav button[data-tooltip]:not(:disabled):focus-visible::after {
    opacity: 1;
    transform: translateY(0);
  }

  .event-nav button:not(:disabled):hover,
  .inspector-tabs button:not(.active):hover {
    border-color: #17202a;
    background: #ffffff;
  }

  .event-nav button:disabled {
    cursor: not-allowed;
    opacity: 0.45;
  }

  .tab-panel {
    display: grid;
    gap: 0.8rem;
  }

  .detail-block,
  .preview-shell,
  .story-reading {
    display: grid;
    gap: 0.45rem;
    padding: 0.85rem;
    border: 1px solid #e0e6ec;
    border-radius: 8px;
    background: #ffffff;
  }

  .story-reading {
    gap: 0.75rem;
    padding: 0.95rem 0.95rem 0.85rem;
  }

  .story-copy {
    display: grid;
    gap: 0.45rem;
  }

  .significance-note {
    display: grid;
    gap: 0.35rem;
    padding-top: 0.7rem;
    border-top: 1px solid #e0e6ec;
  }

  .story-sources {
    display: grid;
    gap: 0.4rem;
    padding: 0 0.1rem;
  }

  .detail-block h3,
  .story-copy h3,
  .significance-note h3,
  .story-sources h3 {
    margin: 0;
    color: #314151;
    font-size: 0.78rem;
    font-weight: 800;
    letter-spacing: 0.06em;
    text-transform: uppercase;
  }

  .detail-block p,
  .story-copy p,
  .significance-note p,
  .empty-inline,
  .supporting-note,
  li,
  a {
    margin: 0;
    color: #536170;
    font-size: 0.9rem;
    line-height: 1.45;
  }

  .story-copy p {
    color: #314151;
    font-size: 0.94rem;
    line-height: 1.52;
  }

  .significance-note p {
    color: #536170;
    font-size: 0.88rem;
  }

  .supporting-note {
    color: #6b7785;
  }

  .connection-list,
  .source-list {
    display: grid;
    gap: 0.45rem;
    margin: 0;
  }

  .connection-list.compact {
    padding: 0;
    list-style: none;
  }

  .source-list.compact {
    display: flex;
    flex-wrap: wrap;
    gap: 0.35rem;
    padding: 0;
    list-style: none;
  }

  .source-list.compact a {
    display: inline-flex;
    padding: 0.28rem 0.45rem;
    border: 1px solid #d7dfe7;
    border-radius: 999px;
    background: #ffffff;
    color: #536170;
    font-size: 0.78rem;
    font-weight: 700;
    text-decoration: none;
  }

  .source-list.compact a:hover {
    border-color: #17202a;
    color: #17202a;
  }

  .source-list:not(.compact) {
    padding-left: 1.1rem;
  }

  .connection-row {
    display: grid;
    gap: 0.2rem;
    width: 100%;
    padding: 0.7rem 0.8rem;
    border: 1px solid #d7dfe7;
    border-radius: 8px;
    background: #f9fbfc;
    color: inherit;
    text-align: left;
  }

  .connection-row:hover {
    border-color: #17202a;
    background: #ffffff;
  }

  .connection-kicker {
    display: flex;
    flex-wrap: wrap;
    gap: 0.3rem;
    align-items: center;
    color: #6b7785;
    font-size: 0.7rem;
    font-weight: 800;
    letter-spacing: 0.06em;
    text-transform: uppercase;
  }

  .connection-kicker span + span::before {
    content: '•';
    margin-right: 0.3rem;
    color: #9aa7b4;
  }

  .connection-title {
    color: #17202a;
    font-size: 0.9rem;
    font-weight: 800;
    line-height: 1.3;
  }

  .connection-meta {
    display: flex;
    flex-wrap: wrap;
    align-items: center;
    gap: 0.35rem;
    color: #6b7785;
    font-size: 0.76rem;
    font-weight: 700;
    line-height: 1.35;
  }

  .connection-summary {
    color: #536170;
    font-size: 0.85rem;
    line-height: 1.4;
  }

  .preview-shell {
    min-height: 0;
  }

  .image-preview,
  .media-placeholder,
  .embedded-media,
  .external-media {
    display: grid;
    gap: 0.6rem;
  }

  .image-frame {
    position: relative;
    overflow: hidden;
    border-radius: 8px;
    background: #e9eef3;
    aspect-ratio: 4 / 3;
  }

  .image-frame img {
    width: 100%;
    height: 100%;
    object-fit: cover;
  }

  .image-preview figcaption {
    display: grid;
    gap: 0.15rem;
  }

  .image-preview strong,
  .media-placeholder h3,
  .external-media h3 {
    color: #17202a;
    font-size: 0.95rem;
    line-height: 1.3;
  }

  .image-preview span,
  .media-placeholder p,
  .external-media p {
    color: #6b7785;
    font-size: 0.8rem;
  }

  .external-media h3,
  .external-media p {
    margin: 0;
  }

  .media-placeholder {
    place-content: center;
    min-height: 14rem;
    padding: 1rem;
    border: 1px dashed #cfd7df;
    border-radius: 8px;
    text-align: left;
    background: #f9fbfc;
  }

  .external-media {
    align-content: center;
    min-height: 14rem;
    padding: 1rem;
    border: 1px solid #d7dfe7;
    border-radius: 8px;
    background:
      linear-gradient(135deg, rgba(23, 32, 42, 0.08) 0%, rgba(23, 32, 42, 0) 42%),
      #f9fbfc;
  }

  .external-media-badge {
    width: fit-content;
    padding: 0.25rem 0.45rem;
    border: 1px solid #d7dfe7;
    border-radius: 999px;
    background: #ffffff;
    color: #536170;
    font-size: 0.68rem;
    font-weight: 800;
    letter-spacing: 0.05em;
    text-transform: uppercase;
  }

  .media-placeholder a,
  .external-media a {
    width: fit-content;
    padding: 0.45rem 0.65rem;
    border: 1px solid #cfd7df;
    border-radius: 999px;
    background: #ffffff;
    color: #17202a;
    font-size: 0.78rem;
    font-weight: 700;
    text-decoration: none;
  }

  .external-media a:hover,
  .media-placeholder a:hover {
    border-color: #17202a;
  }

  .preview-list {
    display: grid;
    grid-template-columns: repeat(auto-fill, minmax(8.5rem, 1fr));
    gap: 0.5rem;
  }

  .preview-chip {
    display: grid;
    gap: 0.45rem;
    align-content: start;
    padding: 0.45rem;
    border: 1px solid #cfd7df;
    border-radius: 8px;
    background: #ffffff;
    color: #314151;
    text-align: left;
  }

  .preview-chip.active {
    border-color: #17202a;
    box-shadow: 0 0 0 1px rgba(23, 32, 42, 0.2);
  }

  .preview-chip img {
    width: 100%;
    aspect-ratio: 4 / 3;
    border-radius: 6px;
    object-fit: cover;
    background: #e9eef3;
  }

  .preview-badge {
    display: grid;
    place-items: center;
    width: 100%;
    aspect-ratio: 4 / 3;
    border-radius: 6px;
    background: #17202a;
    color: #ffffff;
    font-size: 0.78rem;
    font-weight: 800;
    letter-spacing: 0.03em;
    text-transform: uppercase;
  }

  .preview-text {
    display: grid;
    gap: 0.1rem;
    min-width: 0;
  }

  .preview-text strong {
    color: #17202a;
    font-size: 0.82rem;
    line-height: 1.25;
  }

  .preview-text small {
    color: #6b7785;
    font-size: 0.72rem;
    line-height: 1.25;
  }

  .empty {
    display: grid;
    gap: 0.5rem;
    padding: 1rem;
    color: #536170;
  }

  .empty.error h2,
  .empty.error p {
    color: #8f2d16;
  }

  .sr-only {
    position: absolute;
    width: 1px;
    height: 1px;
    padding: 0;
    margin: -1px;
    overflow: hidden;
    clip: rect(0, 0, 0, 0);
    white-space: nowrap;
    border: 0;
  }

  :global(.embedded-media .media-embed) {
    gap: 0.55rem;
  }

  :global(.embedded-media .media-embed .player) {
    border-radius: 8px;
  }

  @media (max-width: 920px) {
    .header-controls {
      grid-template-columns: 1fr;
      align-items: start;
    }

    .event-nav {
      justify-self: start;
    }
  }
</style>
