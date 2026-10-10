#!/usr/bin/env python3
"""Build vector-first type-study HTML boards around the untouched canonical mark."""
from __future__ import annotations
import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[4]
SOURCE = Path(__file__).resolve().parent
DOCS = ROOT / "docs/cin-egitim/typography-round-01"
DATA = json.loads((SOURCE / "directions.json").read_text())
FONT_LINKS = '''<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Barlow+Condensed:wght@500;600;700;800&family=Manrope:wght@400;500;600;700;800&family=Source+Serif+4:opsz,wght@8..60,400..700&display=swap" rel="stylesheet">'''

CSS = r'''*{box-sizing:border-box}html{scroll-behavior:smooth}body{margin:0;background:#f5f0e7;color:#202020;font:16px/1.6 Manrope,Arial,sans-serif}a{color:inherit}a:focus-visible{outline:3px solid #bf0c1a;outline-offset:4px}main{max-width:1160px;padding:28px 24px 72px;margin:auto}.mast{display:flex;align-items:center;justify-content:space-between;gap:16px;border-bottom:1px solid #c9c1b5;padding-bottom:14px}.eyebrow,.tag{font:600 11px/1.4 Manrope,Arial,sans-serif;letter-spacing:.14em;text-transform:uppercase;color:#655f57}.mast a,.back{font-size:13px;text-decoration:none;border-bottom:1px solid #bf0c1a}.intro{display:grid;grid-template-columns:88px 1fr;gap:22px;align-items:center;padding:34px 0 28px}.intro img{width:88px;height:88px;object-fit:contain}.intro h1{font:600 clamp(34px,5vw,58px)/1.02 'Source Serif 4',Georgia,serif;letter-spacing:-.035em;margin:2px 0 8px}.intro p{max-width:68ch;color:#514c45;margin:0}.notice{font-size:13px;background:#fffdf8;border-left:3px solid #bf0c1a;padding:12px 16px;margin:8px 0 28px}.chooser{display:grid;grid-template-columns:repeat(3,minmax(0,1fr));gap:16px}.option{min-width:0;background:#fffdf8;border:1px solid #d5cec2;border-radius:14px;padding:18px;text-decoration:none;display:flex;flex-direction:column;transition:box-shadow .15s,border-color .15s}.option:hover{border-color:#202020;box-shadow:4px 4px 0 #202020}.option h2{font:600 24px/1.1 Manrope,Arial,sans-serif;margin:8px 0 5px}.option p{font-size:14px;color:#514c45;margin:0 0 14px}.option .go{margin-top:auto;padding-top:12px;font-size:13px;border-bottom:1px solid #bf0c1a;align-self:flex-start}.preview{min-height:176px;display:grid;place-items:center;background:#f5f0e7;border:1px solid #e5ded2;border-radius:10px;padding:14px}.lockup{color:#202020}.lockup img{display:block;object-fit:contain;flex:none}.lockup-a{display:flex;align-items:center;gap:16px}.lockup-a img{width:72px;height:72px}.word-a{display:flex;flex-direction:column;font:500 35px/.94 'Source Serif 4',Georgia,serif;letter-spacing:-.045em}.lockup-b{display:flex;flex-direction:column;align-items:center;gap:11px}.lockup-b img{width:72px;height:72px}.word-b{font:700 24px/1 Manrope,Arial,sans-serif;letter-spacing:-.055em}.word-b span{font-weight:500}.lockup-c{display:flex;align-items:center;gap:13px}.lockup-c img{width:68px;height:68px}.word-c{border-left:2px solid #bf0c1a;padding-left:12px;display:flex;flex-direction:column;font:700 31px/.84 'Barlow Condensed','Arial Narrow',sans-serif;letter-spacing:.055em}.cards-head{display:flex;align-items:end;justify-content:space-between;gap:20px;margin:32px 0 14px}.cards-head h2{font:600 23px/1.2 Manrope,Arial,sans-serif;margin:0}.cards-head p{font-size:12px;color:#655f57;margin:0}.dirhead{padding:36px 0 22px}.dirhead .tag{color:#bf0c1a}.dirhead h1{font:600 clamp(38px,6vw,66px)/1 'Source Serif 4',Georgia,serif;letter-spacing:-.04em;margin:8px 0}.dirhead p{max-width:65ch;color:#514c45;margin:0}.detail-lockup{margin:20px 0 28px;padding:clamp(24px,5vw,54px);background:#fffdf8;border:1px solid #d5cec2;border-radius:16px;min-height:270px;display:grid;place-items:center}.detail-lockup .lockup-a img,.detail-lockup .lockup-b img,.detail-lockup .lockup-c img{width:108px;height:108px}.detail-lockup .word-a{font-size:clamp(48px,7vw,76px)}.detail-lockup .word-b{font-size:clamp(36px,5vw,52px)}.detail-lockup .word-c{font-size:clamp(48px,7vw,70px);padding-left:18px}.detail-lockup .lockup-a{gap:24px}.detail-lockup .lockup-b{gap:16px}.detail-lockup .lockup-c{gap:20px}.twocol{display:grid;grid-template-columns:1.2fr .8fr;gap:16px}.panel{background:#fffdf8;border:1px solid #d5cec2;border-radius:14px;padding:20px}.panel h2{font:600 18px/1.3 Manrope,Arial,sans-serif;margin:0 0 12px}.sample{font-size:clamp(40px,7vw,72px);line-height:.98;letter-spacing:-.04em;margin:12px 0 18px}.type-a .sample{font-family:'Source Serif 4',Georgia,serif;font-weight:500}.type-b .sample{font-family:Manrope,Arial,sans-serif;font-weight:700;letter-spacing:-.06em}.type-c .sample{font-family:'Barlow Condensed','Arial Narrow',sans-serif;font-weight:700;letter-spacing:.045em;text-transform:uppercase}.glyphs{border-top:1px solid #ded7cb;padding-top:12px;font-size:18px;letter-spacing:.035em}.glyphs small{display:block;font-size:10px;letter-spacing:.12em;color:#655f57;margin-bottom:5px}.specs{display:grid;grid-template-columns:1fr 1fr;gap:9px 18px;margin:0}.specs div{border-top:1px solid #ded7cb;padding-top:8px}.specs dt{font-size:10px;text-transform:uppercase;letter-spacing:.11em;color:#655f57}.specs dd{font-size:13px;margin:2px 0 0}.sizes{display:flex;align-items:baseline;gap:16px;flex-wrap:wrap;margin-top:14px}.sizes span{font-size:13px}.sizes b{font-weight:600}.footnote{font-size:12px;color:#655f57;margin:18px 0 0}.tag-red{color:#bf0c1a}.pagefoot{display:flex;justify-content:space-between;gap:16px;align-items:center;border-top:1px solid #c9c1b5;margin-top:30px;padding-top:14px;font-size:12px;color:#655f57}.pagefoot a{color:#202020}@media(max-width:820px){.chooser{grid-template-columns:1fr}.option{display:grid;grid-template-columns:minmax(0,1fr) minmax(170px,.8fr);gap:8px 16px}.option .preview{grid-column:2;grid-row:1/5;min-height:150px}.option h2{align-self:end}.option .go{align-self:start}.twocol{grid-template-columns:1fr}}@media(max-width:560px){main{padding:18px 15px 48px}.mast .eyebrow{font-size:9px}.intro{grid-template-columns:58px 1fr;gap:14px;padding:26px 0 20px}.intro img{width:58px;height:58px}.intro h1{font-size:34px}.intro p{font-size:14px}.chooser{gap:12px}.option{grid-template-columns:minmax(0,1fr) 126px;padding:12px;gap:6px 10px}.option .preview{min-height:128px;padding:8px}.lockup-a{gap:8px}.lockup-a img{width:44px;height:44px}.word-a{font-size:23px}.lockup-b{gap:6px}.lockup-b img{width:42px;height:42px}.word-b{font-size:17px}.lockup-c{gap:7px}.lockup-c img{width:41px;height:41px}.word-c{font-size:22px;padding-left:7px}.cards-head{display:block}.cards-head p{margin-top:4px}.dirhead{padding:28px 0 16px}.dirhead h1{font-size:42px}.detail-lockup{min-height:210px;padding:20px}.detail-lockup .lockup-a img,.detail-lockup .lockup-b img,.detail-lockup .lockup-c img{width:72px;height:72px}.detail-lockup .word-a{font-size:46px}.detail-lockup .word-b{font-size:32px}.detail-lockup .word-c{font-size:46px;padding-left:10px}.detail-lockup .lockup-a{gap:14px}.detail-lockup .lockup-c{gap:12px}.specs{grid-template-columns:1fr}.pagefoot{align-items:flex-start;flex-direction:column}}@media(prefers-reduced-motion:reduce){html{scroll-behavior:auto}.option{transition:none}}'''


def lockup(direction, image_src):
    common = f'<img src="{image_src}" alt="Kilitli Çin Eğitim sembolü">'
    slug = direction["slug"]
    if slug == "direction-a":
        word = '<span>Çin</span><span>Eğitim</span>'
    elif slug == "direction-b":
        word = 'Çin <span>Eğitim</span>'
    else:
        word = '<span>ÇİN</span><span>EĞİTİM</span>'
    return f'<div class="lockup lockup-{slug[-1]}">{common}<div class="word-{slug[-1]}">{word}</div></div>'


def page_shell(title, body, image_src, home=False):
    nav_href = "../" if home else "index.html"
    nav_label = "Çin Eğitim bölümü" if home else "Üç yön"
    return f'''<!doctype html>
<html lang="tr"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<meta name="description" content="Çin Eğitim için kilitli sembolle birlikte tipografi yönü incelemeleri. Üç ayrı wordmark ve yazı karakteri denemesi; henüz seçim/onay yok.">
<title>{title}</title>{FONT_LINKS}<link rel="stylesheet" href="typography.css"></head>
<body><main><header class="mast"><span class="eyebrow">ÇİN EĞİTİM · TİPOGRAFİ / 01</span><a href="{nav_href}">{nav_label}</a></header>{body}
<footer class="pagefoot"><span>Yalnız inceleme. Kanonik sembol kilitli; wordmark seçilmedi.</span><a href="index.html">{'Üç yönü karşılaştır ↑' if home else 'Tüm yönlere dön ↑'}</a></footer></main></body></html>'''


def card(direction, image_src):
    slug = direction["slug"]
    return f'''<a class="option" href="{slug}.html" aria-label="{direction['id']} yönü {direction['name']} ayrıntıları">
<div class="preview">{lockup(direction, image_src)}</div><span class="tag tag-red">YÖN {direction['id']} · {direction['font_display']}</span>
<h2>{direction['name']}</h2><p>{direction['promise']}</p><span class="go">Tipografiyi incele →</span></a>'''


def index_html(image_src):
    body = f'''<section class="intro"><img src="{image_src}" alt="Kilitli Çin Eğitim sembolü"><div><span class="eyebrow">Sembol kilitli · wordmark henüz yok</span><h1>Yazı karakteri, sembolle birlikte.</h1>
<p>Aynı onaylı sembolle üç ayrı tipografi ve lockup denemesi. Her seçenekte Türkçe marka adı ve farklı okuma ritmi; sembolün kendisine dokunulmadı.</p></div></section>
<aside class="notice"><strong>İnceleme aşaması.</strong> Bu sayfalar tipografi denemesidir; logo ailesi, marka sistemi veya nihai wordmark onayı değildir. Seçim yapıldığında yalnız seçilen yön geliştirilir.</aside>
<div class="cards-head"><h2>Üç ayrı tipografik karakter</h2><p>Renk ve sembol aynı · yazı karakteri ve yerleşim farklı</p></div>
<section class="chooser" aria-label="Tipografi yönleri">{''.join(card(d, image_src) for d in DATA['directions'])}</section>
<p class="footnote"><a href="README.md">Bu turun kapsamı</a> · <a href="research.md">Araştırma ve font kaynakları</a></p>'''
    return page_shell("Çin Eğitim — Tipografi yönleri", body, image_src, home=True)


def direction_html(direction, image_src):
    slug = direction["slug"]
    label = direction["id"]
    if slug == "direction-a":
        class_name = "type-a"
        specimen = '<span>Çin</span><br><span>Eğitim</span>'
        sizes = '<span style="font:500 16px/1.15 \'Source Serif 4\',serif">16 px</span><span style="font:500 24px/1.1 \'Source Serif 4\',serif">24 px</span><span style="font:500 36px/1 \'Source Serif 4\',serif">36 px</span>'
        setting = "Source Serif 4 500 / 600; bilgi metninde Manrope 400 / 500. İki satırlı wordmark, sıkı satır aralığı ve hafif negatif harf aralığıyla."
        integration = "Sembol solda, wordmark sağda; optik dikey merkez ortak. Çizgi veya açıklama sembolün çevresindeki boşluğa girmez."
    elif slug == "direction-b":
        class_name = "type-b"
        specimen = 'Çin <span style="font-weight:500">Eğitim</span>'
        sizes = '<span style="font:700 16px/1.15 Manrope,sans-serif">16 px</span><span style="font:700 24px/1.1 Manrope,sans-serif">24 px</span><span style="font:700 36px/1 Manrope,sans-serif">36 px</span>'
        setting = "Manrope 700 / 500; tek aile, iki ağırlık. Wordmark kompakt negatif aralıkla tek satır; metin/arayüz Manrope 400 / 500."
        integration = "Ortalanmış kurgu: sembol tek satırlı ismin üstünde. Web başlığı ve dar mobil yerleşimde doğrudan okunur; ek slogan yok."
    else:
        class_name = "type-c"
        specimen = 'ÇİN<br>EĞİTİM'
        sizes = '<span style="font:700 16px/1.05 \'Barlow Condensed\',sans-serif;letter-spacing:.04em">16 px</span><span style="font:700 24px/1 \'Barlow Condensed\',sans-serif;letter-spacing:.04em">24 px</span><span style="font:700 36px/.9 \'Barlow Condensed\',sans-serif;letter-spacing:.04em">36 px</span>'
        setting = "Barlow Condensed 700 / 600; destek bilgisinde Manrope 400 / 600. Büyük harfli iki satır, sıkı satır aralığı ve açık harf aralığı."
        integration = "Sembol solda; büyük harfli blok ince kırmızı indeks çizgisinin sağında. Çizgi ve indeks yalnız tipografi yerleşimine aittir."
    body = f'''<section class="dirhead"><span class="tag">YÖN {label} · TİPOGRAFİ DENEMESİ</span><h1>{direction['name']}</h1><p>{direction['promise']} <span class="footnote">{direction['research_effect']}</span></p></section>
<section class="detail-lockup" aria-label="Kilitli sembol ile tipografik wordmark birleşimi">{lockup(direction, image_src)}</section>
<section class="twocol"><article class="panel {class_name}"><h2>Wordmark karakteri · {direction['wordmark_case']}</h2><div class="sample">{specimen}</div><div class="glyphs"><small>Türkçe karakter kontrolü</small>İ I ı · Ş ş · Ğ ğ · Ç ç · Ö ö · Ü ü</div><div class="sizes"><span>Ölçek:</span>{sizes}</div></article>
<article class="panel"><h2>Tipografik kurgu</h2><dl class="specs"><div><dt>Display</dt><dd>{direction['font_display']}</dd></div><div><dt>Destek / metin</dt><dd>{direction['font_support']}</dd></div><div><dt>Wordmark</dt><dd>{direction['wordmark_case']}</dd></div><div><dt>Yerleşim</dt><dd>{direction['arrangement']}</dd></div><div><dt>Logo mantığı</dt><dd>{direction['logic']}</dd></div><div><dt>Renk</dt><dd>Kilitli sembol aynen · yazı #202020</dd></div></dl><p class="footnote"><strong>Uygulama fikri:</strong> {integration}</p><p class="footnote">Ölçüler, harf aralığı ve boşluklar bu turda karşılaştırma amaçlıdır; üretim spesifikasyonu değildir.</p></article></section>
<aside class="notice"><strong>Değişmeyen varlık:</strong> kullanılan sembol <code>brands/cin-egitim/assets/symbol.svg</code> ile byte-byte aynıdır. Geometri, renk, oran ve SVG içeriği değiştirilmedi. Bu yazı henüz onaylı bir kilit değildir.</aside>'''
    return page_shell(f"{label} — {direction['name']} · Çin Eğitim", body, image_src)


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def build_target(folder: Path, image_src: str):
    folder.mkdir(parents=True, exist_ok=True)
    outputs = {"typography.css": CSS, "index.html": index_html(image_src)}
    for direction in DATA["directions"]:
        outputs[f"{direction['slug']}.html"] = direction_html(direction, image_src)
    for name, content in outputs.items():
        (folder / name).write_text(content, encoding="utf-8")
    return outputs


def main():
    metadata = json.loads((ROOT / "brands/cin-egitim/brand.json").read_text())
    logo = ROOT / metadata["canonicalLogo"]["path"]
    actual = sha(logo)
    assert metadata["canonicalLogo"]["locked"] and actual == DATA["canonical_logo_sha256"]
    source_outputs = build_target(SOURCE, "../../assets/symbol.svg")
    docs_outputs = build_target(DOCS, "../assets/symbol.svg")
    for support_file in ("README.md", "research.md"):
        (DOCS / support_file).write_bytes((SOURCE / support_file).read_bytes())
    site_logo = ROOT / "docs/cin-egitim/assets/symbol.svg"
    assert sha(site_logo) == actual, "Published-site logo copy is not the locked canonical SVG"
    record = {
        **DATA,
        "canonical_logo_sha256": actual,
        "directions_source_sha256": sha(SOURCE / "directions.json"),
        "build_recipe_sha256": sha(SOURCE / "build.py"),
        "source_outputs": {name: hashlib.sha256(content.encode()).hexdigest() for name, content in source_outputs.items()},
        "docs_outputs": {name: hashlib.sha256(content.encode()).hexdigest() for name, content in docs_outputs.items()},
        "published_support_files": {name: sha(DOCS / name) for name in ("README.md", "research.md")},
        "sources": {
            "manrope": "https://fonts.google.com/specimen/Manrope",
            "source_serif_4": "https://fonts.google.com/specimen/Source+Serif+4",
            "barlow_condensed": "https://fonts.google.com/specimen/Barlow+Condensed",
            "market_reference": "https://pekinedu.com/"
        },
        "image_model_calls": 0,
        "approval": "Human A/B/C selection pending. No canonical wordmark or brand-system approval."
    }
    (SOURCE / "manifest.json").write_text(json.dumps(record, ensure_ascii=False, indent=2) + "\n")
    print(json.dumps({"status": "BUILT / REVIEW ONLY", "canonical_logo_sha256": actual,
                      "source_pages": len(source_outputs), "docs_pages": len(docs_outputs)}, indent=2))


if __name__ == "__main__":
    main()
