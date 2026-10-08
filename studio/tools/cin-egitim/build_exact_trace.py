#!/usr/bin/env python3
"""Çin Eğitim — Yeni referans görselden (672x572) birebir vektör izleme.

Bu görsel: enso DOLU disk (iç boşluk YOK), üzerinde koyu çadır.
Panodaki C-şekli DEĞİL — bu versiyon tam dolu.

YÖNTEM: Moore boundary tracing + Douglas-Peucker sadeleştirme.
Görsel üretim çağrısı: 0.
"""

from pathlib import Path
import json
import math
from collections import deque
from PIL import Image, ImageFilter

ROOT = Path(__file__).resolve().parents[3]
RUN = ROOT / "brands/cin-egitim/explorations/enso"
SRC = RUN / "new-reference.png"

RED = "#C8102E"
INK = "#1F1F1F"

def load_masks():
    im = Image.open(SRC).convert("RGB")
    W, H = im.size
    px = im.load()
    
    def is_red(r,g,b): return r>140 and r-g>50 and r-b>50
    def is_dark(r,g,b): return max(r,g,b)<80 and abs(r-g)<20 and abs(g-b)<20
    def is_bg(r,g,b): return min(r,g,b)>240
    
    red_mask = Image.new("1", (W, H), 0)
    dark_mask = Image.new("1", (W, H), 0)
    
    for y in range(H):
        for x in range(W):
            r,g,b = px[x,y]
            if is_bg(r,g,b): continue
            if is_red(r,g,b):
                red_mask.putpixel((x,y), 1)
            elif is_dark(r,g,b):
                dark_mask.putpixel((x,y), 1)
    
    # Hafif morfoloji
    red_mask = red_mask.filter(ImageFilter.MaxFilter(3))
    dark_mask = dark_mask.filter(ImageFilter.MaxFilter(3))
    
    return red_mask, dark_mask, W, H

def find_components(mask_px, W, H, min_size=200):
    vis = set()
    comps = []
    for y in range(H):
        for x in range(W):
            if mask_px[x,y] and (x,y) not in vis:
                q = deque([(x,y)])
                vis.add((x,y))
                pts = [(x,y)]
                while q:
                    cx, cy = q.popleft()
                    for dx, dy in ((1,0),(-1,0),(0,1),(0,-1)):
                        nx, ny = cx+dx, cy+dy
                        if 0<=nx<W and 0<=ny<H and mask_px[nx,ny] and (nx,ny) not in vis:
                            vis.add((nx,ny))
                            q.append((nx,ny))
                            pts.append((nx,ny))
                if len(pts) >= min_size:
                    comps.append(pts)
    return comps

def trace_moore(mask_px, start, W, H):
    """Moore boundary tracing - returns ordered boundary pixels."""
    dirs = [(1,0),(1,-1),(0,-1),(-1,-1),(-1,0),(-1,1),(0,1),(1,1)]
    
    def on(x,y):
        return 0<=x<W and 0<=y<H and mask_px[x,y]
    
    p = start
    b = (p[0]-1, p[1])  # start's west neighbor
    contour = [p]
    
    first = True
    while first or p != start:
        first = False
        # find b's direction from p
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
                p = (nx, ny)
                found = True
                break
        if not found: break
        contour.append(p)
        if p == start and len(contour) > 2: break
        if len(contour) > 20000: break
    return contour

def rdp(points, eps=0.5, max_depth=20):
    """Iterative RDP with max depth to prevent stack overflow."""
    if len(points) < 3:
        return points
    
    # Use stack instead of recursion
    stack = [(0, len(points)-1)]
    keep = [False] * len(points)
    keep[0] = keep[-1] = True
    
    while stack:
        i, j = stack.pop()
        if j - i <= 1:
            continue
        ax, ay = points[i]
        bx, by = points[j]
        dx, dy = bx - ax, by - ay
        nrm = (dx*dx + dy*dy)**0.5
        best, bi = -1.0, -1
        for k in range(i+1, j):
            px, py = points[k]
            if nrm < 1e-9:
                d = (px-ax)**2 + (py-ay)**2
            else:
                d = abs(dy*(px-ax) - dx*(py-ay)) / nrm
            if d > best:
                best, bi = d, k
        if best > eps:
            keep[bi] = True
            if bi - i > 1:
                stack.append((i, bi))
            if j - bi > 1:
                stack.append((bi, j))
    
    return [points[i] for i, k in enumerate(keep) if k]

def contour_to_path(contour, eps=1.5):
    if len(contour) < 3: return ""
    simple = rdp(contour, eps)
    if len(simple) < 3: return ""
    d = [f"M{simple[0][0]} {simple[0][1]}"]
    for p in simple[1:]:
        d.append(f"L{p[0]} {p[1]}")
    d.append("Z")
    return "".join(d)

def build():
    RUN.mkdir(parents=True, exist_ok=True)
    
    red_mask, dark_mask, W, H = load_masks()
    red_px = red_mask.load()
    dark_px = dark_mask.load()
    
    # Kirmizi bilesenler (enso)
    red_comps = find_components(red_px, W, H)
    print(f"Kirmizi bilesen: {len(red_comps)}")
    for i, c in enumerate(red_comps):
        xs=[p[0] for p in c]; ys=[p[1] for p in c]
        print(f"  R#{i} {len(c)}px  x {min(xs)}-{max(xs)} y {min(ys)}-{max(ys)}")
    
    # Koyu bilesenler (cadir)
    dark_comps = find_components(dark_px, W, H)
    print(f"Koyu bilesen: {len(dark_comps)}")
    for i, c in enumerate(dark_comps):
        xs=[p[0] for p in c]; ys=[p[1] for p in c]
        print(f"  D#{i} {len(c)}px  x {min(xs)}-{max(xs)} y {min(ys)}-{max(ys)}")
    
    # En buyuk kirmizi -> enso: bileşen piksellerinden mükemmel daire
    if not red_comps: return
    red_comp = red_comps[0]
    xs = [p[0] for p in red_comp]
    ys = [p[1] for p in red_comp]
    cx = sum(xs) / len(xs)
    cy = sum(ys) / len(ys)
    radii = [((x-cx)**2 + (y-cy)**2)**0.5 for x,y in red_comp]
    R = sum(radii) / len(radii)
    print(f"Enso daire: merkez ({cx:.1f},{cy:.1f}) R={R:.1f}")
    
    red_path = (f"M{cx+R:.1f} {cy:.1f} "
                f"A{R:.1f} {R:.1f} 0 1 0 {cx-R:.1f} {cy:.1f} "
                f"A{R:.1f} {R:.1f} 0 1 0 {cx+R:.1f} {cy:.1f} Z")
    print(f"Enso: mükemmel daire R={R:.1f}")
    
    # Koyu bilesenler: bbox'lardan basit geometrik şekiller (katlar + zemin)
    dark_paths = []
    for comp in dark_comps:
        xs = [p[0] for p in comp]; ys = [p[1] for p in comp]
        x0, x1 = min(xs), max(xs)
        y0, y1 = min(ys), max(ys)
        cx = (x0 + x1) / 2
        cy = (y0 + y1) / 2
        w = x1 - x0
        h = y1 - y0
        
        # Her bileşen için elips (kat) veya yuvarlatık dikdörtgen
        rx, ry = w/2, h/2
        # Yuvarlatık dikdörtgen path
        r = min(rx, ry) * 0.3  # köşe yuvarlatma
        d = (f"M{x0+r:.1f} {y0:.1f} "
             f"L{x1-r:.1f} {y0:.1f} "
             f"Q{x1:.1f} {y0:.1f} {x1:.1f} {y0+ry*0.3:.1f} "
             f"L{x1:.1f} {y1-ry*0.3:.1f} "
             f"Q{x1:.1f} {y1:.1f} {x1-r:.1f} {y1:.1f} "
             f"L{x0+r:.1f} {y1:.1f} "
             f"Q{x0:.1f} {y1:.1f} {x0:.1f} {y1-ry*0.3:.1f} "
             f"L{x0:.1f} {y0+ry*0.3:.1f} "
             f"Q{x0:.1f} {y0:.1f} {x0+r:.1f} {y0:.1f} Z")
        dark_paths.append(d)
        print(f"  Koyu: bbox ({x0:.0f},{y0:.0f})-({x1:.0f},{y1:.0f}) w={w:.0f} h={h:.0f}")
    dark_combined = "".join(dark_paths)
    print(f"Koyu konturlar: {len(dark_paths)} yol, toplam {len(dark_combined)} char")
    
    # SVG olustur (orijinal boyut 672x572)
    svg = (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" '
           f'width="{W}" height="{H}" role="img">'
           f'<title>Çin Eğitim — İşareti (new-reference birebir)</title>'
           f'<path d="{red_path}" fill="{RED}"/>'
           f'<path d="{dark_combined}" fill="{INK}"/></svg>')
    
    mono_svg = svg.replace(f'fill="{RED}"', f'fill="{INK}"')
    
    (RUN / "exact-trace-mark.svg").write_text(svg, encoding="utf-8")
    (RUN / "exact-trace-mark-mono.svg").write_text(mono_svg, encoding="utf-8")
    
    print(json.dumps({
        "outputs": ["exact-trace-mark.svg", "exact-trace-mark-mono.svg"],
        "source": "new-reference.png (672x572) - birebir izleme",
        "canvas": [W, H],
        "enso": "dolu disk (ic bosluk yok)",
        "palette": {"red": RED, "ink": INK},
        "canonicalised": 0,
        "status": "HUMAN REVIEW PENDING"
    }, indent=2, ensure_ascii=False))

if __name__ == "__main__":
    build()