#!/usr/bin/env bash
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/../.." && pwd)"
cd "$ROOT"
test -x .venv/bin/python || { echo 'Run studio/cloud/setup.sh first' >&2; exit 1; }
.venv/bin/python -c 'import sys, PIL, fontTools, numpy, cv2; print("Python",sys.version.split()[0],"Pillow",PIL.__version__,"fonttools",fontTools.__version__,"numpy",numpy.__version__,"OpenCV",cv2.__version__)'
node --version
rsvg-convert --version
node --input-type=module <<'JS'
import{createRequire}from'node:module';import{existsSync}from'node:fs';
const require=createRequire(process.cwd()+'/studio/cloud/package.json');
const {chromium}=require('playwright-core');
const exe=chromium.executablePath();if(!existsSync(exe))throw Error('Missing pinned Chromium');
const browser=await chromium.launch({headless:true});
const page=await browser.newPage();await page.setContent('<h1>Cloud render smoke test</h1>');
if(await page.locator('h1').textContent()!=='Cloud render smoke test')throw Error('Browser smoke test failed');
console.log('Headless Chromium:',await browser.version());await browser.close();
JS
python3 studio/cloud/audit.py --root .
echo 'Tool smoke test passed. Codex account activation and image connectors are separate checks.'
