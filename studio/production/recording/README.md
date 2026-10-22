# Brandstudio Production Recorder v1

A **stdlib-only** provenance ledger shared by regular ChatGPT, Work, Codex
and other coding agents. This is NOT an automatic token meter, screenshot checker,
render engine, or GitHub plugin.

## What it records

- Unique run ID, exact source commit SHA, route/strategy, brand and category.
- Executor, requested thinking effort (never claimed as verified), optional
  model ID supplied with a declared host/provider metadata source.
- Event kinds/timestamps and on-disk artifact SHA-256 hashes.
- Optional observed token figures with a declared observation source.
  **Null means unavailable**, not zero. No guessed quotas or cost.
- Optional GitHub PR/head/check/merge attestation marked **reported by caller**.
- Elapsed calendar wall-clock, *not* provider model-execution duration.

The raw brief is NOT stored. An optional brief-file contributes only a private
SHA-256 digest; even that digest is omitted from the public summary.

## Public repository warning

`cinegitim/design` is PUBLIC. Private run files must be inside
`.brandstudio-private/` (gitignored), never committed to Git or Pages.
The public summary is allowlisted, but must still be reviewed before committing.
The recorder does not itself call GitHub or independently verify supplied
model IDs, PR data, token observations, or remote deployments.

## Minimal dry-run example

From an isolated checkout with Python 3.11+:

```sh
MAIN_SHA=$(git rev-parse main)   # check this against remote main first
python3 studio/production/recording/recorder.py init \
  --file .brandstudio-private/demo.json \
  --brand asyada-egitim --category instagram-carousel \
  --executor chatgpt-chat --route chatgpt-connected-v1 \
  --source-commit "$MAIN_SHA"
python3 studio/production/recording/recorder.py event \
  --file .brandstudio-private/demo.json --kind repo-read
python3 studio/production/recording/recorder.py finish \
  --file .brandstudio-private/demo.json --status planned
python3 studio/production/recording/recorder.py export \
  --file .brandstudio-private/demo.json --output /tmp/brandstudio-public.json
python3 studio/production/recording/recorder.py validate \
  --file .brandstudio-private/demo.json
```

The example does NOT generate a design or claim delivery.

## Evidence-only optional commands

- `artifact --file PRIVATE --root CHECKOUT --path docs/.../output.svg`:
  compute real file hash, reject symlinks/traversal/out-of-repo paths.
- `metrics --file PRIVATE --source provider-usage --input-tokens N`:
  only when those numbers were genuinely reported. Otherwise omit.
- `model --file PRIVATE --model-id NAME --source host-metadata`:
  label observed host/provider metadata, NOT independent verification.
- `delivery --file PRIVATE --pr-number N --head-sha SHA
  --checked-head-sha SHA --ci-status success`:
  requires the caller to have checked exact-head GitHub CI; matching SHAs
  are validated but no GitHub API call is made by recorder.
- `finish --file PRIVATE --status finished`:
  requires at least one locally hashed artifact; not proof of social posting.
- `export --file PRIVATE --output PUBLIC.json`:
  explicit public-safe fields; refuses to overwrite existing output.

**Normal ChatGPT with only GitHub connectors:** do not claim this Python
program ran in a checkout. Capture verified GitHub evidence through
connected tools and prepare a compatible public-safe summary manually;
unavailable model tokens and local artifact hashes remain null/unverified.
A future host-native collector can automate the bridge.

## Test

```sh
python3 -m unittest discover -s studio/production/tests -v
```

Follow the existing AGENTS.md and PUBLISHING.md. A CI green result does not
constitute human aesthetic approval or confirmation of public deployment.
