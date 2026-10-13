"""Deterministic Chinese editorial motif primitives (SVG paths, no raster).

Every function returns SVG markup only. Motifs are generated from explicit
geometry so the campaign art direction is reproducible and editable.
"""
import math

# ---------------------------------------------------------------- palette
BRAND_RED   = '#BD2120'   # approved brand signature red
BRAND_INK   = '#1D2027'
BRAND_PAPER = '#F7F3E9'
CHINA_RED   = '#DE2910'   # campaign-only
GOLD_IMP    = '#D9A441'   # campaign-only
GOLD_BRIGHT = '#F3C64D'   # campaign-only
IVORY       = '#F4E8D3'   # campaign-only


# ------------------------------------------------------- A. window lattice
def lattice(x, y, w, h, cols, rows, stroke, sw, opacity=1.0, inset=0.0,
            pattern='ice', gap=None):
    """Chinese window-lattice panel drawn as an ice-ray / angular grid.

    pattern='ice'    -> diagonal ice-ray cracks inside a square lattice
    pattern='angular'-> staggered angular breaks (Suzhou garden screen)
    pattern='huawin' -> rounded flower-window ring with radial mullions
    """
    g = gap if gap is not None else sw
    cw, ch = (w - 2 * inset) / cols, (h - 2 * inset) / rows
    p = [f'<g opacity="{opacity}" fill="none" stroke="{stroke}" '
         f'stroke-width="{sw}" stroke-linecap="round">']
    x0, y0 = x + inset, y + inset
    if pattern == 'huawin':
        r = min(cw, ch) * 0.62
        cx, cy = x0 + cw * 0.5, y0 + ch * 0.5
        p.append(f'<circle cx="{cx:.2f}" cy="{cy:.2f}" r="{r:.2f}"/>')
        n = max(cols, rows)
        for i in range(n):
            a = 2 * math.pi * i / n
            p.append(f'<path d="M{cx:.2f} {cy:.2f} L{cx + math.cos(a) * r:.2f} '
                     f'{cy + math.sin(a) * r:.2f}"/>')
    p.append('</g>')
    # outer frame
    p.append(f'<rect x="{x0:.2f}" y="{y0:.2f}" width="{w - 2 * inset:.2f}" '
             f'height="{h - 2 * inset:.2f}" fill="none" stroke="{stroke}" '
             f'stroke-width="{sw * 1.35:.2f}" opacity="{opacity}"/>')
    # interior rules
    inner = [f'<g opacity="{opacity}" fill="none" stroke="{stroke}" '
             f'stroke-width="{sw * 0.8:.2f}">']
    for c in range(1, cols):
        inner.append(f'<path d="M{x0 + c * cw:.2f} {y0:.2f} '
                     f'L{x0 + c * cw:.2f} {y0 + h - 2 * inset:.2f}"/>')
    for r_ in range(1, rows):
        inner.append(f'<path d="M{x0:.2f} {y0 + r_ * ch:.2f} '
                     f'L{x0 + w - 2 * inset:.2f} {y0 + r_ * ch:.2f}"/>')
    # diagonals
    for r_ in range(rows):
        for c in range(cols):
            cx, cy = x0 + c * cw, y0 + r_ * ch
            if pattern == 'ice' and (r_ + c) % 2 == 0:
                inner.append(f'<path d="M{cx:.2f} {cy + ch:.2f} '
                             f'L{cx + cw:.2f} {cy:.2f}"/>')
            elif pattern == 'angular' and (r_ + c) % 3 == 0:
                inner.append(f'<path d="M{cx:.2f} {cy + ch:.2f} '
                             f'L{cx + cw * 0.5:.2f} {cy + ch * 0.5:.2f} '
                             f'L{cx + cw:.2f} {cy:.2f}"/>')
    inner.append('</g>')
    return ''.join(p + inner)


# --------------------------------------------------- B. xiangyun auspicious
def xiangyun(cx, cy, scale, stroke, sw, opacity=1.0, lobes=5):
    """Flowing auspicious-cloud contour (xiangyun) built from lobed arcs."""
    r = scale
    pts = []
    for i in range(lobes):
        a = math.pi * (0.15 + 1.7 * i / (lobes - 1))
        pts.append((cx + math.cos(a) * r * 0.95,
                    cy - math.sin(a) * r * 0.42))
    d = f'M{cx - r:.2f} {cy:.2f}'
    d += f' C{cx - r * 0.86:.2f} {cy - r * 0.60:.2f} ' \
         f'{cx - r * 0.52:.2f} {cy - r * 0.66:.2f} {cx - r * 0.28:.2f} {cy - r * 0.46:.2f}'
    for i, (px, py) in enumerate(pts):
        nx = pts[i + 1][0] if i + 1 < len(pts) else cx + r
        ny = pts[i + 1][1] if i + 1 < len(pts) else cy - r * 0.30
        mx = (px + nx) / 2
        d += f' C{px:.2f} {py - r * 0.34:.2f} {nx:.2f} {ny - r * 0.30:.2f} ' \
             f'{nx:.2f} {ny:.2f}'
    d += f' C{cx + r * 0.72:.2f} {cy + r * 0.26:.2f} {cx + r * 0.40:.2f} ' \
         f'{cy + r * 0.02:.2f} {cx:.2f} {cy + r * 0.02:.2f}' \
         f' C{cx - r * 0.42:.2f} {cy + r * 0.02:.2f} {cx - r * 0.70:.2f} ' \
         f'{cy + r * 0.30:.2f} {cx - r:.2f} {cy:.2f} Z'
    return f'<path d="{d}" fill="none" stroke="{stroke}" ' \
           f'stroke-width="{sw}" stroke-linecap="round" opacity="{opacity}"/>'


# --------------------------------------------------------- C. seal accent
def seal_mark(x, y, size, fill, opacity=1.0, glyphs=1):
    """Small geometric seal-inspired editorial accent.

    Deliberately abstract: a rounded square with an inscribed diamond and a
    centre dot. It never imitates an official government stamp, a university
    seal, an award or an endorsement.
    """
    s = size
    cx, cy = x + s / 2, y + s / 2
    d = s * 0.30
    out = [f'<g opacity="{opacity}">']
    out.append(f'<rect x="{x:.2f}" y="{y:.2f}" width="{s:.2f}" height="{s:.2f}" '
               f'rx="{s * 0.16:.2f}" fill="{fill}"/>')
    out.append(f'<path d="M{cx:.2f} {cy - d:.2f} L{cx + d:.2f} {cy:.2f} '
               f'L{cx:.2f} {cy + d:.2f} L{cx - d:.2f} {cy:.2f} Z" '
               f'fill="none" stroke="{BRAND_PAPER}" stroke-width="{s * 0.085:.2f}"/>')
    out.append(f'<circle cx="{cx:.2f}" cy="{cy:.2f}" r="{s * 0.055:.2f}" '
               f'fill="{BRAND_PAPER}"/>')
    out.append('</g>')
    return ''.join(out)


# ------------------------------------------ D. key / meander (leiwen) border
def meander_border(x, y, w, h, stroke, sw, cell=26, opacity=1.0, inset=0):
    """Restrained leiwen (thunder/key) meander used as a frame detail."""
    p = [f'<g opacity="{opacity}" fill="none" stroke="{stroke}" '
         f'stroke-width="{sw}" stroke-linejoin="round">']
    def row(yy, reverse=False):
        d = f'M{x + inset:.2f} {yy:.2f}'
        n = int((w - 2 * inset) // cell)
        for i in range(n + 1):
            xx = x + inset + i * cell
            if i == n:
                d += f' L{xx:.2f} {yy:.2f}'
                continue
            sgn = 1 if not reverse else -1
            d += (f' L{xx + cell * 0.30:.2f} {yy + sgn * cell * 0.34:.2f}'
                  f' L{xx + cell * 0.70:.2f} {yy - sgn * cell * 0.34:.2f}'
                  f' L{xx + cell:.2f} {yy:.2f}')
        p.append(f'<path d="{d}"/>')
    def col(xx, reverse=False):
        d = f'M{xx:.2f} {y + inset:.2f}'
        n = int((h - 2 * inset) // cell)
        for i in range(n + 1):
            yy = y + inset + i * cell
            if i == n:
                d += f' L{xx:.2f} {yy:.2f}'
                continue
            sgn = 1 if not reverse else -1
            d += (f' L{xx + sgn * cell * 0.34:.2f} {yy + cell * 0.30:.2f}'
                  f' L{xx - sgn * cell * 0.34:.2f} {yy + cell * 0.70:.2f}'
                  f' L{xx:.2f} {yy + cell:.2f}')
        p.append(f'<path d="{d}"/>')
    row(y + inset)
    row(y + h - inset, True)
    col(x + inset)
    col(x + w - inset, True)
    p.append('</g>')
    return ''.join(p)


# ------------------------------------------- F. moon gate / circular opening
def moon_gate(cx, cy, r, ring_stroke, ring_sw, inner_clip_id, opacity=1.0):
    """Circular moon-gate silhouette ring with a clip path for photography."""
    return (f'<clipPath id="{inner_clip_id}">'
            f'<circle cx="{cx:.2f}" cy="{cy:.2f}" r="{r:.2f}"/></clipPath>'
            f'<circle cx="{cx:.2f}" cy="{cy:.2f}" r="{r:.2f}" fill="none" '
            f'stroke="{ring_stroke}" stroke-width="{ring_sw}" '
            f'opacity="{opacity}"/>')


def roofline(x, y, w, h, fill, opacity=1.0, tiers=3):
    """Geometric Chinese roofline rhythm: stacked upturned-eave silhouettes."""
    out = [f'<g opacity="{opacity}" fill="{fill}">']
    tier_h = h / tiers
    for t in range(tiers):
        ty = y + t * tier_h
        tw = w * (1 - t * 0.16)
        tx = x + (w - tw) / 2
        out.append(f'<path d="M{tx:.2f} {ty + tier_h:.2f} '
                   f'C{tx + tw * 0.10:.2f} {ty + tier_h * 0.62:.2f} '
                   f'{tx + tw * 0.30:.2f} {ty + tier_h * 0.20:.2f} '
                   f'{tx + tw * 0.50:.2f} {ty + tier_h * 0.16:.2f} '
                   f'C{tx + tw * 0.72:.2f} {ty + tier_h * 0.16:.2f} '
                   f'{tx + tw * 0.92:.2f} {ty + tier_h * 0.60:.2f} '
                   f'{tx + tw:.2f} {ty + tier_h:.2f} Z"/>')
    out.append('</g>')
    return ''.join(out)


def ink_sweep(pts, fill, opacity=1.0):
    """Expressive ink-like directional sweep (no calligraphy imitation)."""
    d = 'M' + ' L'.join(f'{px:.2f} {py:.2f}' for px, py in pts)
    return (f'<path d="{d} Z" fill="{fill}" opacity="{opacity}" '
            f'stroke="none"/>')
