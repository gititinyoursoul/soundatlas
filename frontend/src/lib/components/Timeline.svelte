<script lang="ts">
  import type { TimelineRange } from '$lib/types/soundatlas';

  export let range: TimelineRange = { fromYear: 1965, toYear: 1985 };
  export let minYear = 1965;
  export let maxYear = 1985;
  export let onChangeRange: (range: TimelineRange) => void = () => {};

  function updateFromYear(value: string): void {
    const fromYear = Number(value);
    onChangeRange({
      fromYear,
      toYear: Math.max(fromYear, range.toYear)
    });
  }

  function updateToYear(value: string): void {
    const toYear = Number(value);
    onChangeRange({
      fromYear: Math.min(range.fromYear, toYear),
      toYear
    });
  }
</script>

<section class="timeline" aria-label="Zeitraum">
  <div class="timeline-header">
    <span>{range.fromYear}</span>
    <strong>Timeline</strong>
    <span>{range.toYear}</span>
  </div>

  <div class="sliders">
    <label>
      Von
      <input
        aria-label="Startjahr"
        type="range"
        min={minYear}
        max={maxYear}
        value={range.fromYear}
        on:input={(event) => updateFromYear(event.currentTarget.value)}
      />
    </label>
    <label>
      Bis
      <input
        aria-label="Endjahr"
        type="range"
        min={minYear}
        max={maxYear}
        value={range.toYear}
        on:input={(event) => updateToYear(event.currentTarget.value)}
      />
    </label>
  </div>

  <div class="focus-year">
    <span>1965</span>
    <span class="marker">1977</span>
    <span>1985</span>
  </div>
</section>

<style>
  .timeline {
    display: grid;
    gap: 0.65rem;
    padding: 1rem;
    border-top: 1px solid #d9e0e7;
    background: #ffffff;
  }

  .timeline-header,
  .focus-year {
    display: flex;
    align-items: center;
    justify-content: space-between;
    color: #536170;
    font-size: 0.85rem;
  }

  .timeline-header strong {
    color: #17202a;
    font-size: 0.95rem;
  }

  .sliders {
    display: grid;
    gap: 0.5rem;
  }

  label {
    display: grid;
    grid-template-columns: 2.5rem 1fr;
    align-items: center;
    gap: 0.5rem;
    color: #314151;
    font-size: 0.85rem;
  }

  input[type='range'] {
    width: 100%;
    accent-color: #e4572e;
  }

  .marker {
    padding: 0.15rem 0.45rem;
    border-radius: 999px;
    background: #17202a;
    color: #ffffff;
  }
</style>
