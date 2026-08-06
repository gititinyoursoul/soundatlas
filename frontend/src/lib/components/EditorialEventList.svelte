<script lang="ts">
  import type { RouteReviewProposal } from '$lib/types/soundatlas';

  export let proposals: RouteReviewProposal[] = [];
  export let onSelect: (proposal: RouteReviewProposal) => void = () => {};
</script>

<div class="event-list" aria-label="Editorial route candidates">
  {#each proposals as proposal (proposal.candidate_id)}
    <button
      type="button"
      class="event-summary"
      on:click={() => onSelect(proposal)}
    >
      <strong
        >{String(
          proposal.event?.title ??
            proposal.proposal.working_title ??
            proposal.proposal.title ??
            proposal.candidate_id
        )}</strong
      >
      <span class="event-review-state"
        >State: {proposal.editorial_state.replace('_', ' ')}</span
      >
      <span class="finding-counts" aria-label="Event finding counts">
        <span class="finding-count warning-count"
          >Warnings: {proposal.warnings.length}</span
        >
        <span class="finding-count error-count"
          >Blocking errors: {proposal.technical_errors.length}</span
        >
      </span>
    </button>
  {/each}
</div>

<style>
  .event-list {
    display: grid;
    gap: 0.65rem;
  }
  .event-summary {
    display: grid;
    gap: 0.25rem;
    min-width: 0;
    padding: 0.65rem;
    border: 1px solid #d9e0e7;
    border-radius: 8px;
    background: #fff;
    color: #314151;
    font: inherit;
    text-align: left;
  }
  .event-summary:hover strong {
    color: #bb3f22;
  }
  .event-review-state {
    color: #536170;
    font-size: 0.72rem;
    font-weight: 700;
    text-transform: capitalize;
  }
  .finding-counts {
    display: flex;
    flex-wrap: wrap;
    gap: 0.3rem;
  }
  .finding-count {
    padding: 0.16rem 0.38rem;
    border: 1px solid currentColor;
    border-radius: 999px;
    font-size: 0.66rem;
    font-weight: 800;
  }
  .warning-count {
    color: #78510c;
    background: #fffaf0;
  }
  .error-count {
    color: #8b2020;
    background: #fff5f5;
  }
</style>
