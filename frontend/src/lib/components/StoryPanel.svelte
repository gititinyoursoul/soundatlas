<script lang="ts">
  import MediaEmbed from '$lib/components/MediaEmbed.svelte';
  import { parseYouTubeEmbed, type YouTubeEmbed } from '$lib/media/youtube';
  import type {
    Connection,
    Event,
    ImageLink,
    MediaLink,
    MediaProvider,
    MediaType,
    Place,
    Route
  } from '$lib/types/soundatlas';

  type InspectorTab = 'story' | 'media' | 'sources';

  type PreviewItem =
    | {
        id: string;
        kind: 'image';
        title: string;
        subtitle: string;
        previewUrl: string;
        imageLink: ImageLink;
      }
    | {
        id: string;
        kind: 'media';
        title: string;
        subtitle: string;
        mediaLink: MediaLink;
        embed: YouTubeEmbed | null;
      };

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

  let activeTab: InspectorTab = 'story';
  let selectedPreviewId = '';
  let lastEventId: string | null = null;

  $: previewItems = buildPreviewItems(event);
  $: if (event?.id !== lastEventId) {
    lastEventId = event?.id ?? null;
    activeTab = 'story';
    selectedPreviewId = previewItems[0]?.id ?? '';
  }
  $: if (previewItems.length > 0 && !previewItems.some((item) => item.id === selectedPreviewId)) {
    selectedPreviewId = previewItems[0].id;
  }
  $: selectedPreviewItem = previewItems.find((item) => item.id === selectedPreviewId) ?? null;
  $: mediaCount = event?.media_links.length ?? 0;
  $: imageCount = event?.image_links.length ?? 0;
  $: sourceCount = event?.source_urls.length ?? 0;
  $: connectionCount = connections.length;

  function buildPreviewItems(currentEvent: Event | null): PreviewItem[] {
    if (!currentEvent) {
      return [];
    }

    const imageItems = currentEvent.image_links.map<PreviewItem>((imageLink) => ({
      id: `image:${imageLink.image_url}`,
      kind: 'image',
      title: imageLink.title,
      subtitle: `${formatImageDescriptor(imageLink.provider, imageLink.type)} · ${formatRightsLabel(
        imageLink.rights_status
      )}`,
      previewUrl: imageLink.thumbnail_url ?? imageLink.image_url,
      imageLink
    }));

    const mediaItems = currentEvent.media_links.map<PreviewItem>((mediaLink) => ({
      id: `media:${mediaLink.url}`,
      kind: 'media',
      title: mediaLink.title,
      subtitle: `${formatMediaDescriptor(mediaLink.provider, mediaLink.type)} · ${mediaLink.review_status}`,
      mediaLink,
      embed: parseYouTubeEmbed(mediaLink.url)
    }));

    return [...imageItems, ...mediaItems];
  }

  function formatMediaDescriptor(provider: MediaProvider, type: MediaType): string {
    return `${mediaProviderLabels[provider]} ${humanize(type)}`;
  }

  function formatImageDescriptor(provider: string, type: string): string {
    return `${imageProviderLabels[provider] ?? humanize(provider)} ${humanize(type)}`;
  }

  function formatRightsLabel(rightsStatus: string): string {
    return humanize(rightsStatus);
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
      <div class="eyebrow">
        <span>Selected event</span>
        <span>{currentEventIndex + 1} / {eventCount}</span>
      </div>

      <div class="title-block">
        <h2>{event.title}</h2>
        <p>{formatEventYears(event)}</p>
      </div>

      <dl class="event-meta">
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
          <span>{mediaCount + imageCount + sourceCount + connectionCount}</span>
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
          id="inspector-tab-sources"
          type="button"
          role="tab"
          class:active={activeTab === 'sources'}
          aria-selected={activeTab === 'sources'}
          aria-controls="inspector-panel-sources"
          on:click={() => selectTab('sources')}
        >
          Sources
          <span>{sourceCount}</span>
        </button>
      </div>

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

    <div class="inspector-body">
      {#if activeTab === 'story'}
        <div
          id="inspector-panel-story"
          role="tabpanel"
          aria-labelledby="inspector-tab-story"
          class="tab-panel"
        >
          <section class="detail-block">
            <h3>What happened</h3>
            <p>{event.summary}</p>
          </section>

          <section class="detail-block emphasis">
            <h3>Why it matters</h3>
            <p>{event.significance}</p>
          </section>

          <section class="detail-block">
            <h3>Connections</h3>
            {#if connections.length > 0}
              <ul class="connection-list">
                {#each connections as connection}
                  <li>{connection.summary}</li>
                {/each}
              </ul>
            {:else}
              <p class="empty-inline">No connection notes are attached to this event yet.</p>
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
                  showReviewActions={false}
                />
              </div>
            {:else if selectedPreviewItem?.kind === 'media'}
              <div class="media-placeholder">
                <h3>{selectedPreviewItem.title}</h3>
                <p>{selectedPreviewItem.subtitle}</p>
                <a href={selectedPreviewItem.mediaLink.url} target="_blank" rel="noreferrer">
                  Open media link
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
            <h3>Images and media</h3>
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
                      <span class="preview-badge">{previewItem.embed ? 'Play' : 'Link'}</span>
                    {/if}
                    <span class="preview-text">
                      <strong>{previewItem.title}</strong>
                      <small>{previewItem.subtitle}</small>
                    </span>
                  </button>
                {/each}
              </div>
            {:else}
              <p class="empty-inline">No image or media links are attached to this event yet.</p>
            {/if}
          </section>
        </div>
      {:else}
        <div
          id="inspector-panel-sources"
          role="tabpanel"
          aria-labelledby="inspector-tab-sources"
          class="tab-panel"
        >
          <section class="detail-block">
            <h3>Source URLs</h3>
            {#if event.source_urls.length > 0}
              <ul class="source-list">
                {#each event.source_urls as sourceUrl, index}
                  <li>
                    <a href={sourceUrl} target="_blank" rel="noreferrer">
                      Source {index + 1}
                    </a>
                  </li>
                {/each}
              </ul>
            {:else}
              <p class="empty-inline">No source URLs have been added for this event yet.</p>
            {/if}
          </section>

          <section class="detail-block compact">
            <h3>Citation notes</h3>
            <p class="supporting-note">
              Keep source links external and traceable. Public media browsing stays in the Media tab.
            </p>
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
    gap: 0.8rem;
    padding: 0.95rem 1rem 0.8rem;
    border-bottom: 1px solid #d9e0e7;
    background: linear-gradient(180deg, #ffffff 0%, #fbfcfd 100%);
  }

  .inspector-body {
    display: grid;
    gap: 0.8rem;
    padding: 0.95rem 1rem 1rem;
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

  .title-block {
    display: grid;
    gap: 0.1rem;
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
    font-size: 0.84rem;
    font-weight: 700;
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

  .inspector-tabs {
    display: grid;
    grid-template-columns: repeat(3, minmax(0, 1fr));
    gap: 0.35rem;
  }

  .inspector-tabs button {
    display: inline-flex;
    align-items: center;
    justify-content: space-between;
    gap: 0.5rem;
    min-width: 0;
    padding: 0.55rem 0.7rem;
    border: 1px solid #cfd7df;
    border-radius: 8px;
    background: #ffffff;
    color: #314151;
    font: inherit;
    font-size: 0.84rem;
    font-weight: 700;
  }

  .inspector-tabs button span {
    color: #6b7785;
    font-size: 0.76rem;
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
    font: inherit;
    font-size: 0.85rem;
    font-weight: 700;
  }

  .event-nav button:not(:disabled):hover,
  .inspector-tabs button:not(.active):hover {
    border-color: #17202a;
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
  .preview-shell {
    display: grid;
    gap: 0.45rem;
    padding: 0.85rem;
    border: 1px solid #e0e6ec;
    border-radius: 8px;
    background: #ffffff;
  }

  .detail-block.emphasis {
    border-color: #efc8be;
    background: #fff7f4;
  }

  .detail-block h3 {
    color: #314151;
    font-size: 0.78rem;
    font-weight: 800;
    letter-spacing: 0.06em;
    text-transform: uppercase;
  }

  .detail-block p,
  .empty-inline,
  .supporting-note,
  li,
  a {
    color: #536170;
    font-size: 0.9rem;
    line-height: 1.45;
  }

  .supporting-note {
    color: #6b7785;
  }

  .connection-list,
  .source-list {
    display: grid;
    gap: 0.45rem;
    margin: 0;
    padding-left: 1.1rem;
  }

  .preview-shell {
    min-height: 0;
  }

  .image-preview,
  .media-placeholder,
  .embedded-media {
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
  .media-placeholder h3 {
    color: #17202a;
    font-size: 0.95rem;
    line-height: 1.3;
  }

  .image-preview span,
  .media-placeholder p {
    color: #6b7785;
    font-size: 0.8rem;
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

  .media-placeholder a {
    width: fit-content;
    padding: 0.45rem 0.65rem;
    border: 1px solid #efc8be;
    border-radius: 999px;
    background: #fff7f4;
    color: #bb3f22;
    font-size: 0.78rem;
    font-weight: 700;
    text-decoration: none;
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

  :global(.embedded-media .media-embed) {
    gap: 0.55rem;
  }

  :global(.embedded-media .media-embed .player) {
    border-radius: 8px;
  }
</style>
