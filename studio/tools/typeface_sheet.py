#!/usr/bin/env python
"""Side-by-side sheet: reference vs candidate typefaces, aligned on cap height."""
import os
import subprocess
import sys

from PIL import Image, ImageDraw

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import type_assy as TA  # noqa: E402

ROOT = "/Users/serdaryurt/Documents/OpenCode/Design"
RUN = os.path.join(ROOT, "brands/asyada-egitim/explorations/wordmark-ref")
CAND = os.path.expanduser("~/.cache/brand-studio/fonts/shortlist")
INK, PAPER = "#1D2027", "#F7F3E9"
CAP, BASE = 142.0, 155.0        # reference cap height; baseline inside the canvas


def render(d, w, h):
    svg = ('<svg xmlns="http://www.w3.org/2000/svg" width="%d" height="%d" '
           'viewBox="0 0 %d %d"><rect width="%d" height="%d" fill="%s"/>'
           '<path d="%s" fill="%s"/></svg>' % (w, h, w, h, w, h, PAPER, d, INK))
    open("/tmp/_sh.svg", "w").write(svg)
    subprocess.run(["rsvg-convert", "-w", str(w), "-o", "/tmp/_sh.png", "/tmp/_sh.svg"],
                   check=True)
    return Image.open("/tmp/_sh.png").convert("RGB")


def sheet(rows, path, width=1240, pad=14, lh=24):
    H = sum(i.height + lh + pad for _l, i in rows) + pad
    out = Image.new("RGB", (width, H), PAPER)
    d = ImageDraw.Draw(out)
    y = pad
    for lab, im in rows:
        d.rectangle([0, y, width, y + lh], fill=PAPER)
        d.text((6, y + 7), lab, fill=(20, 20, 20))
        out.paste(im, (pad, y + lh))
        d.rectangle([pad, y + lh, pad + im.width, y + lh + im.height],
                    outline=(210, 205, 195))
        y += lh + im.height + pad
    out.save(path)
    return out.size


def main():
    outdir = os.path.join(RUN, "typefaces")
    os.makedirs(outdir, exist_ok=True)
    ref = Image.open(os.path.join(RUN, "reference.jpg")).convert("RGB")
    W, H = 1240, 190

    rows = [("REFERENCE  ·  ASYA'DA  (raster)", ref.crop((38, 55, 936, 215))
             .resize((1346, 240), Image.LANCZOS).crop((0, 0, W, H)))]

    fonts = [("Poppins-Bold.ttf", None), ("Jost-VF.ttf", 600), ("Outfit-VF.ttf", 600),
             ("Figtree-VF.ttf", 600), ("PlusJakarta-VF.ttf", 600),
             ("Montserrat-VF.ttf", 700), ("Manrope-VF.ttf", 700)]
    for fn, wg in fonts:
        p = os.path.join(CAND, fn)
        if not os.path.exists(p):
            continue
        f = TA.load(p, wght=wg)
        d, _w = TA.compose(f, "ASYA'DA", TA.cap_scale(f, CAP), (20.0, BASE))
        rows.append(("%s%s" % (fn, "" if wg is None else " @%d" % wg), render(d, W, H)))

    # glyph strips at matched cap height
    keys = list("SADGMT")
    gw = 200
    gh = 210
    rs = Image.new("RGB", (gw * len(keys), gh), PAPER)
    src = {"S": (198, 314), "A": (36, 184), "D": (636, 768), "G": (188, 330),
           "M": (830, 946), "T": (470, 620)}
    for i, ch in enumerate(keys):
        if ch in src:
            x0, x1 = src[ch]
            c = ref.crop((x0, 52, x1, 226))
            c = c.resize((gw, gh), Image.LANCZOS)
            rs.paste(c, (i * gw, 0))
    rows.insert(1, ("REFERENCE glyphs  ·  " + "  ".join(keys), rs))

    for fn, wg in fonts:
        p = os.path.join(CAND, fn)
        if not os.path.exists(p):
            continue
        f = TA.load(p, wght=wg)
        strip = Image.new("RGB", (gw * len(keys), gh), PAPER)
        for i, ch in enumerate(keys):
            d, _ = TA.compose(f, ch, TA.cap_scale(f, 165), (gw / 2 - 0.0, 180))
            t = render(d, gw, gh)
            strip.paste(t, (i * gw, 0))
        rows.append(("%s  ·  %s" % (fn, "  ".join(keys)), strip))

    size = sheet(rows, os.path.join(outdir, "sheet.png"))
    print("wrote %s %s" % (os.path.join(outdir, "sheet.png"), size))


if __name__ == "__main__":
    main()