export type ReviewStatus = 'draft' | 'reviewed';
export type MediaProvider = 'youtube' | 'spotify' | 'qobuz';
export type MediaType = 'track' | 'album' | 'playlist' | 'video' | 'search';

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
