import js from '@eslint/js';
import security from 'eslint-plugin-security';
import svelte from 'eslint-plugin-svelte';
import globals from 'globals';
import tseslint from 'typescript-eslint';

export default tseslint.config(
  {
    ignores: ['.svelte-kit/**', 'build/**', 'coverage/**', 'node_modules/**']
  },
  {
    languageOptions: {
      globals: {
        ...globals.browser,
        ...globals.node,
        ...globals.vitest
      }
    }
  },
  js.configs.recommended,
  ...tseslint.configs.recommended,
  security.configs.recommended,
  ...svelte.configs['flat/recommended'],
  {
    files: ['**/*.svelte'],
    languageOptions: {
      parserOptions: {
        parser: tseslint.parser
      }
    },
    rules: {
      'no-useless-assignment': 'off'
    }
  },
  {
    files: ['scripts/**/*.mjs'],
    rules: {
      'security/detect-non-literal-fs-filename': 'off'
    }
  },
  {
    files: ['**/*.svelte', '**/*.ts', '**/*.js', '**/*.mjs'],
    rules: {
      'security/detect-object-injection': 'off'
    }
  }
);
