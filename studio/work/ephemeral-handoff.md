# Ephemeral workspace implementation — 2026-10-10

- Executor: OpenCode, existing local macOS tool host. No remote VM, no RAM disk.
- Task: implement one reusable temporary root per host, isolated disposable task
  clones, shared GitHub handoff and conservative verified completion cleanup.
- Branch: `publish/opencode-ephemeral-workspaces-20261010`.
- Original main: `a7af288a77a32032e2f83383b4e3c48595cb4463`; inherited PR #74's
  dual-producer documentation via cherry-pick, then replaced its remote-first
  guidance with the user's later temporary-local choice. This PR supersedes #74;
  neither is merged/closed automatically. Main advanced concurrently through #73;
  integrate that main without modifying its China's-brand artwork.
- Sources: existing AGENTS, delivery adapters, publishing policy, cloud audit and
  recorded user intent. No third-party image generation, build or campaign revision.
- Outputs: `ephemeral.py`, `EPHEMERAL.md`, real-Git local-remotes tests, updated
  executor/docs/cloud guidance. No change to bundle policy or independent CI checker.
- Installed locally: one private owned temporary root, launcher in `control/`,
  empty `tasks/`, metadata in `records/`. Init is idempotent. This small control
  state intentionally survives task cleanup; OS temp retention is not permanent.
- Verification: 43 ephemeral tests + 4 contract tests + 10 preflight tests passed;
  14 cloud audit tests passed; independent bundle/source audit passed (15 canonical
  records, existing five-slide package hash unchanged). Task-branch preflight
  checked 16 approved source files. Full Pillow-dependent logo verifier was not
  available under isolated Python; no logo production performed. Hash audit and
  preflight passed without that dependency; do not call this a new visual logo approval.
- Tests exercise actual local Git clone/push/fresh fetch/byte proof/cleanup and
  sparse retrieval, ignored/dirty/staged/unpushed files, symlinks, modes, legacy
  preservation, CI-head gate, stash/reflog/branch retention, task collisions and
  explicit OpenCode→Codex-style branch handoff. GitHub PR/CI gate scenarios are
  mocked unit tests; execution label `codex` in a local fixture is a simulation,
  NOT an actual Codex cloud-account activation or native image connector test.
- Review: fixed initial no-checkout clone's empty-index behavior by checking out
  the explicit fetched base; bound cleanup proof to the CI-reviewed SHA; guarded
  unreconciled reflog work and legacy/source stores; runtime exclusion opt-in only.
- Docs preview: actual Chromium renders at 375/1440px inspected, single h1 and
  no horizontal overflow. Hierarchy 9, consistency 9, aesthetics 8, usability 8.
  Visible delta: temporary-local choice and safe cleanup replace VM-first guidance.
- Safety: task cleanup is explicit completion, no daemon; caller must stop writers
  and move out of task. Only manager-owned independent clones may be deleted.
  Existing bootstrap worktrees/legacy folders are retained, not retroactively adopted.
  Global OpenCode/auth/model/tool caches are outside scope. No secure-erase promise.
- Remaining limits: Linux/Codex account run not verified here; unsupported LFS,
  submodules and Release-only files block cleanup. Failed network/CI or unique
  ignored/uncommitted work leaves task files intact. Concurrency lock serializes
  manager commands but cannot freeze arbitrary editors. No blanket zero-local-data
  or token-saving guarantee. Review/download/export uses ordinary local memory/disk.
- Human gates: implementation requested; no authorization to merge this PR,
  remove old local archives, approve new artwork or post to social media.
- Delivery: open PR + exact-head independent submitted-file CI. Publication pending;
  existing Pages stays unchanged until explicit authorization for this PR.
