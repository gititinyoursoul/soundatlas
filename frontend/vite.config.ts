import { sveltekit } from '@sveltejs/kit/vite';
import tailwindcss from '@tailwindcss/vite';
import { defineConfig } from 'vitest/config';

const PANE_PREVIEW_PATH = '/__soundatlas/pane-preview';

function escapeHtml(value: string): string {
  return value.replace(/[&<>'"]/g, (character) => {
    const entities: Record<string, string> = {
      '&': '&amp;',
      '<': '&lt;',
      '>': '&gt;',
      "'": '&#39;',
      '"': '&quot;'
    };
    return entities[character];
  });
}

function panePreviewPage(): string {
  const identity = {
    pane: process.env.SOUNDATLAS_PANE_PREVIEW_NAME ?? 'unknown Pane',
    paneId: process.env.SOUNDATLAS_PANE_PREVIEW_ID ?? 'unknown id',
    branch: process.env.SOUNDATLAS_PANE_PREVIEW_BRANCH ?? 'unknown branch',
    commit: process.env.SOUNDATLAS_PANE_PREVIEW_COMMIT ?? 'unknown commit',
    state: process.env.SOUNDATLAS_PANE_PREVIEW_STATE ?? 'unknown state',
    mode: process.env.SOUNDATLAS_PANE_PREVIEW_MODE ?? 'api',
    editorial: process.env.VITE_EDITORIAL_MODE === 'true' ? 'on' : 'off'
  };
  const label = Object.entries(identity)
    .map(([key, value]) => `<dt>${escapeHtml(key)}</dt><dd>${escapeHtml(value)}</dd>`)
    .join('');

  return `<!doctype html><html lang="en"><head><meta charset="utf-8"><title>SoundAtlas Pane preview</title><style>body{margin:0;background:#eef0f2;color:#18212b;font:15px system-ui,sans-serif}header{padding:12px 18px;border-bottom:1px solid #aab3bc;background:#fff}h1{font-size:18px;margin:0 0 8px}p{margin:0}dl{display:grid;grid-template-columns:max-content 1fr;gap:4px 10px;margin:10px 0 0}dt{font-weight:700}dd{margin:0;font-family:ui-monospace,monospace}iframe{border:0;width:100%;height:calc(100vh - 150px);background:#fff}</style></head><body><header><h1>SoundAtlas Pane preview — not the host Compose frontend</h1><p>This page is served from the selected Pane-managed worktree. Restart the helper after changes to refresh this identity snapshot.</p><dl>${label}</dl></header><iframe title="SoundAtlas application from selected Pane worktree" src="/"></iframe></body></html>`;
}

function panePreviewPlugin() {
  return {
    name: 'soundatlas-pane-preview',
    configureServer(server: { middlewares: { use: (path: string, handler: (request: unknown, response: { end: (content: string) => void; setHeader: (name: string, value: string) => void }) => void) => void } }) {
      if (process.env.SOUNDATLAS_PANE_PREVIEW !== '1') return;
      server.middlewares.use(PANE_PREVIEW_PATH, (_request, response) => {
        response.setHeader('Content-Type', 'text/html; charset=utf-8');
        response.end(panePreviewPage());
      });
    }
  };
}

export default defineConfig({
  plugins: [tailwindcss(), sveltekit(), panePreviewPlugin()],
  test: {
    environment: 'node',
    include: ['src/**/*.test.ts'],
    coverage: {
      provider: 'v8',
      reporter: ['text', 'html'],
      reportsDirectory: 'coverage',
      include: ['src/**/*.{ts,svelte}'],
      exclude: [
        'src/**/*.test.ts',
        'src/**/*.d.ts',
        'src/app.html',
        'src/routes/+layout.svelte',
        'src/routes/+page.svelte',
        'src/routes/+page.ts',
        'src/lib/test/**'
      ]
    }
  }
});
