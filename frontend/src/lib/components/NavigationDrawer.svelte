<script lang="ts">
  import { tick } from 'svelte';
  import type { Route } from '$lib/types/soundatlas';
  import Icon from './Icon.svelte';

  type DrawerVariant = 'expanded' | 'collapsed';
  type DrawerPanel = 'main' | 'routes';
  type NavIcon = 'book' | 'circle' | 'layers' | 'map' | 'route' | 'settings' | 'sparkles' | 'timeline';

  type NavItem = {
    id: string;
    label: string;
    icon: NavIcon;
    badge?: string;
    disabled?: boolean;
    disabledReason?: string;
  };

  type NavSection = {
    id: string;
    title: string;
    items: NavItem[];
    emptyMessage?: string;
    errorMessage?: string | null;
  };

  export let open = false;
  export let variant: DrawerVariant = 'expanded';
  export let activeItemId = 'map';
  export let routes: Route[] = [];
  export let selectedRouteId: string | null = null;
  export let routeEventCounts: Record<string, number> = {};
  export let eventCount = 0;
  export let isLoading = false;
  export let errorMessage: string | null = null;
  export let onClose: () => void = () => {};
  export let onToggleVariant: () => void = () => {};
  export let onSelectItem: (itemId: string) => void = () => {};
  export let onSelectRoute: (routeId: string) => void = () => {};

  let drawerElement: HTMLDivElement;
  let panelHeadingElement: HTMLHeadingElement;
  let didFocusForOpen = false;
  let activePanel: DrawerPanel = 'main';

  $: sections = buildSections(routes.length, eventCount, errorMessage);
  $: if (open && !didFocusForOpen) {
    didFocusForOpen = true;
    void focusDrawer();
  }
  $: if (!open && didFocusForOpen) {
    didFocusForOpen = false;
    activePanel = 'main';
  }

  function buildSections(routes: number, events: number, error: string | null): NavSection[] {
    return [
      {
        id: 'explore',
        title: 'Explore',
        items: [
          {
            id: 'routes',
            label: 'Routes',
            icon: 'route',
            badge: routes > 0 ? String(routes) : undefined
          }
        ],
        emptyMessage: routes === 0 && !error ? 'No route entries loaded.' : undefined,
        errorMessage: error
      },
      {
        id: 'research',
        title: 'Research',
        items: [
          {
            id: 'events',
            label: 'Events',
            icon: 'layers',
            badge: events > 0 ? String(events) : undefined
          },
          { id: 'connections', label: 'Connections', icon: 'sparkles' },
          { id: 'sources', label: 'Sources', icon: 'book' }
        ]
      },
      {
        id: 'workflow',
        title: 'Workflow',
        items: [
          {
            id: 'media-review',
            label: 'Media Review',
            icon: 'settings',
            disabled: true,
            disabledReason: 'Admin access required'
          },
          {
            id: 'validation',
            label: 'Validation',
            icon: 'circle',
            disabled: true,
            disabledReason: 'Admin access required'
          }
        ]
      }
    ];
  }

  async function focusDrawer(): Promise<void> {
    await tick();
    drawerElement?.focus();
  }

  function handleOverlayClick(): void {
    onClose();
  }

  function handleItemClick(item: NavItem): void {
    if (item.disabled) {
      return;
    }

    if (item.id === 'routes') {
      openRoutesPanel();
      return;
    }

    onSelectItem(item.id);
  }

  async function openRoutesPanel(): Promise<void> {
    activePanel = 'routes';
    onSelectItem('routes');

    if (variant === 'collapsed') {
      onToggleVariant();
    }

    await tick();
    panelHeadingElement?.focus();
  }

  async function returnToMainPanel(): Promise<void> {
    activePanel = 'main';
    await tick();
    panelHeadingElement?.focus();
  }

  function handleRouteClick(routeId: string): void {
    onSelectRoute(routeId);
  }

  function handleKeydown(event: KeyboardEvent): void {
    if (event.key === 'Escape') {
      event.preventDefault();
      onClose();
      return;
    }

    if (event.key !== 'Tab' || !drawerElement) {
      return;
    }

    const focusableElements = Array.from(
      drawerElement.querySelectorAll<HTMLElement>(
        'button, [href], [tabindex]:not([tabindex="-1"])'
      )
    ).filter((element) => !element.hasAttribute('disabled') && element.tabIndex !== -1);

    if (focusableElements.length === 0) {
      event.preventDefault();
      drawerElement.focus();
      return;
    }

    const firstElement = focusableElements[0];
    const lastElement = focusableElements[focusableElements.length - 1];

    if (event.shiftKey && document.activeElement === firstElement) {
      event.preventDefault();
      lastElement.focus();
    } else if (!event.shiftKey && document.activeElement === lastElement) {
      event.preventDefault();
      firstElement.focus();
    }
  }

  function retryLoading(): void {
    window.location.reload();
  }
</script>

{#if open}
  <div class="drawer-layer" aria-label="Navigation overlay">
    <button
      type="button"
      class="dim-overlay"
      aria-label="Close navigation"
      on:click={handleOverlayClick}
    ></button>

    <div
      bind:this={drawerElement}
      class:collapsed={variant === 'collapsed'}
      class="navigation-drawer"
      role="dialog"
      aria-modal="true"
      aria-label="Primary navigation"
      tabindex="-1"
      on:keydown={handleKeydown}
    >
      <header class="drawer-header">
        <div class="brand" aria-hidden={variant === 'collapsed'}>
          {#if variant === 'expanded'}
            <span>SoundAtlas</span>
            <strong>Navigation</strong>
          {:else}
            <strong>S</strong>
          {/if}
        </div>

        <div class="header-actions">
          <button
            type="button"
            class="icon-button"
            aria-label={variant === 'expanded' ? 'Collapse navigation' : 'Expand navigation'}
            data-tooltip={variant === 'expanded' ? 'Collapse' : 'Expand'}
            on:click={onToggleVariant}
          >
            <Icon name={variant === 'expanded' ? 'collapse' : 'expand'} />
          </button>
          <button
            type="button"
            class="icon-button"
            aria-label="Close navigation"
            data-tooltip="Close"
            on:click={onClose}
          >
            <Icon name="close" />
          </button>
        </div>
      </header>

      <div class="drawer-body">
        {#if isLoading}
          <section class="nav-section" aria-label="Navigation loading">
            {#if variant === 'expanded'}
              <div class="section-label skeleton-label"></div>
            {/if}
            <div class="skeleton-list" aria-hidden="true">
              <span></span>
              <span></span>
              <span></span>
            </div>
            <span class="visually-hidden">Loading navigation</span>
          </section>
        {:else if activePanel === 'routes'}
          <section class="routes-panel" aria-labelledby="drawer-routes-heading">
            <button type="button" class="back-button" on:click={returnToMainPanel}>
              <Icon name="collapse" />
              <span>Back to navigation</span>
            </button>

            <div class="panel-heading">
              <span>Routes</span>
              <h2 id="drawer-routes-heading" bind:this={panelHeadingElement} tabindex="-1">
                Choose active route
              </h2>
            </div>

            {#if routes.length === 0}
              <div class="section-empty">
                <Icon name="circle" />
                <span>No routes loaded.</span>
              </div>
            {:else}
              <div class="route-list" aria-label="Available routes">
                {#each routes as route}
                  <button
                    type="button"
                    class:active={selectedRouteId === route.id}
                    class="route-option"
                    style={`--route-color: ${route.color}`}
                    aria-current={selectedRouteId === route.id ? 'page' : undefined}
                    on:click={() => handleRouteClick(route.id)}
                  >
                    <span class="route-swatch" aria-hidden="true"></span>
                    <span class="route-copy">
                      <strong>{route.title}</strong>
                      <span>
                        {route.year_start}-{route.year_end}
                        {#if routeEventCounts[route.id]}
                          · {routeEventCounts[route.id]} {routeEventCounts[route.id] === 1 ? 'event' : 'events'}
                        {/if}
                      </span>
                    </span>
                    {#if selectedRouteId === route.id}
                      <span class="route-active-label">Active</span>
                    {/if}
                  </button>
                {/each}
              </div>
            {/if}
          </section>
        {:else}
          <h2 class="visually-hidden" bind:this={panelHeadingElement} tabindex="-1">
            Main navigation
          </h2>
          {#each sections as section}
            <section class="nav-section" aria-labelledby={`drawer-section-${section.id}`}>
              {#if variant === 'expanded'}
                <h2 id={`drawer-section-${section.id}`}>{section.title}</h2>
              {:else}
                <span class="section-rule" aria-hidden="true"></span>
              {/if}

              {#if section.errorMessage}
                <div class="section-error">
                  <Icon name="warning" />
                  {#if variant === 'expanded'}
                    <div>
                      <strong>Loading failed</strong>
                      <p>{section.errorMessage}</p>
                      <button type="button" on:click={retryLoading}>Retry</button>
                    </div>
                  {/if}
                </div>
              {:else if section.emptyMessage}
                <div class="section-empty">
                  <Icon name="circle" />
                  {#if variant === 'expanded'}
                    <span>{section.emptyMessage}</span>
                  {/if}
                </div>
              {/if}

              <div class="nav-items">
                {#each section.items as item}
                  <button
                    type="button"
                    class:active={activeItemId === item.id}
                    class:disabled={item.disabled}
                    class="nav-item"
                    aria-current={activeItemId === item.id ? 'page' : undefined}
                    aria-disabled={item.disabled ? 'true' : undefined}
                    aria-label={item.label}
                    data-tooltip={item.disabled ? item.disabledReason : item.label}
                    on:click={() => handleItemClick(item)}
                  >
                    <span class="item-icon"><Icon name={item.icon} /></span>
                    {#if variant === 'expanded'}
                      <span class="item-label">{item.label}</span>
                      {#if item.badge}
                        <span class="item-badge">{item.badge}</span>
                      {/if}
                      {#if item.disabled && item.disabledReason}
                        <span class="item-reason">{item.disabledReason}</span>
                      {/if}
                    {:else if item.badge}
                      <span class="item-dot" aria-hidden="true"></span>
                    {/if}
                  </button>
                {/each}
              </div>
            </section>
          {/each}
        {/if}
      </div>

      <footer class="drawer-footer">
        {#if variant === 'expanded'}
          <div class="session">
            <span>Access</span>
            <strong>Public explorer</strong>
          </div>
        {:else}
          <span class="access-mark" aria-label="Public explorer" data-tooltip="Public explorer">
            <Icon name="circle" />
          </span>
        {/if}
      </footer>
    </div>
  </div>
{/if}

<style>
  .drawer-layer {
    position: fixed;
    inset: 0;
    z-index: 1000;
  }

  .dim-overlay {
    position: absolute;
    inset: 0;
    width: 100%;
    height: 100%;
    border: 0;
    background: rgba(23, 32, 42, 0.36);
    animation: fade-in 180ms ease-out;
  }

  .navigation-drawer {
    position: absolute;
    inset: 0 auto 0 0;
    display: grid;
    grid-template-rows: auto minmax(0, 1fr) auto;
    width: 20rem;
    max-width: calc(100vw - 2rem);
    border-right: 1px solid #cfd7df;
    background: #ffffff;
    box-shadow: 18px 0 48px rgba(23, 32, 42, 0.24);
    outline: none;
    animation: slide-in 220ms cubic-bezier(0.2, 0, 0, 1);
    transition: width 180ms ease-out;
  }

  .navigation-drawer.collapsed {
    width: 4.5rem;
  }

  .drawer-header {
    display: grid;
    grid-template-columns: minmax(0, 1fr) auto;
    align-items: start;
    gap: 0.75rem;
    padding: 1rem;
    border-bottom: 1px solid #d9e0e7;
  }

  .collapsed .drawer-header {
    grid-template-columns: 1fr;
    justify-items: center;
    padding: 0.85rem 0.6rem;
  }

  .brand {
    display: grid;
    gap: 0.2rem;
    min-width: 0;
  }

  .brand span {
    color: #6b7785;
    font-size: 0.68rem;
    font-weight: 800;
    letter-spacing: 0.08em;
    text-transform: uppercase;
  }

  .brand strong {
    color: #17202a;
    font-size: 1rem;
    line-height: 1.2;
  }

  .collapsed .brand strong {
    display: grid;
    place-items: center;
    width: 2rem;
    height: 2rem;
    border: 1px solid #d9e0e7;
    border-radius: 8px;
    background: #f3f6f8;
    font-size: 1rem;
  }

  .header-actions {
    display: flex;
    gap: 0.35rem;
  }

  .collapsed .header-actions {
    display: grid;
    justify-items: center;
  }

  .icon-button,
  .nav-item {
    position: relative;
    border: 1px solid transparent;
    font: inherit;
  }

  .icon-button {
    display: grid;
    place-items: center;
    width: 2rem;
    height: 2rem;
    border-color: #d9e0e7;
    border-radius: 8px;
    background: #ffffff;
    color: #314151;
    font-size: 1rem;
  }

  .icon-button:hover,
  .nav-item:hover:not(:disabled) {
    background: #f3f6f8;
  }

  .drawer-body {
    display: grid;
    align-content: start;
    gap: 1rem;
    min-height: 0;
    padding: 0.75rem;
    overflow-y: auto;
  }

  .collapsed .drawer-body {
    padding: 0.75rem 0.6rem;
  }

  .nav-section {
    display: grid;
    gap: 0.45rem;
  }

  .routes-panel {
    display: grid;
    gap: 0.8rem;
  }

  .back-button {
    display: inline-flex;
    align-items: center;
    width: max-content;
    max-width: 100%;
    gap: 0.45rem;
    min-height: 2rem;
    padding: 0.3rem 0.45rem;
    border: 1px solid #d9e0e7;
    border-radius: 8px;
    background: #ffffff;
    color: #314151;
    font: inherit;
    font-size: 0.78rem;
    font-weight: 800;
  }

  .back-button:hover {
    background: #f3f6f8;
  }

  .panel-heading {
    display: grid;
    gap: 0.18rem;
  }

  .panel-heading span {
    color: #6b7785;
    font-size: 0.68rem;
    font-weight: 800;
    letter-spacing: 0.08em;
    text-transform: uppercase;
  }

  .panel-heading h2 {
    margin: 0;
    color: #17202a;
    font-size: 1rem;
    line-height: 1.2;
  }

  .panel-heading h2:focus {
    outline: none;
  }

  .route-list {
    display: grid;
    gap: 0.5rem;
  }

  .route-option {
    display: grid;
    grid-template-columns: auto minmax(0, 1fr) auto;
    align-items: center;
    gap: 0.7rem;
    min-height: 4.4rem;
    padding: 0.7rem 0.75rem;
    border: 1px solid #d9e0e7;
    border-left: 0.32rem solid var(--route-color);
    border-radius: 8px;
    background: #ffffff;
    color: #314151;
    font: inherit;
    text-align: left;
  }

  .route-option:hover {
    background: #f8fafb;
  }

  .route-option.active {
    border-color: #efc8be;
    border-left-color: var(--route-color);
    background: #fff7f4;
    box-shadow: inset 0 0 0 1px rgba(228, 87, 46, 0.18);
  }

  .route-swatch {
    width: 0.85rem;
    height: 0.85rem;
    border: 1px solid rgba(23, 32, 42, 0.26);
    border-radius: 999px;
    background: var(--route-color);
  }

  .route-copy {
    display: grid;
    gap: 0.2rem;
    min-width: 0;
  }

  .route-copy strong {
    overflow: hidden;
    color: #17202a;
    font-size: 0.88rem;
    font-weight: 800;
    line-height: 1.25;
    text-overflow: ellipsis;
    white-space: nowrap;
  }

  .route-copy span {
    overflow: hidden;
    color: #536170;
    font-size: 0.76rem;
    font-weight: 700;
    line-height: 1.3;
    text-overflow: ellipsis;
    white-space: nowrap;
  }

  .route-active-label {
    align-self: end;
    color: #bb3f22;
    font-size: 0.68rem;
    font-weight: 800;
    letter-spacing: 0.06em;
    text-transform: uppercase;
  }

  .nav-section h2 {
    margin: 0;
    padding: 0 0.5rem;
    color: #6b7785;
    font-size: 0.68rem;
    font-weight: 800;
    letter-spacing: 0.08em;
    text-transform: uppercase;
  }

  .section-rule {
    display: block;
    height: 1px;
    margin: 0.25rem 0.35rem;
    background: #d9e0e7;
  }

  .nav-items,
  .skeleton-list {
    display: grid;
    gap: 0.25rem;
  }

  .nav-item {
    display: grid;
    grid-template-columns: 1.5rem minmax(0, 1fr) auto;
    align-items: center;
    gap: 0.75rem;
    min-height: 2.75rem;
    padding: 0.5rem 0.65rem;
    border-radius: 8px;
    background: transparent;
    color: #314151;
    text-align: left;
  }

  .collapsed .nav-item {
    grid-template-columns: 1fr;
    justify-items: center;
    min-height: 3rem;
    padding: 0.5rem;
  }

  .nav-item.active {
    border-color: #efc8be;
    background: #fff7f4;
    color: #7e2d19;
    box-shadow: inset 4px 0 0 #e4572e;
  }

  .nav-item.disabled,
  .nav-item:disabled {
    color: #8a96a3;
    cursor: default;
    opacity: 0.58;
  }

  .item-icon {
    display: grid;
    place-items: center;
    color: currentColor;
    font-size: 1.25rem;
  }

  .collapsed .item-icon {
    font-size: 1.38rem;
  }

  .item-label {
    overflow: hidden;
    font-size: 0.88rem;
    font-weight: 700;
    line-height: 1.3;
    text-overflow: ellipsis;
    white-space: nowrap;
  }

  .item-badge {
    min-width: 1.35rem;
    padding: 0.12rem 0.38rem;
    border: 1px solid #efc8be;
    border-radius: 999px;
    color: #7e2d19;
    font-size: 0.68rem;
    font-weight: 800;
    text-align: center;
  }

  .item-dot {
    position: absolute;
    top: 0.48rem;
    right: 0.55rem;
    width: 0.42rem;
    height: 0.42rem;
    border-radius: 999px;
    background: #e4572e;
  }

  .item-reason {
    grid-column: 2 / -1;
    color: #8a96a3;
    font-size: 0.68rem;
    font-weight: 700;
    line-height: 1.25;
  }

  .section-error,
  .section-empty {
    display: grid;
    grid-template-columns: auto minmax(0, 1fr);
    gap: 0.55rem;
    align-items: start;
    margin: 0.1rem 0;
    padding: 0.65rem;
    border: 1px solid #efc8be;
    border-radius: 8px;
    background: #fff1ed;
    color: #bb3f22;
  }

  .section-empty {
    border-color: #d9e0e7;
    background: #f8fafb;
    color: #536170;
  }

  .collapsed .section-error,
  .collapsed .section-empty {
    display: grid;
    place-items: center;
    grid-template-columns: 1fr;
    padding: 0.65rem 0.5rem;
  }

  .section-error strong,
  .section-error p {
    margin: 0;
  }

  .section-error strong {
    display: block;
    color: #7e2d19;
    font-size: 0.8rem;
  }

  .section-error p,
  .section-empty span {
    color: #536170;
    font-size: 0.78rem;
    line-height: 1.35;
  }

  .section-error button {
    margin-top: 0.45rem;
    padding: 0.32rem 0.55rem;
    border: 1px solid #efc8be;
    border-radius: 999px;
    background: #ffffff;
    color: #bb3f22;
    font-size: 0.75rem;
    font-weight: 800;
  }

  .skeleton-label,
  .skeleton-list span {
    overflow: hidden;
    border-radius: 8px;
    background: linear-gradient(90deg, #edf1f4 0%, #f8fafb 50%, #edf1f4 100%);
    background-size: 200% 100%;
    animation: shimmer 1.2s ease-in-out infinite;
  }

  .skeleton-label {
    width: 5rem;
    height: 0.7rem;
    margin: 0.2rem 0.5rem;
  }

  .skeleton-list span {
    height: 2.75rem;
  }

  .collapsed .skeleton-list span {
    height: 3rem;
  }

  .drawer-footer {
    display: grid;
    gap: 0.75rem;
    padding: 0.85rem 1rem 1rem;
    border-top: 1px solid #d9e0e7;
  }

  .collapsed .drawer-footer {
    justify-items: center;
    padding: 0.75rem 0.6rem;
  }

  .session {
    display: grid;
    gap: 0.15rem;
  }

  .session span {
    color: #6b7785;
    font-size: 0.68rem;
    font-weight: 800;
    letter-spacing: 0.08em;
    text-transform: uppercase;
  }

  .session strong {
    color: #314151;
    font-size: 0.82rem;
  }

  .icon-button:focus-visible,
  .back-button:focus-visible,
  .nav-item:focus-visible,
  .route-option:focus-visible,
  .section-error button:focus-visible {
    outline: 2px solid #2454d6;
    outline-offset: 2px;
  }

  .access-mark {
    position: relative;
    display: grid;
    place-items: center;
    width: 3rem;
    min-height: 3rem;
    border: 1px solid #d9e0e7;
    border-radius: 8px;
    background: #f8fafb;
    color: #536170;
    font-size: 1rem;
  }

  .collapsed [data-tooltip]:hover::after,
  .collapsed [data-tooltip]:focus-visible::after,
  .icon-button[data-tooltip]:hover::after,
  .icon-button[data-tooltip]:focus-visible::after {
    position: absolute;
    z-index: 2;
    left: calc(100% + 0.6rem);
    top: 50%;
    transform: translateY(-50%);
    width: max-content;
    max-width: 14rem;
    padding: 0.35rem 0.5rem;
    border-radius: 8px;
    background: #17202a;
    color: #ffffff;
    content: attr(data-tooltip);
    font-size: 0.75rem;
    font-weight: 800;
    line-height: 1.25;
    pointer-events: none;
    white-space: nowrap;
  }

  .icon-button[data-tooltip]:hover::after,
  .icon-button[data-tooltip]:focus-visible::after {
    left: auto;
    right: 0;
    top: calc(100% + 0.45rem);
    transform: none;
  }

  .visually-hidden {
    position: absolute;
    width: 1px;
    height: 1px;
    overflow: hidden;
    clip: rect(0 0 0 0);
    white-space: nowrap;
  }

  @keyframes fade-in {
    from {
      opacity: 0;
    }
    to {
      opacity: 1;
    }
  }

  @keyframes slide-in {
    from {
      transform: translateX(-100%);
    }
    to {
      transform: translateX(0);
    }
  }

  @keyframes shimmer {
    from {
      background-position: 100% 0;
    }
    to {
      background-position: -100% 0;
    }
  }

  @media (max-width: 900px) {
    .drawer-layer {
      display: none;
    }
  }
</style>
