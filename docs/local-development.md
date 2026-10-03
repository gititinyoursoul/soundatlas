# Local Development

This document covers host development and the backend/frontend development
containers. The former workspace/devcontainer setup is retired.

## Component-container development

Install Docker with Compose v2 on the host. From the repository root:

```sh
docker compose up -d --build --wait
docker compose ps
```

Root Compose starts only `backend` and `frontend`, using their explicit `dev`
targets. The URLs are `http://localhost:5173` and `http://localhost:8000/health`.
No application secret or GitHub credential is needed. Editing and Git/GitHub
operations stay on the host or in the developer's chosen environment.

The backend contains Python, uv, pytest, ruff and pyright, plus Node as Pyright's
runtime (without npm or a runtime download). The frontend contains
Node/npm, Vite, Vitest, ESLint and Playwright-managed Chromium with its system
libraries. Chromium is installed at image-build time under `/opt/playwright`;
it does not depend on a workspace cache or a later browser download. Neither
component has a prod target. The frontend produces a static build; the existing
GitHub Pages deployment is unchanged.

Source edits are bind-mounted. Frontend seed and editorial inputs are mounted
read-only; generated data, build output and screenshots remain in ignored
frontend directories. Backend data/content mounts remain writable for existing
editorial operations. Container processes and validation run as `soundatlas`.

### Component checks and dependency refresh

```sh
docker compose exec --user soundatlas backend uv run ruff check .
docker compose exec --user soundatlas backend uv run pyright
docker compose exec --user soundatlas backend uv run pytest
docker compose exec --user soundatlas frontend npm run validate:pages
```

`validate:pages` runs frontend checks/tests and builds static data with the
`/soundatlas` base path. Output is `frontend/build`; generated data is under
`frontend/static/soundatlas-data`. Stop extra screenshot/preview processes
before building: Vite and builds share `.svelte-kit` in a given checkout.

After changing lockfiles, rebuild and explicitly refresh the mounted frontend
dependency volume. Its existing contents survive image rebuilds:

```sh
docker compose build
docker compose up -d --force-recreate --wait backend frontend
docker compose exec --user soundatlas frontend npm ci
docker compose restart frontend
```

The rebuild synchronizes backend dependencies in the image and installs the
Chromium revision matching the frontend lockfile. Do not update only npm
packages when the Playwright version changes; rebuild the browser image too.
Use `docker compose stop` to stop services. Do not delete volumes as routine
cleanup. Existing retired workspace containers/volumes are not removed by these
commands.

### Browser checks inside the frontend container

The normal Vite server uses `http://localhost:8000` for a browser on the host.
A browser inside the frontend container instead needs `http://backend:8000`.
The egress guard allows that exact destination while retaining the existing
private-network restrictions. It resolves the backend address at frontend
startup. After recreating the backend, wait for health and restart the frontend
to refresh the rule:

```sh
docker compose up -d --force-recreate --wait backend
docker compose restart frontend
```

For a dedicated browser check, stop the normal frontend and open a one-off
frontend container with its normal command replaced by a shell. The image
entrypoint applies the same egress policy and drops to `soundatlas`. This avoids
simultaneous Vite/build writers in the shared source directory:

```sh
# From the host, after stopping the normal frontend during a dedicated check:
docker compose stop frontend
docker compose run --rm --no-deps frontend sh
```

In the one-off container, dependencies and the backend must already be ready.
Create this temporary harness (ignored under `screenshots/`); it uses the
installed Playwright package, not a separate browser service:

```sh
mkdir -p screenshots
cat > screenshots/container-smoke.mjs <<'JS'
import assert from 'node:assert/strict';
import { chromium, expect } from '@playwright/test';

const mode = process.argv[2];
assert.ok(['api', 'static'].includes(mode));
const origin = mode === 'api' ? 'http://127.0.0.1:5174' : 'http://127.0.0.1:4173';
const url = mode === 'api' ? origin : `${origin}/soundatlas/`;
const failures = [];
const received = new Map();
let backendAttempts = 0;
const browser = await chromium.launch({ headless: true });
try {
  const context = await browser.newContext({ viewport: { width: 1440, height: 1000 } });
  await context.route('**/*', async (route) => {
    const requestUrl = new URL(route.request().url());
    const isBackend = requestUrl.origin === 'http://backend:8000';
    if (isBackend || ['8000', '18070'].includes(requestUrl.port)) backendAttempts += 1;
    if (requestUrl.origin === origin || (mode === 'api' && isBackend)) {
      return route.continue();
    }
    // External tiles/media never determine smoke-check success.
    return route.abort();
  });
  const page = await context.newPage();
  const paths = mode === 'api'
    ? ['/routes', '/events', '/places']
    : ['/soundatlas/soundatlas-data/routes.json',
       '/soundatlas/soundatlas-data/events.json',
       '/soundatlas/soundatlas-data/places.json'];
  page.on('requestfailed', (request) => {
    const requestUrl = new URL(request.url());
    if (paths.includes(requestUrl.pathname)) failures.push(request.url());
  });
  const responses = paths.map((path) => page.waitForResponse((response) => {
    const responseUrl = new URL(response.url());
    return responseUrl.pathname === path && responseUrl.origin ===
      (mode === 'api' ? 'http://backend:8000' : origin);
  }, { timeout: 20000 }).then(async (response) => {
    assert.ok(response.ok(), `${response.url()}: ${response.status()}`);
    received.set(path, await response.json());
  }));
  await Promise.all([page.goto(url, { waitUntil: 'domcontentloaded' }), ...responses]);
  const routesPayload = received.get(paths[0]);
  const eventsPayload = received.get(paths[1]);
  const routes = Array.isArray(routesPayload) ? routesPayload : routesPayload.routes;
  const events = Array.isArray(eventsPayload) ? eventsPayload : eventsPayload.events;
  assert.ok(routes.length && events.length, 'Expected route and event data');
  const inspector = page.getByRole('complementary', { name: 'Event inspector' });
  await expect.poll(async () => {
    const title = await inspector.locator('h2').textContent();
    return events.some((event) => event.title === title?.trim());
  }, { timeout: 20000 }).toBe(true);
  await page.screenshot({ path: `screenshots/${mode}-loaded.png` });
  await page.getByRole('button', { name: 'Open navigation', exact: true }).click();
  const drawer = page.getByRole('dialog', { name: 'Primary navigation' });
  await expect(drawer).toBeVisible();
  await expect(drawer.getByText(routes[0].title, { exact: true }).first()).toBeVisible();
  await drawer.evaluate(async (element) => {
    await new Promise(requestAnimationFrame);
    await Promise.all(element.getAnimations({ subtree: true }).map((a) => a.finished));
  });
  await page.screenshot({ path: `screenshots/${mode}-navigation.png` });
  await drawer.getByRole('button', { name: 'Collapse navigation', exact: true }).click();
  await expect(drawer).toHaveClass(/collapsed/);
  await drawer.evaluate(async (element) => {
    await new Promise(requestAnimationFrame);
    await Promise.all(element.getAnimations({ subtree: true }).map((a) => a.finished));
  });
  await page.screenshot({ path: `screenshots/${mode}-collapsed.png` });
  assert.deepEqual(failures, []);
  if (mode === 'static') assert.equal(backendAttempts, 0);
  else assert.ok(backendAttempts > 0);
  console.log(`${mode}: data, content and navigation passed`);
} finally {
  await browser.close();
}
JS
```

Run API and static phases sequentially. Shell PIDs below belong only to the
temporary servers started in this shell:

```sh
VITE_API_BASE_URL=http://backend:8000 ./node_modules/.bin/vite dev --host 127.0.0.1 --port 5174 --strictPort > /tmp/soundatlas-api.log 2>&1 &
api_pid=$!
# Wait until /tmp/soundatlas-api.log reports the server ready.
node screenshots/container-smoke.mjs api
kill "$api_pid"
wait "$api_pid" || true
npm run validate:pages
VITE_BASE_PATH=/soundatlas ./node_modules/.bin/vite preview --host 127.0.0.1 --port 4173 --strictPort > /tmp/soundatlas-static.log 2>&1 &
preview_pid=$!
# Wait until /tmp/soundatlas-static.log reports the server ready.
node screenshots/container-smoke.mjs static
kill "$preview_pid"
wait "$preview_pid" || true
exit
```

From the host, restore the ordinary frontend with `docker compose up -d frontend`.
The harness exits non-zero for missing data, failed required responses or
navigation assertions. Keep its captures as local evidence, not approved design
assets. The existing `npm run capture:drawer -- --output-dir=screenshots`
command remains available against a running port-5174 server, but launches its
own browser without interception. Its output is supplementary evidence only.

### Optional provider tasks

Normal startup and checks need no secrets. To run a provider task, mount only
its existing external application file read-only and select it explicitly.
For example, in a host Bash shell (substitute the actual absolute file path):

```sh
docker compose run --rm --no-deps \
  -v /absolute/external/soundatlas/.env:/run/secrets/soundatlas.env:ro \
  -e SOUNDATLAS_ENV_FILE=/run/secrets/soundatlas.env \
  backend uv run python scripts/run_youtube_search_requests.py --help
```

PowerShell accepts the same arguments on one line. On Windows quote the complete
`-v` argument containing the drive path. The example only displays help; replace
the task command intentionally. Do not mount the secret root or supply GitHub
credentials to application tasks. An empty or synthetic file is sufficient to
check delivery without live provider calls. See the
[credential contract](development-credentials.md) for selection and failures.

### Isolated migration validation

For infrastructure changes, validate from a separate working copy containing the
exact candidate tracked files and deletions. Record the base revision plus a
candidate diff/manifest. Do not copy real credentials, node_modules, caches or
generated output. Use a unique Compose project, fresh dependency volumes and
alternate host ports. Resolve `docker compose config` before starting: every
bind source and build context must refer to the validation copy, never the
active development checkout. Match the normal Vite API URL to the alternate
published backend port when checking the host path.

A project name alone does not isolate source mounts or `.svelte-kit`. Run build
and browser phases sequentially. Verify changed-backend-IP recovery in this
isolated project: recreate the backend on a different address using a temporary
network override, wait for health, restart the frontend and repeat API smoke.
Record old/new addresses and the refreshed destination rule. Reusing the same
IP proves recreation only, not changed-address recovery. Preserve user-owned
containers and volumes; stop only the validation resources you created.

## Prerequisites

Install the following tools on the host:

- Python `>=3.13`
- `uv`
- Node.js and npm
- Bash for `scripts/setup-dev.sh` and `scripts/start-dev.sh`, or PowerShell
  for the `.ps1` scripts

## First-time setup

Run the setup script from the repository root. It installs the backend and
frontend dependencies from their lockfiles.

PowerShell:

```powershell
.\scripts\setup-dev.ps1
```

Bash:

```sh
./scripts/setup-dev.sh
```

Run the setup script again after changing either dependency lockfile.

## Start the application

PowerShell:

```powershell
.\scripts\start-dev.ps1
```

Bash:

```sh
./scripts/start-dev.sh
```

The scripts start both services and stop them together when the process ends.

Default URLs:

- Frontend: `http://127.0.0.1:5173`
- Backend: `http://127.0.0.1:8000`
- Health: `http://127.0.0.1:8000/health`

The Bash start script accepts `--backend-port` and `--frontend-port` when the
default ports are already in use.

## Editorial review mode

The normal development server is the public explorer. To inspect a generated
route review through the existing map, timeline, navigation drawer, and
StoryPanel, start the frontend with `VITE_EDITORIAL_MODE=true` while using the
API data path. The flag is opt-in and defaults to public mode; static data mode
does not expose editorial controls. Review state changes are sent to the
backend review API and require its current revision. Editorial mode renders the
seed-shaped event, place, and connection content bound to that revision through
the same StoryPanel used publicly; planning fields and warnings remain in the
separate event review-tools area. Route publication is available from the
navigation drawer's Route Review panel. That panel summarizes included-event
warning and blocking-error counts; full event findings stay with the selected
event, while full route-only blocking errors and collapsed route-level warnings
remain in Route Review.

## Checks

Run backend checks from `backend/`:

```sh
uv run ruff check .
uv run pyright
uv run pytest
```

Run frontend checks from `frontend/`:

```sh
npm run validate
```

For larger frontend changes that also need a production build, run
`npm run validate:release` instead.

To validate the GitHub Pages deployment mode locally, run:

```sh
npm run validate:pages
```

This uses the same static-data mode and `/soundatlas` base path as Frontend CI.

Optional coverage reports:

```sh
cd backend
uv run pytest --cov

cd ../frontend
npm run test:coverage
```

## Troubleshooting

- If frontend installation fails with an npm lockfile synchronization error,
  resolve the dependency change intentionally and rerun the setup script.
- If a service port is already in use, pass alternate ports to the Bash start
  script or use the corresponding parameters of the PowerShell script.
