export type ReviewStatus = 'draft' | 'reviewed';
export type MediaProvider = 'youtube' | 'spotify' | 'qobuz';
export type MediaType = 'track' | 'album' | 'playlist' | 'video' | 'search';
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
  | 'open_license'
  | 'public_domain'
  | 'provider_restricted'
  | 'unknown';

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
  review_status: ReviewStatus;
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
  review_status: ReviewStatus;
  source_urls: string[];
};

export type MediaLink = {
  provider: MediaProvider;
  type: MediaType;
  title: string;
  url: string;
  query: string;
  confidence: number;
  review_status: ReviewStatus;
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
  review_status: ReviewStatus;
};

export type Event = {
  id: string;
  route_id: string;
  place_id: string;
  title: string;
  year_start: number;
  year_end: number;
  summary: string;
  significance: string;
  tags: string[];
  review_status: ReviewStatus;
  source_urls: string[];
  media_links: MediaLink[];
  image_links: ImageLink[];
};

export type Connection = {
  id: string;
  from_event_id: string;
  to_event_id: string;
  type: string;
  summary: string;
  review_status: ReviewStatus;
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
