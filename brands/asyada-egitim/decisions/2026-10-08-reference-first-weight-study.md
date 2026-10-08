# Reference-first typography weight review — 2026-10-08

## Human decision and scope

- Candidate B is **REJECTED**. Its geometry and previews are not regenerated.
- Candidate A / Jost 700 is **NOT APPROVED**.
- The original supplied `reference.jpg` is the visual authority.
- This is a weight study within Jost, not new brand directions, a custom
  alphabet, or a logo approval. No winner or optical alignment is selected.
- Status: **HUMAN TYPOGRAPHY REVIEW PENDING**.

## Reference measurements

Measured on original pixels, excluding red from neutral-letter analysis.
The primary threshold is L<140 (approximately 50% edge coverage). JPEG and
anti-aliasing introduce roughly ±1 native-pixel uncertainty; English ratios
are particularly sensitive because the caps are only 35px high.

| Row | Flat cap | Vertical probe median | V/cap | Horizontal probe median | H/cap |
|---|---:|---:|---:|---:|---:|
| ASYA’DA | 140px | 28px (D) | .200 | 24px (A crossbars) | .171 |
| EĞİTİM | 139px | 23px (E/I/T/M) | .165 | 22px (E/T bars) | .158 |
| EDUCATION IN ASIA | 35px | 5px | .143 | 4px | .114 |

Mean glyph-box filled fraction, excluding I's always-full rectangular box:
TR1 45.2%, TR2 47.3%, English 39.9%. This is descriptive, not an approval score.
Per-glyph width/height, counter bounds, gaps, diacritics, threshold sensitivity
and original-file SHA-256 are in `weight-study/measurement.json`.

The earlier cap-top=80 / apostrophe-overshoot=12px interpretation is not used.
The flat TR1 cap is at y=69; the original red comma begins at y=68. Ordinary
round and pointed overshoots are distinguished from the flat-cap reference.

## Real-font experiments

- Turkish: 400, 450, 500, 550, 600, 650.
- English: 200, 250, 300, 350, instantiated independently from Turkish.
- All letter geometry comes directly from Jost variable-font outlines.
- Scale is uniform, determined by the actual flat E outline height. No glyph
  is stretched, condensed, sheared or traced. A/M pointed overshoots remain.
- Measured source gap rhythm is retained with one additive tracking correction
  per line to achieve the existing 881px common measure.
- Review subset: Turkish 500/550, English 300/350, based on the closest sampled
  stem measurements. Advisory only; all weights and all 24 lockup pairings
  remain available. The initial preview is not a winner or human selection.
- Jost's slab-shaped U+2019 was visibly wrong. A single source-matched red comma
  correction uses five intentional cubic segments in the measured 30×49px
  envelope, fixed across all trials. This is punctuation only, not a new font
  or any Candidate B geometry; no raster fitting is used.
- SIL OFL licence and the exact source font are retained with the study.

## Actual rendered findings — no exact-fidelity claim

1. **A:** pointed high apex instead of the original small flat top. Its counter
   is larger/taller at 500: approximately 38×44px versus original 34×39px.
2. **S:** wider, different bowl balance, terminal cuts and spine silhouette.
3. **D:** more open counter at 500: approximately 69×96px versus 57×87px.
4. **G:** incompatible lower-right construction. The source has a squared return
   with a vertical inner edge below its bar; Jost continues around a circular
   bowl. Jost's body is about 141px wide at 500 versus original 128px.
5. **M:** incompatible structure: splayed outer stems, pointed shoulders and a
   sharp V instead of upright stems, flat shoulders and a blunt junction.
   About 153px wide at 500 versus original 138px.
6. **Ğ:** inherits G's mismatch; its breve is deeper and higher than the source.
7. **İ:** genuine dot present; its size and clearance vary with weight. Around
   500 it is about 27×26px versus approximately 24×24px in the source mask.

No single sampled Turkish weight matches both rows perfectly. English 350 is
closest within the requested range but still thinner: vertical approximately
3.5px versus source 5px; horizontal 3.25px versus source 4px. This difference
is visible in the final rendered comparison, not just a numeric discrepancy.
The source is relatively lighter than Turkish, but font weight numbers do not
transfer directly between typeface designs.

## Verification and visual inspection

- All 24 final SVG wordmarks independently rendered inside an expanded canvas:
  25px padding + 1000px visible measure + 25px padding. No clipping-to-measure.
- Every line spans x=0..999 at that scale, with 0px measured edge error.
- All final wordings, red punctuation, Turkish diacritics and expected counters
  present; no inter-letter collision/component merging in the inspected masks.
- 48 final lockups compared to canonical seal element geometry: unchanged.
- Seal retains its exact 400:370 aspect; established sizes/gap/padding remain
  fixed across trials. Previous optical alternatives remain linked unchanged.
- Reference JPEG bytes unchanged. No image-generation calls.
- Direct multimodal inspection: Turkish and English comparison plates, enlarged
  A/S/D/G/M/Ğ/İ, final horizontal and stacked SVG renders.
- Browser DOM check: 103 images, none broken; six TR / four EN options; matching
  close-up canvas dimensions and 50% overlay opacity.
- Requested Muse Spark 1.3 Free multimodal advisory review completed on actual
  images. Independently flagged A/M/G mismatches; factual contradictions are
  reconciled in `weight-study/muse-review.md`. No approval or winner.
- New −4/0/+4/+8 native-pixel alternatives move only the wordmark vertically
  relative to the fixed seal. Historical alternatives stay unchanged. All 192
  new alternatives independently checked for exact relative offset and geometry.
- Desktop screenshots unavailable: the browser reports no visible desktop tab.
  DOM validation and actual SVG raster renders are used, not a claimed screenshot.

Technical checks establish content/placement, not visual approval. Earlier
raster curvature-sign-flip/node counts did not establish typographic quality;
that argument is withdrawn and these metrics are not used in this study.

## Files and delivery

- Review: `docs/asyada-seal/typography-weights/`.
- Source, measurements and inspection plates: `wordmark-ref/weight-study/`.
- Builder: `studio/tools/build_typography_weights.py`.
- Independent verifier: `studio/tools/verify_typography_weights.py`.
- The old `build_type_candidates.py` now routes to this study and cannot
  regenerate B or reinstate the Jost-700-for-both-roles default.
- Historical A/B page explicitly marked rejected/unapproved, not a live
  development source. No canonical system or approved logo files changed.

Canonical seal SHA-256:
`8f5d46f0302c4cc7e3765d3bfce9445f842dbd92f1e0f8fbe99f9f509c77e11a`.
