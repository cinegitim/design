#!/bin/sh
# Verify a final branded output against the canonical logo lock.
#
# Every branded output must record the canonical logo hash it used. This script
# is the mechanical check: it confirms the canonical asset is byte-identical to
# the approved file, and prints the hash to record in the output manifest.
#
# Usage:
#   studio/tools/verify-canonical-logo.sh                 # verify + print hash
#   studio/tools/verify-canonical-logo.sh --manifest FILE # append a manifest line
#
# Exit 0 = canonical asset intact. Exit 1 = TAMPERED. Exit 2 = missing.

set -eu

REPO_ROOT=$(cd "$(dirname "$0")/../.." && pwd)
CANONICAL="$REPO_ROOT/brands/asyada-egitim/assets/v01-canonical.svg"
EXPECTED="8f5d46f0302c4cc7e3765d3bfce9445f842dbd92f1e0f8fbe99f9f509c77e11a"
SLUG="asyada-egitim"

if [ ! -f "$CANONICAL" ]; then
  echo "FAIL  canonical asset missing: $CANONICAL" >&2
  exit 2
fi

ACTUAL=$(shasum -a 256 "$CANONICAL" | cut -d' ' -f1)

if [ "$ACTUAL" != "$EXPECTED" ]; then
  echo "FAIL  canonical logo has been modified." >&2
  echo "      expected $EXPECTED" >&2
  echo "      actual   $ACTUAL" >&2
  echo "      The V-01 logo is LOCKED. Restore it from git:" >&2
  echo "      git checkout main -- brands/asyada-egitim/assets/v01-canonical.svg" >&2
  exit 1
fi

LINE="canonical_logo_sha256=$ACTUAL"

if [ "${1:-}" = "--manifest" ] && [ -n "${2:-}" ]; then
  printf '%s\n' "$LINE" >> "$2"
  echo "OK    $LINE -> $2"
else
  echo "OK    canonical logo intact"
  echo "      path    brands/$SLUG/assets/v01-canonical.svg"
  echo "      $LINE"
fi

exit 0