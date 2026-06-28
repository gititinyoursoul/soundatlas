<script lang="ts">
  export let name:
    | 'book'
    | 'chevron-left'
    | 'chevron-right'
    | 'circle'
    | 'close'
    | 'collapse'
    | 'expand'
    | 'layers'
    | 'map'
    | 'route'
    | 'settings'
    | 'sparkles'
    | 'timeline'
    | 'warning' = 'circle';
  export let decorative = true;
</script>

<svg
  class="icon"
  viewBox="0 0 24 24"
  fill="none"
  stroke="currentColor"
  stroke-width="2"
  stroke-linecap="round"
  stroke-linejoin="round"
  aria-hidden={decorative}
  focusable="false"
>
  {#if name === 'book'}
    <path d="M4 19.5A2.5 2.5 0 0 1 6.5 17H20" />
    <path d="M4 4.5A2.5 2.5 0 0 1 6.5 2H20v20H6.5A2.5 2.5 0 0 1 4 19.5z" />
  {:else if name === 'close'}
    <path d="M18 6 6 18" />
    <path d="m6 6 12 12" />
  {:else if name === 'chevron-left'}
    <path d="m15 18-6-6 6-6" />
  {:else if name === 'chevron-right'}
    <path d="m9 18 6-6-6-6" />
  {:else if name === 'collapse'}
    <path d="m15 18-6-6 6-6" />
    <path d="M20 4v16" />
  {:else if name === 'expand'}
    <path d="m9 18 6-6-6-6" />
    <path d="M4 4v16" />
  {:else if name === 'layers'}
    <path d="m12 2 9 5-9 5-9-5 9-5z" />
    <path d="m3 12 9 5 9-5" />
    <path d="m3 17 9 5 9-5" />
  {:else if name === 'map'}
    <path d="M9 18 3 21V6l6-3 6 3 6-3v15l-6 3-6-3z" />
    <path d="M9 3v15" />
    <path d="M15 6v15" />
  {:else if name === 'route'}
    <circle cx="6" cy="19" r="3" />
    <circle cx="18" cy="5" r="3" />
    <path d="M12 19h1.5a4.5 4.5 0 0 0 0-9H10a4.5 4.5 0 0 1 0-9H12" />
  {:else if name === 'settings'}
    <path d="M12 15.5A3.5 3.5 0 1 0 12 8a3.5 3.5 0 0 0 0 7.5z" />
    <path d="M19.4 15a1.7 1.7 0 0 0 .34 1.88l.06.06a2 2 0 1 1-2.83 2.83l-.06-.06A1.7 1.7 0 0 0 15 19.4a1.7 1.7 0 0 0-1 .6 1.7 1.7 0 0 0-.36 1.1V21a2 2 0 1 1-4 0v-.09A1.7 1.7 0 0 0 9 19.4a1.7 1.7 0 0 0-1.88.34l-.06.06a2 2 0 1 1-2.83-2.83l.06-.06A1.7 1.7 0 0 0 4.6 15a1.7 1.7 0 0 0-.6-1 1.7 1.7 0 0 0-1.1-.36H3a2 2 0 1 1 0-4h.09A1.7 1.7 0 0 0 4.6 9a1.7 1.7 0 0 0-.34-1.88l-.06-.06a2 2 0 1 1 2.83-2.83l.06.06A1.7 1.7 0 0 0 9 4.6a1.7 1.7 0 0 0 1-.6 1.7 1.7 0 0 0 .36-1.1V3a2 2 0 1 1 4 0v.09A1.7 1.7 0 0 0 15 4.6a1.7 1.7 0 0 0 1.88-.34l.06-.06a2 2 0 1 1 2.83 2.83l-.06.06A1.7 1.7 0 0 0 19.4 9c.15.37.36.7.6 1 .3.28.7.43 1.1.4H21a2 2 0 1 1 0 4h-.09A1.7 1.7 0 0 0 19.4 15z" />
  {:else if name === 'sparkles'}
    <path d="m12 3 1.5 4.5L18 9l-4.5 1.5L12 15l-1.5-4.5L6 9l4.5-1.5L12 3z" />
    <path d="m19 14 .7 2.3L22 17l-2.3.7L19 20l-.7-2.3L16 17l2.3-.7L19 14z" />
  {:else if name === 'timeline'}
    <path d="M4 6h16" />
    <path d="M4 12h16" />
    <path d="M4 18h16" />
    <circle cx="8" cy="6" r="2" />
    <circle cx="14" cy="12" r="2" />
    <circle cx="10" cy="18" r="2" />
  {:else if name === 'warning'}
    <path d="m12 3 10 18H2L12 3z" />
    <path d="M12 9v4" />
    <path d="M12 17h.01" />
  {:else}
    <circle cx="12" cy="12" r="9" />
  {/if}
</svg>

<style>
  .icon {
    display: block;
    width: 1em;
    height: 1em;
  }
</style>
