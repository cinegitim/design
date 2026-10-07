# Unified logo + wordmark geometry

**Date:** 2026-10-08
**Status:** PROPOSED — quality gate 29/29 PASS, awaiting human approval.
**Nothing canonicalised. Canonical seal untouched.**

---

## Two human requirements, which override the reference

1. The canonical seal and wordmark must be precisely aligned.
2. All three text lines must fill the same horizontal measure.

These override the unequal line widths measured from the original raster
(881 / 865 / 856 px). The reference's own proportions no longer govern the
line edges; its letterforms still do.

Starting point: the W3 letterform reconstruction. Only layout geometry changed.

## Step 1 — common measure W = 881 px

| line | ink left | ink right | width | dev L | dev R |
|---|---|---|---|---|---|
| ASYA'DA | 0.00 | 879.68 | 880.12 | 0.00 | 0.32 |
| EĞİTİM | 0.00 | 879.68 | 880.12 | 0.00 | 0.32 |
| EDUCATION IN ASIA | 0.00 | 879.68 | 880.12 | 0.00 | 0.32 |

Worst deviation **0.32 px** against a 1 px tolerance at 1000 px wordmark width.

Reached without stretching. Letters are rigid bodies; only inter-letter gaps
change, by one uniform per-gap delta per line:

| line | natural | target | delta | gaps | per gap |
|---|---|---|---|---|---|
| ASYA'DA | 881 | 881 | 0 | 5 | +0.00 px |
| EĞİTİM | 865 | 881 | +16 | 5 | +3.20 px |
| EDUCATION IN ASIA | 856 | 881 | +25 | 14 | +1.79 px |

Right-edge residual is exactly 0.000 px on every line.

## Step 2 — unified lockup geometry

**Stacked** — seal above, wordmark below

| measurement | deviation |
|---|---|
| seal L / R / T / B | 0.29 / 0.25 / 0.37 / 0.23 px |
| text L / R / T / B | 0.37 / 1.06 / 0.28 / 0.37 px |
| optical centre axis | **0.69 px** |
| seal–wordmark gap | 84.49 px (intended 85, error −0.51) |

**Horizontal** — seal left spanning the full text-block height, wordmark right

| measurement | deviation |
|---|---|
| seal L / R / T / B | 0.46 / 0.94 / 0.46 / 0.48 px |
| text L / R / T / B | 0.75 / 1.40 / 0.46 / 0.48 px |
| vertical centre | **0.00 px** |
| seal–wordmark gap | 85.19 px (intended 85, error +0.19) |

All figures from rendered visible ink: artwork bounding boxes measured
per element with the page background stripped. No viewBox number, declared
width or advance width is trusted.

## Step 4 — quality gate

29 checks, 29 PASS, 0 FAIL.

| FAIL condition | measured | result |
|---|---|---|
| any text line leaves the common measure | 0.32 px | PASS |
| seal and wordmark misaligned | 0.69 px | PASS |
| glyphs visibly distorted | rigid bodies, no stretch | PASS |
| Turkish diacritics damaged | breve + 2 dots, 0 orphans | PASS |
| logo geometry changed | SHA-256 same, 3/3 byte-identical | PASS |

Reference IoU was not optimised for any of these.

## Counter restoration

W3's whole-mask `RETR_EXTERNAL` trace had filled every letter counter solid —
D bowls, A triangles, O and G all measured as ink (32) against paper (243).
Per-component `RETR_CCOMP` tracing with evenodd fill restores them. This is a
restoration of the approved artwork, not a redesign; letterform contours are
unchanged, only the winding relationship between outer ring and holes.

## Six bugs found by measuring, not by looking

1. **Paper read as ink.** `#F7F3E9` converts to L 243, so a `<250` cut made the
   entire background ink and every lockup measurement collapsed to canvas size.
2. **Seal centred on the canvas** instead of the text measure — off by PAD
   (44 px).
3. **Element split a whole seal-height off.** A "first blank row" search caught
   the seal's own whitespace (the D bowl), cutting the wordmark band and reading
   every text edge ~87 px wrong.
4. **Measured in document coordinates, compared against a stale frame** —
   a constant ~87 px error in the report while the render was correct.
5. **Counters filled solid** (W3 trace defect, restored above).
6. **Counter probe read one wrong pixel.** The D bowl at x=700 is the stem; the
   counter is the light run between stems. The probe must scan a range.

## Seal policy

`canonical_logo_sha256` `8f5d46f0302c4cc7e3765d3bfce9445f842dbd92f1e0f8fbe99f9f509c77e11a`,
verified intact. Three lockups (stacked / horizontal / horizontal-dark); seal
path data and rect geometry compared byte-for-byte: **0 deviations**. Only
placement and the approved `mono-paper` colour variant differ.

## Production

Deterministic: `studio/tools/build_unified.py`, `build_unified_lockups.py`,
`verify_unified.py`, `quality_gate.py`. Real traced contours as SVG path data,
no `<text>` element. **Image-generation calls: 0.**

## Open

- Nothing canonicalised; awaiting human lockup approval.
- The earlier 5-lockup family remains uncanonicalised history.
