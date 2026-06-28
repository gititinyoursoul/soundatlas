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
  let computedMarkerCount = 0;
  let renderedMarkerCount = 0;
  let markerRenderError: string | null = null;

  $: computedMarkerCount = getEventMarkerPlacements(events, places, routes).length;

  $: if (leaflet && placeGeometryLayer && placeGeometryLabelLayer && map) {
    renderPlaceGeometries(events, selectedPlace?.id ?? null, selectedRoute?.color ?? null);
  }

  $: if (leaflet && markerLayer && map) {
    syncMapState(selectedRouteId, selectedEventId, events, places, routes);
  }

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
    syncMapState(selectedRouteId, selectedEventId, events, places, routes);

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
      const avatarOptions = getMarkerOptions(isSelected, placement.route.color, placement.event);
      const marker = leaflet
        .marker(placement.position, {
          riseOnHover: true,
          zIndexOffset: isSelected ? 1000 : 0,
          icon: leaflet.divIcon({
            className: avatarOptions.className,
            html: avatarOptions.html,
            iconAnchor: avatarOptions.iconAnchor,
            iconSize: avatarOptions.iconSize
          })
        })
        .bindTooltip(`${placement.event.title} (${placement.event.year_start})`, {
          className: 'event-tooltip',
          direction: 'top',
          offset: [0, -20]
        });

      marker.on('click', () => onSelectEvent(placement.event.id));
      marker.addTo(markerLayer);

      if (isSelected) {
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

    try {
      const routeChanged = currentSelectedRouteId !== lastFramedRouteId;
      const placements = renderMarkers(currentSelectedEventId, currentEvents, currentPlaces, currentRoutes, {
        panToSelectedEvent: !routeChanged
      });
      renderedMarkerCount = placements.length;
      markerRenderError = null;

      if (routeChanged) {
        frameRouteBounds(placements);
        lastFramedRouteId = currentSelectedRouteId;
      }
    } catch (error) {
      renderedMarkerCount = 0;
      markerRenderError = error instanceof Error ? error.message : 'Marker rendering failed';
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

  <div class="map-debug" aria-label="Map debug state">
    <span>route: {selectedRouteId ?? 'none'}</span>
    <span>event: {selectedEventId ?? 'none'}</span>
    <span>route events: {events.length}</span>
    <span>placements: {computedMarkerCount}</span>
    <span>markers: {renderedMarkerCount}</span>
    {#if markerRenderError}
      <span class="error">error: {markerRenderError}</span>
    {/if}
  </div>

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

  .map-debug {
    position: absolute;
    z-index: 500;
    top: 1rem;
    right: 1rem;
    display: grid;
    gap: 0.18rem;
    padding: 0.55rem 0.68rem;
    border: 1px solid rgba(23, 32, 42, 0.14);
    border-radius: 8px;
    background: rgba(255, 255, 255, 0.92);
    color: #314151;
    font-size: 0.72rem;
    font-weight: 700;
    line-height: 1.2;
    font-family: ui-monospace, SFMono-Regular, SF Mono, Consolas, Liberation Mono, Menlo, monospace;
    box-shadow: 0 8px 24px rgba(23, 32, 42, 0.12);
    pointer-events: none;
  }

  .map-debug .error {
    color: #8e1f1f;
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

  :global(.event-avatar-marker) {
    background: transparent;
    border: 0;
  }

  :global(.event-avatar-marker .event-avatar) {
    width: 100%;
    height: 100%;
    overflow: hidden;
    border: 2px solid var(--route-color);
    border-radius: 999px;
    background: rgba(255, 255, 255, 0.9);
    box-shadow: 0 8px 16px rgba(23, 32, 42, 0.16);
    transition:
      transform 140ms ease,
      box-shadow 140ms ease,
      border-width 140ms ease;
  }

  :global(.event-avatar-marker.selected .event-avatar) {
    transform: scale(1.08);
    border-width: 3px;
    box-shadow: 0 10px 20px rgba(23, 32, 42, 0.2);
  }

  :global(.event-avatar-marker .event-avatar-image) {
    display: block;
    width: 100%;
    height: 100%;
    object-fit: cover;
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
    .selected-place {
      right: 1rem;
      width: auto;
    }
  }
</style>
