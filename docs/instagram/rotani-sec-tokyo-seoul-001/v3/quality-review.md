# Quality review — Rotanı Seç #001 / V2

## What changed against V1

V1 was a competent editorial carousel with four defects this revision fixes:

| V1 defect | V2 fix |
|---|---|
| Absolute-positioned copy with hand-chosen x/y, verified only by collision test | Structural CSS Grid/Flex containers; every text block measured in-browser and re-composed as SVG from those measurements |
| Automatic baseline offset pushed glyphs below the CSS line box, causing overlaps where line-height was tight | Baseline computed from real font metrics: `top + (lineHeight - fontSize)/2 + fontSize * 0.75` |
| Dark lockup variants on light grounds (white wordmark invisible) | Automated logo-contrast gate that samples the true ground — including the lockup's own opaque chip — and requires the matching approved variant |
| H-02 placed at 330px, below its approved 528px minimum | H-02/dark raised to 540px with an automated minimum-size assertion |

V2 also replaces V1's content with the new six-slide contract: admission-letter cover, Songdo campus geography, six university atlas, English-taught study, accommodation costs, and decision CTA.

## Geometry audit

`geometry-audit.json` records, for every slide:

- measured bounding box of each text block (line boxes, not generous ink bounds)
- parent container and whether the block escapes it
- text/text, text/decorative, text/logo intersection areas
- logo box, variant and minimum-width compliance
- Jost font load state and image load state

Current result: **6/6 slides, 0 unintended overlaps, 0 clipping, 0 logo collisions.**

## Self-correction log

Six real defects were found by measurement and inspection, then fixed and re-rendered:

1. **Sheet 01** — headline/support overlap from the baseline formula → fixed formula.
2. **Sheet 05** — `₩350.000–550.000*` wrapped mid-string and collided with the EUR line → `white-space:nowrap` plus a smaller, still-dominant price size; EUR kept visibly smaller.
3. **Sheet 06** — decorative "Tokyo/Seul" labels were counted as contract copy → moved to `data-decor`, still rendered and still audited.
4. **Sheets 04/05** — inline `<b>`/`<em>` boundaries dropped the source space ("fakültedeİngilizce") → whitespace preservation plus `xml:space="preserve"`.
5. **Sheet 06** — H-02 at 330px violated the approved 528px minimum → 540px.
6. **Sheets 01/06** — signature contrast mismatches → `D-04/dark` on the dark cover, `H-02/dark` integrated into the dark finale with no paper band.

## Typographic system

One typeface (Jost). Measured type scale on a 1080px canvas:

| Role | Slide 01 | 02 | 03 | 04 | 05 | 06 |
|---|---|---|---|---|---|---|
| Headline | 104 | 48 | 50 | 52 | 47 | 58 |
| Secondary | 44 | 31 | 26 | 34 | 33 | 64 |
| Body | — | 29 | 24 | 24 | 24 | 24 |
| Labels | 21 | 22 | 21 | 23 | 19 | 19 |
| Footnotes | — | 29 | — | 26 | 23 | — |

Critical text carries 56–58px outer margins. Adjacent groups keep measured separation. No extreme negative tracking is used on body copy.

## Visual direction

Two ground treatments repeat deliberately: dark cinematic scrims on slides 01, 04 and 06; paper-based light grounds on 02, 03 and 05. Inside each, compositions differ — diagonal split, two-column documentary band, campus atlas, split photo field, price grid, and a mirrored photographic callback.

Tokyo reads cyan/steel, Seoul reads pink, interaction reads acid lime; red, ink and paper stay the brand anchors. Colour is applied as grading and accent, not as a full-slide wash.
