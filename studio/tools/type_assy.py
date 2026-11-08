#!/usr/bin/env python
"""Typesetting module: lay out a string from genuine font outlines to SVG paths.

This is the basis for candidate A. Everything it emits comes from the font's
own quadratic outlines — no tracing, no polygon simplification, no
raster-to-Bezier conversion.

Two things this got right after the first attempt failed:

  * the weight axis tag lives on `axis.axisTag`, not `axis.tag` (which is None
    here), so variable fonts were silently left at their default weight;
  * advance widths come from `font["hmtx"].metrics[g]`, not `font["hmtx"][g]`
    — the latter is a table object and does not index by glyph name.
"""
import os

from fontTools.pens.svgPathPen import SVGPathPen
from fontTools.ttLib import TTFont
from fontTools.varLib.instancer import instantiateVariableFont


def load(path, wght=None):
    f = TTFont(path)
    if "fvar" in f and wght is not None:
        for ax in f["fvar"].axes:
            if ax.axisTag == "wght":
                f = instantiateVariableFont(f, {"wght": wght}, inplace=False)
                break
    return f


def font_metrics(font):
    upem = font["head"].unitsPerEm
    os2 = font["OS/2"]
    cap = getattr(os2, "sCapHeight", None) or upem * 0.70
    xh = getattr(os2, "sxHeight", None) or cap * 0.72
    return {"upem": upem, "cap": cap, "xh": xh}


def cap_scale(font, cap_px):
    m = font_metrics(font)
    return cap_px / float(m["cap"])


def glyph_path(font, ch, k, dx=0.0, dy=0.0):
    """One glyph's outline as SVG path data, scaled by k and offset.

    The transform flips Y. Font outlines are y-up with the baseline at 0; SVG is
    y-down. Without the flip the glyph is drawn BELOW its own origin and is
    clipped out of the canvas entirely.
    """
    from fontTools.pens.transformPen import TransformPen
    cmap = font.getBestCmap()
    name = cmap.get(ord(ch))
    if name is None:
        return None, None, 0.0
    gs = font.getGlyphSet()
    pen = SVGPathPen(gs)
    gs[name].draw(TransformPen(pen, (k, 0, 0, -k, dx, dy)))
    # advance in FONT UNITS; the caller scales it by k to get pixels
    adv = float(font["hmtx"].metrics[name][0])
    return pen.getCommands(), name, adv


def compose(font, text, k, origin=(0.0, 0.0), tracking_em=0.0):
    """Lay out `text`; returns (path data, total advance in px).

    `x` is kept in PIXELS and advances are font units scaled by k. Accumulating
    in em while offsetting in pixels made the whole line collapse into a few
    pixels of advance and every glyph piled on the last.
    """
    ox, oy = origin
    upem = float(font["head"].unitsPerEm)
    parts, x = [], 0.0
    for ch in text:
        d, _name, adv_u = glyph_path(font, ch, k, ox + x, oy)
        if d:
            parts.append(d)
        x += adv_u * k + tracking_em * k
    return "".join(parts), x


def text_width(font, text, k, tracking_em=0.0):
    """Rendered width in PIXELS.

    `k` is pixels per FONT UNIT (cap_px / cap_units), so advances must be summed
    in font units and multiplied by k. Accumulating in em and multiplying by k
    understates the width by upem and produces absurd tracking values.
    """
    cmap = font.getBestCmap()
    hm = font["hmtx"].metrics
    upem = float(font["head"].unitsPerEm)
    total = 0.0
    for ch in text:
        g = cmap.get(ord(ch))
        if g:
            total += hm[g][0] + tracking_em * upem
    return total * k


def fit_tracking(font, text, target_w, cap_px):
    """Per-gap tracking in PIXELS that makes `text` span exactly target_w.

    Only the gaps change; no glyph is scaled or condensed.
    """
    k = cap_scale(font, cap_px)
    n = len(text) - 1
    if n <= 0:
        return 0.0, k, text_width(font, text, k)
    natural = text_width(font, text, k)
    return (target_w - natural) / n, k, target_w