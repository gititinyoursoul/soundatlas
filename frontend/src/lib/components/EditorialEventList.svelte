<script lang="ts">
  import type { RouteReviewProposal } from '$lib/types/soundatlas';

  export let proposals: RouteReviewProposal[] = [];
  export let onSelect: (proposal: RouteReviewProposal) => void = () => {};

  function countLabel(count: number, singular: string, plural: string): string {
    return `${count} ${count === 1 ? singular : plural}`;
  }
</script>

<div class="event-list" aria-label="Editorial route candidates">
  {#each proposals as proposal (proposal.candidate_id)}
    <button
      type="button"
      class="event-summary"
      on:click={() => onSelect(proposal)}
    >
      <span class="event-heading">
        <strong
          >{String(
            proposal.event?.title ??
              proposal.proposal.working_title ??
              proposal.proposal.title ??
              proposal.candidate_id
          )}</strong
        >
        <span class="event-review-state"
          >{proposal.editorial_state.replace('_', ' ')}</span
        >
      </span>
      {#if proposal.warnings.length > 0 || proposal.technical_errors.length > 0}
        <span class="finding-counts" aria-label="Event finding counts">
          {#if proposal.warnings.length > 0}
            <span class="finding-count warning-count">
              {countLabel(proposal.warnings.length, 'warning', 'warnings')}
            </span>
          {/if}
          {#if proposal.technical_errors.length > 0}
            <span class="finding-count error-count">
              {countLabel(
                proposal.technical_errors.length,
                'blocking error',
                'blocking errors'
              )}
            </span>
          {/if}
        </span>
      {/if}
    </button>
  {/each}
</div>

<style>
  .event-list {
    display: grid;
  }
  .event-summary {
    display: grid;
    gap: 0.3rem;
    min-width: 0;
    padding: 0.55rem 0.1rem;
    border: 0;
    border-bottom: 1px solid #d9e0e7;
    background: transparent;
    color: #314151;
    font: inherit;
    text-align: left;
  }
  .event-summary:hover strong {
    color: #bb3f22;
  }
  .event-heading {
    display: flex;
    align-items: baseline;
    justify-content: space-between;
    gap: 0.5rem;
  }
  .event-review-state {
    flex: 0 0 auto;
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
