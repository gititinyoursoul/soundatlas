<script lang="ts">
  import { onMount } from 'svelte';
  import type { Feature, GeoJsonObject } from 'geojson';
  import 'leaflet/dist/leaflet.css';
  import {
    boroughColors,
    nycBoroughs,
    type BoroughFeature
  } from '$lib/data/nyc-boroughs';
  import { resolvePlaceSelection } from '$lib/data/spatial';
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
  export let selectedPlaceId: string | null = null;
  export let contextPlaceId: string | null = null;
  export let selectedPlace: Place | null = null;
  export let selectedRoute: Route | null = null;
  export let selectedPlaceEventCount = 0;
  export let onSelectLocation: (
    eventId: string,
    placeId: string
  ) => void = () => {};

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
  let relationshipLayer: import('leaflet').LayerGroup | null = null;
  let leaflet: typeof import('leaflet') | null = null;
  let lastFramedRouteId: string | null = null;
  let lastFramedEventId: string | null = null;
  let lastFramedContextPlaceId: string | null = null;
  let placeChoice: { place: Place; events: Event[] } | null = null;

  $: if (leaflet && placeGeometryLayer && placeGeometryLabelLayer && map) {
    renderPlaceGeometries(
      events,
      places,
      selectedEventId,
      contextPlaceId ?? selectedPlaceId,
      selectedRoute?.color ?? null
    );
  }

  $: if (leaflet && relationshipLayer && map) {
    renderRelationships(events, places, selectedEventId);
  }

  $: if (leaflet && markerLayer && map) {
    syncMapState(
      selectedRouteId,
      selectedEventId,
      selectedPlaceId,
      contextPlaceId,
      events,
      places,
      routes
    );
  }

  onMount(() => {
    let isMounted = true;

    void initializeMap(() => isMounted);

    return () => {
      isMounted = false;
      disposeMap();
    };
  });

  async function initializeMap(isMounted: () => boolean): Promise<void> {
    leaflet = await import('leaflet');

    if (!isMounted()) {
      leaflet = null;
      return;
    }

    map = leaflet.map(mapContainer, {
      zoomControl: false,
      attributionControl: true
    });

    map.createPane('boroughs');
    map.createPane('place-geometries');
    map.createPane('place-relationships');
    map.createPane('borough-labels');
    map.createPane('place-geometry-labels');
    const boroughPane = map.getPane('boroughs');
    const placeGeometryPane = map.getPane('place-geometries');
    const relationshipPane = map.getPane('place-relationships');
    const boroughLabelPane = map.getPane('borough-labels');
    const placeGeometryLabelPane = map.getPane('place-geometry-labels');

    if (boroughPane) {
      boroughPane.style.zIndex = '350';
      boroughPane.style.pointerEvents = 'none';
    }

    if (placeGeometryPane) {
      placeGeometryPane.style.zIndex = '355';
    }

    if (relationshipPane) {
      relationshipPane.style.zIndex = '365';
    }

    if (boroughLabelPane) {
      boroughLabelPane.style.zIndex = '360';
      boroughLabelPane.style.pointerEvents = 'none';
    }

    if (placeGeometryLabelPane) {
      placeGeometryLabelPane.style.zIndex = '370';
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
      .geoJSON(nycBoroughs as GeoJsonObject, {
        pane: 'boroughs',
        interactive: false,
        style: styleBoroughFeature
      })
      .addTo(map);

    boroughLabelLayer = leaflet.layerGroup().addTo(map);
    renderBoroughLabels();

    placeGeometryLayer = leaflet.layerGroup().addTo(map);
    placeGeometryLabelLayer = leaflet.layerGroup().addTo(map);
    relationshipLayer = leaflet.layerGroup().addTo(map);

    leaflet.control.zoom({ position: 'bottomright' }).addTo(map);
    markerLayer = leaflet.layerGroup().addTo(map);
    syncMapState(
      selectedRouteId,
      selectedEventId,
      selectedPlaceId,
      contextPlaceId,
      events,
      places,
      routes
    );
  }

  function disposeMap(): void {
    boroughLayer?.remove();
    boroughLayer = null;
    boroughLabelLayer?.remove();
    boroughLabelLayer = null;
    placeGeometryLayer?.remove();
    placeGeometryLayer = null;
    placeGeometryLabelLayer?.remove();
    placeGeometryLabelLayer = null;
    relationshipLayer?.remove();
    relationshipLayer = null;
    markerLayer?.remove();
    markerLayer = null;
    map?.remove();
    map = null;
    leaflet = null;
  }

  function renderMarkers(
    activeEventId = selectedEventId,
    focusedPlaceId = selectedPlaceId,
    currentEvents = events,
    currentPlaces = places,
    currentRoutes = routes,
    options: { panToSelectedEvent?: boolean } = {}
  ): EventMarkerPlacement[] {
    if (!leaflet || !markerLayer) {
      return [];
    }

    markerLayer.clearLayers();

    const placements = getEventMarkerPlacements(
      currentEvents,
      currentPlaces,
      currentRoutes
    );
    let selectedMarkerPosition: [number, number] | null = null;

    for (const placement of placements) {
      const isSelected = activeEventId === placement.event.id;
      const avatarOptions = getMarkerOptions(
        isSelected,
        placement.route.color,
        placement.event
      );
      const isFocused = focusedPlaceId === placement.place.id;
      const marker = leaflet
        .marker(placement.position, {
          riseOnHover: true,
          zIndexOffset: isSelected ? 1000 : 0,
          icon: leaflet.divIcon({
            className: `${avatarOptions.className}${isFocused ? ' focused' : ''}`,
            html: avatarOptions.html,
            iconAnchor: avatarOptions.iconAnchor,
            iconSize: avatarOptions.iconSize
          })
        })
        .bindTooltip(
          `${placement.event.route_entry_role === 'context' ? 'Route context: ' : ''}${placement.event.title} (${placement.event.year_start})`,
          {
            className: 'event-tooltip',
            direction: 'top',
            offset: [0, -20]
          }
        );

      marker.on('click', () =>
        onSelectLocation(placement.event.id, placement.place.id)
      );
      marker.addTo(markerLayer);

      if (isFocused || (isSelected && !selectedMarkerPosition)) {
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
    currentSelectedPlaceId: string | null,
    currentContextPlaceId: string | null,
    currentEvents: Event[],
    currentPlaces: Place[],
    currentRoutes: Route[]
  ): void {
    if (!map || !leaflet || !markerLayer) {
      return;
    }

    try {
      const routeChanged = currentSelectedRouteId !== lastFramedRouteId;
      const eventChanged = currentSelectedEventId !== lastFramedEventId;
      const contextPlaceChanged =
        currentContextPlaceId !== lastFramedContextPlaceId;
      renderMarkers(
        currentSelectedEventId,
        currentContextPlaceId ?? currentSelectedPlaceId,
        currentEvents,
        currentPlaces,
        currentRoutes,
        {
          panToSelectedEvent:
            !routeChanged && !eventChanged && !contextPlaceChanged
        }
      );

      if (routeChanged) {
        frameRouteBounds(currentEvents, currentPlaces);
        lastFramedRouteId = currentSelectedRouteId;
      } else if (eventChanged || contextPlaceChanged) {
        if (currentContextPlaceId) {
          framePlace(currentContextPlaceId, currentPlaces);
        } else {
          frameSelectedEvent(
            currentSelectedEventId,
            currentEvents,
            currentPlaces
          );
        }
      }
      lastFramedEventId = currentSelectedEventId;
      lastFramedContextPlaceId = currentContextPlaceId;
    } catch (error) {
      console.error(error);
    }
  }

  function frameRouteBounds(
    currentEvents: Event[],
    currentPlaces: Place[]
  ): void {
    if (!leaflet || !map) {
      return;
    }

    const placeById = new Map(currentPlaces.map((place) => [place.id, place]));
    const positions = currentEvents.flatMap((event) =>
      event.place_ids.flatMap((placeId) => {
        const place = placeById.get(placeId);
        return place ? getPlaceBoundsPositions(place) : [];
      })
    );

    if (positions.length === 0) {
      map.setView(defaultMapCenter, defaultMapZoom);
      return;
    }

    const bounds = leaflet.latLngBounds(positions);

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

  function frameSelectedEvent(
    eventId: string | null,
    currentEvents: Event[],
    currentPlaces: Place[]
  ): void {
    if (!leaflet || !map || !eventId) {
      return;
    }

    const event = currentEvents.find((item) => item.id === eventId);
    const placeById = new Map(currentPlaces.map((place) => [place.id, place]));
    const positions = event?.place_ids.flatMap((placeId) => {
      const place = placeById.get(placeId);
      return place ? getPlaceBoundsPositions(place) : [];
    });

    if (!positions || positions.length === 0) {
      return;
    }
    if (positions.length === 1) {
      map.panTo(positions[0], { animate: true, duration: 0.35 });
      return;
    }

    map.fitBounds(leaflet.latLngBounds(positions), {
      padding: routeFitPadding,
      maxZoom: routeFitMaxZoom,
      animate: true,
      duration: 0.35
    });
  }

  function framePlace(placeId: string, currentPlaces: Place[]): void {
    if (!leaflet || !map) return;
    const place = currentPlaces.find((item) => item.id === placeId);
    if (!place) return;
    const positions = getPlaceBoundsPositions(place);
    if (positions.length === 1) {
      map.panTo(positions[0], { animate: true, duration: 0.35 });
      return;
    }
    map.fitBounds(leaflet.latLngBounds(positions), {
      padding: routeFitPadding,
      maxZoom: routeFitMaxZoom,
      animate: true,
      duration: 0.35
    });
  }

  function getPlaceBoundsPositions(place: Place): [number, number][] {
    const focus: [number, number] = [place.latitude, place.longitude];
    if (!place.geometry) {
      return [focus];
    }

    const polygons =
      place.geometry.type === 'Polygon'
        ? [place.geometry.coordinates]
        : place.geometry.coordinates;
    return [
      focus,
      ...polygons.flatMap((polygon) =>
        polygon.flatMap((ring) =>
          ring.map(
            ([longitude, latitude]) => [latitude, longitude] as [number, number]
          )
        )
      )
    ];
  }

  function styleBoroughFeature(
    feature?: Feature
  ): import('leaflet').PathOptions {
    const boroughName = (feature as BoroughFeature | undefined)?.properties
      .name;
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
    currentPlaces: Place[],
    activeEventId: string | null,
    focusedPlaceId: string | null,
    selectedRouteColor: string | null
  ): void {
    if (!leaflet || !placeGeometryLayer || !placeGeometryLabelLayer) {
      return;
    }

    placeGeometryLayer.clearLayers();
    placeGeometryLabelLayer.clearLayers();

    const visiblePlaceIds = new Set(
      currentEvents.flatMap((event) => event.place_ids)
    );
    const activeEvent = currentEvents.find(
      (event) => event.id === activeEventId
    );

    for (const place of currentPlaces) {
      if (!place.geometry || !visiblePlaceIds.has(place.id)) {
        continue;
      }

      const feature = {
        type: 'Feature',
        properties: { placeId: place.id },
        geometry: place.geometry
      } as GeoJsonObject;

      leaflet
        .geoJSON(feature, {
          pane: 'place-geometries',
          interactive: true,
          style: () =>
            stylePlaceGeometry(
              place,
              activeEvent?.place_ids.includes(place.id) ?? false,
              focusedPlaceId === place.id,
              selectedRouteColor
            ),
          onEachFeature: (_feature, layer) => {
            layer.on('click', () => handlePlaceClick(place));
            layer.bindTooltip(place.name, {
              className: 'event-tooltip',
              direction: 'top'
            });
          }
        })
        .addTo(placeGeometryLayer);

      const isSelected = activeEvent?.place_ids.includes(place.id) ?? false;
      const isFocused = focusedPlaceId === place.id;

      const labelMarker = leaflet.marker([place.latitude, place.longitude], {
        interactive: true,
        keyboard: true,
        pane: 'place-geometry-labels',
        icon: leaflet.divIcon({
          className: `place-geometry-label${isSelected ? ' selected' : ''}${isFocused ? ' focused' : ''}`,
          html: `<span>${place.name}</span>`,
          iconAnchor: [66, 12],
          iconSize: [132, 24]
        })
      });
      labelMarker.on('click', () => handlePlaceClick(place));
      labelMarker.addTo(placeGeometryLabelLayer);
    }
  }

  function stylePlaceGeometry(
    place: Place,
    isSelected: boolean,
    isFocused: boolean,
    selectedRouteColor: string | null
  ): import('leaflet').PathOptions {
    const isSite = place.geometry_precision === 'site';
    const fillColor = isSite ? '#3b9468' : '#8f7353';
    const strokeColor =
      isSelected && selectedRouteColor ? selectedRouteColor : fillColor;

    return {
      color: strokeColor,
      dashArray:
        place.geometry_precision === 'interpretive'
          ? isFocused
            ? '8 5'
            : '5 5'
          : undefined,
      fillColor,
      fillOpacity: isSelected ? (isSite ? 0.26 : 0.12) : isSite ? 0.2 : 0.07,
      opacity: isFocused ? 1 : isSelected ? 0.92 : 0.58,
      weight: isFocused ? 4 : isSelected ? 2.4 : 1.3
    };
  }

  function handlePlaceClick(place: Place): void {
    const resolution = resolvePlaceSelection(events, selectedEventId, place.id);

    if (resolution.eventId) {
      placeChoice = null;
      onSelectLocation(resolution.eventId, place.id);
      return;
    }

    if (resolution.needsChoice) {
      const matchingIds = new Set(resolution.eventIds);
      placeChoice = {
        place,
        events: events.filter((event) => matchingIds.has(event.id))
      };
    }
  }

  function renderRelationships(
    currentEvents: Event[],
    currentPlaces: Place[],
    activeEventId: string | null
  ): void {
    if (!leaflet || !relationshipLayer) {
      return;
    }

    relationshipLayer.clearLayers();
    const event = currentEvents.find((item) => item.id === activeEventId);
    if (!event) {
      return;
    }

    const placeById = new Map(currentPlaces.map((place) => [place.id, place]));
    for (const relationship of event.place_relationships) {
      const fromPlace = placeById.get(relationship.from_place_id);
      const toPlace = placeById.get(relationship.to_place_id);
      if (!fromPlace || !toPlace) {
        continue;
      }

      const from: [number, number] = [fromPlace.latitude, fromPlace.longitude];
      const to: [number, number] = [toPlace.latitude, toPlace.longitude];
      const line = leaflet.polyline([from, to], {
        pane: 'place-relationships',
        color: selectedRoute?.color ?? '#314151',
        dashArray:
          relationship.directionality === 'undirected' ? '7 6' : undefined,
        opacity: 0.88,
        weight: relationship.directionality === 'reciprocal' ? 5 : 3
      });
      line.bindTooltip(relationship.context_label, {
        className: 'event-tooltip',
        direction: 'top'
      });
      line.addTo(relationshipLayer);

      const midpoint: [number, number] = [
        (from[0] + to[0]) / 2,
        (from[1] + to[1]) / 2
      ];
      const symbol =
        relationship.directionality === 'forward'
          ? '→'
          : relationship.directionality === 'reciprocal'
            ? '↔'
            : '—';
      leaflet
        .marker(midpoint, {
          interactive: false,
          keyboard: false,
          pane: 'place-relationships',
          icon: leaflet.divIcon({
            className: 'relationship-direction',
            html: `<span aria-hidden="true">${symbol}</span>`,
            iconAnchor: [13, 13],
            iconSize: [26, 26]
          })
        })
        .addTo(relationshipLayer);

      for (const place of [fromPlace, toPlace]) {
        const endpoint = leaflet.circleMarker(
          [place.latitude, place.longitude],
          {
            pane: 'place-relationships',
            color: '#ffffff',
            fillColor: selectedRoute?.color ?? '#314151',
            fillOpacity: 1,
            opacity: 1,
            radius: 6,
            weight: 2
          }
        );
        endpoint.on('click', () => onSelectLocation(event.id, place.id));
        endpoint.addTo(relationshipLayer);
      }
    }
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
          · {selectedPlaceEventCount}
          {selectedPlaceEventCount === 1 ? 'route event' : 'route events'}
        {/if}
      </p>
    </aside>
  {/if}

  {#if placeChoice}
    <aside
      class="place-choice"
      aria-label={`Choose an event at ${placeChoice.place.name}`}
    >
      <div>
        <span>Events at</span>
        <strong>{placeChoice.place.name}</strong>
      </div>
      <button
        type="button"
        class="choice-close"
        aria-label="Close event chooser"
        on:click={() => (placeChoice = null)}
      >
        ×
      </button>
      <ul>
        {#each placeChoice.events as choiceEvent (choiceEvent.id)}
          <li>
            <button
              type="button"
              on:click={() => {
                onSelectLocation(choiceEvent.id, placeChoice?.place.id ?? '');
                placeChoice = null;
              }}
            >
              <strong>{choiceEvent.title}</strong>
              <span>
                {choiceEvent.year_start === choiceEvent.year_end
                  ? choiceEvent.year_start
                  : `${choiceEvent.year_start}–${choiceEvent.year_end}`}
              </span>
            </button>
          </li>
        {/each}
      </ul>
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

  :global(.place-geometry-label.focused span) {
    outline: 3px double #101820;
    outline-offset: 2px;
  }

  :global(.relationship-direction) {
    display: grid;
    place-items: center;
    border: 2px solid #ffffff;
    border-radius: 999px;
    background: #17202a;
    color: #ffffff;
    font-size: 1rem;
    font-weight: 900;
    box-shadow: 0 3px 8px rgba(23, 32, 42, 0.24);
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
    box-shadow: 0 6px 12px rgba(23, 32, 42, 0.16);
    transition:
      transform 140ms ease,
      box-shadow 140ms ease,
      border-width 140ms ease;
  }

  :global(.event-avatar-marker.selected .event-avatar) {
    transform: scale(1.06);
    border-width: 2px;
    box-shadow:
      0 0 0 2px rgba(255, 255, 255, 0.86),
      0 8px 16px rgba(23, 32, 42, 0.2);
  }

  :global(.event-avatar-marker.focused .event-avatar) {
    outline: 3px double #101820;
    outline-offset: 2px;
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
    left: 0.85rem;
    bottom: 0.85rem;
    display: grid;
    gap: 0.12rem;
    width: min(18rem, calc(100% - 2rem));
    padding: 0.48rem 0.6rem;
    border: 1px solid rgba(23, 32, 42, 0.14);
    border-left: 0.25rem solid var(--route-color);
    border-radius: 8px;
    background: rgba(255, 255, 255, 0.9);
    box-shadow: 0 8px 20px rgba(23, 32, 42, 0.14);
    backdrop-filter: blur(3px);
  }

  .place-choice {
    position: absolute;
    z-index: 510;
    top: 0.85rem;
    left: 0.85rem;
    display: grid;
    grid-template-columns: minmax(0, 1fr) auto;
    gap: 0.55rem;
    width: min(22rem, calc(100% - 2rem));
    max-height: min(24rem, calc(100% - 2rem));
    padding: 0.7rem;
    overflow: auto;
    border: 1px solid #cfd7df;
    border-radius: 8px;
    background: rgba(255, 255, 255, 0.96);
    box-shadow: 0 12px 28px rgba(23, 32, 42, 0.18);
  }

  .place-choice > div {
    display: grid;
    gap: 0.08rem;
  }

  .place-choice > div span {
    color: #6b7785;
    font-size: 0.68rem;
    font-weight: 800;
    letter-spacing: 0.06em;
    text-transform: uppercase;
  }

  .choice-close {
    width: 2rem;
    height: 2rem;
    border: 1px solid #d9e0e7;
    border-radius: 6px;
    background: #f7f9fb;
    color: #314151;
    font: inherit;
    font-size: 1.2rem;
  }

  .place-choice ul {
    grid-column: 1 / -1;
    display: grid;
    gap: 0.35rem;
    margin: 0;
    padding: 0;
    list-style: none;
  }

  .place-choice li > button {
    display: flex;
    justify-content: space-between;
    gap: 0.7rem;
    width: 100%;
    min-height: 2.75rem;
    padding: 0.55rem 0.65rem;
    border: 1px solid #d9e0e7;
    border-radius: 7px;
    background: #ffffff;
    color: #17202a;
    font: inherit;
    text-align: left;
  }

  .place-choice li > button span {
    color: #6b7785;
    font-size: 0.74rem;
    white-space: nowrap;
  }

  .selected-place span {
    color: #6b7785;
    font-size: 0.66rem;
    font-weight: 800;
    letter-spacing: 0.06em;
    text-transform: uppercase;
  }

  .selected-place strong {
    color: #17202a;
    font-size: 0.88rem;
    line-height: 1.2;
  }

  .selected-place p {
    margin: 0;
    color: #536170;
    font-size: 0.72rem;
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
      left: 0.75rem;
      bottom: 0.75rem;
      width: min(16.5rem, calc(100% - 4.75rem));
      padding: 0.44rem 0.55rem;
    }
  }
</style>
