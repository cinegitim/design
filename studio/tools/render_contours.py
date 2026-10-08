#!/usr/bin/env python
"""Render the before/after contour comparison plates for human review.

Produces 100 %, 400 % and 800 % crops of the same letter regions from the
polygonal build and the cubic-Bezier build, plus a difference overlay, so the
review page can show what actually changed rather than asserting it.
"""
import os
import subprocess

from PIL import Image, ImageDraw

ROOT = "/Users/serdaryurt/Documents/OpenCode/Design"
RUN = os.path.join(ROOT, "brands/asyada-egitim/explorations/wordmark-ref")
SVG = os.path.join(RUN, "svg")
OUT = os.path.join(RUN, "contours")
PAPER = (247, 243, 233)

# native-unit crops (x0, y0, w, h) chosen to cover the shapes the eye reads:
# the S spine (curve), the A apex (sharp corner), the G bowl + counter,
# the D bowl (counter), the red apostrophe and the G breve / I dot diacritics.
REGIONS = [
    ("S-spine", 150, -14, 130, 150),
    ("A-apex",  406, -14, 130, 150),
    ("D-bowl",  606, -14, 150, 150),
    ("G-bowl",  150, 150, 200, 190),
    ("I-dot",   390, 150, 120, 190),
    ("EN-line", 0, 366, 300, 62),
]


def raster(svg_path, w):
    out = "/tmp/_cc_%s_%d.png" % (os.path.basename(svg_path).replace(".svg", ""), w)
    subprocess.run(["rsvg-convert", "-w", str(w), "-o", out, svg_path], check=True)
    im = Image.open(out).convert("RGBA")
    bg = Image.new("RGBA", im.size, PAPER + (255,))
    bg.alpha_composite(im)
    return bg.convert("RGB"), w / 881.0


def crop(im, k, x0, y0, w, h):
    return im.crop((int(x0 * k), int(y0 * k), int((x0 + w) * k), int((y0 + h) * k)))


def main():
    os.makedirs(OUT, exist_ok=True)
    W = 941

    for label, zoom in (("100", 1), ("400", 4), ("800", 8)):
        # Render at the zoom's own resolution. Cropping a 1x render at 8x walks
        # off the bitmap and PIL pads the result with black, which produced a
        # completely black "800 %" plate.
        rasters = {k: raster(os.path.join(SVG, v + ".svg"), W * zoom)
                   for k, v in (("poly", "WU-poly"), ("cubic", "WU"))}
        for name, x0, y0, w, h in REGIONS:
            panels = []
            for key in ("poly", "cubic"):
                im, k = rasters[key]
                c = crop(im, k, x0, y0, w, h)
                tw = min(880, int(w * k))
                c = c.resize((tw, max(1, int(c.height * tw / c.width))), Image.LANCZOS)
                panels.append((c, "polygon (before)" if key == "poly"
                               else "cubic Bézier (after)"))
            lab_h, gap = 30, 18
            H = sum(p[0].height for p in panels) + lab_h * 2 + gap
            out = Image.new("RGB", (880, H), (255, 255, 255))
            d = ImageDraw.Draw(out)
            y = 0
            for c, txt in panels:
                d.rectangle([0, y, 879, y + lab_h], fill=(255, 255, 255))
                d.text((6, y + 9), "%s  ·  %s  ·  %s%%" % (name, txt, label),
                       fill=(20, 20, 20))
                out.paste(c, (0, y + lab_h))
                d.rectangle([0, y + lab_h, 879, y + lab_h + c.height],
                            outline=(190, 190, 190))
                y += lab_h + c.height + gap
            out.save(os.path.join(OUT, "%s-%s.png" % (name.lower(), label)))
    print("wrote %d comparison plates to %s" % (len(REGIONS) * 3, OUT))


if __name__ == "__main__":
    main()