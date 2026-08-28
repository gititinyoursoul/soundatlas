export type ContentReviewStatus = 'draft' | 'reviewed';
/** Legacy type name retained for migration consumers; use ContentReviewStatus. */
export type ReviewStatus = ContentReviewStatus;
export type ReviewAction = 'reviewed' | 'reject';
export type ReviewLinkKind = 'media' | 'image';
export type MediaProvider = 'youtube' | 'spotify' | 'qobuz';
export type MediaType = 'track' | 'album' | 'playlist' | 'video' | 'search';
export type MediaPlaybackMode = 'embed' | 'external';
export type ImageProvider =
  | 'wikimedia'
  | 'loc'
  | 'nypl'
  | 'internet_archive'
  | 'cover_art_archive'
  | 'manual';
export type ImageType =
  | 'venue_photo'
  | 'artist_photo'
  | 'album_cover'
  | 'flyer_poster'
  | 'archive_photo'
  | 'map_image'
  | 'press_scan';
export type RightsStatus =
  'open_license' | 'public_domain' | 'provider_restricted' | 'unknown';
export type GeometryPrecision = 'site' | 'interpretive';
export type GeometrySourceType = 'external' | 'curated';
export type PlaceRelationshipDirection =
  'undirected' | 'forward' | 'reciprocal';

export type PolygonGeometry = {
  type: 'Polygon';
  coordinates: [number, number][][];
};

export type MultiPolygonGeometry = {
  type: 'MultiPolygon';
  coordinates: [number, number][][][];
};

export type PlaceGeometry = PolygonGeometry | MultiPolygonGeometry;

export type Route = {
  id: string;
  title: string;
  color: string;
  creator: string;
  year_start: number;
  year_end: number;
  summary: string;
  thesis: string;
  tags: string[];
  content_review_status: ContentReviewStatus;
  source_urls: string[];
};

export type Place = {
  id: string;
  name: string;
  borough: string;
  place_type: string;
  latitude: number;
  longitude: number;
  summary: string;
  content_review_status: ContentReviewStatus;
  source_urls: string[];
  geometry?: PlaceGeometry | null;
  geometry_precision?: GeometryPrecision | null;
  geometry_source_type?: GeometrySourceType | null;
  geometry_source_url?: string | null;
  geometry_source_note?: string | null;
  geometry_license?: string | null;
};

export type MediaLink = {
  provider: MediaProvider;
  type: MediaType;
  title: string;
  url: string;
  query: string;
  confidence: number;
  content_review_status: ContentReviewStatus;
  playback_mode?: MediaPlaybackMode;
  video_id?: string | null;
  channel_title?: string | null;
  description?: string | null;
  published_at?: string | null;
  reason?: string | null;
};

export type ImageLink = {
  provider: ImageProvider;
  type: ImageType;
  title: string;
  image_url: string;
  thumbnail_url?: string | null;
  source_url: string;
  creator?: string | null;
  license?: string | null;
  license_url?: string | null;
  rights_status: RightsStatus;
  alt_text: string;
  query: string;
  confidence: number;
  content_review_status: ContentReviewStatus;
};

export type PlaceRelationship = {
  from_place_id: string;
  to_place_id: string;
  directionality: PlaceRelationshipDirection;
  context_label: string;
  source_urls: string[];
};

export type EventStorySection = {
  heading: string;
  body: string;
};

export type Event = {
  id: string;
  route_id: string;
  place_id: string;
  place_ids: string[];
  default_place_id: string;
  place_relationships: PlaceRelationship[];
  title: string;
  route_entry_role?: RouteEntryRole;
  year_start: number;
  year_end: number;
  summary: string | null;
  significance: string | null;
  story_sections: EventStorySection[];
  tags: string[];
  content_review_status: ContentReviewStatus;
  source_urls: string[];
  media_links: MediaLink[];
  image_links: ImageLink[];
};

export type EventInput = Omit<
  Event,
  | 'place_ids'
  | 'default_place_id'
  | 'place_relationships'
  | 'summary'
  | 'significance'
  | 'story_sections'
> &
  Partial<
    Pick<
      Event,
      | 'place_ids'
      | 'default_place_id'
      | 'place_relationships'
      | 'summary'
      | 'significance'
      | 'story_sections'
    >
  >;

export type Connection = {
  id: string;
  from_event_id: string;
  to_event_id: string;
  type: string;
  summary: string;
  review_status: ReviewStatus;
};

export type StoryConnectionItem = {
  id: string;
  summary: string;
  type: string;
  directionLabel: string;
  event: Event;
  place: Place | null;
  route: Route | null;
};

export type TimelineRange = {
  fromYear: number;
  toYear: number;
};

export type SoundAtlasData = {
  routes: Route[];
  places: Place[];
  events: Event[];
  connections: Connection[];
};

export type RouteNavigationEntry = {
  route: Route;
  review_revision_id: string | null;
  published_revision_id: string | null;
  appears_in_published_routes: boolean;
  appears_in_routes_to_review: boolean;
};

export type RouteNavigationSummary = { routes: RouteNavigationEntry[] };

export type ReviewQueueItem = {
  id: string;
  kind: ReviewLinkKind;
  eventId: string;
  eventTitle: string;
  routeId: string;
  title: string;
  provider: MediaProvider | ImageProvider;
  type: MediaType | ImageType;
  url: string;
  previewUrl?: string | null;
};

export type EditorialState = 'draft' | 'approved' | 'dont_use';
export type RouteEntryRole = 'active' | 'context' | 'exclude';

export type RouteReviewProposal = {
  candidate_id: string;
  editorial_state: EditorialState;
  active: boolean;
  included: boolean;
  renderable: boolean;
  agent_recommendation: string | null;
  route_entry_role?: RouteEntryRole;
  next_evidence_task?: Record<string, unknown> | null;
  warnings: string[];
  technical_errors: string[];
  material_signature: string;
  proposal: Record<string, unknown>;
  event: Event | null;
};

export type RouteReviewPlace = {
  decision: 'reuse' | 'new' | 'update';
  place: Place;
  canonical_place?: Place | null;
  canonical_spatial_signature?: string | null;
  proposed_spatial_signature?: string | null;
  spatial_update_approved: boolean;
  warnings: string[];
};

export type FindingOwner =
  | 'candidate_composition'
  | 'active_event'
  | 'active_route'
  | 'source_media'
  | 'technical';

export type RouteReviewFinding = {
  owner: FindingOwner;
  message: string;
  candidate_id?: string | null;
  blocking: boolean;
};

export type CompositionOutcome =
  'active' | 'omitted' | 'merged_into' | 'split_into' | 'added';

export type RouteReviewCandidateAccount = {
  candidate_id: string;
  outcome: CompositionOutcome;
  reason: string;
  related_candidate_ids: string[];
  active: boolean;
  preview: Record<string, unknown>;
  context: Record<string, unknown>;
  findings: RouteReviewFinding[];
};

export type RouteEditorialReview = {
  route_id: string;
  revision_id: string;
  source: string;
  proposals: RouteReviewProposal[];
  dormant_proposals: RouteReviewProposal[];
  places: RouteReviewPlace[];
  connections: Connection[];
  candidate_accounts: RouteReviewCandidateAccount[];
  phase_coverage: Record<string, unknown>[];
  findings: RouteReviewFinding[];
  warnings: string[];
  technical_errors: string[];
  technical_ready: boolean;
};

export type PublicationEventSummary = {
  candidate_id: string;
  title: string;
  editorial_state: EditorialState;
  included: boolean;
};

export type RoutePublicationSummary = {
  route_id: string;
  revision_id: string;
  source: string;
  included_events: PublicationEventSummary[];
  excluded_event_ids: string[];
  warnings: string[];
  technical_errors: string[];
  route_warnings: string[];
  route_technical_errors: string[];
  included_event_warning_count: number;
  included_event_technical_error_count: number;
  technical_ready: boolean;
  published_revision_id: string | null;
};

export type RoutePublicationResult = RoutePublicationSummary & {
  published: boolean;
};
