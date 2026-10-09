#!/usr/bin/env bash
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/../.." && pwd)"
cd "$ROOT"
python3 -c 'import sys; assert sys.version_info[:2] == (3,12), "Select Python 3.12 in the cloud environment"'
node -e 'if(process.versions.node.split(".")[0]!=="22")throw Error("Select Node 22 in the cloud environment")'
if ! command -v rsvg-convert >/dev/null; then
  if command -v apt-get >/dev/null && command -v sudo >/dev/null; then
    sudo apt-get update
    sudo apt-get install -y librsvg2-bin
  else
    echo "Install librsvg2-bin in the cloud VM; this script does not configure macOS." >&2
    exit 1
  fi
fi
mkdir -p "$HOME/.cache/brand-studio"
python3 -m venv .venv
.venv/bin/python -m pip install --disable-pip-version-check -r studio/cloud/requirements.txt
npm ci --prefix studio/cloud --ignore-scripts --no-audit --no-fund
node studio/cloud/install-browser.mjs
bash studio/cloud/doctor.sh
echo 'Environment installed. No campaign outputs or images were generated.'
