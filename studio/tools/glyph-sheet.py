#!/usr/bin/env python
"""Turkish glyph + apostrophe behaviour proof sheet, rendered deterministically.

Real outlines. Shows:
  - the full Turkish uppercase set in Bold and in Light (the two roles)
  - the apostrophe in all three states the brand has to decide between
  - the red apostrophe detail as it actually renders, at three optical sizes
  - the wordmark at 3 sizes to prove diacritics survive small sizes
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from typeset import runs_to_path, measure, text_to_path

ROOT = "/Users/serdaryurt/Documents/OpenCode/Design"
OUT = os.path.join(ROOT, "docs/asyada-seal/lockups/assets")
PAPER, INK, VERM = "#F7F3E9", "#141210", "#BD2120"

TR_UP = "ĞĞİİŞŞÇÇÖÖÜÜĞ"
TR_LOW = "ğğışşçöüı"
PUNCT = "’‘'\"–—·…"


def line(runs, weight, cap, track, x, base):
    return runs_to_path(runs, weight, x, base, cap, track)[0]


def build():
    W = 1180
    o = []
    y = 34

    def head(t):
        nonlocal y
        o.append('<text x="0" y="%d" font-family="Helvetica Neue,Helvetica,Arial" font-size="13" '
                 'letter-spacing="1.5" fill="%s" opacity=".55">%s</text>' % (y, INK, t))
        y += 26

    def note(t, at=None):
        """Label sits BELOW the descender/cedilla zone of the row it describes."""
        nonlocal y
        yy = at if at is not None else y
        o.append('<text x="0" y="%d" font-family="Helvetica Neue,Helvetica,Arial" font-size="12" '
                 'fill="%s" opacity=".5">%s</text>' % (yy, INK, t))
        y = yy + 22

    def block(h_px):
        nonlocal y
        y += h_px
        return y

    def row(cap, diacritics=True, desc=0.30):
        """Reserve a baseline with enough headroom for diacritics and descenders."""
        block(cap * (1.45 if diacritics else 1.0) + cap * desc)
        return y

    # --- 1. Turkish uppercase, bold, the wordmark role ---
    head("TÜRKÇE BÜYÜK HARFLER — Bold (wordmark rolü)")
    cap, track = 58, 8
    base = row(cap)
    o.append(line([(TR_UP, INK)], "bold", cap, track, 0, base))
    note("cap %d · tracking %d/1000 em · ölçü %.1f" % (cap, track, measure(TR_UP, "bold", cap, track)),
         at=base + cap * 0.62)
    y += 18

    # --- 2. lowercase + dotless i, to prove the lowercase is real ---
    head("TÜRKÇE KÜÇÜK HARFLER — noktasız ı ve i ayrımı")
    cap2 = 40
    base = row(cap2)
    o.append(line([("asya'da eğitim — ığışçöü", INK)], "light", cap2, 10, 0, base))
    y += cap2 * 0.5 + 40

    # --- 3. the apostrophe decision ---
    head("APOSTROPH DAVRANIŞI — üç durum, aynı punto")
    cap3 = 46
    base = row(cap3, diacritics=False)
    x = 0
    for label, ap in (("’ kıvrık (U+2019)", "’"),
                      ("' düz (U+0027)", "'"),
                      ("apostrofsuz", "")):
        runs = [("ASYA", INK)] + ([(ap, VERM)] if ap else []) + [("DA", INK)]
        o.append(line(runs, "bold", cap3, 6, x, base))
        o.append('<text x="%d" y="%d" font-family="Helvetica Neue,Helvetica,Arial" font-size="12" '
                 'fill="%s" opacity=".55">%s</text>' % (x, base + 22, INK, label))
        x += measure("ASYA" + ap + "DA", "bold", cap3, 6) + 54
    y += 62

    # --- 4. punctuation coverage ---
    head("NOKTALAMA — ’ ‘ ' – — · …")
    b1 = row(38, diacritics=False, desc=0.55)
    o.append(line([(PUNCT, INK)], "bold", 38, 60, 0, b1))
    b2 = row(38, diacritics=False, desc=0.10)
    o.append(line([(PUNCT, INK)], "light", 38, 60, 0, b2))
    y += 58

    # --- 5. the red detail at three optical sizes ---
    head("KIRMIZI APOSROF DETAYI — gerçek boyutlarda")
    base = row(72, diacritics=False, desc=0.50)
    x = 0
    for cap4 in (72, 34, 16):
        o.append(line([("ASYA", INK), ("’", VERM), ("DA", INK)], "bold", cap4, 6, x, base))
        o.append('<text x="%d" y="%d" font-family="Helvetica Neue,Helvetica,Arial" font-size="12" '
                 'fill="%s" opacity=".55">cap %d px</text>' % (x, base + 20, INK, cap4))
        x += measure("ASYA’DA", "bold", cap4, 6) + 46
    y += 54

    # --- 6. wordmark at real delivery sizes ---
    head("TESLİM BOYUTLARI — diyakritikler küçük boyutta da doğru")
    for cap5 in (44, 22, 13):
        base = row(cap5, desc=0.45)
        o.append(line([("ASYA", INK), ("’", VERM), ("DA EĞİTİM", INK)], "bold", cap5, 6, 0, base))
        note("cap %d px" % cap5, at=base + cap5 * 0.62)
        y += 20
    H = y + 24

    svg = ('<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 %d %d" width="%d" height="%d">'
           '<rect width="%d" height="%d" fill="%s"/>%s</svg>'
           % (W, H, W, H, W, H, PAPER, "".join(o)))
    p = os.path.join(OUT, "glyph-test.svg")
    open(p, "w", encoding="utf-8").write(svg)
    print("wrote", os.path.relpath(p, ROOT), W, "x", H)


if __name__ == "__main__":
    build()