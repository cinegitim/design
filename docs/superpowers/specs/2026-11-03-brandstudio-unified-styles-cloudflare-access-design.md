# Brandstudio 4.0 — Unified visual language, GitHub-first production, editor, publication proof and Access

**Date:** 2026-11-03. **Status:** DESIGN PROPOSAL / NOT APPROVED. No production configuration changes. No entitlement to automatically publish a social post or approve a new design.

## Product intent

Any authorized producer — ChatGPT chat, ChatGPT Work, Codex, OpenCode, Antigravity, or another medium capable of reading the repo — should be able to choose **Brand → Category → Style family → Preset → Optional variations** and deliver a recognizably consistent, editable design. Brand identity remains byte-exact, but layouts and expressive imagery can vary. GitHub is the durable source of truth for *production*, Cloudflare is the private presentation/editor and draft revision layer, and verified platform publication evidence appears in the product panel.

The private Brandstudio UI is \`https://studio.asyadaegitim.com\`. Published social-media assets and the historical public GitHub Pages repository are **not made private by protecting the UI**.

## Baseline verified before proposal

- \`brands/asyada-egitim/brand.json\` locks exact approved V-01 and canonical H-02/P-01/F-05 SVGs with SHA-256s; **C-03 and D-04 are retired**; typography includes Jost.
- \`studio/production/style_catalog.py\` supports brand/category-scoped styles, presets and six variation axes. The only currently listed style family is \`instagram-carousel/editorial-campaign\`, \`version=0.1.0\`, \`status=review-only\`, **not approved**. Its hard-lock options and README still reference retired D-04: fix this contradiction *before* using the style as a production contract, without rewriting historical assets.
- \`studio/production/routes.json\` has six categories including Instagram carousel, social post, identity application, print catalog, web design and new identity; most have no registered style families.
- \`docs/visual-editor/browser/index.html\` already has editing, version history, cloud state sync, public product catalogue, per-product provenance footer and publication bridge. \`github-sync.js\` writes draft versions to the private Cloudflare API/DO, **not** to GitHub. Repo production GitHub PR flow is separate.
- \`studio/publication-tracker/worker.mjs\` can scan Meta Instagram/Facebook and supported other providers, but scan runs via authenticated endpoint; \`docs/instagram/publication-bridge.js\` exposes only **family_verified** publication matches publicly. A family match is not evidence that a particular edited version was posted.
- \`studio.asyadaegitim.com\` is a Cloudflare Worker custom domain routed to \`brandstudio-edge\`; it has a password/trusted-browser Durable Object session (up to 365d) but **no Brandstudio Cloudflare Access app** yet. \`brandstudio-pages-git.pages.dev\` and original \`cinegitim.github.io/design\` are alternative public asset access paths.
- The Asya'da Eğitim Cloudflare account already contains an unrelated signature-management Access app, one-time PIN IdP, and four-address allow policy. Reusing the allowlist for Brandstudio **requires explicit user confirmation**; do not silently grant access.
- Cloudflare documentation: **Global, application and policy Access session durations cap at one month**, not one year. A 365-day application trusted-device cookie may remain as device recognition, but cannot bypass Access reauthentication when Access expires.

## Architectural alternatives

**A — prompts and templates only:** cheap and easy, but independent agents can silently drift, incorrect SVGs can pass, and local editor versions never reach GitHub. Not sufficient.

**B — GitHub-first style pack + CI, with Cloudflare private editor and verified publication overlay (recommended):** smallest change to existing, free/low-on-demand infrastructure. Every agent can read identical versioned JSON rules and references; PR/CI verifies the deliverable. Draft revisions are cheap DO snapshots; explicit **Publish version to GitHub** commits a version safely via server-side authorized mechanism and PR. Existing publication tracker provides verified platform events and maps exact versions only when evidence exists.

**C — central always-on multi-agent orchestration/database:** more immediate sync but duplicates agents' execution, adds operational burden, quotas, security surface and cost. Defer until B proves insufficient.

**Selected by implementer as proposal, pending user approval:** B; do not build C by default.

## 1. Portable style and identity contract

A versioned \`studio/production/design-system/\` contract plus per-brand \`styles/<category>/<style-id>/style.json\` records:

- Identity lock: mandatory canonical \`brand_slug\`, approved complete lockup \`id/path/sha256\`, seal SHA, minimum readable size/clearspace, permitted color variants. SVGs must be referenced/copied as-is; no model-generated, retyped, recolored or transformed logos. Retired C-03/D-04 fail closed.
- Visual consistency: permitted tokenized family palette, font family/weight sets, type scales, optional semantic accent limits and contrast checks; Jost is default. No requirement to use an identical grid/visual layout in every output.
- Selected \`category\`, \`style_id\`, \`style_version\`, \`preset_id\`, \`variation_overrides\`; \`approved\` vs \`review-only\` is explicit. A review-only family may be previewed but cannot be auto-passed as approved.
- Agent-independent normalized task brief / resolved style bundle; downloadable/readable from connected repo. Populate AGENTS.md, .opencode and ChatGPT Work instructions as *thin references* to one canonical contract, never three divergent copies.
- A new product manifest includes source file list, actual render, approval, exact output dimensions, immutable brand SHA, style choices, task/host provenance, Git source/PR and publication status. Correctly distinguish reported agent identity from host-verified identity.

**Design rule:** locking exact logo bytes does not mean the logo must be placed in the same position; permitted placement and safe scaling remain variable.

## 2. GitHub and Visual Editor source of truth

1. Producer selects style *before generation*, gets normalized style pack and source reference; creates its own feature branch, editable HTML/CSS/SVG, optional image layers and an output manifest; submits PR. CI gates identity/style/asset measurements and technical render. Human design approval remains separate.
2. GitHub commit/merge makes immutable **source version** discoverable in catalogue, with maker/agent credit.
3. Existing Visual Editor loads source plus DO overlays. Auto-save and manual version snapshots stay in the secure DO to avoid one GitHub commit per drag/key stroke. Add explicit **GitHub'a sürüm kaydet** action to export the chosen overlay as a new reviewed source/manifest snapshot, on an isolated branch/PR; server-to-GitHub credentials never appear in browser JS. State-to-source conversion must preserve editability and locked SVG hash. After exact-head tests pass, catalogue indexes new version.
4. In the editor, group style selection is at product creation (and optional explicit 'change style' action), not on every micro-edit. The read-only provenance footer shows style, variant, source PR, actual contributor and timeline; never overlays the artboard.
5. The cloud editor must not silently claim a GitHub commit exists when only DO autosave has completed. Distinguish **local pending**, **cloud draft saved**, **GitHub PR submitted**, **GitHub main version**, **social published**.

## 3. Multi-channel publication proof

- Reuse \`brandstudio-publications\` ingestion, existing Meta/provider integrations, and the publication bridge. Prefer explicit platform-post webhooks/success events where available; for arbitrary manual/off-platform publication, a cheap on-demand refresh and optional low-frequency scan if the user authorizes it.
- A platform permalink + authorized account/creator ID + published timestamp is required before recording \`social_published=true\`; an internal publication button or scheduled post is not sufficient.
- Distinguish \`family_verified\` (some version in that campaign family was published) from \`revision_verified\` (exact source/export hash plus platform publication or upload correlation). UI may show a family-level indicator, but never falsely claim a specific version was published.
- Protect platform API keys server-side and leave read-only public proof feed sanitized. Deduplicate idempotently; no automatic re-publication, no paid API default, bounded requests.

## 4. Cloudflare Access for the studio

**Target:** self-hosted Access application protecting \`studio.asyadaegitim.com/*\` with explicit individual e-mail allowlist and existing one-time PIN IdP, \`720h\` (30-day) app/policy session maximum. The same maximum may apply to global SSO; \`1y\` *Access login session* is not technically supported.

**Identity choice required:** user must confirm Brandstudio's authorized e-mail list. The existing signature-management policy is a candidate, not an authorization.

**Safe rollout:**
1. Read-only baseline for \`brandstudio-edge\`, its custom domain, \`brandstudio-pages-git.pages.dev\`, editor revision APIs and the existing trusted-device session.
2. Build Access app with confirmed allowlist; test one intended authorized account, one unauthorized account and login return URLs. Keep the old admin path/rollback functioning until Access is verified.
3. Front-door Access alone does not guarantee origin/API security. Bind protected hostname and validate Access JWT/identity at the write gateway or otherwise make sure direct worker URLs cannot bypass; preserve CSRF/authorization. Prefer Access for sign-in rather than asking for the previous username/password once JWT validation and rollback are in place.
4. Protect or remove public duplicate admin/editor entrypoints. A separate Pages \`*.pages.dev\` / preview Access policy may be needed and may have distinct implications; **GitHub Pages and the public repository remain public** — do not claim asset confidentiality there. If fully private designs are desired, move unreleased drafts to private storage, and separate public marketing assets.
5. Preserve 365d browser **trusted-device recognition only** if desired, but reauthentication at ≤30-day Access limit is mandatory. Ensure explicit logout/revocation, same-site cookie safety, fail-closed paths.
6. No DNS cutover, changes to unrelated signature system, deletion of Durable Objects, alteration of published artwork, or deployment before authorized identity verification.

## Incremental implementation and acceptance

**Phase A — enforce portable design pack:** reconcile retired D-04 references; define stable schema/validation tests; include color/font and exact logo SHA; connect existing style router; add styles for more categories only after human style approval.

**Phase B — integrate into editor:** add optional compact style/preset picker and resolved style badge. Retain existing editing and version history. Add branch/PR-based GitHub checkpoint; test rollback, conflict resolution and private token handling.

**Phase C — publication proofs:** add exact-version proof mapping where supported, keep weaker family matches labeled. Use existing provider APIs; enable on-demand refresh first (no 24/7 crawler). Verify external-post edge cases.

**Phase D — Access:** with confirmed email allowlist, create protected app and test permitted/denied access. Stage the authentication transition so no authorized user is locked out; no 1y Cloudflare Access promise.

**Independent gates:** visual-language unit tests, exact lockup SHA and retired-logo rejection, font/palette consistency, no clipped elements at export dimensions, correct editability/replay of editor revisions, no publish without provider proof, state and login authorization tests, all existing editor/production CI. Preserve branded SVG source bytes, existing production and all prior history.

**Open decisions for user:** (1) confirm the exact authorized email allowlist for Brandstudio; (2) approve recommended architecture B. A global one-year Access session cannot be offered; propose 30-day max plus existing trusted-browser recognition.

**No production mutations authorized by this draft.**
