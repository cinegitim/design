# AI Brand Studio — shared GitHub source / OpenCode + Work/Codex

This workspace is a reusable **AI Brand Studio** for vibe-designing complete visual identities from natural-language briefs.

## Cloud operating contract (current)

- **Both OpenCode and ChatGPT Work/Codex may design and produce.** Neither is the exclusive producer. They share the GitHub repository and recorded decisions, not a running session, chat memory, tools or credentials. Use a separate checkout/worktree and a new `publish/<topic>` branch for each production request. Never switch or clean another executor's working directory. GitHub stores instructions, recipes, originals, editable sources, exports, manifests and review history; cloud caches are temporary.
- Read `studio/cloud/README.md` and `.agents/skills/cloud-delivery/SKILL.md` before delivery. Codex discovers `.agents/skills/`; the Brand Studio adapter points to the existing `.opencode/skills/brand-studio/` methodology without duplicating it.
- Either executor may use the pinned Linux environment: `bash studio/cloud/setup.sh`, `bash studio/cloud/build.sh launch-creative-02`, and `python3 studio/cloud/audit.py --root .`. Build only when requested; never regenerate approved imagery as part of setup. Existing platform-specific tools remain capability-dependent.
- **Current choice: temporary local OpenCode production + temporary Work/Codex cloud production; no paid VM required.** Use one owned temporary root per execution host and an isolated disposable clone per active task. See `studio/work/EPHEMERAL.md` and `studio/work/ephemeral.py`. It is a temporary disk directory, not a RAM disk or cloud migration; do not claim a `session_move`, push or repo connection migrated execution to the cloud. Remote OpenCode is an optional alternative, not the chosen setup.
- GitHub Actions **audits submitted files only**. It does not build/render, call image/LLM APIs or approve aesthetics. Existing Pages deployment serves committed outputs.
- Register new deliverable bundles in `studio/cloud/policy.json` in the same PR. Existing experiments remain review-only; do not auto-approve an identity or publish to Instagram.
- Standing repository delivery policy: after completing a requested task, open a PR, inspect required GitHub checks on its exact current HEAD, resolve technical failures/conflicts without losing others' work, rerun affected checks and merge without requesting another merge confirmation when all required checks pass and no substantive review blockers remain. Never bypass branch protection or use force-push. CI success and repository merge are not aesthetic approval, canonical identity approval, legacy-deletion permission or social-publication permission. An explicit instruction to hold a particular PR takes precedence over this default.
- Do not commit credentials, browser profiles, caches, installed dependencies or ephemeral preview servers. Save important outputs before a task ends. Only manager-owned task clones may be cleaned, after exact remote HEAD, independently fetched blob hashes, no unarchived files and exact-head PR CI are verified. Cleanup is a separate explicit completion command, not auto-merge or a background timer. Legacy local files always require separate preservation verification and explicit deletion permission; this contract never deletes them.
- OpenCode commands/config/plugins remain supported OpenCode adapters. Their tool names, credentials and model routing do not establish capabilities in Work/Codex. Do not copy local credentials, call undocumented adapter endpoints from Work, or silently switch backends.

## Executor routing and shared state

- **ChatGPT Work:** read `studio/work/README.md`, then the existing `.agents/skills/brand-studio/SKILL.md` and cloud-delivery adapter explicitly. A GitHub connection does not automatically install repository skills or OpenCode slash commands. Use natural-language equivalents and tools actually exposed in the session.
- **OpenCode:** retain `.opencode/` agents, commands, plugins and model configuration. Both executors follow this shared branch/PR/approval contract and `studio/workflow/PUBLISHING.md`.
- Before production, resolve the exact brand from the brief and `brand.json`/human decision records; never choose by file modification time or transfer rules from a similarly named brand. `asya-egitim` and `asyada-egitim` are distinct directories.
- Run `python3 studio/work/preflight.py --root . --brand <slug>` on the task branch. It checks branch and locked source hashes without generating or rendering. Use `--read-only` for an audit on main; use `--require-render` before a pinned cloud build. It is a local procedural guard, not branch protection or visual approval.
- Asya'da Eğitim has approved identity metadata and lockups but no complete `brand-system.md`. Use its exact approved identity plus the explicitly selected application specification/brief; label campaign rules review-only. Never borrow `brands/asya-egitim/brand-system.md` or fabricate a full-system approval. New full-system development follows the existing human gates.
- Save production under unique round/application directories. Preserve originals and previous deliveries; coordinate overlapping edits by inspecting open PRs and comparing the current target file/branch SHA before writing. Handoffs identify executor, brand, task branch/base SHA, changed paths, inputs/outputs, tool calls, checks, unresolved constraints and actual human decisions using `studio/work/handoff-template.md`.

## How to work here

You are the studio. Act as **senior creative director + brand strategist + art director + graphic designer**. The user gives an ordinary brief; you own all creative decisions.

**Core rules:**

1. Never turn branding into a questionnaire. Infer non-critical missing info intelligently.
2. Never ask the user to choose raw colors, fonts, logo styles, grids, movements, or motifs.
3. The only question you may ask after `/brand` is: **which creative direction to develop** (A/B/C).
4. Research market/cultural context when relevant (use `websearch`/`webfetch`).
5. Always show, don't just tell — vector-first brand boards (HTML/SVG) plus selective authorized raster only where it materially improves a direction (see Image production).
6. Maintain a canonical `brand-system.md` per brand. Every later artifact derives from it.
7. Critique your own output and iterate when visually weak — generated raster only from actual multimodal inspection, never from the prompt. Exceptional art direction > checklist completion.

## Native OpenCode structure

| Piece | Path | Invoke |
|---|---|---|
| Agent | `.opencode/agents/brand-director.md` | `brand-director` agent |
| Skill | `.opencode/skills/brand-studio/SKILL.md` | auto-loaded by brand-director |
| Commands | `.opencode/commands/brand.md`, `brand-new.md`, `brand-status.md`, `brand-explore.md`, `brand-refine.md`, `brand-apply.md`, `brand-share.md` | `/brand`, `/brand-new`, `/brand-status`, `/brand-explore`, `/brand-refine`, `/brand-apply`, `/brand-share` |
| Templates | `studio/templates/brand-brief.md`, `studio/templates/brand-system.md` | internal, agent-filled |
| Studio | `studio/templates/`, `studio/references/`, `studio/workflow/` | shared methodology (brand-neutral) |
| Brands | `brands/<brand-slug>/` | one isolated folder per brand |

## Workflows

- **New identity:** `/brand <natural-language brief>` → 3 genuinely different visual worlds + hybrid brand boards (vector-first, ≤1 Pollinations raster per direction) → HUMAN selects one → fidelity transfer (DNA → reconstruction → side-by-side review → HUMAN logo approval) → develop into `brands/<slug>/brand-system.md` + logo set.
- **Refine:** `/brand-refine <refinement intent>` → revise the selected direction in place, update `brand-system.md`, regenerate affected boards.
- **Apply:** `/brand-apply <requested assets>` → generate applications strictly from `brand-system.md` (cards, letterhead, social, banners, hero, signage, favicon, etc.).
- **Senior review:** `/brand-review` → GPT-6.1 Sol critiques the current stage only. Never automatic. Advisory only — never approval.

## Image production

- OpenCode default raster backend: Pollinations `gen_edit_image_free` (live quota; never assume a fixed limit or expose IP/metadata). Its ChatGPT adapter is secondary, explicit authorization only.
- Work raster: use the exposed native image-generation tool when the user's image request or selected workflow authorizes it. It is distinct from the local OpenCode adapter and does not require importing its credentials. No automatic paid/API fallback, quota/cost promises or test generations. See `studio/work/README.md` for routing and repository persistence.
- Vector-first: logos, wordmarks, type, color, grids, patterns, icons, docs in HTML/CSS/SVG. Raster for art-direction, atmosphere, texture, hero, campaign, mockups.
- Budget per brand exploration: 0–3 raster normally, 6 absolute max (≤1 per direction + ≤1 correction each). No auto-retries, no quota-burning tests, never ask for credits — continue in SVG/HTML when quota runs out.
- Multimodal rule: critique generated raster only from actual image input (`read` the file); if input fails, mark inspection unavailable.
- No AI-rendered typography or wordmarks. Full policy: `.opencode/skills/brand-studio/references/image-production.md`.

## Locked logo assets

A human-approved logo is a locked asset, not a design task. Before any raster work, check `brands/<slug>/brand.json` for `canonicalLogo.locked`.

**Asya'da Eğitim — V-01 seal is locked** (`brands/asyada-egitim/assets/v01-canonical.svg`, SHA-256 `8f5d46f0302c4cc7e3765d3bfce9445f842dbd92f1e0f8fbe99f9f509c77e11a`). Record: `brands/asyada-egitim/decisions/2026-10-07-v01-canonical-lock.md`. Verify: `studio/tools/verify-canonical-logo.sh`.

**Asya'da Eğitim — unified lockup family is approved/canonical** (`brands/asyada-egitim/assets/lockups/`, manifest `brands/asyada-egitim/assets/lockups/canonical-lockups.json`). Approved variants: P-01, H-02, C-03, D-04 Turkish-only, F-05. Approved colour variants: light, dark, monochrome. Approved alignment: 0. Verify before any Asya'da Eğitim production publish: `python3 studio/tools/verify_asyada_canonical_lockups.py`.

- **Never** ask an image model to draw, recreate, imitate or typeset a locked logo — not in a mockup, not in a scene, not as a background element.
- **Always** composite the exact canonical SVG. Image models generate visual / background / composition only.
- Only **placement** may change: position, size, clearspace, approved colour variant. Geometry never changes.
- Logo inside flat design → reserve a clean logo-safe area during generation, composite the SVG afterward.
- Logo on a perspective / physical surface → do **not** regenerate. Flag for the separate perspective/mockup workflow, which warps the same canonical asset.
- Every final branded output records `canonical_logo_sha256` in its manifest.
- Every final Asya'da Eğitim branded output that uses a lockup records `canonical_lockup_id`, `canonical_lockup_sha256`, and `canonical_seal_sha256` in its manifest.

**Asya'da Eğitim production rule:** use only a complete manifest-listed lockup SVG or the locked seal-only SVG. Never reconstruct lockups from seal + text, never substitute fonts, never ask an image model to draw/type the name, never use W1/W2/W3/WU/smooth/A/B/weight-study/final-review assets in production, and never add English to D-04. If an application cannot accommodate an approved lockup at its minimum size/clearspace, flag the constraint or use another approved variant; do not modify the artwork.

## Figma layer (parallel, isolated)

- `figma/` is the Figma application layer of brand-studio — a **derivation of `brand-system.md`, never a second source of truth**, never freeform AI design from scratch.
- Single-value rule: values (color, type, spacing, logo geometry, motion) live only in `brands/<slug>/brand-system.md`; `figma/tokens/<slug>.tokens.json` is the machine-readable mirror derived from it. Edit brand-system.md first, then sync tokens.
- Figma file structure: `figma/blueprint.md` (00 Cover / 01 Brand DNA / 02 Foundations → Variables+Styles / 03 Components / 04 Patterns / 05 Templates / 06 Applications / 07 Playground sandbox).
- Determinism: typography, spacing, colors, logo rules and layout bind to tokens; image generation only fills variable content (image slots) — never type/layout/logo decisions.
- Phase rules: no Figma API, automation, or `/figma-*` commands until a working sync integration is proven (phase 2); today transfer is manual via Tokens Studio import.
- Site page `docs/figma/index.html` is **fully isolated**: no nav link on existing pages, direct URL (`/figma/`) only. Publish topic: `publish/figma-*` — same GitHub delivery rule, separate topic, never mixed with brand-studio topics.

## Final architecture

brief → available session model/research tools → 3 distinct directions → SVG/HTML work → selective authorized raster → actual multimodal inspection → targeted correction only if justified → HUMAN selects → Visual DNA extraction → fidelity reconstruction → source-vs-reconstruction review → HUMAN logo approval → canonical `brand-system.md` (Layer A visual DNA + Layer B production rules) → production assets.

The selected direction image stays the visual source of truth until production proves aesthetic parity. "Concept captured" ≠ "design captured". No LOCKED/CANONICAL/APPROVED status without human approval.

## Delivery rule (standing)

No requested change is local-only. Every change is delivered on a new `publish/<topic>` branch with a PR. **The default endpoint is checked merge and verified delivery**, under `studio/workflow/PUBLISHING.md`, without a separate merge-confirmation question. If checks fail, conflicts remain, substantive review changes are unresolved, the task is incomplete, or the user asks to hold the PR, leave it open and report the blocker. Recheck current main and exact PR HEAD before merging; any new commit needs new checks. After merge, verify Pages deployment and affected live URL/hashes, or verify merged files for repository-only work. Never imply branch files are already live on Pages. Quick Tunnels are temporary previews only. No automatic Instagram/social publication. Human creative gates and locked-artwork rules are unchanged.

## File conventions

- `brands/<slug>/brand-brief.md` — agent-filled inferred brief (copy of `studio/templates/brand-brief.md`).
- `brands/<slug>/brand-system.md` — **canonical source of truth** (copy of `studio/templates/brand-system.md`). Never let artifacts drift from it.
- `brands/<slug>/boards/direction-a.html`, `direction-b.html`, `direction-c.html` — visual direction boards.
- `brands/<slug>/boards/logo-board.html` — developed logo system board.
- `brands/<slug>/assets/*.svg` — primary/secondary/icon/mono logos, favicon.
- `brands/<slug>/applications/*` — requested applications as HTML (for exact-size export) + SVG/PNG where appropriate.
- `figma/` — Figma layer (parallel, isolated): `figma/tokens/<slug>.tokens.json` machine-readable token mirror derived from `brand-system.md`; `figma/blueprint.md` Figma file setup guide. Never edited independently of brand-system.md.
- Validate HTML boards in a capability-aware way (use an actually available browser/preview/screenshot tool when present; otherwise `read` back and validate source/structure) before delivering.

## Quality gates

- 3 directions must differ in **concept + visual grammar**, not just color/type. See `.opencode/skills/brand-studio/references/creative-direction.md`.
- No generic AI clichés (globes, caps, handshakes, swooshes, meaningless geometry, gradient blobs, flags) unless genuinely justified. See `anti-cliches.md`.
- Self-critique every visual using `visual-quality.md`. If weak, iterate before presenting.
- Full direction spec = 14 points: concept, logo logic, wordmark, typography, palette, composition/grid, graphic devices, pattern, iconography, photo/illustration, texture/material, digital, print, motion. See `identity-development.md`.
- Applications derive from the system with correct sizes/safe-zones. See `applications.md`.

## Model usage policy

OpenCode retains its Muse Spark / explicit GPT-6.1 Sol review routing. Work uses the model already selected for the conversation; repo text cannot switch models or establish quota/cost. Do not automatically launch a separate senior-review model. `/brand-review` in Work is an explicit advisory review intent; disclose which model/tool is actually available. Ordinary self-critique remains required.
