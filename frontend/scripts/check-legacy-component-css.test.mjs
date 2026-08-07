import assert from 'node:assert/strict';
import test from 'node:test';

import {
  componentStyleBytes,
  validateBaselineChange,
  validateLegacyComponentCss
} from './check-legacy-component-css.mjs';

const baseline = {
  total_bytes: 12,
  components: { 'lib/Legacy.svelte': 12 }
};

test('counts component-scoped style bytes', () => {
  assert.equal(componentStyleBytes('<style>.x {}</style>'), 5);
  assert.equal(componentStyleBytes('<script>const value = 1;</script>'), 0);
});

test('permits legacy CSS removal', () => {
  assert.deepEqual(validateLegacyComponentCss({}, baseline), {
    errors: [],
    total: 0
  });
});

test('rejects a new component style block', () => {
  const result = validateLegacyComponentCss(
    { ...baseline.components, 'lib/New.svelte': 1 },
    baseline
  );

  assert.match(result.errors[0], /introduces a new component-scoped/);
});

test('rejects component and aggregate CSS growth', () => {
  const result = validateLegacyComponentCss(
    { 'lib/Legacy.svelte': 13 },
    baseline
  );

  assert.equal(result.errors.length, 2);
  assert.match(result.errors[0], /increases legacy component CSS/);
  assert.match(result.errors[1], /increases in total/);
});

test('rejects an unapproved global CSS exception surface', () => {
  const result = validateLegacyComponentCss(baseline.components, baseline, {
    'src/styles/new-global.css': 1
  });

  assert.match(result.errors[0], /new global CSS exception surface/);
});

test('rejects a baseline increase or new exception surface', () => {
  const current = {
    total_bytes: 13,
    components: { 'lib/Legacy.svelte': 13 },
    exception_files: { 'src/styles/new-global.css': 0 }
  };

  const errors = validateBaselineChange(current, baseline);

  assert.equal(errors.length, 3);
  assert.match(errors[0], /baseline increases/);
  assert.match(errors[1], /component CSS baseline/);
  assert.match(errors[2], /new global CSS exception surface/);
});
