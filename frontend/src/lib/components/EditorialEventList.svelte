<script lang="ts">
  import type { RouteReviewProposal } from '$lib/types/soundatlas';

  export let proposals: RouteReviewProposal[] = [];
  export let onSelect: (proposal: RouteReviewProposal) => void = () => {};

  function countLabel(count: number, singular: string, plural: string): string {
    return `${count} ${count === 1 ? singular : plural}`;
  }
</script>

<div class="grid" aria-label="Editorial route candidates">
  {#each proposals as proposal (proposal.candidate_id)}
    <button
      type="button"
      class="group grid min-w-0 gap-[0.3rem] border-0 border-b border-[#d9e0e7] bg-transparent px-[0.1rem] py-[0.55rem] text-left text-[#314151]"
      on:click={() => onSelect(proposal)}
    >
      <span class="flex items-baseline justify-between gap-2">
        <strong class="group-hover:text-[#bb3f22]"
          >{String(
            proposal.event?.title ??
              proposal.proposal.working_title ??
              proposal.proposal.title ??
              proposal.candidate_id
          )}</strong
        >
        <span
          class="shrink-0 capitalize text-[0.72rem] font-bold text-[#536170]"
          >{proposal.editorial_state.replace('_', ' ')}</span
        >
      </span>
      {#if proposal.warnings.length > 0 || proposal.technical_errors.length > 0}
        <span
          class="flex flex-wrap gap-[0.3rem]"
          aria-label="Event finding counts"
        >
          {#if proposal.warnings.length > 0}
            <span
              class="rounded-full border border-current bg-[#fffaf0] px-[0.38rem] py-[0.16rem] text-[0.66rem] font-extrabold text-[#78510c]"
            >
              {countLabel(proposal.warnings.length, 'warning', 'warnings')}
            </span>
          {/if}
          {#if proposal.technical_errors.length > 0}
            <span
              class="rounded-full border border-current bg-[#fff5f5] px-[0.38rem] py-[0.16rem] text-[0.66rem] font-extrabold text-[#8b2020]"
            >
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
