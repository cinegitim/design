#!/usr/bin/env python3
"""Build the five image-first launch slides from original artwork + editable SVG type.

The generated artwork remains an intact, full-bleed visual layer. Only exact Turkish
copy, campaign-native vector interventions and manifest-listed canonical SVG lockups
are composited on top. No legacy carousel layout is used.
"""
from __future__ import annotations

import hashlib
import html
import json
import os
import base64
import re
import shutil
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
HERE = Path(__file__).resolve().parent
ORIGINALS = HERE / "originals"
SOURCE = HERE / "source"
FINAL = HERE / "final"
ASSETS = HERE / "assets"
LOCKUPS = ASSETS / "lockups"
MANIFEST_PATH = HERE / "manifest.json"
CANONICAL = ROOT / "brands/asyada-egitim/assets/lockups/canonical-lockups.json"
SEAL_SHA = "8f5d46f0302c4cc7e3765d3bfce9445f842dbd92f1e0f8fbe99f9f509c77e11a"
W, H = 1080, 1350
PAPER, INK, RED = "#F7F3E9", "#1D2027", "#BD2120"

SLIDES = [
    {
        "id": "01-cover", "file": "01-cover.png", "original": "01-cover.png",
        "lockup": "D-04/dark", "logo_xy": [842, 30], "logo_width": 220,
        "copy": ["Üniversite için başka bir dünya var.", "Yurtdışı eğitime başka bir yerden bak."],
        "elements": [
            ('text', 60, 910, 58, INK, 620, 480, 'Üniversite için'),
            ('text', 57, 1010, 92, INK, 740, 440, 'başka bir'),
            ('text', 105, 1125, 108, RED, 750, 535, 'dünya var.'),
            ('text', 145, 1200, 27, INK, 560, 500, 'Yurtdışı eğitime başka bir yerden bak.'),
        ],
        "direction": "Collage takes the image from a close student portrait through architectural layers into the campus vista; exact copy occupies the torn-paper sweep, not a poster header/footer.",
        "fidelity": "The 1122×1402 generated collage is retained as the complete base; only campaign copy and the approved small-use lockup are added. The photographic focal face, red paper arcs, grain and irregular montage remain unchanged.",
    },
    {
        "id": "02-perspective", "file": "02-perspective.png", "original": "02-perspective.png",
        "lockup": "P-01/dark", "logo_xy": [26, 968], "logo_width": 352,
        "copy": ["Yurtdışı eğitimin tek yönü yok.", "Amerika ve Avrupa, seçeneklerin tamamı değil."],
        "elements": [
            ('text', 56, 150, 106, INK, 760, 500, 'Yurtdışı'),
            ('text', 56, 250, 89, INK, 680, 500, 'eğitimin'),
            ('text', 52, 365, 100, RED, 800, 505, 'tek yönü'),
            ('text', 52, 495, 139, INK, 820, 500, 'yok.'),
            ('paper-strip', 39, 515, 518, 112),
            ('text', 60, 567, 30, INK, 560, 485, 'Amerika ve Avrupa,'),
            ('text', 60, 609, 30, INK, 560, 485, 'seçeneklerin tamamı değil.'),
        ],
        "direction": "The student-height passage moves from dark foreground to a bright campus horizon. A differently scaled, stacked lockup sits against the backpack silhouette rather than a recurring corner zone.",
        "fidelity": "Perspective, passerby, red vanishing-axis sweep and cream collage margin are retained intact. The four-line headline follows the reserved paper field; the lockup is placed on a separate dark photographic region.",
    },
    {
        "id": "03-five-worlds", "file": "03-five-worlds.png", "original": "03-five-worlds.png",
        "lockup": "D-04/light", "logo_xy": [397, 842], "logo_width": 220,
        "copy": ["Tek bir Asya yok.", "Beş rota. Birbirinden farklı dünyalar.", "Çin", "Japonya", "Güney Kore", "Singapur", "Hong Kong"],
        "elements": [
            ('text', 58, 590, 78, INK, 600, 300, 'Tek bir'),
            ('text', 52, 718, 130, RED, 820, 570, 'Asya yok.'),
            ('paper-note', 38, 753, 636, 195),
            ('text', 70, 798, 30, INK, 600, 450, 'Beş rota. Birbirinden farklı'),
            ('text', 70, 838, 30, INK, 600, 175, 'dünyalar.'),
            ('tag', 24, 28, 126, 54, PAPER, INK, -4, 'Çin', 28),
            ('tag', 851, 286, 178, 54, RED, PAPER, 3, 'Japonya', 27),
            ('tag', 790, 592, 224, 56, INK, PAPER, -2, 'Güney Kore', 26),
            ('tag', 24, 1055, 192, 54, RED, PAPER, 3, 'Singapur', 27),
            ('tag', 836, 1165, 202, 55, PAPER, INK, -3, 'Hong Kong', 26),
        ],
        "direction": "One paper aperture anchors the thesis while five intentionally varied editorial labels pin five visually distinct city fragments; there are no uniform destination tiles.",
        "fidelity": "The five-city collage, edge crops, overprinted red, ink and torn-paper geometry are retained. Type is set into the original central aperture and city windows without converting the composition into a grid.",
    },
    {
        "id": "04-experience", "file": "04-experience.png", "original": "04-experience.png",
        "lockup": "C-03/dark", "logo_xy": [616, 20], "logo_width": 448,
        "copy": ["Sadece bir üniversite seçmiyorsun.", "Yeni bir şehir, yeni insanlar, yeni bir dil ve dünyaya başka bir bakış açısı.", "Lisans", "Yüksek Lisans", "Dil Programları", "Yaz Okulları"],
        "elements": [
            ('text', 40, 93, 61, INK, 620, 460, 'Sadece bir'),
            ('text', 39, 183, 83, INK, 720, 500, 'üniversite'),
            ('text', 39, 270, 68, RED, 720, 500, 'seçmiyorsun.'),
            ('tag', 28, 484, 166, 52, PAPER, INK, -3, 'Lisans', 28),
            ('tag', 736, 575, 258, 55, RED, PAPER, 2, 'Yüksek Lisans', 27),
            ('paper-note', 357, 837, 685, 220),
            ('text', 410, 895, 28, INK, 560, 595, 'Yeni bir şehir, yeni insanlar,'),
            ('text', 410, 938, 28, INK, 560, 595, 'yeni bir dil ve dünyaya başka'),
            ('text', 410, 981, 28, INK, 560, 595, 'bir bakış açısı.'),
            ('tag', 30, 1130, 270, 54, PAPER, RED, 2, 'Dil Programları', 27),
            ('tag', 736, 1163, 220, 55, INK, PAPER, -2, 'Yaz Okulları', 27),
        ],
        "direction": "Study and friendship remain the main photographic subjects; a diagonal torn-paper annotation crosses the lower collage, while four pathways are dispersed around separate image fragments.",
        "fidelity": "Portrait, study action, friends, city dusk, red print marks and collage edges remain intact. The only newly reconstructed shape is an irregular vellum note that follows the original layered-paper language and protects the exact supporting line.",
    },
    {
        "id": "05-invitation", "file": "05-invitation.png", "original": "05-invitation.png",
        "lockup": "H-02/light", "logo_xy": [224, 565], "logo_width": 632,
        "copy": ["Senin rotan nerede başlıyor?", "Çin · Japonya · Güney Kore · Singapur · Hong Kong", "Ücretsiz ön görüşme", "Profildeki bağlantıdan bize ulaş."],
        "elements": [
            ('text', 585, 168, 81, PAPER, 720, 450, 'Senin rotan'),
            ('text', 582, 262, 70, PAPER, 650, 260, 'nerede'),
            ('text', 582, 344, 70, RED, 800, 350, 'başlıyor?'),
            ('text', 590, 422, 27, PAPER, 560, 460, 'Çin · Japonya · Güney Kore ·'),
            ('text', 590, 460, 27, PAPER, 560, 400, 'Singapur · Hong Kong'),
            ('cta-ribbon', 531, 1068, 520, 86),
            ('text', 570, 1127, 41, PAPER, 720, 440, 'Ücretsiz ön görüşme'),
            ('text', 583, 1297, 29, PAPER, 500, 460, 'Profildeki bağlantıdan bize ulaş.'),
        ],
        "direction": "The campaign closes with a dark cinematic field and an oversized bilingual lockup centered on the original cream vellum wave; CTA follows the red diagonal rather than a standard ad button/footer.",
        "fidelity": "The dark atmospheric image, student silhouette, cream central sweep, red diagonals and grain are retained. One targeted edit replaced a temple-like roof with modern city architecture; the first generation is retained as provenance. The bilingual SVG is prominent at 632px, above its 528px minimum.",
    },
]


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def text(x: int, y: int, size: int, fill: str, weight: int, width: int, value: str) -> str:
    return (f'<text x="{x}" y="{y}" font-family="Jost" font-size="{size}px" '
            f'font-weight="{weight}" fill="{fill}" textLength="{width}" lengthAdjust="spacingAndGlyphs" '
            f'xml:space="preserve">{html.escape(value)}</text>')


def svg_for(s: dict) -> str:
    source_path = ORIGINALS / s["original"]
    original_href = f'../originals/{source_path.name}'
    lock = s["lockup"].replace("/", "-")
    lock_file = {
        "P-01-dark": "p-01-primary-stacked-dark.svg",
        "P-01-light": "p-01-primary-stacked-light.svg",
        "C-03-dark": "c-03-compact-dark.svg",
        "D-04-dark": "d-04-small-use-digital-dark.svg",
        "D-04-light": "d-04-small-use-digital-light.svg",
        "H-02-light": "h-02-primary-horizontal-light.svg",
    }[lock]
    lock_path = LOCKUPS / lock_file
    lock_href = f'../assets/lockups/{lock_file}'
    ar = {"P-01": 1.017, "C-03": 2.312, "D-04": 2.612, "H-02": 2.666}[s["lockup"].split("/")[0]]
    logo_h = round(s["logo_width"] / ar)
    logo_x, logo_y = s["logo_xy"]
    exact_copy_attr = html.escape(json.dumps(s["copy"], ensure_ascii=False, separators=(",", ":")), quote=True)
    els = []
    for e in s["elements"]:
        if e[0] == "text":
            _, x, y, size, fill, weight, width, value = e
            els.append(text(x, y, size, fill, weight, width, value))
        elif e[0] == "tag":
            _, x, y, width, height, bg, fg, angle, value, size = e
            # Every destination caption is independently sized and rotated; no repeated tile component.
            d = f'M 0 3 L {width-13} 0 L {width} 8 L {width-3} {height-3} L 9 {height} L 0 {height-8} Z'
            els.append(f'<g transform="translate({x} {y}) rotate({angle} {width/2} {height/2})">'
                       f'<path d="{d}" fill="{bg}" fill-opacity="0.96"/>'
                       f'<text x="{width/2}" y="{height/2+size*.35}" text-anchor="middle" '
                       f'font-family="Jost" font-size="{size}px" font-weight="700" fill="{fg}">{html.escape(value)}</text></g>')
        elif e[0] == "paper-note":
            _, x, y, width, height = e
            path = f'M{x} {y+12} L{x+width-26} {y} L{x+width} {y+18} L{x+width-9} {y+height-14} L{x+width-42} {y+height} L{x+21} {y+height-7} L{x} {y+height-28} Z'
            els.append(f'<path d="{path}" fill="{PAPER}" fill-opacity="0.96"/>')
            els.append(f'<path d="M{x+18} {y+20} L{x+width-30} {y+13}" stroke="{RED}" stroke-width="5"/>')
        elif e[0] == "paper-strip":
            _, x, y, width, height = e
            path = f'M{x+7} {y+7} L{x+width-24} {y} L{x+width} {y+13} L{x+width-7} {y+height-14} L{x+width-30} {y+height} L{x+18} {y+height-5} L{x} {y+height-21} Z'
            els.append(f'<path d="{path}" fill="{PAPER}" fill-opacity="0.97"/>')
        elif e[0] == "cta-ribbon":
            _, x, y, width, height = e
            path = f'M{x} {y+14} L{x+width-20} {y} L{x+width} {y+height-12} L{x+17} {y+height} Z'
            els.append(f'<path d="{path}" fill="{RED}" fill-opacity="0.96"/>')
    # The lockup is a complete, externally linked, manifest-listed canonical SVG. Its geometry is not rebuilt.
    els.append(f'<image href="{lock_href}" x="{logo_x}" y="{logo_y}" width="{s["logo_width"]}" height="{logo_h}" preserveAspectRatio="xMidYMid meet"/>')
    alt = " · ".join(s["copy"])
    return (f'''<?xml version="1.0" encoding="UTF-8"?>
<svg xmlns="http://www.w3.org/2000/svg" xmlns:xlink="http://www.w3.org/1999/xlink" width="{W}" height="{H}" viewBox="0 0 {W} {H}" role="img" aria-labelledby="title desc">
<title id="title">{html.escape(s['id'])} — Asya’da Eğitim launch carousel</title>
<desc id="desc">{html.escape(alt)}</desc>
<metadata>Image-first source reconstruction. Canonical lockup: {s['lockup']}; no geometry alteration.</metadata>
<image href="{original_href}" x="0" y="0" width="{W}" height="{H}" preserveAspectRatio="xMidYMid slice"/>
<g id="editable-campaign-copy" data-typeface="Jost" data-exact-copy-json="{exact_copy_attr}">{''.join(els)}</g>
</svg>''')


def main() -> None:
    for p in (ORIGINALS, SOURCE, FINAL, LOCKUPS):
        p.mkdir(parents=True, exist_ok=True)
    # Keep canonical SVGs verbatim and locally linked for the self-contained ZIP.
    canonical = json.loads(CANONICAL.read_text())
    recs = {r["canonical_lockup_id"]: r for r in canonical["records"]}
    for s in SLIDES:
        rec = recs[s["lockup"]]
        src = ROOT / rec["canonical_file_path"]
        dst = LOCKUPS / src.name
        if not dst.exists() or sha(dst) != rec["sha256"]:
            shutil.copy2(src, dst)
        if sha(dst) != rec["sha256"]:
            raise RuntimeError(f"Canonical lockup hash mismatch: {s['lockup']}")
        src_svg = SOURCE / f"{s['id']}.svg"
        src_svg.write_text(svg_for(s), encoding="utf-8")

    # CairoSVG resolves the local font through a temporary, portable Fontconfig config.
    with tempfile.TemporaryDirectory(prefix="asyada-launch-font-") as tmp:
        tmp_path = Path(tmp)
        config = tmp_path / "fonts.conf"
        config.write_text(f'''<?xml version="1.0"?>\n<!DOCTYPE fontconfig SYSTEM "fonts.dtd">\n<fontconfig><dir>{ASSETS.resolve()}</dir><cachedir>{tmp_path / 'cache'}</cachedir></fontconfig>''')
        os.environ["FONTCONFIG_FILE"] = str(config)
        import cairosvg
        for s in SLIDES:
            src_svg = SOURCE / f"{s['id']}.svg"
            markup = src_svg.read_text(encoding="utf-8")
            image_data = base64.b64encode((ORIGINALS / s["original"]).read_bytes()).decode("ascii")
            lock_file = next(x for x in LOCKUPS.iterdir() if x.name in markup)
            lock_data = base64.b64encode(lock_file.read_bytes()).decode("ascii")
            markup = markup.replace(f'../originals/{s["original"]}', f'data:image/png;base64,{image_data}')
            markup = re.sub(r'\.\./assets/lockups/[^\"]+\.svg', f'data:image/svg+xml;base64,{lock_data}', markup)
            render_svg = tmp_path / f"{s['id']}.svg"
            render_svg.write_text(markup, encoding="utf-8")
            cairosvg.svg2png(url=str(render_svg), write_to=str(FINAL / s["file"]), output_width=W, output_height=H)

    m = json.loads(MANIFEST_PATH.read_text()) if MANIFEST_PATH.exists() else {}
    m.update({
        "title": "Asya’da Eğitim — Launch Carousel Experiment 02",
        "campaign": "Üniversite için başka bir dünya var.",
        "status": "HUMAN EXPERIMENTAL CAMPAIGN REVIEW PENDING",
        "dimensions": [W, H],
        "production_method": "Five full editorial compositions generated first with gpt-image-2. Original images are preserved; accurate copy is editable SVG text, and exact canonical SVG lockups are externally linked and composited in the reconstruction.",
        "font": {"family": "Jost", "file": "assets/Jost-VF.ttf", "sha256": sha(ASSETS / "Jost-VF.ttf")},
        "palette": {"paper": PAPER, "ink": INK, "red": RED},
        "exact_copy": {s["id"]: s["copy"] for s in SLIDES},
        "imagery_disclosure": "All generated people and places are illustrative campaign imagery, not documentary photographs. Destination imagery on slide 03 uses broad city cues; it is not a claim of exact landmark photography or a specific university.",
        "gpt_image_2": {"generation_count": 5, "edit_count": 1, "backend": "gpt-image-2 via connected ChatGPT subscription", "edited_slide": "05-invitation: one targeted correction replaced an unintended temple-like silhouette with contemporary city architecture; first generation retained as provenance."},
        "alternate_generations": [{"slide": "05-invitation", "file": "originals/05-invitation-first.png", "sha256": sha(ORIGINALS / "05-invitation-first.png"), "note": "Initial gpt-image-2 composition before the single targeted roofline correction."}],
        "slides": []
    })
    for s in SLIDES:
        rec = recs[s["lockup"]]
        original = ORIGINALS / s["original"]
        final = FINAL / s["file"]
        src_svg = SOURCE / f"{s['id']}.svg"
        m["slides"].append({
            "id": s["id"], "final_file": f"final/{s['file']}", "final_sha256": sha(final),
            "original_file": f"originals/{s['original']}", "original_sha256": sha(original),
            "source_file": f"source/{s['id']}.svg", "source_sha256": sha(src_svg),
            "dimensions": [W, H], "copy": s["copy"], "creative_fidelity_review": s["fidelity"],
            "canonical_lockup_id": s["lockup"], "canonical_lockup_sha256": rec["sha256"],
            "canonical_logo_sha256": SEAL_SHA, "canonical_seal_sha256": SEAL_SHA,
            "logo_width_px": s["logo_width"], "minimum_supported_display_width_px": rec["minimum_supported_display_size"]["screen_width_px"],
            "logo_x_y_px": s["logo_xy"], "composition_note": s["direction"],
        })
    MANIFEST_PATH.write_text(json.dumps(m, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"Built {len(SLIDES)} slides at {W}x{H}; source SVGs and canonical lockups verified.")


if __name__ == "__main__":
    main()
