# Vector-quality candidates A and B — 2026-10-08

Human review of the "smooth" wordmark: **visually worse despite passing every
automated check**. Two defects were reported and both were correct.

The smooth build replaced a 592-vertex polygon with 1460 cubic segments and
0 straight segments by tracing a raster and fitting Béziers to the trace. That
optimised raster agreement, not vector quality. Measured on the final outlines:

| version | nodes | curves | straight | curvature sign flips |
|---|---|---|---|---|
| WU polygonal | 592 | 0 | 552 | 113 |
| WU smooth (overfitted) | 1500 | 1460 | 0 | **110** |
| candidate A (typeface) | 313 | 224 | 43 | 72 |
| candidate B (custom) | **196** | 31 | 104 | **52** |

The overfitted result is *worse* on oscillation than the polygon it replaced,
while using 2.5x the nodes. Zero straight segments was never a quality target.
The pipeline is stopped. Neither candidate uses `approxPolyDP`, raster tracing,
or automatic raster-to-Bézier conversion.

## A — typeface-based

Reference identifiers read from the raster: oblique-cut S terminals, near-round
D and G bowls, pointed A apex with a low crossbar, circular İ dot, wide flat T,
square E terminals, G with a bar and no spur.

Scored on per-glyph shape agreement (Poppins 0.420, Jost 0.386, Poppins
SemiBold 0.382, Figtree 0.363, Outfit 0.362). **Jost** chosen: Futura lineage,
which matches the oblique S terminals — the single most visible identifier.
Poppins was rejected because its S terminals are horizontal.

Outlines come from the font itself via fontTools. Turkish diacritics (Ğ breve,
İ dots) come from the font. The red apostrophe is drawn, not borrowed: the
reference mark is a comma, 30 × 49 native px, straddling the cap line.

## B — custom vector lettering

Hand-drafted glyph by glyph on a 1000-unit em, from primitives:

- `stem` — an exact rectangle; straight edges are mathematically straight
- `fmt_ring` — a true annulus sector drawn with SVG arc commands; curves are
  exact circles, so curvature is stable and cannot oscillate
- `wedge` / chevron — parallelogram bars

Because curves are circular arcs rather than interpolated through sampled
points, stair-stepping, bumps, spikes and wobble are impossible **by
construction**, not by filtering. Stem weight is one shared parameter, so it is
consistent across the alphabet structurally.

## Layout contract held

Both candidates fill the unified measure exactly: all three lines span
[0, 880.90] native px, the same as the approved WU wordmark. Alignment is on
INK, not on advance width — measured from the rendered SVG and corrected by
adjusting inter-letter gaps only. No glyph is scaled, condensed or stretched.

## Known open defects (for the human reviewer)

- **B**: the M vertex still leaves a slight notch; the G bar could be
  re-tuned to the aperture angle.
- **A**: Jost's M is wider than the reference and A's apex opening differs;
  optical correction recommended.

## Bugs found on the way

- `ax.tag` is `None` in this fontTools version — the real axis tag is
  `ax.axisTag`, so variable fonts were silently left at their default weight
  (Outfit rendered as hairline).
- `font["hmtx"]` is a table object; advance widths come from
  `font["hmtx"].metrics[g]`.
- Font outlines are y-up, SVG is y-down: without a Y flip every glyph drew
  below its own origin and was clipped out of the canvas.
- Advance accumulated in em but offset in px, collapsing each line into a few
  pixels.
- `text_width` multiplied em by `k`, but `k` is pixels per FONT UNIT — understated
  widths by upem and produced tracking values of 700+ em.
- A full circle cannot be one SVG arc (identical endpoints): O rendered as
  nothing. Two half arcs are emitted instead.
- `brv` held path STRINGS and `[b[0] for b in brv]` took each string's first
  character, emitting the Ğ breve as the single letter `M` — it never rendered.
- The apostrophe bounds were inverted, putting the mark above the viewBox; in
  candidate A the path data was also emitted raw inside a `<g>` with no `<path>`
  wrapper, so it rendered as nothing at all.
- Lockups clipped the wordmark: the -12 px diacritic allowance needs a vertical
  offset or the top of TR1 falls outside the lockup's own viewBox.

## Status

Not canonicalised. Not approved. No candidate selected. No alignment selected.
Canonical seal untouched: SHA-256 `8f5d46f0302c4cc7e3765d3bfce9445f842dbd92f1e0f8fbe99f9f509c77e11a`.
