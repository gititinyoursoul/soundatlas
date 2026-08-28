<script lang="ts">
  import { onMount, tick } from 'svelte';
  import {
    IS_EDITORIAL_MODE,
    IS_PUBLIC_STATIC_MODE,
    loadRoutePublication,
    loadRouteNavigation,
    loadRouteReview,
    loadSoundAtlasData,
    publishRoute,
    reviewEventLink,
    updateRouteReviewState
  } from '$lib/api/soundatlas';
  import Icon from '$lib/components/Icon.svelte';
  import MapView from '$lib/components/MapView.svelte';
  import NavigationDrawer from '$lib/components/NavigationDrawer.svelte';
  import InactiveCandidatePanel from '$lib/components/InactiveCandidatePanel.svelte';
  import StoryPanel from '$lib/components/StoryPanel.svelte';
  import Timeline from '$lib/components/Timeline.svelte';
  import { filterEvents } from '$lib/data/filters';
  import {
    projectRouteReview,
    projectConsideredCandidates,
    type ConsideredCandidateProjection,
    type EditorialProjection
  } from '$lib/data/editorial-review';
  import {
    compareEvents,
    getFirstEventIdForRoute,
    getInitialRouteId
  } from '$lib/data/selection';
  import {
    getEventPlaces,
    getEventsForPlace,
    resolveFocusedPlaceId
  } from '$lib/data/spatial';
  import type {
    Connection,
    EditorialState,
    Event,
    Place,
    ReviewAction,
    ReviewQueueItem,
    RouteReviewProposal,
    RouteEditorialReview,
    RoutePublicationResult,
    RoutePublicationSummary,
    RouteNavigationSummary,
    RouteSelectionContext,
    Route,
    StoryConnectionItem
  } from '$lib/types/soundatlas';

  let routes: Route[] = [];
  let routeNavigation: RouteNavigationSummary | null = null;
  let places: Place[] = [];
  let events: Event[] = [];
  const activeConnections: Connection[] = [];
  let selectedRouteId: string | null = null;
  let selectedRouteContext: RouteSelectionContext = 'reader';
  let selectedEventId: string | null = null;
  let selectedPlaceId: string | null = null;
  let isLoading = true;
  let errorMessage: string | null = null;
  let isNavigationOpen = false;
  let navigationVariant: 'expanded' | 'collapsed' = 'expanded';
  let activeNavigationItemId = 'routes';
  let navigationTriggerElement: HTMLButtonElement;
  let headerRegionElement: HTMLElement;
  let storyRegionElement: HTMLElement;
  let reviewSavingItemId: string | null = null;
  const dataSourceLabel = IS_PUBLIC_STATIC_MODE ? 'static data' : 'API data';
  let reviewErrorMessage: string | null = null;
  let selectedInspectorTab: 'story' | 'media' | 'related' = 'story';
  let selectedPreviewUrl: string | null = null;
  let routeReview: RouteEditorialReview | null = null;
  let editorialProjections: EditorialProjection[] = [];
  let consideredCandidateProjections: ConsideredCandidateProjection[] = [];
  let selectedConsideredCandidateId: string | null = null;
  let editorialErrorMessage: string | null = null;
  let editorialSavingCandidateId: string | null = null;
  let editorialActionError: string | null = null;
  let publicationSummary: RoutePublicationSummary | null = null;
  let publicationSaving = false;
  let publicationError: string | null = null;
  let publicationSuccess = false;

  $: publicRouteEvents = [...filterEvents(events, selectedRouteId)].sort(
    compareEvents
  );
  $: editorialEvents = editorialProjections.flatMap((item) =>
    item.event ? [item.event] : []
  );
  $: activePlaces =
    IS_EDITORIAL_MODE && routeReview && selectedRouteContext === 'review'
      ? routeReview.places.map((item) => item.place)
      : places;
  $: routeEvents =
    IS_EDITORIAL_MODE && routeReview && selectedRouteContext === 'review'
      ? editorialProjections
          .filter((item) => item.renderOnTimeline && item.event)
          .flatMap((item) =>
            item.event
              ? [{ ...item.event, route_entry_role: item.routeEntryRole }]
              : []
          )
      : publicRouteEvents;
  $: mapEvents =
    IS_EDITORIAL_MODE && routeReview && selectedRouteContext === 'review'
      ? editorialProjections
          .filter((item) => item.renderOnMap && item.event)
          .flatMap((item) =>
            item.event
              ? [{ ...item.event, route_entry_role: item.routeEntryRole }]
              : []
          )
      : publicRouteEvents;
  $: reviewProposals = routeReview?.proposals ?? [];
  $: selectedConsideredCandidate =
    consideredCandidateProjections.find(
      (candidate) =>
        candidate.account.candidate_id === selectedConsideredCandidateId
    ) ?? null;
  $: selectedProjection =
    editorialProjections.find(
      (item) => item.proposal.candidate_id === selectedEventId
    ) ?? null;
  $: routeEventCounts = routes.reduce<Record<string, number>>(
    (counts, route) => {
      counts[route.id] = events.filter(
        (event) => event.route_id === route.id
      ).length;
      return counts;
    },
    {}
  );
  $: readerRoutes =
    routeNavigation?.routes
      .filter((entry) => entry.appears_in_routes)
      .map((entry) => entry.route) ?? [];
  $: reviewRoutes =
    routeNavigation?.routes
      .filter((entry) => entry.appears_in_routes_to_review)
      .map((entry) => entry.route) ?? [];
  $: isReviewSelection =
    IS_EDITORIAL_MODE && selectedRouteContext === 'review';
  $: reviewQueueItems = IS_PUBLIC_STATIC_MODE
    ? []
    : events.flatMap((event) => [
        ...event.media_links
          .filter((mediaLink) => mediaLink.content_review_status === 'draft')
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
          .filter((imageLink) => imageLink.content_review_status === 'draft')
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
  $: selectedEventIsVisible = isReviewSelection
    ? reviewProposals.some(
        (proposal) => proposal.candidate_id === selectedEventId
      )
    : routeEvents.some((event) => event.id === selectedEventId);
  $: activeSelectedEventId =
    selectedEventIsVisible || routeEvents.length === 0
      ? selectedEventId
      : routeEvents[0].id;
  $: selectedEvent =
    IS_EDITORIAL_MODE && routeReview && selectedRouteContext === 'review'
      ? (selectedProjection?.event ?? null)
      : (routeEvents.find((event) => event.id === activeSelectedEventId) ??
        null);
  $: selectedReviewProposal = selectedProjection?.proposal ?? null;
  $: editorialContentError =
    selectedReviewProposal &&
    (!selectedReviewProposal.event || !selectedReviewProposal.renderable)
      ? selectedReviewProposal.technical_errors.join(' ') ||
        'The generated event is missing required reader-facing story content.'
      : null;
  $: activeSelectedPlaceId = resolveFocusedPlaceId(
    selectedEvent,
    selectedPlaceId
  );
  $: consideredCandidatePlaceId = selectedConsideredCandidate
    ? resolveCandidatePlaceId(selectedConsideredCandidate, activePlaces)
    : null;
  $: consideredCandidateRange = selectedConsideredCandidate
    ? resolveCandidateRange(selectedConsideredCandidate)
    : null;
  $: selectedEventIndex = selectedEvent
    ? routeEvents.findIndex((event) => event.id === selectedEvent.id)
    : -1;
  $: previousEvent =
    selectedEventIndex > 0 ? routeEvents[selectedEventIndex - 1] : null;
  $: nextEvent =
    selectedEventIndex >= 0 && selectedEventIndex < routeEvents.length - 1
      ? routeEvents[selectedEventIndex + 1]
      : null;
  $: selectedEventPlaces = getEventPlaces(selectedEvent, activePlaces);
  $: selectedPlace =
    selectedEventPlaces.find((place) => place.id === activeSelectedPlaceId) ??
    null;
  $: selectedPlaceEventCount = selectedPlace
    ? getEventsForPlace(routeEvents, selectedPlace.id).length
    : 0;
  $: activeRoute = routes.find((route) => route.id === selectedRouteId) ?? null;
  $: selectedRoute = activeRoute;
  $: timelineRoute = selectedRoute ?? activeRoute ?? routes[0] ?? null;
  $: timelineStartYear = timelineRoute?.year_start ?? 1965;
  $: timelineEndYear = timelineRoute?.year_end ?? 1985;
  $: headerRouteTitle = activeRoute?.title ?? 'Loading route context';
  $: headerRouteYears = activeRoute
    ? `${activeRoute.year_start}-${activeRoute.year_end}`
    : '';
  $: headerRouteSummary =
    activeRoute?.thesis ||
    activeRoute?.summary ||
    'Fetching the curated route, event sequence, and map places.';
  $: statusLabel = isLoading
    ? `Loading ${dataSourceLabel}`
    : errorMessage
      ? `${IS_PUBLIC_STATIC_MODE ? 'Static data' : 'API'} unavailable`
      : `${routeEvents.length} events visible`;
  $: selectedConnections = selectedEvent
    ? buildStoryConnectionItems(
        selectedEvent,
        activeConnections,
        isReviewSelection ? editorialEvents : events,
        activePlaces,
        routes
      )
    : [];

  onMount(async () => {
    try {
      const [data, navigation] = await Promise.all([
        loadSoundAtlasData(),
        loadRouteNavigation()
      ]);
      routes = data.routes;
      routeNavigation = navigation;
      places = data.places;
      events = data.events;
      const selectableRoutes = navigation.routes
        .filter((entry) => entry.appears_in_routes)
        .map((entry) => entry.route);
      const initialRouteId =
        selectedRouteId ?? getInitialRouteId(selectableRoutes);
      selectedRouteId = initialRouteId;
      selectedRouteContext = 'reader';

      if (
        !selectedEventId ||
        !data.events.some(
          (event) =>
            event.id === selectedEventId && event.route_id === initialRouteId
        )
      ) {
        selectedEventId = getFirstEventIdForRoute(data.events, initialRouteId);
      }
      const initialEvent =
        data.events.find((event) => event.id === selectedEventId) ?? null;
      selectedPlaceId = resolveFocusedPlaceId(initialEvent, selectedPlaceId);
    } catch (error) {
      const message =
        error instanceof Error
          ? error.message
          : 'Frontend konnte API-Daten nicht laden.';
      if (IS_EDITORIAL_MODE && routes.length > 0) {
        editorialErrorMessage = `Editorial review unavailable: ${message}`;
      } else {
        errorMessage = message;
      }
    } finally {
      isLoading = false;
    }
  });

  function selectEvent(eventId: string, routeId?: string): void {
    if (routeId) {
      selectedRouteId = routeId;
    }

    const nextEvent = isReviewSelection
      ? (editorialProjections.find((item) => item.event?.id === eventId)
          ?.event ?? null)
      : (events.find((event) => event.id === eventId) ?? null);
    selectedEventId = eventId;
    selectedConsideredCandidateId = null;
    selectedPlaceId = resolveFocusedPlaceId(nextEvent, selectedPlaceId);
    selectedInspectorTab = 'story';
    selectedPreviewUrl = null;
  }

  function selectConsideredCandidate(
    candidate: ConsideredCandidateProjection
  ): void {
    selectedConsideredCandidateId = candidate.account.candidate_id;
    selectedInspectorTab = 'story';
    selectedPreviewUrl = null;
  }

  function resolveCandidatePlaceId(
    candidate: ConsideredCandidateProjection,
    availablePlaces: Place[]
  ): string | null {
    const explicitPlaceId = candidate.account.context.place_id;
    if (
      typeof explicitPlaceId === 'string' &&
      availablePlaces.some((place) => place.id === explicitPlaceId)
    ) {
      return explicitPlaceId;
    }
    const placeName = candidate.place?.trim().toLocaleLowerCase();
    return (
      availablePlaces.find(
        (place) => place.name.trim().toLocaleLowerCase() === placeName
      )?.id ?? null
    );
  }

  function resolveCandidateRange(
    candidate: ConsideredCandidateProjection
  ): { start: number; end: number } | null {
    const context = candidate.account.context;
    const start = numericYear(context.year_start);
    const end = numericYear(context.year_end);
    if (start !== null) return { start, end: end ?? start };

    const years = candidate.years?.match(/\d{4}/g)?.map(Number) ?? [];
    return years.length > 0
      ? { start: years[0], end: years[1] ?? years[0] }
      : null;
  }

  function numericYear(value: unknown): number | null {
    return typeof value === 'number' && Number.isInteger(value) ? value : null;
  }

  function selectLocation(eventId: string, placeId: string): void {
    const event = isReviewSelection
      ? editorialProjections.find((item) => item.event?.id === eventId)?.event
      : events.find((item) => item.id === eventId);
    if (!event || !event.place_ids.includes(placeId)) {
      return;
    }

    selectedRouteId = event.route_id;
    selectedEventId = event.id;
    selectedConsideredCandidateId = null;
    selectedPlaceId = placeId;
    selectedInspectorTab = 'story';
    selectedPreviewUrl = null;
  }

  function focusSelectedEventPlace(placeId: string): void {
    if (selectedEvent) {
      selectLocation(selectedEvent.id, placeId);
    }
  }

  function selectRoute(
    routeId: string,
    context: RouteSelectionContext = 'reader'
  ): void {
    selectedRouteId = routeId;
    selectedRouteContext = context;
    selectedEventId = getFirstEventIdForRoute(events, routeId);
    const firstEvent =
      events.find((event) => event.id === selectedEventId) ?? null;
    selectedPlaceId = resolveFocusedPlaceId(firstEvent, null);
    activeNavigationItemId = 'routes';
    selectedInspectorTab = 'story';
    selectedPreviewUrl = null;
    if (IS_EDITORIAL_MODE && context === 'review') {
      routeReview = null;
      editorialProjections = [];
      consideredCandidateProjections = [];
      selectedConsideredCandidateId = null;
      editorialErrorMessage = null;
      publicationSummary = null;
      publicationError = null;
      publicationSuccess = false;
      void loadEditorialRoute(routeId);
    } else if (IS_EDITORIAL_MODE) {
      routeReview = null;
      editorialProjections = [];
      consideredCandidateProjections = [];
      selectedConsideredCandidateId = null;
      editorialErrorMessage = null;
      publicationSummary = null;
      publicationError = null;
      publicationSuccess = false;
    }
  }

  async function loadEditorialRoute(routeId: string): Promise<void> {
    try {
      const review = await loadRouteReview(routeId);
      if (selectedRouteId !== routeId || selectedRouteContext !== 'review')
        return;
      routeReview = review;
      publicationSummary = await loadRoutePublication(routeId);
      if (selectedRouteId !== routeId || selectedRouteContext !== 'review')
        return;
      editorialProjections = projectRouteReview(review);
      consideredCandidateProjections = projectConsideredCandidates(review);
      selectedEventId = review.proposals[0]?.candidate_id ?? null;
    } catch (error) {
      if (selectedRouteId !== routeId || selectedRouteContext !== 'review')
        return;
      routeReview = null;
      publicationSummary = null;
      editorialProjections = [];
      consideredCandidateProjections = [];
      if (isLegacyRoute(routeId)) {
        selectedEventId = getFirstEventIdForRoute(events, routeId);
        editorialErrorMessage = null;
        return;
      }
      editorialErrorMessage =
        error instanceof Error
          ? `Editorial review unavailable: ${error.message}`
          : 'Editorial review unavailable.';
    }
  }

  function isLegacyRoute(routeId: string): boolean {
    const entry = routeNavigation?.routes.find(
      (candidate) => candidate.route.id === routeId
    );
    return (
      entry?.appears_in_routes === true &&
      entry.appears_in_published_routes === false &&
      entry.appears_in_routes_to_review === false
    );
  }

  async function setEditorialState(
    proposal: RouteReviewProposal,
    editorialState: EditorialState
  ): Promise<void> {
    if (!routeReview || !selectedRouteId) return;
    editorialSavingCandidateId = proposal.candidate_id;
    editorialActionError = null;
    try {
      const updated = await updateRouteReviewState(
        selectedRouteId,
        proposal.candidate_id,
        routeReview.revision_id,
        editorialState
      );
      routeReview = updated;
      editorialProjections = projectRouteReview(updated);
      consideredCandidateProjections = projectConsideredCandidates(updated);
      publicationSummary = await loadRoutePublication(selectedRouteId);
    } catch (error) {
      editorialActionError =
        error instanceof Error
          ? error.message
          : 'Editorial state update failed.';
    } finally {
      editorialSavingCandidateId = null;
    }
  }

  async function publishSelectedRoute(): Promise<void> {
    if (!publicationSummary || !selectedRouteId || !routeReview) return;
    publicationSaving = true;
    publicationError = null;
    publicationSuccess = false;
    try {
      const result: RoutePublicationResult = await publishRoute(
        selectedRouteId,
        routeReview.revision_id
      );
      publicationSummary = result;
      publicationSuccess = result.published;
    } catch (error) {
      publicationError =
        error instanceof Error ? error.message : 'Publication failed.';
    } finally {
      publicationSaving = false;
    }
  }

  function buildStoryConnectionItems(
    baseEvent: Event,
    allConnections: Connection[],
    allEvents: Event[],
    allPlaces: Place[],
    allRoutes: Route[]
  ): StoryConnectionItem[] {
    return allConnections.flatMap<StoryConnectionItem>((connection) => {
      if (
        connection.from_event_id !== baseEvent.id &&
        connection.to_event_id !== baseEvent.id
      ) {
        return [];
      }

      const connectedEventId =
        connection.from_event_id === baseEvent.id
          ? connection.to_event_id
          : connection.from_event_id;
      const connectedEvent = allEvents.find(
        (event) => event.id === connectedEventId
      );

      if (!connectedEvent) {
        return [];
      }

      return [
        {
          id: connection.id,
          summary: connection.summary,
          type: connection.type,
          directionLabel:
            connection.from_event_id === baseEvent.id
              ? 'Leads to'
              : 'Linked from',
          event: connectedEvent,
          place:
            allPlaces.find(
              (place) => place.id === connectedEvent.default_place_id
            ) ?? null,
          route:
            allRoutes.find((route) => route.id === connectedEvent.route_id) ??
            null
        }
      ];
    });
  }

  function selectReviewItem(item: ReviewQueueItem): void {
    selectedRouteId = item.routeId;
    selectedRouteContext = 'reader';
    selectedEventId = item.eventId;
    selectedPlaceId = resolveFocusedPlaceId(
      events.find((event) => event.id === item.eventId) ?? null,
      selectedPlaceId
    );
    selectedInspectorTab = 'media';
    selectedPreviewUrl = item.url;
    activeNavigationItemId = 'media-review';
  }

  async function reviewQueueItem(
    item: ReviewQueueItem,
    action: ReviewAction
  ): Promise<void> {
    if (IS_PUBLIC_STATIC_MODE) {
      return;
    }

    reviewSavingItemId = item.id;
    reviewErrorMessage = null;
    selectedRouteId = item.routeId;
    selectedEventId = item.eventId;
    selectedPlaceId = resolveFocusedPlaceId(
      events.find((event) => event.id === item.eventId) ?? null,
      selectedPlaceId
    );
    selectedInspectorTab = 'media';
    selectedPreviewUrl = item.url;
    activeNavigationItemId = 'media-review';

    try {
      const updatedEvent = await reviewEventLink(
        item.eventId,
        item.kind,
        item.url,
        action
      );
      events = events.map((event) =>
        event.id === updatedEvent.id ? updatedEvent : event
      );
    } catch (error) {
      reviewErrorMessage =
        error instanceof Error ? error.message : 'Review action failed.';
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
    navigationVariant =
      navigationVariant === 'expanded' ? 'collapsed' : 'expanded';
  }

  async function selectNavigationItem(itemId: string): Promise<void> {
    activeNavigationItemId = itemId;

    if (itemId === 'routes' || itemId === 'editorial-review') {
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
    if (
      itemId === 'events' ||
      itemId === 'connections' ||
      itemId === 'sources'
    ) {
      return storyRegionElement;
    }

    return headerRegionElement;
  }

  function markStoryNavigationActive(): void {
    if (
      !['media-review', 'editorial-review'].includes(activeNavigationItemId)
    ) {
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
      const eventToSelect =
        nextEvent ?? (!selectedEvent ? routeEvents[0] : null);

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
    routes={readerRoutes}
    {reviewRoutes}
    {selectedRouteId}
    {selectedRouteContext}
    {routeEventCounts}
    {reviewQueueItems}
    {reviewSavingItemId}
    {reviewErrorMessage}
    showAdminReview={!IS_PUBLIC_STATIC_MODE}
    showEditorialReview={IS_EDITORIAL_MODE}
    enableEditorialActions={IS_EDITORIAL_MODE &&
      selectedRouteContext === 'review'}
    editorialProposalCount={reviewProposals.length}
    editorialProposals={reviewProposals}
    editorialConsideredCandidates={consideredCandidateProjections}
    {editorialErrorMessage}
    {publicationSummary}
    {publicationSaving}
    {publicationError}
    {publicationSuccess}
    {isLoading}
    {errorMessage}
    onClose={closeNavigation}
    onToggleVariant={toggleNavigationVariant}
    onSelectItem={selectNavigationItem}
    onSelectRoute={selectRoute}
    onSelectReviewItem={selectReviewItem}
    onSelectEditorialProposal={(proposal) => selectEvent(proposal.candidate_id)}
    onSelectConsideredCandidate={selectConsideredCandidate}
    onPublishRoute={publishSelectedRoute}
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

        <div
          class="route-context"
          style={`--route-color: ${activeRoute?.color ?? '#314151'}`}
          aria-label="Selected route context"
        >
          <span class="route-accent" aria-hidden="true"></span>
          <div class="route-heading">
            <h2>{headerRouteTitle}</h2>
            {#if headerRouteYears}
              <span>{headerRouteYears}</span>
            {/if}
          </div>
          <p class="route-summary">{headerRouteSummary}</p>
        </div>

        <div class="status">
          {statusLabel}
        </div>
      </header>

      {#if errorMessage}
        <div class="notice error">
          <strong
            >{IS_PUBLIC_STATIC_MODE
              ? 'Static data unavailable'
              : 'Backend unavailable'}</strong
          >
          <span>{errorMessage}</span>
          {#if IS_PUBLIC_STATIC_MODE}
            <small
              >Generate the static seed data, rebuild the frontend, then refresh
              this page.</small
            >
          {:else}
            <small
              >Start the FastAPI backend on http://127.0.0.1:8000, then refresh
              this page.</small
            >
          {/if}
        </div>
      {:else if editorialErrorMessage}
        <div class="notice error">
          <strong>Editorial review unavailable</strong>
          <span>{editorialErrorMessage}</span>
          <small>Public explorer data is not used as a review fallback.</small>
        </div>
      {:else}
        <section class="map-region" tabindex="-1" aria-label="Map exploration">
          <MapView
            events={mapEvents}
            places={activePlaces}
            {routes}
            {selectedRouteId}
            selectedEventId={activeSelectedEventId}
            selectedPlaceId={activeSelectedPlaceId}
            contextPlaceId={consideredCandidatePlaceId}
            {selectedPlace}
            {selectedRoute}
            {selectedPlaceEventCount}
            onSelectLocation={selectLocation}
          />
        </section>
      {/if}

      <section class="timeline-region" tabindex="-1" aria-label="Timeline">
        <Timeline
          routeStartYear={timelineStartYear}
          routeEndYear={timelineEndYear}
          eventStartYear={selectedConsideredCandidate
            ? (consideredCandidateRange?.start ?? null)
            : IS_EDITORIAL_MODE
              ? selectedProjection?.renderOnTimeline
                ? (selectedEvent?.year_start ?? null)
                : null
              : (selectedEvent?.year_start ?? null)}
          eventEndYear={selectedConsideredCandidate
            ? (consideredCandidateRange?.end ?? null)
            : IS_EDITORIAL_MODE
              ? selectedProjection?.renderOnTimeline
                ? (selectedEvent?.year_end ?? null)
                : null
              : (selectedEvent?.year_end ?? null)}
          events={routeEvents}
          selectedEventId={activeSelectedEventId}
          onSelectEvent={selectEvent}
        />
      </section>
    </div>

    <section
      bind:this={storyRegionElement}
      class="story-region"
      tabindex="-1"
      aria-label="Event inspector"
      on:focusin={markStoryNavigationActive}
    >
      {#if selectedConsideredCandidate}
        <InactiveCandidatePanel candidate={selectedConsideredCandidate} />
      {:else}
        <StoryPanel
          event={selectedEvent}
          place={selectedPlace}
          places={selectedEventPlaces}
          selectedPlaceId={activeSelectedPlaceId}
          route={selectedRoute}
          connections={selectedConnections}
          {previousEvent}
          {nextEvent}
          onNavigateEvent={selectEvent}
          onFocusPlace={focusSelectedEventPlace}
          {isLoading}
          {errorMessage}
          initialTab={selectedInspectorTab}
          {selectedPreviewUrl}
          showReviewActions={!IS_PUBLIC_STATIC_MODE}
          editorialMode={IS_EDITORIAL_MODE}
          editorialProposal={selectedReviewProposal}
          editorialRole={selectedReviewProposal?.route_entry_role ?? 'active'}
          editorialSaving={editorialSavingCandidateId ===
            selectedReviewProposal?.candidate_id}
          editorialErrorMessage={editorialActionError}
          {editorialContentError}
          onSetEditorialState={(state) =>
            selectedReviewProposal &&
            setEditorialState(selectedReviewProposal, state)}
        />
      {/if}
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
    grid-template-columns: minmax(0, 0.95fr) minmax(21rem, 27rem);
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
    gap: 0.85rem;
    padding: 0.65rem 0.9rem;
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
    grid-template-columns: 0.28rem minmax(0, 1fr);
    column-gap: 0.55rem;
    row-gap: 0.24rem;
    align-items: start;
    min-width: 0;
  }

  .route-accent {
    grid-row: 1 / span 2;
    width: 100%;
    min-height: 2.2rem;
    border-radius: 999px;
    background: var(--route-color);
  }

  .route-heading {
    grid-column: 2;
    display: flex;
    align-items: baseline;
    gap: 0.55rem;
    min-width: 0;
  }

  .route-heading h2,
  .route-summary {
    margin: 0;
  }

  .route-heading h2 {
    overflow: hidden;
    color: #17202a;
    font-size: 1rem;
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
    grid-column: 2;
    max-width: 68rem;
    color: #314151;
    font-size: 0.8rem;
    line-height: 1.35;
    overflow: hidden;
    display: -webkit-box;
    -webkit-box-orient: vertical;
    -webkit-line-clamp: 1;
    line-clamp: 1;
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

    .route-heading {
      align-items: flex-start;
      flex-direction: column;
      gap: 0.2rem;
    }

    .route-heading h2 {
      white-space: normal;
    }
  }
</style>
