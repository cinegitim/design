# Agent-source merge policy proposal — 2026-10-10

- Executor: OpenCode, local macOS; new manager-owned isolated task clone.
- Brand: none; agent configuration source only, no branded assets changed.
- Base: `11731285ffb8d518d2de17b568697da16ddf25b8`.
- Branch: `publish/opencode-merge-policy-source-20261010`.
- User request: change the merge-confirmation instruction in the repository's
  `.opencode/agents/brand-director.md` source.
- Delta: propose PR → exact-head required checks → lossless technical conflict
  fixes → rerun checks → merge without an additional confirmation → verify live
  deployment. Preserve branch protection and human creative/locked-artwork gates.
- Scope/activation: this is a source proposal, NOT a change to the active session's
  higher-priority instructions. Root AGENTS, publishing procedure, Work/Codex
  adapters and commands still require per-PR authorization. They must be reconciled
  in a separately reviewed policy migration before enabling the proposed behavior.
  The ephemeral CLI currently accepts only an OPEN PR for cleanup, so a future
  merge-before-cleanup pipeline also needs a tested cleanup-gate migration.
- Checks: source read-back/diff validation; existing documentation, preflight and
  ephemeral tests; GitHub independent submitted-file audit for this exact PR head.
  No image/model generation, campaign rebuild, logo changes or deployment claimed.
- Delivery: open PR. Active rules still require explicit authorization for this
  specific PR; editing the agent source neither authorizes its merge nor changes
  instructions already loaded into this conversation. No force-push or auto-merge.
