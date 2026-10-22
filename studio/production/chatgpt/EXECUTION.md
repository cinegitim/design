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
