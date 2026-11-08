# Asya'da Eğitim — final lockup family for human approval

**HUMAN FINAL LOCKUP APPROVAL PENDING.** Draft production specification,
not a canonical brand system. The user selected Jost 550 Turkish / 350 English;
no lockup arrangement, offset or minimum-size rule is approved yet.

## Immutable inputs

- Seal: `brands/asyada-egitim/assets/v01-canonical.svg`.
- Seal SHA-256: `8f5d46f0302c4cc7e3765d3bfce9445f842dbd92f1e0f8fbe99f9f509c77e11a`.
- Exact selected outline source:
  `docs/asyada-seal/typography-weights/assets/tr550-en350-wordmark.svg`.
- Every path and per-glyph translation is copied from that source. No new
  typesetting, font instancing, changed tracking, weight or glyph drawing.
- Retain the red comma-shaped apostrophe already present in that selected
  source. It is the prior reference-based vector punctuation correction,
  not a new reconstruction or a claim of pixel-identical JPEG tracing.
- Seal geometry, original 400:370 viewport and clipping remain unchanged.
  Approved mono variants use the same geometry as transparent knockout masks.

## Shared construction / proposed review tokens

- Wordmark common visible measure: **881 native units** for ASYA’DA,
  EĞİTİM and EDUCATION IN ASIA, unchanged from the selected outline source.
- Fixed caps/vertical rhythm: **140 / 139 / 35 units**. Only entire wordmark
  groups may be uniformly scaled; no line or glyph receives independent sizing.
- Ink `#1D2027`, paper `#F7F3E9`, seal/apostrophe red `#BD2120`, original seal
  highlights `#FFFFFF`. Derived from the selected source, not new colors.
- Clearspace: **70 native units** (half the Turkish flat cap), outside all ink,
  including the furthest extent of every alignment alternative.
- Proposed neutral alignment is the prior source's **0 comparison baseline**,
  not an optical approval. Retain **−4 / 0 / +4 / +8 native units**, moving only
  the wordmark vertically; seal position and viewport never move with it.
- Size specifications refer to the complete SVG canvas including clearspace.
  Screen previews are actual CSS pixels at 100% browser zoom; print sizes are
  CSS millimeters, physically reliable only when printed at 100% / actual size.

## Five family members

| ID | Structure and purpose | Seal / gap (native) | Proposed minimum screen width | Proposed minimum print width |
|---|---|---|---:|---:|
| P-01 | Primary stacked; general brand signature | 370w / 85 | 352px | 75mm |
| H-02 | Primary horizontal; website / wide signatures | 426h / 85 | 528px | 110mm |
| C-03 | Compact horizontal; a smaller seal and tighter footprint, bilingual | 260h / 56 | 448px | 95mm |
| D-04 | Small-use / digital; unchanged two Turkish rows, omit English | 220h / 56 | 200px | 45mm |
| F-05 | Formal bilingual; larger centered crest, generous ceremonial gap | 500w / 140 | 352px | 75mm |

**D-04 is deliberately Turkish-only**: the English line cannot stay readable
at the small-use size without changing the selected type geometry. It reuses
the two existing Turkish rows, not a one-line redraw. Where English is mandatory,
use C-03 or another bilingual variant at its larger minimum. Below D-04's minimum,
use the exact seal alone (32px proposed minimum); do not squash the full lockup.
This structural omission is explicitly presented for human approval.

P/H/C/F all carry the identical three-line wordmark. D carries its identical
Turkish subset. No dividers, ornaments, retouched letters or new imagery.

## Delivery and review gate

- Per variant: light, dark, mono ink and mono paper outlined SVGs at every offset.
- Minimum-size raster renders are deterministic SVG inspection outputs only,
  not image-generation output. Actual-size HTML applications are review-only.
- Manifest records each output hash, source wordmark hash and canonical seal hash.
- Independent verification checks geometry, glyphs, clipping, common measure,
  offset isolation, clearspace and minimum-size components/counters.
- Readability is also inspected visually; numerical checks do not mean approval.
- Existing weight/alignment reviews remain unchanged and linked.
- No `brand-system.md` exists yet; this draft intentionally does not create one,
  change `brand.json`, or overwrite any canonical asset before human approval.
