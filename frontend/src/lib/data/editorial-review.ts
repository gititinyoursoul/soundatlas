import type {
  Event,
  RouteReviewProposal,
  RouteReviewResult
} from '$lib/types/soundatlas';

export type EditorialProjection = {
  proposal: RouteReviewProposal;
  event: Event | null;
  renderOnMap: boolean;
  renderOnTimeline: boolean;
  warnings: string[];
};

export function projectRouteReview(
  review: RouteReviewResult
): EditorialProjection[] {
  return review.proposals
    .filter((proposal) => proposal.active)
    .map(projectProposal);
}

function projectProposal(
  proposal: RouteReviewProposal
): EditorialProjection {
  const warnings = [...proposal.warnings, ...proposal.technical_errors];
  const event = proposal.event;

  return {
    proposal,
    event,
    renderOnMap:
      Boolean(event?.default_place_id) &&
      proposal.renderable &&
      proposal.included,
    renderOnTimeline:
      Boolean(event) && proposal.renderable && proposal.included,
    warnings
  };
}
