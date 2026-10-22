# Editorial Campaign — candidate style family (v0.1.0)

**Brand:** `asyada-egitim` · **Category:** `instagram-carousel` · **Style ID:** `editorial-campaign` · **State:** `review-only`.

This file is an art-direction proposal and a test contract, **not** a human approval of a new identity, canonical type system or style. The only approved identity is the exact `brand.json` and canonical lockup manifest. The original user brief and approved Turkish wording always win.

## Why these four references form one family

- [Carousel 01](../../../../../../docs/instagram/carousel-01/) — photo windows, sparse paper compositions, compact lockups.
- [Carousel 01 v2](../../../../../../docs/instagram/carousel-01-v2/) — clearer repeatable logo placement, photo/type rhythm.
- [Carousel 01 v3](../../../../../../docs/instagram/carousel-01-v3/) — strong alternating paper/ink/red pages and headline hierarchy.
- [Carousel 02](../../../../../../docs/instagram/carousel-02/) — related layout grammar with different opening questions and stronger contrast.

These are **candidate references**, not four locked templates. Their review manifests say human approval was pending. Variation changes composition and color distribution within one coherent family; style identity is not equivalent to a single screenshot.

## Visual grammar

**Must be recognisable:** strong Jost display type; editorial information hierarchy; alternating image/type counterpoint; measured negative space and clear separation of primary message, support, and CTA; exact manifest-listed `P-01` or `D-04` SVG; familiar cream (#F7F3E9), ink (#1D2027) and crimson (#BD2120) anchors. Only the identity itself is canonical; the visual grammar is a proposed campaign layer.

**May vary:** cover archetype, background rhythm, image window/crop, alignment, content density, location of lines/meta, CTA presentation, photo density, and the balance between photographic and type-led slides. `interior_bias` is only a bias; mixed sequencing is encouraged. The logo may move to a safe position, but may never deform or be retypeset.

**Paper as institutional default:** paper is the expected recurring high-frequency brand surface, not a mandatory background on every slide. For five slides, a *guideline* is at least three paper-dominant frames and one deliberate contrast change. `paper-red-balanced` and `dark-contrast-accented` presets intentionally relax that heuristic. Consider the whole sequence; do not color every slide the same, and do not force red to dominate by default.

**Prohibited:** repetitive template stamping, five identical color blocks, AI-drawn copy or brand name, independent wordmark reconstruction, arbitrary additional colors, generic globes/airplanes/caps, invented campus claims, unauthorized photo use, loss of Turkish diacritics, inappropriate small logo rendering.

## UI selection contract

A future UI should expose `Brand → Category → Style family → Preset → Advanced variations`. The **style family** remains one ID even when a preset or override differs. It should not create a separate style entity for each variation combination.

| Preset ID | Label | Intended use |
| --- | --- | --- |
| `institutional-paper` | Kurumsal krem | Default; information or trust-led posts |
| `campaign-dynamic` | Dinamik kampanya | Aspirational launch or strong rhythm |
| `photo-editorial` | Fotoğraf odaklı editoryal | Student/campus photo stories |
| `ink-accent` | Kontrast vurgulu | Concise high-impact messaging |

The six variation axes and their allowed values live only in `style.json`. An advanced user may override individual axes; invalid values should fail loudly. Never infer a different brand because a style with the same name exists elsewhere.

### CLI smoke check (read-only)

```sh
python3 studio/production/router.py --executor chatgpt-chat \
  --brand asyada-egitim --category instagram-carousel \
  --capability github-read --list-styles

python3 studio/production/router.py --executor chatgpt-chat \
  --brand asyada-egitim --category instagram-carousel \
  --capability github-read --style editorial-campaign \
  --preset institutional-paper --variation layout_rhythm=dynamic
```

The router prints a **candidate plan**. It does not build a carousel, select a model, render in a browser or verify aesthetic quality. The chosen family/preset/variation should subsequently be recorded in the asset manifest if a real production happens.

## Controlled reproducibility trial — not yet executed

Produce **three separate five-slide carousels**, each as editable HTML/CSS/SVG + real browser-rendered 1080×1350 PNG, using the real `P-01` or `D-04` complete SVG and preserved photo provenance:

1. **A:** "Neden Asya'da üniversite okumalı?" — `institutional-paper`; informative and paper-led.
2. **B:** "Üniversite için başka bir dünya var." — `campaign-dynamic`; distinct splits/crops/red contrasts.
3. **C:** "Japonya'da öğrenci hayatı" — `photo-editorial`; same family, different topic, more imagery.

**Acceptance tests (separate judgments):**

- Family recognition: human sees all three as one related family when mixed with earlier Carousel 01 / v2 / v3 / 02.
- Non-duplication: at least three slide layout archetypes per five-slide series; varied background and image treatment; not screenshot recolors.
- Color behavior: paper returns as main brand surface where the chosen preset calls for it; accent/color contrast follows selected variant.
- Production: originals + editable HTML/CSS/SVG + real PNGs + verified SVG SHA, 1080×1350, no text clipping/contrast failures.
- Evidence: run summaries record `brand`, `category`, `style_id`, `version`, `preset_id`, resolved variations, git SHA and comparison images; human approval remains pending until explicitly given.

The three output trials require a separate actual production run and human visual review. No success/repeatability score is asserted by this spec. Previous productions must not be overwritten.
