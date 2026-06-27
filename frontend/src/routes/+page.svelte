<script lang="ts">
  import { onMount } from 'svelte';
  import { loadSoundAtlasData } from '$lib/api/soundatlas';
  import MapView from '$lib/components/MapView.svelte';
  import StoryPanel from '$lib/components/StoryPanel.svelte';
  import Timeline from '$lib/components/Timeline.svelte';
  import { filterEvents } from '$lib/data/filters';
  import { compareEvents, getFirstEventIdForRoute, getInitialRouteId } from '$lib/data/selection';
  import type { Connection, Event, Place, Route } from '$lib/types/soundatlas';

  let routes: Route[] = [];
  let places: Place[] = [];
  let events: Event[] = [];
  let connections: Connection[] = [];
  let selectedRouteId: string | null = null;
  let selectedEventId: string | null = null;
  let isLoading = true;
  let errorMessage: string | null = null;

  $: visibleEvents = filterEvents(events, selectedRouteId);
  $: orderedVisibleEvents = [...visibleEvents].sort(compareEvents);
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
  $: selectedRoute = selectedEvent
    ? routes.find((route) => route.id === selectedEvent?.route_id) ?? null
    : null;
  $: activeRoute = routes.find((route) => route.id === selectedRouteId) ?? null;
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
  <section class="workspace" aria-label="SoundAtlas workspace">
    <div class="map-column">
      <header class="app-header">
        <div class="scope-block">
          <p>SoundAtlas</p>
          <h1>New York 1965-1985</h1>
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
      {/if}

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
    </div>

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
