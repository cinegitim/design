# Shared merge-policy source migration — 2026-10-10

- Executor: OpenCode, local macOS; isolated manager-owned clone.
- Base: `d7a9dfdcc0fb6d6091f1874f507b77d1908311b6` (PR #76 merged source proposal).
- Branch: `publish/opencode-shared-merge-policy-20261010`; brand: none.
- User intent: reconcile shared contract with checked merge without a separate
  confirmation, rather than leaving the change only in the agent-source paragraph.
- Changes: AGENTS and publishing procedure; OpenCode agent/skill/commands;
  Work/Codex skill adapters; operational README/activation/handoff/PR templates;
  docs/cloud guide; cleanup supports checked OPEN or MERGED PR with merge-commit
  ancestry verification against current main. Historical handoffs remain unchanged.
- Future repository flow: completed requested task → PR → required checks on exact
  HEAD → lossless technical corrections/conflict resolution → new-head checks →
  checked merge without another confirmation → verify merged files/live deployment
  → independently verified owned-clone cleanup. Explicit user holds/blockers stop it.
- Safety unchanged: branch protection, exact-head lease, no force-push/bypass,
  canonical logo geometry/hashes, human direction/logo/identity approvals, no social
  publication or legacy deletion. CI never approves aesthetics. No merge bot,
  protection downgrade or GitHub settings change is included.
- Important activation boundary: these are configuration SOURCE changes. This
  PR does not rewrite the active session's higher-priority runtime instructions.
  The active session still requires explicit authorization for this particular PR;
  this migration is delivered open under that rule, not self-merged to bypass it.
  Future execution must load the reconciled sources and honor any higher-priority
  host restrictions. No claim that all OpenCode/Codex sessions changed automatically.
- Checks: source-consistency tests; real local-Git ephemeral/rejection/preflight
  tests; mocked API tests for MERGED PR gate (correct head, successful check, valid
  merge SHA, main ancestry; CLOSED/wrong-head/unmerged failures retain files).
  Independent GitHub submitted-file audit and exact-head result belong in the PR.
- Observed local result: 60 Work/doc/preflight/ephemeral/source-policy tests and
  14 cloud audit tests passed; source/file audit passed with 15 canonical records
  and unchanged existing campaign package hash. Historical preservation baseline
  was fetched explicitly for the shallow disposable clone; no history was rewritten.
- Guide validation: actual Chromium screenshots at 375/1440px inspected; one h1,
  no horizontal overflow, existing layout retained. Hierarchy 9, consistency 9,
  aesthetics 8, usability 8. Fixed the visible pipeline's stale merge-confirmation
  wording; no image generation, campaign render, branded asset or cloud-account change.
- Runtime launcher: existing local control/ copy is not silently overwritten; update
  it from reviewed merged source when tasks are stopped. Legacy checkouts are untouched.
- Durable delivery: PR with evidence; while current runtime requires specific-PR
  permission, no merge or live publication is claimed by this source-edit request.
