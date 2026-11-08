#!/usr/bin/env python
"""Build seal + wordmark lockups (stacked and horizontal) for W1/W2/W3.

The canonical seal is composited from the locked file, never redrawn: only
placement transforms are applied, and the geometry is asserted byte-identical.
"""
import hashlib
import json
import os
import re
import subprocess
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import build_wordmark as B

ROOT = "/Users/serdaryurt/Documents/OpenCode/Design"
RUN = os.path.join(ROOT, "brands/asyada-egitim/explorations/wordmark-ref")
OUT = os.path.join(RUN, "lockups")
CANON = os.path.join(ROOT, "brands/asyada-egitim/assets/v01-canonical.svg")
CANON_SHA = "8f5d46f0302c4cc7e3765d3bfce9445f842dbd92f1e0f8fbe99f9f509c77e11a"

INK = B.INK
PAPER = B.PAPER


def seal(ink=None, paper=None, mono=False):
    """Canonical seal, verbatim, with only an optional colour-variant recolour."""
    ink = ink or INK
    paper = paper or PAPER
    src = open(CANON, encoding="utf-8").read()
    assert hashlib.sha256(src.encode()).hexdigest() == CANON_SHA, "canonical seal changed"
    rect = re.search(r'<rect [^>]*/>', src).group(0)
    paths = re.findall(r'<path d="[^"]+" fill="#FFFFFF"/>', src)
    assert len(paths) == 2
    if mono:
        rect = rect.replace('fill="#BD2120"', 'fill="%s"' % paper)
        paths = [p.replace('fill="#FFFFFF"', 'fill="%s"' % ink) for p in paths]
    return rect, paths


def inner_of(svg_path):
    s = open(svg_path, encoding="utf-8").read()
    m = re.search(r'</title>(.*)</svg>', s, re.S)
    return m.group(1).strip()


def dims(svg_path):
    m = re.search(r'viewBox="0 0 ([\d.]+) ([\d.]+)"', open(svg_path, encoding="utf-8").read())
    return float(m.group(1)), float(m.group(2))


def build(name):
    src = os.path.join(RUN, "svg", "%s.svg" % name)
    inner = inner_of(src)
    w, h = dims(src)
    seal_w = 300.0
    seal_h = seal_w * 370.0 / 400.0
    pad = 44.0

    # ---- stacked: seal centred above, wordmark centred below ----
    gap = 64.0
    W = max(seal_w, w) + pad * 2
    H = seal_h + gap + h + pad * 2
    r, ps = seal()
    body = ('<g transform="translate(%.2f,%.2f) scale(%.6f)" data-canonical-sha256="%s">%s%s</g>'
            % ((W - seal_w) / 2, pad, seal_w / 400.0, CANON_SHA, r, "".join(ps)))
    body += ('<g transform="translate(%.2f,%.2f)">%s</g>'
             % ((W - w) / 2, pad + seal_h + gap, inner))
    svg = ('<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 %.2f %.2f" width="%.2f" '
           'height="%.2f" role="img" aria-label="Asya\'da Eğitim — %s stacked lockup">'
           '<title>%s — stacked lockup</title>\n<rect width="%.2f" height="%.2f" fill="%s"/>\n%s\n</svg>\n'
           % (W, H, W, H, name, name, W, H, PAPER, body))
    p1 = os.path.join(OUT, "%s-stacked.svg" % name)
    open(p1, "w", encoding="utf-8").write(svg)

    # ---- horizontal: seal left, wordmark right, optically centred ----
    gap = 76.0
    W2 = seal_w + gap + w + pad * 2
    H2 = max(seal_h, h) + pad * 2
    r, ps = seal()
    body = ('<g transform="translate(%.2f,%.2f) scale(%.6f)" data-canonical-sha256="%s">%s%s</g>'
            % (pad, pad + (H2 - pad * 2 - seal_h) / 2, seal_w / 400.0, CANON_SHA, r, "".join(ps)))
    body += ('<g transform="translate(%.2f,%.2f)">%s</g>'
             % (pad + seal_w + gap, pad + (H2 - pad * 2 - h) / 2, inner))
    svg = ('<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 %.2f %.2f" width="%.2f" '
           'height="%.2f" role="img" aria-label="Asya\'da Eğitim — %s horizontal lockup">'
           '<title>%s — horizontal lockup</title>\n<rect width="%.2f" height="%.2f" fill="%s"/>\n%s\n</svg>\n'
           % (W2, H2, W2, H2, name, name, W2, H2, PAPER, body))
    p2 = os.path.join(OUT, "%s-horizontal.svg" % name)
    open(p2, "w", encoding="utf-8").write(svg)

    # ---- dark variant of the horizontal lockup (mono-paper seal) ----
    r, ps = seal(mono=True)
    body = ('<g transform="translate(%.2f,%.2f) scale(%.6f)" data-canonical-sha256="%s" '
            'data-colour-variant="mono-paper">%s%s</g>'
            % (pad, pad + (H2 - pad * 2 - seal_h) / 2, seal_w / 400.0, CANON_SHA, r, "".join(ps)))
    dark_inner = re.sub(r'fill="#1D2027"', 'fill="#F7F3E9"', inner)
    body += ('<g transform="translate(%.2f,%.2f)">%s</g>'
             % (pad + seal_w + gap, pad + (H2 - pad * 2 - h) / 2, dark_inner))
    svg = ('<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 %.2f %.2f" width="%.2f" '
           'height="%.2f" role="img" aria-label="Asya\'da Eğitim — %s horizontal lockup, dark">'
           '<title>%s — horizontal lockup, dark</title>\n<rect width="%.2f" height="%.2f" fill="%s"/>\n%s\n</svg>\n'
           % (W2, H2, W2, H2, name, name, W2, H2, INK, body))
    p3 = os.path.join(OUT, "%s-horizontal-dark.svg" % name)
    open(p3, "w", encoding="utf-8").write(svg)

    return {"stacked": p1, "horizontal": p2, "dark": p3,
            "stacked_dims": [round(W, 2), round(H, 2)],
            "horizontal_dims": [round(W2, 2), round(H2, 2)]}


if __name__ == "__main__":
    os.makedirs(OUT, exist_ok=True)
    out = {}
    for n in ("W1", "W2", "W3"):
        out[n] = build(n)
        print("%-3s stacked %s  horizontal %s" % (n, out[n]["stacked_dims"], out[n]["horizontal_dims"]))
    json.dump(out, open(os.path.join(RUN, "audit/lockup-dims.json"), "w"), indent=1)