<script lang="ts">
  import type { MediaLink } from '$lib/types/soundatlas';
  import { parseYouTubeEmbed } from '$lib/media/youtube';

  export let mediaLinks: MediaLink[] = [];
  export let eventId = '';
  export let showReviewActions = true;
  export let onReviewMediaLink: (
    eventId: string,
    url: string,
    action: 'reviewed' | 'reject'
  ) => Promise<void> = async () => {};

  let selectedUrl = '';
  let isSaving = false;
  let errorMessage: string | null = null;

  $: playableLinks = mediaLinks
    .map((mediaLink) => ({ mediaLink, embed: parseYouTubeEmbed(mediaLink.url) }))
    .filter((entry): entry is { mediaLink: MediaLink; embed: NonNullable<ReturnType<typeof parseYouTubeEmbed>> } =>
      Boolean(entry.embed)
    );

  $: if (playableLinks.length > 0 && !playableLinks.some((entry) => entry.mediaLink.url === selectedUrl)) {
    selectedUrl = playableLinks[0].mediaLink.url;
  }

  $: selectedEntry = playableLinks.find((entry) => entry.mediaLink.url === selectedUrl) ?? playableLinks[0];

  async function reviewSelectedMediaLink(action: 'reviewed' | 'reject'): Promise<void> {
    if (!selectedEntry || isSaving) {
      return;
    }

    isSaving = true;
    errorMessage = null;

    try {
      await onReviewMediaLink(eventId, selectedEntry.mediaLink.url, action);
    } catch (error) {
      errorMessage = error instanceof Error ? error.message : 'Could not update media link.';
    } finally {
      isSaving = false;
    }
  }
</script>

{#if selectedEntry}
  <div class="media-embed">
    <div class="player">
      <iframe
        src={selectedEntry.embed.embedUrl}
        title={`YouTube player: ${selectedEntry.mediaLink.title}`}
        loading="lazy"
        allow="accelerometer; clipboard-write; encrypted-media; gyroscope; picture-in-picture; web-share"
        allowfullscreen
      ></iframe>
    </div>

    <div class="media-meta">
      <div>
        <strong>{selectedEntry.mediaLink.title}</strong>
        <span>{selectedEntry.mediaLink.review_status} · {selectedEntry.embed.kind}</span>
      </div>
    </div>

    {#if showReviewActions}
      <!-- @todo Hide or gate these admin-only review actions before a public explorer view. -->
      <div class="review-actions" aria-label="Media review actions">
        <button
          type="button"
          disabled={isSaving || selectedEntry.mediaLink.review_status === 'reviewed'}
          on:click={() => reviewSelectedMediaLink('reviewed')}
        >
          Mark reviewed
        </button>
        <button
          class="reject"
          type="button"
          disabled={isSaving}
          on:click={() => reviewSelectedMediaLink('reject')}
        >
          Reject
        </button>
      </div>

      {#if errorMessage}
        <p class="review-error">{errorMessage}</p>
      {/if}
    {/if}

    {#if playableLinks.length > 1}
      <label class="media-selector">
        <span>Switch media</span>
        <select bind:value={selectedUrl}>
          {#each playableLinks as entry}
            <option value={entry.mediaLink.url}>{entry.mediaLink.title}</option>
          {/each}
        </select>
      </label>
    {/if}
  </div>
{/if}

<style>
  .media-embed {
    display: grid;
    gap: 0.65rem;
  }

  .player {
    position: relative;
    overflow: hidden;
    border-radius: 12px;
    background: #17202a;
    aspect-ratio: 16 / 9;
  }

  iframe {
    position: absolute;
    inset: 0;
    width: 100%;
    height: 100%;
    border: 0;
  }

  .media-meta {
    display: flex;
    flex-wrap: wrap;
    gap: 0.5rem;
    align-items: start;
    justify-content: space-between;
  }

  .media-meta div,
  .media-selector {
    display: grid;
    gap: 0.2rem;
  }

  strong {
    color: #314151;
    font-size: 0.9rem;
    line-height: 1.35;
  }

  span {
    color: #6b7785;
    font-size: 0.78rem;
  }

  select {
    width: 100%;
    padding: 0.55rem 0.65rem;
    border: 1px solid #cfd7df;
    border-radius: 8px;
    background: #ffffff;
    color: #314151;
    font: inherit;
  }

  .review-actions {
    display: flex;
    flex-wrap: wrap;
    gap: 0.5rem;
  }

  button {
    padding: 0.45rem 0.65rem;
    border: 1px solid #cfd7df;
    border-radius: 8px;
    background: #ffffff;
    color: #314151;
    font: inherit;
    font-size: 0.85rem;
    font-weight: 700;
  }

  button:not(:disabled):hover {
    border-color: #17202a;
  }

  button:disabled {
    cursor: not-allowed;
    opacity: 0.5;
  }

  .reject {
    border-color: #efc8be;
    color: #bb3f22;
  }

  .review-error {
    margin: 0;
    color: #bb3f22;
    font-size: 0.82rem;
    line-height: 1.4;
  }
</style>
