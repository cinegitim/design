#!/usr/bin/env python
"""Identify the closest open-licence typeface to the approved wordmark reference.

Renders each candidate's "ASYA'DA" at the reference's cap height and weight,
then scores per-glyph shape agreement against the reference. The score guides
the choice; it is not the final judgement — the reference's letterforms are
checked by eye afterwards.

Comparison is shape-only (normalised, aligned on the glyph's own bounding box),
so it measures letterform character rather than size or position.
"""
import os
import subprocess
import sys

import numpy as np
from fontTools.pens.svgPathPen import SVGPathPen
from fontTools.pens.transformPen import TransformPen
from fontTools.ttLib import TTFont
from fontTools.varLib.instancer import instantiateVariableFont
from PIL import Image, ImageDraw

ROOT = "/Users/serdaryurt/Documents/OpenCode/Design"
RUN = os.path.join(ROOT, "brands/asyada-egitim/explorations/wordmark-ref")
CAND = os.path.expanduser("~/.cache/brand-studio/fonts/shortlist")

PAPER_L, INK_L = 243.0, 235.0

# the reference's Turkish line, glyph by glyph, in the order it appears
REF_GLYPHS = list("ASYADA")          # TR1 without the apostrophe (A S Y A D A)
REF_APOS = "'"


def glyph_path(font, ch, upem):
    cmap = font.getBestCmap()
    gname = cmap.get(ord(ch))
    if gname is None:
        return None
    gs = font.getGlyphSet()
    pen = SVGPathPen(gs)
    t = TransformPen(pen, (upem / 1000.0, 0, 0, upem / 1000.0))
    gs[gname].draw(t)
    return pen.getCommands()


def render_glyph(commands, px=160):
    svg = ('<svg xmlns="http://www.w3.org/2000/svg" width="%d" height="%d" '
           'viewBox="-200 -200 1400 1400"><rect x="-200" y="-200" width="1400" '
           'height="1400" fill="#1D2027"/><path d="%s" fill="#F7F3E9"/></svg>'
           % (px, px, commands))
    open("/tmp/_g.svg", "w").write(svg)
    subprocess.run(["rsvg-convert", "-w", str(px), "-o", "/tmp/_g.png", "/tmp/_g.svg"],
                   check=True)
    return np.asarray(Image.open("/tmp/_g.png").convert("RGB")).astype(np.float32)


def norm(mask, n=64):
    """Crop to ink, square-pad, resample to n x n, return bool."""
    ys, xs = np.where(mask)
    if len(ys) == 0:
        return np.zeros((n, n), bool)
    m = mask[ys.min():ys.max() + 1, xs.min():xs.max() + 1]
    h, w = m.shape
    s = max(h, w)
    canvas = np.zeros((s, s), bool)
    canvas[(s - h) // 2:(s - h) // 2 + h, (s - w) // 2:(s - w) // 2 + w] = m
    return np.asarray(Image.fromarray((canvas * 255).astype(np.uint8))
                      .resize((n, n), Image.LANCZOS)) > 127


def ref_masks():
    """Per-glyph reference masks for A S Y A D from the reference raster.

    TR1 also contains the red apostrophe, and red is dark enough to pass the
    ink threshold, so components are split by hue: a red-dominant component is
    the apostrophe and is dropped. Without that filter the glyph list would be
    7 long and every subsequent glyph would be compared against the wrong
    letter.
    """
    import cv2
    img = Image.open(os.path.join(RUN, "reference.jpg")).convert("RGB")
    a = np.asarray(img).astype(np.float32)
    L = a[..., 0] * 0.2126 + a[..., 1] * 0.7152 + a[..., 2] * 0.0722
    ink = (L < INK_L).astype(np.uint8)
    red = (a[..., 0] - a[..., 1] > 25) & (a[..., 0] - a[..., 2] > 25) & ink.astype(bool)
    ink = ink & ~red
    band = np.zeros_like(ink)
    band[68:210, :] = ink[68:210, :]
    n, lab, stats, _ = cv2.connectedComponentsWithStats(band, connectivity=8)
    comps = []
    for k in range(1, n):
        x, y, w, h, area = stats[k]
        if area < 400:
            continue
        comps.append((int(x), (lab[y:y + h, x:x + w] == k)))
    comps.sort(key=lambda c: c[0])
    return comps


def score_font(path, label):
    font = TTFont(path)
    if "fvar" in font:
        for ax in font["fvar"].axes:
            if getattr(ax, "tag", ax.axisTag) == "wght":
                font = instantiateVariableFont(font, {"wght": 600}, inplace=False)
    upem = font["head"].unitsPerEm
    total, per = 0.0, []
    for ch, (_x, ref) in zip(REF_GLYPHS, ref_masks()):
        cmd = glyph_path(font, ch, upem)
        if not cmd:
            return None, {}
        m = render_glyph(cmd)
        L = m[..., 0] * 0.2126 + m[..., 1] * 0.7152 + m[..., 2] * 0.0722
        cm = L > (PAPER_L + INK_L) / 2        # glyph is the light colour here
        A, B = norm(cm), norm(ref)
        iou = float((A & B).sum()) / float((A | B).sum())
        per.append((ch, round(iou, 3)))
        total += iou
    return total / len(per), dict(per)


def main():
    fonts = sorted(f for f in os.listdir(CAND) if f.endswith(".ttf"))
    rows = []
    for f in fonts:
        try:
            s, per = score_font(os.path.join(CAND, f), f)
        except Exception as exc:                       # noqa: BLE001
            print("skip %s: %s" % (f, exc))
            continue
        if s is None:
            print("skip %s: missing glyph" % f)
            continue
        rows.append((s, f, per))
    rows.sort(reverse=True)
    print("\n%-24s %6s   %s" % ("font", "mean", "per-glyph IoU (A S Y A D A)"))
    print("-" * 74)
    for s, f, per in rows:
        print("%-24s %6.3f   %s" % (f, s, " ".join("%s=%.3f" % (c, v)
                                                  for c, v in per.items())))
    return rows


if __name__ == "__main__":
    main()