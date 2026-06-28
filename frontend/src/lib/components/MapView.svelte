<script lang="ts">
  import { onMount } from 'svelte';
  import 'leaflet/dist/leaflet.css';
  import type { Event, Place, Route } from '$lib/types/soundatlas';
  import {
    getEventMarkerPlacements,
    getMarkerOptions,
    getVisibleRoutes,
    type EventMarkerPlacement
  } from './map-utils';

  export let events: Event[] = [];
  export let places: Place[] = [];
  export let routes: Route[] = [];
  export let selectedRouteId: string | null = null;
  export let selectedEventId: string | null = null;
  export let selectedPlace: Place | null = null;
  export let selectedRoute: Route | null = null;
  export let selectedPlaceEventCount = 0;
  export let onSelectEvent: (eventId: string) => void = () => {};

  const defaultMapCenter: [number, number] = [40.82, -73.93];
  const defaultMapZoom = 12;
  const routeFitPadding: [number, number] = [64, 64];
  const routeFitMaxZoom = 18;

  let mapContainer: HTMLDivElement;
  let map: import('leaflet').Map | null = null;
  let markerLayer: import('leaflet').LayerGroup | null = null;
  let leaflet: typeof import('leaflet') | null = null;
  let lastFramedRouteId: string | null = null;

  $: if (leaflet && markerLayer && map) {
    syncMapState(selectedRouteId, selectedEventId, events, places, routes);
  }

  $: visibleRoutes = getVisibleRoutes(routes, events);

  onMount(async () => {
    leaflet = await import('leaflet');

    map = leaflet.map(mapContainer, {
      zoomControl: false,
      attributionControl: true
    });

    map.setView(defaultMapCenter, defaultMapZoom);

    leaflet
      .tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
        maxZoom: 19,
        attribution: '&copy; OpenStreetMap contributors'
      })
      .addTo(map);

    leaflet.control.zoom({ position: 'bottomright' }).addTo(map);
    markerLayer = leaflet.layerGroup().addTo(map);

    return () => {
      map?.remove();
      map = null;
    };
  });

  function renderMarkers(
    activeEventId = selectedEventId,
    currentEvents = events,
    currentPlaces = places,
    currentRoutes = routes,
    options: { panToSelectedEvent?: boolean } = {}
  ): EventMarkerPlacement[] {
    if (!leaflet || !markerLayer) {
      return [];
    }

    markerLayer.clearLayers();

    const placements = getEventMarkerPlacements(currentEvents, currentPlaces, currentRoutes);
    let selectedMarkerPosition: [number, number] | null = null;

    for (const placement of placements) {
      const isSelected = activeEventId === placement.event.id;
      const marker = leaflet
        .circleMarker(placement.position, getMarkerOptions(isSelected, placement.route.color))
        .bindTooltip(`${placement.event.title} (${placement.event.year_start})`, {
          direction: 'top',
          offset: [0, -8]
        });

      marker.on('click', () => onSelectEvent(placement.event.id));
      marker.addTo(markerLayer);

      if (isSelected) {
        marker.bringToFront();
        selectedMarkerPosition = placement.position;
      }
    }

    if (options.panToSelectedEvent !== false && selectedMarkerPosition && map) {
      map.panTo(selectedMarkerPosition, {
        animate: true,
        duration: 0.35
      });
    }

    return placements;
  }

  function syncMapState(
    currentSelectedRouteId: string | null,
    currentSelectedEventId: string | null,
    currentEvents: Event[],
    currentPlaces: Place[],
    currentRoutes: Route[]
  ): void {
    if (!map || !leaflet || !markerLayer) {
      return;
    }

    const routeChanged = currentSelectedRouteId !== lastFramedRouteId;
    const placements = renderMarkers(currentSelectedEventId, currentEvents, currentPlaces, currentRoutes, {
      panToSelectedEvent: !routeChanged
    });

    if (routeChanged) {
      frameRouteBounds(placements);
      lastFramedRouteId = currentSelectedRouteId;
    }
  }

  function frameRouteBounds(routePlacements: EventMarkerPlacement[]): void {
    if (!leaflet || !map) {
      return;
    }

    if (routePlacements.length === 0) {
      map.setView(defaultMapCenter, defaultMapZoom);
      return;
    }

    const bounds = leaflet.latLngBounds(routePlacements.map((placement) => placement.position));

    if (!bounds.isValid()) {
      map.setView(defaultMapCenter, defaultMapZoom);
      return;
    }

    map.fitBounds(bounds, {
      padding: routeFitPadding,
      maxZoom: routeFitMaxZoom,
      animate: true,
      duration: 0.35
    });
  }

</script>

<div class="map-shell">
  <div bind:this={mapContainer} class="map" aria-label="SoundAtlas map"></div>

  {#if visibleRoutes.length > 0}
    <div class="map-legend" aria-label="Map legend">
      <div class="legend-row">
        <span class="legend-marker selected"></span>
        <span>Selected event</span>
      </div>
      {#each visibleRoutes as route}
        <div class="legend-row">
          <span class="legend-marker" style={`--route-color: ${route.color}`}></span>
          <span>{route.title}</span>
        </div>
      {/each}
    </div>
  {/if}

  {#if events.length === 0}
    <div class="map-empty">No events in the active time range.</div>
  {/if}

  {#if selectedPlace}
    <aside
      class="selected-place"
      style={`--route-color: ${selectedRoute?.color ?? '#e4572e'}`}
      aria-label="Selected map place"
      aria-live="polite"
    >
      <span>Selected place</span>
      <strong>{selectedPlace.name}</strong>
      <p>
        {selectedPlace.borough}
        {#if selectedPlaceEventCount > 0}
          · {selectedPlaceEventCount} {selectedPlaceEventCount === 1 ? 'route event' : 'route events'}
        {/if}
      </p>
    </aside>
  {/if}
</div>

<style>
  .map-shell {
    position: relative;
    min-height: 480px;
    height: 100%;
    overflow: hidden;
    background: #dfe7ed;
  }

  .map {
    width: 100%;
    height: 100%;
    min-height: 480px;
  }

  .map-legend {
    position: absolute;
    z-index: 500;
    top: 1rem;
    left: 1rem;
    display: grid;
    gap: 0.35rem;
    max-width: min(16.5rem, calc(100% - 2rem));
    padding: 0.5rem 0.6rem;
    border: 1px solid rgba(207, 215, 223, 0.9);
    border-radius: 8px;
    background: rgba(255, 255, 255, 0.94);
    color: #314151;
    font-size: 0.78rem;
    font-weight: 700;
    box-shadow: 0 8px 24px rgba(23, 32, 42, 0.12);
  }

  .selected-place {
    position: absolute;
    z-index: 500;
    left: 1rem;
    bottom: 1rem;
    display: grid;
    gap: 0.18rem;
    width: min(22rem, calc(100% - 2rem));
    padding: 0.62rem 0.72rem;
    border: 1px solid rgba(23, 32, 42, 0.14);
    border-left: 0.35rem solid var(--route-color);
    border-radius: 8px;
    background: rgba(255, 255, 255, 0.95);
    box-shadow: 0 12px 30px rgba(23, 32, 42, 0.16);
  }

  .selected-place span {
    color: #6b7785;
    font-size: 0.75rem;
    font-weight: 800;
    letter-spacing: 0.06em;
    text-transform: uppercase;
  }

  .selected-place strong {
    color: #17202a;
    font-size: 0.94rem;
    line-height: 1.2;
  }

  .selected-place p {
    margin: 0;
    color: #536170;
    font-size: 0.78rem;
    line-height: 1.35;
  }

  .legend-row {
    display: flex;
    align-items: center;
    gap: 0.45rem;
    min-width: 0;
  }

  .legend-row span:last-child {
    overflow: hidden;
    text-overflow: ellipsis;
    white-space: nowrap;
  }

  .legend-marker {
    flex: 0 0 auto;
    width: 0.8rem;
    height: 0.8rem;
    border: 1px solid #17202a;
    border-radius: 999px;
    background: var(--route-color, #314151);
  }

  .legend-marker.selected {
    width: 0.95rem;
    height: 0.95rem;
    border: 2px solid #17202a;
    background: #2e7d32;
  }

  .map-empty {
    position: absolute;
    top: 1rem;
    left: 50%;
    transform: translateX(-50%);
    max-width: min(24rem, calc(100% - 2rem));
    padding: 0.65rem 0.85rem;
    border: 1px solid #cfd7df;
    border-radius: 8px;
    background: rgba(255, 255, 255, 0.94);
    color: #314151;
    font-size: 0.9rem;
    box-shadow: 0 8px 24px rgba(23, 32, 42, 0.12);
  }

  @media (max-width: 640px) {
    .map-legend {
      max-width: min(15rem, calc(100% - 2rem));
    }

    .selected-place {
      right: 1rem;
      width: auto;
    }
  }
</style>
