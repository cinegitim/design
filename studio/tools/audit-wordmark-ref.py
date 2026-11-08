#!/usr/bin/env python
"""Deterministic audit of the approved Asya'da Eğitim typography reference.

Measures the reference from pixels and reports every quantity the wordmark
reconstruction needs: line bands, cap heights, baselines, justified measures,
per-glyph boxes, diacritic geometry (Ğ breve, İ dot) and the red apostrophe.

No image generation. No font guesses. Every number below is measured.
"""
import json
import os

import numpy as np
from PIL import Image

ROOT = "/Users/serdaryurt/Documents/OpenCode/Design"
SRC = os.path.join(ROOT, "brands/asyada-egitim/explorations/wordmark-ref/reference.jpg")


def classify(a):
    """paper / ink / red masks, tolerant of JPEG ringing."""
    r, g, b = a[..., 0], a[..., 1], a[..., 2]
    mx = a.max(2)
    mn = a.min(2)
    ink = mx < 170                      # dark ink
    red = (r > 150) & (r - g > 55) & (r - b > 45)
    ink = ink & ~red
    return ink, red


def runs_1d(mask):
    """True-runs -> [(start, end_inclusive)]"""
    out = []
    s = None
    for i, v in enumerate(mask):
        if v and s is None:
            s = i
        elif not v and s is not None:
            out.append((s, i - 1))
            s = None
    if s is not None:
        out.append((s, len(mask) - 1))
    return out


def merge(runs, gap):
    out = []
    for r in runs:
        if out and r[0] - out[-1][1] - 1 <= gap:
            out[-1] = (out[-1][0], r[1])
        else:
            out.append(r)
    return out


def audit():
    im = Image.open(SRC).convert("RGB")
    a = np.asarray(im).astype(int)
    H, W, _ = a.shape
    ink, red = classify(a)
    any_ink = ink | red

    report = {"image": {"w": W, "h": H}}

    # ---------- line bands ----------
    # Raw bands first. Turkish diacritics (Ğ breve, İ dots) float ABOVE the cap
    # line as their own thin band, so a naive merge splits one text line in two.
    # A band whose x-extent spans most of the image is a real line; a narrower
    # band is a diacritic fragment and belongs to the next wide band below it.
    rowcov = any_ink.sum(1)
    raw = merge([r for r in runs_1d(rowcov > 0)], 2)
    wide = W * 0.55
    lines, pending = [], []
    for (y0, y1) in raw:
        colcov = any_ink[y0:y1 + 1].sum(0)
        cr = merge([r for r in runs_1d(colcov > 0)], 0)
        x0, x1 = cr[0][0], cr[-1][1]
        if (x1 - x0 + 1) >= wide:
            # close any fragments collected above into this line
            for (py0, py1, px0, px1) in pending:
                y0 = min(y0, py0)
            pending = []
            lines.append({"y0": y0, "y1": y1, "x0": x0, "x1": x1})
        else:
            pending.append((y0, y1, x0, x1))
    if pending:                       # trailing fragments fold into last line
        for (py0, py1, _, _) in pending:
            lines[-1]["y0"] = min(lines[-1]["y0"], py0)

    report["raw_bands"] = [{"y0": b[0], "y1": b[1], "h": b[1] - b[0] + 1} for b in raw]
    report["bands"] = [{"y0": l["y0"], "y1": l["y1"], "h": l["y1"] - l["y0"] + 1} for l in lines]

    # per-glyph column runs, and the cap line (top of the glyph BODY, i.e. the
    # row where the profile jumps from the diacritics down to the caps)
    for i, l in enumerate(lines):
        colcov = any_ink[l["y0"]:l["y1"] + 1].sum(0)
        l["glyph_cols"] = merge([r for r in runs_1d(colcov > 0)], 0)
        # cap line = first row from the bottom whose coverage >= 60% of the
        # glyph's own full coverage (excludes the isolated diacritic rows)
        rc = any_ink[l["y0"]:l["y1"] + 1].sum(1)
        full = rc.max()
        cap_y = l["y1"]
        for yy in range(len(rc)):
            if rc[yy] >= 0.60 * full:
                cap_y = l["y0"] + yy
                break
        l["cap_top"] = cap_y
        l["cap_h"] = l["y1"] - cap_y + 1
        l["diacritic_h"] = cap_y - l["y0"]
        l["x0"] = l["glyph_cols"][0][0]
        l["x1"] = l["glyph_cols"][-1][1]
        l["w"] = l["x1"] - l["x0"] + 1
    report["lines"] = [{k: v for k, v in l.items() if k != "glyph_cols"} for l in lines]

    if len(lines) < 3:
        report["error"] = "found %d line(s), need 3" % len(lines)
        out = os.path.join(ROOT, "brands/asyada-egitim/explorations/wordmark-ref/audit")
        os.makedirs(out, exist_ok=True)
        json.dump(report, open(os.path.join(out, "reference-audit.json"), "w"), indent=1)
        return report

    tr1, tr2, en = lines[0], lines[1], lines[2]

    def glyphs(l, min_px=6):
        out = []
        for (c0, c1) in l["glyph_cols"]:
            if c1 - c0 + 1 < min_px:
                continue
            strip = any_ink[l["y0"]:l["y1"] + 1, c0:c1 + 1]
            rr = merge([r for r in runs_1d(strip.sum(1) > 0)], 3)
            out.append({"x0": c0, "x1": c1, "w": c1 - c0 + 1,
                        "y0": l["y0"] + rr[0][0], "y1": l["y0"] + rr[-1][1],
                        "h": rr[-1][1] - rr[0][0] + 1})
        return out

    import cv2

    def glyphs_on(l, mask, min_px=6):
        """Connected components, not column runs.

        Column runs silently merge letters that touch or overlap (Y+A in ASYA
        merge into one 255 px run), which corrupts every per-glyph number.
        8-connectivity also keeps the İ dot and the Ğ breve attached to their
        own letter instead of floating as separate components.
        """
        sub = (mask[l["y0"]:l["y1"] + 1] * 255).astype(np.uint8)
        n, lab, stats, _ = cv2.connectedComponentsWithStats(sub, connectivity=8)
        out = []
        for i in range(1, n):
            x, y, w, h, area = stats[i]
            if w < min_px or h < 3:
                continue
            out.append({"x0": int(l["y0"] * 0 + x + l["y0"] * 0), "x1": int(x + w - 1 + l["x0"] * 0),
                        "w": int(w), "y0": int(y + l["y0"]), "y1": int(y + h - 1 + l["y0"]),
                        "h": int(h), "area": int(area)})
        out.sort(key=lambda g_: g_["x0"])
        return out

    report["tr1_glyphs"] = glyphs_on(tr1, ink)
    report["tr2_glyphs"] = glyphs_on(tr2, ink)
    report["en_glyphs"] = glyphs_on(en, ink, min_px=3)
    # red apostrophe as its own component, measured separately
    report["apostrophe_cc"] = glyphs_on(tr1, red, min_px=4)

    # ---- cap height: the baseline is solid, so take it as the line bottom.
    # Cap height comes from glyph components whose TOP equals the modal glyph
    # top (i.e. plain caps, not letters carrying a breve/dot above the line).
    def cap_from(gs):
        if not gs:
            return 0
        tops = sorted({g_["y0"] for g_ in gs})
        from collections import Counter
        base_top = Counter(g_["y0"] for g_ in gs).most_common(1)[0][0]
        plain = [g_ for g_ in gs if g_["y0"] == base_top]
        base_bot = max(g_["y1"] for g_ in plain)
        return base_bot - base_top + 1

    for l, k in ((tr1, "tr1"), (tr2, "tr2"), (en, "en")):
        l["cap_h_true"] = cap_from(report[k + "_glyphs"])
        l["cap_top_true"] = min(g_["y0"] for g_ in report[k + "_glyphs"]
                                if g_["y0"] <= max(x["y0"] for x in report[k + "_glyphs"]) + 3)

    # ---------- diacritic geometry ----------
    # Isolated components whose top sits above the modal cap top: the Ğ breve
    # and the two İ dots. Measured by re-segmenting the band ABOVE the cap line
    # alone, so a breve that slightly overlaps its letter is not missed.
    for l, key in ((tr2, "tr2"),):
        gs = report[key + "_glyphs"]
        # cap top = the LOWEST glyph top that still belongs to a plain cap. The
        # breve/dot components sit higher, so the modal top of the tallest
        # components is the cap line.
        from collections import Counter
        tall = [g_ for g_ in gs if g_["h"] > l["cap_h_true"] * 0.6]
        base_top = Counter(g_["y0"] for g_ in tall).most_common(1)[0][0]
        band_top = l["y0"]
        depth = base_top - band_top
        if depth <= 0:
            report[key + "_diacritics"] = []
            report[key + "_cap_top_used"] = int(base_top)
            continue
        above = (ink[band_top:base_top, :] * 255).astype(np.uint8)
        n, lab, stats, _ = cv2.connectedComponentsWithStats(above, connectivity=8)
        di = []
        for i in range(1, n):
            x, y, w, h, area = stats[i]
            if w < 4 or h < 3 or area < 20:
                continue
            # which letter does it belong to: nearest component at/below cap
            di.append({"x0": int(x), "x1": int(x + w - 1), "w": int(w),
                       "y0": int(y + l["y0"]), "h": int(h),
                       "bottom": int(y + h - 1 + l["y0"]),
                       "rises_above_cap": int(base_top - (y + l["y0"])),
                       "clearance_to_cap": int(base_top - (y + h - 1 + l["y0"])),
                       "w_over_cap": round(w / float(l["cap_h_true"]), 4)})
        di.sort(key=lambda z: z["x0"])
        report[key + "_diacritics"] = di
        report[key + "_cap_top_used"] = int(base_top)

    # ---------- apostrophe (red only) ----------
    ys, xs = np.where(red)
    if len(xs):
        sel = ys <= tr1["y1"]
        ap = {"x0": int(xs[sel].min()), "x1": int(xs[sel].max()),
              "w": int(xs[sel].max() - xs[sel].min() + 1),
              "y0": int(ys[sel].min()), "y1": int(ys[sel].max()),
              "h": int(ys[sel].max() - ys[sel].min() + 1)}
        ap["centre_x"] = (ap["x0"] + ap["x1"]) / 2
        ap["rises_above_cap"] = tr1["cap_top"] - ap["y0"]
        ap["above_baseline"] = tr1["y1"] - ap["y1"]
        # locate it between which two ink glyphs
        left = [g_ for g_ in report["tr1_glyphs"] if g_["x1"] < ap["x0"]]
        ap["after_glyph_index"] = len(left)
        ap["gap_to_prev_glyph"] = ap["x0"] - left[-1]["x1"] if left else None
        report["apostrophe"] = ap

    # ---------- English tracking ----------
    ec = report["en_glyphs"]
    widths = [x["w"] for x in ec if x["w"] > 2]
    advs, gaps = [], []
    for i in range(1, len(ec)):
        d = ec[i]["x0"] - ec[i - 1]["x0"]
        g_ = ec[i]["x0"] - ec[i - 1]["x1"] - 1
        gaps.append(g_)
        if d < 60:
            advs.append(d)
    advs = [a for a in advs if a > 0]
    gaps = [g_ for g_ in gaps if g_ >= 0]
    if advs and widths:
        ma = float(np.median(advs))
        mw = float(np.mean([ec[i]["w"] for i in range(1, len(ec))
                            if ec[i]["x0"] - ec[i - 1]["x0"] < 60]))
        report["en_tracking_est"] = {
            "median_advance": round(ma, 2), "mean_glyph_width": round(mw, 2),
            "tracking_ratio_adv_over_width": round(ma / mw, 4),
            "letter_gap_min": int(min(gaps)), "letter_gap_max": int(max(gaps)),
            "n_glyphs": len(ec)}

    # ---------- geometry ----------
    cap1 = int(tr1["cap_h_true"])
    cap2 = int(tr2["cap_h_true"])
    capen = int(en["cap_h_true"])
    report["geometry"] = {
        "cap_tr1": cap1, "cap_tr2": cap2, "cap_en": capen,
        "tr1_cap_top": int(tr1["cap_top"]), "tr1_baseline": int(tr1["y1"]),
        "tr2_cap_top": int(tr2["cap_top"]), "tr2_baseline": int(tr2["y1"]),
        "en_cap_top": int(en["cap_top"]), "en_baseline": int(en["y1"]),
        "tr_baseline_delta": int(tr2["y1"] - tr1["y1"]),
        "tr2_baseline_to_en": int(en["y1"] - tr2["y1"]),
        "tr1_leading_ratio": round((tr2["y1"] - tr1["y1"]) / cap1, 4),
        "en_drop_ratio": round((en["y1"] - tr2["y1"]) / cap1, 4),
        "en_cap_ratio": round(capen / cap1, 4),
        "tr2_cap_ratio": round(cap2 / cap1, 4),
        "measure_tr1": int(tr1["w"]), "measure_tr2": int(tr2["w"]),
        "measure_en": int(en["w"]),
        "tr1_x0": int(tr1["x0"]), "tr1_x1": int(tr1["x1"]),
        "tr2_x0": int(tr2["x0"]), "tr2_x1": int(tr2["x1"]),
        "en_x0": int(en["x0"]), "en_x1": int(en["x1"]),
        "measure_spread_tr": int(abs(tr1["w"] - tr2["w"])),
        "measure_en_minus_tr1": int(en["w"] - tr1["w"]),
    }

    out = os.path.join(ROOT, "brands/asyada-egitim/explorations/wordmark-ref/audit")
    os.makedirs(out, exist_ok=True)
    json.dump(report, open(os.path.join(out, "reference-audit.json"), "w"), indent=1)
    return report


def show(r):
    g = r["geometry"]
    print("=" * 74)
    print("REFERENCE AUDIT  %d x %d px" % (r["image"]["w"], r["image"]["h"]))
    print("=" * 74)
    print("\nRAW ROW BANDS (diacritics split off)")
    for b in r["raw_bands"]:
        print("   y %3d-%3d   h %3d" % (b["y0"], b["y1"], b["h"]))
    if "geometry" not in r:
        print("!! %s" % r.get("error"))
    g = r["geometry"]
    print("\nLINES RESOLVED")
    for k, lab in (("tr1", "TR1 ASYA'DA"), ("tr2", "TR2 EGITIM"), ("en", "EN EDUCATION...")):
        L = next(l for l in r["lines"] if l is not None) if False else None
    for i, l in enumerate(r["lines"]):
        print("   [%d] cap top %3d  baseline %3d  cap %3d  diacritic band %3d  x %3d-%3d  w %4d"
              % (i, l["cap_top"], l["y1"], l["cap_h"], l["diacritic_h"], l["x0"], l["x1"], l["w"]))
    print("\nCAP HEIGHTS")
    print("   TR line 1 cap   %3d px" % g["cap_tr1"])
    print("   TR line 2 cap   %3d px" % g["cap_tr2"])
    print("   EN line cap     %3d px" % g["cap_en"])
    print("\nMEASURES  (the justified block)")
    print("   ASYA'DA     x %3d-%3d   w %4d px" % (g["tr1_x0"], g["tr1_x1"], g["measure_tr1"]))
    print("   EGITIM      x %3d-%3d   w %4d px" % (g["tr2_x0"], g["tr2_x1"], g["measure_tr2"]))
    print("   EDUCATION..  x %3d-%3d   w %4d px" % (g["en_x0"], g["en_x1"], g["measure_en"]))
    print("   -> TR spread %d px | EN vs TR1 %+d px" % (g["measure_spread_tr"], g["measure_en_minus_tr1"]))
    print("\nVERTICAL")
    print("   TR1 baseline %3d | TR2 baseline %3d | delta %3d px = %.4f cap"
          % (g["tr1_baseline"], g["tr2_baseline"], g["tr_baseline_delta"], g["tr_baseline_delta"] / g["cap_tr1"]))
    print("   EN  baseline %3d | TR2->EN %3d px = %.4f cap"
          % (g["en_baseline"], g["tr2_baseline_to_en"], g["tr2_baseline_to_en"] / g["cap_tr1"]))
    print("   EN cap / TR cap  = %.4f" % g["en_cap_ratio"])
    print("   TR2 cap / TR1 cap = %.4f" % g["tr2_cap_ratio"])
    print("\nGLYPH BOXES - TR line 1")
    for i, x in enumerate(r["tr1_glyphs"]):
        print("   [%d] x %3d-%3d  w %3d  h %3d" % (i, x["x0"], x["x1"], x["w"], x["h"]))
    print("GLYPH BOXES - TR line 2")
    for i, x in enumerate(r["tr2_glyphs"]):
        print("   [%d] x %3d-%3d  w %3d  h %3d" % (i, x["x0"], x["x1"], x["w"], x["h"]))
    print("GLYPH BOXES - EN line (first 8)")
    for i, x in enumerate(r["en_glyphs"][:8]):
        print("   [%d] x %3d-%3d  w %3d  h %3d" % (i, x["x0"], x["x1"], x["w"], x["h"]))
    print("\nDIACRITICS ABOVE THE CAP LINE")
    for d in r.get("tr2_diacritics", []):
        kind = "breve (Ğ)" if d["h"] > 30 else "dot (İ)"
        print("   %-10s x %3d-%3d  w %3d  h %3d  rises %2d px above cap | %2d px clear of it | w/cap %.4f"
              % (kind, d["x0"], d["x1"], d["w"], d["h"],
                 d["rises_above_cap"], d["clearance_to_cap"], d["w_over_cap"]))
    ap = r["apostrophe"]
    print("\nENGLISH TRACKING")
    t = r["en_tracking_est"]
    print("   %d ink runs | median advance %.1f | mean glyph width %.1f | adv/width %.4f"
          % (t["n_glyphs"], t["median_advance"], t["mean_glyph_width"], t["tracking_ratio_adv_over_width"]))
    print("   inter-glyph gap min %d max %d" % (t["letter_gap_min"], t["letter_gap_max"]))

    print("\nPER-LETTER ADVANCES — EN line (tracking per 1000 em of cap)")
    capen_ = g["cap_en"]
    adv = []
    ec = r["en_glyphs"]
    for i in range(1, len(ec)):
        d = ec[i]["x0"] - ec[i - 1]["x0"]
        adv.append(int(round(d / capen_ * 1000)))
    print("   " + "  ".join(str(a) for a in adv))

    # NOTE: `"fmt" % a / b` parses as `("fmt" % a) / b` — % and / bind at the
    # same precedence, left to right — so the division must be parenthesised.
    print("\nSUMMARY — the numbers a reconstruction must hit")
    print("   TR cap                     %.1f px" % g["cap_tr1"])
    print("   TR leading  (TR1→TR2)      %.4f cap" % (g["tr_baseline_delta"] / g["cap_tr1"]))
    print("   EN cap / TR cap            %.4f" % g["en_cap_ratio"])
    print("   EN drop (TR2→EN baseline)  %.4f cap" % (g["tr2_baseline_to_en"] / g["cap_tr1"]))
    print("   TR1 measure                %.1f px" % g["measure_tr1"])
    print("   EN  measure                %.1f px  (%+.1f vs TR1)"
          % (g["measure_en"], g["measure_en_minus_tr1"]))
    print("   apostrophe w/cap           %.4f  h/cap %.4f"
          % (r["apostrophe"]["w"] / g["cap_tr1"], r["apostrophe"]["h"] / g["cap_tr1"]))


if __name__ == "__main__":
    show(audit())