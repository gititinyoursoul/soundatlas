<script lang="ts">
  import type { InactiveCandidateProjection } from '$lib/data/editorial-review';

  export let candidate: InactiveCandidateProjection | null = null;

  $: account = candidate?.account ?? null;
  $: context = account?.context ?? {};
  $: sourceUrls = stringValues(context.source_urls);
  $: sourceLeads = displayValues(context.source_leads);
  $: claims = displayValues(context.claims);
  $: gaps = displayValues(context.risk_notes);
  $: narrative = stringValue(context.decision_rationale);
  $: routeFunction = stringValue(context.route_function);
  $: recommendation = stringValue(context.status);

  function stringValue(value: unknown): string | null {
    return typeof value === 'string' && value.trim() ? value : null;
  }

  function stringValues(value: unknown): string[] {
    return Array.isArray(value)
      ? value.filter(
          (item): item is string =>
            typeof item === 'string' && Boolean(item.trim())
        )
      : [];
  }

  function displayValues(value: unknown): string[] {
    return Array.isArray(value)
      ? value.map((item) =>
          typeof item === 'string' ? item : JSON.stringify(item)
        )
      : [];
  }
</script>

<aside
  class="grid h-full content-start gap-5 overflow-y-auto bg-white p-5 text-[#314151]"
  aria-label="Inactive candidate details"
>
  {#if candidate && account}
    <header class="grid gap-2 border-b border-[#d9e0e7] pb-4">
      <p
        class="m-0 text-xs font-extrabold uppercase tracking-[0.14em] text-[#78510c]"
      >
        Inactive candidate · Not in current route
      </p>
      <h2 class="m-0 text-xl leading-tight">{candidate.title}</h2>
      <p class="m-0 text-sm text-[#536170]">
        Timeframe: {candidate.years ?? 'Unresolved'} · Place: {candidate.place ??
          'Unresolved'}
      </p>
    </header>

    {#if candidate.summary}
      <section class="grid gap-1.5">
        <h3 class="m-0 text-sm font-extrabold uppercase tracking-wide">
          Summary
        </h3>
        <p class="m-0 leading-relaxed">{candidate.summary}</p>
      </section>
    {/if}
    {#if candidate.significance}
      <section class="grid gap-1.5">
        <h3 class="m-0 text-sm font-extrabold uppercase tracking-wide">
          Significance
        </h3>
        <p class="m-0 leading-relaxed">{candidate.significance}</p>
      </section>
    {/if}

    <section class="grid gap-1.5">
      <h3 class="m-0 text-sm font-extrabold uppercase tracking-wide">
        Composition
      </h3>
      <p class="m-0">
        <strong>Outcome:</strong>
        {account.outcome.replace('_', ' ')}
      </p>
      <p class="m-0"><strong>Reason:</strong> {account.reason}</p>
      {#if account.related_candidate_ids.length > 0}
        <p class="m-0">
          <strong>Related candidates:</strong>
          {account.related_candidate_ids.join(', ')}
        </p>
      {:else}
        <p class="m-0">
          <strong>Related candidates:</strong> No merge, split, or overlap relationship
          was recorded.
        </p>
      {/if}
    </section>

    <p
      class="m-0 border-t border-[#d9e0e7] pt-4 text-sm leading-relaxed text-[#536170]"
    >
      To disagree with this generated composition outcome, use the route
      revision request boundary in #85. This review does not edit, activate, or
      regenerate the candidate.
    </p>

    {#if routeFunction || narrative || recommendation}
      <section class="grid gap-1.5">
        <h3 class="m-0 text-sm font-extrabold uppercase tracking-wide">
          Route context
        </h3>
        {#if routeFunction}<p class="m-0">
            <strong>Function:</strong>
            {routeFunction}
          </p>{/if}
        {#if narrative}<p class="m-0">
            <strong>Narrative:</strong>
            {narrative}
          </p>{/if}
        {#if recommendation}<p class="m-0">
            <strong>Agent recommendation:</strong>
            {recommendation}
          </p>{/if}
      </section>
    {/if}

    {#if sourceUrls.length > 0 || sourceLeads.length > 0 || gaps.length > 0}
      <section class="grid gap-1.5">
        <h3 class="m-0 text-sm font-extrabold uppercase tracking-wide">
          Sources and gaps
        </h3>
        {#if sourceUrls.length > 0}
          <ul class="m-0 grid gap-1 break-words pl-5">
            {#each sourceUrls as url (url)}
              <li>
                <!-- eslint-disable svelte/no-navigation-without-resolve -->
                <a
                  class="text-[#bb3f22] underline"
                  href={url}
                  target="_blank"
                  rel="noreferrer">{url}</a
                >
                <!-- eslint-enable svelte/no-navigation-without-resolve -->
              </li>
            {/each}
          </ul>
        {/if}
        {#if sourceLeads.length > 0}<p class="m-0">
            <strong>Source leads:</strong>
            {sourceLeads.join('; ')}
          </p>{/if}
        {#if gaps.length > 0}<p class="m-0">
            <strong>Gaps:</strong>
            {gaps.join('; ')}
          </p>{/if}
      </section>
    {/if}

    {#if claims.length > 0}
      <section class="grid gap-1.5">
        <h3 class="m-0 text-sm font-extrabold uppercase tracking-wide">
          Claims
        </h3>
        <ul class="m-0 grid gap-1 pl-5">
          {#each claims as claim (claim)}<li>{claim}</li>{/each}
        </ul>
      </section>
    {/if}

    {#if account.findings.length > 0}
      <section class="grid gap-1.5">
        <h3 class="m-0 text-sm font-extrabold uppercase tracking-wide">
          Findings
        </h3>
        <ul class="m-0 grid gap-1 pl-5">
          {#each account.findings as finding (finding.owner + finding.message)}<li
            >
              {finding.message}
            </li>{/each}
        </ul>
      </section>
    {/if}
  {/if}
</aside>
