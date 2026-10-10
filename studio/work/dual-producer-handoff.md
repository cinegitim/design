# Dual producer policy handoff — 2026-10-10

- Executor: OpenCode, existing local macOS tool host; isolated checkout/branch.
  This administrative change is **not** remote OpenCode execution or a cloud cutover.
- Task: authorize both OpenCode and Work/Codex production; explain how to avoid a
  project checkout on the user's machine without mistaking GitHub for a render host.
- Base: `a7af288a77a32032e2f83383b4e3c48595cb4463`.
- Branch: `publish/dual-producer-policy`.
- Scope: shared AGENTS/README, delivery skill, cloud recipe metadata, activation
  guide, remote OpenCode architecture, `docs/cloud/` guide, four documentation tests.
- Inputs: latest Work/OpenCode compatibility contract; official V2 CLI and network
  client documentation linked in `studio/cloud/REMOTE-OPENCODE.md`.
- Outputs: dual-producer instructions, remote-vs-local execution boundary,
  API-only limited-edit explanation and remote activation acceptance checklist.
- Checks: 14 cloud checker tests + 14 Work/doc/preflight tests passed; independent
  source/asset audit passed; branch preflight checked 16 locked files unchanged.
  Preflight correctly reports missing pinned render environment on this tool host.
- Guide validation: actual 375px and 1440px screenshots inspected; no horizontal
  overflow. Mobile full-page GPU capture had a tiling artifact; a tall-viewport,
  GPU-disabled capture plus DOM positions confirmed a single, correctly laid out
  page. Hierarchy 9 / consistency 9 / aesthetics 8 / usability 8. No design assets
  or logo geometry changed. No image generation, campaign rebuild or deployment.
- Human decision: prepare the correction; **no permission to merge this PR yet**.
- Unresolved: remote OpenCode VM/server not provisioned; protected endpoint and
  actual remote tool execution not tested; Work/Codex Cloud and image connectors
  remain separately verifiable. Desktop remote connection must be verified for
  the actual client; CLI support alone is not desktop activation.
- Durable delivery: pushed task branch + open PR with GitHub audit result. Pages
  stays unchanged until explicit permission to merge that PR. No local files deleted.
