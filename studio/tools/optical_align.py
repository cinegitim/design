#!/usr/bin/env python
"""Independent optical alignment measurement for the horizontal lockup.

The existing horizontal lockup centres the seal on the whole wordmark bounding
box. That is a geometric fact, not a perceptual one: the box includes the
apostrophe, which overshoots the cap line by 12 native px, and it includes the
gap under the EN line. A box-centred seal therefore sits optically high.

This module measures the things the eye actually weighs, separately:

  seal_top / seal_bottom          visible seal ink, measured from the render
  cap_line                        TR1 baseline-to-apex, measured from the render
  apostrophe_overshoot            how far the apostrophe rises above the cap line
  wordmark_top / wordmark_bottom  complete wordmark ink
  perceived_centre                ink-weighted centroid, i.e. where the mass is
  optical_centre                  midpoint of the CAP-TO-BASELINE band, which is
                                  what the eye uses as the reference line for
                                  the flat-sided seal

It then emits four horizontal previews at controlled offsets of -4, 0, +4 and
+8 native px relative to the current placement, each still containing the
exact canonical seal, untransformed apart from translation and uniform scale.

Nothing here selects an answer. The four offsets are laid out for human review.
"""
import hashlib
import json
import os
import re
import subprocess
import sys

import numpy as np
from PIL import Image

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from build_unified_lockups import CANON, CANON_SHA, GAP, PAD, PAPER, seal_group  # noqa: E402

ROOT = "/Users/serdaryurt/Documents/OpenCode/Design"
RUN = os.path.join(ROOT, "brands/asyada-egitim/explorations/wordmark-ref")
SVG = os.path.join(RUN, "svg")
LOCK = os.path.join(RUN, "lockups")
OUT = os.path.join(RUN, "alignment")
AUDIT = os.path.join(RUN, "audit")

# Paper #F7F3E9 converts to L = 243; ink sits at L 32-40. Anything below 235 is
# unambiguously ink. An earlier threshold of 250 read the PAPER as ink and
# collapsed every measurement to the canvas size.
INK_L = 235.0
SCALE = 10.0          # render at 10x native for sub-pixel edge resolution
PAPER_L = 243.0

OFFSETS = (-4.0, 0.0, 4.0, 8.0)


def render(svg_text, width_px):
    p = "/tmp/_oa_%d.svg" % abs(hash(svg_text) % (10 ** 8))
    open(p, "w", encoding="utf-8").write(svg_text)
    subprocess.run(["rsvg-convert", "-w", str(int(width_px)), "-o", "/tmp/_oa.png", p],
                   check=True)
    return Image.open("/tmp/_oa.png").convert("RGB")


def ink_mask(im):
    """Boolean ink mask. Paper is L=243 and must NOT be counted as ink."""
    a = np.asarray(im).astype(np.float32)
    L = a[..., 0] * 0.2126 + a[..., 1] * 0.7152 + a[..., 2] * 0.0722
    return L < INK_L


def wordmark_svg():
    src = open(os.path.join(SVG, "WU.svg"), encoding="utf-8").read()
    vb = re.search(r'viewBox="([^"]+)"', src).group(1).split()
    return src, [float(v) for v in vb]


def wrap(width, height, body, bg=PAPER):
    return ('<svg xmlns="http://www.w3.org/2000/svg" width="%d" height="%d" '
            'viewBox="0 0 %d %d">'
            '<rect width="%d" height="%d" fill="%s"/>%s</svg>'
            % (width, height, width, height, width, height, bg, body))


def measure_vertical(ref_y0, ref_y1):
    """Vertical measurements from a high-resolution render, in native units.

    ref_y0/ref_y1 are the native-space y range covered by the render.
    """
    a = ink_mask(Image.open("/tmp/_oa.png"))
    rows = np.where(a.any(1))[0]
    h = a.shape[0]
    y0 = ref_y0 + rows.min() / SCALE
    y1 = ref_y0 + rows.max() / SCALE
    # ink-weighted centroid (perceived mass centre)
    ys = np.arange(h)[:, None]
    mass = a.sum()
    centroid = ref_y0 + float((ys * a).sum() / mass) / SCALE
    return {"top": y0, "bottom": y1, "bbox_centre": (y0 + y1) / 2.0,
            "ink_centroid": centroid, "mass": int(mass)}


def measure_tr1(ref_y0):
    """Isolate TR1's cap line and the apostrophe overshoot.

    The apostrophe is the only component that rises above the cap line, so it
    is found as a small, isolated connected component above the main body mass
    rather than by thresholding a row profile — a narrow mark like the
    apostrophe still trips a row-sum test and reports an overshoot of zero.
    """
    import cv2
    a = ink_mask(Image.open("/tmp/_oa.png")).astype(np.uint8)
    rowsum = a.sum(1)
    top_row = int(np.argmax(rowsum > 0))
    # Find the FIRST INTERNAL BAND GAP. Scanning only the non-empty rows cannot
    # find it at all: the gap between TR1 and TR2 is entirely zero-ink rows and
    # therefore absent from that list, so the scan ran straight through to the
    # bottom of the wordmark and reported a 426 px "TR1 band".
    nz = rowsum > 0
    gap_after = None
    for r in range(top_row + 1, len(rowsum) - 1):
        if not nz[r:r + int(3 * SCALE)].any():
            gap_after = r
            break
    band_bottom = (gap_after - 1) if gap_after is not None else len(rowsum) - 1
    sub = a[top_row:band_bottom + 1]
    n, lab, stats, _ = cv2.connectedComponentsWithStats(sub, connectivity=8)
    if n < 2:
        return {"cap_line_y": ref_y0 + top_row / SCALE,
                "apostrophe_top_y": None, "band_rows": [top_row, band_bottom]}
    band_h_px = band_bottom - top_row
    body_tops, small_tops = [], []
    for k in range(1, n):
        h = stats[k, cv2.CC_STAT_HEIGHT]
        t = top_row + int(stats[k, cv2.CC_STAT_TOP])
        # a letter is tall; the apostrophe is a small mark. Splitting on height
        # is what keeps the apostrophe out of the cap-line statistic — taking
        # the absolute topmost pixel instead reports the A's 1 px apex sliver
        # as the cap line, which understates the cap height by ~12 px.
        (body_tops if h > 0.5 * band_h_px else small_tops).append(t)
    cap_line = float(np.median(body_tops)) if body_tops else float(top_row)
    ap_top = min(small_tops) if small_tops else None
    return {"cap_line_y": ref_y0 + cap_line / SCALE,
            "letter_top_median_y": ref_y0 + cap_line / SCALE,
            "apostrophe_top_y": (ref_y0 + ap_top / SCALE) if ap_top is not None else None,
            "band_top_y": ref_y0 + top_row / SCALE,
            "band_bottom_y": ref_y0 + band_bottom / SCALE,
            "band_rows": [top_row, band_bottom]}


def build_horizontal(offset, seal_h, text_top, text_bottom):
    """Horizontal lockup with the seal shifted vertically by `offset` native px.

    Placement is identical to the production lockup except for the offset, so
    the four previews differ by exactly the stated amount. The seal itself is
    never distorted: one uniform scale, one translation.
    """
    src, _ = wordmark_svg()
    scale = seal_h / 400.0
    seal_w = 400.0 * scale
    x0 = PAD
    # the whole composition is dropped by PAD so nothing clips the canvas; the
    # offset then moves ONLY the seal, relative to the wordmark
    seal = seal_group(x0, offset, scale)
    text = src.replace("<svg ", "<g ").replace("</svg>", "</g>")
    text = text.replace("<g ", '<g transform="translate(%.3f,0)" ' % (x0 + seal_w + GAP), 1)
    body = '<g transform="translate(0,%.3f)">%s%s</g>' % (PAD, seal, text)
    w = int(round(x0 + seal_w + GAP + 881.0 + PAD))
    h = int(round(PAD + seal_h + PAD))
    return wrap(w, h, body), {"seal_x": x0, "seal_y": PAD + offset,
                              "seal_scale": scale, "seal_w": seal_w, "seal_h": seal_h}


def main():
    os.makedirs(OUT, exist_ok=True)
    os.makedirs(AUDIT, exist_ok=True)

    _, vb = wordmark_svg()
    WU_TOP = -12.0
    # measured text block height: TR1 top (-12) -> EN baseline (414) = 426
    seal_h = 426.0
    # PAD of clear space above/below, so the seal is never clipped by the canvas
    text_top, text_bottom = PAD, PAD + seal_h

    report = {"canonical_sha256": CANON_SHA, "render_scale": SCALE,
              "ink_threshold_L": INK_L, "paper_L": PAPER_L, "variants": []}

    # ---- independent measurement of the UNMOVED wordmark -------------------
    src, _ = wordmark_svg()
    body = src.replace("<svg ", "<g ").replace("</svg>", "</g>")
    pad = 20
    canvas = wrap(round(881 + 2 * pad), round(427 + 2 * pad),
                  '<g transform="translate(%d,%d)">%s</g>' % (pad, pad - WU_TOP, body))
    canvas = canvas.replace('width="%d" height="%d" viewBox="0 0 %d %d"'
                            % (round(881 + 2 * pad), round(427 + 2 * pad),
                               round(881 + 2 * pad), round(427 + 2 * pad)),
                            'width="%d" height="%d" viewBox="0 0 %d %d"'
                            % (round(881 + 2 * pad), round(427 + 2 * pad),
                               round(881 + 2 * pad), round(427 + 2 * pad)))
    px_w = round((881 + 2 * pad) * SCALE)
    px_h = round((427 + 2 * pad) * SCALE)
    canvas = ('<svg xmlns="http://www.w3.org/2000/svg" width="%d" height="%d" '
              'viewBox="0 0 %d %d"><rect width="%d" height="%d" fill="%s"/>'
              '<g transform="translate(%d,%d)">%s</g></svg>'
              % (px_w, px_h, 881 + 2 * pad, 427 + 2 * pad, px_w, px_h, PAPER,
                 pad, pad - WU_TOP, body))
    open("/tmp/_oa_meas.svg", "w", encoding="utf-8").write(canvas)
    subprocess.run(["rsvg-convert", "-w", str(px_w), "-o", "/tmp/_oa.png",
                    "/tmp/_oa_meas.svg"], check=True)
    # render row 0 sits at viewBox y=0, which is native WU y = WU_TOP - pad
    ref = WU_TOP - pad
    wm = measure_vertical(ref, ref)
    tr1 = measure_tr1(ref)

    report["wordmark"] = wm
    report["wordmark_tr1"] = tr1
    # Seal-aligned optical reference: the seal is flat-sided, so the eye judges
    # it against the dominant cap-to-baseline band, NOT against the full ink box
    # (which includes the EN line's descender space) nor against the raw topmost
    # pixel (which is a 1 px apex sliver on the A).
    cap = tr1.get("cap_line_y")
    baseline = tr1.get("band_bottom_y")
    if cap is not None and baseline is not None:
        optical = (cap + baseline) / 2.0
        report["optical_reference"] = {
            "cap_line_y": round(cap, 2),
            "tr1_baseline_y": round(baseline, 2),
            "cap_to_baseline_mid_y": round(optical, 2),
            "wordmark_bbox_centre_y": round(wm["bbox_centre"], 2),
            "bbox_minus_optical_px": round(wm["bbox_centre"] - optical, 2),
        }
    report["apostrophe_overshoot_px"] = (
        None if (cap is None or tr1.get("apostrophe_top_y") is None)
        else round(cap - tr1["apostrophe_top_y"], 2))

    # ---- four controlled offsets -------------------------------------------
    # The canvas height is FIXED across all four variants. Letting it follow the
    # offset changes the render scale, so the same native pixel measured at -4
    # and at +8 lands on a different number of device rows and the whole
    # comparison drifts.
    fixed_h = int(round(PAD + seal_h + PAD + max(0.0, -min(OFFSETS))))
    for off in OFFSETS:
        svg, info = build_horizontal(off, seal_h, text_top, text_bottom)
        w = int(re.search(r'width="(\d+)"', svg).group(1))
        svg = svg.replace('height="%d" viewBox="0 0 %d %d"' % (h0 := int(re.search(r'height="(\d+)"', svg).group(1)), w, h0),
                          'height="%d" viewBox="0 0 %d %d"' % (fixed_h, w, fixed_h))
        h = fixed_h
        px_w, px_h = int(round(w * SCALE)), int(round(h * SCALE))
        svg2 = svg.replace('width="%d" height="%d" viewBox="0 0 %d %d"'
                           % (w, h, w, h),
                           'width="%d" height="%d" viewBox="0 0 %d %d"'
                           % (px_w, px_h, w, h))
        name = "h-offset%+.0f" % off
        open(os.path.join(OUT, name + ".svg"), "w", encoding="utf-8").write(svg2)
        subprocess.run(["rsvg-convert", "-w", str(px_w), "-o",
                        os.path.join(OUT, name + ".png"),
                        os.path.join(OUT, name + ".svg")], check=True)
        a = ink_mask(Image.open(os.path.join(OUT, name + ".png")))
        rows = np.where(a.any(1))[0]
        top = rows.min() / SCALE
        bottom = rows.max() / SCALE
        mass = a.sum()
        ys = np.arange(a.shape[0])[:, None]
        centroid = float((ys * a).sum() / mass) / SCALE
        report["variants"].append({
            "name": name, "offset_px": off,
            "svg": "%s.svg" % name, "png": "%s.png" % name,
            "lockup_ink_top_px": round(top, 2),
            "lockup_ink_bottom_px": round(bottom, 2),
            "lockup_ink_centre_px": round((top + bottom) / 2.0, 2),
            "lockup_ink_centroid_px": round(centroid, 2),
        })
        print("%-12s offset %+5.1f  ink %7.2f..%7.2f  centre %7.2f  centroid %7.2f"
              % (name, off, top, bottom, (top + bottom) / 2.0, centroid))

    # ---- stacked optical centring (independent) -----------------------------
    st = os.path.join(LOCK, "WU-stacked.svg")
    if os.path.exists(st):
        s = open(st, encoding="utf-8").read()
        m = re.search(r'width="(\d+)"\s+height="(\d+)"', s)
        px_w, px_h = int(m.group(1)), int(m.group(2))
        open("/tmp/_oa_st.svg", "w", encoding="utf-8").write(s)
        subprocess.run(["rsvg-convert", "-w", str(px_w), "-o", "/tmp/_oa.png",
                        "/tmp/_oa_st.svg"], check=True)
        a = ink_mask(Image.open("/tmp/_oa.png"))
        k = px_w / float(re.search(r'viewBox="0 0 ([\d.]+) ([\d.]+)', s).group(1))
        cols = np.where(a.any(0))[0]
        rows = np.where(a.any(1))[0]
        report["stacked"] = {
            "px_per_native_unit": round(k, 4),
            "ink_left_px": round(cols.min() / k, 2),
            "ink_right_px": round(cols.max() / k, 2),
            "ink_centre_px": round(((cols.min() + cols.max()) / 2.0) / k, 2),
            "canvas_centre_px": round((cols.min() + cols.max()) / 2.0 / k, 2),
            "ink_top_px": round(rows.min() / k, 2),
            "ink_bottom_px": round(rows.max() / k, 2),
        }

    json.dump(report, open(os.path.join(AUDIT, "optical-alignment.json"), "w"),
              indent=2)
    print("\nwordmark ink %s" % json.dumps({k: (round(v, 2) if isinstance(v, float) else v)
                                           for k, v in wm.items()}))
    print("TR1 %s" % json.dumps(tr1))
    print("apostrophe overshoot: %s px" % report["apostrophe_overshoot_px"])
    return 0


if __name__ == "__main__":
    sys.exit(main())