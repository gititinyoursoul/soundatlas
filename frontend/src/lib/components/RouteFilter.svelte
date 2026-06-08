<script lang="ts">
  import type { Route } from '$lib/types/soundatlas';

  export let routes: Route[] = [];
  export let activeRouteIds: Set<string> = new Set();
  export let onToggleRoute: (routeId: string) => void = () => {};
</script>

<section class="route-filter" aria-label="Routenfilter">
  <div class="section-label">Routen</div>

  {#if routes.length === 0}
    <p class="empty">Keine Routen geladen.</p>
  {:else}
    <div class="routes">
      {#each routes as route}
        <button
          class:active={activeRouteIds.has(route.id)}
          type="button"
          on:click={() => onToggleRoute(route.id)}
          title={route.summary}
        >
          <span class="swatch" style={`--route-color: ${route.color}`}></span>
          <span>{route.title}</span>
        </button>
      {/each}
    </div>
  {/if}
</section>

<style>
  .route-filter {
    display: grid;
    gap: 0.65rem;
  }

  .section-label {
    color: #6b7785;
    font-size: 0.78rem;
    font-weight: 700;
    letter-spacing: 0.04em;
    text-transform: uppercase;
  }

  .routes {
    display: flex;
    flex-wrap: wrap;
    gap: 0.5rem;
  }

  button {
    display: inline-flex;
    align-items: center;
    gap: 0.45rem;
    padding: 0.45rem 0.65rem;
    border: 1px solid #cfd7df;
    border-radius: 999px;
    background: #ffffff;
    color: #314151;
  }

  button.active {
    border-color: #17202a;
    background: #17202a;
    color: #ffffff;
  }

  .swatch {
    width: 0.75rem;
    height: 0.75rem;
    border-radius: 999px;
    background: var(--route-color);
  }

  .empty {
    margin: 0;
    color: #6b7785;
    font-size: 0.9rem;
  }
</style>
