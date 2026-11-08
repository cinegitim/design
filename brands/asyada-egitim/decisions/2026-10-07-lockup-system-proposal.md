# Lockup system proposal — 5 structural variants

**Date:** 2026-10-07
**Status:** PROPOSED — awaiting human visual selection. **Not canonical.**
**Typeface direction:** supplied/approved in principle. Not re-opened here.

---

## What was and was not decided

The typographic direction was given, so this work did **not** choose a font
family. It developed **five arrangements of one typographic character**.

Locked across all five, identical:

| | |
|---|---|
| Typeface | Helvetica Neue (neo-grotesque, full Turkish coverage) |
| Turkish line | Bold, uppercase |
| English line | Light, uppercase, wide tracking |
| Vertical rhythm | leading 1.46 × TR cap · EN baseline drop 0.70 × TR cap |
| Accent | `’` U+2019 in `#BD2120` |
| Seal | locked canonical `v01-canonical.svg`, byte-identical geometry |

The only variables: arrangement, measure, seal-to-type ratio, spacing,
English optical size/weight, minimum size.

## The reference behaviour that was reproduced

Every type line is justified to **one common measure**. Each line finds its own
tracking for that measure. This is why `ASYA’DA` sets tight (+6), `EĞİTİM`
sets open (+153) and `EDUCATION IN ASIA` sets very open (+177…+390) — three
completely different trackings, all exactly the same width.

Verified numerically, not by eye. All 13 justified lines share their measure to
within **0.026 px** at 400–900 px scale.

Cap height is *derived* from the measure, never guessed; measure is in turn
*derived* from the cap at the design tracking. Both directions were tried and
the wrong one produced clamp-bound artefacts that only showed up in numbers.

## The five variants

| ID | Variant | Arrangement | TR lines | Seal : TR cap | EN / TR | Aspect | Min W |
|---|---|---|---|---|---|---|---|
| P-01 | Primary stacked | stacked, centred | 2 | 3.24 | 0.28 Light | 0.89 | 170 px |
| H-02 | Primary horizontal | horizontal, left | 2 | 3.42 | 0.28 Light | 2.87 | 250 px |
| C-03 | Compact | horizontal, left | 2 | 1.88 | 0.30 Light | 2.44 | 165 px |
| D-04 | Small-use / digital | stacked, centred | 1 | 7.04 | **none** | 1.38 | 110 px |
| F-05 | Formal bilingual | horizontal, left | 2 | 3.42 | 0.36 Light | 2.86 | 300 px |

### Decision requiring human confirmation — D-04 has no English line

This is a **structural** difference, chosen from measurement rather than taste:

- A single-line Turkish measure is 13 characters; the English line is 17.
- Justifying the English line to that measure needs **+940/1000 em** of tracking
  (reads as air pushed through a straw), or an English optical size of **0.48**
  TR cap (collapses the TR/EN hierarchy).
- Either way the line is below legibility at the sizes D-04 exists to serve.

So D-04 is the monolingual small-use lockup, and the rule is: **below 200 px,
drop to a seal-only or monolingual lockup; at 200 px and above the bilingual
lockups take over.** If the human wants D-04 bilingual, it needs either a
different Turkish line break (3 lines) or a shorter English string — both of
which change the brief, so it was not decided unilaterally.

### F-05's rule

The vermilion hairline between the Turkish and English blocks is a deliberate
hierarchy device, not decoration: it states where the language boundary is. On
the mono variant it becomes paper.

## Lockup policy compliance

- Canonical seal hash: `8f5d46f0302c4cc7e3765d3bfce9445f842dbd92f1e0f8fbe99f9f509c77e11a`
- 10 SVGs (5 variants × light/mono). Seal path data and rect geometry compared
  byte-for-byte against the locked file: **0 deviations across all 10.**
- Mono variants are produced by the *same code path* with a colour parameter —
  not by text substitution — so the canonical `fill="#FFFFFF"` is handled by the
  same `seal_group()` that reads the locked file. (An earlier string-substitution
  version silently left the mark white on a cream field; caught by reading the
  generated fills back, not by looking at it.)
- Only placement and the approved `mono-paper` colour variant differ.

## Production

Deterministic. `studio/tools/typeset.py` + `studio/tools/build-lockups.py` +
`studio/tools/glyph-sheet.py`. Real glyph outlines from the real font, emitted
as SVG path data. No `<text>` element in any output, so there is no runtime font
dependency and no chance of a substituted font on a client's machine.

**Image-generation calls: 0.**

## Open

- No variant selected.
- Nothing canonicalised; `brand.json` and `status.md` deliberately not updated
  to claim a lockup.
- Two decisions flagged for the human: D-04 monolingual, and the curly vs
  straight apostrophe (curly `’` is used, matching the reference).