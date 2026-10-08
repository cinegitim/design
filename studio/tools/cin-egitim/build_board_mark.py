#!/usr/bin/env python3
"""Çin Eğitim — Concept 03 panosundaki işaretin vektör kurulumu.

BİREBİR DEĞİLDİR — VE BU BİLEREK BİR TERCİHTİR
    Pano bir sunum artefaktıdır: 1440x1080, içindeki en büyük ikon ~250 piksel.
    Böyle bir rasterı izleyip "birebir" demek uydurma hassasiyet olur. Pano
    bir sunum ekranıdır; VECTOR kaynak değildir.

    Burada yapılan: panodaki işaretin TASARIMI gözle okunup, ölçülebilir
    parametrelere çevrildi ve o parametrelerden kurgusal geometri kuruldu.
    Çadır ve mürekkep zemini ise daha önce 862px kaynaktan İZLENMİŞ temiz
    vektördür — aynı çizim, panoda da aynı çizim.

    Birebir sonuç için gereken tek şey: panoyu üreten kişinin kaynak vektörü
    ya da yüksek çözünürlüklü PNG'si. O geldiğinde bu dosya geçersiz olur.

TASARIMIN PANDAN OKUNAN HALİ
    - Arka dağ yok, kuş yok. (Panonun kendi sadeleştirmesi.)
    - Enso üst-sağda açılır, gövdesi daha düzgün ve daha ince.
    - Enso'nun üst ucunda kuru fırça pırıltısı: paralel ince çizgiler.
    - Çadır kompakt, halkanın alt-ortasında.
    - Zemin küçük bir mürekkep sıvraması; canlı sitedeki devasa süpürme değil.
    - Palet: Heritage Red #C8102E · Charcoal #1F1F1F · Warm Gray #EAE7E3

Görsel üretim çağrısı: 0.  Kanonikleştirme: YOK.
"""
from __future__ import annotations

from pathlib import Path
import json
import math

ROOT = Path(__file__).resolve().parents[3]
RUN = ROOT / "brands/cin-egitim/explorations/enso"

RED = "#C8102E"          # Heritage Red — panonun paletinden
INK = "#1F1F1F"          # Charcoal

# --- pano tasarımından okunan parametreler (1000x1000 tuval) ---
CX, CY = 500.0, 500.0
R_MID = 366.0           # halkanın orta yarıçapı
GAP = (330.0, 645.0)    # açıklık üst-sağda; yay 315°
W_MED = 88.0           # medyan darbe kalınlığı
W_END = 0.30            # uçlarda kalan oran


def profile(arc: tuple, n: int = 260) -> list[dict]:
    """Panonun düzgünleştirilmiş darbesi için yazar profili.

    Canlı sitenin darbesinden FARKLI: kaynaktan ölçülmedi, panodan okundu.
    Gövde sol-ortada biraz daha kalın, uçlarda incelir — panodaki gibi.
    """
    a0, a1 = arc
    span = a1 - a0
    out = []
    for i in range(n + 1):
        t = i / n
        deg = a0 + span * t
        th = math.radians(deg)
        # Kalınlık: taban + sol tarafta hafif artış (panodaki ağırlık)
        left = math.cos(math.radians(deg - 100.0))
        w = W_MED * (1.0 + 0.10 * left)
        # Uçlarda sivrilme — sıfıra değil, W_END oranına
        e = min(t / 0.10, (1.0 - t) / 0.10, 1.0)
        k = max(0.0, e) ** 2 * (3 - 2 * max(0.0, e))
        w = w * W_END + (w - w * W_END) * k
        # Yarıçap hafifçe darbe dışına taşar (kabarık gövde)
        r = R_MID + 6.0 * math.sin(math.pi * t) - 2.0
        out.append({"deg": deg, "th": th, "mid": r, "width": w})
    return out


def smooth(points, tension=1.0):
    """Açık dizi üzerinden yumuşak kübik Bézier."""
    n = len(points)
    if n < 3:
        return "".join(f"L{p[0]:.2f} {p[1]:.2f}" for p in points[1:])

    def at(i):
        return points[min(max(i, 0), n - 1)]

    d = []
    for i in range(n - 1):
        p0, p1, p2, p3 = at(i - 1), at(i), at(i + 1), at(i + 2)
        c1 = (p1[0] + (p2[0] - p0[0]) / 6.0 * tension,
              p1[1] + (p2[1] - p0[1]) / 6.0 * tension)
        c2 = (p2[0] - (p3[0] - p1[0]) / 6.0 * tension,
              p2[1] - (p3[1] - p1[1]) / 6.0 * tension)
        d.append(f"C{c1[0]:.2f} {c1[1]:.2f} {c2[0]:.2f} {c2[1]:.2f} "
                 f"{p2[0]:.2f} {p2[1]:.2f}")
    return "".join(d)


def enso_path() -> str:
    """Dış kenar ileri, düz kapak, iç kenar geri, düz kapak."""
    prof = profile(GAP)
    outer, inner = [], []
    for p in prof:
        h = p["width"] / 2.0
        outer.append((CX + (p["mid"] + h) * math.cos(p["th"]),
                      CY + (p["mid"] + h) * math.sin(p["th"])))
        inner.append((CX + (p["mid"] - h) * math.cos(p["th"]),
                      CY + (p["mid"] - h) * math.sin(p["th"])))
    return (f"M{outer[0][0]:.2f} {outer[0][1]:.2f}"
            + smooth(outer[1:])
            + f"L{inner[-1][0]:.2f} {inner[-1][1]:.2f}"
            + smooth(list(reversed(inner[1:-1])) or inner[-2::-1])
            + "Z")


def fringe() -> str:
    """Kuru fırça pırıltısı: enso'nun ÜST ucundan çıkan paralel ince çizgiler.

    Panonun imza detayı. Kaynakta ıbrısımdı; burada bilinçli, sınırlı ve
    her ölçekte okunacak biçimde kurgulanıyor.
    """
    a_end = GAP[1]
    th = math.radians(a_end)
    base_r = R_MID - 10.0
    out = []
    for spread, ln, w in (
            (-9.0, 108.0, 4.6), (-4.0, 132.0, 3.6), (1.5, 118.0, 4.2),
            (7.0, 88.0, 5.0), (13.0, 66.0, 4.4), (19.0, 44.0, 3.2)):
        a = th + math.radians(spread)
        x0 = CX + base_r * math.cos(a)
        y0 = CY + base_r * math.sin(a)
        x1 = x0 + ln * math.cos(a)
        y1 = y0 + ln * math.sin(a)
        mx = (x0 + x1) / 2 - ln * 0.12 * math.sin(a)
        my = (y0 + y1) / 2 + ln * 0.12 * math.cos(a)
        out.append(
            f"M{x0 - w * math.sin(a):.2f} {y0 + w * math.cos(a):.2f}"
            f" Q{mx:.2f} {my:.2f} {x1:.2f} {y1:.2f}"
            f" Q{mx:.2f} {my:.2f} {x0 + w * math.sin(a):.2f} {y0 - w * math.cos(a):.2f} Z")
    return "".join(out)


def place_interior(d: str, span: float, target: tuple) -> str:
    """İzlenmiş iç kurguyu (kaynak koordinatları) hedefe ölçekler.

    Ölçek: iç kurgunun EN UZUN KENARI `span` olacak şekilde. Konum: kaynak
    kutusunun MERKEZİ `target` noktasına gelsin. Dönüşüm tek satır:
    ölçekle çarp, sonra hedefe kaydır.
    """
    import re
    nums = [float(v) for v in re.findall(r"-?\d+\.?\d*", d)]
    xs, ys = nums[0::2], nums[1::2]
    sx0, sy0, sx1, sy1 = min(xs), min(ys), max(xs), max(ys)
    k = span / max(sx1 - sx0, sy1 - sy0)
    ox = target[0] - (sx0 + sx1) / 2.0 * k
    oy = target[1] - (sy0 + sy1) / 2.0 * k
    return (f'<g transform="translate({ox:.2f} {oy:.2f}) scale({k:.5f})">'
            f'<path d="{d}" fill="{INK}"/></g>')


def _points(sub: str) -> list[tuple[float, float]]:
    import re
    n = [float(v) for v in re.findall(r"-?\d+\.?\d*", sub)]
    return list(zip(n[0::2], n[1::2]))


def _emit(pts) -> str:
    return "M" + " ".join(f"{x:.1f} {y:.1f}" for x, y in pts[:-1]) + "Z"


def clip_above(d: str, cut: float) -> str:
    """Yatay düzlemin ÜSTÜNDE kalan kısmı al (Sutherland–Hodgman)."""
    import re
    out = []
    for sub in re.split(r"(?=M)", d):
        if not sub.strip():
            continue
        p = _points(sub)
        if len(p) < 3:
            continue
        cl = []
        for i in range(len(p) - 1):
            a, b = p[i], p[i + 1]
            ain, bin_ = a[1] <= cut, b[1] <= cut
            if ain:
                cl.append(a)
            if ain != bin_:
                t = (cut - a[1]) / (b[1] - a[1])
                cl.append((a[0] + (b[0] - a[0]) * t, cut))
        if len(cl) >= 3:
            out.append(_emit(cl))
    return "".join(out)


def ground(pagoda_box: tuple) -> str:
    """Kompakt mürekkep sıvraması — panodaki gibi, canlı sitenin devasa
    süpürmesi DEĞİL. Asimetrik: sol kuyruk uzun/ince, sağ kuyruk kısa."""
    x0, y0, x1, y1 = pagoda_box
    bw = x1 - x0
    cx = (x0 + x1) / 2.0
    top = y1 - 2.0
    h = bw * 0.22
    f = lambda v: f"{v:.1f}"
    L = cx - bw * 0.86          # sol uç (uzun, ince kuyruk)
    R = cx + bw * 0.62          # sağ uç (kısa)
    return (
        f"M{f(L + bw * 0.30)} {f(top + h * 0.46)} "
        f"C{f(L + bw * 0.16)} {f(top + h * 0.12)} {f(cx - bw * 0.34)} {f(top + h * 0.04)} "
        f"{f(cx - bw * 0.14)} {f(top - h * 0.06)} "
        f"C{f(cx + bw * 0.06)} {f(top - h * 0.16)} {f(cx + bw * 0.26)} {f(top + h * 0.10)} "
        f"{f(cx + bw * 0.44)} {f(top + h * 0.06)} "
        f"C{f(R - bw * 0.06)} {f(top + h * 0.10)} {f(R - bw * 0.02)} {f(top + h * 0.46)} "
        f"{f(R)} {f(top + h * 0.86)} "
        f"C{f(R - bw * 0.16)} {f(top + h * 1.10)} {f(cx + bw * 0.30)} {f(top + h * 1.18)} "
        f"{f(cx - bw * 0.02)} {f(top + h * 1.14)} "
        f"C{f(cx - bw * 0.34)} {f(top + h * 1.10)} {f(cx - bw * 0.56)} {f(top + h * 1.24)} "
        f"{f(L + bw * 0.34)} {f(top + h * 1.02)} "
        f"C{f(L + bw * 0.16)} {f(top + h * 0.92)} {f(L + bw * 0.05)} {f(top + h * 0.74)} "
        f"{f(L)} {f(top + h * 0.52)} Z"
    )


def build() -> dict:
    import re
    traced = (RUN / "simplified-mark.svg").read_text(encoding="utf-8")
    parts = re.findall(r'<path d="([^"]+)" fill="([^"]+)"', traced)
    interior_d = parts[1][0]          # izlenmiş çadır + zemin

    # Çadır ve zemin izlemede BİRLEŞİK çıktı. Panodaki zemin canlı sitedekinden
    # farklı (küçük bir sıvraması), dolayısıyla izlemeyi yeniden kullanamaz.
    # Çadır kaide hizasında yatay kırpılır, zemin kurgusal olarak yazılır.
    CUT = 566.0
    pagoda_d = clip_above(interior_d, CUT)
    pb = _points(pagoda_d)[0], None
    pts = [p for sub in re.split(r"(?=M)", pagoda_d) if sub.strip()
           for p in _points(sub)]
    pbox = (min(p[0] for p in pts), min(p[1] for p in pts),
            max(p[0] for p in pts), max(p[1] for p in pts))
    interior_new = pagoda_d + ground(pbox)

    body = place_interior(interior_new, span=490.0, target=(CX - 4, CY + 110))
    svg = (
        '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 1000 1000" '
        'width="1000" height="1000" role="img" '
        'aria-label="Çin Eğitim — Concept 03 işareti">'
        '<title>Çin Eğitim — Concept 03 işareti</title>'
        f'<path d="{enso_path()}" fill="{RED}"/>'
        f'<path d="{fringe()}" fill="{RED}"/>'
        f'{body}'
        '</svg>')
    mono = svg.replace(f'fill="{RED}"', f'fill="{INK}"')
    (RUN / "board-mark.svg").write_text(svg, encoding="utf-8")
    (RUN / "board-mark-mono.svg").write_text(mono, encoding="utf-8")
    return {
        "outputs": ["board-mark.svg", "board-mark-mono.svg"],
        "arc_degrees": [GAP[0], GAP[1]],
        "arc_sweep_degrees": GAP[1] - GAP[0],
        "median_stroke_width": W_MED,
        "pagoda_box_source_coords": [round(v, 1) for v in pbox],
        "ground": "kurgusal — panodaki kompakt sıvrama",
        "fidelity": "TASARIM KURULUMU — birebir izleme DEĞİL",
        "fidelity_reason": ("pano 1440x1080, en büyük ikon ~250 px; "
                            "birebir iddia edilemez"),
        "reused_vector": "çadır: 862px kaynaktan izlenip kaide hizasında kırpıldı",
        "image_generation_calls": 0,
        "canonicalised": 0,
        "status": "HUMAN REVIEW PENDING",
    }


if __name__ == "__main__":
    print(json.dumps(build(), indent=2, ensure_ascii=False))