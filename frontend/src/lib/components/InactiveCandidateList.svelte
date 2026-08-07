<script lang="ts">
  import type { InactiveCandidateProjection } from '$lib/data/editorial-review';

  export let candidates: InactiveCandidateProjection[] = [];
  export let onSelect: (
    candidate: InactiveCandidateProjection
  ) => void = () => {};
</script>

<div class="grid" aria-label="Inactive route candidates">
  {#each candidates as candidate (candidate.account.candidate_id)}
    <button
      type="button"
      class="grid min-w-0 gap-1 border-0 border-b border-[#d9e0e7] bg-transparent px-0.5 py-2 text-left text-[#314151] hover:text-[#bb3f22] focus-visible:outline focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-[#bb3f22]"
      on:click={() => onSelect(candidate)}
    >
      <span class="flex items-baseline justify-between gap-2">
        <strong>{candidate.title}</strong>
        <span
          class="shrink-0 text-xs font-bold uppercase tracking-wide text-[#536170]"
          >{candidate.account.outcome.replace('_', ' ')}</span
        >
      </span>
      {#if candidate.years || candidate.place}
        <span class="text-xs text-[#536170]">
          {[candidate.years, candidate.place].filter(Boolean).join(' · ')}
        </span>
      {/if}
    </button>
  {/each}
</div>
