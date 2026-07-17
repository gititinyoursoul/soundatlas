import adapter from '@sveltejs/adapter-static';

const base = process.env.VITE_BASE_PATH ?? '';

/** @type {import('@sveltejs/kit').Config} */
const config = {
  kit: {
    adapter: adapter({
      fallback: 'index.html'
    }),
    prerender: {
      entries: []
    },
    paths: {
      base
    }
  }
};

export default config;
