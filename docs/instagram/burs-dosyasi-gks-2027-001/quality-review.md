# Burs Dosyası / 001 — GKS 2027 · quality review record

## Automated gates (all PASS)
- **Exact copy**: every locked string from the campaign specification is present on its slide,
  verified twice — in-page DOM capture vs `copy-manifest.json`, and SVG `<text>` join vs
  `data-exact-copy-json` (see `manifest.json` → copy_validation).
- **Geometry**: `qa/geometry-report.json` — canvas bounds, 64 px safe area, text clipping,
  text↔text and text↔logo overlap measured after `document.fonts.ready`. 0 errors on all six slides.
- **Typography**: real Jost variable font metrics; Turkish glyphs (ğ, ş, ı, İ, â, Ü) confirmed in the
  rendered PNGs; no hardcoded line-height below glyph requirements (all line-heights ≥ 1.0 with
  font-metric-aware baselines in the SVG masters).
- **Hierarchy (slide 05)**: KRW figure 122 px vs EUR 54 px ≈ 2.26× emphasis; EUR sits directly below
  KRW on the same left axis; asterisk retained and resolved by the exchange-rate note.

## Visual review (actual image inspection, 1080 px and 375 px)
Defects found and fixed during production, each corrected in source and re-rendered:
1. Slide 01 — the strike-through crossed the emphasis sentence; date graphic and strike were moved
   into the clear zone between the paragraph and the bottom lockup band.
2. Slide 02 — orphan word in the header (manual two-line break); timeline dots re-aligned to the
   measured date baselines; D-04 lockup added to the footer for complete brand presence.
3. Slide 03 — orphan word in the headline (two-line break at 48 px); the giant 100 was integrated
   with the engineering photograph as required.
4. Slide 06 — the single-choice path node collided with the service sentence; the path was shortened
   and the node re-seated on the line.
5. Slide 05 — the KRW line overflowed the safe area at 128 px; set to 122 px (2.26× EUR emphasis).

Contact sheet, mobile strip (375 px) and source-vs-final sheet were inspected as images after the
final render. Distinct backgrounds: 01 photo/ink, 02 paper editorial, 03 warm neutral, 04 deep paper,
 05 ink financial, 06 photo/ink — no repeated beige template.

## Colour revision — Korean blue #003478
The campaign replaces brand red `#BD2120` with Korean blue as its single accent. The colour is
authored in exactly one place, `svgmaster.py`, and propagates through `source/NN.svg` →
`export/NN.png` → `original/NN.png` → ZIP → published gallery.

A first pass converted only a subset of the accent sites and left brand red on primary elements
(the headline line and its rules on 01, "13 Ekim 2026 itibarıyla." on 02, the "100" numeral on 03,
the TÜRK VATANDAŞLARI band on 04, the CTA band on 06). That partial state was incorrect and has been
superseded by a full conversion of the remaining nine sites.

`#BD2120` is retained **only** inside the linked canonical lockup SVGs under `assets/lockups/`.
Those are locked, human-approved assets, linked by reference and never edited, recoloured,
redrawn or re-typeset.

Verified after the re-render, by inspecting each exported PNG as image input:
- `#BD2120` occurs **zero** times in `source/01.svg`–`06.svg`.
- On every export, all remaining red-family pixels fall inside that slide's canonical-lockup
  bounding box from `manifest.json`. Red outside the logo is **0 on all six slides**.
- `studio/tools/verify_asyada_canonical_lockups.py` passes — 15 records, seal `8f5d46f0…c77e11a`.
- Copy, geometry and Jost gates re-ran clean (0 errors, all six slides, 1080×1350).

## Slide 01 headline copy and accent-line legibility (both at human request)
Copy changed from "Kore devlet bursunu kaçırdın mı?" to "Kore devlet bursunu kaçırdım diye üzülme."
— a reframe that addresses the reader's family rather than asking the reader a question, and sets up
the "Ama üniversite yolunda Ekim son tarihleri var." turn below it. The line is 12 characters longer,
so the CSS prototype was re-measured (`build.py --css`) rather than hand-fitted: the accent line
measures 690.1 px in the 920 px `.q` column (229.9 px spare), the block still ends at 338.2 px
against the next block at 404 px (65.8 px clearance), and the right edge lands at 762.1 px, well
inside the 1016 px safe limit.

Separately, the accent line in `#003478` sat over a darkened photograph and its glyph edge was lost
against the mid-tone sky and buildings — it read as disappearing. Fixed with a two-stage black drop
shadow on **that line only** (`#04070C`, dy 6 / blur 9, plus a tight dy 1 / blur 1.5 contact pass),
declared once in `svgmaster.py` as `QS_SHADOW` and applied per line through the `line_extra`
argument added to `text_el()`. The cream line above it and every other slide are untouched; the
filter appears in `source/01.svg` only.

Measured on the exported PNG before and after, across the line's own bounding box:
- median luminance of the 1 px ring immediately around the glyphs: **0.0571 → 0.0116**
- brightest ring pixel (98th percentile): **0.1217 → 0.0520**
- glyph-to-ring contrast: **1.22:1 → 1.43:1**

Confirmed by inspecting the export as image input at 1080 px and again at the 375 px mobile
preview: the accent line reads cleanly at both.

Note: the locked copy lives in three places — the `COPY` dict and the CSS prototype in `build.py`,
and the `copy_group` literals in `svgmaster.py`. `copy-manifest.json` is generated from `COPY`.
`Slide.render()` compares the two and aborts on drift, which is the intended guard; when copy
changes, all three must be updated together.

## Remaining constraints (disclosed, not blocking)
- Photography is licensed Wikimedia Commons imagery; correct identification of KOREATECH, Ajou,
  Kookmin buildings and Korean campuses. Not a claim of partnership or admission.
- Human creative approval is still pending. Social publication is not authorized.
