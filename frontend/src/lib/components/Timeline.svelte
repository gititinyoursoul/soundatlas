<script lang="ts">
  export let routeTitle = 'Route';
  export let routeStartYear = 1965;
  export let routeEndYear = 1985;
  export let eventStartYear: number | null = null;
  export let eventEndYear: number | null = null;

  $: axisStart = Math.min(routeStartYear, routeEndYear);
  $: axisEnd = Math.max(routeStartYear, routeEndYear);
  $: axisSpan = Math.max(axisEnd - axisStart, 1);
  $: hasEventRange = eventStartYear !== null && eventEndYear !== null;
  $: highlightedStartYear = hasEventRange
    ? Math.max(axisStart, Math.min(eventStartYear, eventEndYear))
    : axisStart;
  $: highlightedEndYear = hasEventRange
    ? Math.min(axisEnd, Math.max(eventStartYear, eventEndYear))
    : axisStart;
  $: highlightedStart = ((highlightedStartYear - axisStart) / axisSpan) * 100;
  $: highlightedWidth = Math.max(((highlightedEndYear - highlightedStartYear) / axisSpan) * 100, 0);
  function toPercent(year: number): number {
    return ((year - axisStart) / axisSpan) * 100;
  }
</script>

<section class="timeline" aria-label={`Timeline for route ${routeTitle}`}>
  <div class="timeline-header">
    <div class="title-block">
      <span>Route</span>
      <strong>{routeTitle}</strong>
    </div>
    <span class="year-range">{axisStart} - {axisEnd}</span>
  </div>

  <div class="track">
    <div class="axis" aria-hidden="true">
      <div class="line"></div>
      {#if hasEventRange}
        <div
          class="highlight"
          style:left={`${Math.max(0, Math.min(100, highlightedStart))}%`}
          style:width={`${Math.max(0, Math.min(100, highlightedWidth))}%`}
        ></div>
      {/if}
      <div class="tick start" style:left={`${toPercent(axisStart)}%`} aria-hidden="true"></div>
      <div class="tick end" style:left={`${toPercent(axisEnd)}%`} aria-hidden="true"></div>
    </div>

    <div class="labels" aria-hidden="true">
      <span>{axisStart}</span>
      <span>{axisEnd}</span>
    </div>
  </div>

</section>

<style>
  .timeline {
    display: grid;
    gap: 0.75rem;
    padding: 1rem;
    border-top: 1px solid #d9e0e7;
    background: linear-gradient(180deg, #ffffff 0%, #f9fbfc 100%);
  }

  .timeline-header {
    display: flex;
    align-items: flex-end;
    justify-content: space-between;
    gap: 1rem;
  }

  .title-block {
    display: grid;
    gap: 0.1rem;
  }

  .title-block span {
    color: #6b7785;
    font-size: 0.78rem;
    font-weight: 800;
    letter-spacing: 0.08em;
    text-transform: uppercase;
  }

  .title-block strong {
    color: #17202a;
    font-size: 0.98rem;
  }

  .year-range {
    color: #314151;
    font-size: 0.9rem;
    font-weight: 700;
    white-space: nowrap;
  }

  .track {
    display: grid;
    gap: 0.45rem;
  }

  .axis {
    position: relative;
    height: 2.5rem;
  }

  .line {
    position: absolute;
    inset: 50% 0 auto;
    height: 0.25rem;
    transform: translateY(-50%);
    border-radius: 999px;
    background: linear-gradient(90deg, #d3dce5 0%, #b8c5d1 100%);
  }

  .highlight {
    position: absolute;
    inset: 50% auto auto;
    height: 0.75rem;
    min-width: 0.85rem;
    transform: translateY(-50%);
    border-radius: 999px;
    background: linear-gradient(90deg, #e4572e 0%, #ef8c63 100%);
    box-shadow: 0 0 0 1px rgba(228, 87, 46, 0.15);
  }

  .tick {
    position: absolute;
    top: 50%;
    width: 0.7rem;
    height: 0.7rem;
    transform: translate(-50%, -50%);
    border: 2px solid #17202a;
    border-radius: 999px;
    background: #ffffff;
  }

  .labels {
    display: flex;
    align-items: center;
    justify-content: space-between;
    color: #536170;
    font-size: 0.8rem;
  }

</style>
