<script lang="ts">
  import { onMount } from 'svelte';
  import 'leaflet/dist/leaflet.css';
  import type { Event, Place, Route } from '$lib/types/soundatlas';

  export let events: Event[] = [];
  export let places: Place[] = [];
  export let routes: Route[] = [];
  export let selectedEventId: string | null = null;
  export let onSelectEvent: (eventId: string) => void = () => {};

  let mapContainer: HTMLDivElement;
  let map: import('leaflet').Map | null = null;
  let markerLayer: import('leaflet').LayerGroup | null = null;
  let leaflet: typeof import('leaflet') | null = null;

  $: if (leaflet && markerLayer) {
    renderMarkers(selectedEventId, events, places, routes);
  }

  onMount(async () => {
    leaflet = await import('leaflet');

    map = leaflet.map(mapContainer, {
      zoomControl: false,
      attributionControl: true
    });

    map.setView([40.82, -73.93], 12);

    leaflet
      .tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
        maxZoom: 19,
        attribution: '&copy; OpenStreetMap contributors'
      })
      .addTo(map);

    leaflet.control.zoom({ position: 'bottomright' }).addTo(map);
    markerLayer = leaflet.layerGroup().addTo(map);
    renderMarkers(selectedEventId, events, places, routes);

    return () => {
      map?.remove();
      map = null;
    };
  });

  function renderMarkers(
    activeEventId = selectedEventId,
    currentEvents = events,
    currentPlaces = places,
    currentRoutes = routes
  ): void {
    if (!leaflet || !markerLayer) {
      return;
    }

    markerLayer.clearLayers();

    const eventsByPlaceId = groupEventsByPlaceId(currentEvents);
    let selectedMarkerPosition: [number, number] | null = null;

    const currentPlaceById = new Map(currentPlaces.map((place) => [place.id, place]));
    const currentRouteById = new Map(currentRoutes.map((route) => [route.id, route]));

    for (const event of currentEvents) {
      const place = currentPlaceById.get(event.place_id);
      const route = currentRouteById.get(event.route_id);

      if (!place || !route) {
        continue;
      }

      const isSelected = activeEventId === event.id;
      const colocatedEvents = eventsByPlaceId.get(event.place_id) ?? [event];
      const eventIndex = colocatedEvents.findIndex((colocatedEvent) => colocatedEvent.id === event.id);
      const markerPosition = getMarkerPosition(place, eventIndex, colocatedEvents.length);
      const marker = leaflet
        .circleMarker(markerPosition, {
          radius: isSelected ? 13 : 7,
          color: '#17202a',
          weight: isSelected ? 3 : 1,
          fillColor: isSelected ? '#2e7d32' : route.color,
          fillOpacity: isSelected ? 1 : 0.75
        })
        .bindTooltip(`${event.title} (${event.year_start})`, {
          direction: 'top',
          offset: [0, -8]
        });

      marker.on('click', () => onSelectEvent(event.id));
      marker.addTo(markerLayer);

      if (isSelected) {
        marker.bringToFront();
        selectedMarkerPosition = markerPosition;
      }
    }

    if (selectedMarkerPosition && map) {
      map.panTo(selectedMarkerPosition, {
        animate: true,
        duration: 0.35
      });
    }
  }

  function groupEventsByPlaceId(eventsToGroup: Event[]): Map<string, Event[]> {
    const groupedEvents = new Map<string, Event[]>();

    for (const event of eventsToGroup) {
      groupedEvents.set(event.place_id, [...(groupedEvents.get(event.place_id) ?? []), event]);
    }

    return groupedEvents;
  }

  function getMarkerPosition(
    place: Place,
    eventIndex: number,
    colocatedEventCount: number
  ): [number, number] {
    if (colocatedEventCount <= 1 || eventIndex < 0) {
      return [place.latitude, place.longitude];
    }

    const angle = (2 * Math.PI * eventIndex) / colocatedEventCount;
    const radiusInMeters = 70;
    const latitudeOffset = (Math.sin(angle) * radiusInMeters) / 111_320;
    const longitudeOffset =
      (Math.cos(angle) * radiusInMeters) /
      (111_320 * Math.cos((place.latitude * Math.PI) / 180));

    return [place.latitude + latitudeOffset, place.longitude + longitudeOffset];
  }
</script>

<div class="map-shell">
  <div bind:this={mapContainer} class="map" aria-label="SoundAtlas map"></div>

  {#if events.length === 0}
    <div class="map-empty">No events in the active time range.</div>
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
</style>
