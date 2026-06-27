<script lang="ts">
  import { onMount, tick } from 'svelte';
  import { loadSoundAtlasData, reviewEventLink } from '$lib/api/soundatlas';
  import Icon from '$lib/components/Icon.svelte';
  import MapView from '$lib/components/MapView.svelte';
  import NavigationDrawer from '$lib/components/NavigationDrawer.svelte';
  import StoryPanel from '$lib/components/StoryPanel.svelte';
  import Timeline from '$lib/components/Timeline.svelte';
  import { filterEvents } from '$lib/data/filters';
  import { compareEvents, getFirstEventIdForRoute, getInitialRouteId } from '$lib/data/selection';
  import type {
    Connection,
    Event,
    Place,
    ReviewAction,
    ReviewQueueItem,
    Route
  } from '$lib/types/soundatlas';

  let routes: Route[] = [];
  let places: Place[] = [];
  let events: Event[] = [];
  let connections: Connection[] = [];
  let selectedRouteId: string | null = null;
  let selectedEventId: string | null = null;
  let isLoading = true;
  let errorMessage: string | null = null;
  let isNavigationOpen = false;
  let navigationVariant: 'expanded' | 'collapsed' = 'expanded';
  let activeNavigationItemId = 'routes';
  let navigationTriggerElement: HTMLButtonElement;
  let headerRegionElement: HTMLElement;
  let storyRegionElement: HTMLElement;
  let reviewSavingItemId: string | null = null;
  let reviewErrorMessage: string | null = null;

  $: visibleEvents = filterEvents(events, selectedRouteId);
  $: orderedVisibleEvents = [...visibleEvents].sort(compareEvents);
  $: routeEventCounts = routes.reduce<Record<string, number>>((counts, route) => {
    counts[route.id] = events.filter((event) => event.route_id === route.id).length;
    return counts;
  }, {});
  $: reviewQueueItems = events.flatMap((event) => [
    ...event.media_links
      .filter((mediaLink) => mediaLink.review_status === 'draft')
      .map<ReviewQueueItem>((mediaLink) => ({
        id: `media:${event.id}:${mediaLink.url}`,
        kind: 'media',
        eventId: event.id,
        eventTitle: event.title,
        routeId: event.route_id,
        title: mediaLink.title,
        provider: mediaLink.provider,
        type: mediaLink.type,
        url: mediaLink.url
      })),
    ...event.image_links
      .filter((imageLink) => imageLink.review_status === 'draft')
      .map<ReviewQueueItem>((imageLink) => ({
        id: `image:${event.id}:${imageLink.image_url}`,
        kind: 'image',
        eventId: event.id,
        eventTitle: event.title,
        routeId: event.route_id,
        title: imageLink.title,
        provider: imageLink.provider,
        type: imageLink.type,
        url: imageLink.image_url,
        previewUrl: imageLink.thumbnail_url ?? imageLink.image_url
      }))
  ]);
  $: selectedEvent = orderedVisibleEvents.find((event) => event.id === selectedEventId) ?? null;
  $: selectedEventIndex = selectedEvent
    ? orderedVisibleEvents.findIndex((event) => event.id === selectedEvent.id)
    : -1;
  $: previousEvent = selectedEventIndex > 0 ? orderedVisibleEvents[selectedEventIndex - 1] : null;
  $: nextEvent =
    selectedEventIndex >= 0 && selectedEventIndex < orderedVisibleEvents.length - 1
      ? orderedVisibleEvents[selectedEventIndex + 1]
      : null;
  $: selectedPlace = selectedEvent
    ? places.find((place) => place.id === selectedEvent?.place_id) ?? null
    : null;
  $: selectedPlaceEventCount = selectedPlace
    ? orderedVisibleEvents.filter((event) => event.place_id === selectedPlace?.id).length
    : 0;
  $: activeRoute = routes.find((route) => route.id === selectedRouteId) ?? null;
  $: selectedRoute = selectedEvent
    ? routes.find((route) => route.id === selectedEvent?.route_id) ?? activeRoute
    : activeRoute;
  $: timelineRoute = selectedRoute ?? activeRoute ?? routes[0] ?? null;
  $: timelineStartYear = timelineRoute?.year_start ?? 1965;
  $: timelineEndYear = timelineRoute?.year_end ?? 1985;
  $: headerRouteTitle = activeRoute?.title ?? 'Loading route context';
  $: headerRouteYears = activeRoute ? `${activeRoute.year_start}-${activeRoute.year_end}` : '';
  $: headerRouteSummary =
    activeRoute?.thesis || activeRoute?.summary || 'Fetching the curated route, event sequence, and map places.';
  $: headerRouteTags = activeRoute?.tags.slice(0, 3).join(' / ') ?? 'Route loading';
  $: statusLabel = isLoading
    ? 'Loading API data'
    : errorMessage
      ? 'API unavailable'
      : `${visibleEvents.length} events visible`;
  $: selectedConnections = selectedEvent
    ? connections.filter(
        (connection) =>
          connection.from_event_id === selectedEvent?.id ||
          connection.to_event_id === selectedEvent?.id
      )
    : [];

  onMount(async () => {
    try {
      const data = await loadSoundAtlasData();
      routes = data.routes;
      places = data.places;
      events = data.events;
      connections = data.connections;
      selectedRouteId = getInitialRouteId(data.routes);
      selectedEventId = getFirstEventIdForRoute(data.events, selectedRouteId);
    } catch (error) {
      errorMessage = error instanceof Error ? error.message : 'Frontend konnte API-Daten nicht laden.';
    } finally {
      isLoading = false;
    }
  });

  function selectEvent(eventId: string): void {
    selectedEventId = eventId;
  }

  function selectRoute(routeId: string): void {
    selectedRouteId = routeId;
    selectedEventId = getFirstEventIdForRoute(events, routeId);
    activeNavigationItemId = 'routes';
  }

  function selectReviewItem(item: ReviewQueueItem): void {
    selectedRouteId = item.routeId;
    selectedEventId = item.eventId;
    activeNavigationItemId = 'media-review';
  }

  async function reviewQueueItem(item: ReviewQueueItem, action: ReviewAction): Promise<void> {
    reviewSavingItemId = item.id;
    reviewErrorMessage = null;
    selectedRouteId = item.routeId;
    selectedEventId = item.eventId;
    activeNavigationItemId = 'media-review';

    try {
      const updatedEvent = await reviewEventLink(item.eventId, item.kind, item.url, action);
      events = events.map((event) => (event.id === updatedEvent.id ? updatedEvent : event));
    } catch (error) {
      reviewErrorMessage = error instanceof Error ? error.message : 'Review action failed.';
    } finally {
      reviewSavingItemId = null;
    }
  }

  function openNavigation(): void {
    isNavigationOpen = true;
  }

  async function closeNavigation(): Promise<void> {
    isNavigationOpen = false;
    await tick();
    navigationTriggerElement?.focus();
  }

  function toggleNavigationVariant(): void {
    navigationVariant = navigationVariant === 'expanded' ? 'collapsed' : 'expanded';
  }

  async function selectNavigationItem(itemId: string): Promise<void> {
    activeNavigationItemId = itemId;

    if (itemId === 'routes') {
      return;
    }

    const target = getNavigationTarget(itemId);

    if (!target) {
      return;
    }

    target.scrollIntoView({ block: 'nearest', inline: 'nearest' });
    await tick();
    target.focus({ preventScroll: true });
  }

  function getNavigationTarget(itemId: string): HTMLElement | null {
    if (itemId === 'events' || itemId === 'connections' || itemId === 'sources') {
      return storyRegionElement;
    }

    return headerRegionElement;
  }

  function markStoryNavigationActive(): void {
    if (!['media-review'].includes(activeNavigationItemId)) {
      activeNavigationItemId = 'routes';
    }
  }

  function handleKeydown(event: KeyboardEvent): void {
    if (event.defaultPrevented || isEditableTarget(event.target)) {
      return;
    }

    if (event.key === 'ArrowLeft' && previousEvent) {
      event.preventDefault();
      selectEvent(previousEvent.id);
    }

    if (event.key === 'ArrowRight') {
      const eventToSelect = nextEvent ?? (!selectedEvent ? orderedVisibleEvents[0] : null);

      if (eventToSelect) {
        event.preventDefault();
        selectEvent(eventToSelect.id);
      }
    }
  }

  function isEditableTarget(target: EventTarget | null): boolean {
    return (
      target instanceof HTMLInputElement ||
      target instanceof HTMLTextAreaElement ||
      target instanceof HTMLSelectElement ||
      (target instanceof HTMLElement && target.isContentEditable)
    );
  }

</script>

<svelte:window on:keydown={handleKeydown} />

<svelte:head>
  <title>SoundAtlas</title>
  <meta
    name="description"
    content="Interactive map for New York 1965-1985 and the Birth of Hip-Hop route."
  />
</svelte:head>

<main class="app-shell">
  <NavigationDrawer
    open={isNavigationOpen}
    variant={navigationVariant}
    activeItemId={activeNavigationItemId}
    {routes}
    {selectedRouteId}
    {routeEventCounts}
    {reviewQueueItems}
    {reviewSavingItemId}
    {reviewErrorMessage}
    {isLoading}
    {errorMessage}
    onClose={closeNavigation}
    onToggleVariant={toggleNavigationVariant}
    onSelectItem={selectNavigationItem}
    onSelectRoute={selectRoute}
    onSelectReviewItem={selectReviewItem}
    onReviewQueueItem={reviewQueueItem}
  />

  <section class="workspace" aria-label="SoundAtlas workspace">
    <div class="map-column">
      <header class="app-header" bind:this={headerRegionElement} tabindex="-1">
        <div class="scope-cluster">
          <button
            bind:this={navigationTriggerElement}
            type="button"
            class="drawer-trigger"
            aria-label="Open navigation"
            aria-haspopup="dialog"
            aria-expanded={isNavigationOpen}
            on:click={openNavigation}
          >
            <Icon name="layers" />
          </button>

          <div class="scope-block">
            <p>SoundAtlas</p>
            <h1>New York 1965-1985</h1>
          </div>
        </div>

        <div class="route-context" aria-label="Selected route context">
          <div class="route-heading">
            <p>Active route</p>
            <div>
              <h2>{headerRouteTitle}</h2>
              {#if headerRouteYears}
                <span>{headerRouteYears}</span>
              {/if}
            </div>
          </div>
          <p class="route-summary">{headerRouteSummary}</p>
          <div class="route-meta">
            <span>{orderedVisibleEvents.length} events</span>
            <span>{headerRouteTags}</span>
          </div>
        </div>

        <div class="status">
          {statusLabel}
        </div>
      </header>

      {#if errorMessage}
        <div class="notice error">
          <strong>Backend unavailable</strong>
          <span>{errorMessage}</span>
          <small>Start the FastAPI backend on http://127.0.0.1:8000, then refresh this page.</small>
        </div>
      {:else}
        <section
          class="map-region"
          tabindex="-1"
          aria-label="Map exploration"
        >
          <MapView
            events={orderedVisibleEvents}
            {places}
            {routes}
            {selectedEventId}
            {selectedPlace}
            {selectedRoute}
            {selectedPlaceEventCount}
            onSelectEvent={selectEvent}
          />
        </section>
      {/if}

      <section
        class="timeline-region"
        tabindex="-1"
        aria-label="Timeline sequence"
      >
        <Timeline
          routeTitle={timelineRoute?.title ?? 'Route'}
          routeStartYear={timelineStartYear}
          routeEndYear={timelineEndYear}
          eventStartYear={selectedEvent?.year_start ?? null}
          eventEndYear={selectedEvent?.year_end ?? null}
          events={orderedVisibleEvents}
          {selectedEventId}
          onSelectEvent={selectEvent}
        />
      </section>
    </div>

    <section
      bind:this={storyRegionElement}
      class="story-region"
      tabindex="-1"
      aria-label="Story and research details"
      on:focusin={markStoryNavigationActive}
    >
      <StoryPanel
        event={selectedEvent}
        place={selectedPlace}
        route={selectedRoute}
        connections={selectedConnections}
        {previousEvent}
        {nextEvent}
        currentEventIndex={selectedEventIndex}
        eventCount={orderedVisibleEvents.length}
        onNavigateEvent={selectEvent}
        {isLoading}
        {errorMessage}
      />
    </section>
  </section>
</main>

<style>
  .app-shell {
    min-height: 100vh;
    padding: 1rem;
    background: #f3f5f7;
  }

  .workspace {
    display: grid;
    grid-template-columns: minmax(0, 1fr) minmax(18rem, 23rem);
    grid-template-rows: minmax(0, 1fr);
    min-height: calc(100vh - 2rem);
    height: calc(100vh - 2rem);
    overflow: hidden;
    border: 1px solid #d9e0e7;
    border-radius: 8px;
    background: #ffffff;
  }

  .map-column {
    display: grid;
    grid-template-rows: auto minmax(0, 1fr) auto;
    min-height: 0;
    min-width: 0;
  }

  .app-header {
    display: grid;
    grid-template-columns: minmax(10rem, 16rem) minmax(0, 1fr) auto;
    align-items: start;
    gap: 1rem;
    padding: 0.75rem 1rem;
    border-bottom: 1px solid #d9e0e7;
    background: #ffffff;
  }

  .app-header:focus,
  .map-region:focus,
  .timeline-region:focus,
  .story-region:focus {
    outline: 2px solid #2454d6;
    outline-offset: -2px;
  }

  .scope-cluster {
    display: flex;
    align-items: center;
    gap: 0.75rem;
    min-width: 0;
  }

  .drawer-trigger {
    display: grid;
    flex: 0 0 auto;
    place-items: center;
    width: 2.35rem;
    height: 2.35rem;
    border: 1px solid #cfd7df;
    border-radius: 8px;
    background: #ffffff;
    color: #314151;
    font-size: 1.1rem;
  }

  .drawer-trigger:hover {
    background: #f3f6f8;
  }

  .drawer-trigger:focus-visible {
    outline: 2px solid #2454d6;
    outline-offset: 2px;
  }

  .scope-block p,
  .scope-block h1 {
    margin: 0;
  }

  .scope-block p {
    color: #6b7785;
    font-size: 0.72rem;
    font-weight: 800;
    letter-spacing: 0.08em;
    text-transform: uppercase;
  }

  .scope-block h1 {
    color: #17202a;
    font-size: 1.05rem;
    line-height: 1.1;
  }

  .status {
    flex: 0 0 auto;
    padding: 0.38rem 0.6rem;
    border: 1px solid #cfd7df;
    border-radius: 999px;
    color: #314151;
    font-size: 0.78rem;
    font-weight: 700;
    white-space: nowrap;
  }

  .route-context {
    display: grid;
    gap: 0.28rem;
    min-width: 0;
  }

  .route-heading {
    display: flex;
    align-items: baseline;
    gap: 0.6rem;
    min-width: 0;
  }

  .route-heading p,
  .route-heading h2,
  .route-summary {
    margin: 0;
  }

  .route-heading p {
    flex: 0 0 auto;
    color: #6b7785;
    font-size: 0.7rem;
    font-weight: 800;
    letter-spacing: 0.08em;
    text-transform: uppercase;
  }

  .route-heading div {
    display: flex;
    align-items: baseline;
    gap: 0.55rem;
    min-width: 0;
  }

  .route-heading h2 {
    overflow: hidden;
    color: #17202a;
    font-size: 0.98rem;
    line-height: 1.2;
    text-overflow: ellipsis;
    white-space: nowrap;
  }

  .route-heading span {
    flex: 0 0 auto;
    color: #314151;
    font-size: 0.78rem;
    font-weight: 800;
  }

  .route-summary {
    max-width: 68rem;
    color: #314151;
    font-size: 0.8rem;
    line-height: 1.35;
    overflow: hidden;
    display: -webkit-box;
    -webkit-box-orient: vertical;
    -webkit-line-clamp: 1;
  }

  .route-meta {
    display: flex;
    flex-wrap: wrap;
    gap: 0.45rem;
  }

  .route-meta span {
    padding: 0.16rem 0.4rem;
    border: 1px solid #efc8be;
    border-radius: 999px;
    color: #7e2d19;
    font-size: 0.68rem;
    font-weight: 700;
  }

  .notice {
    display: grid;
    place-content: center;
    gap: 0.5rem;
    min-height: 30rem;
    padding: 2rem;
    text-align: center;
  }

  .notice strong {
    color: #17202a;
  }

  .notice span,
  .notice small {
    color: #536170;
  }

  .notice small {
    font-size: 0.82rem;
  }

  .error {
    background: #fff7f4;
  }

  .map-region,
  .timeline-region,
  .story-region {
    min-width: 0;
    min-height: 0;
  }

  .map-region {
    display: grid;
  }

  .timeline-region {
    display: grid;
  }

  .story-region {
    display: grid;
    min-height: 0;
  }

  @media (max-width: 900px) {
    .app-shell {
      padding: 0;
    }

    .workspace {
      grid-template-columns: 1fr;
      grid-template-rows: auto;
      min-height: 100vh;
      height: auto;
      border: 0;
      border-radius: 0;
    }

    .app-header {
      grid-template-columns: 1fr;
      align-items: flex-start;
      gap: 0.7rem;
    }

    .drawer-trigger {
      display: none;
    }

    .map-column {
      grid-template-rows: auto minmax(30rem, 58vh) auto;
      min-height: 100vh;
    }

    .route-heading,
    .route-heading div {
      align-items: flex-start;
      flex-direction: column;
      gap: 0.2rem;
    }

    .route-heading h2 {
      white-space: normal;
    }
  }
</style>
