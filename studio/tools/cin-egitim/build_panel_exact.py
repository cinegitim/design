#!/usr/bin/env python3
"""Çin Eğitim — Concept 03 panosundan ölçülen parametrik vektör ( kompozisyon doğru)."""

from pathlib import Path
import math
import json

ROOT = Path(__file__).resolve().parents[3]
RUN = ROOT / "brands/cin-egitim/explorations/enso"

RED = "#C8102E"
INK = "#1F1F1F"

# Pano oranlarını koru: panel 1448x1086 -> tuval 1200x900 (4:3)
W, H = 1200, 900

# Pano koordinatlarında ölçümler (ikon kırpma: 750,150, 350x400)
# Enso merkez: panelde (837, 319)
# Çadır merkez: panelde (971, 364)
# Ölçek: panel 1448 -> tuval 1200 = 0.8287

SCALE = 1200 / 1448.0

# Enso (panelden ölçüldü)
enso_cx = 837 * SCALE   # 694
enso_cy = 319 * SCALE   # 264
R_OUTER = 232 * SCALE   # 192
R_INNER = 48  * SCALE   # 40
STROKE = R_OUTER - R_INNER  # 152

# Yay: 37° - 338° (boşluk tepede, sağ-üst)
ARC_START = 37.0
ARC_END = 338.0
ARC_SWEEP = ARC_END - ARC_START  # 301°

# Çadır (panelden ölçüldü)
pagoda_cx = 971 * SCALE   # 805
pagoda_cy = 364 * SCALE   # 302

# Çadır yapısı (üst kısım, zemin hariç) - panel bbox
# rel enso: x[-61,262], y[-169,49] -> genişlik 323, yükseklik 218
# Tuval ölçeğinde:
PAGODA_W = 323 * SCALE   # 268
PAGODA_H = 218 * SCALE   # 181

# Zemin (alt kısım)
GROUND_W = 324 * SCALE   # 269
GROUND_H = 180 * SCALE   # 149

def enso_path(cx, cy):
    n = 200
    outer, inner = [], []
    for i in range(n+1):
        t = i / n
        deg = ARC_START + ARC_SWEEP * t
        th = math.radians(deg)
        h = STROKE / 2.0
        ro = R_INNER + STROKE
        ri = R_INNER
        outer.append((cx + (ro + h) * math.cos(th), cy + (ro + h) * math.sin(th)))
        inner.append((cx + (ri - h) * math.cos(th), cy + (ri - h) * math.sin(th)))
    
    def smooth(pts):
        if len(pts) < 3: return "".join(f"L{p[0]:.1f} {p[1]:.1f}" for p in pts[1:])
        def at(i): return pts[min(max(i,0), len(pts)-1)]
        d = []
        for i in range(len(pts)-1):
            p0,p1,p2,p3 = at(i-1),at(i),at(i+1),at(i+2)
            c1 = (p1[0]+(p2[0]-p0[0])/6.0, p1[1]+(p2[1]-p0[1])/6.0)
            c2 = (p2[0]-(p3[0]-p1[0])/6.0, p2[1]-(p3[1]-p1[1])/6.0)
            d.append(f"C{c1[0]:.1f} {c1[1]:.1f} {c2[0]:.1f} {c2[1]:.1f} {p2[0]:.1f} {p2[1]:.1f}")
        return "".join(d)
    
    d = [f"M{outer[0][0]:.1f} {outer[0][1]:.1f}"]
    d.append(smooth(outer[1:]))
    d.append(f"L{inner[-1][0]:.1f} {inner[-1][1]:.1f}")
    d.append(smooth(list(reversed(inner[1:-1])) or inner[-2::-1]))
    d.append("Z")
    return "".join(d)

def roof_path(cx, top_y, half_width, drop, upturn):
    ridge = half_width * 0.25
    eave = half_width
    d = []
    d.append(f"M{cx - ridge:.1f} {top_y:.1f}")
    d.append(f"C{cx - ridge*0.5:.1f} {top_y - drop*0.3:.1f} "
             f"{cx - eave*0.85:.1f} {top_y - drop*0.1:.1f} "
             f"{cx - eave:.1f} {top_y:.1f}")
    d.append(f"C{cx - eave*0.7:.1f} {top_y - upturn*0.8:.1f} "
             f"{cx - eave*0.5:.1f} {top_y - upturn*0.4:.1f} "
             f"{cx - eave*0.3:.1f} {top_y:.1f}")
    d.append(f"L{cx + ridge:.1f} {top_y:.1f}")
    d.append(f"C{cx + ridge*0.5:.1f} {top_y - drop*0.3:.1f} "
             f"{cx + eave*0.85:.1f} {top_y - drop*0.1:.1f} "
             f"{cx + eave:.1f} {top_y:.1f}")
    d.append(f"C{cx + eave*0.7:.1f} {top_y - upturn*0.8:.1f} "
             f"{cx + eave*0.5:.1f} {top_y - upturn*0.4:.1f} "
             f"{cx + eave*0.3:.1f} {top_y:.1f}")
    d.append(f"L{cx + ridge:.1f} {top_y:.1f} Z")
    return "".join(d)

def tier_path(cx, top_y, half_width, drop, upturn, body_half_width, body_h):
    roof = roof_path(cx, top_y, half_width, drop, upturn)
    body_top = top_y + drop * 0.5
    return roof + (
        f"M{cx - body_half_width:.1f} {body_top:.1f} "
        f"L{cx + body_half_width:.1f} {body_top:.1f} "
        f"L{cx + body_half_width:.1f} {body_top + body_h:.1f} "
        f"L{cx - body_half_width:.1f} {body_top + body_h:.1f} Z"
    )

def pagoda_path(cx, cy):
    d = []
    # Finial
    fx, fy = cx, cy - PAGODA_H/2 - 10
    d.append(f"M{fx:.1f} {fy:.1f} L{fx-4:.1f} {fy+18:.1f} L{fx+4:.1f} {fy+18:.1f} Z")
    for ry in [fy+20, fy+32]:
        d.append(f"M{fx-7:.1f} {ry:.1f} L{fx+7:.1f} {ry:.1f}")
    
    tier_h = PAGODA_H / 3.5
    roof_drop = tier_h * 0.45
    upturn = tier_h * 0.25
    
    for i in range(3):
        tier_top = cy - PAGODA_H/2 + i * tier_h + 15
        hw = PAGODA_W/2 * (1.0 + i * 0.22)
        bw = hw * 0.4
        bh = tier_h * 0.55
        d.append(tier_path(cx, tier_top, hw, roof_drop, upturn, bw, bh))
    
    # Zemin
    gx, gy = cx, cy + PAGODA_H/2 - 8
    d.append(f"M{gx - GROUND_W/2:.1f} {gy:.1f} "
             f"C{gx - GROUND_W*0.35:.1f} {gy + 5:.1f} "
             f"{gx - GROUND_W*0.55:.1f} {gy + GROUND_H*0.4:.1f} "
             f"{gx - GROUND_W*0.25:.1f} {gy + GROUND_H:.1f} "
             f"L{gx + GROUND_W*0.35:.1f} {gy + GROUND_H:.1f} "
             f"C{gx + GROUND_W*0.55:.1f} {gy + GROUND_H*0.4:.1f} "
             f"{gx + GROUND_W*0.35:.1f} {gy + 5:.1f} "
             f"{gx + GROUND_W/2:.1f} {gy:.1f} Z")
    return "".join(d)

def build():
    RUN.mkdir(parents=True, exist_ok=True)
    
    enso_d = enso_path(enso_cx, enso_cy)
    pagoda_d = pagoda_path(pagoda_cx, pagoda_cy)
    
    color_svg = (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" '
                 f'width="{W}" height="{H}" role="img">'
                 f'<title>Çin Eğitim — Concept 03 İşareti (panel kompozisyonu)</title>'
                 f'<path d="{enso_d}" fill="{RED}"/>'
                 f'<path d="{pagoda_d}" fill="{INK}"/></svg>')
    
    mono_svg = color_svg.replace(f'fill="{RED}"', f'fill="{INK}"')
    
    (RUN / "panel-exact-mark.svg").write_text(color_svg, encoding="utf-8")
    (RUN / "panel-exact-mark-mono.svg").write_text(mono_svg, encoding="utf-8")
    
    print(json.dumps({
        "outputs": ["panel-exact-mark.svg", "panel-exact-mark-mono.svg"],
        "canvas": [W, H],
        "enso": {"cx": enso_cx, "cy": enso_cy, "R_outer": R_OUTER, "R_inner": R_INNER,
                 "arc": [ARC_START, ARC_END], "sweep": ARC_SWEEP},
        "pagoda": {"cx": pagoda_cx, "cy": pagoda_cy, "w": PAGODA_W, "h": PAGODA_H},
        "palette": {"red": RED, "ink": INK},
        "source": "Concept 03 panel (1448x1086) -> tuval 1200x900, koordinatları panelden",
        "canonicalised": 0,
        "status": "HUMAN REVIEW PENDING"
    }, indent=2, ensure_ascii=False))

if __name__ == "__main__":
    build()