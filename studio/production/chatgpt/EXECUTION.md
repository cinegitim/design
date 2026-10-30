# Brandstudio — three ChatGPT-family execution routes (v1)

Shared authority: root AGENTS.md; brand.json, approved decisions and canonical
lockup manifests; studio/production/BOOTSTRAP.md; existing publishing rules.
This document **does not** install Work or Codex, select a model/effort, or grant
permissions. The user's complete natural-language brief is preserved unchanged.

## Surface decision

1. Identify the **actual experience**: standard ChatGPT chat, ChatGPT Work, or
   Codex. A user asking for GPT-6 High does not switch the UI picker.
2. Identify observable GitHub read/write tools, filesystem/terminal, rendering
   and image capabilities separately. Unknown means unavailable, not false.
3. For standard ChatGPT use --executor chatgpt-chat. If user/UI explicitly
   specifies High, pass --requested-effort high and record it as requested,
   **not runtime-verified**. With github-read this selects
   chatgpt-high-connected-v1; without it use a limited/image route.
4. For Work use --executor chatgpt-work; for Codex use --executor codex.
   Never apply the Chat thinking slider to Work/Codex model metadata.
5. Pin the GitHub main commit SHA and route/skill versions before production.

## Style layer beside production category

An optional style ID (for example `editorial-campaign`) is selected separately from `instagram-carousel`. It resolves only within the exact brand/category through `studio/production/style_catalog.py` and the selected family's `style.json`. A preset and validated axis overrides change layout/color/photo behavior **within the same family**, never the route ID or canonical identity. Prefer cream/paper as a recurring institutional surface when the selected style specifies it; do not stamp the same background/layout onto every slide. Record style family/version, preset and resolved variations in the real output manifest.

A `review-only` style may guide experimental art direction but is not human-approved. In ordinary ChatGPT with GitHub connector access, read the style manifest via GitHub and apply equivalent validation manually if the Python checkout is absent. The local router's reads do not prove its Python CLI ran on the host.

## Instagram carousel: preserve the existing code-and-render method

**Default across ChatGPT/Work/Codex:** consult the current brand's actual
previous `build.py`/HTML/CSS/SVG application, then build or adapt editable source;
composite an approved *complete* canonical lockup SVG from its manifest;
render at the exact requested dimensions with an observed browser/Playwright
runtime; inspect PNGs and record source, lockup hashes and output evidence.
For `asyada-egitim`, a real reference is
`brands/asyada-egitim/applications/instagram-carousel-01-v3/build.py`;
this is an example, not permission to borrow the sibling `asya-egitim` identity
or to overwrite an earlier application. Campaign choices remain review-only.

Use image generation only for separately composited photography, illustrations
or backgrounds **when authorized**. Do not generate full-slide text/logo/layout
via native ImageGen as the default, regardless of tool availability. An explicit
user instruction to explore image-only slides enables a separate *experimental*
path; it is not the legacy deliverable, cannot be described as canonical, and
still cannot redraw or retype approved logos. Image-only tools without a
rendering/source pipeline are insufficient to finish a production carousel;
stop and disclose that limitation rather than replacing the method silently.

Source code, genuine browser-rendered exports, logo verifiers and visual review
are distinct checks. A chat-rendered image or CI pass alone proves none of them.
Do not claim a finished production until the actual deliverables are preserved.
See `routes.json` → `production_policies.instagram-carousel`.

## Standard ChatGPT — GPT-6 High / connected tools

Optimized for conversational orchestration: read only the exact brand metadata,
locked approval assets and relevant category skill, then compile the user brief
into compact execution steps. Prefer existing connected GitHub file tools for
source reads and small edits. Image generation may be used only if the user
requested an actual new or modified image. Do not treat an image displayed in
a chat as proof its bytes exist in GitHub. If creating editable SVG/HTML/source
assets, preserve the real source, not only a visual rendering. Never assert
a local checkout or Work computer in normal chat. No invented token usage.
Use a separate publish branch and exact-head review/CI/merge if repo writes
are actually possible; otherwise report the precise blocked delivery step.
Visual/creative acceptance remains distinct from technical CI.

## ChatGPT Work — workspace-first

The user must actively enter Work. Follow studio/work/README.md and
.agents/skills/brand-studio/SKILL.md. Prefer its actual cloud workspace/computer
for multi-file tasks, isolated worktrees, brand preflight, editable source,
pinned recipe render, output hashes, PR, independent checks, verified merge
and publication. Check which tools and models the Work session exposes; a
GitHub connector is not a replacement for a working build environment.
Do not assume this workflow is executable from a standard ChatGPT message.

## Codex — code and test-first

The user must actively enter Codex. Start at the repository root/worktree;
use AGENTS.md and .agents/skills/, detect actual selected Codex model and
enabled tools, then produce deterministic sources and tested rendering.
Run unit tests and studio checks where available. Separate checkout/branch,
base SHA, CI-head verification, merge and deployment rules are unchanged.
Avoid copying ChatGPT-specific model/effort labels into Codex records.

## Optional post-production Visual Editor handoff

Visual Editor is **not** a production executor: the canonical prompt-driven HTML/CSS/SVG → real render workflow remains the default. When and only when a producer has verified original editable source and actual slide PNGs, the user may opt to register that output in their **installed local companion** via `studio/visual-editor/bridge.py`. The bridge verifies the exact on-disk P-01/light hash against the current brand lockup manifest, refuses duplicate product IDs and retains the original deliverable. The bridge's `--dry-run` inspects inputs but does not register a product.

The public Pages `docs/visual-editor/` route and product-specific site actions only *navigate* to the user's local companion; Pages cannot run Python, write v2/v3 folders or silently sync GitHub. Local private revision states are not GitHub commits or approved production. A real published revision requires its own reviewed deliverable and exact-head PR/CI. A missing companion is a normal optional-capability state: do not block successful prompt production or invent registration.

## One common delivery contract

Capture: original task, exact brand slug/approval manifest, category, source
commit SHA, executor + model evidence, route id and strategy version, actual
tool calls, editable assets and outputs, changed paths, PR/head/checks,
publication evidence (if applicable), genuine metrics or "unavailable".
Treat a dry-run as a dry-run: do not fabricate production, a token counter,
a saved output, aesthetic approval, or automatic skill invocation.

## E2E acceptance probes (no asset generation)

A new ChatGPT Project conversation may ask:

"Brandstudio: Asya'da Eğitim için karusel üretimini BAŞLATMADAN
model/ortam tespiti, GitHub ana commit'i, canonical marka kaynağı,
seçilen rota ve erişemediğin yetenekleri doğrula. Tasarım üretme
ve GitHub'a yazma."

PASS only if the response cites actually fetched GitHub source files, does
not borrow sibling-brand identity, distinguishes observed from assumed
model settings, records proper route/fallback, and does no unrequested edits.
This test proves **that conversation's** activation, not automatic activation
in all future conversations. Work and Codex must be separately tested in
their respective experiences.

## Production Recorder v1 (after a real production request)

See `studio/production/recording/README.md` and
`studio/production/recording/recorder.py`. The recorder is an explicit
CLI for Work/Codex/checkouts, not an automatically installed ChatGPT
telemetry connector. Private event ledger lives only in ignored
`.brandstudio-private/`; the public repository receives an allowlisted
summary after explicit review and the normal checked PR workflow.
Never place original personal briefs or private URLs in public run records.
Report absent model tokens/cost as unavailable. For ordinary ChatGPT with
connector-only tools, log only connector-observed evidence; do not pretend
to have executed recorder.py. "Finished" requires a hashed real artifact;
a planned/dry-run task is not a finished production.

## Asya'da Eğitim: logo seçimi — 30 Ekim 2026

Yeni üretimlerde `brands/asyada-egitim/brand.json` ve etkin `canonical-lockups.json` manifesti esas alınır. **H-02** tüm olağan yatay/dijital imzalar için varsayılandır. Ayrı bir kompakt logo üretme; onaylı H-02 SVG'sini tamamıyla orantılı küçült (360–480px önerilen, 320px alt sınır; ince İngilizce satırı gerçek boyutta denetle). 320px altında yalnız **V-01 mühür**. Dikey tasarımlarda P-01; resmî çift dilli kompozisyonlarda F-05. Eski C-03 ve D-04 dosyaları yalnızca tarihsel kaynaklarda kalır, yeni üretimlerde seçilemez veya yeniden karıştırılamaz. Ayrıntı: `brands/asyada-egitim/decisions/2026-10-30-h02-small-use-retire-c03-d04.md`.
