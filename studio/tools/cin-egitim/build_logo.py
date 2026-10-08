#!/usr/bin/env python3
"""Çin Eğitim — Hedef logonun vektörü (ölçülmüş radyal profilden).

Kaynak: Concept 03 panel -> ICON DETAIL kirpma (170x209) -> 8x LANCZOS (1360x1672).
Yapı: C-seklinde enso halkasi (sagda bosluk) + pagoda.
"""

from pathlib import Path
import math
import json

ROOT = Path(__file__).resolve().parents[3]
RUN = ROOT / "brands/cin-egitim/explorations/enso"
SRC = RUN / "icon-8x.png"

RED = "#C8102E"
INK = "#1F1F1F"

# Kirpma koordinatlarinda olculmus merkez (170x209 olcek)
# 8x olcege cevrilir
CROP_CX, CROP_CY = 107.0, 106.0
SCALE = 8


def load():
    from PIL import Image
    im = Image.open(SRC).convert("RGB")
    return im, im.size[0], im.size[1]


def is_red(p): return p[0] > 140 and p[1] < 100 and p[0] - p[2] > 50
def is_dark(p): return max(p) < 80 and abs(p[0]-p[1]) < 20 and abs(p[1]-p[2]) < 20


def radial_profile(im, W, H):
    px = im.load()
    cx = CROP_CX * SCALE
    cy = CROP_CY * SCALE
    profile = {}
    for deg in range(360):
        th = math.radians(deg)
        hits = []
        for t in range(1, 1200):
            x = int(cx + t * math.cos(th))
            y = int(cy + t * math.sin(th))
            if 0 <= x < W and 0 <= y < H and is_red(px[x, y]):
                hits.append(t)
        if len(hits) >= 3:
            runs = []
            cur = [hits[0]]
            for i in range(1, len(hits)):
                if hits[i] - hits[i-1] > 20:
                    runs.append(cur); cur = [hits[i]]
                else:
                    cur.append(hits[i])
            runs.append(cur)
            main = max(runs, key=len)
            if len(main) >= 3:
                profile[deg] = {
                    "inner": main[0],
                    "outer": main[-1],
                    "width": main[-1] - main[0],
                    "mid": (main[0] + main[-1]) / 2.0,
                }
    return cx, cy, profile


def smooth_open(pts, tension=1.0):
    """Açık nokta dizisi üzerinden yumuşak kübik Bézier."""
    n = len(pts)
    if n < 3:
        return "".join(f"L{p[0]:.1f} {p[1]:.1f}" for p in pts[1:])
    def at(i): return pts[min(max(i, 0), n-1)]
    d = []
    for i in range(n-1):
        p0, p1, p2, p3 = at(i-1), at(i), at(i+1), at(i+2)
        c1 = (p1[0] + (p2[0]-p0[0])/6.0*tension, p1[1] + (p2[1]-p0[1])/6.0*tension)
        c2 = (p2[0] - (p3[0]-p1[0])/6.0*tension, p2[1] - (p3[1]-p1[1])/6.0*tension)
        d.append(f"C{c1[0]:.1f} {c1[1]:.1f} {c2[0]:.1f} {c2[1]:.1f} {p2[0]:.1f} {p2[1]:.1f}")
    return "".join(d)


def enso_path(cx, cy, profile):
    """Yay: dış kenar ileri → düz kapak → iç kenar geri → düz kapak."""
    degs = sorted(profile.keys())
    # Kesintisiz yay: en geniş aralık
    arcs = []
    curr = [degs[0]]
    for i in range(1, len(degs)):
        if degs[i] - degs[i-1] <= 3:
            curr.append(degs[i])
        else:
            arcs.append(curr); curr = [degs[i]]
    arcs.append(curr)
    main_arc = max(arcs, key=len)

    outer_pts, inner_pts = [], []
    for deg in main_arc:
        p = profile[deg]
        th = math.radians(deg)
        outer_pts.append((cx + p["outer"]*math.cos(th), cy + p["outer"]*math.sin(th)))
        inner_pts.append((cx + p["inner"]*math.cos(th), cy + p["inner"]*math.sin(th)))

    d = (f"M{outer_pts[0][0]:.1f} {outer_pts[0][1]:.1f}"
         + smooth_open(outer_pts[1:])
         + f"L{inner_pts[-1][0]:.1f} {inner_pts[-1][1]:.1f}"
         + smooth_open(list(reversed(inner_pts[1:-1])) or inner_pts[-2::-1])
         + "Z")
    return d, main_arc[0], main_arc[-1]


def pagoda_path(im, W, H, cx, cy):
    """Koyu şekilleri bul ve her biri için kontur izle."""
    from collections import deque
    px = im.load()

    dark_pts = [(x, y) for y in range(H) for x in range(W) if is_dark(px[x, y])]
    if not dark_pts:
        return ""

    # Sadece enso'nun iç bolgesindekileri al (R~600 icinde)
    R_limit = 300
    dark_pts = [(x, y) for x, y in dark_pts
                if math.hypot(x-cx, y-cy) < R_limit]

    # Bilesenler
    dark_set = set(dark_pts)
    vis = set()
    comps = []
    for p in dark_pts:
        if p in vis: continue
        q = deque([p]); vis.add(p); comp = [p]
        while q:
            c = q.popleft()
            for dx, dy in ((1,0),(-1,0),(0,1),(0,-1)):
                n = (c[0]+dx, c[1]+dy)
                if n in dark_set and n not in vis:
                    vis.add(n); q.append(n); comp.append(n)
        if len(comp) >= 500:
            comps.append(comp)

    comps.sort(key=len, reverse=True)
    print(f"Pagoda bilesen (enso ici): {len(comps)}")

    # Kontur izleme + RDP
    def trace_contour(comp_set, start):
        dirs = [(1,0),(1,-1),(0,-1),(-1,-1),(-1,0),(-1,1),(0,1),(1,1)]
        def on(x, y):
            return 0 <= x < W and 0 <= y < H and (x, y) in comp_set
        p = start
        b = (p[0]-1, p[1])
        contour = [p]
        first = True
        while first or p != start:
            first = False
            b_dir = None
            for d in range(8):
                if (p[0]+dirs[d][0], p[1]+dirs[d][1]) == b:
                    b_dir = d; break
            if b_dir is None:
                b_dir = 4; b = (p[0]-1, p[1])
            found = False
            for k in range(8):
                d = (b_dir + 1 + k) % 8
                nx, ny = p[0]+dirs[d][0], p[1]+dirs[d][1]
                if on(nx, ny):
                    b = (p[0]+dirs[(d+4)%8][0], p[1]+dirs[(d+4)%8][1])
                    p = (nx, ny); found = True; break
            if not found: break
            contour.append(p)
            if p == start and len(contour) > 2: break
            if len(contour) > 40000: break
        return contour

    def rdp_iter(points, eps):
        if len(points) < 3: return points
        stack = [(0, len(points)-1)]
        keep = [False] * len(points)
        keep[0] = keep[-1] = True
        while stack:
            i, j = stack.pop()
            if j - i <= 1: continue
            ax, ay = points[i]; bx, by = points[j]
            dx, dy = bx-ax, by-ay
            nrm = math.hypot(dx, dy)
            best, bi = -1.0, -1
            for k in range(i+1, j):
                px2, py2 = points[k]
                if nrm < 1e-9:
                    d = math.hypot(px2-ax, py2-ay)
                else:
                    d = abs(dy*(px2-ax) - dx*(py2-ay)) / nrm
                if d > best:
                    best, bi = d, k
            if best > eps:
                keep[bi] = True
                if bi - i > 1: stack.append((i, bi))
                if j - bi > 1: stack.append((bi, j))
        return [points[i] for i, k in enumerate(keep) if k]

    parts = []
    for ci, comp in enumerate(comps[:6]):
        comp_set = set(comp)
        start = min(comp, key=lambda p: (p[1], p[0]))
        contour = trace_contour(comp_set, start)
        xs = [p[0] for p in comp]; ys = [p[1] for p in comp]
        diag = max(max(xs)-min(xs), max(ys)-min(ys))
        eps = max(3.0, min(diag * 0.004, 15.0))
        simple = rdp_iter(contour, eps)
        if len(simple) >= 4:
            d = [f"M{simple[0][0]} {simple[0][1]}"]
            for pt in simple[1:]:
                d.append(f"L{pt[0]} {pt[1]}")
            d.append("Z")
            parts.append("".join(d))
            print(f"  Sekil {ci}: {len(contour)} -> {len(simple)} nokta  bbox {min(xs)}-{max(xs)} x {min(ys)}-{max(ys)}")
    return "".join(parts)


def build():
    RUN.mkdir(parents=True, exist_ok=True)
    im, W, H = load()

    print("Radyal profil olculuyor...")
    cx, cy, profile = radial_profile(im, W, H)
    print(f"Merkez: ({cx:.0f}, {cy:.0f})  olculen aci: {len(profile)}")

    widths = [p["width"] for p in profile.values()]
    print(f"Genislik: min {min(widths)}  medyan {sorted(widths)[len(widths)//2]}  max {max(widths)}")

    enso_d, arc_start, arc_end = enso_path(cx, cy, profile)
    print(f"Yay: {arc_start}° .. {arc_end}°  ({arc_end-arc_start}°)")

    print("\nPagoda izleniyor...")
    dark_d = pagoda_path(im, W, H, cx, cy)

    svg = (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" '
           f'width="{W}" height="{H}" role="img">'
           f'<title>Çin Eğitim — logo</title>'
           f'<path d="{enso_d}" fill="{RED}"/>'
           f'<path d="{dark_d}" fill="{INK}"/></svg>')

    mono = svg.replace(f'fill="{RED}"', f'fill="{INK}"')
    (RUN / "logo.svg").write_text(svg, encoding="utf-8")
    (RUN / "logo-mono.svg").write_text(mono, encoding="utf-8")

    print(f"\nSVG: {len(svg)//1024} KB")
    print(json.dumps({
        "outputs": ["logo.svg", "logo-mono.svg"],
        "canvas": [W, H],
        "enso": {"cx": cx, "cy": cy, "arc": [arc_start, arc_end]},
        "palette": {"red": RED, "ink": INK},
        "canonicalised": 0,
        "status": "HUMAN REVIEW PENDING"
    }, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    build()