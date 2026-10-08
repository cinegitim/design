#!/usr/bin/env python3
"""Çin Eğitim — three creative direction boards (vector-first, deterministic).

Emits brands/cin-egitim/boards/direction-{a,b,c}.html and docs/cin-egitim/index.html.

Policy compliance:
  * Vector-first. Logo marks are real SVG geometry on a declared modular grid.
  * No image-generation calls. No <text> is used for the marks; wordmark previews
    in the boards are live webfonts and are explicitly labelled as previews —
    production ships outlined paths, exactly like the Asya'da Eğitim reviews.
  * Nothing here is canonical. No brand.json, no manifest, no lock. Human
    direction selection is required before any asset is promoted.
  * Isolated from brands/asyada-egitim: own slug, own folder, own fonts.
"""
from __future__ import annotations

from pathlib import Path
import json

# This file lives at studio/tools/cin-egitim/, so the repo root is four levels up.
# parents[2] would resolve to studio/ and silently write the whole tree there.
ROOT = Path(__file__).resolve().parents[3]
BOARDS = ROOT / "brands/cin-egitim/boards"
DOC = ROOT / "docs/cin-egitim"

# ─────────────────────────────────────────────────────────── the three marks
# Every mark is authored on a 120×120 grid with a 12-unit outer margin.

def mark_a(colours: dict[str, str]) -> str:
    """KAYIT / THE REGISTER — official stamp ring + ruled record grid, ONE cell
    filled. Modulus 6; ring weight 9; rule weight 2.5.

    The filled cell is a CORNER cell, not the centre. Filling the centre made the
    two rule pairs read as a crosshair/nick — a target, not a register — which is
    the wrong idea entirely. A corner cell keeps the 3×3 grid legible as a grid
    while still stating "exactly one of these is yours".
    """
    red, ink = colours["accent"], colours["ink"]
    x0, span, third = 32.0, 56.0, 18.6667
    a, b = x0 + third, x0 + 2 * third
    rules = []
    for v in (a, b):
        rules.append(f'<line x1="{v}" y1="{x0}" x2="{v}" y2="{x0+span}"/>')
        rules.append(f'<line x1="{x0}" y1="{v}" x2="{x0+span}" y2="{v}"/>')
    # lower-right cell: x b..x0+span, y b..x0+span, inset 1.5
    return (
        f'<circle cx="60" cy="60" r="47" fill="none" stroke="{red}" stroke-width="9"/>'
        f'<g stroke="{ink}" stroke-width="2.5" opacity=".8">' + "".join(rules) + '</g>'
        f'<rect x="{b+1.5}" y="{b+1.5}" width="{third-3}" height="{third-3}" fill="{red}"/>'
    )


def mark_b(colours: dict[str, str]) -> str:
    """KALEM / THE SINGLE STROKE — one pressure-released stroke, squared start,
    written against a short measured guide. Two elements, nothing else.

    The earlier bottom edge bulged downward and the whole shape read as a LEAF
    with a spike, not a stroke. The belly is now convex along the stroke's own
    axis: thick at the left (29 units), released to a 2-unit tip at the right.
    The guide covers only the left half so it anchors the press instead of
    underlining the whole mark.
    """
    ink, red = colours["ink"], colours["accent"]
    return (
        f'<path d="M 14 47 C 48 49 74 55 102 59 L 102 61 C 74 62 46 66 14 76 Z" fill="{ink}"/>'
        f'<rect x="14" y="88" width="44" height="3" fill="{red}"/>'
    )


def mark_c(colours: dict[str, str]) -> str:
    """KOORDİNAT / THE INTERSECTION — two equal coordinate frames sharing one
    axis; the overlap is the brand. Exact circle intersection, x=60,
    y = 60 ± √(34²−20²) = 32.5 / 87.5."""
    ink, red = colours["ink"], colours["accent"]
    return (
        f'<circle cx="40" cy="60" r="34" fill="none" stroke="{ink}" stroke-width="7"/>'
        f'<circle cx="80" cy="60" r="34" fill="none" stroke="{ink}" stroke-width="7"/>'
        f'<path d="M 60 32.5 A 34 34 0 0 1 60 87.5 A 34 34 0 0 1 60 32.5 Z" fill="{red}"/>'
    )


def mark_c_small(colours: dict[str, str]) -> str:
    """16–24 px variant: the lens collapses to a single measured point. Same two
    circles, axis marked instead of lens filled."""
    ink, red = colours["ink"], colours["accent"]
    return (
        f'<circle cx="40" cy="60" r="34" fill="none" stroke="{ink}" stroke-width="11"/>'
        f'<circle cx="80" cy="60" r="34" fill="none" stroke="{ink}" stroke-width="11"/>'
        f'<circle cx="60" cy="60" r="7" fill="{red}"/>'
    )


# Marks are stored in DIRECTIONS by name so the spec table stays plain data;
# this resolves a name to the actual drawing function.
MARK_FN = {"mark_a": mark_a, "mark_b": mark_b, "mark_c": mark_c,
           "mark_c_small": mark_c_small}


# ─────────────────────────────────────────────────────────── direction specs
DIRECTIONS = [
    dict(
        key="a", slug="direction-a", name="KAYIT", en="THE REGISTER",
        concept="Resmî kayıt · İnsî navigasyon",
        thesis=(
            "Çin'de bir öğrencinin hayatı bir sicile, bir koda, bir puana dayanır: 学号, "
            "高考 puanı, 学分, 985/211 ayrımı. Bürokrasi dünyanın en güçlü sistemi ve "
            "uzaktan görünmez. Çin Eğitim'in değeri bu kaydı okunur kılmak. "
            "Marka bir damga değil, bir <b>kayıt hücresi</b>: kaç kayıt arasında tam "
            "bir tane senin hücren dolu."
        ),
        grammar="Sıkı modüler grid · saç teli kurallar · tablo rakamları · kart yoğunluğu",
        function=(
            "Bürokratik otoriteyi insani navigasyona çevirir. Katı, ölçülebilir, "
            "kuşkulu değil. Bir danışmanın masasında duran belge gibi."
        ),
        risk=("Dar. Katı sistem dili yumuşak gelecek vaadiyle çatışabilir; "
              "veliye 'evrak işi' gibi gelebilir."),
        smallsize=("EN ZAYIF KÜÇÜLME. 24px altında 3×3 ızgara okunmuyor; marka halka + "
                   "tek lekeye düşüyor ve kavamını kaybediyor. D-04 için 24px tabanı "
                   "gerekli, altında sadeleştirilmiş yeni bir varyant üretmek zorunda."),
        why=("Ürünün gerçek farklılaştırıcısı 23 000 programlık bilgi tabanı. "
             "Bu bir veri ürünüdür; kimlik de veri gibi davranabilir."),
        display='"Archivo", "Helvetica Neue", Arial, sans-serif',
        mono='"IBM Plex Mono", ui-monospace, monospace',
        fonts="Archivo + IBM Plex Mono · her ikisi de Google Fonts OFL",
        display_wght="600 / 700", mono_wght="400 / 500",
        palette=[
            ("Mürekkep", "#16191C", "Birincil metin, işaret", "30%"),
            ("Kâğıt", "#F4F1EA", "Zemin", "58%"),
            ("Vermilyon", "#B4321F", "Tek imza rengi", "&lt; 7%"),
            ("Ardoz", "#6E7B80", "İkincil metin", "—"),
            ("Kural", "#D8D2C6", "Saç teli çizgi", "—"),
        ],
        accents=["#B4321F", "#16191C"],
        mark=mark_a, mark_fn="mark_a",
        grid=[
            "Kenar boşluğu: 12 birim (marka 120 birimlik karede)",
            "Halka ağırlığı 9 · kural ağırlığı 2.5 · dolu hücre iç boşluk 2",
            "Kayıt ızgarası 3×3, 56 birim alan, eşit 18.67 bölme",
            "Dış güvenli alan: 32 birim (halka dış çapına göre)",
        ],
        device=("Saç teli kural + tırnak. Her bölüm başlığı sol kenarda bir "
                "kural ve 4 birimlik tırnakla başlar. Başka hiçbir yerde kırmızı "
                "çizgi kullanılmaz."),
        pattern=("Yok. Doldurulmuş tek hücre tek başına o kadar güçlü ki desen "
                 "onu seyreltirdi."),
        imagery=("Belge yüzeyleri, damga izi, arşiv kutu kenarı, mürekkep ıslaklığı. "
                 "Stok kampüs fotoğrafı yok, gülümsayan öğrenci klişesi yok."),
        material="Soğuk kâğıt, mürekkep, selüloz. Baskıda 1 renk + spot kırmızı.",
        lockups=[
            ("P-01", "Birincil dikey", "Mühür üstte, kelime-marka altta"),
            ("H-02", "Birincil yatay", "Mühür solda tam yükseklikte"),
            ("C-03", "Kompakt", "Küçülmüş mühür, sıkı boşluk"),
            ("D-04", "Küçük kullanım", "Yalnız mühür — sözcük yok"),
            ("F-05", "Resmî", "Büyük mühür, geniş boşluk"),
        ],
    ),
    dict(
        key="b", slug="direction-b", name="KALEM", en="THE SINGLE STROKE",
        concept="Mürekkep · Hareket ekonomisi",
        thesis=(
            "Çin'de kalem bir zanaat değil bir disiplin: iki bin yılda öğrenilen tek "
            "şey, ikna etmek için ne kadar az çizgi gerektiğidir. Marka tam olarak "
            "bu: <b>tek bir kararlı çizgi</b> seni karşıya taşır. Fırça süsü değil — "
            "basınçla başlayıp bırakılan, kurala yazılmış tek bir vuruş."
        ),
        grammar="Hareket + boşluk · ızgara dışı asimetri · aşırı negatif alan · tek vurgu",
        function=(
            "Kalabalıktan koparır. Katalog değil manifesto hissi verir. "
            "Gencin heyecanını, velinin saygısını aynı anda taşır."
        ),
        risk=("Fırça klişesi. Ölçülebilir ızgarada kurgulanmazsa Ankaralı bir "
              "kağıt kâğıdına dönüşür. Yatay ağırlıklı form ayrıca kare içinde "
              "uygulama simgesi olarak zayıf; oynat düğmesi çağrışımı izlenmeli."),
        smallsize=("ORTA. Büyük boyutta güçlü ve akılda kalıcı. 40px altında kırmızı "
                   "kılavuz kopuk bir tireye dönüşüyor ve yatay çizgi kare içinde "
                   "okunmuyor. Uygulama simgesi için ayrı bir dikey varyant gerekir."),
        why=("Çin Eğitim'in tonu zaten seyahat değil, sahiplenme. "
             "Senin programın, senin kaydın, senin hikâyen."),
        display='"Newsreader", Georgia, serif',
        mono='"Figtree", "Helvetica Neue", Arial, sans-serif',
        fonts="Newsreader + Figtree · ikisi de Google Fonts OFL",
        display_wght="400 / 500 · italik vurgu", mono_wght="400 / 500",
        palette=[
            ("Mürekkep", "#1B1A18", "Birincil metin, vuruş", "28%"),
            ("Sıcak kâğıt", "#F2EDE3", "Zemin", "60%"),
            ("Kızıl mürekkep", "#A8382A", "Tek vurgu", "&lt; 6%"),
            ("Soluk", "#8C857A", "İkincil metin", "—"),
            ("Yıkama", "#DED7C8", "Kâğıt dokusu / çizgi", "—"),
        ],
        accents=["#A8382A", "#1B1A18"],
        mark=mark_b, mark_fn="mark_b",
        grid=[
            "Marka 120 birim; kenar boşluğu 14 birim (bilinçli olarak A'dan geniş)",
            "Vuruş taban çizgisi 12 birim yükseklik, 86 birimde biten sivrilme",
            "Kural tam vuruş genişliği kadar (14→104), 3 birim kalınlık",
            "Dış güvenli alan: 40 birim — en yüksek, çünkü en az sayıda eleman var",
        ],
        device=("Tek kırmızı kural. Her yerde tek çizgi, üstüne asla ikinci "
                "çizgi gelmez. Kırmızı yalnız bu kuralda ve tek bir vurguda yaşar."),
        pattern=("Yok. Boşluk desendir. Kâğıt dokusu %4–6 serbest."),
        imagery=("Kâğıt, mürekkep, yakın el malzemesi, kırpılmış boşluk. "
                 "Manzara yok. Yüz yoksa yüz de yok — marka konuşsun."),
        material="Yumuşak kâğıt, kuru mürekkep. Kapakta göbek baskı yok.",
        lockups=[
            ("P-01", "Birincil dikey", "Vuruş üstte, kelime-marka altta"),
            ("H-02", "Birincil yatay", "Vuruş solda, kelime-marka sağda"),
            ("C-03", "Kompakt", "Vuruş küçülür, metin korunur"),
            ("D-04", "Küçük kullanım", "Yalnız vuruş + kural"),
            ("F-05", "Resmî", "Geniş boşluk, küçük vuruş"),
        ],
    ),
    dict(
        key="c", slug="direction-c", name="KOORDİNAT", en="THE INTERSECTION",
        concept="Ölçüm · Kesişim",
        thesis=(
            "Türkiye 37° kuzey, 37° doğu. Çin 39° kuzey, 116° doğu. Beijing "
            "kuzey-güney ekseni üzerinde kurulmuş bir şehir. Bir Türk öğrenci "
            "meridyen geçiyor. Çin Eğitim iki koordinat sisteminin <b>kesiştiği</b> "
            "noktadır — iki çerçeve, tek ortak eksen, tam üst üste binen alan."
        ),
        grammar="Koordinat ağı · tırnaklar · her öğede ölçülmüş koordinat",
        function=(
            "Kesinlik ve çağdaşlık. 'Nereye, hangi koordinatta' sorusunu "
            "markanın kendisi cevaplar. Harita ve yönlendirme dili."
        ),
        risk=("Soğuk olabilir. 15 yaşındaki kitle için teknoloji şirketi "
              "gibi okuyabilir; veli soğuk bulabilir."),
        smallsize=("EN GÜÇLÜ KÜÇÜLME. Üç bileşeni de 24px'e kadar korunuyor: iki "
                   "çember + kırmızı merkez nokta. Silüet en ayırt edici, uygulama "
                   "simgesi olarak en sağlam. 16px'te kırmızı merkez doğal "
                   "varyanta geçmeli."),
        why=("Ürün zaten bir veritabanı ve eşleştirme. Doğruluk dili markanın "
             "içinde zaten var — dışarıdan almaya gerek yok."),
        display='"Space Grotesk", "Helvetica Neue", Arial, sans-serif',
        mono='"JetBrains Mono", ui-monospace, monospace',
        fonts="Space Grotesk + JetBrains Mono · ikisi de Google Fonts OFL",
        display_wght="500 / 700", mono_wght="400 / 500",
        palette=[
            ("Mürekkep lacivert", "#14202A", "Birincil metin, çerçeve", "32%"),
            ("Serin kâğıt", "#EFEFEA", "Zemin", "54%"),
            ("Sinyal", "#C0392B", "Kesişim, tek vurgu", "&lt; 6%"),
            ("Ardoz", "#5C6E78", "İkincil metin / eksen", "—"),
            ("Saç teli", "#C6CECC", "Ağ çizgisi", "—"),
        ],
        accents=["#C0392B", "#14202A"],
        mark=mark_c, mark_fn="mark_c",
        grid=[
            "Marka 120 birim; iki çember r=34, merkezler x=40 ve x=80",
            "Kesişim tam olarak x=60, y=32.5 ve y=87.5 (√(34²−20²))",
            "Çember ağırlığı 8 · küçük boyutta 11 ve kesişim noktaya iner",
            "Dış güvenli alan: 36 birim",
        ],
        device=("Koordinat tırnakları. Her blok başlığının yanında küçük bir "
                "koordinat okuması: 39°54′N 116°23′E. Asla büyük harfle kutsanmayan, "
                "sadece konumu doğrulayan bir ayrıntı."),
        pattern=("Çok ince koordinat ağı (%6 opaklık), yalnız arka plan "
                 "düzlemlerinde. Metin üstünde değil."),
        imagery=("Ölçüm, kırpılmış altyazı, meteorolojik bant, teknik çizim. "
                 "Stok kampüs/öğrenci fotoğrafı yok."),
        material="Mat kağıt, soğuk mürekkep, teknik film hissi. Baskıda "
                 "CMYK zenginliği korunur.",
        lockups=[
            ("P-01", "Birincil dikey", "Çerçeve üstte, kelime-marka altta"),
            ("H-02", "Birincil yatay", "Çerçeve solda, kelime-marka sağda"),
            ("C-03", "Kompakt", "Çerçeve küçülür, metin korunur"),
            ("D-04", "Küçük kullanım", "Yalnız çerçeve + nokta"),
            ("F-05", "Resmî", "Geniş koordinat bandı"),
        ],
    ),
]

# ──────────────────────────────────────────────────────────────── lockups
# Lockups are composed here as real SVG, so the board proves the geometry
# rather than describing it. Wordmark text stays live (board preview only).

# Wordmark text stays live on the boards (production ships outlined paths), so
# the composer's advance widths are ESTIMATES. They must still be consistent
# within a variant, because every position below is derived from them.
TR_WORD = "\u00c7\u0130N E\u011e\u0130T\u0130M"
EN_WORD = "EDUCATION IN CHINA"
CHAR_W = {"a": 0.655, "b": 0.600, "c": 0.655}   # caps advance / em, per direction


def lockup_svg(d: dict, variant: str, colours: dict, mono: bool = False) -> str:
    """Compose one lockup role from real geometry.

    The mark is authored on a 120-unit grid and is SCALED into whatever
    display size the role uses. The earlier version reserved a width but drew
    the mark at full size, so the wordmark landed on top of the mark in every
    horizontal role.
    """
    ink = colours["paper"] if mono else colours["ink"]
    acc = colours["paper"] if mono else colours["accent"]
    body = (MARK_FN[d["mark_fn"]] if mono else d["mark"])(colours)
    pad = 16.0
    fam = ("Newsreader, Georgia, serif" if d["key"] == "b"
           else "Archivo, 'Helvetica Neue', Arial, sans-serif")
    heavy = 500 if d["key"] == "b" else 600

    def width(s: str, size: float, tracking: float) -> float:
        return len(s) * size * CHAR_W[d["key"]] + tracking * (len(s) - 1)

    def line(x, y, s, size, weight, tracking, fill, opacity="1"):
        return (f'<text x="{x:.1f}" y="{y:.1f}" font-family="{fam}" font-size="{size}" '
                f'font-weight="{weight}" letter-spacing="{tracking}" fill="{fill}" '
                f'opacity="{opacity}">{s}</text>')

    def place(body, ms, x, y):
        return f'<g transform="translate({x:.1f},{y:.1f}) scale({ms/120:.5f})">{body}</g>'

    # D-04 is the small-use role: the mark plus the Turkish line only. It is
    # matched on the variant id, never on a substring of a display label.
    tr_only = variant == "D-04"
    fs_t = {"P-01": 44, "H-02": 44, "C-03": 34, "D-04": 26, "F-05": 48}[variant]
    fs_e = {"P-01": 14, "H-02": 14, "C-03": 12, "D-04": 0, "F-05": 15}[variant]
    trk_t, trk_e = -0.8, 3.0
    tw = width(TR_WORD, fs_t, trk_t)
    ew = width(EN_WORD, fs_e, trk_e) if not tr_only else 0.0
    text_w = max(tw, ew)
    gap = {"P-01": 20, "H-02": 24, "C-03": 18, "D-04": 14, "F-05": 32}[variant]

    if variant in ("P-01", "F-05"):
        ms = 118 if variant == "P-01" else 148
        block_h = fs_t + (fs_e + 14 if not tr_only else 0)
        w = max(ms, text_w) + pad * 2
        h = pad * 2 + ms + gap + block_h
        x0 = (w - text_w) / 2
        inner = place(body, ms, (w - ms) / 2, pad)
        ty = pad + ms + gap + fs_t
        inner += line(x0, ty, TR_WORD, fs_t, heavy, trk_t, ink)
        if tr_only:
            pass
        elif variant == "F-05":
            inner += (f'<rect x="{x0:.1f}" y="{ty + 10:.1f}" width="{text_w:.1f}" '
                      f'height="2" fill="{acc}"/>')
            inner += line(x0, ty + 32, EN_WORD, fs_e, 400, trk_e, ink, ".78")
        else:
            inner += line(x0, ty + fs_e + 14, EN_WORD, fs_e, 400, trk_e, acc)
    elif tr_only:
        # D-04: horizontal, mark left, Turkish line only.
        ms = 56
        block = max(ms, fs_t)
        w = pad * 2 + ms + gap + tw
        h = pad * 2 + block
        inner = place(body, ms, pad, pad + (block - ms) / 2)
        inner += line(pad + ms + gap, pad + block / 2 + fs_t * 0.36,
                      TR_WORD, fs_t, heavy, trk_t, ink)
    elif variant == "C-03":
        ms = 52
        block_h = fs_t + fs_e + 14
        w = pad * 2 + ms + gap + text_w
        h = pad * 2 + max(ms, block_h)
        inner = place(body, ms, pad, pad + (max(ms, block_h) - ms) / 2)
        tx = pad + ms + gap
        ty = pad + (max(ms, block_h) - block_h) / 2 + fs_t
        inner += line(tx, ty, TR_WORD, fs_t, heavy, trk_t, ink)
        inner += line(tx, ty + fs_e + 14, EN_WORD, fs_e, 400, trk_e, acc)
    else:  # H-02
        ms = 92
        block_h = fs_t + fs_e + 14
        w = pad * 2 + ms + gap + text_w
        h = pad * 2 + max(ms, block_h)
        inner = place(body, ms, pad, pad + (max(ms, block_h) - ms) / 2)
        tx = pad + ms + gap
        ty = pad + (max(ms, block_h) - block_h) / 2 + fs_t
        inner += line(tx, ty, TR_WORD, fs_t, heavy, trk_t, ink)
        inner += line(tx, ty + fs_e + 14, EN_WORD, fs_e, 400, trk_e, acc)

    return _svg(w, h, inner, f"\u00c7in E\u011fitim \u2014 {variant}")


def _svg(w: float, h: float, inner: str, label: str) -> str:
    return (f'<svg viewBox="0 0 {w:.1f} {h:.1f}" role="img" aria-label="{label}" '
            f'preserveAspectRatio="xMidYMid meet">{inner}</svg>')


# ───────────────────────────────────────────────────────────── board markup
# Panel CSS lives outside the f-string on purpose: doubling every brace in a
# template makes the stylesheet unreadable and hides real syntax errors.
PANEL_STYLE = """
{
*{box-sizing:border-box;margin:0;padding:0}
:root{--ink:#16191C;--paper:#F4F1EA;--accent:#B4321F;--line:#D8D2C6;--muted:#6E7B80;--card:#FBF9F4}
body{background:var(--paper);color:var(--ink);font:16px/1.62 "Archivo","Helvetica Neue",Arial,sans-serif;-webkit-font-smoothing:antialiased}
.wrap{max-width:1180px;margin:0 auto;padding:0 28px 100px}
a{color:inherit;text-underline-offset:4px}
.crumb{font:12px/1.4 ui-monospace,Menlo,monospace;color:var(--muted);padding:22px 0;
  border-bottom:1px solid var(--ink);display:flex;gap:10px;flex-wrap:wrap;align-items:baseline}
.crumb b{font:600 15px/1.2 "Archivo",sans-serif}
.brandbar{border-bottom:1px solid var(--ink);padding:16px 0 18px;display:flex;gap:18px;align-items:center;flex-wrap:wrap}
.brandbar .blab{font:11px/1.4 ui-monospace,Menlo,monospace;letter-spacing:.14em;color:var(--muted);text-transform:uppercase}
.brandbar .opts{display:flex;gap:10px;flex-wrap:wrap}
.opt{display:flex;align-items:center;gap:12px;text-decoration:none;color:var(--ink);border:1px solid var(--line);border-radius:10px;padding:9px 16px 9px 11px;background:var(--card);min-height:56px}
.opt:hover{border-color:var(--ink)}
.opt.here{border-color:var(--ink);box-shadow:3px 3px 0 var(--ink)}
.opt img,.opt .pending{width:38px;height:38px;flex:none;border-radius:7px}
.opt .pending{border:1.5px dashed var(--line);display:grid;place-items:center;font:10px/1.1 ui-monospace,Menlo,monospace;color:var(--muted);letter-spacing:.04em;text-align:center}
.opt .txt{display:flex;flex-direction:column;gap:2px}
.opt .on{font-size:16px;font-weight:500;letter-spacing:-.01em}
.opt .sub{font:11px/1.2 ui-monospace,Menlo,monospace;color:var(--muted);letter-spacing:.05em}
.opt.here .sub{color:var(--accent)}
h1{font-size:clamp(40px,6.4vw,80px);line-height:1.0;letter-spacing:-.05em;margin:52px 0 0;font-weight:700}
.sub{font-size:19px;max-width:60ch;margin-top:18px;color:#3b3a35}
.kicker{font:11px/1.4 ui-monospace,Menlo,monospace;letter-spacing:.13em;text-transform:uppercase;color:var(--muted)}
.pending{border:1px solid var(--accent);border-left-width:5px;background:var(--card);
  padding:16px 20px;margin:30px 0 0;font:12px/1.5 ui-monospace,Menlo,monospace;
  letter-spacing:.05em;color:var(--accent)}
section{border-top:1px solid var(--ink);margin-top:70px;padding-top:30px}
h2{font-size:clamp(26px,3.6vw,40px);line-height:1.1;letter-spacing:-.035em;margin:8px 0 14px;font-weight:600}
.cards{display:grid;grid-template-columns:repeat(auto-fit,minmax(300px,1fr));gap:18px;margin-top:26px}
.card{display:block;background:var(--card);border:1px solid var(--ink);border-radius:3px;
  padding:0 0 22px;text-decoration:none;overflow:hidden}
.card:hover{box-shadow:7px 7px 0 var(--ink)}
.art{height:230px;display:grid;place-items:center;background:var(--paper);border-bottom:1px solid var(--line);padding:26px}
.art svg{width:150px;height:auto}
.tag{display:block;font:11px ui-monospace,Menlo,monospace;letter-spacing:.13em;color:var(--accent);margin:20px 24px 0}
.card b{display:block;font-size:30px;letter-spacing:-.03em;margin:6px 24px 0}
.card .en{display:block;font:13px ui-monospace,Menlo,monospace;color:var(--muted);margin:2px 24px 0;letter-spacing:.05em}
.card p{font-size:14.5px;color:#3b3a35;margin:12px 24px 0}
.swatch{display:flex;gap:0;margin:16px 24px 0;border:1px solid var(--line)}
.swatch i{display:block;height:22px;flex:1}
.go{display:inline-block;margin:16px 24px 0;font-size:13px;border-bottom:2px solid var(--accent);padding-bottom:2px}
.table{width:100%;border-collapse:collapse;font-size:14px;margin-top:20px}
.table th,.table td{text-align:left;padding:10px 12px;border-bottom:1px solid var(--line)}
.table th{font:12px ui-monospace,Menlo,monospace;color:var(--muted);text-transform:uppercase;letter-spacing:.05em}
.table code{font:12.5px ui-monospace,Menlo,monospace}
.scroll{overflow-x:auto;border:1px solid var(--line);border-radius:3px}
.iso{display:grid;grid-template-columns:1fr 1fr;gap:20px;margin-top:24px}
.iso div{border:1px solid var(--line);border-radius:3px;padding:20px 22px;background:var(--card)}
.iso h3{font-size:15px;margin-bottom:8px}
.iso p{font-size:14px;color:#3b3a35}
.iso code{font:12px ui-monospace,Menlo,monospace;color:var(--accent);overflow-wrap:anywhere}
footer{margin-top:70px;padding-top:20px;border-top:1px solid var(--line);
  font:12px ui-monospace,Menlo,monospace;color:var(--muted);display:flex;justify-content:space-between;gap:16px;flex-wrap:wrap}
@media(max-width:820px){.iso{grid-template-columns:1fr}.wrap{padding:0 18px 70px}}
"""

STYLE = """
*{box-sizing:border-box;margin:0;padding:0}
:root{--ink:#16191C;--paper:#F4F1EA;--accent:#B4321F;--line:#D8D2C6;--muted:#6E7B80;--card:#FBF9F4}
body{background:var(--paper);color:var(--ink);
  font:16px/1.62 "Archivo","Helvetica Neue",Arial,sans-serif;
  -webkit-font-smoothing:antialiased}
.wrap{max-width:1240px;margin:0 auto;padding:0 28px 110px}
a{color:inherit;text-underline-offset:4px}
.crumb{font:12px/1.4 ui-monospace,Menlo,monospace;color:var(--muted);
  padding:22px 0;border-bottom:1px solid var(--ink);display:flex;gap:10px;flex-wrap:wrap;align-items:baseline}
.crumb b{font:600 15px/1.2 "Archivo",sans-serif;letter-spacing:.01em}
h1{font-size:clamp(40px,7vw,86px);line-height:1.0;letter-spacing:-.05em;margin:52px 0 0;
  font-weight:700;text-wrap:balance}
.sub{font-size:19px;max-width:58ch;margin-top:18px;color:#3b3a35}
.kicker{font:11px/1.4 ui-monospace,Menlo,monospace;letter-spacing:.13em;
  text-transform:uppercase;color:var(--muted)}
section{border-top:1px solid var(--ink);margin-top:76px;padding-top:30px}
h2{font-size:clamp(26px,3.6vw,40px);line-height:1.1;letter-spacing:-.035em;margin:8px 0 14px;font-weight:600}
h3{font-size:19px;letter-spacing:-.01em;margin:0 0 8px;font-weight:600}
p{max-width:74ch;color:#33322e}
.stage{background:var(--card);border:1px solid var(--line);border-radius:3px;
  padding:clamp(26px,5vw,60px);display:grid;place-items:center;margin-top:26px;
  background-image:linear-gradient(var(--line) 1px,transparent 1px),
    linear-gradient(90deg,var(--line) 1px,transparent 1px);
  background-size:40px 40px;background-position:-1px -1px}
.stage.dark{background:var(--ink);border-color:var(--ink);color:var(--paper)}
.stage.dark .kicker{color:#8d8a80}
.mark{max-width:260px;width:100%;height:auto}
.mark.small{max-width:96px}
.grid2{display:grid;grid-template-columns:1fr 1fr;gap:20px;margin-top:26px}
.grid3{display:grid;grid-template-columns:repeat(3,1fr);gap:16px;margin-top:26px}
.box{border:1px solid var(--line);border-left:4px solid var(--accent);
  background:var(--card);padding:18px 22px;margin-top:22px;border-radius:2px}
.box.warn{border-left-color:var(--ink)}
.box b{font-weight:600}
.risk{border-left-color:#8a2b27}
.risk b{color:#8a2b27}
.sw{display:grid;grid-template-columns:repeat(auto-fit,minmax(150px,1fr));gap:12px;margin-top:22px}
.sw figure{border:1px solid var(--line);border-radius:2px;overflow:hidden;background:var(--card)}
.sw .chip{height:96px}
.sw .meta{padding:12px 14px;font-size:13px}
.sw .meta b{display:block;font-size:14px}
.sw .meta code{font:12px ui-monospace,Menlo,monospace;color:var(--muted)}
.lock{display:grid;grid-template-columns:repeat(auto-fit,minmax(210px,1fr));gap:14px;margin-top:24px}
.lock figure{border:1px solid var(--line);border-radius:2px;padding:20px 16px 12px;
  background:var(--card)}
.lock figure.on-dark{background:var(--ink);border-color:var(--ink);color:var(--paper)}
.lock .view{height:150px;display:grid;place-items:center;margin-bottom:12px}
.lock .view svg{max-width:100%;max-height:130px}
.lock figcaption{font-size:12px;color:var(--muted)}
.lock figure.on-dark figcaption{color:#a09b8f}
.lock code{font:11px ui-monospace,Menlo,monospace;overflow-wrap:anywhere}
dl.spec{display:grid;grid-template-columns:170px 1fr;gap:0;margin-top:20px;
  border-top:1px solid var(--line);font-size:15px}
dl.spec dt{padding:11px 14px 11px 0;border-bottom:1px solid var(--line);color:var(--muted);
  font:12px/1.5 ui-monospace,Menlo,monospace;letter-spacing:.04em;text-transform:uppercase}
dl.spec dd{padding:11px 0;border-bottom:1px solid var(--line);margin:0}
.type-demo{border:1px solid var(--line);border-radius:2px;background:var(--card);
  padding:24px;margin-top:20px;overflow:hidden}
.type-demo .big{font-size:clamp(32px,5vw,54px);line-height:1.05;letter-spacing:-.04em}
.type-demo .en{font-size:15px;letter-spacing:.28em;margin-top:10px;color:var(--muted)}
.type-demo .mono{font:13px/1.7 ui-monospace,Menlo,monospace;margin-top:18px;
  color:var(--muted);word-spacing:.1em}
.sizes{display:flex;gap:26px;align-items:flex-end;flex-wrap:wrap;margin-top:22px;
  border:1px solid var(--line);border-radius:2px;padding:24px;background:var(--card)}
.sizes figure{margin:0;text-align:center}
.sizes figcaption{font:11px ui-monospace,Menlo,monospace;color:var(--muted);margin-top:10px}
.misuse{display:grid;grid-template-columns:repeat(auto-fit,minmax(120px,1fr));gap:12px;margin-top:20px}
.misuse figure{aspect-ratio:1;border:1px solid var(--line);display:grid;place-items:center;
  padding:14px;background:var(--card);border-radius:2px;position:relative}
.misuse svg{width:100%;height:auto;opacity:.28}
.misuse figcaption{position:absolute;bottom:6px;left:0;right:0;text-align:center;
  font:10px ui-monospace,Menlo,monospace;color:#8a2b27}
.nav{display:flex;gap:14px;flex-wrap:wrap;margin-top:34px;font-size:14px}
.nav a{border:1px solid var(--ink);border-radius:999px;padding:9px 18px;text-decoration:none}
.nav a.here{background:var(--ink);color:var(--paper)}
footer{margin-top:70px;padding-top:20px;border-top:1px solid var(--line);
  font:12px ui-monospace,Menlo,monospace;color:var(--muted);display:flex;
  justify-content:space-between;gap:16px;flex-wrap:wrap}
@media(max-width:820px){.grid2,.grid3{grid-template-columns:1fr}.wrap{padding:0 18px 70px}}
@media(prefers-reduced-motion:reduce){*{scroll-behavior:auto}}
"""


def board(d: dict) -> str:
    c = {"ink": d["palette"][0][1], "paper": d["palette"][1][1],
         "accent": d["accents"][0]}
    dark = {"ink": "#16191C", "paper": d["palette"][1][1],
            "accent": d["accents"][0]}

    # Construction figure: the mark on its own 120-unit grid.
    grid_svg = (
        f'<svg viewBox="0 0 120 120" role="img" aria-label="construction grid">'
        f'<defs><pattern id="g{d["key"]}" width="6" height="6" patternUnits="userSpaceOnUse">'
        f'<path d="M6 0H0V6" fill="none" stroke="{d["palette"][4][1]}" stroke-width=".4"/>'
        f'</pattern></defs>'
        f'<rect width="120" height="120" fill="url(#g{d["key"]})"/>'
        f'<rect x="12" y="12" width="96" height="96" fill="none" stroke="{d["accents"][0]}" '
        f'stroke-width=".8" stroke-dasharray="3 2" opacity=".8"/>'
        f'{d["mark"](c)}</svg>')

    small_variant = mark_c_small if d["key"] == "c" else d["mark"]

    def lock_fig(vid, name, note, mono=False):
        s = lockup_svg(d, vid, dark if mono else c, mono)
        return (f'<figure class="on-dark" if mono else "figure">'
                f'<div class="view">{s}</div>'
                f'<figcaption><b>{vid}</b> · {name}<br>{note}<br>'
                f'<code>{vid.lower()}-{"mono" if mono else "light"}</code></figcaption></figure>')

    pal = "".join(
        f'<figure><div class="chip" style="background:{hexv}"></div>'
        f'<div class="meta"><b>{nm}</b>{role}<br><code>{hexv}</code> · {prop}</div></figure>'
        for nm, hexv, role, prop in d["palette"])

    locks = "".join(lock_fig(v, n, note) for v, n, note in d["lockups"])
    monos = "".join(lock_fig(v, n, "tek renk", mono=True) for v, n, note in d["lockups"][:3])

    sizes = ""
    for px in (512, 256, 128, 64, 32, 16):
        m = small_variant if px <= 24 else d["mark"]
        s = _svg(120, 120, m(c), "size test")
        sizes += (f'<figure><div style="width:{px}px;max-width:100%">{s}</div>'
                  f'<figcaption>{px}px</figcaption></figure>')

    mis = d["mark"](c)
    misuse = "".join(
        f'<figure><svg viewBox="0 0 120 120">{g}</svg><figcaption>{lab}</figcaption></figure>'
        for g, lab in [
            (f'<g transform="rotate(9 60 60)">{mis}</g>', "döndürme"),
            (f'<g transform="translate(60,60) scale(1.35,.78) translate(-60,-60)">{mis}</g>', "esnetme"),
            (f'<g style="filter:invert(1)">{mis}</g>', "sistem dışı renk"),
            (mis.replace(d["accents"][0], "#3a7bd5"), "renk değiştirme"),
        ])

    return f"""<!doctype html>
<html lang="tr">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>Çin Eğitim — Yön {d['key'].upper()} · {d['name']} / {d['en']}</title>
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Archivo:wght@400;500;600;700&family=IBM+Plex+Mono:wght@400;500&family=Newsreader:ital,wght@0,400;0,500;1,400&family=Figtree:wght@400;500;600&family=Space+Grotesk:wght@400;500;700&family=JetBrains+Mono:wght@400;500&display=swap" rel="stylesheet">
<style>{STYLE}</style>
</head>
<body>
<div class="wrap">

<div class="crumb">
  <a href="../../../docs/cin-egitim/index.html">Çin Eğitim</a><span>›</span>
  <a href="../../../docs/cin-egitim/index.html">Yönler</a><span>›</span>
  <b>Yön {d['key'].upper()} — {d['name']}</b>
</div>

<p class="kicker">CREATIVE DIRECTION {d['key'].upper()} · TAHMİN EDİLMİŞ FİKİR · İNSAN ONAYI BEKLENİYOR</p>
<h1>{d['name']}<br><span style="opacity:.42">{d['en']}</span></h1>
<p class="sub">{d['concept']}</p>

<section>
  <p class="kicker">01 · KAVRAM</p>
  <h2>Fikir</h2>
  <p>{d['thesis']}</p>
  <div class="box"><b>İşlev:</b> {d['function']}</div>
  <div class="box"><b>Neden bu:</b> {d['why']}</div>
  <div class="box risk"><b>Risk — insan düzeltmesi için not:</b> {d['risk']}</div>
</section>

<section>
  <p class="kicker">02 · İŞARET</p>
  <h2>Marka geometrisi</h2>
  <div class="grid2">
    <div>
      <div class="stage"><div class="mark">{grid_svg}</div></div>
      <p class="kicker" style="margin-top:12px">Kurulum ızgarası · 6 birim modül</p>
    </div>
    <div>
      <div class="stage"><div class="mark">{d['mark'](c)}</div></div>
      <p class="kicker" style="margin-top:12px">İzole işaret</p>
      <div class="stage dark" style="margin-top:14px"><div class="mark">{d['mark']({'ink':'#F4F1EA','accent':d['accents'][0]})}</div></div>
      <p class="kicker" style="margin-top:12px;color:var(--muted)">Koyu zemin</p>
    </div>
  </div>
  <dl class="spec">
    <dt>Modül</dt><dd>{d['grid'][0]}</dd>
    <dt>Ağırlık</dt><dd>{d['grid'][1]}</dd>
    <dt>Geometri</dt><dd>{d['grid'][2]}</dd>
    <dt>Güvenli alan</dt><dd>{d['grid'][3]}</dd>
  </dl>
</section>

<section>
  <p class="kicker">03 · KİLİT AİLESİ</p>
  <h2>Beş rol, tek işaret</h2>
  <p>Bu beiz düzen gerçek SVG geometrisiyle birleştirilmiştir; tarif edilmemektedir.
     Kelime-marka bu panoda canlı yazı tipiyle gösterilir — <b>üretimde dışa
     çizilmiş yol (outline path) olarak teslim edilir</b>, böylece istemcinin
     makinesinde yazı tipi değişimi olamaz.</p>
  <div class="lock">{locks}</div>
  <h3 style="margin-top:38px">Tek renk varyantları</h3>
  <div class="lock">{monos}</div>
  <h3 style="margin-top:38px">Gerçek boyut testi</h3>
  <div class="sizes">{sizes}</div>
  <div class="box risk" style="margin-top:18px"><b>Küçük boyut bulgusu:</b> {d['smallsize']}</div>
  <p class="kicker" style="margin-top:14px">32px altında varyant değişebilir;
     her markanın küçük boyut kuralı ayrıca kanıtlanmalıdır.</p>
</section>

<section>
  <p class="kicker">04 · RENK</p>
  <h2>Palet</h2>
  <div class="sw">{pal}</div>
  <div class="box" style="margin-top:22px"><b>Tek vurgu kuralı:</b> vurgu rengi
    yalnız imza işinde ve tek bir grafik aygıtta yaşar. Dolgu, yüzey veya
    dekorasyon rengi olarak kullanılmaz. Aksi hâlde sistem dağılır ve
    imza gücünü kaybeder.</div>
</section>

<section>
  <p class="kicker">05 · TİPOGRAFİ</p>
  <h2>Yazı</h2>
  <div class="type-demo" style="font-family:{d['display']}">
    <div class="big">ÇİN EĞİTİM</div>
    <div class="en">EDUCATION IN CHINA</div>
    <div class="mono">39°54′06″N 116°23′29″E · 23335 PROGRAM · 4 ADIM · 1 MERİDYEN</div>
  </div>
  <dl class="spec">
    <dt>Display</dt><dd>{d['display']}<br><b>{d['display_wght']}</b></dd>
    <dt>Arayüz</dt><dd>{d['mono']}<br><b>{d['mono_wght']}</b></dd>
    <dt>Lisans</dt><dd>{d['fonts']}</dd>
  </dl>
</section>

<section>
  <p class="kicker">06 · DİL</p>
  <h2>Grafik gramer</h2>
  <dl class="spec">
    <dt>Gramer</dt><dd>{d['grammar']}</dd>
    <dt>Aygıt</dt><dd>{d['device']}</dd>
    <dt>Desen</dt><dd>{d['pattern']}</dd>
    <dt>Görsel</dt><dd>{d['imagery']}</dd>
    <dt>Malzeme</dt><dd>{d['material']}</dd>
  </dl>
</section>

<section>
  <p class="kicker">07 · YANLIŞ KULLANIM</p>
  <h2>Dört yasak</h2>
  <div class="misuse">{misuse}</div>
</section>

<div class="nav">
  <a href="../../../docs/cin-egitim/index.html">← Üç yön</a>
  {''.join(f'<a href="{o}.html">{x}</a>' for o, x in [
      ('direction-a', 'Yön A · KAYIT'), ('direction-b', 'Yön B · KALEM'),
      ('direction-c', 'Yön C · KOORDİNAT')] if o != d['slug'])}
</div>

<footer>
  <span>Çin Eğitim · Yön {d['key'].upper()} · {d['name']} / {d['en']}</span>
  <span>Görsel üretim çağrısı: 0 · Kanonikleştirme: yok · İnsan seçimi bekleniyor</span>
</footer>
</div>
</body>
</html>
"""


def index_page() -> str:
    cards = []
    for d in DIRECTIONS:
        c = {"ink": d["palette"][0][1], "accent": d["accents"][0]}
        sw = "".join(f'<i style="background:{h}"></i>' for _n, h, _r, _p in d["palette"][:4])
        cards.append(f"""<a class="card" href="boards/{d['slug']}.html">
  <div class="art">{d['mark'](c)}</div>
  <span class="tag">YÖN {d['key'].upper()}</span>
  <b>{d['name']}</b><span class="en">{d['en']}</span>
  <p>{d['concept']}</p>
  <div class="swatch">{sw}</div>
  <span class="go">Panonu aç →</span>
</a>""")

    audit_rows = "".join(
        f'<tr><td>{k}</td><td><code>{v}</code></td></tr>' for k, v in [
            ("primary / destructive", "#8f1f2d"), ("accent-foreground", "#741723"),
            ("accent", "#f7ecee"), ("navy", "#3a1720"), ("foreground", "#20252b"),
            ("muted / muted-fg", "#f2f3f4 / #626970"), ("border / input", "#e3e5e7 / #dfe2e5"),
            ("font-family", "Arial, Helvetica, sans-serif"),
            ("logo raster", "120×116 px PNG"),
        ])

    return f"""<!doctype html>
<html lang="tr">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>Çin Eğitim — Brand Studio</title>
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Archivo:wght@400;500;600;700&family=IBM+Plex+Mono:wght@400;500&display=swap" rel="stylesheet">
<style>{PANEL_STYLE}</style>
</head>
<body>
<div class="wrap">

<div class="brandbar" role="navigation" aria-label="Marka seçimi">
  <span class="blab">Marka</span>
  <div class="opts">
    <a class="opt" href="../">
      <img src="../asyada-seal/assets/v01-canonical.svg" alt="">
      <span class="txt"><span class="on">Asya'da Eğitim</span><span class="sub">Education in Asia · KANONİK</span></span>
    </a>
    <a class="opt here" href="./" aria-current="true">
      <span class="pending" aria-hidden="true">YÖN<br>PANOSU</span>
      <span class="txt"><span class="on">Çin Eğitim</span><span class="sub">Education in China · YÖN SEÇİMİ BEKLENİYOR</span></span>
    </a>
  </div>
</div>

<div class="crumb">
  <a href="../index.html">Brand Studio</a><span>›</span>
  <b>Çin Eğitim</b>
</div>

<p class="kicker">ÇİN EĞİTİM · KİMLİK ARAŞTIRMASI · AYRI SÜREÇ</p>
<h1>Çin Eğitim</h1>
<p class="sub">Çin odaklı eğitim danışmanlığı için sıfırdan bir kimlik. Asya'da
Eğitim ile paylaşılan tek şey bu klasörün çalışma <b>disiplini</b>; varlık,
karar, araç ve kanon hiçbir şey paylaşılmıyor.</p>
<div class="pending">ÜÇ YÖN PENDİNG · HİÇBİR ŞEY KANONİKLEŞTİRİLMEDİ · İNSAN SEÇİMİ GEREKLİ</div>

<section>
  <p class="kicker">01 · MEVCUT DURUMUN ÖLÇÜMÜ</p>
  <h2>Canlı siteden çıkarılan gerçek token'lar</h2>
  <p>Üretim CSS'i (<code>/_next/static/css/index.Co_vgAiy.css</code>, 214 923 bayt)
     doğrudan okundu. Aşağıdakiler tahmin değil ölçümdür.</p>
  <div class="scroll"><table>
    <tr><th>Token</th><th>Canlı değer</th></tr>
    {audit_rows}
  </table></div>
  <div class="iso">
    <div>
      <h3>Logo denetimi</h3>
      <p><code>cinegitim-logo.png</code> · PNG 120×116 RGBA ·
      SHA-256 <code>0b53aa17feb…</code>. Dört ayrı fikir tek işarette: pagoda
      siluetleri, kırmızı fırça hilal (Japonya okunuyor), kurt, gri dağlar.
      Tek bir fikir yok; 120 px'te çatı hatları ~6 px, kurt bacakları ~2 px.
      Favicon boyutu, tek renk varyantı ve güvenli alan kuralı mevcut değil.</p>
      <p class="path">Nihai izlenim: turizm acentesi. Seçici akademik danışmanlık değil.</p>
    </div>
    <div>
      <h3>Sonuç</h3>
      <p>Canlı kimlik tarayıcı varsayılan yazı tipi yığını, ulusal sembol
      kolajı ve raster bir logodan ibaret. Kelime-marka, tipografi, ızgara,
      palet disiplini, kilit ailesi ve tasarım dili <b>hiçbiri</b> yok.
      Kurulacak ve kilitlenecek olan tam olarak budur.</p>
      <p class="path">Çin Eğitim kendi kimliğini kuracak — Asya'da Eğitim ile aynı değil, aynı yöntemle.</p>
    </div>
  </div>
</section>

<section>
  <p class="kicker">02 · ÜÇ YÖN</p>
  <h2>Üç ayrı dünya</h2>
  <p>Üçü de kavramsal olarak ve grafik gramer olarak birbirinden ayrıdır:
     bürokratik kayıt, hareket ekonomisi, koordinat ölçümü.
     <b>Palet takas testi</b> uygulanmalıdır — üç palet birbiriyle değiştirildiğinde
     kavramlar ayakta kalmalıdır. Paletlerin taşıdığı şey fikirdir, kavramsız
     bir yön paletle taşınmamalıdır.</p>
  <div class="cards">{''.join(cards)}</div>
</section>

<section>
  <p class="kicker">03 · İZOLASYON</p>
  <h2>Tamamen ayrı süreç</h2>
  <div class="iso">
    <div>
      <h3>Çin Eğitim</h3>
      <p><code>brands/cin-egitim/</code> · <code>brands/cin-egitim/boards/</code><br>
      <code>brands/cin-egitim/assets/lockups/</code><br>
      <code>brands/cin-egitim/decisions/</code><br>
      <code>docs/cin-egitim/</code><br>
      <code>studio/tools/cin-egitim/</code><br>
      Doğrulayıcı: <code>cin-egitim/verify_cin_canonical_lockups.py</code></p>
    </div>
    <div>
      <h3>Asya'da Eğitim</h3>
      <p><code>brands/asyada-egitim/</code><br>
      <code>docs/asyada-seal/</code><br>
      <code>studio/tools/verify_asyada_canonical_lockups.py</code><br>
      <br>
      Hiçbir dosya paylaşılmıyor. Çin Eğitim araçları Asya'da Eğitim
      dosyalarını okumaz; Asya'da Eğitim araçları Çin Eğitim dosyalarını
      okumaz. Manifest'ler ayrı, SHA'lar ayrı, karar kayıtları ayrı.</p>
    </div>
  </div>
  <div class="iso" style="margin-top:20px">
    <div>
      <h3>Ortak olan tek yüzey</h3>
      <p>Yayın panelindeki marka geçişi (<code>docs/index.html</code>). İki marka
      arasında geçiş yapar, ortak varlık kullanmaz, ortak kural uygulamaz.</p>
    </div>
    <div>
      <h3>Branch</h3>
      <p><code>publish/cin-egitim-identity</code>. Çin Eğitim geliştirme süreci
      bu branch'te yürür; <code>main</code> ve Asya'da Eğitim branch'lerine
      dokunulmaz.</p>
    </div>
  </div>
</section>

<footer>
  <span>Çin Eğitim Brand Studio · üç yön · seçim bekleniyor</span>
  <span>Görsel üretim çağrısı: 0 · Kanonik dosya: 0 · İzole: evet</span>
</footer>
</div>
</body>
</html>
"""


def main() -> None:
    BOARDS.mkdir(parents=True, exist_ok=True)
    DOC.mkdir(parents=True, exist_ok=True)
    for d in DIRECTIONS:
        (BOARDS / f"{d['slug']}.html").write_text(board(d), encoding="utf-8")
    (DOC / "index.html").write_text(index_page(), encoding="utf-8")
    # Boards are also published under docs/ so Pages can serve them standalone.
    pub = DOC / "boards"
    pub.mkdir(parents=True, exist_ok=True)
    for d in DIRECTIONS:
        text = (BOARDS / f"{d['slug']}.html").read_text(encoding="utf-8")
        text = text.replace('href="../../../docs/cin-egitim/', 'href="../')
        (pub / f"{d['slug']}.html").write_text(text, encoding="utf-8")
    print(json.dumps({
        "boards": [f"brands/cin-egitim/boards/{d['slug']}.html" for d in DIRECTIONS],
        "published": f"docs/cin-egitim/index.html (+{len(DIRECTIONS)} board pages)",
        "image_generation_calls": 0,
        "canonicalised": 0,
        "status": "HUMAN DIRECTION SELECTION PENDING",
    }, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()