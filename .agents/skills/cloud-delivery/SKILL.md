---
name: cloud-delivery
description: Build and deliver Brand Studio assets in ChatGPT Work or Codex Cloud. Preserve recipes, outputs and history on GitHub with audit-only CI. Use for cloud setup, export, packaging, isolated branch delivery and handoffs to OpenCode.
---

# Work / Codex builds; GitHub audits

1. Read `AGENTS.md`, `studio/work/README.md`, `studio/cloud/README.md`, `studio/cloud/policy.json`.
2. Start from current main in a separate checkout/worktree and a new
   `publish/<topic>` branch. Preserve other branches/PRs and use the handoff template.
   Run `python3 studio/work/preflight.py --root . --brand <slug>` before production.
3. For requested rendering, install with `bash studio/cloud/setup.sh`; inspect capabilities with
   `bash studio/cloud/doctor.sh`. Installation **does not build or generate images**.
4. Run the registered recipe only when the task requests output changes:
   `bash studio/cloud/build.sh launch-creative-02` is the first supported example.
   Historical Mac-dependent scripts are archive/reference, not automatically migrated recipes.
5. Preserve generated originals and old deliveries. Use complete approved SVGs.
   Save recipe, tool versions, editable sources, exports, exact-copy manifest,
   review/comparison images and ZIP. Register new bundles in `policy.json`.
6. Inspect actual images with an available image-viewing capability; record what
   was inspected. Source validation alone is not visual inspection. No claim of
   aesthetic parity, OCR correctness or raster logo authenticity from hash checks alone.
7. Run `python3 studio/cloud/audit.py --root .` and
   `python3 -m unittest discover -s studio/cloud/tests -v`.
8. Commit the relevant work and open a PR, describing image/model calls, changes,
   accepted limitations and human approval still needed. Passing audit is technical only.
9. GitHub's `audit / submitted-files` checks actual committed inputs independently;
   it never renders. Leave every PR open until explicit authorization to merge it;
   human creative acceptance alone is not merge authorization.
10. After an authorized merge, verify Pages and live export hashes. CI artifacts
    expire and cloud task state is temporary: commit important results or use a
    durable release with a checksum index. Never end with unique files only in the VM.

Cloud selection/account consent cannot be provisioned by adding repo files.
Follow `studio/cloud/ACTIVATION.md`; mark cloud activation and raster connectors
pending until actual account-side tests pass.
