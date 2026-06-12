<script lang="ts">
  import type { Route } from '$lib/types/soundatlas';

  export let routes: Route[] = [];
  export let activeRouteIds: Set<string> = new Set();
  export let onToggleRoute: (routeId: string) => void = () => {};
</script>

<section class="route-filter" aria-label="Route filter">
  <div class="section-label">Routes</div>

  {#if routes.length === 0}
    <p class="empty">No routes loaded.</p>
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
          <span class="route-copy">
            <span>{route.title}</span>
            <small>Creator: {route.creator}</small>
          </span>
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
    text-align: left;
  }

  button.active {
    border-color: #17202a;
    background: #17202a;
    color: #ffffff;
  }

  .swatch {
    flex: 0 0 auto;
    width: 0.75rem;
    height: 0.75rem;
    border-radius: 999px;
    background: var(--route-color);
  }

  .route-copy {
    display: grid;
    gap: 0.05rem;
  }

  small {
    color: currentColor;
    font-size: 0.68rem;
    opacity: 0.72;
  }

  .empty {
    margin: 0;
    color: #6b7785;
    font-size: 0.9rem;
  }
</style>
