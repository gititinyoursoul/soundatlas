export type YouTubeEmbed = {
  kind: 'video' | 'playlist';
  id: string;
  embedUrl: string;
};

export function parseYouTubeEmbed(url: string): YouTubeEmbed | null {
  let parsedUrl: URL;

  try {
    parsedUrl = new URL(url);
  } catch {
    return null;
  }

  const hostname = parsedUrl.hostname.replace(/^www\./, '');
  const playlistId = parsedUrl.searchParams.get('list');

  if (playlistId && isYouTubeHostname(hostname)) {
    return {
      kind: 'playlist',
      id: playlistId,
      embedUrl: `https://www.youtube-nocookie.com/embed/videoseries?list=${encodeURIComponent(playlistId)}`
    };
  }

  const videoId = extractVideoId(parsedUrl, hostname);
  if (!videoId) {
    return null;
  }

  return {
    kind: 'video',
    id: videoId,
    embedUrl: `https://www.youtube-nocookie.com/embed/${encodeURIComponent(videoId)}`
  };
}

function extractVideoId(parsedUrl: URL, hostname: string): string | null {
  if (hostname === 'youtu.be') {
    return cleanId(parsedUrl.pathname.slice(1));
  }

  if (!isYouTubeHostname(hostname)) {
    return null;
  }

  if (parsedUrl.pathname === '/watch') {
    return cleanId(parsedUrl.searchParams.get('v'));
  }

  const embedMatch = parsedUrl.pathname.match(/^\/embed\/([^/]+)/);
  if (embedMatch) {
    return cleanId(embedMatch[1]);
  }

  return null;
}

function isYouTubeHostname(hostname: string): boolean {
  return hostname === 'youtube.com' || hostname === 'music.youtube.com' || hostname === 'youtube-nocookie.com';
}

function cleanId(value: string | null): string | null {
  const cleanedValue = value?.trim();
  return cleanedValue ? cleanedValue : null;
}
