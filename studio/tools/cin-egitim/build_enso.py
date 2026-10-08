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

CX, CY = 303.5, 417.0        # kutu türetmesinden
ARC = (57.0, 313.0)          # ana yay, derece (ölçüldü)
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


def measure(step_deg: float = 1.0):
    isred = load_red_mask()
    a0, a1 = ARC
    samples = []
    deg = a0
    while deg <= a1 + 1e-9:
        th = math.radians(deg)
        hits = []
        t = 40.0
        while t <= 540.0:
            if isred(int(CX + t * math.cos(th)), int(CY + t * math.sin(th))):
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
            main = max(runs_l, key=len)
            lo, hi = main[0], main[-1]
            w = hi - lo
            rec.update({"runs": len(runs_l), "mid": (lo + hi) / 2.0, "width": w,
                        "ok": MIN_RUN <= len(runs_l) <= MAX_RUN and W_LO <= w <= W_HI})
        samples.append(rec)
        deg += step_deg
    return samples


def median(vals):
    s = sorted(vals)
    return s[len(s) // 2] if s else 0.0


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


def smooth_series(values, passes: int = 3):
    """Yerel medyan yumuşatma: ölçüm gürültüsünü alır, karakteri korur."""
    out = list(values)
    for _ in range(passes):
        nxt = list(out)
        for i in range(1, len(out) - 1):
            trio = sorted(out[i - 1:i + 2])
            nxt[i] = trio[1]
        out = nxt
    return out


def build_profile(samples):
    samples = interpolate_gaps(samples)
    degs = [s["deg"] for s in samples]
    mids = smooth_series([s["mid"] for s in samples])
    widths = smooth_series([max(3.0, s["width"]) for s in samples])

    # Uçlarda genişliği sıfıra indirerek gerçek bir sivrilme kur. Sivrilme
    # yalnız en dış %8'de uygulanır; gövde ölçülen değerinde kalır.
    a0, a1 = ARC
    span = a1 - a0
    fade = span * 0.08
    prof = []
    for d, m, w in zip(degs, mids, widths):
        e = min((d - a0) / fade, (a1 - d) / fade, 1.0)
        e = max(0.0, e)
        k = e * e * (3 - 2 * e)                      # smoothstep
        prof.append({"deg": d, "mid": m, "width": max(2.5, w * k)})

    measured = sum(1 for s in samples if not s.get("filled"))
    return {"arc": ARC, "centre": [CX, CY],
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

    # Tek KAPALI döngü kurulur: dış kenar ileri → uç kapağı → iç kenar geri →
    # başlangıç kapağı. İki ayrı alt yol + örtük kapanış YANLIŞTIR: dış
    # kontorun Z'si atılırsa renderer 313°'den 57°'ye halkanın GÖVDESİNDEN
    # geçen bir kordon kapatır ve gap'i ince bir dikene çevirir (görüldü).
    loop = outer + list(reversed(inner))
    return catmull_path(loop)


def svg(path_d, colour, title, w=862, h=834):
    return (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {w} {h}" '
            f'width="{w}" height="{h}" role="img" aria-label="{title}">'
            f'<title>{title}</title><path d="{path_d}" fill="{colour}"/></svg>')


def main():
    RUN.mkdir(parents=True, exist_ok=True)
    src_sha = hashlib.sha256(SRC.read_bytes()).hexdigest()

    samples = measure(1.0)
    samples = reject_outliers(samples)
    prof = build_profile(samples)
    prof["arc"] = ARC
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
        "arc_sweep_degrees": round(prof["arc"][1] - prof["arc"][0], 1),
        "centre": prof["centre"],
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