# Smooth contours + independent optical alignment — 2026-10-08

Human visual review of the unified WU lockup returned two defects:

1. the top Turkish line read as optically misaligned with the seal;
2. letter contours showed jagged edges, bumps and irregular curves.

Automated checks had been 29/29 PASS, which is exactly why these went unnoticed.

## A — Contour reconstruction

The WU wordmark was a polygonal reconstruction: 592 vertices, 552 straight
segments, zero curves, traced with `approxPolyDP(epsilon=0.9)`. At 800 % the
simplified outline reads as flat facets and irregular bumps.

Replaced with corner-aware cubic Bézier reconstruction (`studio/tools/curves.py`):

- dense `CHAIN_APPROX_NONE` trace, resampled to ~0.7 px so corner detection has
  several points per edge;
- corners found structurally — a line is fitted to the half-window either side
  of each vertex and a corner is two low-residual straight fits meeting at a
  large angle. Windowed turn angles alone cannot do this: on a dense curve the
  chord angle grows in proportion to the window and passes any absolute
  threshold, so the whole shape reads as "corners";
- the contour is split at corners; each span is fitted with least-squares cubic
  Béziers (Schneider), endpoints pinned to the corner vertices, interior joins
  G1;
- each span is smoothed by 6 endpoint-pinned [1 2 1] passes before fitting, to
  remove the raster's own 1 px quantisation, which `approxPolyDP` had averaged
  away on its way through;
- counters stay open (outer ring + holes in one path, evenodd fill);
- Turkish diacritics reconstructed as geometry, not images.

Result: 1460 cubic segments, 0 straight segments, worst tangent break inside a
span 0.00°, worst deviation from the traced contour ≈ 1.0 px at 881 px width.

No image generation, no upscaling, no new font, no change to lettering concept,
colours or wording. No word or letter is stretched.

## B — Optical alignment

The horizontal lockup centred the seal on the whole wordmark bounding box.
Measured independently instead (`studio/tools/optical_align.py`), on 10× renders
with paper at L=243 and an ink threshold of L<235:

- TR1 cap line — median of the letter components' tops. Taking the topmost
  pixel instead reports the A's 1 px apex sliver as the cap line and understates
  the cap height by about 12 px;
- TR1 baseline, apostrophe top, complete wordmark ink box, ink-weighted centroid;
- cap→baseline midpoint, which is the reference the eye uses for a flat-sided
  seal.

Four horizontal previews at controlled seal offsets of −4, 0, +4 and +8 native px
were produced, each containing the exact canonical seal, uniformly scaled and
translated only.

**No alignment was selected.** The choice belongs to the human reviewer.

## Verification

- `studio/tools/verify_smooth.py` — 10 checks, 10 PASS, 0 FAIL
- `studio/tools/quality_gate.py` — 29 checks, 29 PASS, 0 FAIL
- canonical seal SHA-256 `8f5d46f0302c4cc7e3765d3bfce9445f842dbd92f1e0f8fbe99f9f509c77e11a`
  unchanged, 0 geometry deviations in all lockups
- three text lines still share one measure: spread 0.40 px

## Bugs found and fixed on the way (all produced confidently wrong numbers)

- `_fit_line` returned the line's principal direction, so antiparallel lines
  read 180° apart and a straight edge looked like a hard corner.
- `_fit_line` measured distance *along* the line instead of perpendicular to it,
  so a perfect straight edge reported a residual equal to its own half-length.
- `shift_path` shifted only the coordinate pair immediately following a command
  letter. `fmt` strips trailing zeros, so most coordinates became bare integers
  and were silently skipped — control points scattered and letterforms rendered
  as hair-thin spikes.
- the least-squares column for the second tangent magnitude needs its sign
  flipped (`p2 = p3 − a2·t2`); without it the solve returns a negative value
  which the clamp silently zeroed, collapsing every curve to a straight line.
- the split tangent was read from the *start* of the left sub-span rather than
  from the split point.
- spans shorter than 8 points fell back to a polyline; chaining those was the
  remaining source of visible facets.
- verification rendered the transparent wordmark straight to RGB, so empty
  areas came back black and were counted as ink — no counter could be found.
- the numpy ink mask is indexed `[row=y, col=x]`; slicing columns sampled a
  vertical strip and reported a 145 px "line width".
- band detection scanned only non-empty rows, so it could never see the
  zero-ink gap between TR1 and TR2 and reported a 426 px "TR1 band".
- the four alignment variants had variable canvas heights, which changed the
  render scale and made the same native px measure differently at each offset.
- the seal was placed at y=0 with no padding, so it was clipped by the canvas.

## Status

Not canonicalised. Not approved. Awaiting human review of the alignment choice.
