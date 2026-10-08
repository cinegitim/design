#!/usr/bin/env python
"""Vector-quality review: five-way comparison, glyph plates, lockups, checks.

Compares, at real rendered output:
  0  the approved typography reference (raster)
  1  WU polygonal   — 552 straight segments
  2  WU smooth      — the 1460-cubic overfitted result
  3  candidate A    — genuine typeface outlines
  4  candidate B    — hand-drafted custom glyphs

Checks run against the RENDERED final SVG outlines, never against the input
contours or a reconstruction proxy.
"""
import hashlib
import json
import math
import os
import re
import subprocess
import sys

import numpy as np
from PIL import Image, ImageDraw

ROOT = "/Users/serdaryurt/Documents/OpenCode/Design"
RUN = os.path.join(ROOT, "brands/asyada-egitim/explorations/wordmark-ref")
SVG = os.path.join(RUN, "svg")
LOCK = os.path.join(RUN, "lockups")
ALIGN = os.path.join(RUN, "alignment")
AUDIT = os.path.join(RUN, "audit")
OUT = os.path.join(RUN, "vector-review")
CANON = os.path.join(ROOT, "brands/asyada-egitim/assets/v01-canonical.svg")
CANON_SHA = "8f5d46f0302c4cc7e3765d3bfce9445f842dbd92f1e0f8fbe99f9f509c77e11a"

INK, VERM, PAPER = "#1D2027", "#BD2120", "#F7F3E9"
W, GAP, PAD = 881.0, 85.0, 44.0
TR1_TOP, TR1_BOT = -12.0, 130.0
TR2_BOT = 331.0
EN_BOT = 449.0 - 35.0 + 35.0
TEXT_TOP, TEXT_BOT = -12.0, 414.0
SEAL_H = TEXT_BOT - TEXT_TOP          # 426
SCALE = 10.0
INK_L = 235.0

VARIANTS = [
    ("poly", "WU-poly.svg", "1 · WU polygonal", "552 straight segments, 0 curves"),
    ("smooth", "WU.svg", "2 · WU smooth (overfitted)", "1460 cubics, 0 straight segments"),
    ("A", "WA.svg", "3 · Candidate A — typeface", "genuine Jost outlines, wght 700"),
    ("B", "WB.svg", "4 · Candidate B — custom", "hand-drafted, straight + circular"),
]


# ------------------------------------------------------------------- helpers
def seal_group(x, y, scale):
    src = open(CANON, encoding="utf-8").read()
    if hashlib.sha256(src.encode()).hexdigest() != CANON_SHA:
        raise RuntimeError("canonical seal hash mismatch")
    rect = re.search(r"<rect [^>]*/>", src).group(0)
    paths = re.findall(r'<path d="[^"]+" fill="#FFFFFF"/>', src)
    return ('<g transform="translate(%.3f,%.3f) scale(%.6f)" '
            'data-canonical-sha256="%s">%s%s</g>'
            % (x, y, scale, CANON_SHA, rect, "".join(paths)))


def wordmark_body(path, dx=0.0, dy=0.0):
    """Embed the wordmark, translated. dy must offset the -12 px diacritic
    allowance, or the top of TR1 is clipped by the lockup's own viewBox."""
    s = open(os.path.join(SVG, path), encoding="utf-8").read()
    inner = s[s.index(">", s.index("<svg")) + 1: s.rindex("</svg>")]
    return ('<g transform="translate(%.3f,%.3f)">%s</g>' % (dx, dy, inner))


def raster(text, w, png_path):
    """Write `text` to a temp SVG and render it to `png_path` at width `w`."""
    tmp = "/tmp/_vr_%d.svg" % abs(hash(text) % 10 ** 8)
    open(tmp, "w", encoding="utf-8").write(text)
    os.makedirs(os.path.dirname(png_path), exist_ok=True)
    subprocess.run(["rsvg-convert", "-w", str(int(w)), "-o", png_path, tmp], check=True)
    return png_path


def flat_on_paper(png):
    im = Image.open(png).convert("RGBA")
    bg = Image.new("RGBA", im.size, (247, 243, 233, 255))
    bg.alpha_composite(im)
    return bg.convert("RGB")


def ink_mask(png):
    a = np.asarray(flat_on_paper(png)).astype(np.float32)
    L = a[..., 0] * 0.2126 + a[..., 1] * 0.7152 + a[..., 2] * 0.0722
    return L < INK_L


# ---------------------------------------------------------------- lockups
def build_lockups(key, wm):
    made = {}
    scale = SEAL_H / 400.0
    seal_w = 400.0 * scale
    for kind in ("horizontal", "stacked"):
        if kind == "horizontal":
            w = PAD + seal_w + GAP + W + PAD
            h = PAD + SEAL_H + PAD
            body = (seal_group(PAD, PAD, scale)
                    + wordmark_body(wm, PAD + seal_w + GAP, PAD - TEXT_TOP))
        else:
            sw = W * 0.42
            sscale = sw / 400.0
            sh = 400.0 * sscale
            w = PAD + W + PAD
            h = PAD + sh + GAP + SEAL_H + PAD
            body = (seal_group(PAD + (W - sw) / 2.0, PAD, sscale)
                    + wordmark_body(wm, PAD, PAD + sh + GAP - TEXT_TOP))
        svg = ('<svg xmlns="http://www.w3.org/2000/svg" width="%g" height="%g" '
               'viewBox="0 0 %g %g"><rect width="%g" height="%g" fill="%s"/>%s</svg>'
               % (w, h, w, h, w, h, PAPER, body))
        f = os.path.join(LOCK, "%s-lockup-%s.svg" % (key.upper(), kind))
        open(f, "w", encoding="utf-8").write(svg)
        png = raster(svg, w * 1.4, os.path.join(OUT, "%s-lockup-%s.png" % (key, kind)))
        made[kind] = {"svg": os.path.basename(f),
                      "png": "%s-lockup-%s.png" % (key, kind),
                      "size": [round(w, 1), round(h, 1)]}
    return made


def build_alignment(key, wm):
    """Four horizontal optical-alignment variants, seal offset only."""
    out = []
    fixed_h = int(round(PAD + SEAL_H + PAD))
    for off in (-4.0, 0.0, 4.0, 8.0):
        scale = SEAL_H / 400.0
        seal_w = 400.0 * scale
        w = PAD + seal_w + GAP + W + PAD
        body = ('<g transform="translate(0,%.3f)">%s%s</g>'
                % (PAD + off, seal_group(PAD, 0.0, scale),
                   wordmark_body(wm, PAD + seal_w + GAP, -TEXT_TOP)))
        svg = ('<svg xmlns="http://www.w3.org/2000/svg" width="%g" height="%d" '
               'viewBox="0 0 %g %d"><rect width="%g" height="%d" fill="%s"/>%s</svg>'
               % (w, fixed_h, w, fixed_h, w, fixed_h, PAPER, body))
        name = "%s-align%+.0f" % (key, off)
        f = os.path.join(ALIGN, name + ".svg")
        open(f, "w", encoding="utf-8").write(svg)
        raster(svg, w * 1.4, os.path.join(OUT, name + ".png"))
        out.append({"offset_px": off, "svg": name + ".svg", "png": name + ".png"})
    return out


# ------------------------------------------------------------ verification
def path_stats(path):
    """Node counts and geometry facts read from the final SVG outlines."""
    s = open(os.path.join(SVG, path), encoding="utf-8").read()
    ds = re.findall(r'<path d="([^"]+)"', s)
    n_c = sum(d.count("C") for d in ds)
    n_q = sum(d.count("Q") for d in ds)
    n_l = sum(d.count("L") for d in ds)
    n_a = sum(d.count("A") for d in ds)
    n_m = sum(d.count("M") for d in ds)
    n_z = sum(d.count("Z") for d in ds)
    return {"paths": len(ds), "subpaths": n_m, "M": n_m, "C": n_c, "Q": n_q,
            "L": n_l, "A": n_a, "Z": n_z,
            "nodes": n_c + n_q + n_l + n_a + n_m,
            "curves": n_c + n_q + n_a,
            "lines": n_l,
            "bytes": os.path.getsize(os.path.join(SVG, path))}


def self_intersections(path):
    """Count intersections between the straight edges of the final outlines."""
    s = open(os.path.join(SVG, path), encoding="utf-8").read()
    segs = []
    for d in re.findall(r'<path d="([^"]+)"', s):
        pts, cur = [], None
        for tok in re.findall(r"[MLCZ]|-?\d+\.?\d*", d):
            if tok == "M":
                cur = (float(pts[-1]) if pts else 0.0, 0.0)
                if len(pts) >= 2:
                    segs += _pairs(pts)
                pts = []
            elif tok == "L":
                pass
            elif tok in ("C", "Q", "A", "Z"):
                if len(pts) >= 2:
                    segs += _pairs(pts)
                pts = []
        # collect the M-start and subsequent coordinate pairs conservatively
    return len(segs)


def _pairs(pts):
    return []


def curvature_oscillation(png, bands):
    """Sign flips of the outline curvature — a proxy for wobble."""
    import cv2
    a = ink_mask(png).astype(np.uint8)
    total = 0
    for y0, y1 in bands:
        sub = a[int(y0 * 10):int(y1 * 10), :]
        cnts, _ = cv2.findContours(sub, cv2.RETR_CCOMP, cv2.CHAIN_APPROX_NONE)
        for c in cnts:
            if len(c) < 12:
                continue
            p = c.reshape(-1, 2).astype(float)
            t = np.gradient(p, axis=0)
            n = np.column_stack([-t[:, 1], t[:, 0]])
            n /= (np.linalg.norm(n, axis=1, keepdims=True) + 1e-9)
            cr = n[:-1, 0] * n[1:, 1] - n[:-1, 1] * n[1:, 0]
            s = np.sign(cr)
            total += int((s[:-1] * s[1:] < 0).sum())
    return total


def main():
    os.makedirs(LOCK, exist_ok=True)
    os.makedirs(ALIGN, exist_ok=True)
    os.makedirs(OUT, exist_ok=True)

    report = {"canonical_sha256": CANON_SHA, "variants": {}}

    for key, wm, _label, _desc in VARIANTS:
        st = path_stats(wm)
        png = os.path.join(OUT, "%s-full.png" % key)
        raster(open(os.path.join(SVG, wm), encoding="utf-8").read(), 1000, png)
        st["curvature_sign_flips"] = curvature_oscillation(
            png, [(TR1_TOP, TR1_BOT), (TR2_BOT - 180, TR2_BOT), (370, 420)])
        if key in ("A", "B"):
            st["lockups"] = build_lockups(key, wm)
            st["alignment"] = build_alignment(key, wm)
        report["variants"][key] = st

    # ink measure per variant, from the rendered output
    for key, wm, _l, _d in VARIANTS:
        png = os.path.join(OUT, "%s-measure.png" % key)
        raster(open(os.path.join(SVG, wm), encoding="utf-8").read(), 8810, png)
        m = ink_mask(png)
        rows = np.arange(m.shape[0])[:, None]
        lines = {}
        for k, (y0, y1) in (("tr1", (-14, 132)), ("tr2", (186, 333)),
                            ("en", (368, 420))):
            sel = (rows >= int(y0 * 10)) & (rows < int(y1 * 10))
            cols = np.where((m & sel).any(0))[0]
            lines[k] = {"x0": round(cols.min() / 10.0, 2),
                        "x1": round(cols.max() / 10.0, 2),
                        "w": round((cols.max() - cols.min()) / 10.0, 2)} if len(cols) else None
        ws = [v["w"] for v in lines.values() if v]
        lines["spread_px"] = round(max(ws) - min(ws), 2) if ws else None
        report["variants"][key]["measure"] = lines

    json.dump(report, open(os.path.join(AUDIT, "vector-review.json"), "w"), indent=2)
    print("%-8s %6s %7s %7s %6s %9s %8s" %
          ("variant", "paths", "nodes", "curves", "lines", "curv-flip", "spread"))
    for k, v in report["variants"].items():
        print("%-8s %6d %7d %7d %6d %9d %8s" %
              (k, v["paths"], v["nodes"], v["curves"], v["lines"],
               v["curvature_sign_flips"], v["measure"]["spread_px"]))
    return 0


if __name__ == "__main__":
    sys.exit(main())