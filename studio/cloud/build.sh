#!/usr/bin/env bash
# Production entrypoint. Do not call from GitHub Actions.
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/../.." && pwd)"
cd "$ROOT"
case "${1:-}" in
  launch-creative-02) DIR='docs/instagram/launch-creative-02' ;;
  *) echo 'Usage: bash studio/cloud/build.sh launch-creative-02' >&2; exit 2 ;;
esac
test -x .venv/bin/python || { echo 'Run studio/cloud/setup.sh first' >&2; exit 1; }
export PATH="$ROOT/.venv/bin:$PATH"
export PLAYWRIGHT_MODULE="$ROOT/studio/cloud/node_modules/playwright-core"
# Managed, pinned Playwright browser; no dependency on /Applications or a user's Chrome.
export CHROME_PATH="$(node --input-type=module -e 'import{createRequire}from"node:module";const r=createRequire(process.cwd()+"/studio/cloud/package.json");console.log(r("playwright-core").chromium.executablePath())')"
unset DRAFT_RENDER
mkdir -p "$HOME/.cache/brand-studio"
python3 "$DIR/build.py"
python3 "$DIR/verify_and_package.py"
python3 studio/cloud/audit.py --root .
echo 'Build completed; inspect images and open a PR. This is not visual approval.'
