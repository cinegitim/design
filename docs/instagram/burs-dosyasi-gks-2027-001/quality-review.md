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

## Remaining constraints (disclosed, not blocking)
- Photography is licensed Wikimedia Commons imagery; correct identification of KOREATECH, Ajou,
  Kookmin buildings and Korean campuses. Not a claim of partnership or admission.
- Human creative approval is still pending. Social publication is not authorized.
