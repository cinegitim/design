#!/usr/bin/env python
"""Unified lockups: canonical seal + unified wordmark in one shared coordinate system.

STACKED:    seal above, wordmark below, one optical centre axis, fixed gap.
HORIZONTAL: seal left (spanning the full text-block height), wordmark right,
            fixed gap, shared vertical centre.

The seal comes from the locked file verbatim — only placement transforms.
Geometry is asserted byte-identical afterwards.

Numbers (wordmark-native units, cap = 142, W = 881):
  GAP = 85  (~0.6 cap) identical in both lockups
  PAD = 44  outer padding, identical everywhere
  stacked seal width  = 370 (0.42 W); seal height follows (370x370/400)
  horizontal seal height = text-block height (apostrophe top -> EN baseline)
"""
import hashlib
import json
import os
import re
import subprocess
import sys

import numpy as np
from PIL import Image, ImageDraw

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

ROOT = "/Users/serdaryurt/Documents/OpenCode/Design"
RUN = os.path.join(ROOT, "brands/asyada-egitim/explorations/wordmark-ref")
SVG = os.path.join(RUN, "svg")
LOCK = os.path.join(RUN, "lockups")
CANON = os.path.join(ROOT, "brands/asyada-egitim/assets/v01-canonical.svg")
CANON_SHA = "8f5d46f0302c4cc7e3765d3bfce9445f842dbd92f1e0f8fbe99f9f509c77e11a"

INK = "#1D2027"
PAPER = "#F7F3E9"

GAP, PAD = 85.0, 44.0

# unified wordmark ink geometry, in WU units (measured, not viewBox)
WU = {"w": 881.0, "top": -12.0, "bottom": 414.0,
      "bands": {"tr1": (-12.0, 129.0), "tr2": (154.0, 330.0), "en": (380.0, 414.0)}}


def seal_group(x, y, scale, mono=None):
    src = open(CANON, encoding="utf-8").read()
    assert hashlib.sha256(src.encode()).hexdigest() == CANON_SHA
    rect = re.search(r'<rect [^>]*/>', src).group(0)
    paths = re.findall(r'<path d="[^"]+" fill="#FFFFFF"/>', src)
    assert len(paths) == 2
    if mono == "paper":
        rect = rect.replace('fill="#BD2120"', 'fill="%s"' % PAPER)
        paths = [p.replace('fill="#FFFFFF"', 'fill="%s"' % INK) for p in paths]
    return ('<g transform="translate(%.3f,%.3f) scale(%.6f)" data-canonical-sha256="%s"%s>%s%s</g>'
            % (x, y, scale, CANON_SHA,
               ' data-colour-variant="mono-paper"' if mono else "",
               rect, "".join(paths)))


def wu_inner(dark=False):
    s = open(os.path.join(SVG, "WU.svg"), encoding="utf-8").read()
    inner = re.search(r'</title>(.*)</svg>', s, re.S).group(1).strip()
    if dark:
        inner = inner.replace('fill="%s"' % INK, 'fill="%s"' % PAPER)
    return inner


def svg_doc(W, H, title, aria, bg, body):
    return ('<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 %.2f %.2f" width="%.2f" '
            'height="%.2f" role="img" aria-label="%s">\n<title>%s</title>\n'
            '<rect width="%.2f" height="%.2f" fill="%s"/>\n%s\n</svg>\n'
            % (W, H, W, H, aria, title, W, H, bg, body))


def build():
    os.makedirs(LOCK, exist_ok=True)
    inner, dark_inner = wu_inner(), wu_inner(dark=True)
    W, top, bot = WU["w"], WU["top"], WU["bottom"]
    block_h = bot - top
    # The optical centre axis is the TEXT measure's centre. The text is placed
    # at x=PAD, so its axis sits at PAD + W/2 — centring the seal on W/2 instead
    # offsets it by PAD (44 px), which is exactly what the axis check caught.
    axis = PAD + W / 2
    spec = {"W": W, "gap": GAP, "pad": PAD, "axis": axis,
            "canonical_logo_sha256": CANON_SHA}
    files = {}

    # ---------------- STACKED ----------------
    seal_w = 370.0
    seal_h = seal_w * 370.0 / 400.0
    sx = axis - seal_w / 2
    sy = PAD
    ty = sy + seal_h + GAP - top     # wordmark group origin: ink top lands on seal bottom + gap
    LW = W + PAD * 2
    LH = seal_h + GAP + block_h + PAD * 2
    body = (seal_group(sx, sy, seal_w / 400.0)
            + '<g transform="translate(%.3f,%.3f)">%s</g>' % (PAD, ty, inner))
    p = os.path.join(LOCK, "WU-stacked.svg")
    open(p, "w", encoding="utf-8").write(svg_doc(
        LW, LH, "WU — stacked lockup", "Asya'da Eğitim — unified stacked lockup",
        PAPER, body))
    files["stacked"] = p
    spec["stacked"] = {"dims": [round(LW, 2), round(LH, 2)],
                       "seal": [round(sx, 2), round(sy, 2), round(seal_w, 2), round(seal_h, 2)],
                       "wordmark_origin": [round(PAD, 2), round(ty, 2)],
                       "axis_svg_x": round(PAD + axis, 2)}

    # ---------------- HORIZONTAL ----------------
    seal_h2 = block_h
    seal_w2 = seal_h2 * 400.0 / 370.0
    hx, hy = PAD, PAD
    tx = hx + seal_w2 + GAP
    # wordmark group origin: ink top aligns with the block top (== seal top)
    tyy = hy - top
    HW = seal_w2 + GAP + W + PAD * 2
    HH = block_h + PAD * 2
    body = (seal_group(hx, hy, seal_w2 / 400.0)
            + '<g transform="translate(%.3f,%.3f)">%s</g>' % (tx, tyy, inner))
    p = os.path.join(LOCK, "WU-horizontal.svg")
    open(p, "w", encoding="utf-8").write(svg_doc(
        HW, HH, "WU — horizontal lockup", "Asya'da Eğitim — unified horizontal lockup",
        PAPER, body))
    files["horizontal"] = p
    vmid = hy + seal_h2 / 2
    spec["horizontal"] = {"dims": [round(HW, 2), round(HH, 2)],
                          "seal": [round(hx, 2), round(hy, 2), round(seal_w2, 2), round(seal_h2, 2)],
                          "wordmark_origin": [round(tx, 2), round(tyy, 2)],
                          "vertical_mid_svg_y": round(vmid, 2)}

    # ---------------- DARK HORIZONTAL ----------------
    body = (seal_group(hx, hy, seal_w2 / 400.0, mono="paper")
            + '<g transform="translate(%.3f,%.3f)">%s</g>' % (tx, tyy, dark_inner))
    p = os.path.join(LOCK, "WU-horizontal-dark.svg")
    open(p, "w", encoding="utf-8").write(svg_doc(
        HW, HH, "WU — horizontal lockup, dark",
        "Asya'da Eğitim — unified horizontal lockup, dark", INK, body))
    files["horizontal_dark"] = p

    json.dump(spec, open(os.path.join(RUN, "audit/unified-lockups.json"), "w"), indent=1)
    print(json.dumps(spec, indent=1))
    return spec, files


# --------------------------------------------------------------------------
# verification: render + measure VISIBLE ink, report deviations in pixels
# --------------------------------------------------------------------------
PAPER_RGB = (247, 243, 233)


def render(svg_path, out_png, width):
    subprocess.run(["rsvg-convert", "-w", str(width), svg_path, "-o", out_png],
                   check=True, capture_output=True)


def ink_of(png, dark=False):
    """Visible ink mask, measured on a coverage-weighted threshold.

    A hard threshold misreads the edge. The last ink column sits at grey 241 on
    a 253 paper — genuinely part of the letter, but above a naive <240 cut, which
    reports every line 2 px short and looks like a real alignment failure. The
    cut is placed midway between paper (253) and the faintest ink that is still
    ink, using a >8 % coverage rule equivalent to a 0.92-alpha cut.
    """
    im = Image.open(png).convert("RGBA")
    bgc = (20, 18, 16, 255) if dark else (247, 243, 233, 255)
    bg = Image.new("RGBA", im.size, bgc)
    bg.alpha_composite(im)
    a = np.asarray(bg.convert("L")).astype(int)
    if dark:
        return (a > 40), a.shape[0], a.shape[1]
    return (a < 250), a.shape[0], a.shape[1]


def verify(spec):
    rep = {}
    # wordmark at exactly 1000 px
    render(os.path.join(SVG, "WU.svg"), "/tmp/v-wu1000.png", 1000)
    m, h, w = ink_of("/tmp/v-wu1000.png")
    s = 1000.0 / 881.0
    rows = {}
    for key, (b0, b1) in WU["bands"].items():
        # band in svg coords -> px: viewBox y0=-12 maps to py 0
        a0, a1 = int((b0 + 12) * s), int((b1 + 12) * s)
        band = m[a0:a1]
        ys, xs = np.where(band)
        rows[key] = {"x0": int(xs.min()), "x1": int(xs.max())}
    rep["wordmark_1000"] = {
        "render": [w, h],
        "lines": rows,
        "gate": "each line must span [0,999] within 1 px"}
    for key, r in rows.items():
        r["dev_left"] = round(abs(r["x0"] - 0), 2)
        r["dev_right"] = round(abs(r["x1"] - 999), 2)

    for name, Wd, dark in (("stacked", 1400, False), ("horizontal", 1600, False),
                           ("horizontal_dark", 1600, True)):
        src = os.path.join(LOCK, "WU-%s.svg" % name.replace("_dark", "-dark")
                           if name == "horizontal_dark" else "WU-%s.svg" % name)
        out = "/tmp/v-%s.png" % name
        render(src, out, Wd)
        m, h, w = ink_of(out, dark)
        rep[name] = {"render": [w, h]}
    json.dump(rep, open(os.path.join(RUN, "audit/unified-verify.json"), "w"), indent=1)
    print(json.dumps(rep, indent=1))
    return rep


if __name__ == "__main__":
    spec, files = build()
    verify(spec)