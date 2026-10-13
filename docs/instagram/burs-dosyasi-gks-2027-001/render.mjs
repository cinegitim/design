#!/usr/bin/env node
// Render one Burs Dosyası / 001 slide with headless Chrome.
// Usage: node render.mjs <slide-number 1..6> [output.png]
// Renders source/NN.html (the inline-SVG master wrapper) at 1080x1350.
import { spawn } from 'node:child_process';
import { existsSync, statSync } from 'node:fs';
import { resolve, dirname } from 'node:path';
import { fileURLToPath } from 'node:url';

const here = dirname(fileURLToPath(import.meta.url));
const n = String(process.argv[2] ?? '1').padStart(2, '0');
const out = resolve(process.argv[3] ?? resolve(here, 'export', `${n}.png`));
const src = resolve(here, 'source', `${n}.html`);
const chrome = process.env.CHROME ?? '/Applications/Google Chrome.app/Contents/MacOS/Google Chrome';
if (!existsSync(src)) { console.error('missing source:', src); process.exit(1); }
const args = ['--headless=new','--disable-gpu','--hide-scrollbars','--no-first-run',
  '--force-device-scale-factor=1','--window-size=1080,1350','--virtual-time-budget=9000',
  `--user-data-dir=${resolve(here, '.chrome-profile')}`, `--screenshot=${out}`, `file://${src}`];
const proc = spawn(chrome, args, { stdio: 'ignore', detached: true });
const deadline = Date.now() + 45000;
(function poll() {
  if (existsSync(out) && statSync(out).size > 10000) {
    try { process.kill(-proc.pid, 'SIGTERM'); } catch {}
    console.log('rendered', out); process.exit(0);
  }
  if (Date.now() > deadline) { try { process.kill(-proc.pid, 'SIGKILL'); } catch {} console.error('timeout'); process.exit(1); }
  setTimeout(poll, 200);
})();
