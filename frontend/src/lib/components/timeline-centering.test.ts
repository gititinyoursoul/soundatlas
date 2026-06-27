import { describe, expect, it } from 'vitest';
import { getCenteredScrollLeft, getCenteredScrollLeftFromRects } from './timeline-centering';

describe('getCenteredScrollLeft', () => {
  it('centers the selected item when there is room to scroll', () => {
    expect(
      getCenteredScrollLeft({
        containerWidth: 400,
        scrollWidth: 1200,
        itemOffsetLeft: 500,
        itemWidth: 160
      })
    ).toBe(380);
  });

  it('clamps to the left edge when the selected item is near the start', () => {
    expect(
      getCenteredScrollLeft({
        containerWidth: 400,
        scrollWidth: 1200,
        itemOffsetLeft: 40,
        itemWidth: 160
      })
    ).toBe(0);
  });

  it('clamps to the right edge when centering would overscroll', () => {
    expect(
      getCenteredScrollLeft({
        containerWidth: 400,
        scrollWidth: 1200,
        itemOffsetLeft: 1040,
        itemWidth: 160
      })
    ).toBe(800);
  });

  it('returns zero when the strip does not overflow', () => {
    expect(
      getCenteredScrollLeft({
        containerWidth: 400,
        scrollWidth: 300,
        itemOffsetLeft: 120,
        itemWidth: 160
      })
    ).toBe(0);
  });

  it('re-centers a selected card using live container and item geometry', () => {
    expect(
      getCenteredScrollLeftFromRects({
        containerLeft: 100,
        containerWidth: 400,
        scrollLeft: 240,
        scrollWidth: 1200,
        itemLeft: 760,
        itemWidth: 160
      })
    ).toBe(780);
  });

  it('clamps the geometry-based calculation when the selected card is near the end', () => {
    expect(
      getCenteredScrollLeftFromRects({
        containerLeft: 100,
        containerWidth: 400,
        scrollLeft: 700,
        scrollWidth: 1200,
        itemLeft: 1260,
        itemWidth: 160
      })
    ).toBe(800);
  });
});
