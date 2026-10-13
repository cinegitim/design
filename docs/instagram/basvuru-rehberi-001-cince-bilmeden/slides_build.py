# -*- coding: utf-8 -*-
"""Six slide compositions: photographic bases, Chinese motif geometry, Jost text.

'layers'  -> SVG markup (photos + motifs + colour fields); no editable copy.
'texts'   -> one SVG <text> per exact-copy line, in reading order.
'cjk'     -> verified Chinese characters kept OUTSIDE the copy group.
"""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent))
from motifs import (lattice, xiangyun, seal_mark, meander_border, moon_gate,
                    roofline, ink_sweep,
                    BRAND_RED, CHINA_RED, GOLD_IMP, GOLD_BRIGHT, IVORY)
from slides_data import (W, H, PHOTOS, INK, PAPER)

P = lambda n: f'../photos/{n}.jpg'


def _photo(name, x, y, w, h, clip=None, op=None):
    c = f' clip-path="url(#{clip})"' if clip else ''
    o = f' opacity="{op}"' if op else ''
    return (f'<image href="{P(name)}" x="{x}" y="{y}" width="{w}" '
            f'height="{h}" preserveAspectRatio="xMidYMid slice"{c}{o}/>')


def icon(kind, x, y, s, stroke, sw):
    """Seven coherent vector dossier icons (line geometry only)."""
    o = [f'<g fill="none" stroke="{stroke}" stroke-width="{sw}" '
         f'stroke-linecap="round" stroke-linejoin="round">']
    a = o.append
    if kind == 'passport':
        a(f'<rect x="{x}" y="{y}" width="{s}" height="{s*1.28}" rx="{s*0.10}"/>')
        a(f'<circle cx="{x+s/2}" cy="{y+s*0.52}" r="{s*0.20}"/>')
        a(f'<path d="M{x+s*0.14} {y+s*0.92} h{s*0.72}"/>')
    elif kind == 'diploma':
        a(f'<path d="M{x} {y+s*0.18} v{s*0.74} a{s*0.5} {s*0.5} 0 0 0 {s} 0 '
          f'V{y+s*0.18} Z"/>')
        a(f'<path d="M{x+s*0.16} {y+s*0.06} h{s*0.68}"/>')
        a(f'<path d="M{x+s*0.16} {y+s*0.36} h{s*0.44}"/>')
        a(f'<circle cx="{x+s*0.72}" cy="{y+s*0.46}" r="{s*0.13}"/>')
    elif kind == 'english':
        a(f'<rect x="{x}" y="{y}" width="{s}" height="{s*1.24}" rx="{s*0.08}"/>')
        a(f'<path d="M{x+s*0.16} {y+s*0.26} h{s*0.68}"/>')
        a(f'<path d="M{x+s*0.16} {y+s*0.46} h{s*0.50}"/>')
        a(f'<path d="M{x+s*0.16} {y+s*0.70} l{s*0.16} {s*0.16} l{s*0.16} {-s*0.16} '
          f'l{s*0.16} {s*0.16}"/>')
    elif kind == 'test':
        a(f'<path d="M{x+s*0.16} {y} h{s*0.56} l{s*0.12} {s*0.12} v{s*0.86} '
          f'a{s*0.14} {s*0.14} 0 0 1 -{s*0.14} {s*0.14} h-{s*0.56} '
          f'a{s*0.14} {s*0.14} 0 0 1 -{s*0.14} -{s*0.14} Z"/>')
        a(f'<path d="M{x+s*0.30} {y+s*0.86} v-{s*0.24}"/>')
        a(f'<path d="M{x+s*0.48} {y+s*0.86} v-{s*0.44}"/>')
        a(f'<path d="M{x+s*0.66} {y+s*0.86} v-{s*0.34}"/>')
    elif kind == 'plan':
        a(f'<path d="M{x+s*0.20} {y+s*0.06} h{s*0.50} l{s*0.14} {s*0.14} '
          f'v{s*0.90} a{s*0.16} {s*0.16} 0 0 1 -{s*0.16} {s*0.16} h-{s*0.50} '
          f'a{s*0.16} {s*0.16} 0 0 1 -{s*0.16} -{s*0.16} Z"/>')
        a(f'<path d="M{x+s*0.28} {y+s*0.46} h{s*0.34}"/>')
        a(f'<path d="M{x+s*0.74} {y+s*0.94} l-{s*0.34} -{s*0.34}"/>')
        a(f'<path d="M{x+s*0.74} {y+s*0.94} l{s*0.14} -{s*0.14} '
          f'l{s*0.16} {s*0.16} l-{s*0.12} {s*0.14} Z"/>')
    elif kind == 'refs':
        a(f'<rect x="{x}" y="{y+s*0.10}" width="{s*0.72}" height="{s}" '
          f'rx="{s*0.08}"/>')
        a(f'<rect x="{x+s*0.28}" y="{y}" width="{s*0.72}" height="{s}" '
          f'rx="{s*0.08}"/>')
        a(f'<path d="M{x+s*0.42} {y+s*0.28} h{s*0.44}"/>')
        a(f'<path d="M{x+s*0.42} {y+s*0.50} h{s*0.30}"/>')
    elif kind == 'finance':
        a(f'<rect x="{x}" y="{y+s*0.24}" width="{s}" height="{s*0.62}" '
          f'rx="{s*0.08}"/>')
        a(f'<circle cx="{x+s*0.30}" cy="{y+s*0.55}" r="{s*0.13}"/>')
        a(f'<path d="M{x+s*0.52} {y+s*0.42} h{s*0.28}"/>')
        a(f'<path d="M{x+s*0.52} {y+s*0.62} h{s*0.28}"/>')
    o.append('</g>')
    return ''.join(o)


def _rule(x, y, w, h, col, op=1.0):
    return f'<rect x="{x}" y="{y}" width="{w}" height="{h}" fill="{col}" opacity="{op}"/>'


def _clip(i, x, y, w, h, rx=0):
    r = f' rx="{rx}"' if rx else ''
    return f'<clipPath id="{i}"><rect x="{x}" y="{y}" width="{w}" height="{h}"{r}/></clipPath>'


# ============================================================== SLIDE 01 — cover
S01_LAYERS = (
    f'<rect width="{W}" height="{H}" fill="{INK}"/>'
    + _photo('tsinghua-main-building', 0, 0, W, H, op='0.95')
    # deep ink tonal region behind the copy column
    + f'<rect x="0" y="0" width="700" height="{H}" fill="{INK}" opacity="0.88"/>'
    + f'<rect x="0" y="0" width="700" height="{H}" fill="url(#s01-fade)"/>'
    # one large Chinese architectural motif: circular moon-gate opening
    + moon_gate(810, 610, 250, GOLD_BRIGHT, 3, 's01-gate')
    + f'<circle cx="810" cy="610" r="236" fill="none" stroke="{GOLD_IMP}" '
      f'stroke-width="1.4" opacity=".85"/>'
    # lattice geometry framed inside the upper-left arc of the circle
    + lattice(700, 500, 220, 220, 3, 3, GOLD_BRIGHT, 2.2, opacity=.9, pattern='ice')
    # sparse xiangyun contour, large, lower right
    + xiangyun(952, 1010, 132, GOLD_IMP, 2.2, opacity=.5)
    # gold accent under the answer
    + _rule(86, 806, 120, 6, GOLD_BRIGHT)
    + f'<defs><linearGradient id="s01-fade" x1="0" y1="0" x2="1" y2="0">'
      f'<stop offset="0" stop-color="{INK}" stop-opacity="1"/>'
      f'<stop offset=".6" stop-color="{INK}" stop-opacity=".5"/>'
      f'<stop offset="1" stop-color="{INK}" stop-opacity="0"/>'
      f'</linearGradient></defs>'
)

S01_TEXTS = [
    (86, 196, 26, GOLD_IMP, 500, 'BAŞVURU REHBERİ / 001', 'letter-spacing:.24em'),
    (86, 296, 56, PAPER, 400, 'Çince bilmiyorum.', 'letter-spacing:-.01em'),
    (86, 408, 96, PAPER, 600, "Çin'de", 'letter-spacing:-.035em'),
    (86, 516, 96, PAPER, 600, "okuyabilir", 'letter-spacing:-.035em'),
    (86, 624, 96, PAPER, 600, "miyim?", 'letter-spacing:-.035em'),
    (86, 770, 124, BRAND_RED, 700, 'Evet.', 'letter-spacing:-.045em'),
    (86, 1050, 30, PAPER, 400, "Çin'de İngilizce lisans,", ''),
    (86, 1094, 30, PAPER, 400, "yüksek lisans ve doktora", ''),
    (86, 1138, 30, PAPER, 400, "programları var.", ''),
]
S01_CJK = [(926, 142, 40, GOLD_BRIGHT, '留学')]

# ============================================================== SLIDE 02 — fields
S02_LAYERS = (
    f'<rect width="{W}" height="{H}" fill="{IVORY}"/>'
    + _rule(66, 344, 948, 2, GOLD_IMP)
    + _rule(66, 890, 948, 2, GOLD_IMP)
    # asymmetric editorial collage of authentic academic photography
    + _photo('tsinghua-electrical-building', 66, 372, 318, 486, clip='s02-a')
    + _photo('shu-main-library', 408, 372, 300, 236, clip='s02-b')
    + _photo('zju-medicine-gate', 408, 640, 300, 218, clip='s02-c')
    + _photo('shu-campus', 732, 372, 282, 486, clip='s02-d')
    # gold lattice geometry interrupting the right-hand photograph
    + f'<rect x="752" y="372" width="242" height="242" fill="{IVORY}" opacity=".62"/>'
    + lattice(764, 384, 218, 218, 3, 3, GOLD_IMP, 2.2, opacity=.85, pattern='angular')
    # thin gold rules above each subject group except the first
    + ''.join(_rule(66, y, 948, 1.6, GOLD_IMP, .5) for y in (902, 962, 1022, 1082))
    + _rule(66, 1214, 948, 1.6, GOLD_IMP, .5)
    # red seal-inspired geometric accent, clear of the signature
    + seal_mark(944, 1244, 44, CHINA_RED, opacity=.9)
    + f'<defs>'
    + _clip('s02-a', 66, 372, 318, 486)
    + _clip('s02-b', 408, 372, 300, 236)
    + _clip('s02-c', 408, 640, 300, 218)
    + _clip('s02-d', 732, 372, 282, 486)
    + f'</defs>'
)

S02_TEXTS = [
    (66, 118, 26, CHINA_RED, 500, 'LİSANS / İNGİLİZCE EĞİTİM', 'letter-spacing:.20em'),
    (66, 206, 46, INK, 600, "Çin'de İngilizce", 'letter-spacing:-.025em'),
    (66, 258, 46, INK, 600, "hangi bölümleri", 'letter-spacing:-.025em'),
    (66, 310, 46, INK, 600, "okuyabilirsin?", 'letter-spacing:-.025em'),
    (66, 946, 34, INK, 500, 'Mühendislik · Bilgisayar ve Yazılım', ''),
    (66, 1002, 34, INK, 500, 'İşletme · Finans · Ekonomi', ''),
    (66, 1058, 34, INK, 500, 'Tıp · Sağlık Bilimleri', ''),
    (66, 1114, 34, INK, 500, 'Sosyal Bilimler · Uluslararası İlişkiler', ''),
    (66, 1170, 34, INK, 500, 'Mimarlık · Tasarım', ''),
    (66, 1236, 44, CHINA_RED, 700, 'Ve çok daha fazlası.', 'letter-spacing:-.02em'),
    (66, 1296, 24, INK, 400, 'Programların öğretim dili üniversiteye ve bölüme göre değişir.', ''),
]

# ============================================================== SLIDE 03 — atlas
S03_LAYERS = (
    f'<rect width="{W}" height="{H}" fill="{INK}"/>'
    + _rule(66, 228, 948, 2, GOLD_IMP)
    + _rule(66, 1040, 948, 2, GOLD_IMP)
    # three sections read left to right: Pekin, then the dominant Shanghai
    # central photograph, then Hangzhou
    + _photo('tsinghua-grand-auditorium', 66, 252, 290, 456, clip='s03-a')
    + _photo('shu-campus', 382, 252, 416, 596, clip='s03-main')
    + _photo('zju-zijingang-04', 824, 252, 190, 456, clip='s03-b')
    + f'<rect x="66" y="252" width="290" height="456" fill="none" stroke="{GOLD_IMP}" stroke-width="1.6"/>'
    + f'<rect x="382" y="252" width="416" height="596" fill="none" '
      f'stroke="{GOLD_BRIGHT}" stroke-width="2.4"/>'
    + f'<rect x="824" y="252" width="190" height="456" fill="none" stroke="{GOLD_IMP}" stroke-width="1.6"/>'
    # red location identifier band beneath the dominant photograph
    + _rule(382, 862, 416, 62, CHINA_RED)
    # architectural lattice-inspired crop frames as location markers
    + f'<g fill="none" stroke="{GOLD_BRIGHT}" stroke-width="3">'
      f'<path d="M66 252 h58 M66 252 v58"/>'
      f'<path d="M382 252 h58 M382 252 v58"/>'
      f'<path d="M824 252 h58 M824 252 v58"/>'
      f'<path d="M1014 708 h-58 M1014 708 v-58"/>'
      f'</g>'
    + lattice(66, 946, 118, 118, 2, 2, GOLD_IMP, 2, opacity=.65, pattern='huawin')
    + f'<defs>'
    + _clip('s03-a', 66, 252, 290, 456)
    + _clip('s03-b', 824, 252, 190, 456)
    + _clip('s03-main', 382, 252, 416, 596)
    + f'</defs>'
)

S03_TEXTS = [
    (66, 118, 26, GOLD_IMP, 500, 'LİSANS / NEREDE OKUYABİLİRSİN?', 'letter-spacing:.20em'),
    (66, 200, 48, PAPER, 600, 'Pekin, Şanghay, Hangzhou...', 'letter-spacing:-.03em'),
    (66, 780, 36, PAPER, 600, 'PEKİN ·', 'letter-spacing:.04em'),
    (66, 816, 18, PAPER, 500, 'TSINGHUA UNIVERSITY', 'letter-spacing:.12em'),
    (66, 848, 22, PAPER, 400, 'Bilim ve Mühendislik', ''),
    (406, 902, 30, PAPER, 600, 'ŞANGHAY ·', 'letter-spacing:.06em'),
    (406, 942, 19, GOLD_BRIGHT, 500, 'SHANGHAI UNIVERSITY', 'letter-spacing:.12em'),
    (382, 992, 24, PAPER, 400, 'Finans · Uluslararası Ticaret · Dijital Pazarlama', ''),
    (824, 780, 28, PAPER, 600, 'HANGZHOU ·', 'letter-spacing:.04em'),
    (824, 816, 16, PAPER, 500, 'ZHEJIANG UNIVERSITY', 'letter-spacing:.12em'),
    (824, 848, 20, PAPER, 400, 'Tıp (İngilizce MBBS)', ''),
    (66, 1100, 22, PAPER, 400, 'Suzhou, Ningbo ve başka şehirlerde de', ''),
    (66, 1144, 22, PAPER, 400, 'İngilizce program seçenekleri var.', ''),
]
S03_CJK = [
    (700, 908, 20, GOLD_BRIGHT, '上海大学'),
    (66, 878, 18, GOLD_IMP, '清华大学'),
    (824, 878, 18, GOLD_IMP, '浙江大学'),
]

# ============================================================== SLIDE 04 — masters
S04_LAYERS = (
    f'<rect width="{W}" height="{H}" fill="{INK}"/>'
    + _rule(66, 660, 948, 2, GOLD_IMP)
    + _rule(66, 900, 948, 2, GOLD_IMP)
    + _rule(66, 1140, 948, 2, GOLD_IMP)
    # campus photography as the main visual substance
    + _photo('shu-panchi-lake', 66, 240, 560, 388, clip='s04-main')
    + f'<rect x="66" y="240" width="560" height="388" fill="none" '
      f'stroke="{GOLD_IMP}" stroke-width="1.6"/>'
    + _photo('tsinghua-old-library', 666, 240, 348, 182, clip='s04-a')
    + _photo('fudan-guanghua-tower', 666, 446, 348, 182, clip='s04-b')
    + f'<rect x="666" y="240" width="348" height="182" fill="none" stroke="{GOLD_IMP}" stroke-width="1.4"/>'
    + f'<rect x="666" y="446" width="348" height="182" fill="none" stroke="{GOLD_IMP}" stroke-width="1.4"/>'
    # restrained red colour plane for the strong answer
    + _rule(66, 812, 640, 68, CHINA_RED, .92)
    # small seal-inspired geometric accent
    + seal_mark(944, 104, 44, CHINA_RED, opacity=.95)
    + f'<defs>'
    + _clip('s04-main', 66, 240, 560, 388)
    + _clip('s04-a', 666, 240, 348, 182)
    + _clip('s04-b', 666, 446, 348, 182)
    + f'</defs>'
)

S04_TEXTS = [
    (66, 124, 26, GOLD_IMP, 500, 'YÜKSEK LİSANS / İNGİLİZCE EĞİTİM', 'letter-spacing:.20em'),
    (66, 200, 40, PAPER, 500, "Lisansı Türkiye'de bitirdin.", 'letter-spacing:-.02em'),
    (66, 694, 54, PAPER, 600, "Çin'de yüksek", 'letter-spacing:-.03em'),
    (66, 756, 54, PAPER, 600, "lisans yapabilir misin?", 'letter-spacing:-.03em'),
    (96, 856, 33, PAPER, 600, 'Evet. İngilizce programlar var.', 'letter-spacing:-.02em'),
    (66, 954, 21, GOLD_BRIGHT, 600, 'SHANGHAI UNIVERSITY', 'letter-spacing:.12em'),
    (66, 992, 24, PAPER, 400, 'Finans · Uluslararası İşletme', ''),
    (430, 954, 21, GOLD_BRIGHT, 600, 'TSINGHUA UNIVERSITY', 'letter-spacing:.12em'),
    (430, 992, 24, PAPER, 400, 'Küresel Yönetişim', ''),
    (790, 954, 21, GOLD_BRIGHT, 600, 'FUDAN UNIVERSITY', 'letter-spacing:.12em'),
    (790, 992, 24, PAPER, 400, 'Kamu Politikası', ''),
    (66, 1100, 32, GOLD_BRIGHT, 500, 'Ve çok daha fazlası.', 'letter-spacing:-.01em'),
]

# ============================================================== SLIDE 05 — doctorate
S05_LAYERS = (
    f'<rect width="{W}" height="{H}" fill="{INK}"/>'
    + _photo('tsinghua-quantum-center', 0, 0, W, H, op='0.5')
    + f'<rect width="{W}" height="{H}" fill="url(#s05-shade)"/>'
    # one large abstracted circular architectural motif, upper right
    + moon_gate(830, 300, 190, GOLD_BRIGHT, 3, 's05-gate')
    + f'<circle cx="830" cy="300" r="176" fill="none" stroke="{GOLD_IMP}" '
      f'stroke-width="1.4" opacity=".8"/>'
    + lattice(742, 212, 176, 176, 3, 3, GOLD_BRIGHT, 2, opacity=.85, pattern='ice')
    # strong gold accent under the headline
    + _rule(66, 396, 150, 8, GOLD_BRIGHT)
    # controlled China-red graphic surface for the direct answer
    + _rule(66, 706, 948, 76, CHINA_RED)
    # authentic research/campus photography for the two institutions
    + _photo('shu-main-library', 66, 470, 560, 210, clip='s05-a')
    + _photo('fudan-guanghua-tower', 650, 470, 364, 210, clip='s05-b')
    + f'<rect x="66" y="470" width="560" height="210" fill="none" stroke="{GOLD_IMP}" stroke-width="1.6"/>'
    + f'<rect x="650" y="470" width="364" height="210" fill="none" stroke="{GOLD_IMP}" stroke-width="1.4"/>'
    # restrained xiangyun contour, clear of photographic detail
    + xiangyun(884, 1044, 118, GOLD_IMP, 2.2, opacity=.4)
    + _rule(66, 812, 948, 2, GOLD_IMP)
    + f'<defs><linearGradient id="s05-shade" x1="0" y1="0" x2="0" y2="1">'
      f'<stop offset="0" stop-color="{INK}" stop-opacity=".40"/>'
      f'<stop offset=".40" stop-color="{INK}" stop-opacity=".72"/>'
      f'<stop offset="1" stop-color="{INK}" stop-opacity=".90"/>'
      f'</linearGradient>'
    + _clip('s05-a', 66, 470, 560, 210)
    + _clip('s05-b', 650, 470, 364, 210)
    + f'</defs>'
)

S05_TEXTS = [
    (66, 118, 26, GOLD_IMP, 500, 'DOKTORA / İNGİLİZCE EĞİTİM', 'letter-spacing:.20em'),
    (66, 250, 56, PAPER, 600, 'Çince bilmeden doktora', 'letter-spacing:-.03em'),
    (66, 314, 56, PAPER, 600, 'yapabilir misin?', 'letter-spacing:-.03em'),
    (96, 758, 36, PAPER, 600, 'Evet. İngilizce doktora programları da var.', 'letter-spacing:-.02em'),
    (66, 858, 22, GOLD_BRIGHT, 600, 'SHANGHAI UNIVERSITY', 'letter-spacing:.14em'),
    (66, 902, 30, PAPER, 400, 'Küresel Çalışmalar · Finans · Malzeme Bilimi', ''),
    (650, 962, 22, GOLD_BRIGHT, 600, 'FUDAN UNIVERSITY', 'letter-spacing:.14em'),
    (650, 1006, 28, PAPER, 400, 'Uluslararası Politika · Matematik', ''),
    (66, 1078, 30, GOLD_BRIGHT, 500, 'Ve çok daha fazlası.', 'letter-spacing:-.01em'),
    (66, 1160, 24, PAPER, 400, 'Araştırma alanı, danışman ve kabul', ''),
    (66, 1194, 24, PAPER, 400, 'koşulları programa göre değişir.', ''),
]

# ============================================================== SLIDE 06 — dossier
# Four columns x two rows; each label wraps at a space so no cell can collide
# with its neighbour and every label stays fully visible.
_DOSSIER = [
    ('passport', 'Pasaport', ['Pasaport']),
    ('diploma', 'Diploma ve transkript', ['Diploma ve', 'transkript']),
    ('english', 'İngilizce yeterlilik belgesi', ['İngilizce yeterlilik', 'belgesi']),
    ('test', 'Akademik sınav sonuçları', ['Akademik sınav', 'sonuçları']),
    ('plan', 'Niyet veya araştırma planı', ['Niyet veya', 'araştırma planı']),
    ('refs', 'Akademik referanslar', ['Akademik', 'referanslar']),
    ('finance', 'Mali durum belgesi', ['Mali durum', 'belgesi']),
]
_COLS = [66, 303, 540, 777]
_s06_icons, _s06_cells = [], []
for i, (kind, _full, _lines) in enumerate(_DOSSIER):
    col, row = i % 4, i // 4
    cx, cy = _COLS[col] + 34, 506 + row * 144
    _s06_icons.append(icon(kind, cx - 21, cy, 42, PAPER, 2.4))
    for j, line in enumerate(_lines):
        _s06_cells.append((_COLS[col] + 22, 586 + row * 144 + j * 27, 22, PAPER, 500, line, ''))
_s06_icons = ''.join(_s06_icons)

S06_LAYERS = (
    f'<rect width="{W}" height="{H}" fill="{PAPER}"/>'
    + _rule(66, 148, 948, 2, GOLD_IMP)
    + _rule(66, 444, 948, 2, GOLD_IMP)
    + _rule(66, 900, 948, 2, GOLD_IMP)
    + _rule(66, 1186, 948, 2, GOLD_IMP)
    # prominent red archival-folder shape
    + f'<path d="M66 466 h948 a26 26 0 0 1 26 26 v312 a26 26 0 0 1 -26 26 '
      f'H66 a26 26 0 0 1 -26 -26 V492 a26 26 0 0 1 26 -26 Z" fill="{CHINA_RED}"/>'
    + f'<path d="M66 466 h300 l42 46 h130" fill="none" stroke="{BRAND_RED}" '
      f'stroke-width="4" opacity=".5"/>'
    + _rule(66, 488, 948, 3, GOLD_BRIGHT)
    # seven coherent vector document icons inside the dossier
    + f'<g id="dossier-icons">{_s06_icons}</g>'
    # red editorial underline for the call to action
    + _rule(66, 1076, 108, 6, BRAND_RED)
    # restrained seal-like and lattice accents (geometric, not official marks)
    + seal_mark(946, 96, 46, CHINA_RED, opacity=.9)
    + lattice(950, 900, 58, 58, 2, 2, GOLD_IMP, 1.6, opacity=.6, pattern='angular')
)

S06_TEXTS = [
    (138, 118, 26, CHINA_RED, 500, 'BAŞVURU REHBERİ / 001', 'letter-spacing:.20em'),
    (66, 218, 44, INK, 600, "Çin'de üniversiteye", 'letter-spacing:-.03em'),
    (66, 270, 44, INK, 600, "başvurmak için", 'letter-spacing:-.03em'),
    (66, 322, 44, INK, 600, "diploma yetmiyor.", 'letter-spacing:-.03em'),
    (66, 420, 26, INK, 500, 'Başvuruda istenebilen belgeler:', ''),
] + _s06_cells + [
    (66, 868, 32, INK, 600, 'Ve programa göre daha fazlası.', 'letter-spacing:-.02em'),
    (66, 938, 25, INK, 400, 'Bazı üniversiteler mülakat, adli sicil belgesi ve resmî', ''),
    (66, 972, 25, INK, 400, 'çeviri de istiyor.', ''),
    (66, 1042, 30, INK, 500, 'Program seçimi ve başvuru dosyanı birlikte hazırlayalım.', ''),
    (66, 1152, 46, BRAND_RED, 700, 'Ücretsiz ön görüşme', 'letter-spacing:-.025em'),
]

SLIDES = [
    dict(id='01-cover', layers=S01_LAYERS, texts=S01_TEXTS, cjk=S01_CJK),
    dict(id='02-fields', layers=S02_LAYERS, texts=S02_TEXTS, cjk=[]),
    dict(id='03-atlas', layers=S03_LAYERS, texts=S03_TEXTS, cjk=S03_CJK),
    dict(id='04-masters', layers=S04_LAYERS, texts=S04_TEXTS, cjk=[]),
    dict(id='05-doctorate', layers=S05_LAYERS, texts=S05_TEXTS, cjk=[]),
    dict(id='06-dossier', layers=S06_LAYERS, texts=S06_TEXTS, cjk=[]),
]
