#!/usr/bin/env python
"""Build the Asya'da Eğitim lockup family — 5 structural variants, ONE type direction.

Type direction (given, not chosen here): neo-grotesque uppercase sans, bold
Turkish line + wide-tracked light English line, bilingual, full Turkish support.
Reference behaviour reproduced: every type line justified to ONE common measure,
each line finding its own tracking for that measure, so "ASYA'DA" sets tight and
"EĞİTİM" sets open to the same width, and the English line tracks wide to close.

Scale derivation: the Turkish cap height is SOLVED from the measure (never
guessed), so a variant is defined by its measure + seal relationship + ratios,
and every dimension downstream falls out of the type.

The seal is embedded VERBATIM from the locked canonical asset; only <g>
placement transforms are applied. Mono versions recolour fills only.
"""
import hashlib
import json
import os
import re
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from typeset import (runs_to_path, measure, fit_tracking, solve_cap,
                     cap_height, glyph_test)

ROOT = "/Users/serdaryurt/Documents/OpenCode/Design"
CANON = os.path.join(ROOT, "brands/asyada-egitim/assets/v01-canonical.svg")
CANON_SHA = "8f5d46f0302c4cc7e3765d3bfce9445f842dbd92f1e0f8fbe99f9f509c77e11a"

PAPER = "#F7F3E9"
INK = "#141210"
VERM = "#BD2120"

TR1 = "ASYA’DA"
TR2 = "EĞİTİM"
TRS = "ASYA’DA EĞİTİM"
EN = "EDUCATION IN ASIA"

# ---- ONE type scale shared by every variant ------------------------------
LEAD_TR = 1.46     # baseline -> baseline across the two Turkish lines
DROP_EN = 0.70     # Turkish baseline -> English baseline
TR_TRACK = 6       # design tracking for the Turkish line (tight, modern)


def seal_geometry():
    src = open(CANON, encoding="utf-8").read()
    assert hashlib.sha256(src.encode()).hexdigest() == CANON_SHA, "canonical seal changed"
    rect = re.search(r'<rect [^>]*/>', src).group(0)
    paths = re.findall(r'<path d="[^"]+" fill="#FFFFFF"/>', src)
    assert len(paths) == 2
    return rect, paths


def seal_group(x, y, scale, mono=None):
    """Canonical seal at (x,y) scaled. Geometry never altered.

    mono='paper' is the approved mono-paper colour variant: cream field, ink
    mark. It rewrites fill attributes only — d, x, y, width, height and rx of
    the canonical geometry are byte-identical to the locked file.
    """
    rect, paths = seal_geometry()
    if mono == "paper":
        rect = rect.replace('fill="#BD2120"', 'fill="%s"' % PAPER)
        paths = [p.replace('fill="#FFFFFF"', 'fill="%s"' % INK) for p in paths]
    g = ('<g transform="translate(%.3f,%.3f) scale(%.6f)" data-canonical-sha256="%s"%s>'
         % (x, y, scale, CANON_SHA, (' data-colour-variant="mono-paper"' if mono else "")))
    return g + rect + "".join(paths) + "</g>"


def draw_line(runs, weight, cap, track, x, baseline):
    return runs_to_path(runs, weight, x, baseline, cap, track)[0]


def line_width(runs, weight, cap, track):
    return measure("".join(t for t, _ in runs), weight, cap, track)


def build(v, mono=False):
    s = v["spec"]
    align = s["align"]
    cap = s["tr_cap"]                      # the design decision: Turkish cap height

    # Type colour. The seal's own fills are set INSIDE seal_group() from the
    # canonical file and are never touched here — only the type is recoloured.
    T_INK = PAPER if mono else INK
    T_VERM = PAPER if mono else VERM
    seal_mono = "paper" if mono else None

    # --- the measure is DERIVED: line 1 sets it at the design tracking ----
    if s["tr_lines"] == 2:
        tr_runs = [[("ASYA", T_INK), ("’", T_VERM), ("DA", T_INK)], [(TR2, T_INK)]]
    else:
        tr_runs = [[("ASYA", T_INK), ("’", T_VERM), ("DA EĞİTİM", T_INK)]]
    base_txt = "".join(t for t, _ in tr_runs[0])
    measure_w = measure(base_txt, "bold", cap, TR_TRACK)

    en_cap = cap * s["en_ratio"]
    tracks = [TR_TRACK] + [fit_tracking("".join(t for t, _ in r), "bold", measure_w,
                                         cap, -30, 900) for r in tr_runs[1:]]
    en_track = fit_tracking(EN, s["en_weight"], measure_w, en_cap, -20, 1200)

    b1 = cap                                   # Turkish line 1 baseline
    b2 = b1 + LEAD_TR * cap                    # Turkish line 2 baseline
    b3 = b2 + DROP_EN * cap                    # English baseline

    def place(runs, wt, c, tr, base):
        wd = line_width(runs, wt, c, tr)
        x = (measure_w - wd) / 2 if align == "center" else (measure_w - wd if align == "right" else 0)
        return draw_line(runs, wt, c, tr, x, base)

    type_parts = []
    for i, (r, tr) in enumerate(zip(tr_runs, tracks)):
        type_parts.append(place(r, "bold", cap, tr, b1 + i * LEAD_TR * cap))
    en_runs = [(EN, T_INK)]
    if "rule" in s:
        ry = b3 - s["rule_gap"] * cap
        type_parts.append('<rect x="0" y="%.3f" width="%.3f" height="%.3f" fill="%s"/>'
                          % (ry, measure_w, cap * 0.030, T_VERM))
    en_base = b3
    if s.get("en_drop"):
        en_base = b2 + s["en_drop"] * cap
    if s.get("en", True):
        type_parts.append(place(en_runs, s["en_weight"], en_cap, en_track, en_base))
    else:
        # small-use lockup: the English line is dropped. Measured reason —
        # at a 13-character Turkish measure the 17-character English line needs
        # >900/1000 em tracking to justify, or an optical size of 0.48 cap that
        # destroys the TR/EN hierarchy. At small sizes it is a liability, not a
        # line. Documented rule: bilingual lockups take over at >=200px.
        en_base = b2 + cap * 0.0
        en_base = b1 + LEAD_TR * cap * (len(tr_runs) - 1) if len(tr_runs) > 1 else b1
    type_svg = "".join(type_parts)

    # --- place the seal ---------------------------------------------------
    type_top = b1 - cap
    block_h = en_base - type_top
    gap = s["seal_gap"] * cap

    if s["arrange"] == "stacked":
        seal_w = measure_w * s["seal_w_frac"]
        seal_h = seal_w * 370.0 / 400.0
        seal_x = (measure_w - seal_w) / 2
        # the type block's own origin is its cap-top; shift it down past the seal
        offset = gap + seal_h
        inner = (seal_group(seal_x, 0, seal_w / 400.0, seal_mono)
                 + '<g transform="translate(0,%.3f)">%s</g>' % (offset, type_svg))
        content_h = offset + en_base
        content_w = measure_w
        body = inner
    else:
        seal_h = block_h * s.get("seal_h_frac", 1.0)
        seal_w = seal_h * 400.0 / 370.0
        seal_y = (block_h - seal_h) / 2           # optically centred
        content_h = block_h
        content_w = seal_w + gap + measure_w
        body = (seal_group(0, seal_y, seal_w / 400.0, seal_mono)
                + '<g transform="translate(%.3f,0)">%s</g>' % (seal_w + gap, type_svg))

    pad = cap * s.get("pad", 0.30)
    body = '<g transform="translate(%.3f,%.3f)">%s</g>' % (pad, pad, body)
    W = content_w + pad * 2
    H = content_h + pad * 2

    svg = ('<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 %.2f %.2f" width="%.2f" '
           'height="%.2f" role="img" aria-label="%s">\n<title>%s</title>\n%s\n</svg>\n'
           % (W, H, W, H, v["aria"], v["title"], body))

    meta = dict(
        id=v["id"], name=v["name"], width=round(W, 2), height=round(H, 2),
        aspect=round(W / H, 3), align=align, arrangement=s["arrange"],
        tr_lines=s["tr_lines"], measure=round(measure_w, 2),
        tr_cap=round(cap, 2), tr_cap_to_measure=round(cap / measure_w, 4),
        en_cap=round(en_cap, 2), en_ratio=s["en_ratio"], en_weight=s["en_weight"],
        tr_tracking=tracks, en_tracking=en_track,
        seal_w=round(seal_w, 2), seal_ratio_to_cap=round(seal_w / cap, 3),
        seal_gap_ratio=round(s["seal_gap"], 3),
        seal_to_tr_cap=round(seal_w / cap, 2),
        min_width_px=v["min_width"], min_height_px=round(v["min_width"] / (W / H), 1),
        canonical_logo_sha256=CANON_SHA)
    return svg, meta


VARIANTS = [
    # 1 — PRIMARY STACKED. Seal centred above, type block below. The type block
    # is deliberately WIDER than the seal, so the words lead and the mark supports.
    dict(id="P-01", name="Primary stacked",
         title="ASYA’DA EĞİTİM — Education in Asia (primary stacked)",
         aria="Asya'da Eğitim — Education in Asia — primary stacked lockup",
         min_width=170,
         spec=dict(arrange="stacked", tr_cap=72, align="center", tr_lines=2,
                   en_ratio=0.28, en_weight="light", seal_w_frac=0.54,
                   seal_gap=0.62, pad=0.30)),
    # 2 — PRIMARY HORIZONTAL. Seal height == type block height (the join), left aligned.
    dict(id="H-02", name="Primary horizontal",
         title="ASYA’DA EĞİTİM — Education in Asia (primary horizontal)",
         aria="Asya'da Eğitim — Education in Asia — primary horizontal lockup",
         min_width=250,
         spec=dict(arrange="horizontal", tr_cap=82, align="left", tr_lines=2,
                   en_ratio=0.28, en_weight="light", seal_h_frac=1.0,
                   seal_gap=0.80, pad=0.30)),
    # 3 — COMPACT. Same two-line Turkish signature, but the seal steps back to
    # 55% of the block height and every gap tightens: type-forward density.
    dict(id="C-03", name="Compact",
         title="ASYA’DA EĞİTİM — Education in Asia (compact)",
         aria="Asya'da Eğitim — Education in Asia — compact lockup",
         min_width=165,
         spec=dict(arrange="horizontal", tr_cap=88, align="left", tr_lines=2,
                   en_ratio=0.30, en_weight="light", seal_h_frac=0.55,
                   seal_gap=0.52, pad=0.24)),
    # 4 — SMALL USE / DIGITAL. One Turkish line instead of two, and NO English
    # line. Measured, not guessed: a 13-character Turkish measure needs >900/1000
    # em of tracking for the 17-character English line to justify, or an optical
    # size of 0.48 cap — either way the bilingual relationship collapses and the
    # line turns to grey mush below 200px. Seal kept large; reads to ~110px.
    dict(id="D-04", name="Small-use / digital",
         title="ASYA’DA EĞİTİM (small use)",
         aria="Asya'da Eğitim — small use lockup",
         min_width=110,
         spec=dict(arrange="stacked", tr_cap=68, align="center", tr_lines=1,
                   en=False, en_ratio=0.33, en_weight="medium", seal_w_frac=0.62,
                   seal_gap=0.58, pad=0.26)),
    # 5 — FORMAL BILINGUAL. Largest English optical size (0.36 cap, so the least
    # extreme tracking), a vermilion hairline stating the language boundary,
    # widest leading, most generous clearspace.
    dict(id="F-05", name="Formal bilingual",
         title="ASYA’DA EĞİTİM — Education in Asia (formal bilingual)",
         aria="Asya'da Eğitim — Education in Asia — formal bilingual lockup",
         min_width=300,
         spec=dict(arrange="horizontal", tr_cap=86, align="left", tr_lines=2,
                   en_ratio=0.36, en_weight="light", seal_h_frac=1.0,
                   seal_gap=0.90, rule="hairline", rule_gap=0.62, pad=0.34)),
]

if __name__ == "__main__":
    OUT = os.path.join(ROOT, "docs/asyada-seal/lockups/assets/svg")
    os.makedirs(OUT, exist_ok=True)
    metas = []
    for v in VARIANTS:
        svg, meta = build(v)
        open(os.path.join(OUT, v["id"] + ".svg"), "w", encoding="utf-8").write(svg)
        # mono-paper variant, built through the same code path (NOT a text
        # substitution): seal_group() recolours the canonical fills from the
        # locked file, the type is emitted in paper. Geometry never re-derived.
        mono_svg, _ = build(v, mono=True)
        open(os.path.join(OUT, v["id"] + "-mono.svg"), "w", encoding="utf-8").write(mono_svg)
        metas.append(meta)
        print("%-6s %-22s %7.1fx%6.1f a=%5.2f  cap=%5.1f measure=%6.1f seal:cap=%5.2f  trk %-14s en %s %5.0f"
              % (meta["id"], meta["name"], meta["width"], meta["height"], meta["aspect"],
                 meta["tr_cap"], meta["measure"], meta["seal_to_tr_cap"],
                 str(meta["tr_tracking"]), meta["en_weight"], meta["en_tracking"]))
    json.dump(metas, open(os.path.join(ROOT, "docs/asyada-seal/lockups/assets/lockup-meta.json"), "w"),
              indent=1)
    print("\ncanonical:", CANON_SHA)