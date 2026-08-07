import { readFile, readdir } from 'node:fs/promises';
import { execFile } from 'node:child_process';
import { promisify } from 'node:util';
import { dirname, relative, resolve } from 'node:path';
import { fileURLToPath } from 'node:url';

const scriptDirectory = dirname(fileURLToPath(import.meta.url));
const frontendRoot = resolve(scriptDirectory, '..');
const sourceRoot = resolve(frontendRoot, 'src');
const baselinePath = resolve(
  frontendRoot,
  'config/legacy-component-css-baseline.json'
);
const executeFile = promisify(execFile);

export function componentStyleBytes(source) {
  let total = 0;
  let cursor = 0;

  while (cursor < source.length) {
    const openingTag = source.indexOf('<style', cursor);
    if (openingTag === -1) break;
    const contentStart = source.indexOf('>', openingTag);
    if (contentStart === -1) break;
    const closingTag = source.indexOf('</style>', contentStart + 1);
    if (closingTag === -1) break;
    total += Buffer.byteLength(source.slice(contentStart + 1, closingTag));
    cursor = closingTag + '</style>'.length;
  }

  return total;
}

export function validateLegacyComponentCss(
  current,
  baseline,
  exceptionFiles = {}
) {
  const errors = [];
  const expected = baseline.components ?? {};

  for (const [file, bytes] of Object.entries(current)) {
    if (!(file in expected)) {
      errors.push(`${file} introduces a new component-scoped <style> block.`);
    } else if (bytes > expected[file]) {
      errors.push(
        `${file} increases legacy component CSS from ${expected[file]} to ${bytes} bytes.`
      );
    }
  }

  const expectedExceptions = baseline.exception_files ?? {};
  for (const file of Object.keys(exceptionFiles)) {
    if (!(file in expectedExceptions)) {
      errors.push(`${file} introduces a new global CSS exception surface.`);
    }
  }

  const total =
    Object.values(current).reduce((sum, bytes) => sum + bytes, 0) +
    Object.values(exceptionFiles).reduce((sum, bytes) => sum + bytes, 0);
  if (total > baseline.total_bytes) {
    errors.push(
      `Legacy component CSS increases in total from ${baseline.total_bytes} to ${total} bytes.`
    );
  }

  return { errors, total };
}

export function validateBaselineChange(current, previous) {
  const errors = [];
  if (current.total_bytes > previous.total_bytes) {
    errors.push(
      `Legacy CSS baseline increases from ${previous.total_bytes} to ${current.total_bytes} bytes.`
    );
  }

  for (const [file, bytes] of Object.entries(current.components ?? {})) {
    const previousBytes = previous.components?.[file];
    if (previousBytes === undefined) {
      errors.push(`${file} adds a new legacy component CSS baseline entry.`);
    } else if (bytes > previousBytes) {
      errors.push(
        `${file} increases its legacy component CSS baseline from ${previousBytes} to ${bytes} bytes.`
      );
    }
  }

  for (const file of Object.keys(current.exception_files ?? {})) {
    if (!(file in (previous.exception_files ?? {}))) {
      errors.push(`${file} adds a new global CSS exception surface.`);
    }
  }

  return errors;
}

async function filesWithExtension(directory, extension) {
  const entries = await readdir(directory, { withFileTypes: true });
  const nested = await Promise.all(
    entries.map(async (entry) => {
      const path = resolve(directory, entry.name);
      if (entry.isDirectory()) return filesWithExtension(path, extension);
      return entry.isFile() && entry.name.endsWith(extension) ? [path] : [];
    })
  );
  return nested.flat();
}

export async function collectLegacyComponentCss(root = sourceRoot) {
  const files = await filesWithExtension(root, '.svelte');
  const entries = await Promise.all(
    files.map(async (file) => {
      const bytes = componentStyleBytes(await readFile(file, 'utf8'));
      return [relative(root, file).replaceAll('\\', '/'), bytes];
    })
  );
  return Object.fromEntries(entries.filter(([, bytes]) => bytes > 0));
}

export async function collectExceptionCss(root = frontendRoot) {
  const styles = await filesWithExtension(resolve(root, 'src'), '.css');
  const entries = await Promise.all(
    styles.map(async (file) => [
      relative(root, file).replaceAll('\\', '/'),
      Buffer.byteLength(await readFile(file))
    ])
  );
  return Object.fromEntries(entries);
}

export async function readBaseline(path = baselinePath) {
  return JSON.parse(await readFile(path, 'utf8'));
}

async function readBaselineAtRef(reference) {
  if (!/^(?:[0-9a-f]{7,40}|origin\/[A-Za-z0-9._/-]+)$/.test(reference)) {
    throw new Error(
      `Unsupported legacy CSS comparison reference: ${reference}`
    );
  }
  try {
    const { stdout } = await executeFile(
      'git',
      [
        'show',
        `${reference}:frontend/config/legacy-component-css-baseline.json`
      ],
      { cwd: frontendRoot }
    );
    return JSON.parse(stdout);
  } catch {
    return null;
  }
}

async function main() {
  const current = await collectLegacyComponentCss();
  const exceptionFiles = await collectExceptionCss();
  if (process.argv.includes('--print-baseline')) {
    console.log(
      JSON.stringify(
        {
          version: 1,
          description:
            'Maximum legacy CSS bytes for component-scoped Svelte styles and approved global exception surfaces.',
          exceptions: {
            global_styles: ['src/styles/app.css'],
            library_override_files: ['src/styles/library-overrides.css']
          },
          total_bytes:
            Object.values(current).reduce((sum, bytes) => sum + bytes, 0) +
            Object.values(exceptionFiles).reduce(
              (sum, bytes) => sum + bytes,
              0
            ),
          components: current,
          exception_files: exceptionFiles
        },
        null,
        2
      )
    );
    return;
  }

  const result = validateLegacyComponentCss(
    current,
    await readBaseline(),
    exceptionFiles
  );
  const reference = process.env.LEGACY_CSS_BASE_REF;
  if (reference) {
    const previous = await readBaselineAtRef(reference);
    if (previous) {
      result.errors.push(
        ...validateBaselineChange(await readBaseline(), previous)
      );
    }
  }
  if (result.errors.length) {
    console.error('Tailwind migration guardrail failed:');
    for (const error of result.errors) console.error(`- ${error}`);
    process.exitCode = 1;
    return;
  }

  console.log(
    `Tailwind migration guardrail passed: ${result.total} legacy component CSS bytes.`
  );
}

if (process.argv[1] === fileURLToPath(import.meta.url)) {
  await main();
}
