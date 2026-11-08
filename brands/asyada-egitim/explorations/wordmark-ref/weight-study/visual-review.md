# Visual self-review — reference-first weight study

Status: HUMAN TYPOGRAPHY REVIEW PENDING. Advisory, never approval.

## Inspection performed

- Actual final SVG renders in `turkish-actual-comparison.png` (all six weights),
  `english-actual-comparison.png` (all four), `glyphs-actual-comparison.png`,
  `horizontal-actual.png` and `stacked-actual.png` were read as images.
- Browser DOM: 103 image elements loaded without breakage. Identical native
  dimensions across each original/candidate close-up; source/candidate line
  strips remain 1012px wide rather than inconsistently scaling to the viewport.
- Layout checked at 375, 768, 1440px: document width equals viewport width,
  with intended horizontal scrolling confined to comparison/glyph containers.
- Browser screenshot attempted after focusing: unavailable because the desktop
  window is not visible. No screenshot or desktop visual preview is claimed.

## Study-page scores (not identity approval)

| Hierarchy | Consistency | Aesthetics | Usability |
|---:|---:|---:|---:|
| 9 | 9 | 8 | 8 |

Original leads, measurements precede trials, and shared scales keep comparisons
honest. Native scroll areas preserve the ability to inspect instead of shrinking
every wordmark on mobile. More than ten specimens are necessary for this study,
not competing brand typography tokens.

## Severity-ranked observations and corrections

- High / fixed: Jost's slab apostrophe looked like a red slash, not the source
  comma. Replaced only the punctuation with a five-cubic source-envelope drawing.
- High / fixed: normalizing close-up tile heights would have changed the cap
  scale. All versions of each glyph now share one viewBox; zoom multiplies native
  width and height together (100/400/800%).
- Medium / fixed: wide S crop included the next Y's corner. Source close-ups
  now isolate the measured glyph plus 2px edge clearance, without tracing it.
- High / experiment limitation: Jost A/G/M/Ğ shapes diverge from the reference.
  No weight fixes the upright-reference versus splayed-Jost M, or G return.
  These are explicitly shown and reported, not disguised as complete work.
- High / experiment limitation: every requested English weight is thinner than
  the source, including 350. Do not invent a matching result or an approved pair.

Candidate source-fidelity is approximately 5/10, with unresolved structural
differences; this is not a ready-to-approve reconstruction. Technical geometry
checks are necessary but cannot overrule visible source superiority.

## Requested Muse inspection

Muse Spark 1.3 Free completed actual multimodal advisory inspection, separately
flagging critical A/M and high G structure differences and lighter-than-source
English. `muse-review.md` records findings and factual reconciliation of three
inaccurate assertions. No AI assessment chooses or approves a candidate.

New relative-alignment previews explicitly move only the wordmark by −4/0/+4/+8
native pixels while the exact seal stays fixed. Historical alternatives remain
untouched; these new alternatives do not select an alignment.
