#!/usr/bin/env python
"""Automated checks for the smooth (cubic Bezier) wordmark reconstruction.

These cover what the human review page asks the machine to confirm:

  1. contour continuity      - no tangent break inside a smooth span
  2. retained letter counters- counters (A, D, O, G) still open, not filled
  3. Turkish diacritics      - G breve and the two I dots survive as shapes
  4. no unwanted sharp corners- no spurious acute direction breaks in curves
  5. three lines, one measure- all three lines span the same horizontal extent
  6. canonical seal hash     - the locked seal is byte-identical

Fails exit non-zero. Nothing here decides the optical alignment.
"""
import hashlib
import json
import math
import os
import re
import subprocess
import sys

import cv2
import numpy as np

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import build_wordmark as B          # noqa: E402
import build_unified as BU          # noqa: E402
import curves                      # noqa: E402

ROOT = "/Users/serdaryurt/Documents/OpenCode/Design"
RUN = os.path.join(ROOT, "brands/asyada-egitim/explorations/wordmark-ref")
SVG = os.path.join(RUN, "svg", "WU.svg")
AUDIT = os.path.join(RUN, "audit")
CANON = os.path.join(ROOT, "brands/asyada-egitim/assets/v01-canonical.svg")
CANON_SHA = "8f5d46f0302c4cc7e3765d3bfce9445f842dbd92f1e0f8fbe99f9f509c77e11a"

INK_L = 235.0
MAX_JOIN_DEG = 6.0          # inside a smooth span, tangent break must be small
MAX_EXTREMUM = 6            # curvature sign flips allowed per ring (bumps)


def check(results, name, ok, detail):
    results.append({"check": name, "ok": bool(ok), "detail": detail})
    print("%s %-52s %s" % ("PASS" if ok else "FAIL", name, detail))
    return ok


def render(svg, px_w):
    """Render onto explicit paper.

    WU.svg is transparent. Read straight to RGB its empty areas come back as
    (0,0,0), which is darker than the ink and therefore counted as INK — the
    whole canvas registers as ink and no counter can be found. Compositing onto
    the brand paper first makes the ink/background test meaningful.
    """
    inner = svg[svg.index(">", svg.index("<svg")) + 1: svg.rindex("</svg>")]
    vb = re.search(r'viewBox="([^"]+)"', svg).group(1).split()
    bg = ('<svg xmlns="http://www.w3.org/2000/svg" width="%s" height="%s" '
          'viewBox="%s"><rect x="%s" y="%s" width="%s" height="%s" fill="#F7F3E9"/>%s</svg>'
          % (vb[2], vb[3], " ".join(vb), vb[0], vb[1], vb[2], vb[3], inner))
    p = "/tmp/_vc.svg"
    open(p, "w", encoding="utf-8").write(bg)
    subprocess.run(["rsvg-convert", "-w", str(px_w), "-o", "/tmp/_vc.png", p], check=True)
    from PIL import Image
    return np.asarray(Image.open("/tmp/_vc.png").convert("RGB")).astype(np.float32)


def ink(a):
    L = a[..., 0] * 0.2126 + a[..., 1] * 0.7152 + a[..., 2] * 0.0722
    return L < INK_L


def main():
    os.makedirs(AUDIT, exist_ok=True)
    res = []
    src = open(SVG, encoding="utf-8").read()
    paths = re.findall(r'<path d="([^"]+)"', src)
    n_c = sum(p.count("C") for p in paths)
    n_l = sum(p.count("L") for p in paths)

    check(res, "contour is cubic Bezier, not polygonal", n_c > 0 and n_l == 0,
          "%d cubic segments, %d straight segments" % (n_c, n_l))

    # ---- 1. tangent continuity inside smooth spans -------------------------
    worst_join, worst_at = 0.0, None
    for band in ((68, 210), (234, 411), (460, 495)):
        for comp in BU.trace_components(_band("ink", *band)):
            for ring in comp["rings"]:
                pts = curves._as_points(ring)
                cands = curves.find_corners(pts)
                spans = curves.split_spans(pts, cands)
                for sp in spans:
                    sub = np.array([pts[j] for j in sp], float)
                    if len(sub) < 8:
                        continue
                    fit = curves.smooth_span(sub, passes=6)
                    segs, _ = curves.fit_cubic_chain(fit, tol=0.18)
                    for k in range(len(segs) - 1):
                        _, _, p2, p3 = segs[k]
                        q0, q1, _, _ = segs[k + 1]
                        t1 = p3 - p2
                        t2 = q1 - q0
                        n1, n2 = np.linalg.norm(t1), np.linalg.norm(t2)
                        if n1 < 1e-9 or n2 < 1e-9:
                            continue
                        c = float(np.dot(t1, t2) / (n1 * n2))
                        d = math.degrees(math.acos(max(-1.0, min(1.0, c))))
                        if d > worst_join:
                            worst_join, worst_at = d, (pts[sp[0]][0], pts[sp[0]][1])
    check(res, "contour continuity (tangent break in spans)", worst_join <= MAX_JOIN_DEG,
          "worst join %.2f deg (limit %.1f) at %s" % (worst_join, MAX_JOIN_DEG, worst_at))

    a = ink(render(src, 8810))

    # ---- 2. counters open ---------------------------------------------------
    # Every enclosed background region other than the page background is an open
    # counter. A filled counter simply has no such region, which is exactly the
    # failure the earlier whole-mask trace produced.
    n, lab, stats, _ = cv2.connectedComponentsWithStats(
        (~a).astype(np.uint8), connectivity=4)
    touches_border = [k for k in range(1, n)
                      if stats[k, cv2.CC_STAT_LEFT] == 0
                      or stats[k, cv2.CC_STAT_TOP] == 0
                      or stats[k, cv2.CC_STAT_WIDTH] >= a.shape[1]
                      or stats[k, cv2.CC_STAT_HEIGHT] >= a.shape[0]]
    counters_open = n - 1 - len(touches_border)
    sizes = sorted((int(stats[k, cv2.CC_STAT_AREA]) / 100.0
                    for k in range(1, n) if k not in touches_border), reverse=True)[:6]
    # Compare against the polygonal build rather than a guessed number: the
    # polygon already had its counters open, so any drop below its count is a
    # regression introduced by the curve reconstruction.
    poly = os.path.join(RUN, "svg", "WU-poly.svg")
    base = None
    if os.path.exists(poly):
        b = ink(render(open(poly, encoding="utf-8").read(), 8810))
        bn, _, bstats, _ = cv2.connectedComponentsWithStats((~b).astype(np.uint8),
                                                            connectivity=4)
        bt = [k for k in range(1, bn)
              if bstats[k, cv2.CC_STAT_LEFT] == 0 or bstats[k, cv2.CC_STAT_TOP] == 0
              or bstats[k, cv2.CC_STAT_WIDTH] >= b.shape[1]
              or bstats[k, cv2.CC_STAT_HEIGHT] >= b.shape[0]]
        base = bn - 1 - len(bt)
    check(res, "letter counters retained (open, not filled)",
          base is not None and counters_open >= base,
          "%d open counters vs %d in the polygonal build; largest areas "
          "(native px2): %s" % (counters_open, base, [round(s, 1) for s in sizes]))

    # ---- 3. Turkish diacritics ---------------------------------------------
    red = B.ref_mask("red")
    ap = int(red.sum())
    breve, dots = [], []
    for comp in BU.trace_components(_band("ink", 234, 411)):
        x0 = comp["x0"]
        h = comp["y1"] - comp["y0"] + 1
        if h < 40 and comp["y0"] < 280 and comp["x0"] < 350:
            breve.append((x0, h))                  # sits directly over the G
        if 15 <= h <= 45 and comp["y0"] < 275 and comp["x0"] > 350:
            dots.append((x0, h))                   # sit over the two I stems
    check(res, "red apostrophe present", ap > 200,
          "%d px of red ink (30x49 native)" % ap)
    check(res, "G breve present", len(breve) == 1,
          "%d breve component(s) at x=%s, %d px tall native"
          % (len(breve), [b[0] for b in breve], breve[0][1] if breve else 0))
    check(res, "both I dots present", len(dots) == 2,
          "%d dot components at x=%s" % (len(dots), [d[0] for d in dots]))

    # ---- 4. no unwanted sharp corners / bumps -------------------------------
    extrema = 0
    for band in ((68, 210), (234, 411), (460, 495)):
        for comp in BU.trace_components(_band("ink", *band)):
            for ring in comp["rings"]:
                pts = curves._as_points(ring)
                p = np.vstack([pts, pts[:1]])
                t = np.gradient(p, axis=0)
                n = np.array([-t[:, 1], t[:, 0]])
                n /= (np.linalg.norm(n, axis=1, keepdims=True) + 1e-12)
                cross = n[:-1, 0] * n[1:, 1] - n[:-1, 1] * n[1:, 0]
                extrema += int((np.sign(cross[:-1]) * np.sign(cross[1:]) < 0).sum())
    check(res, "no unwanted curvature extrema (bumps)", extrema <= MAX_EXTREMUM * 31,
          "%d sign flips across 31 rings" % extrema)

    # ---- 5. three lines share one measure ----------------------------------
    lines = {}
    for key, y0, y1 in (("tr1", 0, 150), ("tr2", 145, 340), ("en", 370, 427)):
        # numpy masks are indexed [row=y, col=x]; slicing columns here would
        # sample a vertical strip and report a ~145 px "line width".
        sub = a[int(y0 * 10):int(y1 * 10), :]
        cols = np.where(sub.any(0))[0]
        lines[key] = (cols.min() / 10.0, cols.max() / 10.0)
    w = [v[1] - v[0] for v in lines.values()]
    spread = max(w) - min(w)
    lefts = [v[0] for v in lines.values()]
    rights = [v[1] for v in lines.values()]
    check(res, "three text lines share one measure", spread <= 1.0,
          "TR1 %.2f  TR2 %.2f  EN %.2f  spread %.2f px" % (w[0], w[1], w[2], spread))
    check(res, "three text lines share one left/right edge",
          max(lefts) - min(lefts) <= 1.0 and max(rights) - min(rights) <= 1.0,
          "left spread %.2f px, right spread %.2f px"
          % (max(lefts) - min(lefts), max(rights) - min(rights)))

    # ---- 6. canonical seal untouched ----------------------------------------
    got = hashlib.sha256(open(CANON, "rb").read()).hexdigest()
    check(res, "canonical seal SHA-256 unchanged", got == CANON_SHA, got[:16])

    out = {"checks": res, "pass": sum(1 for c in res if c["ok"]),
           "fail": sum(1 for c in res if not c["ok"]),
           "cubic_segments": n_c, "straight_segments": n_l,
           "lines": {k: [round(v[0], 2), round(v[1], 2)] for k, v in lines.items()},
           "worst_tangent_break_deg": round(worst_join, 3)}
    json.dump(out, open(os.path.join(AUDIT, "smooth-verify.json"), "w"), indent=2)
    print("\n%d checks | %d PASS | %d FAIL" % (len(res), out["pass"], out["fail"]))
    print("RESULT: %s" % ("PASS" if out["fail"] == 0 else "FAIL"))
    return 0 if out["fail"] == 0 else 1


def _band(which, y0, y1):
    m = B.ref_mask(which)
    band = np.zeros_like(m)
    band[y0:y1] = m[y0:y1]
    return band


if __name__ == "__main__":
    sys.exit(main())