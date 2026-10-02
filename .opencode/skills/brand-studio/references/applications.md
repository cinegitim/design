# Applications — Deriving Assets from the System

Every application derives strictly from the canonical `brand-system.md`. No orphan colors, fonts, devices, or layouts. If the system lacks a needed token, update the system first.

## Derivation rule

For each asset, list the system tokens used (colors, fonts, grid, devices, imagery rule). If you can't trace a choice to the system, it's wrong.

## Sizes and safe zones

| Asset | Size | Rules |
|---|---|---|
| Business card | 85×55mm (or 3.5×2in) | Name 14pt/700 display, title 9pt uppercase brand color, contact 8pt gray; logo clear space respected |
| Letterhead | A4 | Margin ≥20mm; header lockup left, footer microcopy; body in text font |
| Envelope | DL / C4 | Icon or secondary lockup; minimal addressing zone |
| Flyer / poster | A5–A2 | One focal point; headline ≥3× body; 12-col or system grid |
| Brochure | A4 spread | Cover system + inside rhythm from print behaviour |
| Presentation | 16:9 (1920×1080) | Title/body/master + cover/section/quote layouts |
| Social post | 1080×1080 | Logo in safe corner; headline inside central 80% |
| Story | 1080×1920 | Critical content in central 70–80%; min 44px CTA |
| LinkedIn banner | 1584×396 (personal) / 1128×191 (company) | Keep subject central; test crop |
| X header | 1500×500 | Critical content central 70% |
| YouTube art | 2560×1440 (safe 1546×423) | Logo + tagline in safe area only |
| Web hero | 1920×600–1080 | One headline + one CTA (bottom-right or left-aligned); max 2 fonts; headline ≥32px |
| Event / signage | variable | Max contrast; min 24px-equivalent legibility at distance; mono variant preferred |
| Favicon | 32 ICO / 180 Apple / 192+512 PWA / SVG modern | Simplified icon, padded for circle crop (mark ≈55% of canvas) |
| Email header / signature | 600–1200px wide / table layout | 48px mark, brand-color rule, Arial + inline styles for signature |

General: critical content in central 70–80%; one CTA per asset; max 2 fonts; min 16px body (screen); print 300 DPI + CMYK + 3–5mm bleed.

## Build method (hybrid: vector-first, Pollinations raster)

- Layouts as self-contained HTML (inline CSS, system tokens, inline SVG marks) in `brands/<slug>/applications/`.
- Marks as standalone SVG in `brands/<slug>/assets/`, referenced or inlined. Never AI-generate logos or wordmarks.
- Raster layers (photographic/illustrative direction, atmosphere, texture, hero): Pollinations `gen_edit_image_free` by default, composited under system typography/layout; ChatGPT adapter only on explicit authorization. Read quota live first; continue in CSS/SVG if quota runs out.
- For exact-pixel export, screenshot HTML at the exact size (e.g. headless Chromium) and `read` the result before delivering.

## Verification

- [ ] Tokens trace to `brand-system.md`
- [ ] Clear space + min sizes hold
- [ ] Contrast AA on every text layer
- [ ] Exact dimensions + safe zones respected
- [ ] Previewed/validated and self-critiqued per `visual-quality.md`; raster layers inspected as actual multimodal input
