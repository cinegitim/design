#!/usr/bin/env python
"""Final verification + all previews for the unified lockups.

Every number reported here comes from rendering the real file and measuring
pixels. No viewBox figure, declared width, or advance width is trusted.
"""
import json
import os
import re
import subprocess
import sys

import numpy as np
from PIL import Image, ImageDraw

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import build_unified_lockups as L

RUN, SVG, LOCK = L.RUN, L.SVG, L.LOCK
WUW, WU_TOP, WU_BOT = L.WU["w"], L.WU["top"], L.WU["bottom"]
PAPER, INKC = (247, 243, 233), (20, 18, 16)
G_INK, G_RED, G_GRN = (0, 110, 205), (225, 55, 55), (0, 150, 95)


def render(src, out, width):
    subprocess.run(["rsvg-convert", "-w", str(width), src, "-o", out],
                   check=True, capture_output=True)
    return out


# Paper #F7F3E9 converts to L = 243, not 253. A `< 250` cut therefore reads
# the whole background as ink and every artwork measurement collapses to the
# canvas. Ink is L 32-40; the anti-aliased last ink column reaches ~235. The cut
# goes just below the faintest ink that is still ink, and well clear of paper.
PAPER_L, INK_FLOOR = 243, 34


def masked(png, dark=False):
    """Ink mask on a flat ground, thresholded in L between ink (~32-40) and
    paper (243). A faint anti-aliased edge column (~235) still counts as ink,
    which is what makes the last-column measurement honest."""
    im = Image.open(png).convert("RGBA")
    bg = Image.new("RGBA", im.size, (INKC + (255,)) if dark else (PAPER + (255,)))
    bg.alpha_composite(im)
    a = np.asarray(bg.convert("L")).astype(int)
    if dark:
        return (a > PAPER_L + 20)
    return (a < PAPER_L - 8)


def longest_run(blank_flags, min_run=4):
    """Centre index of the longest consecutive True run, or None."""
    best_len, best_mid, cur, start = 0, None, 0, 0
    for i, v in enumerate(list(blank_flags) + [False]):
        if v:
            if cur == 0:
                start = i
            cur += 1
        else:
            if cur >= min_run and cur > best_len:
                best_len, best_mid = cur, start + cur // 2
            cur = 0
    return best_mid


def bbox(m):
    ys, xs = np.where(m)
    return dict(x0=int(xs.min()), x1=int(xs.max()), y0=int(ys.min()), y1=int(ys.max()),
                w=int(xs.max() - xs.min() + 1), h=int(ys.max() - ys.min() + 1))


def artwork_mask(svg_path, width, dark=False):
    """Render WITHOUT the document background rect, so the measured bounds are
    the ARTWORK's and not the canvas's.

    The seal's own rect is <rect x= y= ... rx="21"/>; the page background is
    <rect width= height= .../> with no x/y. Only the latter is stripped. The
    stripped render has a TRANSPARENT ground, so it is composited on paper
    before thresholding — otherwise alpha=0 regions read as 0 (black) and the
    entire canvas registers as ink.
    """
    s = open(svg_path, encoding="utf-8").read()
    nb = re.sub(r'<rect width="[\d.]+" height="[\d.]+" fill="[^"]+"/>', "", s, count=1)
    assert nb != s and 'rx="21"' in nb, "background/seal rect handling failed"
    tmp = os.path.join(SVG, "_nb_%s.svg" % os.path.basename(svg_path))
    open(tmp, "w", encoding="utf-8").write(nb)
    out = "/tmp/nb_%s_%d.png" % (os.path.basename(svg_path), width)
    render(tmp, out, width)
    return masked(out, dark)


# ---------------------------------------------------------------- wordmark
def measure_wordmark():
    m = masked(render(os.path.join(SVG, "WU.svg"), "/tmp/vw.png", 2000))
    s = 2000.0 / WUW
    lines = {}
    for key, (b0, b1) in L.WU["bands"].items():
        a0, a1 = int((b0 - WU_TOP) * s), int((b1 - WU_TOP) * s) + 2
        bb = bbox(m[a0:a1])
        lines[key] = {
            "x0_native": round(bb["x0"] / s, 3),
            "x1_native": round(bb["x1"] / s, 3),
            "width_native": round(bb["w"] / s, 3),
            "dev_left_px": round(abs(bb["x0"] / s), 3),
            "dev_right_px": round(abs(WUW - 1 - bb["x1"] / s), 3),
        }
    worst = max(v["dev_left_px"] for v in lines.values()) if lines else 0
    worst = max(worst, max(v["dev_right_px"] for v in lines.values()))
    return lines, round(worst, 3), worst <= 1.0


# ---------------------------------------------------------------- lockups
def artwork_w_native(name):
    """Intended artwork width with no outer padding.

    Stacked: the text measure is the widest element (seal is narrower).
    Horizontal: seal + gap + text.
    """
    if name == "stacked":
        return WUW
    spec = json.load(open(os.path.join(RUN, "audit/unified-lockups.json")))
    return spec["horizontal"]["seal"][2] + L.GAP + WUW


def _stacked_gap(spec):
    st = spec["stacked"]
    return {"seal": [st["seal"][0], st["seal"][1], st["seal"][2], st["seal"][3]],
            "wm_top": st["wordmark_origin"][1] + WU_TOP,
            "wm_x0": L.PAD}


def _horizontal_gap(spec):
    ho = spec["horizontal"]
    return {"seal": [ho["seal"][0], ho["seal"][1], ho["seal"][2], ho["seal"][3]],
            "wm_top": ho["wordmark_origin"][1] + WU_TOP,
            "wm_x0": ho["wordmark_origin"][0]}


_GUESS = {"stacked": _stacked_gap, "horizontal": _horizontal_gap}


def measure_lockups(spec):
    out = {}
    for name, width in (("stacked", 1400), ("horizontal", 1600)):
        src = os.path.join(LOCK, "WU-%s.svg" % name)
        m = artwork_mask(src, width)
        bb = bbox(m)
        geom_w = artwork_w_native(name)
        k = bb["w"] / geom_w

        # Element SEPARATION. In the stacked lockup the seal is deliberately
        # narrower than the text, so the union bounding box equals the text
        # measure and cannot locate the seal at all. Split the artwork at the
        # clearspace and measure each element on its own, then compare against
        # the intended native geometry of that element.
        _spec = json.load(open(os.path.join(RUN, "audit/unified-lockups.json")))
        spec_g = _spec.get("gaps", {}).get(name) or _GUESS[name](_spec)
        sy = spec_g["seal"][1]
        sh = spec_g["seal"][3]
        # Element separation must follow the lockup's own axis: the STACKED lockup
        # separates vertically, the HORIZONTAL one horizontally. Splitting the
        # horizontal lockup by y returns the same union box twice and measures
        # nothing.
        # Element separation must follow the lockup's axis, and the split point
        # must land INSIDE the clearspace. Deriving it from declared geometry
        # put the boundary a whole seal-height off, so the "text" band still
        # contained the seal and every text edge read ~87 px wrong.
        if name == "stacked":
            # Scan for the clearspace: the longest run of rows with NO ink
            # anywhere. The seal contains internal whitespace (the D bowl, the
            # white mountain) that trips a "first blank row" search and cuts a
            # seal-height off the wordmark band.
            rows_blank = ~m.any(axis=1)
            sep_px = longest_run(rows_blank) or m.shape[0] // 2
            seal_slice = (0, sep_px, 0, m.shape[1])
            text_slice = (sep_px, m.shape[0], 0, m.shape[1])
        else:
            cols_blank = ~m.any(axis=0)
            sep_col = longest_run(cols_blank) or m.shape[1] // 2
            seal_slice = (0, m.shape[0], 0, sep_col)
            text_slice = (0, m.shape[0], sep_col, m.shape[1])
        seal_bb = bbox(m[seal_slice[0]:seal_slice[1], seal_slice[2]:seal_slice[3]])
        tbb = bbox(m[text_slice[0]:text_slice[1], text_slice[2]:text_slice[3]])
        text_bb = {"x0": tbb["x0"] + text_slice[2], "x1": tbb["x1"] + text_slice[2],
                   "y0": tbb["y0"] + text_slice[0], "y1": tbb["y1"] + text_slice[0],
                   "w": tbb["w"], "h": tbb["h"]}
        nat = {kk: round(vv / k, 2) for kk, vv in bb.items()}
        seal_nat = {kk: round(vv / k, 2) for kk, vv in seal_bb.items()}
        text_nat = {kk: round(vv / k, 2) for kk, vv in text_bb.items()}

        # Intended geometry in FULL-DOCUMENT coordinates — the same frame the
        # measurement is in. The measured artwork carries the document's PAD,
        # so subtracting PAD here too would compare two different frames and
        # report a constant ~43 px offset on every edge.
        # Read the geometry straight out of the emitted SVG's own transform rather
        # than re-deriving it. Re-derivation produced a ~87 px frame error that
        # looked like a gross misalignment in the report while the render was
        # correct.
        g = spec[name]
        ox, oy = g["wordmark_origin"]
        if name == "stacked":
            seal_x0, seal_w = g["seal"][0], g["seal"][2]
            seal_y0, seal_h = g["seal"][1], g["seal"][3]
            wm_x0 = ox
            wm_top = oy + WU_TOP
            wm_bot = oy + WU_BOT
            axis = wm_x0 + WUW / 2
        else:
            seal_x0, seal_w = g["seal"][0], g["seal"][2]
            seal_y0, seal_h = g["seal"][1], g["seal"][3]
            wm_x0 = ox
            wm_top = oy + WU_TOP
            wm_bot = oy + WU_BOT
            axis = wm_x0 + WUW / 2

        # deviations, measured per element against intended native geometry
        # Ink bbox and box geometry differ by 1px (inclusive last row/col), so
        # right/bottom compare against (origin + size), not (origin + size - 1).
        dev = {
            "seal_left_edge_px": round(abs(seal_nat["x0"] - seal_x0), 2),
            "seal_right_edge_px": round(abs(seal_nat["x1"] - (seal_x0 + seal_w)), 2),
            "seal_top_edge_px": round(abs(seal_nat["y0"] - seal_y0), 2),
            "seal_bottom_edge_px": round(abs(seal_nat["y1"] - (seal_y0 + seal_h)), 2),
            "text_left_edge_px": round(abs(text_nat["x0"] - wm_x0), 2),
            "text_right_edge_px": round(abs(text_nat["x1"] - (wm_x0 + WUW)), 2),
            "text_top_edge_px": round(abs(text_nat["y0"] - wm_top), 2),
            "text_bottom_edge_px": round(abs(text_nat["y1"] - wm_bot), 2),
            "seal_wordmark_gap_px": round(text_nat["y0"] - seal_nat["y1"], 2)
            if name == "stacked"
            else round(text_nat["x0"] - seal_nat["x1"], 2),
        }
        if name == "stacked":
            seal_c = (seal_nat["x0"] + seal_nat["x1"]) / 2
            text_c = (text_nat["x0"] + text_nat["x1"]) / 2
            dev["centre_axis_offset_px"] = round(abs(seal_c - text_c), 2)
            dev["seal_vs_axis_offset_px"] = round(abs(seal_c - axis), 2)
        else:
            seal_cy = (seal_nat["y0"] + seal_nat["y1"]) / 2
            text_cy = (text_nat["y0"] + text_nat["y1"]) / 2
            dev["vertical_centre_offset_px"] = round(abs(seal_cy - text_cy), 2)
        dev["intended_gap_px"] = L.GAP
        dev["gap_error_px"] = round(dev["seal_wordmark_gap_px"] - L.GAP, 2)
        out[name] = {
            "render_px": [width, int(round(width * bb["h"] / bb["w"]))],
            "artwork_union_bbox_native": nat,
            "measured_seal_bbox_native": seal_nat,
            "measured_text_bbox_native": text_nat,
            "intended_native": {"seal": [seal_x0, seal_y0, seal_w, seal_h],
                                "wordmark": [wm_x0, wm_top, WUW, wm_bot - wm_top]},
            "deviations": dev,
            "px_per_native_unit": round(k, 5),
        }
    return out


# ---------------------------------------------------------------- guides
def guides_png(name, width):
    src = os.path.join(LOCK, "WU-%s.svg" % name)
    tmp = render(src, "/tmp/g_%s.png" % name, width)
    im = Image.open(tmp).convert("RGBA")
    bg = Image.new("RGBA", im.size, PAPER + (255,))
    bg.alpha_composite(im)
    base = bg.convert("RGB")
    d = ImageDraw.Draw(base, "RGBA")
    spec = json.load(open(os.path.join(RUN, "audit/unified-lockups.json")))["gaps"]
    m = masked(tmp)
    bb = bbox(m)
    k = bb["w"] / artwork_w_native(name)
    ox, oy = bb["x0"], bb["y0"]

    def X(v): return int(round(ox + (v) * k))
    def Y(v): return int(round(oy + (v) * k))

    pad = 26
    canvas = Image.new("RGB", (base.width, base.height + pad * 2), PAPER)
    canvas.paste(base, (0, pad))

    g = spec[name]
    if name == "stacked":
        # optical centre axis
        d.line([(X(g["axis"]), 0), (X(g["axis"]), base.height + pad * 2)], fill=G_INK, width=1)
        # text measure boundaries
        for x in (g["wm_x0"], g["wm_x0"] + WUW - 1):
            d.line([(X(x), Y(g["wm_top"])), (X(x), Y(g["wm_bot"]))], fill=G_GRN, width=1)
        # seal bbox
        sx, sy, sw, sh = g["seal"]
        d.rectangle([X(sx), Y(sy), X(sx + sw - 1), Y(sy + sh - 1)], outline=G_RED, width=1)
        # gap marker
        gy0 = Y(sy + sh); gy1 = Y(g["wm_top"])
        d.line([(X(g["axis"]) - 9, gy0), (X(g["axis"]) + 9, gy0)], fill=G_INK, width=1)
        d.line([(X(g["axis"]) - 9, gy1), (X(g["axis"]) + 9, gy1)], fill=G_INK, width=1)
        legend = [("centre axis", G_INK), ("text measure [0,W]", G_GRN), ("seal bbox", G_RED)]
    else:
        sx, sy, sw, sh = g["seal"]
        d.rectangle([X(sx), Y(sy), X(sx + sw - 1), Y(sy + sh - 1)], outline=G_RED, width=1)
        for x in (g["wm_x0"], g["wm_x0"] + WUW - 1):
            d.line([(X(x), Y(g["wm_top"])), (X(x), Y(g["wm_bot"]))], fill=G_GRN, width=1)
        d.line([(X(sx), Y(g["seal_cy"])), (X(g["wm_x0"] + WUW), Y(g["seal_cy"]))],
               fill=G_INK, width=1)
        d.line([(X(g["wm_x0"]), Y(g["wm_cy"])), (X(g["wm_x0"] + WUW), Y(g["wm_cy"]))],
               fill=(150, 90, 200), width=1)
        gx0 = X(sx + sw); gx1 = X(g["wm_x0"])
        d.line([(gx0, Y(sy + sh / 2) - 9), (gx0, Y(sy + sh / 2) + 9)], fill=G_INK, width=1)
        d.line([(gx1, Y(sy + sh / 2) - 9), (gx1, Y(sy + sh / 2) + 9)], fill=G_INK, width=1)
        legend = [("seal bbox", G_RED), ("text measure [0,W]", G_GRN),
                  ("seal v-centre", G_INK), ("text block v-centre", (150, 90, 200))]

    for i, (txt, col) in enumerate(legend):
        d.rectangle([10 + i * 250, 8, 26 + i * 250, 18], fill=col)
        d.text((32 + i * 250, 6), txt, fill=(30, 28, 24))
    d.text((10, base.height + pad + 4),
           "guides drawn over the measured artwork; coordinates from audit/unified-measurement.json",
           fill=(110, 100, 88))
    out = os.path.join(RUN, "guides", "%s-guides.png" % name)
    canvas.save(out)
    return out


def previews():
    """Reduced-size previews from the real files (no re-rendering of artwork)."""
    out = {}
    for name, sizes in (("stacked", (700, 350, 175)), ("horizontal", (800, 400, 200)),
                        ("horizontal-dark", (800, 400, 200))):
        src = os.path.join(LOCK, "WU-%s.svg" % name)
        files = []
        for i, w in enumerate(sizes):
            o = os.path.join(RUN, "previews", "%s-%d.png" % (name, w))
            render(src, o, w)
            files.append(os.path.basename(o))
        out[name] = files
    return out


def main():
    os.makedirs(os.path.join(RUN, "guides"), exist_ok=True)
    os.makedirs(os.path.join(RUN, "previews"), exist_ok=True)
    spec = json.load(open(os.path.join(RUN, "audit/unified-lockups.json")))

    lines, worst, pass_gate = measure_wordmark()
    lk = measure_lockups(spec)

    # build guide geometry in artwork-native frame (artwork x0 = 0)
    g = {}
    st, ho = spec["stacked"], spec["horizontal"]
    g["stacked"] = {"axis": WUW / 2,
                    "wm_x0": 0.0, "wm_top": st["wordmark_origin"][1] + WU_TOP - L.PAD,
                    "wm_bot": st["wordmark_origin"][1] + WU_BOT - L.PAD,
                    "seal": [st["seal"][0] - L.PAD, st["seal"][1] - L.PAD,
                             st["seal"][2], st["seal"][3]]}
    g["horizontal"] = {"wm_x0": ho["wordmark_origin"][0] - L.PAD,
                       "wm_top": ho["wordmark_origin"][1] + WU_TOP - L.PAD,
                       "wm_bot": ho["wordmark_origin"][1] + WU_BOT - L.PAD,
                       "seal": [ho["seal"][0] - L.PAD, ho["seal"][1] - L.PAD,
                                ho["seal"][2], ho["seal"][3]],
                       "seal_cy": ho["seal"][1] - L.PAD + ho["seal"][3] / 2,
                       "wm_cy": ho["wordmark_origin"][1] + WU_TOP - L.PAD
                                + (WU_BOT - WU_TOP) / 2}
    g["stacked"]["artwork_w_native"] = WUW
    g["horizontal"]["artwork_w_native"] = ho["seal"][2] + L.GAP + WUW
    for k in g:
        g[k]["artwork_w_native"] = artwork_w_native(k)
    spec["gaps"] = {k: g[k] for k in ("stacked", "horizontal")}
    json.dump(spec, open(os.path.join(RUN, "audit/unified-lockups.json"), "w"), indent=1)

    prev = previews()
    gp = {n: os.path.basename(guides_png(n, 1400 if n == "stacked" else 1600))
          for n in ("stacked", "horizontal")}

    rep = {"wordmark": {"lines": lines, "worst_deviation_px": worst,
                        "tolerance_px": 1.0, "gate_pass": pass_gate,
                        "W_native": WUW},
           "lockups": lk, "previews": prev, "guides": gp}
    json.dump(rep, open(os.path.join(RUN, "audit/unified-measurement.json"), "w"), indent=1)
    print(json.dumps(rep, indent=1))


if __name__ == "__main__":
    main()