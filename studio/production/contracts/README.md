# Brandstudio 3.0 P1 — versioned contracts (advisory only)

The approved design is in `docs/superpowers/specs/2026-11-02-brandstudio-multi-agent-v3-design.md`. P1 adds a read-only protocol, **not** new production, image generation, browser render, review approval, publishing or server components. Existing Visual Editor, design-by-code HTML/CSS/SVG, render, catalog, publication tracker and backups stay unchanged.

## Four portable records

- `TaskSpec` (task.schema.json): version 1, pinned source commit, exact brand, safe brief reference, category, output subtree, allowed executors, required capabilities, zero-new-paid-API budget and pending creative approval.
- `CapabilityReport`: observed environment capabilities with declared evidence, or unknown. An observed tool is **a caller report, not independent remote attestation**; advisory rejects missing evidence. `model_id=null` means unknown.
- `TaskReceipt`: what an executor actually produced / attempted, including commit refs and failure codes. No automatic Github claims or real model execution in P1.
- `OutputManifest`: editable sources, real render references and SHA256, manifest-listed lockup, observed checks and a separate human approval reference. A prepared manifest can have unchecked checks; technical verified requires all checked.

All records are JSON Schema Draft 2020-12 validated and have a strict `schema_version=1`. Unknown fields/versions are rejected; changes to breaking fields require a new schema version. Public contracts contain no raw brief, secret, signed link or provider token. Use `private:<safe-id>` only when an authorized private store actually exists; P1 does not create one.

## Offline commands

Use a temporary Python environment (Python 3.12 recommended):

```sh
python3 -m pip install -r studio/production/contracts/requirements.txt
python3 studio/production/contracts_cli.py validate --kind task --file studio/production/tests/fixtures/contracts/task-valid.json --root .
python3 studio/production/contracts_cli.py route --task studio/production/tests/fixtures/contracts/task-valid.json --report studio/production/tests/fixtures/contracts/capability-opencode.json --root .
python3 studio/production/contracts_cli.py transition --from creative_review --to accepted --actor human --evidence-ref review:approval-001
python3 -m unittest discover -s studio/production/tests -v
```

The CLI returns `P1_INVALID_INPUT` for invalid inputs without reproducing their sensitive content. Its transition command proposes a transition; **does not persist it or prove someone approved it**. “CI success” does not count as an aesthetic/human approval. There is no automatic fallback to another executor/provider.

## Two executor examples

`capability-opencode.json`: local filesystem + terminal observed; can propose `opencode-code-v1` for the example TaskSpec. `capability-work.json`: only GitHub read observed and filesystem unknown; the same TaskSpec needs filesystem and **must return `eligible:false`** even though Work is named in `allowed_executors`. If Work really has filesystem capability, its host must provide an observed evidence report before it can be eligible. No external agent is started by this contract.

## Compatibility, privacy and migration

- Existing `studio/production/router.py` remains unchanged, reports `read-only-dry-run`, `candidate-not-benchmarked`; the new `advisory.propose` wraps it without reconfiguring agents.
- Existing `studio/production/recording/` private evidence ledger stays separate (P1's `TaskReceipt` is portable interchange; it does not replace observed recorder evidence).
- Only P1 source and CI tests were added; no edits to Visual Editor/browser source, legacy designs, Workers, Pages or D1. If necessary, revert P1 paths; legacy router remains operational.
- Future P2 implements actual two-executor handoff and per-task branch/PR transactions; P3 addresses real browser visual QA. P1 never declares live activation or human creative approval.
