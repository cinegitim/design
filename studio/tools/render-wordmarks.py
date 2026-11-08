#!/usr/bin/env python
"""Render W1/W2/W3 wordmarks + deterministic overlays against the reference."""
import json
import os
import subprocess
import sys

import numpy as np
from PIL import Image

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import build_wordmark as B
import typeset

ROOT = "/Users/serdaryurt/Documents/OpenCode/Design"
RUN = os.path.join(ROOT, "brands/asyada-egitim/explorations/wordmark-ref")
SVG = os.path.join(RUN, "svg")
PNG = os.path.join(RUN, "png")
REF = os.path.join(RUN, "reference.jpg")
AUDIT = os.path.join(RUN, "audit/reference-audit.json")

PAPER = (247, 243, 233)
PAPER_IMG = (253, 252, 247)      # the reference's own paper
INK_IMG = (29, 32, 39)
VERM_IMG = (208, 32, 30)


def rsvg(svg_path, out_png, width):
    subprocess.run(["rsvg-convert", "-w", str(width), svg_path, "-o", out_png],
                   check=True, capture_output=True)


# ---------------- W1 ----------------
def w1():
    inner, W, H, meta = B.build_w1()
    s = B.svg(inner, W, H, "ASYA’DA EĞİTİM — Education in Asia (W1 font-based fitted)",
              "Asya'da Eğitim wordmark, W1 font-based fitted")
    p = os.path.join(SVG, "W1.svg")
    open(p, "w", encoding="utf-8").write(s)
    return p, W, H, meta


# ---------------- W2 ----------------
def w2():
    ratios = B.glyph_ratios()
    condense = {c: v["scale_x"] for c, v in ratios.items()}
    inner, W, H, meta = B.build_w2(condense=condense, diacritic=True)
    s = B.svg(inner, W, H, "ASYA’DA EĞİTİM — Education in Asia (W2 optically corrected)",
              "Asya'da Eğitim wordmark, W2 optically corrected")
    p = os.path.join(SVG, "W2.svg")
    open(p, "w", encoding="utf-8").write(s)
    return p, W, H, meta


# ---------------- W3 ----------------
def w3():
    inner, W, H, meta = B.render_w3()
    s = B.svg(inner, W, H, "ASYA’DA EĞİTİM — Education in Asia (W3 traced)",
              "Asya'da Eğitim wordmark, W3 high-fidelity custom")
    p = os.path.join(SVG, "W3.svg")
    open(p, "w", encoding="utf-8").write(s)
    return p, W, H, meta


# ---------------- comparison machinery ----------------
def load_ref_alpha():
    """Reference as a clean alpha mask + colour labels, at native size."""
    a = np.asarray(Image.open(REF).convert("RGB")).astype(int)
    r, g, b = a[..., 0], a[..., 1], a[..., 2]
    red = (r > 150) & (r - g > 55) & (r - b > 45)
    ink = (a.max(2) < 170) & ~red
    return ink, red, a.shape


def candidate_alpha(png_path):
    """Composite onto paper first, THEN classify.

    rsvg emits RGBA with a transparent background; converting straight to RGB
    turns transparency into black, so the background classified as ink and 99.8%
    of the frame scored as a match. Compositing reproduces the reference's own
    condition — ink on paper — so both sides are measured the same way.
    """
    im = Image.open(png_path).convert("RGBA")
    bg = Image.new("RGBA", im.size, PAPER_IMG + (255,))
    bg.alpha_composite(im)
    a = np.asarray(bg.convert("RGB")).astype(int)
    r, g, b = a[..., 0], a[..., 1], a[..., 2]
    red = (r > 150) & (r - g > 55) & (r - b > 45)
    ink = (a.max(2) < 190) & ~red
    return ink, red, a.shape


def align_to_reference(ref_ink, cand_ink, cap_y_ref, cap_y_cand):
    """Align on the CAP LINE, not the ink bounding box.

    The reference's ink top is the apostrophe, which rises 12 px above the cap;
    the candidates' ink top is the same apostrophe, but the two were authored at
    different y-origins. Bounding-box alignment therefore shifted the whole
    candidate 12 px down and destroyed the score — W3 read 0.53 when correctly
    aligned it is 0.85. Alignment must use the cap line, which is the quantity
    the typography is actually built on.
    """
    def x0_of(m):
        xs = np.where(m.any(axis=0))[0]
        return int(xs.min()) if len(xs) else None

    rx, cx = x0_of(ref_ink), x0_of(cand_ink)
    if rx is None or cx is None:
        return None
    return int(rx - cx), int(cap_y_ref - cap_y_cand)


def shift(mask, dx, dy):
    out = np.zeros_like(mask)
    h, w = mask.shape
    ys, xs = np.where(mask)
    ny, nx = ys + dy, xs + dx
    keep = (ny >= 0) & (ny < h) & (nx >= 0) & (nx < w)
    out[ny[keep], nx[keep]] = True
    return out


def score(ref_ink, cand_ink, ref_red=None, cand_red=None):
    """IoU on the ink mask, plus an ink-only red-penalty term."""
    inter = np.logical_and(ref_ink, cand_ink).sum()
    union = np.logical_or(ref_ink, cand_ink).sum()
    iou = inter / union if union else 0.0
    res = {"iou": round(float(iou), 4)}
    if ref_red is not None and cand_red is not None:
        ri, ci = np.logical_and(ref_red, cand_red).sum(), np.logical_or(ref_red, cand_red).sum()
        res["red_iou"] = round(float(ri / ci) if ci else 0.0, 4)
    return res


def overlay(ref_ink, cand_ink, ref_red, cand_red, size):
    """50 % overlay: reference in one channel, candidate in another."""
    h, w = size
    img = np.zeros((h, w, 3), np.uint8)
    img[..., :] = PAPER_IMG
    # reference = cyan-ish, candidate = magenta-ish, overlap = dark
    img[ref_ink] = (60, 150, 200)
    img[cand_ink] = (220, 90, 150)
    img[np.logical_and(ref_ink, cand_ink)] = (30, 30, 40)
    if ref_red is not None and cand_red is not None:
        img[ref_red] = (0, 150, 90)
        img[cand_red] = (240, 120, 0)
        img[np.logical_and(ref_red, cand_red)] = (180, 40, 40)
    return Image.fromarray(img)


def diffmap(ref_ink, cand_ink, size):
    h, w = size
    img = np.zeros((h, w, 3), np.uint8)
    img[..., :] = (250, 250, 250)
    only_r = np.logical_and(ref_ink, ~cand_ink)
    only_c = np.logical_and(cand_ink, ~ref_ink)
    both = np.logical_and(ref_ink, cand_ink)
    img[both] = (225, 225, 225)
    img[only_r] = (30, 110, 200)      # reference only  -> candidate missing ink
    img[only_c] = (220, 40, 40)       # candidate only  -> candidate added ink
    return Image.fromarray(img)


def _jsonable(o):
    """numpy scalars leak into dicts; JSON wants plain ints/floats."""
    if isinstance(o, dict):
        return {k: _jsonable(v) for k, v in o.items()}
    if isinstance(o, (list, tuple)):
        return [_jsonable(v) for v in o]
    if isinstance(o, (np.integer,)):
        return int(o)
    if isinstance(o, (np.floating,)):
        return float(o)
    return o


def fit_to_canvas(mask, H, W):
    """Place a mask into an H x W canvas, anchored at its own top-left.

    Candidates are rendered at their natural size and then aligned; they are not
    the same pixel dimensions as the reference, so both masks must live in one
    canvas before any comparison. Anchor is top-left because that is the corner
    the typography is measured from.
    """
    out = np.zeros((H, W), bool)
    h, w = mask.shape
    hh, ww = min(h, H), min(w, W)
    out[:hh, :ww] = mask[:hh, :ww]
    return out


def build_compare(name, ref_ink, ref_red, cand_ink, cand_red, cap_y_ref, cap_y_cand):
    os.makedirs(os.path.join(RUN, "compare"), exist_ok=True)
    H, W = ref_ink.shape
    dx, dy = align_to_reference(ref_ink, cand_ink, cap_y_ref, cap_y_cand)
    ci = fit_to_canvas(cand_ink, H, W)
    cr = fit_to_canvas(cand_red, H, W) if cand_red is not None else None
    ci = shift(ci, dx, dy)
    cr = shift(cr, dx, dy) if cr is not None else None
    sc = score(ref_ink, ci, ref_red, cr)
    overlay(ref_ink, ci, ref_red, cr, (H, W)).save(os.path.join(RUN, "compare", "%s-overlay.png" % name))
    diffmap(ref_ink, ci, (H, W)).save(os.path.join(RUN, "compare", "%s-diff.png" % name))
    return sc, (dx, dy)


def cap_top_y(mask):
    """The cap line = the most common TOP EDGE of the glyph bodies.

    Not a coverage threshold. A coverage threshold reads the apostrophe's top as
    the cap line, because the apostrophe is the first thing to appear in the
    row profile even though it is only 30 px wide — it put the reference cap at
    y=80 when the true glyph tops are at y=68, a 12 px error that shifted every
    candidate down and crushed the score.
    """
    import cv2
    n, lab, stats, _ = cv2.connectedComponentsWithStats((mask * 255).astype(np.uint8),
                                                       connectivity=8)
    tops = []
    for i in range(1, n):
        x, y, w, h, area = stats[i]
        if w >= 4 and h >= 4:
            tops.append(int(y))
    if not tops:
        ys = np.where(mask.any(axis=1))[0]
        return int(ys[0]) if len(ys) else 0
    from collections import Counter
    return int(Counter(tops).most_common(1)[0][0])


def main():
    for d in (SVG, PNG):
        os.makedirs(d, exist_ok=True)
    A = json.load(open(AUDIT))
    ref_ink, ref_red, rshape = load_ref_alpha()
    ref_cap = cap_top_y(ref_ink[68:494]) + 68

    results = {}
    for name, fn in (("W1", w1), ("W2", w2), ("W3", w3)):
        p, W, H, meta = fn()
        rsvg(p, os.path.join(PNG, "%s.png" % name), int(round(W)))
        cp = os.path.join(PNG, "%s.png" % name)
        ci, cr, cshape = candidate_alpha(cp)
        cand_cap = cap_top_y(ci)
        sc, off = build_compare(name, ref_ink, ref_red, ci, cr, ref_cap, cand_cap)
        results[name] = {"meta": _jsonable(meta), "score": _jsonable(sc),
                         "align": _jsonable(off),
                         "ref_cap_y": ref_cap, "cand_cap_y": cand_cap,
                         "size": [int(cshape[1]), int(cshape[0])],
                         "svg_w": round(W, 2), "svg_h": round(H, 2)}
        print("%-4s IoU %.4f red IoU %s  size %dx%d  align %s"
              % (name, sc["iou"], sc.get("red_iou"), cshape[1], cshape[0], off))

    json.dump(results, open(os.path.join(RUN, "audit/wordmark-scores.json"), "w"), indent=1)


if __name__ == "__main__":
    main()