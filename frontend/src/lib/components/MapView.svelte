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

  $: placeById = new Map(places.map((place) => [place.id, place]));
  $: routeById = new Map(routes.map((route) => [route.id, route]));
  $: if (leaflet && markerLayer) {
    renderMarkers();
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
    renderMarkers();

    return () => {
      map?.remove();
      map = null;
    };
  });

  function renderMarkers(): void {
    if (!leaflet || !markerLayer) {
      return;
    }

    markerLayer.clearLayers();

    for (const event of events) {
      const place = placeById.get(event.place_id);
      const route = routeById.get(event.route_id);

      if (!place || !route) {
        continue;
      }

      const isSelected = selectedEventId === event.id;
      const marker = leaflet
        .circleMarker([place.latitude, place.longitude], {
          radius: isSelected ? 10 : 7,
          color: '#17202a',
          weight: isSelected ? 3 : 1,
          fillColor: route.color,
          fillOpacity: isSelected ? 0.95 : 0.75
        })
        .bindTooltip(`${event.title} (${event.year_start})`, {
          direction: 'top',
          offset: [0, -8]
        });

      marker.on('click', () => onSelectEvent(event.id));
      marker.addTo(markerLayer);
    }
  }
</script>

<div class="map-shell">
  <div bind:this={mapContainer} class="map" aria-label="SoundAtlas Karte"></div>

  {#if events.length === 0}
    <div class="map-empty">Keine Events im aktiven Zeitraum.</div>
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
