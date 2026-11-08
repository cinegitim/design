#!/usr/bin/env python
"""Unified wordmark geometry for Asya'da Eğitim (WU).

Starting point: the W3 letterform reconstruction (same reference mask, same
contour epsilon). What changes is LAYOUT GEOMETRY, per the human requirements:

  1. All three text lines fill ONE common horizontal measure W.
     Visible ink edges coincide: ASYA'DA [0,W], EĞİTİM [0,W], EDUCATION [0,W].
  2. The wordmark is built for precise alignment with the canonical seal in
     one shared coordinate system (stacked + horizontal lockups).

How W is reached WITHOUT distorting glyphs: every letter is a rigid body.
Only inter-letter gaps change, by a uniform per-gap tracking delta per line.
No scaling of any word or letter. Contours are byte-identical to a fresh trace
of the same mask; only their x-offsets change.

Additionally this build RESTORES the counters that W3's whole-mask
RETR_EXTERNAL trace filled in (31 single-subpath paths, zero holes: the A
triangles, D/P bowls and O letters rendered solid — measured 32/32 against
paper 253 in the reference). Per-component RETR_CCOMP tracing with evenodd
fill recovers them. Same source, same epsilon; strictly a restoration.

Tolerance: max 1 px edge mismatch at 1000 px wordmark width.
Method: measure actual rendered visible ink bounds (lenient paper threshold so
anti-aliased fringe counts), not viewBox numbers or advance widths.
"""
import hashlib
import json
import os
import re
import sys

import cv2
import numpy as np

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import build_wordmark as B
import curves

ROOT = "/Users/serdaryurt/Documents/OpenCode/Design"
RUN = os.path.join(ROOT, "brands/asyada-egitim/explorations/wordmark-ref")
REF = os.path.join(RUN, "reference.jpg")

INK = B.INK            # #1D2027, measured reference ink
VERM = B.VERM          # #D0201E, measured reference red
PAPER = B.PAPER

# W3 frame: reference pixels minus the W3 origin (tr1_x0, tr1 cap line).
X0, Y0 = 42, 80
EPS = 0.4              # dense trace before resampling
CURVE_TOL = 0.18        # max Bézier deviation, native px
SMOOTH = 6              # endpoint-pinned binomial passes over each span        # max Bézier deviation, native px (~0.18 px at 1000 px wide)

# Line bands in REFERENCE coordinates. TR2's band starts high enough to
# include the breve and the İ dots as their own components.
BANDS = {"tr1": (68, 209), "tr2": (234, 410), "en": (460, 494)}
LETTERS = {"tr1": "ASYADA", "tr2": "EGITIM",
           "en": "EDUCATIONINASIA"}
CAP = 142.0


def trace_components(mask):
    """8-connected components, each traced as outer ring(s) + holes.

    Returns components sorted by x0 with absolute reference-pixel boxes. Each
    component carries `rings`: a list of [outer, hole, hole, ...] point lists
    in absolute reference pixels. The caller MUST emit each ring-group as ONE
    path element with fill-rule evenodd — emitting holes as separate path
    elements fills them instead of cutting them (which is how W3's D bowls, A
    triangles and O letters ended up solid).
    """
    n, lab, stats, _ = cv2.connectedComponentsWithStats(
        (mask * 255).astype(np.uint8), connectivity=8)
    out = []
    for i in range(1, n):
        x, y, w, h, area = (int(v) for v in stats[i])
        if w < 3 or h < 3 or area < 12:
            continue
        sub = ((lab[y:y + h, x:x + w] == i) * 255).astype(np.uint8)
        cnts, hier = cv2.findContours(sub, cv2.RETR_CCOMP, cv2.CHAIN_APPROX_NONE)
        rings = []
        if cnts is not None:
            hier = hier[0]
            for j, c in enumerate(cnts):
                if hier[j][3] != -1:
                    continue                      # hole: handled with its parent
                if len(c) < 3 or cv2.contourArea(c) < 6:
                    continue
                # Resample to even spacing before curve fitting: CHAIN_APPROX_NONE
                # gives uneven density, and multi-scale corner detection needs
                # several points per edge to distinguish an edge junction from
                # sampling density. Coordinates are kept in float reference px.
                ring = curves.resample(
                    np.array([[p[0][0] + x, p[0][1] + y] for p in c], float), 0.7)
                group = [[(float(q[0]), float(q[1])) for q in ring]]
                k = hier[j][2]                     # first child
                while k != -1:
                    hc = cnts[k]
                    if len(hc) >= 3 and cv2.contourArea(hc) >= 6:
                        ring2 = curves.resample(
                            np.array([[p[0][0] + x, p[0][1] + y] for p in hc], float), 0.7)
                        group.append([(float(q[0]), float(q[1])) for q in ring2])
                    k = hier[k][0]                 # next sibling
                rings.append(group)
        if rings:
            out.append({"x0": x, "y0": y, "x1": x + w - 1, "y1": y + h - 1,
                        "rings": rings})
    out.sort(key=lambda c: c["x0"])
    return out


def group_line(comps, line_cap):
    """Attach floating diacritics to their base letter.

    A component whose bottom sits above the cap region and whose x-range
    overlaps a tall base letter belongs to that letter and moves with it.
    `line_cap` is THIS line's own cap height (142/139/35) — using the Turkish
    cap for the English line classified all 15 letters as orphans.
    Returns letter groups in x order; asserts nothing is orphaned.
    """
    tall = [c for c in comps if c["y1"] - c["y0"] + 1 >= line_cap * 0.6]
    small = [c for c in comps if c not in tall]
    groups = [{"base": c, "extra": []} for c in tall]
    orphans = []
    for s in small:
        best, best_ov = None, 0
        for g in groups:
            b = g["base"]
            ov = min(s["x1"], b["x1"]) - max(s["x0"], b["x0"]) + 1
            if ov > best_ov:
                best, best_ov = g, ov
        if best and s["y1"] < best["base"]["y0"] + line_cap * 0.75:
            best["extra"].append(s)
        else:
            orphans.append(s)
    return groups, orphans


def main():
    ink = B.ref_mask("ink")
    red = B.ref_mask("red")
    log = {"origin": [X0, Y0], "epsilon": EPS}

    # per-line cap heights, measured from the audit (TR1 142, TR2 139, EN 35)
    LINE_CAP = {"tr1": 142.0, "tr2": 139.0, "en": 35.0}
    lines = {}
    for key, (y0, y1) in BANDS.items():
        band = np.zeros_like(ink)
        band[y0:y1 + 1] = ink[y0:y1 + 1]
        comps = trace_components(band)
        groups, orphans = group_line(comps, LINE_CAP[key])
        lines[key] = {"comps": comps, "groups": groups, "orphans": orphans}
        log[key] = {"components": len(comps), "letters": len(groups),
                    "orphans": len(orphans)}

    # ---- structural assertions: we know exactly what each line holds ----
    assert len(lines["tr1"]["groups"]) == 6 and not lines["tr1"]["orphans"], \
        "TR1 must be 6 bare letters, got %s" % log["tr1"]
    assert len(lines["tr2"]["groups"]) == 6, "TR2 must be 6 letters, got %s" % log["tr2"]
    assert [len(g["extra"]) for g in lines["tr2"]["groups"]] == [0, 1, 1, 0, 1, 0], \
        "TR2 diacritics misassigned: %s" % [len(g["extra"]) for g in lines["tr2"]["groups"]]
    assert not lines["tr2"]["orphans"], "TR2 orphans: %s" % lines["tr2"]["orphans"]
    assert len(lines["en"]["groups"]) == 15 and not lines["en"]["orphans"], \
        "EN must be 15 bare letters, got %s" % log["en"]

    # red apostrophe: freestanding component(s) in the TR1 band
    rband = np.zeros_like(red)
    y0, y1 = BANDS["tr1"]
    rband[y0:y1 + 1] = red[y0:y1 + 1]
    reds = trace_components(rband)
    assert len(reds) == 1, "expected exactly the apostrophe, got %d red components" % len(reds)
    log["red_components"] = 1
    log["apostrophe_ref_box"] = [reds[0]["x0"], reds[0]["y0"], reds[0]["x1"], reds[0]["y1"]]

    # ---- the common measure: TR1's own ink width sets W ----
    t1 = lines["tr1"]["groups"]
    W = (t1[-1]["base"]["x1"] if not t1[-1]["extra"] else
         max([t1[-1]["base"]["x1"]] + [e["x1"] for e in t1[-1]["extra"]])) - t1[0]["base"]["x0"] + 1
    log["W_native"] = int(W)

    def extent(g):
        xs = [g["base"]["x0"]] + [e["x0"] for e in g["extra"]]
        xe = [g["base"]["x1"]] + [e["x1"] for e in g["extra"]]
        return min(xs), max(xe)

    # ---- layout: rigid bodies, uniform per-gap tracking delta ----
    # Component boxes are in REFERENCE pixels; the emission subtracts X0 once
    # to reach WU coordinates. The placement math must therefore run in the WU
    # frame too — mixing frames double-shifted every line 42 px left and cut
    # the first letters off at the viewBox edge.
    placed = {}   # key -> list of (component, dx)
    layout = {}
    for key in ("tr1", "tr2", "en"):
        groups = lines[key]["groups"]
        exts = [(a - X0, b - X0) for (a, b) in (extent(g) for g in groups)]
        widths = [e[1] - e[0] + 1 for e in exts]
        gaps = [exts[i + 1][0] - exts[i][1] - 1 for i in range(len(groups) - 1)]
        cur = exts[-1][1] - exts[0][0] + 1
        delta = W - cur
        d = delta / (len(groups) - 1)
        pos = [0.0]
        for i in range(len(groups) - 1):
            pos.append(pos[i] + widths[i] + gaps[i] + d)
        shift0 = -exts[0][0]
        dxs = [shift0 + p - (exts[i][0] - exts[0][0]) for i, p in enumerate(pos)]
        # right edge lands exactly on W by construction; record the residual
        resid = (pos[-1] + widths[-1]) - W
        placed[key] = [(groups[i], dxs[i]) for i in range(len(groups))]
        layout[key] = {"width_before": int(cur), "delta": round(delta, 3),
                       "per_gap": round(d, 3), "n_gaps": len(groups) - 1,
                       "right_edge_residual": round(resid, 4),
                       "gaps_before": [int(g) for g in gaps]}
    log["layout"] = layout

    # red apostrophe rides TR1's line shift, in the WU frame like everything
    # else: TR1's first group sits at ref x=42 = wu x=0, so its shift is 0.
    red_dx = -(extent(lines["tr1"]["groups"][0])[0] - X0)
    log["red_dx"] = red_dx

    # ---- emit: corner-aware cubic Bézier contours ----
    # One path element per ring-group; outer ring + holes in one `d` with
    # evenodd fill, so counters stay open.
    def path_of(groups, dx):
        # groups is a list of ring-groups; each group is [outer, hole, ...]
        outp = []
        for group in groups:
            d = curves.bezier_path(group, tol=CURVE_TOL, smooth_passes=SMOOTH)
            if not d:
                continue
            # shift from reference px into WU coordinates
            outp.append(curves.shift_path(d, -X0 + dx, -Y0))
        return "".join(outp)

    parts = []
    for key in ("tr1", "tr2", "en"):
        for g, dx in placed[key]:
            for c in [g["base"]] + g["extra"]:
                d = path_of(c["rings"], dx)
                if d:
                    parts.append('<path d="%s" fill="%s" fill-rule="evenodd"/>' % (d, INK))
    for c in reds:
        d = path_of(c["rings"], red_dx)
        if d:
            parts.append('<path d="%s" fill="%s"/>' % (d, VERM))

    # viewBox spans the true ink: x [0, W], y from the apostrophe top to EN baseline
    ys = [c["y0"] for L in lines.values() for g in L["groups"]
          for c in [g["base"]] + g["extra"]] + [reds[0]["y0"]]
    ye = [c["y1"] for L in lines.values() for g in L["groups"]
          for c in [g["base"]] + g["extra"]] + [reds[0]["y1"]]
    vy0, vy1 = min(ys) - Y0, max(ye) - Y0
    body = "".join(parts)
    svg = ('<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 %.2f %.2f %.2f" '
           'width="%.2f" height="%.2f" role="img" aria-label="Asya\'da Eğitim — Education in Asia, unified wordmark">\n'
           '<title>ASYA’DA EĞİTİM — Education in Asia (unified wordmark)</title>\n%s\n</svg>\n'
           % (vy0, W, vy1 - vy0 + 1, W, vy1 - vy0 + 1, body))
    out = os.path.join(RUN, "svg", "WU.svg")
    open(out, "w", encoding="utf-8").write(svg)
    log["viewBox"] = [0, vy0, int(W), int(vy1 - vy0 + 1)]
    log["ink_top_ref_y"] = int(min(ys))
    log["ink_bottom_ref_y"] = int(max(ye))
    n_paths = len(parts)
    log["paths"] = n_paths
    json.dump(log, open(os.path.join(RUN, "audit/unified-build.json"), "w"), indent=1)
    print(json.dumps(log, indent=1))
    return log


if __name__ == "__main__":
    main()
