import type {
  Event,
  Place,
  RouteReviewProposal,
  RouteReviewResult
} from '$lib/types/soundatlas';

export type EditorialProjection = {
  proposal: RouteReviewProposal;
  event: Event;
  renderOnMap: boolean;
  renderOnTimeline: boolean;
  warnings: string[];
};

export function projectRouteReview(
  review: RouteReviewResult,
  places: Place[],
  routeId = review.route_id
): EditorialProjection[] {
  return review.proposals
    .filter((proposal) => proposal.active)
    .map((proposal) => projectProposal(proposal, places, routeId));
}

function projectProposal(
  proposal: RouteReviewProposal,
  places: Place[],
  routeId: string
): EditorialProjection {
  const value = proposal.proposal;
  const placeValue = typeof value.place === 'string' ? value.place : '';
  const placeId = resolvePlaceId(placeValue, value.place_id, places);
  const years = parseYears(value.years, value.year_start, value.year_end);
  const title =
    stringValue(value.working_title) ||
    stringValue(value.title) ||
    proposal.candidate_id;
  const warnings = [...proposal.warnings, ...proposal.technical_errors];

  const event: Event = {
    id: proposal.candidate_id,
    route_id: stringValue(value.route_id) || routeId,
    place_id: placeId ?? '',
    place_ids: placeId ? [placeId] : [],
    default_place_id: placeId ?? '',
    place_relationships: [],
    title,
    year_start: years?.[0] ?? 0,
    year_end: years?.[1] ?? 0,
    summary: stringValue(value.summary),
    significance: stringValue(value.significance),
    tags: stringList(value.tags),
    review_status: 'draft',
    source_urls: stringList(value.source_urls),
    media_links: [],
    image_links: []
  };

  return {
    proposal,
    event,
    renderOnMap: Boolean(placeId) && proposal.renderable && proposal.included,
    renderOnTimeline:
      Boolean(years) && proposal.renderable && proposal.included,
    warnings
  };
}

function resolvePlaceId(
  label: string,
  candidateId: unknown,
  places: Place[]
): string | null {
  if (
    typeof candidateId === 'string' &&
    places.some((place) => place.id === candidateId)
  ) {
    return candidateId;
  }
  const normalized = normalize(label);
  if (!normalized) return null;
  const matches = places.filter(
    (place) => normalize(place.name) === normalized
  );
  return matches.length === 1 ? matches[0].id : null;
}

function parseYears(
  years: unknown,
  start: unknown,
  end: unknown
): [number, number] | null {
  const values = [start, end].map((value) =>
    typeof value === 'number' ? value : null
  );
  if (values[0] !== null && values[1] !== null) return [values[0], values[1]];
  const matches = typeof years === 'string' ? years.match(/\d{4}/g) : null;
  if (!matches || matches.length === 0) return null;
  const first = Number(matches[0]);
  const second = matches[1] ? Number(matches[1]) : first;
  return [first, second];
}

function normalize(value: string): string {
  return value
    .toLocaleLowerCase()
    .replace(/[^\p{L}\p{N}]+/gu, ' ')
    .trim();
}

function stringValue(value: unknown): string {
  return typeof value === 'string' ? value : '';
}

function stringList(value: unknown): string[] {
  return Array.isArray(value)
    ? value.filter((item): item is string => typeof item === 'string')
    : [];
}
