#!/usr/bin/env python3
"""Çin Eğitim — panel. Asya'da Eğitim panelinin tasarım dili, Çin Eğitim verisiyle.

Tasarım dili kasıtlı olarak Asya'da Eğitim ile aynı tutulur: aynı krem kâğıt,
aynı mürekkep, aynı kart ritmi, aynı tipografi ölçeği, aynı rozet mantığı. Panel
bir markanın kimliği değil, stüdyonun arayüzüdür; iki marka aynı paneli
kullandığında geçiş inandırıcı olur.

Marka tarafı ayrıdır ve ayrı kalır: Çin'in kırmızısı ölçülmüş #A72820, kendi
mürekkebi #292929, kendi işareti (enso).

Veri kaynağı:
    docs/cin-egitim/board-data.json  (ölçüm + yeniden kurulum sonuçları)

Görsel üretim çağrısı: 0.  Kanonikleştirme: YOK.
"""
from __future__ import annotations

from pathlib import Path
import json
import re

ROOT = Path(__file__).resolve().parents[3]
BRAND = ROOT / "brands/cin-egitim"
DOC = ROOT / "docs/cin-egitim"
ENSO_SVG = BRAND / "explorations/enso/enso-reconstruction.svg"
DATA = DOC / "board-data.json"

PANEL_STYLE = """
*{box-sizing:border-box;margin:0;padding:0}
:root{
  --paper:#F7F3E9; --ink:#1D2027; --red:#A72820; --ink-cn:#292929;
  --line:#d9d1bf; --muted:#65625a; --card:#fffdf7;
}
body{background:var(--paper);color:var(--ink);
  font:16px/1.55 "Archivo","Helvetica Neue",Arial,sans-serif;
  -webkit-font-smoothing:antialiased}
.wrap{max-width:1180px;margin:0 auto;padding:0 28px 100px}
a{color:inherit;text-decoration:none}
img,svg{display:block;max-width:100%}
code{font:12px ui-monospace,Menlo,monospace}

/* ---- marka geçişi (Asya paneliyle aynı bileşen) ---- */
.brandbar{display:flex;gap:14px;align-items:center;flex-wrap:wrap;
  padding:18px 0 16px;border-bottom:1px solid var(--ink)}
.brandbar .blab{font-size:12px;letter-spacing:.14em;font-weight:500;color:var(--muted)}
.brandbar .opts{margin-left:auto;display:flex;gap:8px;flex-wrap:wrap}
.opt{display:flex;align-items:center;gap:9px;border:1px solid var(--line);
  border-radius:999px;padding:7px 15px;background:var(--card);min-height:44px}
.opt:hover{border-color:var(--ink)}
.opt.here{border-color:var(--ink);background:var(--ink);color:var(--paper)}
.opt img,.opt svg{width:26px;height:26px;flex:none}
.opt .pending{width:26px;height:26px;border:1.5px dashed var(--muted);border-radius:5px;
  display:grid;place-items:center;font:8px/1.1 ui-monospace,Menlo,monospace;color:var(--muted)}
.opt.here .pending{border-color:var(--paper);color:var(--paper)}
.opt .nm{font-size:14px;font-weight:500}
.opt.here .nm{font-weight:600}

/* ---- topbar (Asya ile aynı) ---- */
.topbar{display:flex;align-items:center;gap:14px;padding:22px 0;
  border-bottom:1px solid var(--ink)}
.topbar .mark{width:40px;height:auto}
.topbar .t{font-size:13px;letter-spacing:.14em;font-weight:500}
.topbar nav{margin-left:auto;display:flex;gap:8px;flex-wrap:wrap}
.topbar nav a{font-size:13px;border:1px solid var(--line);border-radius:999px;
  padding:8px 16px;background:var(--card)}
.topbar nav a.here,.topbar nav a:hover{border-color:var(--ink)}

.hero{display:grid;grid-template-columns:230px 1fr;gap:44px;align-items:center;
  padding:64px 0 20px}
.hero .enso{width:230px;height:auto}
h1{font-size:clamp(44px,7vw,84px);line-height:1;letter-spacing:-.045em;font-weight:600}
.lede{font-size:19px;max-width:58ch;margin-top:16px;color:#33302a}
.badges{display:flex;gap:10px;flex-wrap:wrap;margin-top:22px}
.badge{font-size:12px;letter-spacing:.08em;font-weight:500;border-radius:999px;
  padding:8px 18px;border:1px solid var(--ink)}
.badge.ok{background:var(--ink);color:var(--paper)}
.badge.live{border-color:var(--red);color:var(--red)}
.badge.old{border-color:var(--line);color:var(--muted)}

section.block{margin-top:72px}
.kicker{font-size:12px;letter-spacing:.16em;color:var(--muted);font-weight:500}
h2{font-size:clamp(28px,4vw,44px);letter-spacing:-.03em;margin:8px 0 6px;font-weight:600}
.sub{color:#3d3a34;max-width:72ch}

.cards{display:grid;grid-template-columns:repeat(auto-fit,minmax(290px,1fr));
  gap:16px;margin-top:26px}
.card{display:block;background:var(--card);border:1px solid var(--ink);
  border-radius:14px;padding:26px 24px}
.card:hover{box-shadow:6px 6px 0 var(--ink)}
.card.first{grid-column:1/-1;display:grid;grid-template-columns:1fr 300px;
  gap:28px;align-items:center;background:var(--ink);color:var(--paper);
  border-color:var(--ink)}
.card.first:hover{box-shadow:6px 6px 0 var(--red)}
.card.first .enso{width:280px;max-width:100%;height:auto;margin:auto}
.card .tag{font-size:11px;letter-spacing:.14em;color:var(--red);font-weight:600}
.card.first .tag{color:#ff9c94}
.card b.t{display:block;font-size:24px;margin:8px 0 4px;letter-spacing:-.01em;font-weight:600}
.card p{font-size:15px;opacity:.85}
.card .go{font-size:13px;margin-top:14px;display:inline-block;
  border-bottom:2px solid var(--red);padding-bottom:2px}
.card .enso{width:132px;margin:18px auto 4px}

.compare{display:grid;grid-template-columns:1fr 1fr;gap:18px;margin-top:26px}
.compare figure{margin:0;border:1px solid var(--line);border-radius:14px;
  background:var(--card);padding:18px}
.compare .shot{background:var(--card);border-radius:8px;overflow:hidden}
.compare .shot img{width:100%;height:auto}
.compare figcaption{font-size:13px;color:var(--muted);margin-top:10px}
.compare b{color:var(--ink);font-weight:600}

.stats{display:grid;grid-template-columns:repeat(auto-fit,minmax(150px,1fr));
  gap:12px;margin-top:24px}
.stats figure{border:1px solid var(--line);border-radius:10px;padding:16px 18px;
  background:var(--card)}
.stats b{display:block;font-size:26px;letter-spacing:-.02em;font-weight:600}
.stats span{font-size:12.5px;color:var(--muted)}
.scroll{overflow-x:auto;border:1px solid var(--line);border-radius:10px;margin-top:20px}
table{border-collapse:collapse;width:100%;font-size:14px;min-width:460px}
th,td{text-align:left;padding:11px 14px;border-bottom:1px solid var(--line)}
th{font-size:11px;letter-spacing:.09em;text-transform:uppercase;color:var(--muted);font-weight:600}

.iso{display:grid;grid-template-columns:1fr 1fr;gap:20px;margin-top:24px}
.iso div{border:1px solid var(--line);border-radius:14px;padding:22px;background:var(--card)}
.iso h3{font-size:15px;margin-bottom:10px;font-weight:600}
.iso p{font-size:14px;color:#3d3a34}
.iso code{color:var(--red);overflow-wrap:anywhere}

footer{margin-top:90px;border-top:1px solid var(--line);padding-top:22px;
  font-size:13px;color:var(--muted);display:flex;gap:16px;flex-wrap:wrap;
  justify-content:space-between}

@media(max-width:820px){
  .hero{grid-template-columns:1fr;gap:24px}
  .hero .enso{width:160px}
  .card.first{grid-template-columns:1fr}
  .compare,.iso{grid-template-columns:1fr}
  .wrap{padding:0 18px 70px}
  .brandbar .opts{margin-left:0;width:100%}
}
"""


def enso_mark(colour: str, size: int | None = None) -> str:
    """Enso'yu içeriden göm. <img> dış dosyaya bağımlılık yaratır ve Pages'ta
    göreli yol kırılganlığı getirir."""
    s = ENSO_SVG.read_text(encoding="utf-8")
    path_el = re.search(r"<path[^>]*/>", s).group(0)
    path_el = re.sub(r'fill="[^"]*"', f'fill="{colour}"', path_el)
    vb = re.search(r'viewBox="([^"]+)"', s).group(1)
    dims = f' width="{size}" height="{size}"' if size else ""
    return (f'<svg viewBox="{vb}"{dims} role="img" '
            f'aria-label="Çin Eğitim — enso">{path_el}</svg>')


def render(src_rel: str, out_rel: str, alt: str, caption: str) -> str:
    return (f'<figure><div class="shot"><img src="{src_rel}" alt="{alt}"></div>'
            f'<figcaption><b>{caption}</b></figcaption></figure>')


def main() -> None:
    DOC.mkdir(parents=True, exist_ok=True)
    (DOC / "assets").mkdir(parents=True, exist_ok=True)

    prof = json.loads((BRAND / "explorations/enso/enso-profile.json").read_text())
    data = json.loads(DATA.read_text()) if DATA.exists() else {}
    meas = data.get("fidelity", {})

    # Kaynak ve yeniden kurulum karşılaştırma görselini yayın klasörüne kopyala
    for name in ("enso-final.png",):
        s = Path("/private/var/folders/3j/ffljsl_s66n94xjq7zdv8hb80000gn/T/opencode") / name
        if s.exists():
            (DOC / "assets" / name).write_bytes(s.read_bytes())

    enso_red = enso_mark("#A72820")
    enso_paper = enso_mark("#F7F3E9")

    rows = "".join(
        f"<tr><td>{k}</td><td>{v}</td></tr>" for k, v in [
            ("Kaynak dosya", f"{prof['source']['file']} · {prof['source']['size'][0]}×{prof['source']['size'][1]} px"),
            ("Kaynak SHA-256", f"<code>{prof['source']['sha256'][:32]}…</code>"),
            ("Ana yay", f"{prof['arc'][0]:.0f}° → {prof['arc'][1]:.0f}° ({prof['arc'][1]-prof['arc'][0]:.0f}°)"),
            ("Merkez", f"({prof['centre'][0]}, {prof['centre'][1]})"),
            ("Medyan darbe genişliği", f"{prof['median_width']} birim"),
            ("Doğrudan ölçülen açı", f"{prof['angles_measured_directly']} / {prof['angles_sampled']}"),
            ("İnterpolasyonla onarılan", f"{prof['angles_interpolated']} açı"),
            ("Doku politikası", "kuru fırça ve kâğıt greni <b>bilinçli olarak düşürüldü</b>"),
            ("Silüet IoU (kaynak)", f"<b>{meas.get('iou', '—')}</b>"),
            ("Alan oranı", f"{meas.get('area_ratio', '—')} (kalan fark = düşürülen doku)"),
        ])

    cards = "".join(f"""<a class="card" href="boards/{d['slug']}.html">
<span class="tag">YÖN {d['key'].upper()}</span>
<div class="enso">{enso_red}</div>
<b class="t">{d['name']}</b>
<p>{d['concept']}<br><span style="opacity:.6">{d['grammar']}</span></p>
<span class="go">Panonu aç →</span></a>""" for d in data.get("directions", []))

    html = f"""<!doctype html>
<html lang="tr">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>Çin Eğitim — Brand Studio</title>
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Archivo:wght@400;500;600;700&display=swap" rel="stylesheet">
<style>{PANEL_STYLE}</style>
</head>
<body>
<div class="wrap">

<div class="brandbar" role="navigation" aria-label="Marka seçimi">
  <span class="blab">MARKA</span>
  <div class="opts">
    <a class="opt" href="../">
      <img src="../asyada-seal/assets/v01-canonical.svg" alt="">
      <span class="nm">Asya'da Eğitim</span>
    </a>
    <a class="opt here" href="./" aria-current="true">
      <span class="pending">YÖN</span>
      <span class="nm">Çin Eğitim</span>
    </a>
  </div>
</div>

<div class="topbar">
  <span class="mark">{enso_red}</span>
  <span class="t">ÇİN EĞİTİM &middot; BRAND STUDIO</span>
  <nav>
    <a class="here" href="./">Panel</a>
    <a href="#enso">Enso</a>
    <a href="#yonler">Yönler</a>
    <a href="#izolasyon">İzolasyon</a>
  </nav>
</div>

<div class="hero">
  <span class="enso">{enso_red}</span>
  <div>
    <h1>Brand Studio</h1>
    <p class="lede">Çin odaklı eğitim danışmanlığı için logonun yeniden kurulumu,
    ölçümü ve tasarım dili. Çalışma logonun kendi enso fırça darbesinden başlar;
    yön panoları paralel olarak inceleniyor.</p>
    <div class="badges">
      <span class="badge live">ENSO — ÖLÇÜLDÜ VE VEKTRÖRLEŞTİRİLDİ</span>
      <span class="badge ok">ÖLÇÜM IoU {meas.get('iou', '—')}</span>
      <span class="badge old">ÜÇ YÖN — İNSAN SEÇİMİ BEKLENİYOR</span>
    </div>
  </div>
</div>

<section class="block" id="enso">
  <div class="kicker">01 &middot; LOGO — KAYNAKTAN GEOMETRİYE</div>
  <h2>Enso yeniden kurulumu</h2>
  <p class="sub">Logonun ağırlıklı kısmı kırmızı enso'dur: 125 869 kırmızı
  pikselin 123 070'i, yani %98'i. Bu, tek fırça darbeyle çizilmiş 256°'lik bir
  yaydır. Kilitlenebilir bir varlık vektör olmak zorunda olduğu için raster
  ölçülüp gerçek SVG yola çevrildi.</p>
  <div class="compare">
    {render("assets/enso-final.png", "", "Kaynak 862×834 raster ile yeniden kurulumun yan yana karşılaştırması", "Kaynak ↔ yeniden kurulum · 862×834")}
  </div>
  <div class="scroll"><table>{rows}</table></div>
  <div class="card first" style="margin-top:26px">
    <div>
      <span class="tag">ÖLÇÜLEN KARAR</span>
      <b class="t">Doku atıldı, hareket korundu</b>
      <p>Kaynaktaki kuru fırça beyaz boşlukları ve kâğıt greni bir resim
      dokusudur. 16px'te ve tek renk üretimde yeniden üretilemez, yalnızca
      bulanıklaştırır. Yeniden kurulum bu dokuyu bilinçli olarak düşürür ve
      yalnız hareketi korur: açık yay, ölçülmüş değişken genişlik, iki uçta
      fırça kalkışı. Bu bir güzelleştirme değil, bir üretim kısıtıdır.</p>
    </div>
    <span class="enso">{enso_paper}</span>
  </div>
</section>

<section class="block" id="yonler">
  <div class="kicker">02 &middot; ÜÇ YÖN</div>
  <h2>Paralel araştırma</h2>
  <p class="sub">Logodan yola çıkıyoruz; yönler ise aynı anda araştırılıyor.
  Hiçbiri kanonik değildir ve seçim yapılmadan kilit dosyası üretilmez.</p>
  <div class="cards">{cards}</div>
</section>

<section class="block" id="izolasyon">
  <div class="kicker">03 &middot; AYRI SÜREÇ</div>
  <h2>İzolasyon</h2>
  <div class="iso">
    <div>
      <h3>Çin Eğitim</h3>
      <p><code>brands/cin-egitim/</code><br>
      <code>docs/cin-egitim/</code><br>
      <code>studio/tools/cin-egitim/</code><br>
      Ölçüm: <code>build_enso.py</code></p>
    </div>
    <div>
      <h3>Asya'da Eğitim</h3>
      <p><code>brands/asyada-egitim/</code><br>
      <code>docs/asyada-seal/</code><br>
      <code>studio/tools/verify_asyada_canonical_lockups.py</code><br>
      Hiçbir dosya paylaşılmıyor.</p>
    </div>
  </div>
</section>

<footer>
  <span>Çin Eğitim Brand Studio &middot; enso kaynak SHA <code>{prof['source']['sha256'][:12]}…</code></span>
  <span>Görsel üretim çağrısı: 0 &middot; Kanonikleştirilen dosya: 0</span>
</footer>
</div>
</body>
</html>
"""
    (DOC / "index.html").write_text(html, encoding="utf-8")
    print(json.dumps({"panel": "docs/cin-egitim/index.html",
                      "measurements": meas,
                      "image_generation_calls": 0,
                      "canonicalised": 0}, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()