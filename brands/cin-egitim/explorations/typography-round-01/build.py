#!/usr/bin/env python3
"""Build twelve Turkish typography studies around the unchanged canonical symbol."""
from __future__ import annotations
import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[4]
SOURCE = Path(__file__).resolve().parent
DOCS = ROOT / "docs/cin-egitim/typography-round-01"
DATA = json.loads((SOURCE / "directions.json").read_text())

FONT_URLS = {
    "Barlow Condensed": "https://fonts.google.com/specimen/Barlow+Condensed",
    "Cormorant Garamond": "https://fonts.google.com/specimen/Cormorant+Garamond",
    "DM Serif Display": "https://fonts.google.com/specimen/DM+Serif+Display",
    "IBM Plex Mono": "https://fonts.google.com/specimen/IBM+Plex+Mono",
    "IBM Plex Sans": "https://fonts.google.com/specimen/IBM+Plex+Sans",
    "Lora": "https://fonts.google.com/specimen/Lora",
    "Manrope": "https://fonts.google.com/specimen/Manrope",
    "Nunito Sans": "https://fonts.google.com/specimen/Nunito+Sans",
    "Oswald": "https://fonts.google.com/specimen/Oswald",
    "Roboto Slab": "https://fonts.google.com/specimen/Roboto+Slab",
    "Source Serif 4": "https://fonts.google.com/specimen/Source+Serif+4",
    "Space Grotesk": "https://fonts.google.com/specimen/Space+Grotesk",
}

FONT_LINKS = '''<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Barlow+Condensed:wght@500;600;700;800&family=Cormorant+Garamond:ital,wght@0,500;0,600;1,500;1,600&family=DM+Serif+Display:ital@0;1&family=IBM+Plex+Mono:wght@400;500;600&family=IBM+Plex+Sans:wght@400;500;600;700&family=Lora:ital,wght@0,400;0,500;0,600;1,400;1,500&family=Manrope:wght@400;500;600;700;800&family=Nunito+Sans:opsz,wght@6..12,400..800&family=Oswald:wght@400;500;600;700&family=Roboto+Slab:wght@400;500;600;700&family=Source+Serif+4:opsz,wght@8..60,400..700&family=Space+Grotesk:wght@400;500;600;700&display=swap" rel="stylesheet">'''

CSS = r'''*{box-sizing:border-box}html{scroll-behavior:smooth}body{margin:0;background:#f5f0e7;color:#202020;font:16px/1.6 Manrope,Arial,sans-serif}a{color:inherit}a:focus-visible{outline:3px solid #bf0c1a;outline-offset:4px}main{max-width:1240px;padding:28px 24px 72px;margin:auto}.mast{display:flex;align-items:center;justify-content:space-between;gap:16px;border-bottom:1px solid #c9c1b5;padding-bottom:14px}.eyebrow,.tag{font:600 11px/1.4 Manrope,Arial,sans-serif;letter-spacing:.14em;text-transform:uppercase;color:#655f57}.mast a,.back{font-size:13px;text-decoration:none;border-bottom:1px solid #bf0c1a}.intro{display:grid;grid-template-columns:88px 1fr;gap:22px;align-items:center;padding:34px 0 28px}.intro img{width:88px;height:88px;object-fit:contain}.intro h1{font:600 clamp(34px,5vw,58px)/1.02 'Source Serif 4',Georgia,serif;letter-spacing:-.035em;margin:2px 0 8px}.intro p{max-width:72ch;color:#514c45;margin:0}.notice{font-size:13px;background:#fffdf8;border-left:3px solid #bf0c1a;padding:12px 16px;margin:8px 0 28px}.chooser{display:grid;grid-template-columns:repeat(3,minmax(0,1fr));gap:16px}.option{min-width:0;background:#fffdf8;border:1px solid #d5cec2;border-radius:14px;padding:16px;text-decoration:none;display:flex;flex-direction:column;transition:box-shadow .15s,border-color .15s}.option:hover{border-color:#202020;box-shadow:4px 4px 0 #202020}.option h2{font:600 22px/1.1 Manrope,Arial,sans-serif;margin:8px 0 5px}.option p{font-size:13px;color:#514c45;margin:0 0 12px}.option .go{margin-top:auto;padding-top:10px;font-size:13px;border-bottom:1px solid #bf0c1a;align-self:flex-start}.preview{min-height:148px;display:grid;place-items:center;background:#f5f0e7;border:1px solid #e5ded2;border-radius:10px;padding:12px;overflow:hidden}.lockup{display:flex;align-items:center;justify-content:center;gap:14px;color:#202020;max-width:100%}.lockup img{display:block;width:68px;height:68px;object-fit:contain;flex:none}.wordmark{font-family:Manrope,Arial,sans-serif;font-weight:600;line-height:.95;letter-spacing:-.035em;min-width:0}.wordmark-line{display:block;white-space:nowrap}.type-a{flex-direction:row;gap:14px}.type-a .wordmark{font:500 32px/.91 'Source Serif 4',Georgia,serif;letter-spacing:-.045em}.type-b{flex-direction:column;gap:9px}.type-b .wordmark{font:700 22px/1 Manrope,Arial,sans-serif;letter-spacing:-.055em}.type-c{flex-direction:row;gap:11px}.type-c .wordmark{border-left:2px solid #bf0c1a;padding-left:10px;font:700 26px/.83 'Barlow Condensed','Arial Narrow',sans-serif;letter-spacing:.055em;text-transform:uppercase}.type-d{flex-direction:row;gap:12px}.type-d .wordmark{font:600 32px/1 'Cormorant Garamond',Georgia,serif;letter-spacing:-.035em}.type-e{flex-direction:row;gap:12px}.type-e .wordmark{font:600 26px/.92 'IBM Plex Sans',Arial,sans-serif;letter-spacing:-.055em}.type-e .wordmark-line:nth-child(2){font-weight:400;letter-spacing:-.025em}.type-f{flex-direction:row;gap:12px}.type-f .wordmark{border-block:1px solid #857c70;padding:6px 0;font:500 20px/1.15 'IBM Plex Mono',monospace;letter-spacing:.075em}.type-g{flex-direction:row-reverse;gap:12px}.type-g .wordmark{text-align:right;font:700 26px/.92 'Nunito Sans',Arial,sans-serif;letter-spacing:-.055em}.type-h{flex-direction:column;gap:7px}.type-h .wordmark{text-align:center;font:600 31px/.84 Oswald,'Arial Narrow',sans-serif;letter-spacing:.04em;text-transform:uppercase}.type-i{flex-direction:column;gap:6px}.type-i .wordmark{text-align:center;font:400 29px/.98 'DM Serif Display',Georgia,serif;letter-spacing:-.035em}.type-j{flex-direction:row-reverse;gap:12px}.type-j .wordmark{font:600 21px/1 'Space Grotesk',Arial,sans-serif;letter-spacing:.095em;text-transform:uppercase}.type-k{flex-direction:row-reverse;gap:12px}.type-k .wordmark{text-align:right;font:500 italic 28px/.95 Lora,Georgia,serif;letter-spacing:-.035em}.type-l{flex-direction:row;gap:12px}.type-l .wordmark{border-left:2px solid #bf0c1a;padding-left:10px;font:700 23px/.9 'Roboto Slab',Georgia,serif;letter-spacing:-.045em;text-transform:uppercase}.type-l .wordmark-line:first-child{border-bottom:1px solid #bf0c1a;padding-bottom:4px;margin-bottom:3px}.cards-head{display:flex;align-items:end;justify-content:space-between;gap:20px;margin:32px 0 14px}.cards-head h2{font:600 23px/1.2 Manrope,Arial,sans-serif;margin:0}.cards-head p{font-size:12px;color:#655f57;margin:0}.dirhead{padding:36px 0 22px}.dirhead .tag{color:#bf0c1a}.dirhead h1{font:600 clamp(38px,6vw,66px)/1 'Source Serif 4',Georgia,serif;letter-spacing:-.04em;margin:8px 0}.dirhead p{max-width:72ch;color:#514c45;margin:0}.detail-lockup{margin:20px 0 28px;padding:clamp(24px,5vw,54px);background:#fffdf8;border:1px solid #d5cec2;border-radius:16px;min-height:270px;display:grid;place-items:center}.detail-lockup .lockup{gap:24px}.detail-lockup .lockup img{width:106px;height:106px}.detail-lockup .type-a .wordmark{font-size:clamp(46px,6vw,70px)}.detail-lockup .type-b .wordmark{font-size:clamp(34px,4vw,48px)}.detail-lockup .type-c .wordmark{font-size:clamp(44px,6vw,64px);padding-left:18px}.detail-lockup .type-d .wordmark{font-size:clamp(48px,7vw,76px)}.detail-lockup .type-e .wordmark{font-size:clamp(40px,6vw,66px)}.detail-lockup .type-f .wordmark{font-size:clamp(30px,4vw,46px)}.detail-lockup .type-g .wordmark{font-size:clamp(42px,6vw,66px)}.detail-lockup .type-h .wordmark{font-size:clamp(44px,6vw,66px)}.detail-lockup .type-i .wordmark{font-size:clamp(44px,6vw,68px)}.detail-lockup .type-j .wordmark{font-size:clamp(28px,4vw,44px)}.detail-lockup .type-k .wordmark{font-size:clamp(44px,6vw,68px)}.detail-lockup .type-l .wordmark{font-size:clamp(36px,5vw,58px);padding-left:16px}.twocol{display:grid;grid-template-columns:1.15fr .85fr;gap:16px}.panel{background:#fffdf8;border:1px solid #d5cec2;border-radius:14px;padding:20px}.panel h2{font:600 18px/1.3 Manrope,Arial,sans-serif;margin:0 0 12px}.sample{display:flex;align-items:center;justify-content:center;min-height:140px;margin:8px 0 16px;padding:12px;overflow:hidden}.sample .wordmark{font-size:clamp(34px,6vw,64px)}.type-c.sample .wordmark,.type-h.sample .wordmark,.type-l.sample .wordmark{font-size:clamp(42px,6vw,68px)}.type-b.sample .wordmark,.type-j.sample .wordmark{font-size:clamp(30px,4vw,44px)}.type-f.sample .wordmark{font-size:clamp(25px,3.5vw,38px)}.glyphs{border-top:1px solid #ded7cb;padding-top:12px;font-size:17px;letter-spacing:.025em}.glyphs small{display:block;font-size:10px;letter-spacing:.12em;color:#655f57;margin-bottom:5px}.specs{display:grid;grid-template-columns:1fr 1fr;gap:9px 18px;margin:0}.specs div{border-top:1px solid #ded7cb;padding-top:8px}.specs dt{font-size:10px;text-transform:uppercase;letter-spacing:.11em;color:#655f57}.specs dd{font-size:13px;margin:2px 0 0}.footnote{font-size:12px;color:#655f57;margin:18px 0 0}.tag-red{color:#bf0c1a}.pagefoot{display:flex;justify-content:space-between;gap:16px;align-items:center;border-top:1px solid #c9c1b5;margin-top:30px;padding-top:14px;font-size:12px;color:#655f57}.pagefoot a{color:#202020}@media(max-width:900px){.chooser{grid-template-columns:repeat(2,minmax(0,1fr))}.twocol{grid-template-columns:1fr}}@media(max-width:600px){main{padding:18px 15px 48px}.mast .eyebrow{font-size:9px}.intro{grid-template-columns:58px 1fr;gap:14px;padding:26px 0 20px}.intro img{width:58px;height:58px}.intro h1{font-size:34px}.intro p{font-size:14px}.chooser{grid-template-columns:1fr;gap:12px}.option{display:grid;grid-template-columns:minmax(0,1fr) 142px;gap:6px 10px;padding:12px}.option .preview{grid-column:2;grid-row:1/5;min-height:124px;padding:6px}.option h2{align-self:end}.option .go{align-self:start}.lockup{gap:7px}.lockup img{width:42px;height:42px}.type-a .wordmark,.type-g .wordmark,.type-k .wordmark{font-size:22px}.type-b .wordmark,.type-j .wordmark{font-size:16px}.type-c .wordmark{font-size:20px;padding-left:7px}.type-d .wordmark{font-size:21px}.type-e .wordmark{font-size:20px}.type-f .wordmark{font-size:14px;letter-spacing:.02em}.type-h .wordmark,.type-i .wordmark{font-size:24px}.type-l .wordmark{font-size:17px;padding-left:6px}.cards-head{display:block}.cards-head p{margin-top:4px}.dirhead{padding:28px 0 16px}.dirhead h1{font-size:42px}.detail-lockup{min-height:210px;padding:16px}.detail-lockup .lockup{gap:12px}.detail-lockup .lockup img{width:70px;height:70px}.detail-lockup .wordmark{font-size:clamp(26px,8vw,42px)!important}.detail-lockup .type-f .wordmark{font-size:clamp(18px,5vw,28px)!important}.detail-lockup .type-j .wordmark{font-size:clamp(18px,5vw,28px)!important}.specs{grid-template-columns:1fr}.pagefoot{align-items:flex-start;flex-direction:column}}@media(prefers-reduced-motion:reduce){html{scroll-behavior:auto}.option{transition:none}}'''


def type_class(direction):
    return "type-" + direction["id"].lower()


def wordmark(direction):
    lines = "".join(f'<span class="wordmark-line">{line}</span>' for line in direction["lines"])
    return f'<div class="wordmark">{lines}</div>'


def lockup(direction, image_src):
    return (f'<div class="lockup {type_class(direction)}">'
            f'<img src="{image_src}" alt="Kilitli Çin Eğitim sembolü">{wordmark(direction)}</div>')


def page_shell(title, body, home=False):
    nav_href = "../" if home else "index.html"
    nav_label = "Çin Eğitim bölümü" if home else "12 yönün karşılaştırması"
    return f'''<!doctype html>
<html lang="tr"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<meta name="description" content="Çin Eğitim'in kilitli sembolüyle birlikte on iki ayrı Türkçe tipografi ve wordmark yerleşimi incelemesi. Henüz seçim veya kimlik onayı yok.">
<title>{title}</title>{FONT_LINKS}<link rel="stylesheet" href="typography.css"></head>
<body><main><header class="mast"><span class="eyebrow">ÇİN EĞİTİM · TİPOGRAFİ / 01</span><a href="{nav_href}">{nav_label}</a></header>{body}
<footer class="pagefoot"><span>İnceleme turu · Sembol kilitli · Wordmark seçimi bekleniyor</span><a href="index.html">Tüm 12 yöne dön ↑</a></footer></main></body></html>'''


def card(direction, image_src):
    return f'''<a class="option" href="{direction['slug']}.html" aria-label="Yön {direction['id']}: {direction['name']} ayrıntıları">
<div class="preview">{lockup(direction, image_src)}</div><span class="tag tag-red">YÖN {direction['id']} · {direction['font_display']}</span>
<h2>{direction['name']}</h2><p>{direction['promise']}</p><span class="go">Bu yönü ayrıntılı incele →</span></a>'''


def index_html():
    body = f'''<section class="intro"><img src="../assets/symbol.svg" alt="Kilitli Çin Eğitim sembolü"><div><span class="eyebrow">Sembol değişmez · 12 farklı tipografi karakteri</span><h1>Bir sembol, on iki ayrı tipografik dünya.</h1>
<p>Her seçenekte aynı onaylı SVG, farklı yazı ailesi, harf ritmi ve sembolle yerleşim. Karşılaştırmayı renkten bağımsız tutmak için ortak bir zemin kullandım; logoya müdahale edilmedi.</p></div></section>
<aside class="notice"><strong>Seçim öncesi araştırma turu.</strong> Bu 12 çalışma wordmark eskizidir; hiçbiri onaylı logo, lockup ailesi veya tam marka kimliği değildir. Bir yönü seçtiğinde yalnız o çizgiyi derinleştirip optik düzeltmelerini yapacağım.</aside>
<div class="cards-head"><h2>12 tipografik yön</h2><p>12 yazı ailesi · yatay, dikey, ters yön ve farklı satır düzenleri</p></div>
<section class="chooser" aria-label="On iki tipografi yönü">{''.join(card(d, "../assets/symbol.svg") for d in DATA['directions'])}</section>
<p class="footnote"><a href="README.md">Turun kapsamı</a> · <a href="research.md">Font ve pazar araştırması</a></p>'''
    return page_shell("Çin Eğitim — 12 tipografi yönü", body, home=True)


def direction_html(direction):
    css_class = type_class(direction)
    specimen_lines = "".join(f'<span class="wordmark-line">{line}</span>' for line in direction["lines"])
    specimen = f'<div class="wordmark">{specimen_lines}</div>'
    body = f'''<section class="dirhead"><span class="tag">YÖN {direction['id']} / 12 · TİPOGRAFİ DENEMESİ</span><h1>{direction['name']}</h1><p>{direction['promise']}</p></section>
<section class="detail-lockup" aria-label="Kilitli sembol ve tipografik wordmark denemesi">{lockup(direction, "../assets/symbol.svg")}</section>
<section class="twocol"><article class="panel"><h2>Wordmark karakteri · {direction['case']}</h2><div class="sample {css_class}">{specimen}</div><div class="glyphs"><small>Türkçe karakter kontrolü</small>İ I ı · Ş ş · Ğ ğ · Ç ç · Ö ö · Ü ü</div></article>
<article class="panel"><h2>Yönün tipografik kurgusu</h2><dl class="specs"><div><dt>Display</dt><dd>{direction['font_display']}</dd></div><div><dt>Destek / metin</dt><dd>{direction['font_support']}</dd></div><div><dt>Harf biçimi</dt><dd>{direction['case']}</dd></div><div><dt>Sembol ilişkisi</dt><dd>{direction['arrangement']}</dd></div><div><dt>Yerleşim mantığı</dt><dd>{direction['logic']}</dd></div><div><dt>Karakter</dt><dd>{direction['mood']}</dd></div><div><dt>Renk</dt><dd>Kilitli sembol aynen · yazı #202020</dd></div></dl><p class="footnote">Ölçüler, ağırlıklar ve boşluklar bu turda karşılaştırma amaçlıdır; üretim spesifikasyonu değildir. Kullanılan sembolün kaynak SVG'si değiştirilmedi.</p></article></section>
<aside class="notice"><strong>Onay durumu:</strong> Bu, {direction['id']} yönünün inceleme taslağıdır. Seçim ve daha ileri optik düzenleme öncesi hiçbir wordmark kilitlenmez.</aside>'''
    return page_shell(f"{direction['id']} — {direction['name']} · Çin Eğitim", body)


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def build_target(folder: Path, image_src: str):
    folder.mkdir(parents=True, exist_ok=True)
    outputs = {"typography.css": CSS, "index.html": index_html()}
    for direction in DATA["directions"]:
        outputs[f"{direction['slug']}.html"] = direction_html(direction)
    for name, content in outputs.items():
        # Board and detail pages share the same relative symbol path in this round.
        if name == "index.html":
            content = content.replace('../assets/symbol.svg', image_src)
        else:
            content = content.replace('../assets/symbol.svg', image_src)
        outputs[name] = content
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
        "fonts": FONT_URLS,
        "image_model_calls": 0,
        "approval": "Human A-L selection pending. No canonical wordmark or brand-system approval."
    }
    (SOURCE / "manifest.json").write_text(json.dumps(record, ensure_ascii=False, indent=2) + "\n")
    print(json.dumps({"status": "BUILT / REVIEW ONLY", "directions": len(DATA["directions"]),
                      "canonical_logo_sha256": actual, "source_pages": len(source_outputs),
                      "docs_pages": len(docs_outputs)}, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
