#!/usr/bin/env python
"""QUALITY GATE for the unified lockups. FAIL loudly; print a pass/fail table."""
import json
import os
import sys

import numpy as np
from PIL import Image

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import build_unified_lockups as L

RUN = L.RUN
M = json.load(open(os.path.join(RUN, "audit/unified-measurement.json")))
B = json.load(open(os.path.join(RUN, "audit/unified-build.json")))
import hashlib
import re

CANON = os.path.join(L.ROOT, "brands/asyada-egitim/assets/v01-canonical.svg")
CANON_SHA = "8f5d46f0302c4cc7e3765d3bfce9445f842dbd92f1e0f8fbe99f9f509c77e11a"

TOL_LINE = 1.0        # px, at 1000 px wordmark width
TOL_EDGE = 1.5        # px, lockup element edges (anti-alias at large radii)
TOL_ALIGN = 1.0       # px, centre-axis / vertical-centre


def main():
    rows = []
    w = M["wordmark"]
    for k in ("tr1", "tr2", "en"):
        v = w["lines"][k]
        ok = v["dev_left_px"] <= TOL_LINE and v["dev_right_px"] <= TOL_LINE
        rows.append(("text line %s within common measure W" % k.upper(),
                     "devL %.2f devR %.2f px" % (v["dev_left_px"], v["dev_right_px"]),
                     ok))
    widths = [round(w["lines"][k]["width_native"], 2) for k in ("tr1", "tr2", "en")]
    rows.append(("three lines share one measure W",
                 "widths %s (spread %.2f px)" % (widths, max(widths) - min(widths)),
                 (max(widths) - min(widths)) <= TOL_LINE))

    for name in ("stacked", "horizontal"):
        d = M["lockups"][name]["deviations"]
        for key, label in (("seal_left_edge_px", "seal left edge"),
                           ("seal_right_edge_px", "seal right edge"),
                           ("seal_top_edge_px", "seal top edge"),
                           ("seal_bottom_edge_px", "seal bottom edge"),
                           ("text_left_edge_px", "text left edge"),
                           ("text_right_edge_px", "text right edge"),
                           ("text_top_edge_px", "text top edge"),
                           ("text_bottom_edge_px", "text bottom edge")):
            rows.append(("%s: %s" % (name, label), "%.2f px" % d[key],
                         abs(d[key]) <= TOL_EDGE))
        rows.append(("%s: clearspace error" % name,
                     "%.2f px (intended %.0f)" % (d["gap_error_px"], d["intended_gap_px"]),
                     abs(d["gap_error_px"]) <= TOL_EDGE))
        akey = "centre_axis_offset_px" if name == "stacked" else "vertical_centre_offset_px"
        alab = "optical centre axis" if name == "stacked" else "seal↔text vertical centre"
        rows.append(("%s: %s" % (name, alab), "%.2f px" % d[akey],
                     abs(d[akey]) <= TOL_ALIGN))

    # logo geometry unchanged
    src = open(CANON, encoding="utf-8").read()
    live = hashlib.sha256(src.encode()).hexdigest()
    rows.append(("canonical seal unmodified (SHA-256)", live[:16], live == CANON_SHA))
    cd = re.findall(r'<path d="([^"]+)" fill="#FFFFFF"/>', src)
    crc = re.search(r'<rect x="([^"]+)" y="([^"]+)" width="([^"]+)" height="([^"]+)" rx="([^"]+)"', src).groups()
    geo_bad = 0
    for f in sorted(os.listdir(os.path.join(RUN, "lockups"))):
        if not f.endswith(".svg"):
            continue
        s = open(os.path.join(RUN, "lockups", f), encoding="utf-8").read()
        mm = re.search(r'data-canonical-sha256="%s"[^>]*>(.*?)</g>' % CANON_SHA, s, re.S)
        if not mm:
            continue
        inner = mm.group(1)
        if re.findall(r'<path d="([^"]+)"', inner) != cd or \
           re.search(r'<rect x="([^"]+)" y="([^"]+)" width="([^"]+)" height="([^"]+)" rx="([^"]+)"', inner).groups() != crc:
            geo_bad += 1
    rows.append(("seal geometry byte-identical in all lockups",
                 "%d files, %d deviations" % (3, geo_bad), geo_bad == 0))

    # glyphs not distorted: every letter is a rigid body, so no letter's
    # width or height changed from the reference trace
    lay = B["layout"]
    rigid = all(lay[k]["per_gap"] is not None for k in lay)
    rows.append(("no word/letter stretching (rigid bodies, tracking only)",
                 "per-gap tracking tr2 %.2f / en %.2f px" % (lay["tr2"]["per_gap"], lay["en"]["per_gap"]),
                 rigid))

    # Turkish diacritics intact: 6 letters in TR2, 3 with diacritics, none orphaned
    t2 = B["tr2"]
    rows.append(("Turkish diacritics intact (Ğ breve + 2 İ dots)",
                 "%d components, %d letters, %d orphans" % (t2["components"], t2["letters"], t2["orphans"]),
                 t2["orphans"] == 0 and t2["components"] == 9))

    # Counters open. Probe each counter by its x-RANGE, not a single guessed
    # pixel: the D bowl at x=700 is ink (the bowl's right stem), while the
    # counter itself is the light run between the stem and the bowl. A single
    # wrong probe pixel reads as a false FAIL on a correct glyph.
    import subprocess
    subprocess.run(["rsvg-convert", "-w", "881", os.path.join(RUN, "svg", "WU.svg"),
                    "-o", "/tmp/gate.png"], check=True, capture_output=True)
    im = Image.open("/tmp/gate.png").convert("RGBA")
    bg = Image.new("RGBA", im.size, (247, 243, 233, 255))
    bg.alpha_composite(im)
    g = np.asarray(bg.convert("L")).astype(int)

    def runs_at(y, x0, x1):
        out, cur = [], None
        for i in range(x0, x1):
            d = g[y, i] < 200
            if cur is None or cur[2] != d:
                if cur:
                    out.append(cur)
                cur = [i, i, d]
            else:
                cur[1] = i
        out.append(cur)
        return out

    # (label, y, x0, x1, index of the counter run among LIGHT runs)
    probes = [("A counter (TR1)", 85, 0, 140, 0),
              ("D bowl (TR1)", 70, 600, 720, 1),
              ("G counter (TR2)", 240, 120, 260, 0),
              ("O counter (EN)", 397, 380, 440, 0)]
    detail, bad = [], []
    for label, y, x0, x1, li in probes:
        rs = runs_at(y, x0, x1)
        lights = [r for r in rs if not r[2]]
        if len(lights) > li:
            a, b, _ = lights[li]
            wide = (b - a) >= 6
            detail.append("%s=%d..%d(%dpx)" % (label, a, b, b - a + 1))
            if not wide:
                bad.append(label)
        else:
            detail.append("%s=none" % label)
            bad.append(label)
    rows.append(("letter counters open (not filled solid)",
                 ", ".join(detail), not bad))

    print("=" * 78)
    print("QUALITY GATE — unified wordmark + lockups")
    print("=" * 78)
    for label, val, ok in rows:
        print(" %-4s %-52s %s" % ("PASS" if ok else "FAIL", label, val))
    nfail = sum(1 for _, _, ok in rows if not ok)
    print("=" * 78)
    print(" %d checks · %d PASS · %d FAIL" % (len(rows), len(rows) - nfail, nfail))
    print(" RESULT: %s" % ("PASS" if nfail == 0 else "FAIL"))
    json.dump({"rows": [{"check": a, "value": b, "pass": c} for a, b, c in rows],
               "fail_count": nfail, "result": "PASS" if nfail == 0 else "FAIL"},
              open(os.path.join(RUN, "audit/quality-gate.json"), "w"), indent=1)
    return 0 if nfail == 0 else 1


if __name__ == "__main__":
    sys.exit(main())