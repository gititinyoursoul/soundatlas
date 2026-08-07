import type {
  Event,
  RouteReviewCandidateAccount,
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

export type InactiveCandidateProjection = {
  account: RouteReviewCandidateAccount;
  title: string;
  summary: string | null;
  significance: string | null;
  years: string | null;
  place: string | null;
};

export function projectRouteReview(
  review: RouteReviewResult
): EditorialProjection[] {
  return review.proposals
    .filter((proposal) => proposal.active)
    .map(projectProposal);
}

export function projectInactiveCandidates(
  review: RouteReviewResult
): InactiveCandidateProjection[] {
  return review.candidate_accounts
    .filter((account) => !account.active)
    .map((account) => ({
      account,
      title:
        stringValue(account.context.working_title) ??
        stringValue(account.context.title) ??
        account.candidate_id,
      summary:
        stringValue(account.preview.summary) ??
        stringValue(account.context.summary),
      significance:
        stringValue(account.preview.significance) ??
        stringValue(account.context.significance),
      years:
        stringValue(account.context.years) ??
        rangeValue(account.context.year_start, account.context.year_end),
      place:
        stringValue(account.context.place) ??
        stringValue(account.context.place_id)
    }));
}

function projectProposal(proposal: RouteReviewProposal): EditorialProjection {
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

function stringValue(value: unknown): string | null {
  return typeof value === 'string' && value.trim() ? value : null;
}

function rangeValue(start: unknown, end: unknown): string | null {
  if (typeof start !== 'number') return null;
  return typeof end === 'number' && end !== start
    ? `${start}-${end}`
    : String(start);
}
