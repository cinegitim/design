# Legacy Design — explicitly authorized bulk-file pruning

- Executor: OpenCode, local macOS, independent disposable task clone. No agents
  delegated; no image/model calls, rendering, social publication or credential transfer.
- Human authorization: user confirmed the exact original `Design` folder, then
  narrowed the request to bulky files while permitting small necessary files to
  remain. This is separate explicit legacy-deletion permission, not CI-derived consent.
- Task branch: `publish/opencode-legacy-design-prune-20261010`.
- Base/pinned archive main SHA: `f5c011eade436699aea4c1467da0c72c69c7e6a2`.
- Legacy target HEAD retained: `11731285ffb8d518d2de17b568697da16ddf25b8`.
- Paths: `studio/work/legacy_bulk_prune.py`, its real-Git isolation/rejection tests,
  `studio/work/LEGACY-PRUNE.md`, this round's verified per-file plan and result.
  No GitHub brand originals, bundles, canonical artwork, policies or other PRs changed.
- Proof: 332 distinct source blobs fetched from GitHub into the independent task
  object store; Git blob identity and independently computed SHA-256 matched all
  635 selected local regular raster/package files. The source shares no Git store
  or alternates with the legacy root. Per-file archive paths and hashes are in
  `verified-plan.json`; this is not a hash claim inferred from local Git status.
- Applied: 635 files, 1,396,608,389 logical bytes removed. Exact-file sparse rules
  omit archived tracked files, and verified ignored duplicates were unlinked one
  by one. No broad recursive deletion, branch checkout/reset, stash drop or remote
  deletion. Local Git remains clean, preventing accidental GitHub asset removal.
- Retained: original AGENTS.md and small sources; shared `.git` (about 829 MiB),
  all branches/stash, five existing linked worktrees and their clean statuses,
  active share/share-seal/share-runtime paths (about 431 MB of bulky preview
  assets), dependencies/config, Figma layer and the private persistent baseline.
- Retained exceptions: 102,907,227-byte `asya-egitim-site.zip` has no exact archived
  container blob in pinned main; equivalent-entry archival is not called exact
  container preservation. Two large embedded HTML source boards also remain.
- Observed legacy folder size: approximately 2.8 GiB before / 1.5 GiB after.
  Logical removed bytes and disk allocation are different metrics.
- Safety: fresh local hashes/identity/mode and full proof set rechecked before
  applying. Added dependency/cache protection before apply; no selected candidate
  belonged to those roots. Active preview servers were not stopped or deprived of
  their own files. Other worktree pending-change counts remained zero.
- Tool note: initial read-only verification exceeded a foreground timeout; no
  files had been deleted. Verification completed in a background run with explicit
  completion notification. The apply command completed successfully in foreground.
- Checks: all 81 work tests (including nine new real-Git pruning rejection/isolation
  cases), 14 existing cloud checker tests, local independent file audit (1315
  tracked text files, unchanged five-slide package and 15 canonical records), and
  the existing 16-source locked-identity preflight passed. No render readiness or
  aesthetic approval inferred. This infrastructure/evidence is not a new bundle,
  so cloud-policy registrations remain unchanged.
- Delivery: exact-head independent GitHub audit, checked merge under standing policy,
  then merged file/hash verification and local shared-source baseline calibration.
  This is repository-only evidence/tooling, not a new public application bundle.
- Future work: use independent disposable clones. Non-active legacy boards may
  reference locally omitted imagery, but GitHub/Pages originals are unchanged.
  Sparse disable restores tracked assets and defeats the saving. This request does
  not authorize deleting other worktrees, global caches/auth or the shared `.git`.
