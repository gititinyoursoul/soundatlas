import { describe, expect, it } from 'vitest';
import { resolvePreviewItemId } from './story-preview';

describe('story preview selection', () => {
  it('matches an image item by its canonical url even when the preview url differs', () => {
    const previewItems = [
      {
        id: 'image:123',
        selectionUrl: 'https://upload.wikimedia.org/example.jpg',
        previewUrl: 'https://upload.wikimedia.org/thumb/example.jpg'
      },
      {
        id: 'media:456',
        selectionUrl: 'https://www.youtube.com/watch?v=example',
        previewUrl: 'https://www.youtube.com/watch?v=example'
      }
    ];

    expect(resolvePreviewItemId(previewItems, 'https://upload.wikimedia.org/example.jpg')).toBe(
      'image:123'
    );
  });

  it('matches a media item by its canonical url', () => {
    const previewItems = [
      {
        id: 'image:123',
        selectionUrl: 'https://upload.wikimedia.org/example.jpg',
        previewUrl: 'https://upload.wikimedia.org/thumb/example.jpg'
      },
      {
        id: 'media:456',
        selectionUrl: 'https://www.youtube.com/watch?v=example',
        previewUrl: 'https://www.youtube.com/watch?v=example'
      }
    ];

    expect(resolvePreviewItemId(previewItems, 'https://www.youtube.com/watch?v=example')).toBe(
      'media:456'
    );
  });

  it('falls back to the first item when there is no match', () => {
    const previewItems = [
      {
        id: 'image:123',
        selectionUrl: 'https://upload.wikimedia.org/example.jpg',
        previewUrl: 'https://upload.wikimedia.org/thumb/example.jpg'
      }
    ];

    expect(resolvePreviewItemId(previewItems, 'https://example.invalid/no-match')).toBe(
      'image:123'
    );
  });
});
