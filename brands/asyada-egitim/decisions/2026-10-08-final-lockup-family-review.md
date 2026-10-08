# Final lockup family — human approval review

**HUMAN FINAL LOCKUP APPROVAL PENDING.** The user selected Jost 550 Turkish
and Jost 350 English. This is a typography-direction selection, not approval
of a final lockup, alignment, minimum-size rule or canonical brand system.

## Immutable inputs and delivery

- Canonical seal file untouched, checksum
  `8f5d46f0302c4cc7e3765d3bfce9445f842dbd92f1e0f8fbe99f9f509c77e11a`.
- Existing selected outline source:
  `docs/asyada-seal/typography-weights/assets/tr550-en350-wordmark.svg`;
  SHA-256 `668c0026043cf6ab2496c67feca152da37ad8348d2b6641a354a841b58e375f3`.
- All glyph paths AND per-glyph translations copied exactly. No font instancing,
  tracking correction, punctuation redraw, outline smoothing or type redesign.
- Retained red apostrophe is the prior source-matched comma correction already
  in the selected source, not a new claim of literal JPEG/raster fidelity.
- Original seal 400:370 viewport and edge clipping retained through nested SVG.
- Monochrome uses approved ink/paper variants with transparent knockout features;
  no edited canonical shape or baked-white rectangle.

## Five arrangements

| Variant | Role | Proposed minimum (full canvas width) |
|---|---|---|
| P-01 | Primary stacked | 352px / 75mm |
| H-02 | Primary horizontal | 528px / 110mm |
| C-03 | Compact horizontal | 448px / 95mm |
| D-04 | Two-line Turkish small-use / digital | 200px / 45mm |
| F-05 | Formal bilingual, larger centered crest | 352px / 75mm |

P/H/C/F use the same three-line 881-unit wordmark and fixed 140/139/35 cap rhythm.
D uses its identical two-line Turkish subset; English omission is **explicitly
pending human confirmation**, necessary to avoid illegible English at small size.
Below D's minimum, the exact seal-only companion has a proposed minimum 32px;
16px fine detail is not claimed as reliable and no new simplified icon is drawn.

Clearspace is 70 native units outside all ink, including every offset extreme.
The **−4 / 0 / +4 / +8** options are genuine relative wordmark shifts. The seal
never moves with the lettering. Zero is an existing mechanical comparison anchor,
not a chosen optical alignment. Historical comparisons remain unchanged.

## Proofs and validation

- 80 lockup SVGs: 5 roles × 4 approved colour treatments × 4 offsets.
- 4 exact-seal companions, 5 standalone self-contained HTML application proofs.
- Every published branded asset records canonical seal and source outline hashes.
- Independent final-file checks: exact source glyph/translation equality, original
  seal geometry/aspect/viewport equality, shared 881 measure, all offsets, clearspace,
  no text elements/font dependencies, no image elements or image-generation calls.
- Native minimum-size SVG raster proofs visually inspected in all four treatments.
- 4× device-pixel minimum-size renders retain every expected component/counter.
- At 1×, a hard 50% alpha mask can break the light English outlines at isolated
  pixels; these diagnostics are disclosed, not misrepresented as perfect pixel
  topology. Actual antialiased proofs are visually readable at proposed minima.
- Main type contrast 14.71:1. Original red accent on paper 5.57:1; red on dark
  2.64:1 (logo accent, not normal text). Mono paper recommended when high-contrast
  small-size reverse usage is needed; the original red accent is not recoloured.
- Headless Chrome screenshots actually captured/read for the review masthead
  and all five application proofs. No image-model output.

## Files and gate

- Review: `docs/asyada-seal/final-lockups/`.
- Draft specification / source assets / screenshots:
  `brands/asyada-egitim/explorations/final-lockup-family/`.
- Builder, verifier, proof renderer: `studio/tools/*final_lockup*.py`.
- No approved asset, `brand.json`, historical alignment asset or canonical
  system modified. No final lockup approval claimed.
