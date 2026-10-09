#!/usr/bin/env python3
"""Build the slogan-led, three-platform Asya'da Eğitim cover set."""

from __future__ import annotations

import base64
import hashlib
import json
import re
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[4]
OUT = ROOT / "docs/social-covers"
ASSETS = OUT / "assets"
LOCKUPS = ROOT / "brands/asyada-egitim/assets/lockups"
LOCKUP_MANIFEST = json.loads((LOCKUPS / "canonical-lockups.json").read_text())
RECORDS = {r["canonical_lockup_id"]: r for r in LOCKUP_MANIFEST["records"]}

INK = "#1D2027"
PAPER = "#F7F3E9"
RED = "#BD2120"
ACCENTS = ["#BD2120", "#D7A85B", "#567B94", "#548071", "#C87966"]
COUNTRIES = ["Çin", "Japonya", "Güney Kore", "Singapur", "Hong Kong"]
SEAL_SHA = "8f5d46f0302c4cc7e3765d3bfce9445f842dbd92f1e0f8fbe99f9f509c77e11a"
CANONICAL_LOGO_SHA = SEAL_SHA


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def get_lockup(lockup_id: str, x: int, y: int, width: int) -> tuple[str, dict]:
    record = RECORDS[lockup_id]
    path = ROOT / record["canonical_file_path"]
    raw = path.read_bytes()
    assert sha(path) == record["sha256"]
    viewbox = re.search(rb'<svg[^>]*viewBox="([^"]+)"', raw).group(1).decode()
    _, _, native_w, native_h = map(float, viewbox.split())
    height = width * native_h / native_w
    image = base64.b64encode(raw).decode("ascii")
    element = (f'<image x="{x}" y="{y}" width="{width}" height="{height:.2f}" '
               f'preserveAspectRatio="xMidYMid meet" href="data:image/svg+xml;base64,{image}"/>')
    return element, {"id": lockup_id, "path": str(path.relative_to(ROOT)),
                     "sha256": sha(path), "width_px": width, "height_px": round(height, 2)}


def chip(x: int, y: int, label: str, colour: str, *, dark_label: bool = False,
         height: int = 34, font_size: int = 17) -> str:
    width = max(70, int(len(label) * font_size * .61 + 30))
    ink = INK if dark_label else PAPER
    return f'''<g>
<rect x="{x}" y="{y}" width="{width}" height="{height}" rx="{height // 2}" fill="{colour}"/>
<text x="{x + width/2:.1f}" y="{y + height*.68:.1f}" text-anchor="middle" fill="{ink}" class="label" font-size="{font_size}">{label}</text>
</g>'''


def country_row(x: int, y: int, gap: int, *, compact: bool = False,
                light_surface: bool = False) -> str:
    parts = []
    cursor = x
    for i, (name, colour) in enumerate(zip(COUNTRIES, ACCENTS)):
        dark = light_surface and i in (1, 2, 3, 4)
        h = 29 if compact else 34
        fs = 14 if compact else 17
        width = max(70, int(len(name) * fs * .61 + 30))
        parts.append(chip(cursor, y, name, colour, dark_label=dark, height=h, font_size=fs))
        cursor += width + gap
    return "\n".join(parts)


def head(width: int, height: int, title: str, desc: str, lockup: dict) -> str:
    metadata = {
        "brand_id": "asyada-egitim",
        "application": "slogan-led social page cover",
        "status": "APPLICATION CANDIDATE — NOT A NEW CANONICAL TEMPLATE",
        "canonical_lockup_id": lockup["id"],
        "canonical_lockup_sha256": lockup["sha256"],
        "canonical_logo_sha256": CANONICAL_LOGO_SHA,
        "canonical_seal_sha256": SEAL_SHA,
    }
    return f'''<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="0 0 {width} {height}" role="img" aria-labelledby="title desc">
<title id="title">{title}</title><desc id="desc">{desc}</desc>
<metadata>{json.dumps(metadata, ensure_ascii=False)}</metadata>
<defs><style>
@font-face{{font-family:Jost;src:url('Jost-VF.ttf')}}
.display{{font-family:Jost,'Arial',sans-serif;font-weight:600;letter-spacing:-.045em}}
.medium{{font-family:Jost,'Arial',sans-serif;font-weight:500;letter-spacing:-.02em}}
.label{{font-family:Jost,'Arial',sans-serif;font-weight:600;letter-spacing:.045em}}
.eyebrow{{font-family:Jost,'Arial',sans-serif;font-weight:650;letter-spacing:.13em}}
</style></defs>'''


def render(slug: str, width: int, height: int, title: str, desc: str,
           lockup_id: str, lockup_x: int, lockup_y: int, lockup_w: int, art) -> dict:
    logo, lockup = get_lockup(lockup_id, lockup_x, lockup_y, lockup_w)
    svg = head(width, height, title, desc, lockup) + art(logo) + "</svg>"
    svg_file = ASSETS / f"{slug}.svg"
    png_file = ASSETS / f"{slug}.png"
    svg_file.write_text(svg, encoding="utf-8")
    subprocess.run(["rsvg-convert", "-w", str(width), "-h", str(height), str(svg_file), "-o", str(png_file)], check=True)
    min_width = 528 if lockup_id.startswith("H-02") else 200
    return {
        "platform": slug.split("-")[0].upper(), "id": slug,
        "dimensions_px": {"width": width, "height": height},
        "png": f"assets/{png_file.name}", "png_sha256": sha(png_file),
        "svg": f"assets/{svg_file.name}", "svg_sha256": sha(svg_file),
        "formats": ["PNG", "SVG (editable source)"],
        "canonical_lockup_id": lockup["id"],
        "canonical_lockup_path": lockup["path"],
        "canonical_lockup_sha256": lockup["sha256"],
        "canonical_logo_sha256": CANONICAL_LOGO_SHA,
        "canonical_seal_sha256": SEAL_SHA,
        "minimum_lockup_width_px": min_width,
        "lockup_width_px": lockup_w,
        "status": "APPLICATION CANDIDATE — NOT A NEW CANONICAL TEMPLATE",
    }


def x_art(logo: str) -> str:
    return f'''<rect width="1500" height="500" fill="{INK}"/>
<path d="M318 0H515L423 500H318Z" fill="{RED}"/>
<path d="M424 0H1500V500H424Z" fill="#262A31"/>
<path d="M485 65H875" stroke="{PAPER}" stroke-width="1" opacity=".24"/>
<text x="488" y="111" fill="{RED}" class="eyebrow" font-size="17">BEŞ ÜLKE · FARKLI OLASILIKLAR</text>
<text x="488" y="174" fill="{PAPER}" class="medium" font-size="39">Üniversite için</text>
<text x="488" y="239" fill="{PAPER}" class="display" font-size="52">başka bir dünya</text>
<text x="488" y="295" fill="{RED}" class="display" font-size="46">var.</text>
{country_row(488, 374, 12)}
{logo}'''


def linkedin_art(logo: str) -> str:
    return f'''<rect width="1512" height="256" fill="{PAPER}"/>
<rect x="0" y="0" width="18" height="256" fill="{RED}"/>
<path d="M600 22V234" stroke="{INK}" stroke-width="1" opacity=".17"/>
<text x="638" y="83" fill="{INK}" class="medium" font-size="34">Üniversite için</text>
<text x="638" y="138" fill="{RED}" class="display" font-size="47">başka bir dünya var.</text>
<text x="638" y="177" fill="{INK}" class="eyebrow" font-size="13">ÇİN · JAPONYA · GÜNEY KORE · SİNGAPUR · HONG KONG</text>
<path d="M638 199H1255" stroke="{RED}" stroke-width="2"/>
{logo}'''


def facebook_art(logo: str) -> str:
    return f'''<rect width="851" height="315" fill="{PAPER}"/>
<path d="M0 0H851V315H0Z" fill="{INK}"/>
<path d="M0 0H188L128 315H0Z" fill="{RED}"/>
<path d="M189 0H851V315H130Z" fill="#272B33"/>
<circle cx="808" cy="38" r="78" fill="{RED}" opacity=".9"/>
<text x="248" y="87" fill="{PAPER}" class="medium" font-size="25">Üniversite için</text>
<text x="248" y="139" fill="{PAPER}" class="display" font-size="39">başka bir dünya</text>
<text x="248" y="182" fill="{RED}" class="display" font-size="38">var.</text>
{country_row(248, 229, 7, compact=True)}
{logo}'''


def main() -> None:
    ASSETS.mkdir(parents=True, exist_ok=True)
    font = ROOT / "docs/instagram/carousel-01/assets/Jost-VF.ttf"
    (ASSETS / "Jost-VF.ttf").write_bytes(font.read_bytes())
    assets = [
        render("x-profile-header-v2", 1500, 500, "X cover — Üniversite için başka bir dünya var",
               "Slogan ve beş çalışma ülkesi, X avatarının sol-alt alanından uzakta.",
               "H-02/dark", 932, 136, 528, x_art),
        render("linkedin-page-cover-v2", 1512, 256, "LinkedIn Page cover — Üniversite için başka bir dünya var",
               "Güncel LinkedIn Page cover ölçüsü 1512×256. Slogan ve ülkeler orta güvenli alanda.",
               "H-02/light", 48, 29, 528, linkedin_art),
        render("facebook-page-cover-v2", 851, 315, "Facebook Page cover — Üniversite için başka bir dünya var",
               "Meta'nın önerdiği 851×315 yükleme ölçüsünde, profil fotoğrafı örtüşme alanından uzakta.",
               "D-04/dark", 576, 59, 210, facebook_art),
    ]
    data = {
        "brand_id": "asyada-egitim",
        "version": "02 — slogan and destination set",
        "slogan": "Üniversite için başka bir dünya var.",
        "countries": COUNTRIES,
        "country_accent_colors": ACCENTS,
        "source_tokens": "Approved identity records and the existing country-world application; campaign accent colors are application-only, not canonical brand tokens.",
        "status": "APPLICATION CANDIDATES — NOT NEW CANONICAL TEMPLATES",
        "dimensions_researched": {
            "X": {"upload_px": [1500, 500], "source": "https://help.x.com/en/managing-your-account/how-to-customize-your-profile", "safe_zone_note": "X notes possible 60px top/bottom crop; avatar overlaps lower-left. Key content inset."},
            "LinkedIn Page": {"upload_px": [1512, 256], "source": "https://www.linkedin.com/help/linkedin/answer/a563309/image-specifications-for-your-linkedin-pages-and-career-pages", "note": "Current official Page cover upload size; max 3MB. Older 1128×376 is a separate Life tab main image."},
            "Facebook Page": {"upload_px": [851, 315], "source": "https://www.facebook.com/help/125379114252045", "note": "Meta recommended upload; visible crop can vary, profile picture overlaps left side."},
        },
        "assets": assets,
    }
    (OUT / "manifest.json").write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
