import { mkdir } from 'node:fs/promises';
import path from 'node:path';
import process from 'node:process';
import { chromium } from '@playwright/test';

function readArg(name, fallback) {
  const prefix = `${name}=`;
  const arg = process.argv.find((value) => value.startsWith(prefix));
  return arg ? arg.slice(prefix.length) : fallback;
}

const url = readArg('--url', 'http://127.0.0.1:5173');
const outputDir = path.resolve(readArg('--output-dir', '../screenshots'));
const width = Number(readArg('--width', '1440'));
const height = Number(readArg('--height', '1000'));
const openSelector = readArg('--open-selector', 'button[aria-label="Open navigation"]');
const collapseSelector = readArg('--collapse-selector', 'button[aria-label="Collapse navigation"]');
const closedName = readArg('--closed-name', 'drawer-closed-desktop.png');
const expandedName = readArg('--expanded-name', 'drawer-expanded-desktop.png');
const collapsedName = readArg('--collapsed-name', 'drawer-collapsed-desktop.png');
const routesName = readArg('--routes-name', 'drawer-routes-desktop.png');
const settleDelayMs = Number(readArg('--settle-delay-ms', '200'));

if (!Number.isFinite(width) || !Number.isFinite(height)) {
  throw new Error('Viewport width and height must be numbers.');
}

await mkdir(outputDir, { recursive: true });

const browser = await chromium.launch({ headless: true });
const page = await browser.newPage({ viewport: { width, height } });

try {
  await page.goto(url, { waitUntil: 'networkidle' });
  await page.locator('main.app-shell').waitFor();
  await page.screenshot({ path: path.join(outputDir, closedName) });

  const drawer = page.locator('div[role="dialog"][aria-label="Primary navigation"]');

  await page.locator(openSelector).click();
  await page.waitForFunction(
    (selector) => document.querySelector(selector)?.getAttribute('aria-expanded') === 'true',
    openSelector
  );
  await drawer.waitFor({ state: 'visible' });
  await page.waitForTimeout(settleDelayMs);
  await page.screenshot({ path: path.join(outputDir, expandedName) });

  const routesButton = page.locator('button[aria-label="Routes"]');
  if (await routesButton.isVisible()) {
    await routesButton.click();
    await page.waitForTimeout(settleDelayMs);
  }

  await page.screenshot({ path: path.join(outputDir, routesName) });

  const collapseButton = page.locator(collapseSelector);
  if (await collapseButton.isVisible()) {
    await collapseButton.click();
    await page.waitForTimeout(settleDelayMs);
  }

  await page.screenshot({ path: path.join(outputDir, collapsedName) });

  console.log(`Captured drawer screenshots in ${outputDir}`);
} finally {
  await browser.close();
}
