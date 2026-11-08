#!/usr/bin/env python
"""Deterministic typesetter for the Asya'da Eğitim lockup system.

Real glyph outlines from a real font -> real SVG path data. No text elements
in output, no AI rendering, no browser text measurement.

Typeface: Helvetica Neue (neo-grotesque, full Turkish coverage).
  Turkish line : Bold      (w700)
  English line : Light     (w300) with heavy tracking, per the reference
Cap-height based sizing so variants share one optical scale.
"""
import sys
from fontTools.ttLib import TTFont
from fontTools.pens.svgPathPen import SVGPathPen
from fontTools.pens.transformPen import TransformPen
from fontTools.misc.transform import Transform

HN = "/System/Library/Fonts/HelveticaNeue.ttc"
_cache = {}


def font(weight):
    if weight not in _cache:
        idx = {"light": 7, "medium": 10, "bold": 1}[weight]
        f = TTFont(HN, fontNumber=idx, lazy=True)
        _cache[weight] = (f, f.getGlyphSet(), f["hmtx"].metrics, f["head"].unitsPerEm)
    return _cache[weight]


def cmap_for(weight):
    f, _, _, upm = font(weight)
    return f.getBestCmap()


def kern_pairs(weight):
    """Old-style `kern` table -> {(left_glyph,right_glyph): value_in_upm_units}."""
    f = font(weight)[0]
    try:
        if "kern" not in f:
            return {}
        out = {}
        for st in f["kern"].kernTables:
            for pair, val in st.kernTable.items():
                out[pair] = val
        return out
    except Exception:
        return {}


def glyph_name(ch, weight):
    cm = cmap_for(weight)
    g = cm.get(ord(ch))
    if g is None:
        raise KeyError("font %s lacks U+%04X (%s)" % (weight, ord(ch), ch))
    return g


def run_metrics(text, weight, tracking):
    """Advance width in em units (upm=1000). tracking in 1/1000 em per glyph gap."""
    f, _, hmtx, upm = font(weight)
    kern = kern_pairs(weight)
    total = 0
    names = []
    for i, ch in enumerate(text):
        g = glyph_name(ch, weight)
        names.append(g)
        total += hmtx[g][0]
        if i:
            left = glyph_name(text[i - 1], weight)
            total += kern.get((left, g), 0)
        if i < len(text) - 1:
            total += tracking
    return total, names


def cap_height(weight):
    f = font(weight)[0]
    return getattr(f, "capHeight", None) or 714


def text_to_path(text, weight, x, baseline, size, tracking=0, fill="#141210", extra=""):
    """size = cap height in user units. Returns (svg_path_markup, advance_width_px)."""
    return runs_to_path([(text, fill)], weight, x, baseline, size, tracking, extra)


def runs_to_path(runs, weight, x, baseline, size, tracking=0, extra=""):
    """Typeset consecutive coloured runs as ONE continuous line.

    Shares one cursor, one tracking value and one kerning context across the run
    boundaries, so a coloured detail inside a word (the red apostrophe in
    ASYA’DA) sits at exactly the position it would occupy if the whole line were
    a single colour. Returned width is therefore identical to text_to_path().
    """
    f, glyphset, hmtx, upm = font(weight)
    cap = cap_height(weight)
    scale = (size / cap) * (1000.0 / upm)
    kern = kern_pairs(weight)

    full = "".join(t for t, _ in runs)
    adv, _ = run_metrics(full, weight, tracking)

    out = []
    cursor = 0.0
    prev = None
    for ch_i, ch in enumerate(full):
        fill = next(c for t, c in runs if ch_i < len(t)) if False else None
        # resolve fill by cumulative length
        acc = 0
        for t, c in runs:
            if ch_i < acc + len(t):
                fill = c
                break
            acc += len(t)
        g = glyph_name(ch, weight)
        if prev is not None:
            cursor += kern.get((prev, g), 0) * scale
            if ch_i > 0:
                cursor += tracking * scale
        spen = SVGPathPen(glyphset, ntos=lambda v: "%.2f" % v)
        tpen = TransformPen(spen, Transform(scale, 0, 0, -scale, x + cursor * scale, baseline))
        glyphset[g].draw(tpen)
        d = spen.getCommands()
        if d:
            out.append('<path d="%s" fill="%s"%s/>' % (d, fill, extra))
        cursor += hmtx[g][0]
        prev = g
    return "".join(out), adv * scale


def measure(text, weight, size, tracking=0):
    f = font(weight)
    cap = cap_height(weight)
    scale = (size / cap) * (1000.0 / f[3])
    adv, _ = run_metrics(text, weight, tracking)
    return adv * scale


def solve_cap(text, weight, measure_width, tracking=0, lo=1.0, hi=2000.0):
    """Solve the cap height at which `text` at `tracking` exactly fills the measure.

    Cap height is DERIVED from the measure rather than guessed, so the Turkish
    line is genuinely justified to the measure and the whole system scales from
    one number. Returns (cap, achieved_tracking) with the exact residual.
    """
    lo, hi = float(lo), float(hi)
    for _ in range(80):
        mid = (lo + hi) / 2
        if measure(text, weight, mid, tracking) < measure_width:
            lo = mid
        else:
            hi = mid
    cap = round((lo + hi) / 2, 3)
    return cap, abs(measure(text, weight, cap, tracking) - measure_width)


def fit_tracking(text, weight, measure_width, size, tracking_lo=-30, tracking_hi=320):
    """Binary-search the tracking that makes `text` fill `measure_width` exactly.

    `size` is the cap height in the SAME units as `measure_width` — the two must
    share a coordinate space or the search collapses onto a clamp bound.

    This is what produces the reference behaviour: every line justified to one
    common measure, each line finding its own natural tracking for that measure.
    """
    lo, hi = float(tracking_lo), float(tracking_hi)
    for _ in range(60):
        mid = (lo + hi) / 2
        if measure(text, weight, size, mid) < measure_width:
            lo = mid
        else:
            hi = mid
    return round((lo + hi) / 2, 1)


def glyph_test():
    """Turkish + punctuation coverage proof."""
    need = list("ĞĞİİŞŞÇÇÖÖÜÜğğışçöü") + ["’", "'", "–", "—", "·", "…"]
    out = {}
    for w in ("light", "medium", "bold"):
        cm = cmap_for(w)
        out[w] = {c: cm.get(ord(c)) for c in need}
    return out


if __name__ == "__main__":
    import json
    print(json.dumps({w: {c: (g or "MISSING") for c, g in d.items()}
                      for w, d in glyph_test().items()},
                     ensure_ascii=False, indent=1))
    for w in ("light", "bold"):
        print(w, "cap", cap_height(w), "upm", font(w)[3])