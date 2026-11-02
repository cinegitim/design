# Brandstudio P2 KAIST — ChatGPT Work independent QA

**Status:** technical verification only. No creative approval, social publication, merge, Visual Editor change, historical V2 edit, Cloudflare write, paid API use, or image generation.

## Provenance and lineage
- Original task base: `f44b775d9e52b736facf6d57706ffbf2b0e6ab69`.
- ChatGPT source HEAD: `f50318d619d7a46a7b4504dd0efaefd03c1265b2`.
- OpenCode-attributed GitHub target HEAD: `1b5fd6ca37c81f6c9770ca964ee4228e78047d20`; this is the source used to create `work/brandstudio-p2-kaist-20261102`.
- OpenCode's submitted local HEAD `e1893e2c1d214eb50ee6b949642ca0d2d5bb36b3` and original 7,186-byte HTML attribution remain reported provenance, not independently host-attested here.
- Work added its own review artifact and render harness. OpenCode's original and recovered HTML files remain untouched. Work's adjusted layout exists only in the browser for QA; it was not written over OpenCode's files.
- The H-02 approved lockup at `brands/asyada-egitim/assets/lockups/h-02-primary-horizontal-dark.svg` is byte-identical at source and target Git refs (Git blob `0469f6cab3ec46c93c1d4494aa725ae7432e1cb7`). V-01 `docs/instagram/basvuru-rehberi-china-001/assets/v01-canonical.svg` is likewise identical (blob `b92d101b53a4287b0c25c5aa364647b22e152467`). The file contents identify approved canonical assets. Independent reviewer later computed SHA-256 of exact approved SVG contents and confirmed both embedded SHA-256 strings are correct; the earlier mismatch claim was mistaken. See REVIEW-QA.md.
- The OpenCode changed HTML and its preceding originals were reviewed by the GitHub connector. At HEAD `1b5fd6c…`, H-02 and V-01 paths are not resolvable from the nested artifact location as written; the linked CSS is a full KAIST V2 stylesheet containing selectors/classes this demo does not use.

## Work runtime checks
- Created branch `work/brandstudio-p2-kaist-20261102` from exact OpenCode HEAD `1b5fd6ca37c81f6c9770ca964ee4228e78047d20`.
- Chrome rendered the OpenCode HTML using an isolated harness at 1080×1350 CSS pixels with the original referenced CSS removed and the logo URLs pointed to the immutable approved asset files. This is a controlled browser render, not an exported image.
- DOM confirmed canvas 1080×1350. In the recovered HTML with its compact CSS repair applied for fit, five content sections have bottoms at 494, 650, 806, 1007, and 1208 px; footer begins at 1267 px. All three logo images loaded with nonzero natural dimensions.
- Visual inspection found the original/recovered typography and cards visually fit after CSS adjustment. The original size still pushes the final section below the footer; the previously reported logo hash discrepancy was ruled out by independent SHA-256 verification. No pixel-diff QA or raster export was run.
- Chrome's remote preview at raw.githack.com was used to execute the harness. GitHub raw itself rendered source as plain text, so it is not evidence of rendering. Original unadjusted document's viewport clipping was observed by screenshot and DOM; the successfully fit configuration was inspected at the exact artboard frame.

## Changes and checks
- `work-output/brand-system-demo.html`: separate Work-authored review composition referencing approved assets.
- `work-output/opencode-render-harness.html`: test-only copy of OpenCode corrected artifact with nonworking relative references replaced by immutable absolute asset URLs and external CSS removed for isolation. This harness is not the final deliverable.
- `work-output/render-frame.html`: fixed artboard wrapper; it displays the harness and is test infrastructure, not a published social asset.
- Each GitHub Contents write returned a commit SHA. No workflow runs were returned for the render-frame commit. CI is therefore **not reported as passed**. A PR and CI check still need to be created/triggered.

## Handoff boundary
- ChatGPT Work executed this review in a Work session with GitHub connector and connected Chrome. It is independent of the earlier chat host in execution context; no separate model/host attestation for OpenCode is asserted.
- No creative acceptance, export readiness, or publication status is implied.
## Independent follow-up review — ChatGPT chat, after Work

An independent GitHub reviewer branch corrected broken paths in the **standalone Work composition** (not the Work harness) and made the in-branch P1/P2 records schema-valid without fabricating self-referential commit HEAD. Work and OpenCode artifacts remain in their own subdirectories; the hash-mismatch claim was a false positive. See `REVIEW-QA.md`. Reviewer contribution: `chatgpt-chat`; original Work review: `chatgpt-work`.
