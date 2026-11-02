# Brandstudio 3.0 — P2 Cross-Executor Handoff Design

**Date:** 2026-11-02. **Status:** DRAFT FOR P2 REVIEW. Parent Brandstudio 3.0 modular approach B approved and P1 merged. This document pins the P2 scope; creating this document does not assert that OpenCode or Work has executed a task.

## Intent

Prove that a single Brandstudio job can move between **actual** OpenCode and ChatGPT Work/Codex environments without depending on chat memory or shared process state, preserving immutable source/code/render assets, brand rules, token/privacy boundaries and an exact-commit audit trail. Do not rewrite the designer, browser Visual Editor, renderer, Pages/Cloudflare deployment, existing task storage or brand assets.

### Alternatives evaluated

**1. New orchestrator / always-on cloud runner.** Would require credentials, a daemon/queue and new security and billing obligations; disallowed by approved zero-new-paid-API policy.

**2. GitHub handoff plus existing isolated clones (selected).** Reuse already-tested `studio/work/ephemeral.py start --base publish/opencode-...` (new owned clone from an explicit parent branch) and the P1 TaskSpec / CapabilityReport / TaskReceipt / OutputManifest. Add a small portable handoff envelope and read-only validation. GitHub PR/files serve as durable proof; each executor alone produces its own output in a separate branch. No remote agent is falsely "activated" merely by its name in a JSON document.

**3. One shared checkout/branch for all agents.** Appears easy but breaks independent ownership, risks data loss and stale-head edits; not selected.

The parent B architecture had selected GitHub with independent executor adapters; option 2 is the narrowest implementation of that approved choice.

## What already exists

- `studio/work/ephemeral.py` already starts a new isolated owned clone with `start(task, repo, base=<explicit-parent-branch>, executor=codex|opencode|work)`. The repository has a tested *simulation* `test_executor_handoff_uses_explicit_parent_branch_and_new_clone`, including no mutation of the parent branch. **That simulation does not prove a real OpenCode / Codex session ran.**
- `studio/production/contracts/` P1 schemas and validator already exist, alongside `studio/production/advisory.py`. P1 routes are advisory, do not run agents or independently verify external evidence.
- `studio/work/handoff-template.md` records model/tool use, output hashes, exact-head CI, approval state and remaining work, but it is narrative text without a portable validated parent-SHA handoff envelope.
- User's `cinegitim/design` GitHub connection demonstrably supports branch, file, PR and exact-head check operations. **This chat is not automatically a ChatGPT Work session and does not have verified access to the user's local OpenCode process.** Both must be probed independently for an end-to-end two-host PASS.

## Reusable pilot: KAIST V2, no new image calls

Pilot basis at `main` **`2d0e36aeabeb147d8ec6c5a284d9d3cdad8cf9cd`**:

`docs/instagram/kaist-tech-track-2027-001/v2/` has six editable `source/{01..06}.html` files, six JPEG exports, official KAIST attribution and the **approved Asya'da Eğitim H-02/dark** lockup referenced by its `manifest.json`. V2 specifically changed slides **03** and **06**. It is **in-review**, `creative_approved:false`, `social_published:false`. Respect that state; no auto-approval, no new historical V2 edits.

A pilot uses a **new, isolated experimental output directory**, e.g.
`docs/instagram/brandstudio-p2-kaist-pilot-20261102/v1/`, with only attributable new files. Historic KAIST V2 directories are immutable. Input may refer to the *existing public* V2 manifest; never copy credentials, proprietary unpublished client briefs, or signed URLs into a public handoff.

Pilot **TaskSpec** (version 1) is shared by both executor passes; exact `task_id`, `brief_ref`, `base_sha`, `brand_slug`, `category`, `output_ref`, budget and approval fields must not silently change. For the transport pilot, common required capability is `github-read`, and each executor reports its additional observed tools. This prevents `filesystem+terminal` from erroneously disqualifying a Github-connector Work executor. **Design output still needs real render evidence before any claim of technical verification**; a passing transport pilot is not a rendered carousel.

Pilot budget: `new_paid_api=false`, `image_calls_max=0`, `auto_retry=false`, `max_parallel=1`. First stage may be a **read-only replay/branch-handoff** that merely inspects the existing HTML, JPEG and hash references. No design content change required unless a true executor is available and a separate controlled revision is authorized.

## Protocol and artifacts

1. **Create/validate.** Coordinator pins `main` and creates a sanitized P1 TaskSpec, checks exact brand and output path, checks proposed executor IDs against actual capability observations. If runner unavailable → `blocked`; never replace it with a fake report.
2. **First executor** owns a new unique `publish/opencode-<task>` branch. On **its own host**, call existing ephemeral manager or equivalent isolated clone. It reads only scoped `brands/asyada-egitim`, `studio/production/`, required policies and KAIST V2 sources. Any new original/editable asset has observed local byte SHA-256. Output manifests can remain `draft` until a real rendered PNG/JPEG and required checks exist.
3. **Freeze/receipt.** When a real source branch is pushed, verify exact remote head SHA and changed-path set through GitHub; create P1 `TaskReceipt`, preserving the original TaskSpec `base_sha`, plus an envelope:
   - `schema_version:1`, `task_id`, `source_executor`, `target_executor`, `source_branch`, `source_head_sha`, `original_base_sha`, `target_branch`, `output_ref`, `receipt_ref`, `observed_via`, `handoff_status`;
   - `handoff_status` is one of `prepared`, `source_verified`, `received`, `blocked`. Only verified external GitHub observations can move to `source_verified`; only actual target-host evidence can move to `received`.
   - `source_head_sha` is a real 40-char Git commit, not a SHA-256 asset hash. `receipt_ref` is a safe repo-relative reference; do not store raw brief text.
4. **Second executor** uses a **new** `publish/work-<task>` or `publish/codex-<task>` branch with its base tied to **the exact observed source head**, never `main` silently; it does **not** reuse the first agent's working copy. If the head advanced, refuse and require explicit restart/rebase. Read handoff and source artifacts; produce its own receipt for actual work.
5. **Compare & inspect.** Independent review reconciles both receipts and the working **content SHA-256** where bytes were retrieved, canonical logo ID and SHA-256, rendered pixels (when available), required CI exact head and human review state. A Git blob SHA is **not** a file SHA-256. No artifact hash means `unknown`, not "verified".
6. **Delivery gate.** PR(s) remain open until exact-head independent CI and actual reviewed assets meet delivery requirements. Human creative approval remains separate. No Instagram publishing and no automatic Cloudflare deployment.

## Exact interface / P1 compatibility

Add *small* `studio/production/handoff/` package for **read-only** bundle creation/verification helpers, an envelope JSON Schema and a CLI `prepare / verify / receive` that can run on each host. Leverage existing `contracts.validation.validate_bundle`; do not broaden or rewrite P1 TaskSpec fields or replace `studio/work/ephemeral.py`. Keep GitHub remote interactions at the host adapter boundary (connected tools or git) rather than adding embedded GitHub credentials/network code to the contract validator.

All role descriptions, model IDs, token measures, render checks, GitHub checks, PR merge state and creative approvals must be **observed** or explicitly `unknown`; no self-asserted `success` without evidence.

`prepare(...)` is pure and can run without GitHub; `verify(...)` needs a supplied GitHub observation with unchanged concrete commit/branch; `receive(...)` checks a supplied target branch and receipt without writing to it. Actual clone/push/write remains owned by the correct adapter/host and requires its available tools and user permission.

P1 receipt `base_sha` remains the *original* task commit, while the envelope's `source_head_sha` is the target executor's *handoff base*. These must not be conflated.

The `ephemeral.py` branch naming uses `publish/work-` for its CLI `work` executor (not `chatgpt-work`), whereas P1 uses `chatgpt-work`. A documented explicit mapping is required; silently treating any string as an enabled executor is unsafe.

## Safety and non-goals

Keep all existing Visual Editor browser files and cloud edit history, HTML/CSS/SVG engine, canonical marks and original KAIST assets unchanged. Neither GitHub merge nor a CI green badge grants creative or publishing permission. No additional D1, R2, Cloudflare Worker, Queue, paid image service, long-running agent, cron, or hidden credentials. No force-push, branch reset or clean of foreign directories; retain original Git references and history.

A git commit observed remotely is necessary for receiving a handoff but insufficient to assert OpenCode ran. Operator instructions/recorded host attestation must name the **actual host** with captured log reference, or report `blocked:no-opencode-runtime` / `blocked:no-work-runtime` without claiming a two-executor test.

## Acceptance tests and proof levels

**Code/contracts acceptance:** Test envelope schema (malformed branch/SHA/path/IDs rejected), wrong executor, divergent source head, changed primary SHA, task collision, non-existent target capability, missing output SHA, mismatched output directory, private ref leakage and invalid acceptance escalation. Existing P1 router and `studio/work/tests/test_ephemeral.py` pass unchanged.

**Transport proof:** A real source branch and a fresh target branch exist; source head is checked before target creation; target branch ancestry includes exact source commit; independent GitHub evidence is attached; target does not modify source branch.

**Executor proof:** Actual OpenCode host and Work/Codex host have separate verifiable receipts (not synthetic JSON). If one runtime is inaccessible, record the blocker; a script simulation may pass but do **not** call it a real two-host proof.

**Design proof:** If design output is requested, at least one new editable HTML/CSS/SVG artifact and its rendered pixel output are actually inspected; original V2 remains byte-identical; canonical H-02 logo verified; no creative acceptance without the user. Never call a transport handshake a finished creative carousel.

## Milestones and rollback

- **P2a: contract + replay validation** — read-only envelope tests and CLI, sanitized KAIST pilot description, shared GitHub facts captured.
- **P2b: Work/GitHub connector pass** — verify repo observation; make a separate new *source-only* branch or receipt when the actual connected Work host supports it. Do not claim Work execution if this is normal ChatGPT chat.
- **P2c: OpenCode host pass** — launch only in an observed OpenCode runtime, use existing ephemeral clone to publish to its own task branch; no shared checkout.
- **P2d: real two-host handoff** — target branch created from exact source head; actual output/render and proof compared. This milestone is **blocked**, not marked done, until both hosts' evidence exists.

Each milestone can be reviewed independently. Old site remains default; rollback reverts only new P2 adapter and pilot files, never historical design, source, Cloudflare edit revisions or user files. Pilot remains **review-only** and is not automatically served from main.

## Builder review and explicit uncertainty

Checked repo reality: local independent clone handoff **already has a simulated test**; build on it, do not write a parallel checkout manager. P1's common capability names are not equal to a verified remote session. Actual Chrome inspection in a separate browser context reached `studio.asyadaegitim.com/admin/login`, showing an access-protected site, but **did not authenticate or inspect the Visual Editor post-login**. The main Cloudflare site did not receive a write.

Remaining only real-world limitation: no tool in this conversation has been confirmed to launch the user's local OpenCode process or a dedicated ChatGPT Work cloud computer. The design requires truthful fail-closed receipts rather than assigning model or host names by convention. When such a runtime becomes available, the P2c/P2d host evidence can be obtained without redesigning this protocol.

**Approval:** P2 protocol and pilot scope are presented for explicit user design approval. The broader B architecture and P1 implementation approvals do not imply authorization to deploy or rewrite the existing production UI.
