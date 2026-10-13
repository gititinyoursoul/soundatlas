import { describe, expect, it } from 'vitest';
import { parseYouTubeEmbed } from './youtube';

describe('parseYouTubeEmbed', () => {
  it.each([
    'https://youtu.be/video-123?si=share-token',
    'https://www.youtube.com/watch?v=video-123',
    'https://music.youtube.com/watch?v=video-123',
    'https://youtube.com/embed/video-123',
    'https://www.youtube-nocookie.com/embed/video-123'
  ])('returns a privacy-friendly video embed for %s', (url) => {
    expect(parseYouTubeEmbed(url)).toEqual({
      kind: 'video',
      id: 'video-123',
      embedUrl: 'https://www.youtube-nocookie.com/embed/video-123'
    });
  });

  it('uses the playlist ID when a YouTube URL has both video and list parameters', () => {
    expect(
      parseYouTubeEmbed(
        'https://www.youtube.com/watch?v=video-123&list=PL%20mix'
      )
    ).toEqual({
      kind: 'playlist',
      id: 'PL mix',
      embedUrl:
        'https://www.youtube-nocookie.com/embed/videoseries?list=PL%20mix'
    });
  });

  it.each([
    'video-123',
    'not a URL',
    'https://example.com/watch?v=video-123',
    'https://youtube.com.example.org/watch?v=video-123',
    'https://youtu.be/',
    'https://youtube.com/watch?v=%20',
    'https://youtube.com/embed/',
    'https://youtube.com/shorts/video-123'
  ])('rejects malformed or unsupported input %s', (url) => {
    expect(parseYouTubeEmbed(url)).toBeNull();
  });
});
