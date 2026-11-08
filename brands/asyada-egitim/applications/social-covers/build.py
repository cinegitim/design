#!/usr/bin/env python3
"""Build evergreen social-cover artwork from approved Asya'da Eğitim assets."""

from __future__ import annotations

import base64
import hashlib
import json
import re
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[4]
OUT = ROOT / "docs" / "social-covers"
ASSETS = OUT / "assets"
LOCKUPS = ROOT / "brands/asyada-egitim/assets/lockups"
SEAL_SHA = "8f5d46f0302c4cc7e3765d3bfce9445f842dbd92f1e0f8fbe99f9f509c77e11a"
INK = "#1D2027"
PAPER = "#F7F3E9"
RED = "#BD2120"


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def lockup_image(name: str, x: int, y: int, width: int) -> tuple[str, dict]:
    path = LOCKUPS / name
    raw = path.read_bytes()
    viewbox = re.search(rb'<svg[^>]*viewBox="([^"]+)"', raw).group(1).decode()
    _, _, native_w, native_h = map(float, viewbox.split())
    height = width * native_h / native_w
    payload = base64.b64encode(raw).decode("ascii")
    element = (f'<image x="{x}" y="{y}" width="{width}" height="{height:.2f}" '
               f'preserveAspectRatio="xMidYMid meet" href="data:image/svg+xml;base64,{payload}"/>')
    return element, {"path": str(path.relative_to(ROOT)), "sha256": sha(path), "width_px": width}


def svg_document(width: int, height: int, title: str, body: str, lockup: dict) -> str:
    return f'''<svg xmlns="http://www.w3.org/2000/svg" xmlns:xlink="http://www.w3.org/1999/xlink" width="{width}" height="{height}" viewBox="0 0 {width} {height}" role="img" aria-labelledby="title desc">
<title id="title">{title}</title><desc id="desc">Asya'da Eğitim social cover. Exact canonical lockup embedded without artwork changes.</desc>
<metadata>{{"brand_id":"asyada-egitim","status":"APPLICATION CANDIDATE — NOT A NEW CANONICAL TEMPLATE","canonical_lockup_id":"{lockup['id']}","canonical_lockup_sha256":"{lockup['sha256']}","canonical_seal_sha256":"{SEAL_SHA}"}}</metadata>
<defs><style>
@font-face{{font-family:Jost;src:url('Jost-VF.ttf')}}
.display{{font-family:Jost,'Arial',sans-serif;font-weight:600;letter-spacing:-.045em}}
.body{{font-family:Jost,'Arial',sans-serif;font-weight:450;letter-spacing:.015em}}
.label{{font-family:Jost,'Arial',sans-serif;font-weight:600;letter-spacing:.15em}}
</style></defs>
{body}
</svg>'''


def build_one(slug: str, width: int, height: int, title: str, lockup_filename: str,
              lockup_id: str, lockup_x: int, lockup_y: int, lockup_w: int, art) -> dict:
    lockup_element, linfo = lockup_image(lockup_filename, lockup_x, lockup_y, lockup_w)
    lockup = {"id": lockup_id, **linfo}
    body = art(lockup_element, width, height)
    svg = svg_document(width, height, title, body, lockup)
    svg_path = ASSETS / f"{slug}.svg"
    png_path = ASSETS / f"{slug}.png"
    svg_path.write_text(svg, encoding="utf-8")
    subprocess.run(["rsvg-convert", "-w", str(width), "-h", str(height), str(svg_path), "-o", str(png_path)], check=True)
    return {
        "platform": slug.split("-")[0].upper(), "id": slug, "title": title,
        "dimensions_px": {"width": width, "height": height},
        "format": ["PNG", "SVG"], "png": str(png_path.relative_to(OUT)),
        "png_sha256": sha(png_path), "svg": str(svg_path.relative_to(OUT)),
        "svg_sha256": sha(svg_path), "canonical_lockup_id": lockup_id,
        "canonical_lockup_path": linfo["path"],
        "canonical_lockup_sha256": linfo["sha256"],
        "canonical_seal_sha256": SEAL_SHA,
        "minimum_lockup_width_px": 528 if lockup_id.startswith("H-02") else 352,
        "lockup_width_px": lockup_w,
        "tokens": {"paper": PAPER, "ink": INK, "red": RED, "typeface": "Jost"},
        "status": "APPLICATION CANDIDATE — NOT A NEW CANONICAL TEMPLATE",
    }


def instagram_art(logo: str, w: int, h: int) -> str:
    return f'''<rect width="1080" height="1440" fill="{PAPER}"/>
<path d="M0 0H1080V312H0Z" fill="{INK}"/>
<path d="M0 272H1080" stroke="{RED}" stroke-width="8"/>
<text x="72" y="95" fill="{PAPER}" class="label" font-size="23">ASYA'DA EĞİTİM  /  YOL HARİTASI</text>
<text x="72" y="185" fill="{PAPER}" class="display" font-size="63">Eğitim yolculuğunu</text>
<text x="72" y="252" fill="{PAPER}" class="display" font-size="63">bilgiyle planla.</text>
<text x="76" y="386" fill="{RED}" class="label" font-size="20">HEDEF</text>
<text x="76" y="640" fill="{RED}" class="label" font-size="20">BAŞVURU</text>
<text x="76" y="894" fill="{RED}" class="label" font-size="20">YAŞAM</text>
<path d="M190 380 C450 380 270 634 520 634 S630 888 862 888" fill="none" stroke="{RED}" stroke-width="5"/>
<circle cx="190" cy="380" r="13" fill="{PAPER}" stroke="{RED}" stroke-width="5"/>
<circle cx="520" cy="634" r="13" fill="{PAPER}" stroke="{RED}" stroke-width="5"/>
<circle cx="862" cy="888" r="13" fill="{PAPER}" stroke="{RED}" stroke-width="5"/>
<path d="M930 352V922" stroke="{INK}" stroke-width="1" opacity=".22"/>
<text x="76" y="974" fill="{INK}" class="display" font-size="40">Uzak bir fikir değil.</text>
<text x="76" y="1022" fill="{INK}" class="body" font-size="27">Üzerinde çalışılabilir bir plan.</text>
{logo}
'''


def x_art(logo: str, w: int, h: int) -> str:
    return f'''<rect width="1500" height="500" fill="{INK}"/>
<path d="M390 0H1500V500H390Z" fill="#252932"/>
<path d="M680 454 C840 454 872 430 1010 430 S1250 453 1500 420" fill="none" stroke="{RED}" stroke-width="3" opacity=".85"/>
<path d="M680 466 C840 466 872 442 1010 442 S1250 465 1500 432" fill="none" stroke="{PAPER}" stroke-width="1" opacity=".24"/>
<text x="360" y="110" fill="{RED}" class="label" font-size="18">ASYA'DA EĞİTİM  ·  ÜNİVERSİTE DANIŞMANLIĞI</text>
<text x="360" y="205" fill="{PAPER}" class="display" font-size="60">Hedefini netleştir.</text>
<text x="360" y="278" fill="{PAPER}" class="display" font-size="60">Süreci birlikte planla.</text>
<text x="360" y="340" fill="{PAPER}" class="body" font-size="23" opacity=".8">Ülke · program · başvuru · kampüs yaşamı</text>
<rect x="360" y="382" width="244" height="48" rx="24" fill="{RED}"/>
<text x="482" y="413" text-anchor="middle" fill="{PAPER}" class="label" font-size="17">İLK ADIMI KONUŞALIM</text>
{logo}'''


def linkedin_art(logo: str, w: int, h: int) -> str:
    return f'''<rect width="1128" height="376" fill="{PAPER}"/>
<rect x="0" y="0" width="20" height="376" fill="{RED}"/>
<path d="M48 48V328" stroke="{INK}" stroke-width="2" opacity=".18"/>
<text x="72" y="68" fill="{RED}" class="label" font-size="14">ASYA'DA EĞİTİM</text>
<text x="72" y="125" fill="{INK}" class="display" font-size="36">Hedefinden</text>
<text x="72" y="169" fill="{INK}" class="display" font-size="36">kampüse,</text>
<text x="72" y="213" fill="{INK}" class="display" font-size="36">daha net bir yol.</text>
<text x="72" y="262" fill="{INK}" class="body" font-size="17">Ülke ve program araştırmasından</text>
<text x="72" y="287" fill="{INK}" class="body" font-size="17">başvuru planına.</text>
<path d="M72 322H410" stroke="{RED}" stroke-width="2"/>
{logo}'''


def main() -> None:
    ASSETS.mkdir(parents=True, exist_ok=True)
    # Keep the selected Jost variable font adjacent for editable SVG previews.
    font_src = ROOT / "docs/instagram/carousel-01/assets/Jost-VF.ttf"
    (ASSETS / "Jost-VF.ttf").write_bytes(font_src.read_bytes())
    items = [
        build_one("instagram-feed-cover", 1080, 1440, "Instagram feed cover — Asya'da Eğitim",
                  "p-01-primary-stacked-light.svg", "P-01/light", 364, 1070, 352, instagram_art),
        build_one("x-profile-header", 1500, 500, "X profile header — Asya'da Eğitim",
                  "h-02-primary-horizontal-dark.svg", "H-02/dark", 930, 128, 540, x_art),
        build_one("linkedin-page-cover", 1128, 376, "LinkedIn Page cover — Asya'da Eğitim",
                  "h-02-primary-horizontal-light.svg", "H-02/light", 544, 74, 528, linkedin_art),
    ]
    manifest = {
        "brand_id": "asyada-egitim",
        "purpose": "Platform-specific evergreen profile/brand covers",
        "source_tokens": "Approved identity records and existing Instagram applications; no brand-system.md currently exists.",
        "status": "APPLICATION CANDIDATES — NOT NEW CANONICAL TEMPLATES",
        "created": "2026-10-08",
        "platform_specs": {
            "instagram": {"dimensions_px": "1080x1440", "use": "portrait feed cover; Instagram has no profile header"},
            "x": {"dimensions_px": "1500x500", "use": "profile header; left avatar-overlap region intentionally quiet"},
            "linkedin": {"dimensions_px": "1128x376", "use": "LinkedIn Page cover image"},
        },
        "assets": items,
    }
    (OUT / "manifest.json").write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
