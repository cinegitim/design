#!/usr/bin/env python3
"""Build editable SVG + HTML slide sources for the Tsinghua V2 review bundle."""

from __future__ import annotations

import html
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent
PAPER = "#F7F3E9"
INK = "#1D2027"
RED = "#BD2120"
STONE = "#E9E3D6"
MUTED = "#6C675F"
WHITE = "#FFFFFF"
SEAL_SHA = "8f5d46f0302c4cc7e3765d3bfce9445f842dbd92f1e0f8fbe99f9f509c77e11a"


def tx(copy, x, y, value, size, fill=INK, weight=500, anchor="start", spacing=0, opacity=None):
    copy.append(value)
    alpha = f' opacity="{opacity}"' if opacity is not None else ""
    return (
        f'<text x="{x}" y="{y}" fill="{fill}" font-size="{size}" '
        f'font-weight="{weight}" text-anchor="{anchor}" letter-spacing="{spacing}"{alpha}>'
        f"{html.escape(value)}</text>"
    )


def rect(x, y, width, height, fill, rx=0, opacity=None, extra=""):
    alpha = f' opacity="{opacity}"' if opacity is not None else ""
    return f'<rect x="{x}" y="{y}" width="{width}" height="{height}" fill="{fill}" rx="{rx}"{alpha} {extra}/>'


def rule(x1, y1, x2, y2, stroke=INK, width=2, opacity=None):
    alpha = f' opacity="{opacity}"' if opacity is not None else ""
    return f'<path d="M{x1} {y1}H{x2}" fill="none" stroke="{stroke}" stroke-width="{width}"{alpha}/>'


def image(href, x, y, width, height, extra=""):
    return (
        f'<image href="../assets/{href}" x="{x}" y="{y}" width="{width}" height="{height}" '
        f'preserveAspectRatio="xMidYMid slice" {extra}/>'
    )


def icon(kind, x, y, size=58):
    """Small, consistent, subject-specific line icons; no icon is used as decoration alone."""
    common = f'transform="translate({x} {y}) scale({size / 64:.4f})" fill="none" stroke="{RED}" stroke-width="2.6" stroke-linecap="round" stroke-linejoin="round"'
    forms = {
        "environment": '<path d="M12 48c0-21 17-35 40-35-1 23-14 40-35 40"/><path d="M14 51c9-13 19-21 33-29"/><path d="M32 38c-1-8-5-13-11-17"/>',
        "civil": '<path d="M8 51h48M14 51V32m36 19V32M14 32c10-19 26-19 36 0M18 32h28M21 32v19m11-19v19m11-19v19"/><path d="M6 56h52"/>',
        "architecture": '<path d="M8 54h48M13 54V24h38v30M20 24V12h24v12M22 32h7v8h-7zm13 0h7v8h-7zM27 54V43h10v11"/><path d="m8 24 24-12 24 12"/>',
        "materials": '<path d="m32 7 22 12v26L32 58 10 45V19L32 7Z"/><path d="m10 19 22 13 22-13M32 32v26M21 13l22 13M43 13 21 26"/>',
        "data": '<circle cx="14" cy="14" r="5"/><circle cx="50" cy="14" r="5"/><circle cx="32" cy="32" r="5"/><circle cx="14" cy="50" r="5"/><circle cx="50" cy="50" r="5"/><path d="m19 17 9 11m17-11-9 11M19 47l9-11m17 11-9-11M19 14h26M19 50h26"/>',
        "chemical": '<path d="M24 8h16M28 8v18L15 49a5 5 0 0 0 4 7h26a5 5 0 0 0 4-7L36 26V8"/><path d="M21 44h22M26 38h14"/><circle cx="29" cy="46" r="1.5" fill="#BD2120"/><circle cx="38" cy="41" r="1.5" fill="#BD2120"/>',
    }
    return f'<g {common}>{forms[kind]}</g>'


def svg_wrap(copy, background, artwork, logo_id, logo_file, logo_x, logo_y, logo_width, logo_height):
    data = html.escape(json.dumps(copy, ensure_ascii=False, separators=(",", ":")), quote=True)
    group = f'<g id="editable-campaign-copy" data-exact-copy-json="{data}">{artwork}</g>'
    logo = (
        f'<image id="canonical-lockup" data-canonical-lockup-id="{logo_id}" data-canonical-seal-sha256="{SEAL_SHA}" href="../assets/{logo_file}" x="{logo_x}" y="{logo_y}" '
        f'width="{logo_width}" height="{logo_height}" preserveAspectRatio="xMidYMid meet"/>'
    )
    return f'''<svg xmlns="http://www.w3.org/2000/svg" width="1080" height="1350" viewBox="0 0 1080 1350" role="img">
<defs>
  <linearGradient id="photo-dark" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="{INK}" stop-opacity=".26"/><stop offset=".58" stop-color="{INK}" stop-opacity=".34"/><stop offset="1" stop-color="{INK}" stop-opacity=".92"/></linearGradient>
  <linearGradient id="photo-left-shade" x1="0" y1="0" x2="1" y2="0"><stop offset="0" stop-color="{INK}" stop-opacity=".96"/><stop offset=".54" stop-color="{INK}" stop-opacity=".77"/><stop offset="1" stop-color="{INK}" stop-opacity=".24"/></linearGradient>
  <linearGradient id="photo-top-shade" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="{INK}" stop-opacity=".78"/><stop offset="1" stop-color="{INK}" stop-opacity=".22"/></linearGradient>
  <style>@font-face{{font-family:Jost;src:url('../assets/Jost-VF.ttf') format('truetype');font-weight:100 900;font-display:block}} text{{font-family:Jost,Arial,sans-serif}}</style>
</defs>
{rect(0, 0, 1080, 1350, background)}
{group}
{logo}
</svg>'''


def make_slide1():
    c, a = [], []
    a += [image("main-building.jpg", 0, 0, 1080, 950), rect(0, 0, 1080, 950, "url(#photo-dark)")]
    a.append(tx(c, 72, 86, "TSINGHUA · ÜNİVERSİTE ATLASI", 23, WHITE, 700, spacing=2.2))
    a.append(tx(c, 1008, 86, "01 / 07", 22, WHITE, 650, anchor="end", spacing=1.4))
    a.append(tx(c, 72, 490, "Tsinghua", 142, WHITE, 750, spacing=-5.5))
    a.append(tx(c, 77, 588, "Üniversitesi", 88, WHITE, 550, spacing=-2.4))
    a.append(rect(72, 660, 7, 96, RED))
    a.append(tx(c, 106, 700, "2027 LİSANS BAŞVURU REHBERİ", 28, WHITE, 700, spacing=1.0))
    a.append(tx(c, 106, 742, "PEKİN’DE KÜRESEL ÖLÇEKTE BİR AKADEMİK EKOSİSTEM.", 23, WHITE, 500))
    a.append(rect(0, 930, 1080, 420, PAPER))
    a.append(rule(72, 930, 1008, 930, RED, 8))
    a.append(tx(c, 532, 1060, "SIRALAMALAR · PROGRAMLAR", 24, INK, 700, spacing=1.0))
    a.append(tx(c, 532, 1110, "BAŞVURU TAKVİMİ · ÜCRET · BURS", 24, INK, 600, spacing=.3))
    return svg_wrap(c, PAPER, "".join(a), "P-01/light", "p-01-light.svg", 72, 956, 376, 369.6658132676)


SUBJECTS = [
    ("=7", "Çevre", "Bilimleri", "environment"),
    ("8", "İnşaat ve Yapı", "Mühendisliği", "civil"),
    ("9", "Mimarlık ve", "Yapılı Çevre", "architecture"),
    ("9", "Malzeme", "Bilimleri", "materials"),
    ("10", "Veri Bilimi ve", "Yapay Zekâ", "data"),
    ("10", "Kimya", "Mühendisliği", "chemical"),
]


def make_slide2():
    c, a = [], []
    a.append(rect(0, 0, 1080, 1350, PAPER))
    a.append(tx(c, 72, 74, "02 · QS ALAN SIRALAMALARI", 21, RED, 700, spacing=1.6))
    a.append(tx(c, 1008, 74, "2026", 22, INK, 700, anchor="end", spacing=1.3))
    a.append(tx(c, 72, 185, "Altı alanda", 82, INK, 650, spacing=-3.3))
    a.append(tx(c, 72, 278, "ilk 10’da.", 84, RED, 700, spacing=-3.7))
    a.append(image("chemistry-building.jpg", 744, 102, 264, 236))
    a.append(rect(744, 302, 264, 36, INK, opacity=.88))
    a.append(tx(c, 758, 328, "KİMYA BİNASI · TSINGHUA", 17, WHITE, 650, spacing=.6))
    a.append(tx(c, 72, 374, "DÜNYA SIRALAMASI · QS 2026", 22, MUTED, 700, spacing=1.2))
    for i, (rank, line1, line2, icon_name) in enumerate(SUBJECTS):
        col, row = i % 2, i // 2
        x = 72 + col * 482
        y = 418 + row * 210
        a.append(rule(x, y, x + 450, y, INK, 2, .58))
        a.append(icon(icon_name, x + 105, y + 56, 58))
        a.append(tx(c, x + 18, y + 126, rank, 70, RED, 700, spacing=-2.0))
        a.append(tx(c, x + 188, y + 93, line1, 26, INK, 600))
        a.append(tx(c, x + 188, y + 128, line2, 26, INK, 600))
        a.append(tx(c, x + 18, y + 178, f"0{i + 1}", 18, MUTED, 700, spacing=1.1))
    a.append(tx(c, 318, 1160, "QS World University Rankings by Subject · Dünya sıralaması", 20, MUTED, 500))
    return svg_wrap(c, PAPER, "".join(a), "D-04/light", "d-04-light.svg", 72, 1235, 220, 84.2212131892)


def make_slide3():
    c, a = [], []
    a.append(image("grand-auditorium.jpg", 0, 0, 1080, 585))
    a.append(rect(0, 0, 1080, 585, "url(#photo-top-shade)"))
    a.append(rect(0, 0, 1080, 585, INK, opacity=.20))
    a.append(tx(c, 72, 78, "03 · KÜRESEL SIRALAMALAR", 22, WHITE, 700, spacing=1.6))
    a.append(tx(c, 1008, 78, "2027", 22, WHITE, 700, anchor="end", spacing=1.4))
    a.append(tx(c, 72, 288, "Bir üniversite.", 88, WHITE, 650, spacing=-3.5))
    a.append(tx(c, 72, 390, "Üç küresel ölçüt.", 82, WHITE, 650, spacing=-3.4))
    a.append(tx(c, 72, 468, "Farklı metodolojiler · ayrı edisyonlar", 26, WHITE, 500))
    cards = [
        ("#14", "QS", "World University", "Rankings", "2027"),
        ("#11", "THE", "World University", "Rankings", "2027"),
        ("#6", "U.S. News", "Best Global", "Universities", "2026–2027"),
    ]
    for i, (rank, source, line1, line2, year) in enumerate(cards):
        x = 72 + i * 318
        a.append(rect(x, 625, 292, 466, PAPER, rx=4))
        a.append(rect(x, 625, 292, 9, RED))
        a.append(tx(c, x + 26, 770, rank, 110, RED, 700, spacing=-4.5))
        a.append(tx(c, x + 28, 837, source, 30, INK, 750, spacing=.7))
        a.append(tx(c, x + 28, 890, line1, 26, INK, 500))
        a.append(tx(c, x + 28, 925, line2, 26, INK, 500))
        a.append(rule(x + 28, 966, x + 264, 966, INK, 1, .45))
        a.append(tx(c, x + 28, 1027, year, 27, INK, 650))
    a.append(tx(c, 72, 1165, "Sıralamalar farklı metodolojiler kullanır; doğrudan birbirinin yerine geçmez.", 21, PAPER, 500))
    return svg_wrap(c, INK, "".join(a), "D-04/dark", "d-04-dark.svg", 72, 1235, 220, 84.2212131892)


def make_slide4():
    c, a = [], []
    a.append(rect(0, 0, 380, 1350, INK))
    a.append(image("old-library.jpg", 0, 0, 380, 1350))
    a.append(rect(0, 0, 380, 1350, INK, opacity=.28))
    a.append(rect(380, 0, 700, 1350, PAPER))
    a.append(rect(380, 0, 12, 1350, RED))
    a.append(tx(c, 34, 1286, "ESKİ KÜTÜPHANE · TSINGHUA", 18, WHITE, 700, spacing=.7))
    a.append(tx(c, 438, 74, "04 · PROGRAMLAR + DİL", 20, RED, 700, spacing=1.2))
    a.append(tx(c, 438, 165, "İngilizce", 76, INK, 650, spacing=-3.2))
    a.append(tx(c, 438, 246, "& HSK", 76, RED, 700, spacing=-3.0))
    a.append(tx(c, 438, 295, "2027’DE DUYURULAN ÜÇ TAMAMEN İNGİLİZCE LİSANS PROGRAMI", 18, MUTED, 700, spacing=.1))
    rows = [
        ("01", "Global Talents in Science", "and Engineering"),
        ("02", "Urban Regeneration", "and Design"),
        ("03", "Politics, Economics and Sociology", "for Global Leaders in Smart Society"),
    ]
    for i, (n, line1, line2) in enumerate(rows):
        y = 362 + i * 112
        a.append(rule(438, y, 1028, y, INK, 1, .45))
        a.append(tx(c, 444, y + 45, n, 21, RED, 700, spacing=1.1))
        a.append(tx(c, 500, y + 43, line1, 24, INK, 600))
        a.append(tx(c, 500, y + 75, line2, 24, INK, 600))
    a.append(rect(438, 724, 590, 256, INK, rx=3))
    a.append(rect(438, 724, 9, 256, RED))
    a.append(tx(c, 474, 770, "ÇİNCE–İNGİLİZCE PROGRAMLAR", 20, PAPER, 700, spacing=.9))
    a.append(tx(c, 474, 854, "HSK 5+", 65, PAPER, 700, spacing=-2.2))
    a.append(tx(c, 474, 899, "Dinleme, Okuma ve Yazma puanlarının", 22, PAPER, 550))
    a.append(tx(c, 474, 934, "her biri 60’ın üzerinde olmalı.", 22, PAPER, 550))
    a.append(tx(c, 438, 1025, "TAMAMEN İNGİLİZCE PROGRAMLARDA", 19, RED, 700, spacing=.2))
    a.append(tx(c, 438, 1053, "ÇİNCE YETERLİLİK KANITI GEREKMEZ.", 19, RED, 700, spacing=.2))
    a.append(tx(c, 438, 1100, "Ana dili İngilizce olmayanlar resmî", 21, INK, 500))
    a.append(tx(c, 438, 1134, "İngilizce sınav sonucu sunmalıdır.", 21, INK, 500))
    a.append(tx(c, 438, 1168, "TOEFL / IELTS gibi sonuçlar kabul edilir.", 21, INK, 500))
    return svg_wrap(c, PAPER, "".join(a), "D-04/light", "d-04-light.svg", 438, 1238, 220, 84.2212131892)


def make_slide5():
    c, a = [], []
    a.append(image("quantum-information-center.jpg", 0, 0, 1080, 565))
    a.append(rect(0, 0, 1080, 565, "url(#photo-top-shade)"))
    a.append(rect(0, 0, 1080, 565, INK, opacity=.24))
    a.append(tx(c, 72, 78, "05 · 2027 BAŞVURU TAKVİMİ", 22, WHITE, 700, spacing=1.5))
    a.append(tx(c, 1008, 78, "PEKİN SAATİ", 20, WHITE, 700, anchor="end", spacing=1.0))
    a.append(tx(c, 72, 265, "Takvimini", 96, WHITE, 650, spacing=-3.6))
    a.append(tx(c, 72, 364, "işaretle.", 92, WHITE, 650, spacing=-3.8))
    a.append(rule(72, 605, 1008, 605, RED, 5))
    a.append(rule(540, 650, 540, 1033, RED, 2, .75))
    deadlines = [
        (72, "1. TUR · KAPANIŞ", "20", "KASIM", "2026"),
        (586, "2. TUR · KAPANIŞ", "28", "ŞUBAT", "2027"),
    ]
    for x, label, day, month, year in deadlines:
        a.append(tx(c, x, 681, label, 22, PAPER, 700, spacing=1.0))
        a.append(tx(c, x, 866, day, 176, PAPER, 700, spacing=-7.5))
        a.append(tx(c, x + 250, 835, month, 34, PAPER, 700, spacing=.7))
        a.append(tx(c, x + 250, 879, year, 32, PAPER, 550, spacing=.8))
        a.append(tx(c, x, 955, "17.00 · PEKİN SAATİ", 25, PAPER, 600, spacing=.5))
    a.append(tx(c, 72, 1088, "Bazı programlar yalnızca belirli turda açıktır; güncel program kılavuzunu kontrol edin.", 21, PAPER, 500))
    return svg_wrap(c, INK, "".join(a), "D-04/dark", "d-04-dark.svg", 72, 1238, 220, 84.2212131892)


def make_slide6():
    c, a = [], []
    a.append(rect(0, 0, 1080, 1350, PAPER))
    a.append(tx(c, 72, 74, "06 · ÜCRET + BURS", 20, RED, 700, spacing=1.5))
    a.append(tx(c, 1008, 74, "RMB", 21, INK, 700, anchor="end", spacing=1.2))
    a.append(tx(c, 72, 178, "Ücretler ve burslar", 78, INK, 650, spacing=-3.1))
    a.append(tx(c, 72, 230, "Öğrenim ücreti programa göre değişir.", 27, MUTED, 500))
    cards = [
        (72, STONE, INK, RED, "SEÇİLİ ÇİNCE–İNGİLİZCE", "PROGRAMLAR", "¥30.000", "/ YIL · ÖĞRENİM ÜCRETİ"),
        (558, INK, PAPER, PAPER, "GLOBAL TALENTS IN", "SCIENCE & ENGINEERING", "¥100.000", "/ YIL · ÖĞRENİM ÜCRETİ"),
    ]
    for x, bg, fg, accent, l1, l2, amount, suffix in cards:
        a.append(rect(x, 292, 450, 316, bg, rx=3))
        a.append(tx(c, x + 28, 340, l1, 19, fg, 700, spacing=.8))
        a.append(tx(c, x + 28, 375, l2, 19, fg, 700, spacing=.8))
        a.append(tx(c, x + 28, 492, amount, 66, accent, 700, spacing=-2.6))
        a.append(tx(c, x + 28, 552, suffix, 20, fg, 600, spacing=.5))
    a.append(rect(72, 654, 936, 356, RED, rx=3))
    a.append(tx(c, 104, 820, "~45%", 120, PAPER, 700, spacing=-5.5))
    a.append(tx(c, 490, 728, "2026’DA ULUSLARARASI LİSANS", 21, PAPER, 700, spacing=.7))
    a.append(tx(c, 490, 766, "BİRİNCİ SINIF ÖĞRENCİLERİ", 21, PAPER, 700, spacing=.7))
    a.append(tx(c, 490, 818, "Tsinghua International Undergraduate", 22, PAPER, 600))
    a.append(tx(c, 490, 851, "Freshmen Scholarship aldı.", 22, PAPER, 600))
    a.append(tx(c, 490, 894, "Tam, yarım ve kısmi öğrenim ücreti", 22, PAPER, 500))
    a.append(tx(c, 490, 927, "bursları var; oran garanti değildir.", 22, PAPER, 500))
    a.append(rule(72, 1072, 1008, 1072, INK, 2, .5))
    a.append(tx(c, 72, 1126, "BAŞVURU ÜCRETİ", 19, MUTED, 700, spacing=.8))
    a.append(tx(c, 72, 1170, "¥800", 34, INK, 700))
    a.append(tx(c, 552, 1126, "SAĞLIK SİGORTASI", 19, MUTED, 700, spacing=.8))
    a.append(tx(c, 552, 1170, "¥800 / yıl", 34, INK, 700))
    a.append(tx(c, 335, 1292, "~%45 oranı 2026 kohortuna aittir; bireysel burs garantisi değildir.", 18, MUTED, 500))
    return svg_wrap(c, PAPER, "".join(a), "D-04/light", "d-04-light.svg", 72, 1239, 220, 84.2212131892)


def make_slide7():
    c, a = [], []
    a.append(image("campus-sport.jpg", 0, 0, 1080, 1350))
    a.append(rect(0, 0, 1080, 1350, "url(#photo-left-shade)"))
    a.append(rect(0, 0, 1080, 1350, INK, opacity=.18))
    a.append(tx(c, 72, 506, "Başvuru rotanı", 71, PAPER, 650, spacing=-2.7))
    a.append(tx(c, 72, 594, "birlikte çizelim.", 73, PAPER, 700, spacing=-3.2))
    a.append(rect(72, 660, 96, 7, RED))
    a.append(tx(c, 72, 728, "Tsinghua 2027 lisans başvurusunu", 28, PAPER, 500))
    a.append(tx(c, 72, 770, "adım adım değerlendirelim.", 28, PAPER, 500))
    a.append(rect(72, 838, 452, 86, RED, rx=2))
    a.append(tx(c, 298, 892, "ÖN GÖRÜŞMENİ PLANLA  ↗", 24, WHITE, 700, anchor="middle", spacing=.4))
    return svg_wrap(c, INK, "".join(a), "P-01/dark", "p-01-dark.svg", 72, 70, 360, 353.9353531285)


SLIDE_BUILDERS = [make_slide1, make_slide2, make_slide3, make_slide4, make_slide5, make_slide6, make_slide7]
SLIDE_IDS = [
    "01-cover",
    "02-subject-rankings",
    "03-global-rankings",
    "04-english-hsk",
    "05-deadlines",
    "06-tuition-scholarships",
    "07-cta",
]


def main():
    source = ROOT / "source"
    source.mkdir(parents=True, exist_ok=True)
    all_copy = {}
    for index, (slide_id, builder) in enumerate(zip(SLIDE_IDS, SLIDE_BUILDERS), 1):
        svg = builder()
        copy = []
        # The builder returns SVG; the exact visible copy is encoded in its single editable group.
        import xml.etree.ElementTree as ET

        tree = ET.fromstring(svg)
        group = next(e for e in tree.iter() if e.get("id") == "editable-campaign-copy")
        copy = [e.text or "" for e in group.iter() if e.tag.endswith("text")]
        all_copy[slide_id] = copy
        (source / f"{index:02d}.svg").write_text(svg, encoding="utf-8")
        html_doc = f'''<!doctype html><html lang="tr"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>Tsinghua Atlası V2 · {slide_id}</title><style>*{{box-sizing:border-box}}html,body{{margin:0;width:1080px;height:1350px;overflow:hidden;background:{PAPER}}}svg{{display:block;width:1080px;height:1350px}}</style></head><body>{svg}</body></html>'''
        (source / f"{index:02d}.html").write_text(html_doc, encoding="utf-8")
    (ROOT / "exact-copy.json").write_text(json.dumps(all_copy, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f"Built {len(SLIDE_IDS)} editable SVG/HTML pairs under {source}")


if __name__ == "__main__":
    main()
