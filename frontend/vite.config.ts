import { sveltekit } from '@sveltejs/kit/vite';
import tailwindcss from '@tailwindcss/vite';
import { defineConfig } from 'vitest/config';

export default defineConfig({
  plugins: [tailwindcss(), sveltekit()],
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
