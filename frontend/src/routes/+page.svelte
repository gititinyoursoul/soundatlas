<script lang="ts">
  import { onMount } from 'svelte';
  import { loadSoundAtlasData, reviewEventMediaLink } from '$lib/api/soundatlas';
  import MapView from '$lib/components/MapView.svelte';
  import RouteFilter from '$lib/components/RouteFilter.svelte';
  import StoryPanel from '$lib/components/StoryPanel.svelte';
  import Timeline from '$lib/components/Timeline.svelte';
  import { filterEvents } from '$lib/data/filters';
  import type { Connection, Event, Place, Route } from '$lib/types/soundatlas';

  const DEFAULT_ROUTE_ID = 'birth-of-hip-hop';

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
  $: selectedRoute = selectedEvent
    ? routes.find((route) => route.id === selectedEvent?.route_id) ?? null
    : null;
  $: activeRoute = routes.find((route) => route.id === selectedRouteId) ?? null;
  $: timelineRoute = selectedRoute ?? activeRoute ?? routes[0] ?? null;
  $: timelineStartYear = timelineRoute?.year_start ?? 1965;
  $: timelineEndYear = timelineRoute?.year_end ?? 1985;
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

  function selectRoute(routeId: string): void {
    selectedRouteId = routeId;
    selectedEventId = getFirstEventIdForRoute(events, routeId);
  }

  function getInitialRouteId(currentRoutes: Route[]): string | null {
    return (
      currentRoutes.find((route) => route.id === DEFAULT_ROUTE_ID)?.id ??
      currentRoutes[0]?.id ??
      null
    );
  }

  function getFirstEventIdForRoute(currentEvents: Event[], routeId: string | null): string | null {
    return [...filterEvents(currentEvents, routeId)].sort(compareEvents)[0]?.id ?? null;
  }

  function selectEvent(eventId: string): void {
    selectedEventId = eventId;
  }

  async function handleReviewMediaLink(
    eventId: string,
    url: string,
    action: 'reviewed' | 'reject'
  ): Promise<void> {
    const updatedEvent = await reviewEventMediaLink(eventId, url, action);
    events = events.map((event) => (event.id === updatedEvent.id ? updatedEvent : event));
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

  function compareEvents(left: Event, right: Event): number {
    return (
      left.year_start - right.year_start ||
      left.year_end - right.year_end ||
      left.title.localeCompare(right.title)
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
      <header class="topbar">
        <div>
          <p>SoundAtlas</p>
          <h1>New York 1965-1985</h1>
        </div>
        <div class="status">
          {#if isLoading}
            Loading API data
          {:else if errorMessage}
            API unavailable
          {:else}
            {visibleEvents.length} events visible
          {/if}
        </div>
      </header>

      <div class="controls">
        <RouteFilter {routes} {selectedRouteId} onSelectRoute={selectRoute} />
      </div>

      {#if errorMessage}
        <div class="notice error">
          <strong>Backend unavailable.</strong>
          <span>{errorMessage}</span>
        </div>
      {:else}
        <MapView
          events={orderedVisibleEvents}
          {places}
          {routes}
          {selectedEventId}
          onSelectEvent={selectEvent}
        />
      {/if}

      <Timeline
        routeTitle={timelineRoute?.title ?? 'Route'}
        routeStartYear={timelineStartYear}
        routeEndYear={timelineEndYear}
        eventStartYear={selectedEvent?.year_start ?? null}
        eventEndYear={selectedEvent?.year_end ?? null}
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
      onReviewMediaLink={handleReviewMediaLink}
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
    grid-template-columns: minmax(0, 1fr) minmax(20rem, 28rem);
    min-height: calc(100vh - 2rem);
    overflow: hidden;
    border: 1px solid #d9e0e7;
    border-radius: 8px;
    background: #ffffff;
  }

  .map-column {
    display: grid;
    grid-template-rows: auto auto minmax(30rem, 1fr) auto;
    min-width: 0;
  }

  .topbar {
    display: flex;
    align-items: center;
    justify-content: space-between;
    gap: 1rem;
    padding: 1rem;
    border-bottom: 1px solid #d9e0e7;
    background: #ffffff;
  }

  .topbar p,
  .topbar h1 {
    margin: 0;
  }

  .topbar p {
    color: #6b7785;
    font-size: 0.8rem;
    font-weight: 800;
    letter-spacing: 0.08em;
    text-transform: uppercase;
  }

  .topbar h1 {
    color: #17202a;
    font-size: clamp(1.3rem, 2vw, 2.1rem);
    line-height: 1.1;
  }

  .status {
    flex: 0 0 auto;
    padding: 0.45rem 0.65rem;
    border: 1px solid #cfd7df;
    border-radius: 999px;
    color: #314151;
    font-size: 0.85rem;
  }

  .controls {
    padding: 0.85rem 1rem;
    border-bottom: 1px solid #d9e0e7;
    background: #f8fafb;
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

  .notice span {
    color: #536170;
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
      min-height: 100vh;
      border: 0;
      border-radius: 0;
    }

    .topbar {
      align-items: flex-start;
      flex-direction: column;
    }
  }
</style>
