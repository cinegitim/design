#!/usr/bin/env python
"""Candidate B — custom vector lettering, drafted glyph by glyph.

This is hand-built lettering, not a trace and not a fit. Every glyph is
assembled from a small, deliberate set of primitives on a 1000-unit em:

  stem()   an exact rectangle — straight edges are mathematically straight
  ring()   a true annulus — curves are circular, so curvature is stable and
           cannot oscillate
  wedge()  a triangular bar between two points at a given weight

Because curves are circular arcs rather than interpolated through sampled
points, the letterforms have no raster stair-stepping, no bumps, no spikes and
no wobble by construction. Because every glyph draws its strokes at the same
weight parameter, the stem colour is consistent across the alphabet by
construction rather than by inspection.

Glyphs: A S Y D E G I T M U C O N  + the red apostrophe and the breve.
Turkish: G carries a breve, I carries a dot — drawn, not borrowed.
"""
import math

EM = 1000.0
CAP = 700.0            # cap height
ASC = 760.0            # overshoot for round glyphs


# ---------------------------------------------------------------- primitives
def stem(x, y0, y1, w):
    """Exact rectangle from (x, y0) to (x+w, y1), clockwise from top-left."""
    return ("M%.2f %.2f H%.2f V%.2f H%.2f Z" % (x, y0, x + w, y1, x))


def wedge(x0, y0, x1, y1, w):
    """A bar of weight w whose axis runs from (x0,y0) to (x1,y1).

    Built by offsetting the axis perpendicular to itself, so the two long edges
    are exactly parallel straight lines.
    """
    dx, dy = x1 - x0, y1 - y0
    L = math.hypot(dx, dy) or 1.0
    nx, ny = -dy / L * w / 2.0, dx / L * w / 2.0
    a = (x0 + nx, y0 + ny)
    b = (x1 + nx, y1 + ny)
    c = (x1 - nx, y1 - ny)
    d = (x0 - nx, y0 - ny)
    return "M%.2f %.2f L%.2f %.2f L%.2f %.2f L%.2f %.2f Z" % (a + b + c + d)


def _lin(a0, a1, n):
    if n < 2:
        n = 2
    step = (a1 - a0) / (n - 1)
    return [a0 + i * step for i in range(n)]


def ring(cx, cy, r_out, r_in, a0, a1):
    """Annulus sector from angle a0 to a1 (degrees, CCW, y up).

    Two concentric circular arcs joined by two radial cuts. Constant curvature,
    so the outline is smooth by construction.
    """
    n = max(3, int(abs(a1 - a0) / 6) + 2)
    outer = [(cx + r_out * math.cos(math.radians(a)), cy + r_out * math.sin(math.radians(a)))
             for a in _lin(a0, a1, n)]
    inner = [(cx + r_in * math.cos(math.radians(a)), cy + r_in * math.sin(math.radians(a)))
             for a in _lin(a1, a0, n)]
    pts = outer + inner
    d = "M%.2f %.2f " % pts[0]
    for p in pts[1:]:
        d += "L%.2f %.2f " % p
    return d + "Z"


def fmt_ring(cx, cy, r_out, r_in, a0, a1):
    """Annulus sector as true circular-ARC commands.

    A full circle (a1 - a0 == 360) cannot be drawn as one SVG arc: the start and
    end points are identical and the renderer emits nothing, which is why O came
    out missing entirely. A full ring is emitted as two half arcs instead.
    """
    if abs(a1 - a0) >= 359.9:
        mid = a0 + (180.0 if a1 > a0 else -180.0)
        return fmt_ring(cx, cy, r_out, r_in, a0, mid) + \
            fmt_ring(cx, cy, r_out, r_in, mid, a1)
    large = 1 if abs(a1 - a0) > 180 else 0
    sweep = 1 if a1 > a0 else 0
    x0, y0 = cx + r_out * math.cos(math.radians(a0)), cy + r_out * math.sin(math.radians(a0))
    x1, y1 = cx + r_out * math.cos(math.radians(a1)), cy + r_out * math.sin(math.radians(a1))
    ix1, iy1 = cx + r_in * math.cos(math.radians(a1)), cy + r_in * math.sin(math.radians(a1))
    ix0, iy0 = cx + r_in * math.cos(math.radians(a0)), cy + r_in * math.sin(math.radians(a0))
    return ("M%.2f %.2f A%.2f %.2f 0 %d %d %.2f %.2f L%.2f %.2f "
            "A%.2f %.2f 0 %d %d %.2f %.2f Z"
            % (x0, y0, r_out, r_out, large, sweep, x1, y1, ix1, iy1,
               r_in, r_in, large, 0 if sweep else 1, ix0, iy0))


def circle_path(cx, cy, r):
    """A true circle from two half arcs.

    A single arc cannot express a full circle (identical endpoints), and using
    two arcs with large-arc=1 on a 180 degree span is ambiguous — the dot came
    out as a notched blob. Half arcs with large-arc=0 are exact.
    """
    return ("M%.2f %.2f A%.2f %.2f 0 0 1 %.2f %.2f A%.2f %.2f 0 0 1 %.2f %.2f Z"
            % (cx - r, cy, r, r, cx + r, cy, r, r, cx - r, cy))


# ------------------------------------------------------------------- glyphs
# Every glyph returns (advance_width, [path strings]).
# Shared metrics: ST = stem weight, M = sidebearing, R = bowl outer radius.

def make(w=168, m=26):
    """Build the glyph set at a given stem weight."""
    ST = float(w)
    OUT = ST                      # outer radius offset from the bowl centre
    G = {}

    # ---- A: two straight stems converging at the apex, low crossbar -------
    # The stems must CONVERGE at the top. Running them from the outer top
    # corners down to the inner bottom corners produces an "H" with splayed
    # legs and an open apex.
    aw = 700.0
    apex_x, apex_y = aw / 2.0, CAP
    d = CAP * 0.135                       # how far below the apex the counter meets
    cb0, cb1 = CAP * 0.285, CAP * 0.285 + ST * 0.92
    # inner stem x at height y (both stems converge at the counter apex)
    def _li(y):
        return ST + (apex_x - ST) * (y / (apex_y - d))

    def _ri(y):
        return (aw - ST) + (apex_x - (aw - ST)) * (y / (apex_y - d))
    # Two subpaths under evenodd: the solid body with the crossbar, and the
    # upper counter as a hole. Assembling A from overlapping bars instead leaves
    # a notch at the apex and a flare at the vertex, because every bar ends in a
    # cap cut perpendicular to its own axis.
    G["A"] = (aw, [
        ("M0.00 0.00 L%.2f %.2f L%.2f 0.00 L%.2f 0.00 L%.2f %.2f L%.2f %.2f "
         "L%.2f 0.00 Z"
         % (apex_x, apex_y, aw, aw - ST, _ri(cb0), cb0, _li(cb0), cb0, ST)),
        ("M%.2f %.2f L%.2f %.2f L%.2f %.2f Z"
         % (_ri(cb1), cb1, apex_x, apex_y - d, _li(cb1), cb1)),
    ])

    # ---- S: two circular bowls joined by an oblique spine -----------------
    # Angles are in y-up degrees. The upper bowl runs from the top-right
    # terminal counter-clockwise over the top and down the left; the lower bowl
    # mirrors it. The spine is a parallelogram that keeps the joint solid.
    sw = 620.0
    R = sw / 2.0
    r_in = R - ST
    cx = sw / 2.0
    up_c, lo_c = CAP - R, R
    # Classic geometric S: the TOP HALF and the BOTTOM HALF of two circles,
    # joined by a diagonal spine from the upper bowl's left end to the lower
    # bowl's right start. Using sectors larger than a half-circle makes the two
    # bowls overlap into a solid blob — the spine needs the two open edges to
    # join at, not two nearly complete rings.
    ua0, ua1 = 20.0, 255.0         # upper bowl, counter-clockwise
    la0, la1 = 75.0, -165.0      # lower bowl, clockwise (mirrored)
    # The handoff angles are the whole trick. Ending the upper bowl near 200 deg
    # puts its exit and the lower bowl's entry at almost the same height and the
    # spine comes out horizontal — a flat lens instead of an S's diagonal. At
    # 255/75 deg the exit sits low and the entry high, giving a true diagonal.
    #
    # No spine bar. At these handoff angles the two bowls already overlap into a
    # single stroke; adding a connector quad inserts a hairline sliver into the
    # counter, because the two radial cuts are not parallel and the quad has to
    # be oversized to hide the seam.
    G["S"] = (sw, [
        fmt_ring(cx, up_c, R, r_in, ua0, ua1),
        fmt_ring(cx, lo_c, R, r_in, la0, la1),
    ])

    # ---- Y --------------------------------------------------------------
    yw = 640.0
    G["Y"] = (yw, [
        wedge(0.0, CAP, yw / 2.0, CAP * 0.44, ST),
        wedge(yw, CAP, yw / 2.0, CAP * 0.44, ST),
        stem(yw / 2.0 - ST / 2.0, 0.0, CAP * 0.44, ST),
    ])

    # ---- D: stem + half-ring bowl ----------------------------------------
    dw = 690.0
    R = (dw - ST) / 2.0
    G["D"] = (dw, [
        stem(0.0, 0.0, CAP, ST),
        fmt_ring(ST / 2.0, CAP / 2.0, R + ST / 2.0, R - ST / 2.0, -90, 90),
    ])

    # ---- E: stem + three arms -------------------------------------------
    ew = 580.0
    G["E"] = (ew, [
        stem(0.0, 0.0, CAP, ST),
        ("M%.2f %.2f L%.2f %.2f L%.2f %.2f L%.2f %.2f Z"
         % (ST, CAP - ST, ew, CAP - ST, ew, CAP, ST, CAP)),
        ("M%.2f %.2f L%.2f %.2f L%.2f %.2f L%.2f %.2f Z"
         % (ST, CAP * 0.47, ew - 66, CAP * 0.47, ew - 66, CAP * 0.47 + ST * 0.88,
            ST, CAP * 0.47 + ST * 0.88)),
        ("M%.2f %.2f L%.2f %.2f L%.2f %.2f L%.2f %.2f Z"
         % (ST, 0.0, ew, 0.0, ew, ST, ST, ST)),
    ])

    # ---- G: ring open on the right, with a bar and a short vertical -------
    gw = 620.0
    R = gw / 2.0                     # outer radius; the bowl fills the advance
    cy = CAP / 2.0
    cgx = gw / 2.0
    bar_y = cy - ST / 2.0
    # bowl open at the upper right, plus a bar reaching in from the right at
    # mid-height. There is NO separate stem: a detached rectangle beside the
    # bowl hangs outside the arc and reads as a stray block.
    G["G"] = (gw, [
        fmt_ring(cgx, cy, R, R - ST, 22.0, 338.0),
        ("M%.2f %.2f L%.2f %.2f L%.2f %.2f L%.2f %.2f Z"
         % (cgx, bar_y, cgx + R, bar_y, cgx + R, bar_y + ST, cgx, bar_y + ST)),
    ])

    # ---- I: stem (+ dot) --------------------------------------------------
    iw = ST
    G["I"] = (iw, [stem(0.0, 0.0, CAP, ST)])

    # ---- T ---------------------------------------------------------------
    tw = 660.0
    G["T"] = (tw, [
        ("M0.00 %.2f L%.2f %.2f L%.2f %.2f L%.2f %.2f Z"
         % (CAP - ST, tw, CAP - ST, tw, CAP, 0.0, CAP)),
        stem(tw / 2.0 - ST / 2.0, 0.0, CAP - ST, ST),
    ])

    # ---- M: straight sides, V that stops well above the baseline -----------
    # The diagonals start at the INNER top corner of each stem and meet at a
    # single vertex; running them from the outer corner overshoots the stems and
    # puts a spike outside the outline.
    mw = 860.0
    vy = CAP * 0.26
    # a single chevron: outer vertex at vy, inner vertex above it, arms landing
    # on the inner top corners of the two stems. Two separate bars leave a notch
    # at the vertex.
    G["M"] = (mw, [
        stem(0.0, 0.0, CAP, ST),
        stem(mw - ST, 0.0, CAP, ST),
        ("M%.2f %.2f L%.2f %.2f L%.2f %.2f L%.2f %.2f L%.2f %.2f L%.2f %.2f Z"
         % (ST * 0.6, CAP, mw / 2.0, vy, mw - ST * 0.6, CAP,
            mw - ST * 0.6, CAP - ST, mw / 2.0, vy + ST * 1.16, ST * 0.6, CAP - ST)),
    ])

    # ---- U ---------------------------------------------------------------
    uw = 640.0
    R = (uw - ST) / 2.0
    G["U"] = (uw, [
        stem(0.0, R, CAP, ST),
        stem(uw - ST, R, CAP, ST),
        fmt_ring(uw / 2.0, R, R + ST / 2.0, R - ST / 2.0, 180, 360),
    ])

    # ---- C: ring with a gap on the right ----------------------------------
    cw = 640.0
    R = (cw - ST) / 2.0
    G["C"] = (cw, [fmt_ring(cw / 2.0, CAP / 2.0, R + ST / 2.0, R - ST / 2.0, 38, 322)])

    # ---- O ---------------------------------------------------------------
    ow = 690.0
    R = (ow - ST) / 2.0
    G["O"] = (ow, [fmt_ring(ow / 2.0, CAP / 2.0, R + ST / 2.0, R - ST / 2.0, 0, 360)])

    # ---- N ---------------------------------------------------------------
    nw = 690.0
    # the diagonal is inset from the outer corners by half the stem, so it meets
    # the stems flush instead of overshooting them at top-left and bottom-right
    G["N"] = (nw, [
        stem(0.0, 0.0, CAP, ST),
        stem(nw - ST, 0.0, CAP, ST),
        wedge(ST * 0.5, CAP - ST * 0.5, nw - ST * 0.5, ST * 0.5, ST),
    ])

    # ---- red apostrophe ----------------------------------------------------
    # Drawn, not borrowed. The reference mark is a comma: 30 x 49 native px,
    # its top 12 px ABOVE the cap line and its tail descending 37 px below it,
    # so it spans roughly CAP-60 .. CAP+180 em units at the wordmark's scale.
    # A font's U+0027 is a straight high mark and does not match.
    apw = 148.0
    # The reference mark spans 12 px ABOVE the cap line down to 37 px BELOW it.
    # At the wordmark's scale (k = 142/700) that is +59 .. -182 em units, so the
    # mark straddles the cap line rather than sitting wholly above it — getting
    # this upside down pushed it out of the top of the viewBox.
    a_top, a_bot = CAP + 59.0, CAP - 182.0
    G["'"] = (apw, [
        # comma: round bulb at the top, tail sweeping down and to the left
        ("M%.2f %.2f "
         "C%.2f %.2f %.2f %.2f %.2f %.2f "
         "C%.2f %.2f %.2f %.2f %.2f %.2f "
         "C%.2f %.2f %.2f %.2f %.2f %.2f Z"
         % (apw * 0.50, a_top,
            apw * 0.06, a_top - 6, apw * 0.02, a_top - 52, apw * 0.34, a_top - 74,
            apw * 0.68, a_top - 96, apw * 0.94, a_top - 78, apw * 0.94, a_top - 24,
            apw * 0.60, a_bot + 22, apw * 0.24, a_bot, apw * 0.08, a_bot + 10)),
    ])
    # breve for Ğ: a shallow cup sitting no more than ~34 px above the cap line,
    # as in the reference. Its ends are high and its middle low, which is the
    # 208-332 deg sector of a circle centred well ABOVE the cap line.
    bw = 340.0
    br_t = ST * 0.60
    br_r = 279.0
    br_cy = CAP + 168.0 + 0.469 * br_r
    brv = [fmt_ring(bw / 2.0, br_cy, br_r, br_r - br_t, 208.0, 332.0)]
    # dot for İ: clear of the stem by ~25 em units (~5 px), matching the
    # reference's 9-34 px band above the cap line
    dot_r = ST * 0.43
    dot_cy = CAP + 34.0 + dot_r
    G["dot"] = (ST * 1.0, [circle_path(dot_r, dot_cy, dot_r)])
    # brv holds PATHS (strings); b[0] would take each string's first character
    # and emit the breve as the single letter "M", which is why it never rendered.
    G["Ğ"] = (G["G"][0], list(G["G"][1]) + list(brv))
    G["İ"] = (G["I"][0], list(G["I"][1]) + G["dot"][1])
    return G


def draw(glyph, x, baseline, scale, cap=CAP):
    """Place a glyph at x (baseline y = baseline) and scale em units to px."""
    k = cap / CAP
    adv, paths = glyph
    out = []
    for d in paths:
        out.append('<g transform="translate(%.3f,%.3f) scale(%.6f,%.6f)">'
                   '<path d="%s"/></g>' % (x, baseline, k, -k, d))
    return "".join(out), adv * k