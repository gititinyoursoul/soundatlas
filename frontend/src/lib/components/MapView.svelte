<script lang="ts">
  import { onMount } from 'svelte';
  import 'leaflet/dist/leaflet.css';
  import { boroughColors, nycBoroughs, type BoroughFeature } from '$lib/data/nyc-boroughs';
  import {
    getPlaceGeometriesForPlaceIds,
    placeGeometryColors,
    type PlaceGeometryFeature
  } from '$lib/data/nyc-place-geometries';
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
  let boroughLayer: import('leaflet').GeoJSON | null = null;
  let boroughLabelLayer: import('leaflet').LayerGroup | null = null;
  let placeGeometryLayer: import('leaflet').LayerGroup | null = null;
  let placeGeometryLabelLayer: import('leaflet').LayerGroup | null = null;
  let leaflet: typeof import('leaflet') | null = null;
  let lastFramedRouteId: string | null = null;

  $: if (leaflet && markerLayer && map) {
    syncMapState(selectedRouteId, selectedEventId, events, places, routes);
  }

  $: if (leaflet && placeGeometryLayer && placeGeometryLabelLayer && map) {
    renderPlaceGeometries(events, selectedPlace?.id ?? null, selectedRoute?.color ?? null);
  }

  $: visibleRoutes = getVisibleRoutes(routes, events);

  onMount(async () => {
    leaflet = await import('leaflet');

    map = leaflet.map(mapContainer, {
      zoomControl: false,
      attributionControl: true
    });

    map.createPane('boroughs');
    map.createPane('place-geometries');
    map.createPane('borough-labels');
    map.createPane('place-geometry-labels');
    const boroughPane = map.getPane('boroughs');
    const placeGeometryPane = map.getPane('place-geometries');
    const boroughLabelPane = map.getPane('borough-labels');
    const placeGeometryLabelPane = map.getPane('place-geometry-labels');

    if (boroughPane) {
      boroughPane.style.zIndex = '350';
      boroughPane.style.pointerEvents = 'none';
    }

    if (placeGeometryPane) {
      placeGeometryPane.style.zIndex = '355';
      placeGeometryPane.style.pointerEvents = 'none';
    }

    if (boroughLabelPane) {
      boroughLabelPane.style.zIndex = '360';
      boroughLabelPane.style.pointerEvents = 'none';
    }

    if (placeGeometryLabelPane) {
      placeGeometryLabelPane.style.zIndex = '370';
      placeGeometryLabelPane.style.pointerEvents = 'none';
    }

    map.setView(defaultMapCenter, defaultMapZoom);

    leaflet
      .tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
        maxZoom: 19,
        attribution: '&copy; OpenStreetMap contributors',
        className: 'research-atlas-tiles'
      })
      .addTo(map);

    boroughLayer = leaflet
      .geoJSON(nycBoroughs as GeoJSON.GeoJsonObject, {
        pane: 'boroughs',
        interactive: false,
        style: styleBoroughFeature
      })
      .addTo(map);

    boroughLabelLayer = leaflet.layerGroup().addTo(map);
    renderBoroughLabels();

    placeGeometryLayer = leaflet.layerGroup().addTo(map);
    placeGeometryLabelLayer = leaflet.layerGroup().addTo(map);

    leaflet.control.zoom({ position: 'bottomright' }).addTo(map);
    markerLayer = leaflet.layerGroup().addTo(map);

    return () => {
      boroughLayer?.remove();
      boroughLayer = null;
      boroughLabelLayer?.remove();
      boroughLabelLayer = null;
      placeGeometryLayer?.remove();
      placeGeometryLayer = null;
      placeGeometryLabelLayer?.remove();
      placeGeometryLabelLayer = null;
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
          className: 'event-tooltip',
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

  function styleBoroughFeature(feature?: GeoJSON.Feature): import('leaflet').PathOptions {
    const boroughName = (feature as BoroughFeature | undefined)?.properties.name;
    const fillColor = boroughName ? boroughColors[boroughName] : '#8a99a8';

    return {
      color: '#314151',
      fillColor,
      fillOpacity: 0.2,
      opacity: 0.38,
      weight: 1.2
    };
  }

  function renderPlaceGeometries(
    currentEvents: Event[],
    selectedPlaceId: string | null,
    selectedRouteColor: string | null
  ): void {
    if (!leaflet || !placeGeometryLayer || !placeGeometryLabelLayer) {
      return;
    }

    placeGeometryLayer.clearLayers();
    placeGeometryLabelLayer.clearLayers();

    const placeIds = currentEvents.map((event) => event.place_id);

    if (selectedPlaceId) {
      placeIds.push(selectedPlaceId);
    }

    const visibleGeometries = getPlaceGeometriesForPlaceIds(placeIds);

    for (const geometry of visibleGeometries) {
      leaflet
        .geoJSON(geometry as GeoJSON.GeoJsonObject, {
          pane: 'place-geometries',
          interactive: false,
          style: (feature) => stylePlaceGeometryFeature(feature, selectedPlaceId, selectedRouteColor)
        })
        .addTo(placeGeometryLayer);

      const { label, name, placeId } = geometry.properties;
      const isSelected = selectedPlaceId === placeId;

      leaflet
        .marker([label.latitude, label.longitude], {
          interactive: false,
          keyboard: false,
          pane: 'place-geometry-labels',
          icon: leaflet.divIcon({
            className: `place-geometry-label${isSelected ? ' selected' : ''}`,
            html: `<span>${name}</span>`,
            iconAnchor: [66, 12],
            iconSize: [132, 24]
          })
        })
        .addTo(placeGeometryLabelLayer);
    }
  }

  function stylePlaceGeometryFeature(
    feature: GeoJSON.Feature | undefined,
    selectedPlaceId: string | null,
    selectedRouteColor: string | null
  ): import('leaflet').PathOptions {
    const properties = (feature as PlaceGeometryFeature | undefined)?.properties;
    const kind = properties?.kind ?? 'cultural_area';
    const isSelected = properties?.placeId === selectedPlaceId;
    const color = isSelected && selectedRouteColor ? selectedRouteColor : placeGeometryColors[kind];
    const isSite = kind === 'site';

    return {
      color,
      dashArray: properties?.precision === 'interpretive' ? (isSelected ? '8 5' : '5 5') : undefined,
      fillColor: color,
      fillOpacity: isSelected ? (isSite ? 0.32 : 0.14) : isSite ? 0.2 : 0.07,
      opacity: isSelected ? 0.95 : 0.58,
      weight: isSelected ? 2.2 : 1.3
    };
  }

  function renderBoroughLabels(): void {
    if (!leaflet || !boroughLabelLayer) {
      return;
    }

    for (const borough of nycBoroughs.features) {
      const { label, name } = borough.properties;

      leaflet
        .marker([label.latitude, label.longitude], {
          interactive: false,
          keyboard: false,
          pane: 'borough-labels',
          icon: leaflet.divIcon({
            className: 'borough-label',
            html: `<span>${name}</span>`,
            iconAnchor: [58, 12],
            iconSize: [116, 24]
          })
        })
        .addTo(boroughLabelLayer);
    }
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
    background: #e5e8e5;
  }

  .map {
    width: 100%;
    height: 100%;
    min-height: 480px;
  }

  :global(.research-atlas-tiles) {
    filter: grayscale(0.5) saturate(0.82) contrast(0.92) brightness(1.04);
  }

  :global(.borough-label) {
    display: grid;
    place-items: center;
    pointer-events: none;
  }

  :global(.borough-label span) {
    padding: 0.14rem 0.38rem;
    border: 1px solid rgba(23, 32, 42, 0.16);
    border-radius: 999px;
    background: rgba(255, 255, 255, 0.46);
    color: rgba(23, 32, 42, 0.72);
    font-size: 0.68rem;
    font-weight: 900;
    letter-spacing: 0.08em;
    line-height: 1;
    text-transform: uppercase;
    text-shadow:
      0 1px 0 rgba(255, 255, 255, 0.75),
      0 0 10px rgba(255, 255, 255, 0.74);
    box-shadow: 0 6px 18px rgba(23, 32, 42, 0.08);
    backdrop-filter: blur(2px);
  }

  :global(.place-geometry-label) {
    display: grid;
    place-items: center;
    pointer-events: none;
  }

  :global(.place-geometry-label span) {
    padding: 0.16rem 0.42rem;
    border: 1px solid rgba(49, 65, 81, 0.18);
    border-radius: 999px;
    background: rgba(255, 250, 236, 0.68);
    color: rgba(23, 32, 42, 0.78);
    font-size: 0.66rem;
    font-weight: 900;
    letter-spacing: 0.055em;
    line-height: 1;
    text-transform: uppercase;
    text-shadow: 0 1px 0 rgba(255, 255, 255, 0.76);
    box-shadow: 0 8px 18px rgba(23, 32, 42, 0.1);
    backdrop-filter: blur(2px);
  }

  :global(.place-geometry-label.selected span) {
    border-color: rgba(16, 24, 32, 0.34);
    background: rgba(255, 255, 255, 0.84);
    color: #101820;
  }

  :global(.event-tooltip) {
    padding: 0.35rem 0.48rem;
    border: 1px solid rgba(23, 32, 42, 0.2);
    border-radius: 4px;
    background: rgba(255, 255, 255, 0.94);
    color: #17202a;
    font-size: 0.75rem;
    font-weight: 800;
    letter-spacing: 0.01em;
    box-shadow: 0 8px 18px rgba(23, 32, 42, 0.12);
  }

  :global(.event-tooltip::before) {
    border-top-color: rgba(255, 255, 255, 0.94);
  }

  .map-legend {
    position: absolute;
    z-index: 500;
    top: 1rem;
    left: 1rem;
    display: grid;
    gap: 0.35rem;
    max-width: min(16.5rem, calc(100% - 2rem));
    padding: 0.46rem 0.55rem;
    border: 1px solid rgba(49, 65, 81, 0.12);
    border-radius: 8px;
    background: rgba(255, 255, 255, 0.86);
    color: #314151;
    font-size: 0.75rem;
    font-weight: 700;
    backdrop-filter: blur(4px);
    box-shadow: 0 8px 22px rgba(23, 32, 42, 0.1);
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
    border: 1.5px solid #24313d;
    border-radius: 999px;
    background: var(--route-color, #314151);
  }

  .legend-marker.selected {
    width: 0.95rem;
    height: 0.95rem;
    border: 2.5px solid #101820;
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
