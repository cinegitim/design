#!/usr/bin/env python3
"""Çin Eğitim — sadeleştirilmiş iç kurgu: çadır + zemin, silüet İZLEME.

NEDEN İZLEME, NEDEN KURGU
    İki nesne iki farklı yöntem ister ve bu, geometriden gelir:
      * Enso  -> değişken genişlikli fırça darbesi. Radyal ölçüm + yeniden
        kurulum doğru yöntem; kuru fırça dokusu düşürüldü.
      * Çadır + zemin -> düz SİLÜETler. Sınırları temiz, içleri boş. Bunları
        elle kurgulamak yapıyı bozdu (bkz. karar kaydı 2026-10-08-…-rejected);
        izlemek doğrudur.
    Asya'da Eğitim'in de kaydı aynı sonuca varıyor: yumuşatma hattı ölçümü
    iyileştirdi ama görsel olarak kötüleştirdi.

SADELEŞTİRME OTOMATİK
    Maske yalnız koyu (charcoal) pikseli alır:
      - uzak dağ silsilesi açık gri  -> maskeye giremez
      - kuş sürüsü kırmızı           -> maskeye giremez
    Böylece pano sadeliği elle uygulanmaz, verinin kendisi uygular.

YÖNTEM
    Moore komşuluk sınır izleme -> kapalı kontur -> Douglas-Peucker sadeleştirme.
    Dış sınır + delikler ayrı ayrı izlenir.

Görsel üretim çağrısı: 0.  Kanonikleştirme: YOK.
"""
from __future__ import annotations

from pathlib import Path
import hashlib
import json
import re

ROOT = Path(__file__).resolve().parents[3]
RUN = ROOT / "brands/cin-egitim/explorations/enso"
SRC = Path("/private/var/folders/3j/ffljsl_s66n94xjq7zdv8hb80000gn/T/opencode/cinegitim-icon.png")
INK = "#292929"
RED = "#A72820"

# Taranacak bölge: ölçülmüş zarf + pay (koyu piksel 70688 toplam)
REGION = (150, 300, 740, 780)      # x0, y0, x1, y1


def load_mask():
    from PIL import Image
    im = Image.open(SRC).convert("RGB")
    W, H = im.size
    px = im.load()
    x0, y0, x1, y1 = REGION
    w, h = x1 - x0 + 1, y1 - y0 + 1
    mask = bytearray(w * h)

    def solid(x, y):
        if x < 0 or y < 0 or x >= W or y >= H:
            return 0
        r, g, b = px[x, y]
        # Koyu nötr piksel. Kırmızı (r-g>45) ve açık gri (max>95) dışarıda.
        return 1 if (max(r, g, b) < 105 and abs(r - g) < 32 and abs(g - b) < 32) else 0

    for j in range(h):
        for i in range(w):
            mask[j * w + i] = solid(x0 + i, y0 + j)
    return mask, w, h, (x0, y0)


def trace_boundary(mask, w, h, start):
    """Moore komşuluk izleme: kapalı dış sınırı sıralı noktalar olarak verir."""
    NB = [(-1, 0), (-1, -1), (0, -1), (1, -1), (1, 0), (1, 1), (0, 1), (-1, 1)]

    def on(i, j):
        return 0 <= i < w and 0 <= j < h and mask[j * w + i] == 1

    cur = start
    # Başlangıç yönü: sola bak (yukarıdan gelen ilk piksel).
    prev_dir = 6                       # (0,1) -> aşağı; tarama soldan sağa
    contour = [cur]
    for _ in range(400000):
        i, j = cur
        found = False
        for k in range(8):
            d = (prev_dir + 1 + k) % 8
            ni, nj = i + NB[d][0], j + NB[d][1]
            if on(ni, nj):
                prev_dir = (d + 4) % 8   # geldiğimiz yön
                cur = (ni, nj)
                found = True
                break
        if not found:
            break
        if cur == start and len(contour) > 2:
            contour.append(cur)
            break
        contour.append(cur)
    return contour


def trace_all(mask, w, h):
    """Tüm ayrık bileşenlerin dış sınırlarını izler."""
    seen = bytearray(w * h)
    out = []
    for j in range(h):
        for i in range(w):
            if mask[j * w + i] and not seen[j * w + i]:
                # Bu bileşenin tohum pikseli: en üst, solda
                start = None
                jj, ii = j, i
                while jj < h:
                    k = seen[jj * w + ii] if (ii < w) else 0
                    if mask[jj * w + ii] and not seen[jj * w + ii]:
                        start = (ii, jj)
                        break
                    ii += 1
                    if ii >= w:
                        break
                    jj += 1
                if start is None:
                    continue
                c = trace_boundary(mask, w, h, start)
                for (a, b) in c:
                    seen[b * w + a] = 1
                if len(c) > 40:
                    out.append(c)
    return out


def rdp(points, eps: float):
    """Douglas-Peucker."""
    if len(points) < 3:
        return points
    ax, ay = points[0]
    bx, by = points[-1]
    dx, dy = bx - ax, by - ay
    nrm = (dx * dx + dy * dy) ** 0.5
    best, bi = -1.0, 0
    for k in range(1, len(points) - 1):
        px, py = points[k]
        if nrm < 1e-9:
            d = ((px - ax) ** 2 + (py - ay) ** 2) ** 0.5
        else:
            d = abs(dy * (px - ax) - dx * (py - ay)) / nrm
        if d > best:
            best, bi = d, k
    if best <= eps:
        return [points[0], points[-1]]
    return rdp(points[:bi + 1], eps)[:-1] + rdp(points[bi:], eps)


def contours_to_path(contours, ox, oy, eps=1.1, min_area=260):
    parts = []
    for c in contours:
        pts = [(i + ox, j + oy) for (i, j) in c]
        if len(pts) < 12:
            continue
        s = rdp(pts, eps)
        if len(s) < 4:
            continue
        area = abs(sum(s[i][0] * s[i + 1][1] - s[i + 1][0] * s[i][1]
                       for i in range(len(s) - 1))) / 2.0
        if area < min_area:
            continue
        d = ["M%.1f %.1f" % s[0]]
        for p in s[1:]:
            d.append("L%.1f %.1f" % p)
        d.append("Z")
        parts.append((area, "".join(d)))
    parts.sort(key=lambda t: -t[0])
    return [p[1] for p in parts]


def main() -> None:
    RUN.mkdir(parents=True, exist_ok=True)
    mask, w, h, (ox, oy) = load_mask()
    src_sha = hashlib.sha256(SRC.read_bytes()).hexdigest()

    contours = trace_all(mask, w, h)
    paths = contours_to_path(contours, ox, oy)
    interior = "".join(paths)

    enso = re.search(r'<path[^>]*/>',
                     (RUN / "enso-reconstruction.svg").read_text(encoding="utf-8")).group(0)
    enso_d = re.search(r'd="([^"]+)"', enso).group(1)

    def doc(enso_fill: str, title: str) -> str:
        return (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 862 834" '
                f'width="862" height="834" role="img" aria-label="{title}">'
                f'<title>{title}</title>'
                f'<path d="{enso_d}" fill="{enso_fill}"/>'
                f'<path d="{interior}" fill="{INK}"/></svg>')

    (RUN / "simplified-mark.svg").write_text(doc(RED, "Çin Eğitim — sadeleştirilmiş mark"), encoding="utf-8")
    (RUN / "simplified-mark-mono.svg").write_text(
        doc(INK, "Çin Eğitim — sadeleştirilmiş mark, tek renk"), encoding="utf-8")

    total = sum(1 for v in mask if v)
    verts = interior.count("L")
    (RUN / "interior-path.json").write_text(json.dumps({
        "source_sha256": src_sha,
        "region": REGION,
        "dark_pixels_in_region": total,
        "contours": len(paths),
        "path_vertices": verts,
        "method": ("Moore-neighbourhood boundary trace + Douglas-Peucker "
                   "(eps %.2f px). Light-grey distant ridges and red birds are "
                   "excluded by the mask itself, so the board's simplification "
                   "is applied by the data, not by hand." % 1.1),
        "excluded_automatically": ["uzak dağ silsilesi (açık gri)",
                                   "kuş sürüsü (kırmızı)"],
        "image_generation_calls": 0,
        "canonicalised": 0,
    }, indent=1, ensure_ascii=False), encoding="utf-8")

    print(json.dumps({"contours": len(paths), "path_vertices": verts,
                      "dark_pixels_in_region": total,
                      "outputs": [f"{RUN.name}/simplified-mark.svg",
                                  f"{RUN.name}/simplified-mark-mono.svg"],
                      "canonicalised": 0}, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()