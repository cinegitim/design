#!/usr/bin/env python3
"""Çin Eğitim — enso (円相) ölçümü ve temiz vektör yeniden kurulumu.

KAYNAK
    /cinegitim-icon.png, 862x834, SHA-256 820e3b79…  (canlı sitenin apple-touch-icon)
    Ana logonun (/images/cinegitim-logo.png, 120x116) 7 kat çözünürlüklü sürümü.

NEDEN YENİDEN KURULUYOR
    Kilitlenebilir bir varlık vektör olmak zorunda. 862x834 raster favicon
    (16px), tek renk üretim ve baskı için yeterli değildir. Asya'da Eğitim'de
    de aynı sonuç çıktı: otomatik raster izleme ölçülen her şeyi iyileştirdi
    ama görsel olarak daha kötü oldu.

TASARIM KARARI — DOKU ATILIR, HAREKET KORUNUR
    Kaynaktaki kuru fırça beyaz boşlukları ve kâğıt greni bir RESİM dokusudur;
    16px'te ve tek renkte yeniden üretilemez, yalnızca bulanıklaştırır. Bu
    yüzden yeniden kurulum dokuyu bilinçli olarak düşürür ve yalnız HAREKETI
    korur: açık yay, değişken kalınlık, iki uçta sivrilme.

ÖLÇÜM
    Her açıda kırmızı maskenin yarıçap dağılımı alınır ve RAY ÜZERİNDEKİ
    KIRINTILI BÖLGELERİN SAYISI da raporlanır. Darbe eksenine dik olduğu için
    geniş kalınlık güvenilirdir. Uçlarda darbe eksene paralel ilerler, ray
    boyunca birden çok kırmızı parça görür ve genişlik ölçümü çöker.

    İLK DENEMEDEN ÖĞRENİLEN HATA
    Genişlik tek bir medyana sabitlenip uçlara sivrilme eklendi. Bu, ölçülen
    DEĞİŞKENLİĞİ — yani fırça darbesinin kendi karakterini — attı; sonuç
    silüet IoU 0.670, kaynağın %24'ü eksik, ve uçlarda saç teli dikenler.
    Şimdi her açının KENDİ ölçülen genişliği kullanılır; yalnızca güvenilmez
    sayılan açılar komşularından interpolasyonla onarılır.

ÇIKIŞ
    Düz çizgili çokgen YAPILMAZ (256 doğru segment 800%de belirgin yüzeyler
    üretti). Kutup örneklerinden Catmull-Rom ile kübik Bézier geçişi kurulur.

Görsel üretim çağrısı: 0.  Kanonikleştirme: YOK (insan onayı bekliyor).
"""
from __future__ import annotations

from pathlib import Path
import hashlib
import json
import math

ROOT = Path(__file__).resolve().parents[3]
RUN = ROOT / "brands/cin-egitim/explorations/enso"
SRC = Path("/private/var/folders/3j/ffljsl_s66n94xjq7zdv8hb80000gn/T/opencode/cinegitim-icon.png")

# Yalnızca BAŞLANGIÇ tahmini. Gerçek merkez aşağıda en küçük kare daire
# uydurmasıyla hesaplanır: kutu ortası bir KIRIK çemberde yanlıştır, çünkü
# boşluk kutuyu bir yana kaydırır (ölçüldü: 31.4 piksel yatay sapma).
CX0, CY0 = 303.5, 417.0
# Yay, kaynaktaki GERÇEK kırmızı sınırından türetildi; elle seçilmedi.
# Önceki 57°-313° yayının büyük kısmında kırmızı YOKTUR ve o 82 derece
# interpolasyonlanıyordu (tahmin). Işın taraması 65°-288° arasında kırmızı
# bulur, 288°'den sonra bulmaz. Bu düzeltme, kuru fırça dokusunu düşürme
# kararıyla da tutarlı: uçlardaki ibrisimler doku, jest değil.
ARC0 = (65.0, 288.0)
# Yay: 256° -> 223°. Gerçek ölçüm, 223°.
RED = "#A72820"
INK = "#292929"

MIN_RUN, MAX_RUN = 1, 4      # ray üzerindeki kırmızı parça sayısı
W_LO, W_HI = 20.0, 230.0     # makul genişlik aralığı (ölçümden)


def load_red_mask():
    from PIL import Image
    im = Image.open(SRC).convert("RGBA")
    W, H = im.size
    px = im.load()

    def isred(x, y):
        if x < 0 or y < 0 or x >= W or y >= H:
            return False
        r, g, b, a = px[x, y]
        return a > 60 and r - g > 45 and r - b > 35

    return isred


def measure(step_deg: float = 1.0, cx: float | None = None,
            cy: float | None = None, arc: tuple = ARC0):
    """Verilen merkez ve yay aralığında genişlik profili ölçer."""
    cx = CX0 if cx is None else cx
    cy = CY0 if cy is None else cy
    isred = load_red_mask()
    a0, a1 = arc
    samples = []
    prev_mid = None
    deg = a0
    while deg <= a1 + 1e-9:
        th = math.radians(deg)
        hits = []
        t = 20.0
        while t <= 620.0:
            if isred(int(cx + t * math.cos(th)), int(cy + t * math.sin(th))):
                hits.append(t)
            t += 0.5
        rec = {"deg": deg, "runs": 0, "mid": None, "width": None, "ok": False}
        if len(hits) >= 10:
            # Ray üzerindeki kırmızıyı kesintisiz parçalara böl ve EN UZUN
            # parçayı al. Yüzdelik (p20-p80) kullanmak darbeyi iki uçtan
            # kırpar ve halka sistematik olarak İNCE çıkar (ölçüldü: alan
            # 0.61). Genişlik, darbeye dik olduğu yerde tam sınırdır.
            runs_l, cur = [], [hits[0]]
            for i in range(1, len(hits)):
                if hits[i] - hits[i - 1] > 6.0:
                    runs_l.append(cur)
                    cur = [hits[i]]
                else:
                    cur.append(hits[i])
            runs_l.append(cur)
            main = (max(runs_l, key=len) if prev_mid is None else
                    min(runs_l, key=lambda r: abs((r[0] + r[-1]) / 2.0 - prev_mid)))
            lo, hi = main[0], main[-1]
            w = hi - lo
            prev_mid = (lo + hi) / 2.0
            rec.update({"runs": len(runs_l), "mid": prev_mid, "width": w,
                        "ok": MIN_RUN <= len(runs_l) <= MAX_RUN and W_LO <= w <= W_HI})
        else:
            prev_mid = None
        samples.append(rec)
        deg += step_deg
    return samples


def median(vals):
    s = sorted(vals)
    return s[len(s) // 2] if s else 0.0


def fit_circle(samples, cx, cy):
    """Darbe sınırlarından en küçük kare daire uydurur.

    Kutu ortası KULLANILAMAZ: enso kırık bir çemberdir, boşluk kutuyu bir yana
    kaydırır. İlk denemede kutu ortası alındı ve gerçek merkez 31.4 piksel
    kaymış çıktı; ölçülen IoU bunun yüzünden 0.885'te takıldı.
    """
    pts = []
    for s in samples:
        if not s["ok"]:
            continue
        th = math.radians(s["deg"])
        h = s["width"] / 2.0
        for r in (s["mid"] + h, s["mid"] - h):
            pts.append((cx + r * math.cos(th), cy + r * math.sin(th)))
    if len(pts) < 12:
        return cx, cy, 0.0
    Sx = Sy = Sxx = Syy = Sxy = Sxz = Syz = Sz = 0.0
    for x, y in pts:
        z = x * x + y * y
        Sx += x; Sy += y; Sxx += x * x; Syy += y * y; Sxy += x * y
        Sxz += x * z; Syz += y * z; Sz += z
    n = float(len(pts))
    M = [[Sxx, Sxy, Sx, Sxz], [Sxy, Syy, Sy, Syz], [Sx, Sy, n, Sz]]
    for i in range(3):
        p = max(range(i, 3), key=lambda r: abs(M[r][i]))
        M[i], M[p] = M[p], M[i]
        if abs(M[i][i]) < 1e-9:
            return cx, cy, 0.0
        for r in range(3):
            if r != i:
                f = M[r][i] / M[i][i]
                for c in range(i, 4):
                    M[r][c] -= f * M[i][c]
    a, b, k = (M[i][3] / M[i][i] for i in range(3))
    ncx, ncy = a / 2.0, b / 2.0
    return ncx, ncy, math.sqrt(max(1.0, k + ncx * ncx + ncy * ncy))


def reject_outliers(samples, mid_tol: float = 70.0):
    """Çalışma bandı dışına düşen ölçümleri güvenilmez sayar.

    Uç açılarda ray, darbeye dik değil EŞLEMEYE PARALEL ilerler; en uzun
    kesintisiz parça o zaman sivrilmenin kendisi olur ve yarıçap halka
    merkezinden uzaklaşır. Bu, konturda ince bir saç teli dikenine dönüşür.
    Referans medyan etrafında bant kontrolü bunları eler.
    """
    ok = [s for s in samples if s["width"] is not None and W_LO <= s["width"] <= W_HI]
    if not ok:
        return samples
    ref_mid = median([s["mid"] for s in ok])
    for s in samples:
        if s["mid"] is None:
            continue
        if abs(s["mid"] - ref_mid) > mid_tol:
            s["ok"] = False
            s["rejected"] = "mid-radius outside band"
    samples[0]["reference_mid_radius"] = round(ref_mid, 1)
    return samples


def interpolate_gaps(samples):
    """Güvenilmez açıları en yakın güvenilir iki komşudan doldurur."""
    n = len(samples)
    for i, s in enumerate(samples):
        if s["ok"]:
            continue
        lo = i - 1
        while lo >= 0 and not samples[lo]["ok"]:
            lo -= 1
        hi = i + 1
        while hi < n and not samples[hi]["ok"]:
            hi += 1
        if lo < 0 or hi >= n:
            # Uçtaki güvenilmez örnek: sivrilme olarak zorla kapat.
            s["mid"] = samples[hi if lo < 0 else lo]["mid"]
            s["width"] = 4.0
            s["ok"] = True
            s["filled"] = "taper"
            continue
        t = (i - lo) / (hi - lo)
        samples[i]["mid"] = samples[lo]["mid"] * (1 - t) + samples[hi]["mid"] * t
        samples[i]["width"] = samples[lo]["width"] * (1 - t) + samples[hi]["width"] * t
        samples[i]["ok"] = True
        samples[i]["filled"] = "interp"

    # Ardışık güvenilmez örnekler arka arkaya gelirse sivrilmeyi yumuşat:
    # en dıştaki güveniliz örneğe doğru daralt, ama asla sıfıra inmesin.
    widths = [s["width"] for s in samples]
    for i, s in enumerate(samples):
        if s.get("filled") == "taper":
            prev = widths[i - 1] if i else widths[i + 1]
            s["width"] = max(3.0, min(prev * 0.5, 30.0))
    return samples


def smooth_series(values, passes: int = 3, window: int = 3):
    """Yerel medyan yumuşatma: ölçüm gürültüsünü alır, karakteri korur.

    Pencere/GEÇİŞ DENEMESİ YAPILDI VE GERİ ALINDI. Varsayım, 800px'de sol altta
    görülen testere dişinin kuru fırça dokusu olduğuydu; daha geniş pencere onu
    silecek diye 6 kombinasyon ölçüldü (w3p3 … w9p13). Hiçbiri 59.5 piksellik
    sıçramayı kaldırmadı ve hepsi IoU'yu DÜŞÜRDÜ (0.8758 -> 0.8709).
    Yani sıçrama gürültü değil, kaynakta gerçekten var olan kalıcı bir özellik.
    w3 p3 korundu — ölçümle kazanan seçenek.
    """
    out = list(values)
    half = window // 2
    for _ in range(passes):
        nxt = list(out)
        for i in range(half, len(out) - half):
            nxt[i] = sorted(out[i - half:i + half + 1])[half]
        out = nxt
    return out


def build_profile(samples, arc):
    samples = interpolate_gaps(samples)
    degs = [s["deg"] for s in samples]
    mids = smooth_series([s["mid"] for s in samples])
    widths = smooth_series([max(3.0, s["width"]) for s in samples])

    # Sivrilme sıfıra İNMEZ. Ölçülen gövde kalınlığının bir oranına iner ve uç
    # düz/açılı bir kesmeyle kapanır. Sıfıra inen sivrilme + yumuşatma, uçları
    # kıvrık iğne teli hâline getiriyordu (800px denetiminde görüldü) ve
    # 16px'te leke oluyordu. Taban = medyanın %22'si.
    a0, a1 = arc
    span = a1 - a0
    fade = span * 0.10
    w_min = 0.22 * sorted(widths)[len(widths) // 2]
    prof = []
    for d, m, w in zip(degs, mids, widths):
        e = min((d - a0) / fade, (a1 - d) / fade, 1.0)
        e = max(0.0, e)
        k = e * e * (3 - 2 * e)                      # smoothstep
        prof.append({"deg": d, "mid": m, "width": w_min + (w - w_min) * k})

    measured = sum(1 for s in samples if not s.get("filled"))
    return {"arc": arc, "centre": None,
            "profile": prof,
            "angles_sampled": len(samples),
            "angles_measured_directly": measured,
            "angles_interpolated": len(samples) - measured,
            "median_width": round(sorted(p["width"] for p in prof)[len(prof) // 2], 1)}


def catmull_path(points, tension: float = 1.0):
    """Kapalı nokta dizisi üzerinden yumuşak kübik Bézier.

    Düz çokgen yerine geçiş eğrisi: 1°'lik örnekleme 800%de yüzey ve kenar
    üretiyordu.
    """
    n = len(points)
    d = [f"M{points[0][0]:.2f} {points[0][1]:.2f}"]

    def at(i):
        return points[i % n]

    for i in range(n):
        p0, p1, p2, p3 = at(i - 1), at(i), at(i + 1), at(i + 2)
        c1 = (p1[0] + (p2[0] - p0[0]) / 6.0 * tension,
              p1[1] + (p2[1] - p0[1]) / 6.0 * tension)
        c2 = (p2[0] - (p3[0] - p1[0]) / 6.0 * tension,
              p2[1] - (p3[1] - p1[1]) / 6.0 * tension)
        d.append(f"C{c1[0]:.2f} {c1[1]:.2f} {c2[0]:.2f} {c2[1]:.2f} "
                 f"{p2[0]:.2f} {p2[1]:.2f}")
    d.append("Z")
    return "".join(d)


def catmull_open(points, tension: float = 1.0):
    """AÇIK nokta dizisi üzerinden yumuşak kübik Bézier (uçlar sabitlenir)."""
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


def polar_to_path(prof):
    cx, cy = prof["centre"]
    outer, inner = [], []
    for s in prof["profile"]:
        th = math.radians(s["deg"])
        h = s["width"] / 2.0
        ro = s["mid"] + h
        ri = max(8.0, s["mid"] - h)
        outer.append((cx + ro * math.cos(th), cy + ro * math.sin(th)))
        inner.append((cx + ri * math.cos(th), cy + ri * math.sin(th)))

    # Uçlar KESKİN KALIR. Kapalı Catmull ile kurulmuş sürümde yumuşatma iki uç
    # kapağını da kapsıyordu; köşeler yuvarlayınca kapakları ince, kıvrık bir
    # tele dönüştürüyordu (800px'de görüldü: sağ üstte ve sağ altta iğne).
    # O yüzden dış kenar ileri yumuşatılır, düz çizgiyle kapatılır, iç kenar
    # geri yumuşatılır ve düz çizgiyle kapanır.
    # (İki ayrı alt yol + örtük kapanış da YANLIŞTIR: dış kontorun Z'si
    #  atılırsa renderer halkanın GÖVDESİNDEN geçen bir kordon kapatır.)
    d = [f"M{outer[0][0]:.2f} {outer[0][1]:.2f}"]
    d.append(catmull_open(outer[1:]))
    d.append(f"L{inner[-1][0]:.2f} {inner[-1][1]:.2f}")
    d.append(catmull_open(list(reversed(inner[1:-1])) or inner[-2::-1]))
    d.append("Z")
    return "".join(d)


def svg(path_d, colour, title, w=862, h=834):
    return (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {w} {h}" '
            f'width="{w}" height="{h}" role="img" aria-label="{title}">'
            f'<title>{title}</title><path d="{path_d}" fill="{colour}"/></svg>')


def main():
    RUN.mkdir(parents=True, exist_ok=True)
    src_sha = hashlib.sha256(SRC.read_bytes()).hexdigest()

    # DENEME YAPILDI VE GERİ ALINDI
    # Kutu ortası bir kırık çemberde teorik olarak yanlıştır; en küçük kare daire
    # uydurması merkezi yalnız 4.4/5.9 piksel kaydırdı (31 piksel sandığım
    # kayma, işlenmiş profil üzerinde yapılan ayrı bir denemeydi).
    # İki geçişli merkez + yay genişletmesi İoU'yu DÜŞÜRDÜ (0.8852 -> 0.8792)
    # ve boşluğun içine 82 derece interpolasyonlanmış geometri ekledi.
    # Kanıt: dört kombinasyon ölçüldü, en iyisi bu (tohum merkez + dar yay).
    s1 = reject_outliers(measure(1.0, CX0, CY0, ARC0))
    fitted = fit_circle(s1, CX0, CY0)

    arc = ARC0
    samples = reject_outliers(measure(1.0, CX0, CY0, arc))

    prof = build_profile(samples, arc)
    prof["centre"] = [CX0, CY0]
    prof["arc"] = arc
    prof["centre_fit"] = {
        "seed_used": [CX0, CY0],
        "least_squares_alternative": [round(fitted[0], 1), round(fitted[1], 1)],
        "alternative_offset_px": [round(fitted[0] - CX0, 1), round(fitted[1] - CY0, 1)],
        "decision": ("seed retained — the least-squares alternative and an "
                     "expanded arc both LOWERCED IoU (0.8852 -> 0.8792). "
                     "Tested, not assumed."),
    }
    prof["source"] = {"file": SRC.name, "sha256": src_sha, "size": [862, 834]}
    prof["design_decision"] = (
        "Painterly dry-brush gaps and paper grain are deliberately dropped: "
        "they cannot survive 16 px or one-colour production. Only the gesture "
        "is kept — open arc, measured variable width, tapered ends.")
    prof["texture_policy"] = "dropped (by decision)"

    d = polar_to_path(prof)
    (RUN / "enso-profile.json").write_text(json.dumps(prof, indent=1), encoding="utf-8")
    (RUN / "enso-reconstruction.svg").write_text(svg(d, RED, "enso"), encoding="utf-8")
    (RUN / "enso-reconstruction-mono.svg").write_text(
        svg(d, INK, "enso — monochrome"), encoding="utf-8")

    print(json.dumps({
        "source_sha256": src_sha,
        "centre": [CX0, CY0],
        "centre_alternative_tested": [round(fitted[0], 1), round(fitted[1], 1)],
        "arc_degrees": [round(arc[0], 1), round(arc[1], 1)],
        "arc_sweep_degrees": round(arc[1] - arc[0], 1),
        "angles_sampled": prof["angles_sampled"],
        "measured_directly": prof["angles_measured_directly"],
        "interpolated": prof["angles_interpolated"],
        "median_stroke_width": prof["median_width"],
        "path_commands": d.count("C") + d.count("L"),
        "straight_segments": d.count("L"),
        "canonicalised": 0,
        "status": "HUMAN REVIEW PENDING",
    }, indent=2))


if __name__ == "__main__":
    main()