#!/usr/bin/env python
"""Build the unified three-line wordmark for candidates A and B.

Both candidates share the SAME layout contract as the approved WU wordmark:

  * measure W = 881 native px, all three lines filling it exactly
  * rigid glyph bodies — only inter-letter gaps change, nothing is stretched
  * the same band geometry and the same apostrophe allowance above the cap line
  * ink, vermilion and paper unchanged

A: outlines from a real open-licence typeface, optically customised.
B: hand-drafted custom glyphs.

Neither uses approxPolyDP, raster tracing or automatic raster-to-Bezier fitting.

Lines are aligned on their INK, not their advance: tracking is corrected by
measuring the rendered ink and adjusting the gaps until all three lines span
[0, W]. Only the gaps move; no glyph is scaled, condensed or stretched.
"""
import json
import os
import subprocess
import sys

import numpy as np
from PIL import Image

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import custom_glyphs as CG          # noqa: E402
import type_assy as TA              # noqa: E402

ROOT = "/Users/serdaryurt/Documents/OpenCode/Design"
RUN = os.path.join(ROOT, "brands/asyada-egitim/explorations/wordmark-ref")
SVG = os.path.join(RUN, "svg")
AUDIT = os.path.join(RUN, "audit")
CAND = os.path.expanduser("~/.cache/brand-studio/fonts/shortlist")

INK, VERM, PAPER = "#1D2027", "#BD2120", "#F7F3E9"
APOS = "'"

W = 881.0
CAP = 142.0
EN_CAP = 35.0
LEADING = 1.4155 * CAP
TR1_TOP = -12.0
TR1_BOT = TR1_TOP + CAP
TR2_TOP = TR1_BOT + (LEADING - CAP)
TR2_BOT = TR2_TOP + CAP
EN_TOP = TR2_BOT + (LEADING - CAP)
EN_BOT = EN_TOP + EN_CAP
VB_Y = TR1_TOP
VB_H = EN_BOT - VB_Y

LINES = [("tr1", "ASYA'DA", TR1_TOP, CAP),
         ("tr2", "EĞİTİM", TR2_TOP, CAP),
         ("en", "EDUCATION IN ASIA", EN_TOP, EN_CAP)]

A_FONT = os.path.join(CAND, "Jost-VF.ttf")
A_WGHT = 700
B_STEM = 168.0
APOS_G = CG.make(w=B_STEM)[APOS]


def _line_bands():
    return {"tr1": (TR1_TOP - 2, TR1_BOT + 3),
            "tr2": (TR2_TOP - 3, TR2_BOT + 3),
            "en": (EN_TOP - 3, EN_BOT + 3)}


# ------------------------------------------------------------------ candidate A
def build_A(tracking):
    """Jost (Futura lineage) — the reference's oblique S terminals, round G and
    D bowls and pointed A identify that family. Poppins was the runner-up but
    its S terminals are horizontal, the single most visible mismatch."""
    font = TA.load(A_FONT, wght=A_WGHT)
    parts, audit = [], {}
    for key, text, top, cap in LINES:
        k = TA.cap_scale(font, cap)
        base_y = top + cap
        tr = tracking.get(key, 0.0)
        out = []
        x = 0.0
        for ch in text:
            if ch == APOS:
                out.append('<g transform="translate(%.3f,%.3f) scale(%.6f,%.6f)" '
                           'fill="%s">%s</g>'
                           % (x, base_y, k, -k, VERM,
                              "".join('<path d="%s"/>' % d for d in APOS_G[1])))
                x += APOS_G[0] * k + tr
                continue
            d, _n, adv = TA.glyph_path(font, ch, k, x, base_y)
            if d:
                out.append('<path d="%s" fill="%s"/>' % (d, INK))
            x += adv * k + tr
        parts.append("".join(out))
        audit[key] = {"cap": cap, "tracking_px": round(tr, 3)}
    return parts, audit


# ------------------------------------------------------------------ candidate B
def build_B(tracking):
    G = CG.make(w=B_STEM)
    G[" "] = (260.0, [])
    parts, audit = [], {}
    for key, text, top, cap in LINES:
        k = cap / CG.CAP
        glyphs = [G[APOS if ch == APOS else ch] for ch in text]
        tr = tracking.get(key, 0.0)
        out = []
        x = 0.0
        for i, (ch, (adv, paths)) in enumerate(zip(text, glyphs)):
            col = VERM if ch == APOS else INK
            out.append('<g transform="translate(%.3f,%.3f) scale(%.6f,%.6f)" '
                       'fill="%s" fill-rule="evenodd">%s</g>'
                       % (x, top + cap, k, -k, col,
                          "".join('<path d="%s"/>' % d for d in paths)))
            x += adv * k + tr
        parts.append("".join(out))
        audit[key] = {"cap": cap, "tracking_px": round(tr, 3)}
    return parts, audit


BUILDERS = {"A": build_A, "B": build_B}


def emit(parts, name, audit, note, shift=None):
    shift = shift or {}
    keys = [l[0] for l in LINES]
    body = "".join(
        '<g transform="translate(%.3f,0)">%s</g>' % (shift.get(k, 0.0), p)
        for k, p in zip(keys, parts))
    svg = ('<svg xmlns="http://www.w3.org/2000/svg" width="%g" height="%g" '
           'viewBox="0 %g %g %g">'
           '<rect x="0" y="%g" width="%g" height="%g" fill="%s"/>%s</svg>'
           % (W, VB_H, VB_Y, W, VB_H, VB_Y, W, VB_H, PAPER, body))
    open(os.path.join(SVG, name), "w", encoding="utf-8").write(svg)
    return {"file": name, "viewBox": [0, VB_Y, W, VB_H], "lines": audit, "note": note}


def measure(name):
    """Per-line ink extents of the RENDERED wordmark, in native units."""
    tmp = "/tmp/_tc_meas.png"
    subprocess.run(["rsvg-convert", "-w", "8810", "-o", tmp,
                    os.path.join(SVG, name)], check=True)
    a = np.asarray(Image.open(tmp).convert("RGB")).astype(np.float32)
    L = a[..., 0] * 0.2126 + a[..., 1] * 0.7152 + a[..., 2] * 0.0722
    ink = L < 235.0
    out = {}
    for key, (y0, y1) in _line_bands().items():
        rows = (np.arange(ink.shape[0]) >= int(y0 * 10)) & \
               (np.arange(ink.shape[0]) < int(y1 * 10))
        cols = np.where((ink & rows[:, None]).any(0))[0]
        if len(cols) == 0:
            out[key] = None
            continue
        out[key] = {"x0": cols.min() / 10.0, "x1": cols.max() / 10.0,
                    "w": (cols.max() - cols.min()) / 10.0}
    return out


def build_corrected(label, name, note):
    """Measure the ink, then correct tracking until every line spans [0, W].

    Ink WIDTH grows by exactly one tracking step per gap, so width is what
    tracking fixes. The left edge is then a single whole-line translation of
    -x0, because the first glyph always sits at pen position 0 and its left
    sidebearing alone decides where the ink starts.
    """
    fn = BUILDERS[label]
    tracking, shift = {}, {k: 0.0 for k, _t, _c, _p in
                           [(l[0], l[1], l[2], l[3]) for l in LINES]}
    result = None
    for _ in range(4):
        parts, aud = fn(tracking)
        result = emit(parts, name, aud, note, shift)
        m = measure(name)
        worst_w, worst_x = 0.0, 0.0
        for key, text, _t, _c in LINES:
            v = m.get(key)
            if v is None:
                continue
            n = max(1, len(text) - 1)
            worst_w = max(worst_w, abs(v["w"] - W))
            worst_x = max(worst_x, abs(v["x0"]))
            tracking[key] = tracking.get(key, 0.0) + (W - v["w"]) / n
            shift[key] = shift.get(key, 0.0) - v["x0"]
        if worst_w <= 0.3 and worst_x <= 0.3:
            break
    parts, aud = fn(tracking)
    result = emit(parts, name, aud, note, shift)
    result["ink"] = measure(name)
    result["final_tracking_px"] = {k: round(v, 3) for k, v in tracking.items()}
    return result


def main():
    os.makedirs(SVG, exist_ok=True)
    os.makedirs(AUDIT, exist_ok=True)
    ra = build_corrected("A", "WA.svg",
                         "candidate A - genuine outlines from Jost (SIL OFL) at "
                         "wght %d, optically tracked on ink" % A_WGHT)
    rb = build_corrected("B", "WB.svg",
                         "candidate B - hand-drafted glyphs, %d stem on a %d unit "
                         "em; straight edges exact, curves true circular arcs"
                         % (B_STEM, CG.CAP))
    json.dump({"measure_W": W, "candidates": {"A": ra, "B": rb}},
              open(os.path.join(AUDIT, "type-candidates.json"), "w"), indent=2)
    for r in (ra, rb):
        print("\n%s  %s" % (r["file"], r["note"]))
        for key, _t, _c in [(l[0], 0, 0) for l in LINES]:
            v = r["ink"].get(key)
            print("   %-4s ink x %7.2f .. %7.2f  width %7.2f  (target %g)"
                  % (key, v["x0"], v["x1"], v["w"], W))
    return 0


if __name__ == "__main__":
    sys.exit(main())