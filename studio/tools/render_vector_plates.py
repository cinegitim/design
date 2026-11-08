#!/usr/bin/env python
"""Render the review plates: full wordmarks, glyph crops at 100/400/800, usage."""
import json
import os
import subprocess
import sys

from PIL import Image, ImageDraw

ROOT = "/Users/serdaryurt/Documents/OpenCode/Design"
RUN = os.path.join(ROOT, "brands/asyada-egitim/explorations/wordmark-ref")
SVG = os.path.join(RUN, "svg")
OUT = os.path.join(RUN, "vector-review")
PAPER = (247, 243, 233)

# native-unit crops: x0, y0, w, h
GLYPHS = [
    ("A", 30, -14, 160, 148),
    ("S", 195, -14, 145, 148),
    ("G", 165, 186, 175, 150),
    ("D", 690, -14, 175, 148),
    ("M", 700, 186, 180, 150),
    ("I-dot", 400, 130, 130, 120),
    ("apostrophe", 540, -14, 90, 60),
    ("breve", 165, 130, 175, 62),
]
SMALL = [("full-1000", 1000), ("full-600", 600), ("full-320", 320),
         ("full-200", 200), ("full-120", 120)]

VARIANTS = [("poly", "WU-poly.svg"), ("smooth", "WU.svg"),
            ("A", "WA.svg"), ("B", "WB.svg")]


def render(svg_name, w):
    out = "/tmp/_pl_%s_%d.png" % (svg_name.replace(".", "_"), w)
    subprocess.run(["rsvg-convert", "-w", str(w), "-o", out,
                    os.path.join(SVG, svg_name)], check=True)
    im = Image.open(out).convert("RGBA")
    bg = Image.new("RGBA", im.size, PAPER + (255,))
    bg.alpha_composite(im)
    return bg.convert("RGB"), w / 881.0


def label(img, text, h=26):
    out = Image.new("RGB", (img.width, img.height + h), (255, 255, 255))
    d = ImageDraw.Draw(out)
    d.text((6, 7), text, fill=(20, 20, 20))
    out.paste(img, (0, h))
    return out


def main():
    os.makedirs(OUT, exist_ok=True)
    made = {}

    # ---- full wordmarks at small usage sizes -----------------------------
    for key, wm in VARIANTS:
        tiles = []
        for name, w in SMALL:
            im, _ = render(wm, w)
            tiles.append(label(im, "%s  ·  %d px wide" % (key.upper(), w)))
        W = max(t.width for t in tiles)
        H = sum(t.height + 12 for t in tiles) + 10
        strip = Image.new("RGB", (W, H), (255, 255, 255))
        y = 6
        for t in tiles:
            strip.paste(t, (6, y))
            y += t.height + 12
        strip.save(os.path.join(OUT, "usage-%s.png" % key))
        made.setdefault("usage", {})[key] = "usage-%s.png" % key

    # ---- glyph plates at 100 / 400 / 800 % -------------------------------
    for key, wm in VARIANTS:
        rows = []
        for gname, x0, y0, w, h in GLYPHS:
            tiles = []
            for zoom in (1, 4, 8):
                im, k = render(wm, 881 * zoom)
                c = im.crop((int(x0 * k), int(y0 * k),
                             int((x0 + w) * k), int((y0 + h) * k)))
                tw = 420
                c = c.resize((tw, max(1, int(c.height * tw / c.width))), Image.LANCZOS)
                tiles.append(label(c, "%s %s  ·  %d00 %%" % (key.upper(), gname,
                                                            zoom), h=22))
            row = Image.new("RGB", (420 * 3 + 24, max(t.height for t in tiles)),
                            (255, 255, 255))
            for i, t in enumerate(tiles):
                row.paste(t, (i * (420 + 12), 0))
            rows.append(row)
        W = max(r.width for r in rows)
        H = sum(r.height + 10 for r in rows) + 8
        plate = Image.new("RGB", (W, H), (255, 255, 255))
        y = 4
        for r in rows:
            plate.paste(r, (4, y))
            y += r.height + 10
        plate.save(os.path.join(OUT, "glyphs-%s.png" % key))
        made.setdefault("glyphs", {})[key] = "glyphs-%s.png" % key

    json.dump(made, open(os.path.join(RUN, "audit/vector-review-plates.json"), "w"),
              indent=2)
    print("plates:", ", ".join(sorted(os.listdir(OUT))))


if __name__ == "__main__":
    main()