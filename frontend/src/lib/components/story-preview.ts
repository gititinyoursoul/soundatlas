export type StoryPreviewItem = {
  id: string;
  selectionUrl: string;
  previewUrl?: string | null;
};

export function resolvePreviewItemId(
  previewItems: StoryPreviewItem[],
  selectedPreviewUrl: string | null
): string {
  if (selectedPreviewUrl) {
    const selectedPreviewItem = previewItems.find(
      (item) => item.selectionUrl === selectedPreviewUrl || item.previewUrl === selectedPreviewUrl
    );

    if (selectedPreviewItem) {
      return selectedPreviewItem.id;
    }
  }

  return previewItems[0]?.id ?? '';
}
