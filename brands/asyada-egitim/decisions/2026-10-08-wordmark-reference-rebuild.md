# Wordmark rebuild from the approved typographic reference

**Date:** 2026-10-08
**Status:** PROPOSED — three candidates awaiting human selection. **Nothing canonicalised.**
**Canonical seal:** untouched, verified intact.

---

## Why the previous Helvetica construction did not match

The previous round optimised for internal consistency: the measure was derived
from the text, all three lines were justified to one common measure, and a
single vertical rhythm was applied throughout. The reference is not internally
consistent — it is optically balanced. Measured differences:

| | reference | previous | error |
|---|---|---|---|
| Turkish leading | 1.4155 cap | 1.46 cap | +3.1 % |
| EN cap / TR cap | 0.2465 | 0.28 | +13.6 % |
| TR2→EN baseline drop | 0.5915 cap | 0.70 cap | +18.3 % |
| TR1 tracking | +31.3 /1000 cap | +6 | too tight |
| EN tracking | +526.0 /1000 cap | +390 | too tight |
| line left edges | TR1 x42 · TR2 x45 · EN x53 | all x0 | **no optical step at all** |
| glyph widths (S, E, M) | 0.669 / 0.718 / 0.972 cap | 0.842 / 0.759 / 1.077 cap | Helvetica is materially wider |

The two structural misses were the English line (both too large and set too
low) and the absence of any left-edge stepping between the three lines. The
glyph-width gap is why "use a font that fits" could not have been sufficient on
its own.

## Reference measurements

Source raster: 1012 × 558, SHA-256
`ff9344d9f2c752c307e1a80f8da8edfc288f76be56e042d5df3a9578545f64b1`.

| measurement | value |
|---|---|
| TR cap height | 142 px |
| TR1 / TR2 baselines | y 209 / y 410 |
| TR leading | 201 px = 1.4155 cap |
| EN cap height | 35 px = 0.2465 × TR cap |
| EN baseline | y 494 |
| TR2→EN drop | 84 px = 0.5915 cap |
| ASYA'DA measure | 881 px |
| EĞİTİM measure | 865 px |
| EDUCATION IN ASIA measure | 856 px |
| EN tracking | median advance 55 px, mean glyph 25.6 px → 2.15 |
| red apostrophe | 30 × 49 px, rises 12 px above the TR1 cap line |
| Ğ breve | 66 × 23 px, rises 34 px above the cap line, 12 px clear |
| İ dot | 25 × 25 px, rises 36 px above the cap line, 12 px clear |

The three measures are close but **not identical** (881 / 865 / 856). The
previous round forced them equal. The reference is optically balanced, not
justified to one value.

## Candidates

Three fidelity levels toward the same approved typography — not three
creative directions.

- **W1 — font-based fitted.** Helvetica Neue outlines with the measured cap,
  leading, EN ratio, EN drop, per-line tracking and three line indents applied.
- **W2 — optically corrected.** W1 plus per-glyph horizontal correction derived
  from the reference's own ink measurements (S ×0.79, E ×0.95, M ×0.90,
  T ×0.93, Y ×0.90), with the breve, dots and apostrophe redrawn at reference
  geometry. Letters are placed on the reference's measured ink left edges.
- **W3 — high-fidelity custom.** The reference silhouette traced directly from
  the approved raster.

### Fidelity (alignment on the cap line, not the ink box)

| | ink IoU | red IoU | TR1 | TR2 | EN |
|---|---|---|---|---|---|
| W1 | 0.418 | 0.282 | 0.576 | 0.189 | 0.053 |
| W2 | 0.717 | 0.379 | 0.661 | 0.574 | 0.057 |
| W3 | 0.858 | 0.667 | 0.805 | 0.948 | 0.676 |

Advisory only. The English line and the red apostrophe are the weakest link in
all three.

## Bugs found by measuring rather than by looking

Each of these produced a plausible-looking wordmark that was wrong:

1. **Glyph mirroring.** Font outline coordinates are y-UP; SVG is y-DOWN.
   Emitting them without the sign flip produced vertically mirrored letterforms.
2. **Per-glyph advance drift.** Condensing glyphs while advancing by the font's
   original advance let the line drift; letters are now placed by ink left edge
   on the reference's measured positions.
3. **Missing Turkish diacritics.** W2 initially dropped the Ğ breve and both İ
   dots entirely — the characters that make the wordmark Turkish.
4. **Comparison misalignment.** The cap line was being derived from a coverage
   threshold, which reads the 30 px-wide apostrophe as the cap. That misplaced
   the reference by 12 px and reported W3 at 0.53 when correctly aligned it is
   0.85.
5. **Transparent background read as ink.** `rsvg` emits RGBA; converting
   straight to RGB made the background black, so 99.8 % of the frame scored as
   a match.
6. **Double-traced reference.** Tracing each audit glyph box independently
   re-traced letters whose diacritics were separate components, thickening W3.
7. **Advance-vs-ink comparison.** Glyph ratios were computed against font
   advances rather than ink bounds, producing false condensations near 0.75 for
   E, S and M.

## Lockup policy compliance

- Canonical seal hash `8f5d46f0302c4cc7e3765d3bfce9445f842dbd92f1e0f8fbe99f9f509c77e11a`,
  verified intact before and after.
- 9 lockups (3 candidates × stacked / horizontal / horizontal-dark). Seal path
  data and rect geometry compared byte-for-byte against the locked file:
  **0 deviations across all 9.**
- Only placement and the approved `mono-paper` colour variant differ.

## Production

Deterministic. `studio/tools/audit-wordmark-ref.py`, `build_wordmark.py`,
`render-wordmarks.py`, `wordmark-lockups.py`. Real glyph outlines and traced
reference contours emitted as SVG path data. No `<text>` element anywhere.

**Image-generation calls: 0.**

## Open

- No candidate selected.
- The 5-lockup family from the previous round was **not** rebuilt on any of
  these; it stands uncanonicalised, and no lockup is claimed anywhere.
- W3's fidelity is bounded by the source raster's resolution. A higher-resolution
  capture of the same approved artwork would raise its ceiling.