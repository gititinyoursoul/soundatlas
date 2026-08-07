<script lang="ts">
  import type {
    EditorialState,
    RouteReviewProposal
  } from '$lib/types/soundatlas';

  export let proposal: RouteReviewProposal;
  export let saving = false;
  export let errorMessage: string | null = null;
  export let onSetState: (state: EditorialState) => void = () => {};

  function countLabel(count: number, singular: string, plural: string): string {
    return `${count} ${count === 1 ? singular : plural}`;
  }

  function sentenceCase(value: string): string {
    return value.charAt(0).toUpperCase() + value.slice(1);
  }
</script>

<section class="review-tools" aria-labelledby="event-review-heading">
  <div class="review-heading">
    <h3 id="event-review-heading">Event review</h3>
    <div class="editorial-actions" aria-label="Editorial state actions">
      {#each ['draft', 'approved', 'dont_use'] as state (state)}
        <button
          type="button"
          class:active={proposal.editorial_state === state}
          disabled={saving}
          aria-pressed={proposal.editorial_state === state}
          on:click={() => onSetState(state as EditorialState)}
          >{state === 'dont_use'
            ? 'Don’t use'
            : state.charAt(0).toUpperCase() + state.slice(1)}</button
        >
      {/each}
    </div>
  </div>
  {#if proposal.agent_recommendation}
    <p class="recommendation">
      <strong>Suggested:</strong>
      {sentenceCase(proposal.agent_recommendation)}
    </p>
  {/if}
  {#if proposal.route_entry_role === 'context'}
    <p class="recommendation">
      <strong>Placement:</strong> Route context
    </p>
    {#if proposal.next_evidence_task}
      <p class="recommendation">
        <strong>Next evidence:</strong>
        {proposal.next_evidence_task.expected_output ?? 'Evidence task recorded'}
      </p>
    {/if}
  {/if}
  {#if proposal.warnings.length > 0}
    <section
      class="finding-group warnings"
      aria-labelledby="event-warnings-heading"
    >
      <h4 id="event-warnings-heading">
        {countLabel(proposal.warnings.length, 'warning', 'warnings')}
      </h4>
      <ul>
        {#each proposal.warnings as warning (warning)}
          <li>{warning}</li>
        {/each}
      </ul>
    </section>
  {/if}
  {#if proposal.technical_errors.length > 0}
    <section
      class="finding-group errors"
      aria-labelledby="event-errors-heading"
    >
      <h4 id="event-errors-heading">
        {countLabel(
          proposal.technical_errors.length,
          'blocking error',
          'blocking errors'
        )}
      </h4>
      <ul>
        {#each proposal.technical_errors as error (error)}
          <li>{error}</li>
        {/each}
      </ul>
    </section>
  {/if}
  {#if errorMessage}<p class="review-error" role="alert">
      {errorMessage}
    </p>{/if}
</section>

<style>
  .review-tools {
    display: grid;
    gap: 0.55rem;
    padding: 0.7rem 1rem 0.8rem;
    border-top: 1px solid #d9e0e7;
    background: #f6f8fa;
    color: #314151;
    font-size: 0.78rem;
  }
  .review-heading {
    display: grid;
    gap: 0.4rem;
  }
  .review-heading h3 {
    margin: 0;
    font-size: 0.9rem;
  }

  button:disabled {
    cursor: not-allowed;
    opacity: 0.55;
  }
  p {
    margin: 0;
  }
  .editorial-actions {
    display: grid;
    grid-template-columns: repeat(3, minmax(0, 1fr));
    gap: 0.3rem;
  }
  .editorial-actions button {
    padding: 0.3rem 0.25rem;
    border: 1px solid #b8c8e4;
    border-radius: 6px;
    background: #fff;
    color: #263b5c;
    font: inherit;
    font-weight: 700;
  }
  .editorial-actions button.active {
    border-color: #2454d6;
    background: #2454d6;
    color: #fff;
  }
  .finding-group {
    display: grid;
    gap: 0.3rem;
    padding-top: 0.45rem;
    border-top: 1px solid currentColor;
  }
  .finding-group h4,
  .finding-group ul {
    margin: 0;
  }
  .finding-group h4 {
    font-size: 0.74rem;
  }
  .finding-group ul {
    display: grid;
    gap: 0.35rem;
    padding: 0;
    list-style: none;
  }
  .finding-group li {
    padding: 0.3rem 0 0.3rem 0.55rem;
    border-left: 0.18rem solid currentColor;
    line-height: 1.35;
  }
  .finding-group.warnings {
    border-color: #e6d9b5;
    color: #65440b;
  }
  .finding-group.errors {
    border-color: #e8b9b9;
    color: #8b2020;
  }
  .review-error {
    color: #a32626;
    font-weight: 700;
  }
  .recommendation strong {
    color: #2454d6;
  }
</style>
