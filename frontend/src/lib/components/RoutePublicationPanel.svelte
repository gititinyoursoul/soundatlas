<script lang="ts">
  import type { RoutePublicationSummary } from '$lib/types/soundatlas';

  export let summary: RoutePublicationSummary | null = null;
  export let saving = false;
  export let errorMessage: string | null = null;
  export let success = false;
  export let onPublish: () => void = () => {};

  function countLabel(count: number, singular: string, plural: string): string {
    return `${count} ${count === 1 ? singular : plural}`;
  }
</script>

{#if summary}
  <section
    class="publication-panel"
    aria-labelledby="route-publication-heading"
  >
    <h3 id="route-publication-heading">Publication blocking checks</h3>

    <div class:ready={summary.technical_ready} class="readiness" role="status">
      <strong
        >{summary.technical_ready
          ? 'Publication checks clear'
          : 'Publication blocked'}</strong
      >
    </div>

    <p class="event-totals">
      {summary.included_events.length} included · {summary.excluded_event_ids
        .length} excluded
    </p>

    {#if summary.proposed_route}
      <p class="event-totals">
        Proposed route: <strong>{summary.proposed_route.title}</strong>
        ({summary.proposed_route.year_start}-{summary.proposed_route.year_end})
      </p>
    {/if}

    {#if summary.included_event_warning_count > 0 || summary.included_event_technical_error_count > 0}
      <div class="finding-counts" aria-label="Included event findings">
        {#if summary.included_event_warning_count > 0}
          <span class="finding-count warning-count">
            {countLabel(
              summary.included_event_warning_count,
              'event warning',
              'event warnings'
            )}
          </span>
        {/if}
        {#if summary.included_event_technical_error_count > 0}
          <span class="finding-count error-count">
            {countLabel(
              summary.included_event_technical_error_count,
              'blocking error',
              'blocking errors'
            )}
          </span>
        {/if}
      </div>
    {/if}

    {#if summary.route_technical_errors.length > 0}
      <section
        class="message-group errors"
        aria-labelledby="publication-errors-heading"
      >
        <h4 id="publication-errors-heading">Route blocking errors</h4>
        <ul>
          {#each summary.route_technical_errors as error (error)}<li>
              {error}
            </li>{/each}
        </ul>
      </section>
    {/if}

    {#if summary.route_warnings.length > 0}
      <details class="message-group warnings">
        <summary>
          {countLabel(
            summary.route_warnings.length,
            'route warning',
            'route warnings'
          )}
        </summary>
        <ul class="route-warning-list">
          {#each summary.route_warnings as warning (warning)}<li>
              {warning}
            </li>{/each}
        </ul>
      </details>
    {/if}

    <button
      type="button"
      class="publish-button"
      disabled={!summary.technical_ready || saving}
      on:click={onPublish}
      >{saving ? 'Publishing…' : 'Publish reviewed route'}</button
    >

    {#if success}<p class="success" role="status">
        Published this exact reviewed result.
      </p>{/if}
    {#if errorMessage}<p class="action-error" role="alert">
        {errorMessage}
      </p>{/if}
  </section>
{/if}

<style>
  .publication-panel {
    display: grid;
    gap: 0.5rem;
    padding: 0.65rem 0;
    border-top: 1px solid #d9e0e7;
    border-bottom: 1px solid #d9e0e7;
    color: #314151;
    font-size: 0.78rem;
  }
  .publication-panel > h3,
  .message-group h4 {
    margin: 0;
  }
  .publication-panel > h3 {
    font-size: 0.9rem;
  }
  .event-totals {
    margin: 0;
    color: #536170;
  }
  .readiness {
    padding-left: 0.45rem;
    border-left: 0.2rem solid #a32626;
  }
  .readiness.ready {
    border-left-color: #176b3a;
  }
  .finding-counts {
    display: flex;
    flex-wrap: wrap;
    gap: 0.3rem;
  }
  .finding-count {
    padding: 0.14rem 0.36rem;
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
  .message-group {
    display: grid;
    gap: 0.35rem;
    padding: 0.55rem;
    border-radius: 6px;
  }
  .message-group.errors {
    border: 1px solid #e8b9b9;
    background: #fff5f5;
    color: #8b2020;
  }
  .message-group.warnings {
    color: #65440b;
  }
  .message-group summary {
    cursor: pointer;
    font-weight: 800;
  }
  .message-group ul {
    margin: 0;
  }
  .route-warning-list {
    max-height: 11rem;
    margin-top: 0.4rem !important;
    padding: 0;
    overflow-y: auto;
    border-top: 1px solid #e6d9b5;
    list-style: none;
  }
  .route-warning-list li {
    padding: 0.4rem 0.15rem;
    border-bottom: 1px solid #eee3c7;
    line-height: 1.35;
  }
  .publish-button {
    min-height: 2.25rem;
    padding: 0.45rem 0.6rem;
    border: 1px solid #8e6d1e;
    border-radius: 6px;
    background: #8e6d1e;
    color: #fff;
    font: inherit;
    font-weight: 800;
  }
  .publish-button:disabled {
    cursor: not-allowed;
    opacity: 0.55;
  }
  .success,
  .action-error {
    margin: 0;
    font-weight: 700;
  }
  .success {
    color: #176b3a;
  }
  .action-error {
    color: #a32626;
  }
</style>
