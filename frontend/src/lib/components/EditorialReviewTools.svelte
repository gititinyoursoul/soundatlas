<script lang="ts">
  import type {
    EditorialState,
    RouteReviewProposal
  } from '$lib/types/soundatlas';

  export let proposal: RouteReviewProposal;
  export let saving = false;
  export let errorMessage: string | null = null;
  export let onSetState: (state: EditorialState) => void = () => {};
</script>

<section class="review-tools" aria-label="Editorial review tools">
  <section class="editorial-review-card" aria-label="Editorial review">
    <div>
      <span class="review-kicker">Editorial review</span>
      <strong>State: {proposal.editorial_state.replace('_', ' ')}</strong>
    </div>
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
    {#if proposal.agent_recommendation}
      <section
        class="finding-group recommendation"
        aria-labelledby="agent-recommendation-heading"
      >
        <h3 id="agent-recommendation-heading">Agent recommendation</h3>
        <p>{proposal.agent_recommendation}</p>
      </section>
    {/if}
    {#if proposal.warnings.length > 0}
      <section
        class="finding-group warnings"
        aria-labelledby="event-warnings-heading"
      >
        <h3 id="event-warnings-heading">
          Editorial warnings ({proposal.warnings.length})
        </h3>
        <ul>
          {#each proposal.warnings as warning (warning)}
            <li><strong>Warning</strong><span>{warning}</span></li>
          {/each}
        </ul>
      </section>
    {/if}
    {#if proposal.technical_errors.length > 0}
      <section
        class="finding-group errors"
        aria-labelledby="event-errors-heading"
      >
        <h3 id="event-errors-heading">
          Technical errors ({proposal.technical_errors.length})
        </h3>
        <ul>
          {#each proposal.technical_errors as error (error)}
            <li><strong>Blocking error</strong><span>{error}</span></li>
          {/each}
        </ul>
      </section>
    {/if}
    {#if errorMessage}<p class="review-error" role="alert">
        {errorMessage}
      </p>{/if}
  </section>
</section>

<style>
  .review-tools {
    display: grid;
    gap: 0.65rem;
    padding: 0.9rem 1rem 1rem;
    border-top: 1px solid #d9e0e7;
    background: #f6f8fa;
  }

  .editorial-review-card {
    display: grid;
    gap: 0.55rem;
    padding: 0.65rem;
    border-radius: 8px;
    font-size: 0.78rem;
  }

  .editorial-review-card {
    border: 1px solid #c9d8f2;
    background: #f3f7ff;
    color: #263b5c;
  }

  .editorial-review-card > div:first-child {
    display: flex;
    justify-content: space-between;
    gap: 0.5rem;
  }

  button:disabled {
    cursor: not-allowed;
    opacity: 0.55;
  }
  p {
    margin: 0;
  }
  .review-kicker {
    color: #2454d6;
    font-weight: 800;
    text-transform: uppercase;
    letter-spacing: 0.05em;
  }
  .editorial-actions {
    display: grid;
    grid-template-columns: repeat(3, minmax(0, 1fr));
    gap: 0.3rem;
  }
  .editorial-actions button {
    padding: 0.35rem 0.25rem;
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
    gap: 0.35rem;
    padding: 0.55rem;
    border: 1px solid #c9d8f2;
    border-radius: 6px;
    background: #fff;
  }
  .finding-group h3,
  .finding-group p,
  .finding-group ul {
    margin: 0;
  }
  .finding-group h3 {
    font-size: 0.74rem;
    text-transform: uppercase;
    letter-spacing: 0.04em;
  }
  .finding-group ul {
    display: grid;
    gap: 0.35rem;
    padding: 0;
    list-style: none;
  }
  .finding-group li {
    display: grid;
    gap: 0.12rem;
    padding: 0.42rem;
    border-left: 0.22rem solid currentColor;
    background: #fff;
  }
  .finding-group li strong {
    font-size: 0.68rem;
    text-transform: uppercase;
    letter-spacing: 0.04em;
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
</style>
