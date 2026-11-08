# Persistent local foundation — task handoff

- Request: keep stable shared sources locally after one-time pinning; recalibrate
  when they change. This authorizes a small persistent foundation, not local brand
  archival, cloud migration, deletion of legacy files, or creative approval.
- Executor: OpenCode, local macOS. No delegated agents, image/model calls, rendering,
  dependency install, global config edits or credential transfer.
- Task branch: `publish/opencode-local-baseline-20261010`.
- Base main SHA: `a46cf9b9f74d5728b74b88ec447e89c9c2268e89`.
- Scope: `AGENTS.md`, `studio/work/ephemeral.py`, its real-Git fixture tests,
  `studio/work/BASELINE.md`, work guides, publishing procedure and this handoff.
  No changes to brands, delivery bundles, canonical logos, policies or existing PRs.
- Implementation: owned private persistent source snapshots outside the temporary
  task root; committed main tree identity + per-file Git blob/SHA-256/mode manifest;
  immutable snapshots, recorded launcher refresh, independent task object import.
  Main task startup calibrates automatically. Explicit publish-branch handoffs
  cannot promote their instructions to the persistent main baseline.
- Actual local installation: default `~/.local/share/brand-studio/baseline/`.
  Before this PR merges, the installed snapshot/launcher deliberately contains only
  existing committed main sources, not this unmerged implementation.
- Live GitHub calibration evidence on the base SHA:
  - First: 110 files, 110 loaded source blobs, zero reused.
  - Second: identical digest, zero loaded source blobs, 110 reused.
  - Digest: `0f26b91d1cf4ffec6f8759a510bd02116e6a671848d538e38c2f66c9c537b211`.
- Checks: 72 work tests and 14 cloud checker tests passed on macOS/Python 3.14;
  GitHub's independent audit uses its pinned Python 3.12. Source audit PASS:
  15 canonical records, unchanged five-slide delivery/package, 1307 existing
  tracked text files scanned. Existing Asya'da Eğitim preflight passed (16 locked
  sources); no full-system approval inferred and no rendering prerequisites claimed.
  Initial sparse-checkout missing-file failures were resolved by materializing
  audit-required text/assets and the preservation baseline history, not by
  weakening/skipping tests. This infrastructure is not a branded bundle, so no
  new cloud-policy bundle registration is needed.
- Tested guards: local snapshot/launcher edits, mode/type mismatch, symlinks,
  unowned/wrong-repository storage, source deletion, committed rollback, offline
  failure, task isolation, cleanup preservation and unchanged-source reuse.
- Delivery: inspect CI on the exact PR HEAD, recheck main, checked merge under
  standing policy, verify merged files, then calibrate the local baseline to
  install this new main launcher. Exact CI/head/merge evidence lives in the PR.
- Remaining constraints: network/tree metadata and brand inputs still fetched;
  final preservation proof still uses an independent fresh remote store. Server
  filter support affects download volume. Old tiny snapshots are retained without
  automatic pruning. Launcher/active-record interruptions fail closed. Codex host
  persistence/account activation has not been exercised; no Mac cache sharing.
- Temporary task cleanup is separate and only after exact remote-byte and CI
  verification; legacy `Design` remains unchanged.
