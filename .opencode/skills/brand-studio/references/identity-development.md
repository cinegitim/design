# Identity Development — From Selected Direction to Coherent System

How to turn the winning world into a buildable identity WITHOUT losing its aesthetic character. Read this whole file before touching production assets.

## Order of operations (fidelity pipeline)

1. **Human direction selection** (gate — never auto-select).
2. **Visual DNA extraction** (§Visual DNA): decompose the source image before any redesign. Document proportions, type character, rhythm, tension, light, density — and separate ESSENTIAL aesthetic features from INCIDENTAL generation artifacts. Never "clean up" an essential feature for coding convenience.
3. **Fidelity reconstruction**: rebuild toward the source (RECONSTRUCT → REFINE → SYSTEMATIZE → TEST), never interpret-simplify-replace. Geometry serves appearance; no post-hoc ratio mythology, no symbolic explanations invented after the fact. Preserve productive imperfection (optical imbalance, irregular rhythm, controlled tension) unless regularization visibly improves the result.
4. **Source-vs-reconstruction review**: render both, compare side by side, judge "does this still feel like the same brand?" If the source looks materially better, production is NOT finished — iterate the implementation, never the direction.
5. **Human logo/identity approval** (gate — AI review is advisory only; no LOCKED/CANONICAL/APPROVED status without it).
6. Fill `brand-system.md` (two layers, below). Everything else derives from it.
7. Then SVGs, then boards, then applications. If a later decision contradicts the system, update the system first.

## Visual DNA checklist (extract from the source image)

Dominant proportions · logo-to-wordmark ratio · type character + construction · spacing/rhythm · scale relationships · whitespace behavior · alignment logic · density · contrast hierarchy · border/shape/corner behavior · crop/texture · asymmetry · foreground/background · color relationships · source of premium feeling · source of tension (incl. productive imperfection).

## Two-layer brand system

- **LAYER A — VISUAL DNA**: what must survive visually (proportions, type character, tension, rhythm, mark/image behavior, scale relationships).
- **LAYER B — PRODUCTION RULES**: fonts, tokens, SVGs, spacing, components, responsive, accessibility, applications.
- Layer B exists to reproduce Layer A and must never replace it.

## Logo set (minimum)

- `logo-primary.svg` — full lockup (symbol + wordmark, horizontal). Default use.
- `logo-secondary.svg` — stacked lockup (symbol above wordmark, centered).
- `icon.svg` — symbol only. Must hold at 16px. One distinctive feature, no thin strokes that vanish, no `<text>` dependency.
- `logo-mono.svg` — single-color version (black + white via `currentColor` or paired files).
- `favicon.svg` — simplified icon on rounded square; test at 16/32/180px.

Rules: primary/secondary/icon share construction (same geometry, stroke, corner logic). Clear space = height of icon (or x-height of wordmark) on all sides. Min widths: primary 120px print / 96px screen; icon 24px absolute min. Document 6 misuses: rotate, stretch, recolor, effects, busy background without container, crowding.

## Color system (roles, not just swatches)

Primary 1 · Secondary 1–2 · Neutrals (paper/ink scale) · Accent 1 · Semantic (success/warning/error/info) only if digital product exists. For each: hex + RGB + CMYK/Pantone note when print matters + usage + proportion (e.g. 60 neutral / 30 primary / 10 accent). Verify text/background pairs meet WCAG AA (4.5:1 normal, 3:1 large) and note the ratios.

## Typography system

Display + text (+ mono/accent if needed), max 2–3 families total. For each: role, weights used, fallback stack ending in generic family, scale ratio, line-height/spacing rules. Render specimens on the board (headline, body, numerals, label/microcopy) — never list names alone. Note licensing if a commercial font is specified.

## Tokens

Mirror colors/type/space/radius in `:root` CSS variables so applications copy-paste. Example shape:

```css
:root {
  --brand-primary: #1B2A4A;
  --brand-secondary: #C8A96A;
  --bg-paper: #FAF7F0;
  --text-ink: #1A1A1A;
  --font-display: "Fraunces", Georgia, serif;
  --font-text: "Inter", system-ui, sans-serif;
  --space-unit: 8px;
}
```

One-click copy controls on the HTML board for hex + tokens.

## Logo board (`boards/logo-board.html`)

Self-contained HTML. Sections: large primary on light · dark/inverted · mono black/white · app-icon/circle-crop test · clear-space diagram (x-boxes) · construction grid + geometry callouts · min-size row (16/32/48/180px) · misuse row · application strip (3 real touchpoints). Preserve SVG aspect ratios (`object-fit: contain`, never stretch).

## Imagery production

Logos, wordmarks, and type stay vector (SVG/HTML). Raster direction imagery and photographic layers go through Pollinations `gen_edit_image_free` per `image-production.md` (quota-checked, budgeted, multimodally inspected). Never AI-render the wordmark or final typography.

## Verification before presenting

- Icon recognizable at 16px; no strokes vanish; contrast holds on every background; nothing touches circle crop.
- All 14 direction points resolved into buildable rules (no "premium feel" without a visible decision).
- `brand-system.md` complete — no TODOs. Coverage checklist at the end marked.
