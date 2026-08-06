<script lang="ts">
  import type { RoutePublicationSummary } from '$lib/types/soundatlas';

  export let summary: RoutePublicationSummary | null = null;
  export let saving = false;
  export let errorMessage: string | null = null;
  export let success = false;
  export let onPublish: () => void = () => {};
</script>

{#if summary}
  <section
    class="publication-panel"
    aria-labelledby="route-publication-heading"
  >
    <div class="publication-heading">
      <span>Route action</span>
      <h3 id="route-publication-heading">Publication</h3>
    </div>

    <dl class="publication-counts">
      <div>
        <dt>Included events</dt>
        <dd>{summary.included_events.length}</dd>
      </div>
      <div>
        <dt>Excluded events</dt>
        <dd>{summary.excluded_event_ids.length}</dd>
      </div>
      <div class="warning-count">
        <dt>Event warnings</dt>
        <dd>{summary.included_event_warning_count}</dd>
      </div>
      <div class="error-count">
        <dt>Event blocking errors</dt>
        <dd>{summary.included_event_technical_error_count}</dd>
      </div>
    </dl>

    <div class:ready={summary.technical_ready} class="readiness" role="status">
      <strong
        >{summary.technical_ready
          ? 'Ready to publish'
          : 'Publication blocked'}</strong
      >
      <span>
        {summary.technical_ready
          ? 'No blocking technical errors.'
          : summary.included_event_technical_error_count > 0 &&
              summary.route_technical_errors.length > 0
            ? 'Review affected events below and resolve the route errors listed here.'
            : summary.included_event_technical_error_count > 0
              ? 'Review the affected event rows below or move unusable events to Don’t use.'
              : 'Resolve the route blocking errors listed below.'}
      </span>
    </div>

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
        <summary
          >Route editorial warnings ({summary.route_warnings.length})</summary
        >
        <p>
          These route-level findings require editorial judgment but do not block
          publication.
        </p>
        <ul>
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
      >{saving ? 'Publishing…' : 'Publish exact reviewed route'}</button
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
    gap: 0.7rem;
    padding: 0.75rem;
    border: 1px solid #d8c58f;
    border-radius: 8px;
    background: #fffaf0;
    color: #4c3b16;
    font-size: 0.78rem;
  }
  .publication-heading {
    display: grid;
    gap: 0.15rem;
  }
  .publication-heading span {
    color: #78510c;
    font-size: 0.66rem;
    font-weight: 800;
    letter-spacing: 0.08em;
    text-transform: uppercase;
  }
  .publication-heading h3,
  .message-group h4 {
    margin: 0;
  }
  .publication-heading h3 {
    font-size: 0.95rem;
  }
  .publication-counts {
    display: grid;
    grid-template-columns: repeat(2, minmax(0, 1fr));
    gap: 0.4rem;
    margin: 0;
  }
  .publication-counts div {
    display: grid;
    gap: 0.1rem;
    padding: 0.45rem;
    border: 1px solid #e6d9b5;
    border-radius: 6px;
    background: #fff;
  }
  .publication-counts dt {
    font-size: 0.66rem;
    font-weight: 700;
  }
  .publication-counts dd {
    margin: 0;
    font-size: 1rem;
    font-weight: 800;
  }
  .publication-counts .warning-count {
    border-color: #e6d9b5;
    color: #65440b;
  }
  .publication-counts .error-count {
    border-color: #e8b9b9;
    color: #8b2020;
  }
  .readiness {
    display: grid;
    gap: 0.12rem;
    padding-left: 0.55rem;
    border-left: 0.25rem solid #a32626;
  }
  .readiness.ready {
    border-left-color: #176b3a;
  }
  .readiness span,
  .message-group p {
    line-height: 1.4;
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
    border: 1px solid #e6d9b5;
    background: #fff;
    color: #65440b;
  }
  .message-group summary {
    cursor: pointer;
    font-weight: 800;
  }
  .message-group p,
  .message-group ul {
    margin: 0;
  }
  .message-group ul {
    padding-left: 1rem;
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
