# Brandstudio P2 — Verified Agent Handoff and Quiet Provenance Footer Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Add verifiable source-to-target agent handoff metadata and a compact per-product agent credit plus collapsible production timeline at the bottom of the existing Brandstudio browser editor, without changing code-first designs or their exported pixels.

**Architecture:** P2 handoff is explicit GitHub source-head + isolated target-branch protocol layered on P1 contracts and the existing `studio/work/ephemeral.py` manager; it is not an agent launcher. A separate **read-only**, static public provenance index feeds a small browser component keyed by exact design *version*, never by family alone. Old products have "unrecorded" attribution, no guessed agent. Do not add Cloudflare endpoints or new paid services.

**Tech Stack:** Python 3.12 `unittest` + existing `jsonschema==4.23.0`; Node 22 `node:test` + `vm` used by existing editor tests; semantic HTML `details/summary` and CSS with no third-party UI package.

**Spec:** `docs/superpowers/specs/2026-11-02-brandstudio-p2-handoff-design.md` (approved with provenance-footer addition, 2026-11-02).

## Global Constraints

- Preserve `docs/visual-editor/browser/index.html` edit/undo/redo, HTML/CSS/SVG production, canvas `iframe`, `docs/instagram/**` artwork, `studio/cloudflare-brandstudio/build_pages.py` byte-preserving behavior, Cloudflare Workers, Pages, backup and publication systems.
- The provenance footer is outside all editable/source/exported canvas markup; no modification to historical KAIST V2. Footer compact at bottom; timeline collapsed by default and operable by keyboard/touch. No focus trap, no polling or new always-on API.
- Capability claims, agent names, source/target runtime execution, files and hashes are **evidence-gated**. `chatgpt-chat` with connected GitHub is not `chatgpt-work`. Unknown agent is visibly unknown; no invented chronology.
- Git commit object IDs use SHA-1 of Git objects; asset integrity claims use independently measured content SHA-256. Never interchange.
- All public metadata explicit allowlist, no free-form external URL or unescaped HTML, no private briefs/user IDs/keys/credentials/model secrets, no automatic social publication; GitHub links must target `https://github.com/cinegitim/design/` with a valid PR number/40-char commit only.
- One executor/writer per branch, `max_parallel=1`; no auto paid API or model fallback. Source HEAD must be freshly verified before receiving the handoff. `source_verified` only means GitHub commit/branch observed, **not** model execution.
- P2 pilot is KAIST V2 with in-review status, `creative_approved:false`, `social_published:false`. Historic metadata can contain verified GitHub PR #190 but agent attribution must remain `unknown` until host evidence exists.
- Separate PRs recommended for handoff protocol and footer display so a source adapter change does not block UI rollback.

## Review Focus

1. **A version changes from KAIST v1 to v2:** footer reflects exact `selected.id` and never borrows attribution from the family/default record. Task 4.
2. **No attribution or unknown host:** footer says "Ajan bilgisi belgelenmedi", not a fabricated Work/OpenCode badge; no invented timeline. Tasks 3–4.
3. **Public JSON includes malicious markup, unexpected URL or extra user details:** allowlisted renderer uses `textContent`, rejects URL/domain and unknown schema fields. Task 3.
4. **Source branch advances between reading and target creation:** handoff must refuse stale `source_head_sha`; target base/receipt not silently reassigned to `main`. Tasks 1–2.
5. **Success CI but no pixel inspection/human approval:** P2 can mark a transport exchange, not creative acceptance, published work, or verified rendering. Tasks 2, 4.

---

### Task 1: Versioned portable handoff envelope

**Files:** Create `studio/production/handoff/__init__.py`, `studio/production/handoff/schema.json`, `studio/production/handoff/protocol.py`; test `studio/production/tests/test_handoff.py`.

**Interfaces:**
- `prepare(task: dict, source: dict, *, target_executor: str, target_branch: str) -> dict`: validates P1 TaskSpec and source TaskReceipt, matches original task/base SHA, enforces separate source and target branches and source executor != target executor, and creates a `prepared` envelope; does not claim remote existence.
- `verify(envelope: dict, *, observation: dict) -> dict`: requires a **supplied** observation with `observed_from="github-connector"` or `observed_from="git-remote"`, exact `source_branch` and `source_head_sha`. Fail closed if missing or stale; does not execute Git calls.
- `receive(envelope: dict, *, target_observation: dict, target_receipt: dict) -> dict`: checks target base equals source head, distinct branch and executor, same task ID and supplied target head evidence; never marks creative accepted.

- [ ] **Step 1:** Write tests for valid envelope, SHA mismatch, wrong branch, duplicate task, path traversal, task original base preserved, unknown executor; run `python3 -m unittest studio.production.tests.test_handoff -v` and observe missing implementation FAIL.
- [ ] **Step 2:** Implement schema and `prepare`, rerun test GREEN. No network/PR writes.
- [ ] **Step 3:** Add tests for `verify` stale source and forged observation, for `receive` wrong parent and capability missing; observe RED.
- [ ] **Step 4:** Implement `verify/receive`, rerun new + existing production suite GREEN.
- [ ] **Step 5:** Commit isolated P2 protocol files. Preserve P1 source and `studio/work/ephemeral.py`.

### Task 2: Handoff CLI + pinned pilot replay

**Files:** Create `studio/production/handoff/cli.py`, `studio/production/tests/test_handoff_cli.py`; document `studio/production/handoff/README.md`, `docs/superpowers/evidence/2026-11-02-brandstudio-p2-pilot-replay.md`.

**Interfaces:** `python3 -m studio.production.handoff.cli prepare/verify/receive` accepts local JSON files or explicit command flags and outputs safe JSON. No agent launcher, credentials, image generation or network access embedded into validator.

- [ ] **Step 1:** Write CLI tests for valid fixture, wrong SHA/host, duplicate JSON keys, size >256 KiB, secrets not printed, and no implicit shell/GitHub calls; run RED.
- [ ] **Step 2:** Implement CLI via Task 1 functions; run GREEN.
- [ ] **Step 3:** Describe exact KAIST V2 baseline, verified GitHub blob SHA-1 values, source commit and historic attribution **unknown**. Keep existing assets unchanged. Record live host probe as `blocked` when unavailable, not fake.
- [ ] **Step 4:** Run production suite `python3 -m unittest discover -s studio/production/tests -v` plus existing work tests; commit P2 protocol PR with exact-head CI. Do not mark actual two-host execution PASS unless both hosts were actually observed.

### Task 3: Static public-safe provenance records and renderer

**Files:** Create `docs/visual-editor/browser/provenance.js` and `docs/visual-editor/browser/provenance.json`; test `studio/cloudflare-brandstudio/tests/provenance.test.mjs`.

**Interfaces:** Browser IIFE export `BrandstudioProvenance` with `entry(index, productId)` and `render(rootElement, record)` (both side-effect free outside the passed DOM node). `provenance.json` contains `{schema_version:1,products:{[exactVersionId]: {producer:{executor,verification}, events:[...]}}}` for explicitly documented products. Only allowed agents `opencode`, `codex`, `chatgpt-work`, `chatgpt-chat`, `antigravity`, `unknown`. Proof `verified` only with matching GitHub reference, no guesses. Events have fixed role/status and ISO UTC timestamps, safe evidence refs, with `unknown` allowed only when no host evidence.

- [ ] **Step 1:** Write Node tests for keyed version lookup, unknown attribution, chronological sorting, reject `javascript:` URL and unapproved remote domains, escape injected tags; run `node --test studio/cloudflare-brandstudio/tests/provenance.test.mjs` RED.
- [ ] **Step 2:** Implement renderer using `document.createElement`/`textContent`, not `innerHTML`; links allowlisted to exact repo PR/commit. `<details>` is initially closed; no JS click handler required.
- [ ] **Step 3:** Provide **only truthful** historic KAIST V2 proof from PR #190 (merged timestamp and source commit if checked); unknown original producing agent. Label as GitHub/version proof, not creative review.
- [ ] **Step 4:** Node tests GREEN, inspect generated DOM and CSS, commit.

### Task 4: Subtle bottom-of-page footer integration

**Files:** Modify `docs/visual-editor/browser/index.html`; test `studio/cloudflare-brandstudio/tests/provenance.test.mjs` and existing `studio/cloudflare-brandstudio/tests/editor-ux.test.mjs`, `studio/cloudflare-brandstudio/tests/test_browser_editor.py`.

**Interfaces:** Add a footer **after** closing `#workspace`, not inside `main.center`, the slide `iframe` or export source. The footer owns a one-line small muted credit and native collapsible `details/summary` timeline. On `openProduct(selected.id)` and every version selection, call `BrandstudioProvenance.render(..., BrandstudioProvenance.entry(index, selected.id))`; load static index once using same-origin `fetch('provenance.json')` with error → unknown, no retries/polling. No inert controls.

- [ ] **Step 1:** Add integration tests asserting existing editor DOM and canvases unchanged, footer placed outside `#workspace`, one `fetch`, JS init sequence, version changes update exact id and no raw HTML insertion; run RED.
- [ ] **Step 2:** Add 1 static footer and muted style rules, mobile wrap and no overlay, hook existing product selection; keep old IDs and editing handlers intact.
- [ ] **Step 3:** Run Node suite, browser editor Python suite, static Cloudflare build tests; render/inspect editor in an **authenticated** test context only when already accessible; do not ask for passwords or claim visual inspection of post-login page if unavailable.
- [ ] **Step 4:** Commit on separate UI branch, open PR, exact-head audit plus editor tests, no automatic full Pages deployment while user has not requested it. Do not claim live UI until verified deployed.

### Task 5: Real two-host pilot proof gate

**Files:** A **new** pilot task folder under `docs/instagram/brandstudio-p2-kaist-pilot-20261102/` only if real executor tools and source assets are available. Keep historical `kaist-tech-track-2027-001/v2/` unchanged.

- [ ] **Step 1:** Verify OpenCode executable/host ID and GitHub write permissions in actual local environment. If unavailable, report `blocked:no-opencode-runtime`.
- [ ] **Step 2:** Run actual OpenCode job in a fresh isolated owned clone; save verified source commit/receipt and tested output, no paid generation. Never mark a synthetic CLI call as OpenCode execution.
- [ ] **Step 3:** Verify dedicated Work/Codex host and independent clone using exact source head. If unavailable, report `blocked:no-work-runtime`, retain files.
- [ ] **Step 4:** Validate two receipts, new render and visual review evidence (if produced), source-to-target ancestry, tested PR head. `transport_verified` and `design_technical_verified` remain distinct.
- [ ] **Step 5:** Update footer chronology **only from verified actual events**; code PR or report blocker. No social publishing/creative approval.

## Coverage and deferment

This plan implements the approved P2 feature as two separable code modules: P2 handoff protocol and an unobtrusive provenance footer. It does **not** implement the later P4 task dashboard, new Cloudflare infrastructure, universal agent launch, automatic model switching or P3 render cache.

**Execution preference:** Native, sequential, zero-cost (no multiple subagents). Review and merge code PRs only after exact-head checks and independent relevant suites. Follow repo `PUBLISHING.md`; user has approved P2 architecture and footer feature, not creative output/publishing. A live two-agent PASS requires an actually accessible OpenCode plus Work/Codex runtime; missing access is documented as blocked.
