import { copyFile, mkdir } from 'node:fs/promises';
import path from 'node:path';
import { fileURLToPath } from 'node:url';

const scriptDir = path.dirname(fileURLToPath(import.meta.url));
const repoRoot = path.resolve(scriptDir, '..', '..');
const sourceDir = path.join(repoRoot, 'data', 'seed');
const targetDir = path.join(repoRoot, 'frontend', 'static', 'soundatlas-data');
const seedFiles = ['routes.json', 'places.json', 'events.json', 'connections.json'];

await mkdir(targetDir, { recursive: true });

await Promise.all(
  seedFiles.map((fileName) => copyFile(path.join(sourceDir, fileName), path.join(targetDir, fileName)))
);

console.log(`Generated static SoundAtlas data in ${path.relative(repoRoot, targetDir)}`);
