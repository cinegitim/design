# P2 KAIST — GitHub aktarımı ve OpenCode kaynak kurtarma kaydı

**Status:** source→target GitHub **transport verified**. Real two-host AI-agent execution and design QA **NOT complete**. Keep [PR #196](https://github.com/cinegitim/design/pull/196) draft, do **not merge or publish**.

The source `publish/chatgpt-chat-brandstudio-p2-kaist-20261102` has GitHub-observed HEAD `f50318d619d7a46a7b4504dd0efaefd03c1265b2`. The target `publish/opencode-opencode-p2-kaist-20261102` has GitHub-observed HEAD `1b5fd6ca37c81f6c9770ca964ee4228e78047d20` with **single direct parent `f50318d619d7a46a7b4504dd0efaefd03c1265b2`**. The output branch contains 7 new files under `docs/instagram/brandstudio-p2-kaist-pilot-20261102/v1/opencode-output/` and no changes to historic KAIST V2.

- **Original task base:** `f44b775d9e52b736facf6d57706ffbf2b0e6ab69` (never substitute source `f50318d619d7a46a7b4504dd0efaefd03c1265b2`).
- **Source receipt:** `source-receipt.json` (`chatgpt-chat`).
- **Target receipt:** `target-receipt.json` (`opencode` original authored content, recovered by ChatGPT).
- **Handoff:** `handoff-envelope.json` now `received`, meaning **GitHub transport/ancestry only**; this does NOT certify OpenCode host access, render or creative acceptance.
- **GitHub observation:** `target-observation.json`.
- **Separate credits / timeline:** `pilot-provenance.json` makes distinct the local OpenCode-produced 7186-byte HTML (`5c29a53...`) and the ChatGPT GitHub recovery/path correction (`5b6e54...`). The original local git ref is `e1893e2c1d214eb50ee6b949642ca0d2d5bb36b3`; the imported GitHub commit is **not** that local commit.
- **Local receipt defects:** original `base_sha` incorrectly used source SHA; original `head_sha` was stale `206b2d...`; original envelope `output_ref` was an HTML filename and `received` could not be remotely confirmed. The raw original files are preserved for audit in the target's `original/` directory but should **not** be used as canonical receipts.
- **Repair:** original HTML remains byte-for-byte unchanged in `original/`. A separate `brand-system-demo.html` has only four broken relative asset references repaired. Browser loaded all three images and the CSS after correction; no complete visual render QA was performed.

**Outstanding:** verified second host (dedicated Work/Codex), actual per-host execution log/attestation, full render + pixel QA, and human creative approval. Budget zero extra paid APIs, image calls zero, no automatic publication. No modified historical slides or Visual Editor.

## CSS overflow follow-up

The first local screenshot revealed cropped content (`main.bottom=1670.55`, footer begins at `1240`). In Chrome, the edited CSS was measured at `main.bottom=1129.02`, footer begins at `1260`, with three loaded canonical images and all five content sections visible. The corrected SHA-256 sidecar was updated to `317400ce87798d198515bcb45e9bbae38cb8f6fac1cf00d4531366f1d467b3e7`. Local original HTML and the submitted unpushed Git history remain unmodified. GitHub target HEAD `1b5fd6ca37c81f6c9770ca964ee4228e78047d20` is **four commits ahead** of source `f50318d619d7a46a7b4504dd0efaefd03c1265b2`, not the identical local OpenCode HEAD. No raster export or independent full creative approval.
