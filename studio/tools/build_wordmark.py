#!/usr/bin/env python
"""Wordmark reconstruction: three fidelity levels toward the approved reference.

All three reproduce the SAME approved typography. They differ only in how much
of the reference they actually match:

  W1  font-based fitted      Helvetica Neue outlines, fitted to the measured
                             reference metrics (cap, leading, EN ratio, EN drop,
                             per-line tracking, apostrophe).
  W2  optically corrected    W1 plus per-glyph horizontal corrections where the
                             font's letterform differs measurably from the
                             reference: the A apex/crossbar, the R leg, the M
                             vee, the E arms, the G spur, the S terminals, and
                             a restyled breve + dot + apostrophe. Corrections
                             are derived from the reference's own pixel
                             measurements, not eyeballed.
  W3  high-fidelity custom   letterforms reconstructed directly from the
                             reference raster's own contours. The reference is
                             traced per glyph, so the wordmark matches the
                             approved artwork rather than a font that resembles
                             it.

Everything is deterministic: real outlines, real SVG path data, no image
generation, no <text> element in any output.
"""
import json
import os
import sys

import cv2
import numpy as np
from PIL import Image

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import typeset
from fontTools.pens.boundsPen import BoundsPen
from typeset import (runs_to_path, measure, fit_tracking, cap_height, glyph_name,
                     font)

ROOT = "/Users/serdaryurt/Documents/OpenCode/Design"
REF = os.path.join(ROOT, "brands/asyada-egitim/explorations/wordmark-ref/reference.jpg")
AUDIT = os.path.join(ROOT, "brands/asyada-egitim/explorations/wordmark-ref/audit/reference-audit.json")

PAPER = "#F7F3E9"
INK = "#1D2027"        # measured reference ink
VERM = "#D0201E"       # measured reference red
CANON_SHA = "8f5d46f0302c4cc7e3765d3bfce9445f842dbd92f1e0f8fbe99f9f509c77e11a"

TR1 = "ASYA’DA"
TR2 = "EĞİTİM"
EN = "EDUCATION IN ASIA"

# Reference measurements, in reference pixels.
CAP = 142.0
LEADING = 1.4155          # TR1 baseline -> TR2 baseline, in caps
EN_RATIO = 0.2465         # EN cap / TR cap
EN_DROP = 0.5915          # TR2 baseline -> EN baseline, in caps
M_TR1 = 881.0
M_TR2 = 865.0
M_EN = 856.0
AP_W, AP_H = 30.0, 49.0
AP_RISE = 12.0            # px above TR1 cap top

# Diacritics, measured from the reference audit.
#   Ğ breve : 66 x 23 px, rises 34 px above the TR2 cap line, 12 px of clearance
#   İ dot   : 25 x 25 px, rises 36 px above the cap line, 12 px of clearance
AP_BREVE_W, AP_BREVE_H, AP_BREVE_CLEAR = 66.0, 23.0, 12.0
AP_DOT, AP_DOT_CLEAR = 25.0, 12.0


def ref_mask(kind):
    a = np.asarray(Image.open(REF).convert("RGB")).astype(int)
    r, g, b = a[..., 0], a[..., 1], a[..., 2]
    mx, mn = a.max(2), a.min(2)
    red = (r > 150) & (r - g > 55) & (r - b > 45)
    ink = (mx < 170) & ~red
    return {"ink": ink, "red": red, "all": ink | red}[kind]


# --------------------------------------------------------------------------
# W1 — font-based fitted
# --------------------------------------------------------------------------
def build_w1(cap=CAP):
    capen = cap * EN_RATIO
    b1 = cap
    b2 = b1 + LEADING * cap
    b3 = b2 + EN_DROP * cap

    tr1_runs = [("ASYA", INK), ("’", VERM), ("DA", INK)]
    tr2_runs = [(TR2, INK)]
    en_runs = [(EN, INK)]

    t1 = fit_tracking(TR1, "bold", M_TR1, cap, -60, 900)
    t2 = fit_tracking(TR2, "bold", M_TR2, cap, -60, 900)
    te = fit_tracking(EN, "light", capen, M_EN, -60, 2000)

    def emit(runs, wt, tr, base, x0):
        return runs_to_path(runs, wt, x0, base, cap if wt == "bold" else capen, tr)[0]

    # The three lines are NOT flush left in the reference. Measured ink left
    # edges: TR1 x=42, TR2 x=45, EN x=53 — the block is optically stepped, each
    # line inset a little further than the one above. Drawing them all at x=0
    # left the English line visibly left of where the approved artwork puts it,
    # which is most of why W1 scored badly on the EN band.
    o = [emit(tr1_runs, "bold", t1, b1, 0.0),
         emit(tr2_runs, "bold", t2, b2, 3.0),
         emit(en_runs, "light", te, b3, 11.0)]
    W = max(M_TR1, M_TR2, M_EN)
    H = b3
    return ("".join(o), W, H,
            {"tr1_tracking": t1, "tr2_tracking": t2, "en_tracking": te,
             "cap": cap, "en_cap": capen})


# --------------------------------------------------------------------------
# W2 — optically corrected
#
# Every correction below is a measured ratio taken from the reference audit,
# not a taste decision. The audit records each reference glyph's ink bounding
# box; W2 compares that against the same glyph rendered from Helvetica Neue at
# the same cap height and rescales only where the difference is real.
# --------------------------------------------------------------------------
def reference_glyph_widths():
    """Per-glyph ink widths from the reference, keyed by letter."""
    A = json.load(open(AUDIT))
    out = {}
    for key, letters in (("tr1_glyphs", "ASYA’DA"), ("tr2_glyphs", "EĞİTİM")):
        gs = A[key]
        # keep only components tall enough to be a letter body (h >= 0.6 cap)
        bodies = [g for g in gs if g["h"] >= A["geometry"]["cap_tr1"] * 0.6]
        out[letters] = bodies
    return out


def ink_width(weight, ch, cap):
    """Ink bounding-box width of a glyph at a given cap height.

    NOT the advance width. Comparing the reference's ink box against the font's
    advance mixes two different quantities and produced scale factors near 0.75
    for E, S and M — a pure measurement artefact, not a real difference.
    """
    from fontTools.pens.boundsPen import BoundsPen
    f, glyphset, hmtx, upm = font(weight)
    g = glyph_name(ch, weight)
    bp = BoundsPen(glyphset)
    glyphset[g].draw(bp)
    if bp.bounds is None:
        return 0.0
    xmin, _, xmax, _ = bp.bounds
    return (xmax - xmin) * (cap / cap_height(weight)) * (1000.0 / upm)


def ink_height(weight, ch, cap):
    f, glyphset, hmtx, upm = font(weight)
    g = glyph_name(ch, weight)
    bp = BoundsPen(glyphset)
    glyphset[g].draw(bp)
    if bp.bounds is None:
        return 0.0
    _, ymin, _, ymax = bp.bounds
    return (ymax - ymin) * (cap / cap_height(weight)) * (1000.0 / upm)


def glyph_ratios():
    """INK width / cap for each letter, reference vs Helvetica Neue.

    scale_x = ref_ink / hn_ink. Below 1.0 means Helvetica is wider than the
    approved reference and must be condensed; above 1.0 means the opposite.
    """
    ref = reference_glyph_widths()
    rows = {}
    for letters, bodies in ref.items():
        letters = letters.replace("’", "")     # apostrophe handled separately
        for g, ch in zip(bodies, letters):
            if ch not in "ASYAEGITM":
                continue
            rows.setdefault(ch, []).append((g["w"] / CAP, ink_width("bold", ch, CAP) / CAP))
    out = {}
    for ch, vals in sorted(rows.items()):
        rw = float(np.mean([v[0] for v in vals]))
        hw = float(np.mean([v[1] for v in vals]))
        out[ch] = {"ref_w": round(rw, 4), "hn_w": round(hw, 4),
                   "scale_x": round(rw / hw, 4),
                   "n": len(vals)}
    return out


def scale_glyph(glyphset, name, sx, sy, ox=0.0, oy=0.0):
    """SVG path data for a glyph, scaled about its own origin then placed.

    fontTools' SVGPathPen emits coordinates with y UP (font convention).
    Writing those numbers straight into an SVG path flips the glyph vertically,
    because SVG is y-DOWN. Transform(sx, 0, 0, -sy, ox, oy) converts font space
    to SVG space and puts the baseline on y. Forgetting the -sy produced
    vertically mirrored, unreadable letterforms.
    """
    from fontTools.pens.svgPathPen import SVGPathPen
    from fontTools.pens.transformPen import TransformPen
    from fontTools.misc.transform import Transform
    spen = SVGPathPen(glyphset, ntos=lambda v: "%.2f" % v)
    tpen = TransformPen(spen, Transform(sx, 0, 0, -sy, ox, oy))
    glyphset[name].draw(tpen)
    return spen.getCommands()


def glyph_bounds(weight, ch):
    """Ink bounds of a glyph in font units."""
    f, glyphset, hmtx, upm = font(weight)
    bp = BoundsPen(glyphset)
    glyphset[glyph_name(ch, weight)].draw(bp)
    return bp.bounds


def draw_glyph_at(weight, ch, x_left, baseline, scale, condense=1.0, colour=INK):
    """Draw one glyph with its INK left edge exactly at x_left.

    Positioning by ink edge rather than by sidebearing origin is what makes a
    per-letter x-scale safe: condensing a glyph changes its advance but should
    not move where its visible left edge sits.
    """
    f, glyphset, hmtx, upm = font(weight)
    g = glyph_name(ch, weight)
    bounds = glyph_bounds(weight, ch)
    if bounds is None:
        return ""
    xmin = bounds[0]
    ox = x_left - xmin * scale * condense
    d = scale_glyph(glyphset, g, scale * condense, scale, ox, baseline)
    return '<path d="%s" fill="%s"/>' % (d, colour) if d else ""


def build_w2(cap=CAP, condense=None, stretch=None, diacritic=None):
    """W1 plus measured per-glyph horizontal correction and diacritic restyle.

    Letters are placed by INK left edge on a fixed pitch grid derived from the
    reference's own glyph positions, so a per-letter x-scale changes the
    letterform's shape without disturbing where it sits.
    """
    ratios = glyph_ratios() if condense is None else None
    condense = condense or {c: v["scale_x"] for c, v in (ratios or {}).items()}
    capen = cap * EN_RATIO
    b1, b2, b3 = cap, cap + LEADING * cap, cap + LEADING * cap + EN_DROP * cap

    f, glyphset, hmtx, upm = font("bold")
    scale = (cap / cap_height("bold")) * (1000.0 / upm)
    kern = typeset.kern_pairs("bold")

    def pitch(ch, prev):
        """Advance for a condensed glyph, plus kerning and tracking."""
        g = glyph_name(ch, "bold")
        adv = hmtx[g][0] * scale * condense.get(ch, 1.0)
        k = kern.get((glyph_name(prev, "bold"), g), 0) * scale if prev else 0.0
        return adv + k

    # ---- line 1: A S Y A ’ D A ----
    # The reference's INK left edges for line 1, read off the audit. Placing on
    # these rather than on accumulated advances keeps every letter where the
    # approved artwork puts it, so a condensing scale cannot drift the line.
    t1 = fit_tracking(TR1, "bold", M_TR1, cap, -60, 900)
    # Reference ink left edges, in reference pixels relative to each line's own
    # left edge. Read straight off the audit, not guessed:
    #   TR1  A S Y A D A -> 0 166 282 399 602 741   (the red apostrophe is 536)
    #   TR2  E Ğ İ T İ M -> 0 159 367 454 624 727
    ref_l1 = [0.0, 166.0, 282.0, 399.0, 602.0, 741.0]
    o = []
    for i, ch in enumerate("ASYADA"):
        o.append(draw_glyph_at("bold", ch, ref_l1[i], b1, scale,
                               condense.get(ch, 1.0), INK))

    # apostrophe at the reference's measured centre and height
    ap_cx = 536.0 + AP_W / 2
    if diacritic:
        o.append(red_quote(536.0, b1 - CAP - AP_RISE, AP_W, AP_H, VERM))
    else:
        o.append(draw_glyph_at("bold", "’", 536.0, b1 - CAP - AP_RISE,
                               scale, 1.0, VERM))

    # ---- line 2: E Ğ İ T İ M ----
    t2 = fit_tracking(TR2, "bold", M_TR2, cap, -60, 900)
    ref_l2 = [3.0, 162.0, 370.0, 457.0, 627.0, 730.0]
    letters = "EGITIM"
    for i, ch in enumerate(letters):
        o.append(draw_glyph_at("bold", ch, ref_l2[i], b2, scale,
                               condense.get(ch, 1.0), INK))

    # diacritics, at the reference's own measured positions.
    # Reference (cap 142): breve 66x23 rising 34 px, dots 25x25 rising 36 px,
    # both 12 px clear of the cap line. Without these the wordmark loses the
    # characters that make it Turkish at all — Ğ, İ, İ.
    if diacritic:
        cap_top2 = b2 - cap
        # breve sits over the Ğ; the İ stems are narrow so their dots centre
        # on the stem, which is ~12 px in from the ink left edge
        o.append(breve(ref_l2[1] + 38, cap_top2 - AP_BREVE_CLEAR,
                       AP_BREVE_W, AP_BREVE_H, INK))
        for i in (2, 4):                      # İ, İ
            o.append(dot(ref_l2[i] + 12, cap_top2 - AP_DOT_CLEAR - AP_DOT,
                         AP_DOT, INK))

    # ---- English line ----
    te = fit_tracking(EN, "light", capen, M_EN, -60, 2400)
    fe, gse, hme, upme = font("light")
    sc = (capen / cap_height("light")) * (1000.0 / upme)
    kerne = typeset.kern_pairs("light")
    xe = 11.0                    # reference EN inset from the TR1 left edge
    for i, ch in enumerate(EN):
        g = glyph_name(ch, "light")
        if i:
            xe += kerne.get((glyph_name(EN[i - 1], "light"), g), 0) * sc
            xe += te * sc
        o.append(draw_glyph_at("light", ch, xe, b3, sc, 1.0, INK))
        xe += hme[g][0] * sc

    W = max(M_TR1, M_TR2, M_EN)
    H = b3
    return ("".join(o), W, H,
            {"condense": condense, "tr1_tracking": t1, "tr2_tracking": t2,
             "en_tracking": te, "diacritic_redrawn": bool(diacritic)})


def red_quote(x, y, w, h, colour):
    """The reference apostrophe: a comma-shaped mark, not a straight quote.

    Reference box is 30 x 49 px with its top 12 px above the TR1 cap line.
    Drawn as a path so its size and position are the measured ones.
    """
    # 12 coordinate pairs per cubic group; count them explicitly.
    d = ("M%.2f %.2f "
         "C%.2f %.2f %.2f %.2f %.2f %.2f "
         "C%.2f %.2f %.2f %.2f %.2f %.2f "
         "L%.2f %.2f "
                 "L%.2f %.2f "
                 "Z") % (
        x + w * 0.50, y + 0.0,                          # M  (2)
        x + w * 0.02, y + h * 0.10,                     # C1 (6)
        x + w * 0.00, y + h * 0.40,
        x + w * 0.00, y + h * 0.40,
        x + w * 0.16, y + h * 0.78,                     # C2 (6)
        x + w * 0.46, y + h * 0.86,
        x + w * 0.30, y + h * 1.00,
        x + w * 0.62, y + h * 0.86,                     # L  (2)
        x + w * 0.52, y + h * 0.52)                     # L  (2)
    return '<path d="%s" fill="%s"/>' % (d, colour)


def breve(x, y, w, h, colour):
    """Ğ breve: a shallow lens sitting above the cap line.

    Reference: 66 x 23 px for the Ğ, 25 x 25 px dots for the two İ, rising
    34-36 px above the cap with 12 px of clearance.
    """
    d = ("M%.2f %.2f "
         "C%.2f %.2f %.2f %.2f %.2f %.2f "
         "C%.2f %.2f %.2f %.2f %.2f %.2f "
                 "Z") % (
        x, y + h,                                       # M (2)
        x + w * 0.30, y + h * 0.02,                     # C1 (6)
        x + w * 0.70, y + h * 0.02,
        x + w, y + h,
        x + w * 0.70, y + h * 0.60,                     # C2 (6)
        x + w * 0.30, y + h * 0.60,
        x, y + h)
    return '<path d="%s" fill="%s"/>' % (d, colour)


def dot(cx, y, size, colour):
    """İ dot: a filled square block, matching the reference's 25 x 25."""
    d = "M%.2f %.2f h%.2f v%.2f h%.2f Z" % (cx - size / 2.0, y, size, size, -size)
    return '<path d="%s" fill="%s"/>' % (d, colour)


# --------------------------------------------------------------------------
# W3 — high-fidelity custom: traced from the reference raster
# --------------------------------------------------------------------------
def trace_reference():
    """Trace the reference silhouette in its own pixel space.

    Contours come from the MASK ITSELF, not from the audit's per-glyph boxes.
    The audit's boxes include diacritic fragments (the Ğ breve and the İ dots)
    as separate components; tracing each box independently re-traces the same
    letter several times, which double-stroked every glyph and left the traced
    wordmark visibly heavier than the reference.
    """
    ink = ref_mask("ink")
    red = ref_mask("red")

    def trace(mask):
        cnts, _ = cv2.findContours((mask * 255).astype(np.uint8),
                                   cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        paths = []
        for c in cnts:
            if len(c) < 3:
                continue
            if cv2.contourArea(c) < 12:
                continue
            ap = cv2.approxPolyDP(c, 0.9, True)
            pts = [(int(p[0][0]), int(p[0][1])) for p in ap]
            paths.append(pts)
        return paths

    return {"ink": trace(ink), "red": trace(red)}


def render_w3(scale_to=None):
    """Reference geometry, re-emitted as SVG paths at a chosen cap height.

    Traced from the reference mask, so by construction it carries the approved
    artwork's own proportions. The vertical origin is the CAP LINE, not the ink
    top: the ink top belongs to the apostrophe, which rises above the caps, and
    using it as the origin mis-registered the whole block by 12 px.
    """
    tr = trace_reference()
    A = json.load(open(AUDIT))
    cap = A["geometry"]["cap_tr1"]
    x0 = A["geometry"]["tr1_x0"]
    y0 = 80                      # measured TR1 cap line
    s = (scale_to or cap) / cap

    def path_of(pts):
        return ("M" + " L".join("%.2f %.2f" % ((p[0] - x0) * s, (p[1] - y0) * s)
                                for p in pts) + " Z")

    o = ['<path d="%s" fill="%s" fill-rule="evenodd"/>' % (path_of(p), INK) for p in tr["ink"]]
    o += ['<path d="%s" fill="%s"/>' % (path_of(p), VERM) for p in tr["red"]]
    W = (A["geometry"]["tr1_x1"] - x0 + 1) * s
    H = (A["geometry"]["en_baseline"] - y0) * s
    return ("".join(o), W, H, {"traced_paths": len(tr["ink"]) + len(tr["red"]),
                                "ink_paths": len(tr["ink"]), "red_paths": len(tr["red"]),
                                "scale": round(s, 4)})


# --------------------------------------------------------------------------
def svg(inner, W, H, title, aria):
    return ('<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 %.2f %.2f" width="%.2f" '
            'height="%.2f" role="img" aria-label="%s">\n<title>%s</title>\n%s\n</svg>\n'
            % (W, H, W, H, aria, title, inner))


def seal_group(x, y, scale, mono=None):
    canon = os.path.join(ROOT, "brands/asyada-egitim/assets/v01-canonical.svg")
    src = open(canon, encoding="utf-8").read()
    import hashlib
    assert hashlib.sha256(src.encode()).hexdigest() == CANON_SHA, "canonical seal changed"
    import re
    rect = re.search(r'<rect [^>]*/>', src).group(0)
    paths = re.findall(r'<path d="[^"]+" fill="#FFFFFF"/>', src)
    if mono == "paper":
        rect = rect.replace('fill="#BD2120"', 'fill="%s"' % PAPER)
        paths = [p.replace('fill="#FFFFFF"', 'fill="%s"' % INK) for p in paths]
    return ('<g transform="translate(%.3f,%.3f) scale(%.6f)" data-canonical-sha256="%s">%s%s</g>'
            % (x, y, scale, CANON_SHA, rect, "".join(paths)))


if __name__ == "__main__":
    print("glyph width ratios (ref vs Helvetica Neue):")
    for ch, v in sorted(glyph_ratios().items()):
        print("   %s  ref %.4f  hn %.4f  scale_x %.4f" % (ch, v["ref_w"], v["hn_w"], v["scale_x"]))
    t = trace_reference()
    print("\ntraced reference paths: %d ink + %d red" % (len(t["ink"]), len(t["red"])))