export type TimelineCardCenteringInput = {
  containerWidth: number;
  scrollWidth: number;
  itemOffsetLeft: number;
  itemWidth: number;
};

export type TimelineCardCenteringRectInput = {
  containerLeft: number;
  containerWidth: number;
  scrollLeft: number;
  scrollWidth: number;
  itemLeft: number;
  itemWidth: number;
};

export function getCenteredScrollLeft({
  containerWidth,
  scrollWidth,
  itemOffsetLeft,
  itemWidth
}: TimelineCardCenteringInput): number {
  if (containerWidth <= 0 || scrollWidth <= containerWidth) {
    return 0;
  }

  const desiredScrollLeft = itemOffsetLeft - (containerWidth - itemWidth) / 2;
  const maxScrollLeft = scrollWidth - containerWidth;

  return Math.max(0, Math.min(maxScrollLeft, desiredScrollLeft));
}

export function getCenteredScrollLeftFromRects({
  containerLeft,
  containerWidth,
  scrollLeft,
  scrollWidth,
  itemLeft,
  itemWidth
}: TimelineCardCenteringRectInput): number {
  if (containerWidth <= 0 || scrollWidth <= containerWidth) {
    return 0;
  }

  const desiredScrollLeft =
    scrollLeft + (itemLeft - containerLeft) - (containerWidth - itemWidth) / 2;
  const maxScrollLeft = scrollWidth - containerWidth;

  return Math.max(0, Math.min(maxScrollLeft, desiredScrollLeft));
}
