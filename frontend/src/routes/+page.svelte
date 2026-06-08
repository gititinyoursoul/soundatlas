<script lang="ts">
  import { onMount } from 'svelte';
  import { loadSoundAtlasData } from '$lib/api/soundatlas';
  import MapView from '$lib/components/MapView.svelte';
  import RouteFilter from '$lib/components/RouteFilter.svelte';
  import StoryPanel from '$lib/components/StoryPanel.svelte';
  import Timeline from '$lib/components/Timeline.svelte';
  import { filterEvents } from '$lib/data/filters';
  import type { Connection, Event, Place, Route, TimelineRange } from '$lib/types/soundatlas';

  let routes: Route[] = [];
  let places: Place[] = [];
  let events: Event[] = [];
  let connections: Connection[] = [];
  let activeRouteIds = new Set<string>();
  let timelineRange: TimelineRange = { fromYear: 1965, toYear: 1985 };
  let selectedEventId: string | null = null;
  let isLoading = true;
  let errorMessage: string | null = null;

  $: visibleEvents = filterEvents(events, activeRouteIds, timelineRange);
  $: selectedEvent = visibleEvents.find((event) => event.id === selectedEventId) ?? null;
  $: selectedPlace = selectedEvent
    ? places.find((place) => place.id === selectedEvent?.place_id) ?? null
    : null;
  $: selectedRoute = selectedEvent
    ? routes.find((route) => route.id === selectedEvent?.route_id) ?? null
    : null;
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
      activeRouteIds = new Set(data.routes.map((route) => route.id));
    } catch (error) {
      errorMessage = error instanceof Error ? error.message : 'Frontend konnte API-Daten nicht laden.';
    } finally {
      isLoading = false;
    }
  });

  function toggleRoute(routeId: string): void {
    const nextRouteIds = new Set(activeRouteIds);

    if (nextRouteIds.has(routeId)) {
      nextRouteIds.delete(routeId);
    } else {
      nextRouteIds.add(routeId);
    }

    activeRouteIds = nextRouteIds;
  }

  function updateTimelineRange(range: TimelineRange): void {
    timelineRange = range;
  }

  function selectEvent(eventId: string): void {
    selectedEventId = eventId;
  }
</script>

<svelte:head>
  <title>SoundAtlas</title>
  <meta
    name="description"
    content="Interaktive Karte fuer New York 1965-1985 und die Birth-of-Hip-Hop-Route."
  />
</svelte:head>

<main class="app-shell">
  <section class="workspace" aria-label="SoundAtlas Arbeitsbereich">
    <div class="map-column">
      <header class="topbar">
        <div>
          <p>SoundAtlas</p>
          <h1>New York 1965-1985</h1>
        </div>
        <div class="status">
          {#if isLoading}
            Lade API-Daten
          {:else if errorMessage}
            API nicht erreichbar
          {:else}
            {visibleEvents.length} Events sichtbar
          {/if}
        </div>
      </header>

      <div class="controls">
        <RouteFilter {routes} {activeRouteIds} onToggleRoute={toggleRoute} />
      </div>

      {#if errorMessage}
        <div class="notice error">
          <strong>Backend nicht erreichbar.</strong>
          <span>{errorMessage}</span>
        </div>
      {:else}
        <MapView
          events={visibleEvents}
          {places}
          {routes}
          {selectedEventId}
          onSelectEvent={selectEvent}
        />
      {/if}

      <Timeline range={timelineRange} onChangeRange={updateTimelineRange} />
    </div>

    <StoryPanel
      event={selectedEvent}
      place={selectedPlace}
      route={selectedRoute}
      connections={selectedConnections}
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
