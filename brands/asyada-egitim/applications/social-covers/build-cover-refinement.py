#!/usr/bin/env python3
"""Refine X and Facebook covers to match the approved LinkedIn editorial style."""

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

PAPER = "#F7F3E9"
INK = "#1D2027"
RED = "#BD2120"
SEAL_SHA = "8f5d46f0302c4cc7e3765d3bfce9445f842dbd92f1e0f8fbe99f9f509c77e11a"
SLOGAN = "Üniversite için başka bir dünya var."
COUNTRIES = ["Çin", "Japonya", "Güney Kore", "Singapur", "Hong Kong"]


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def logo(lockup_id: str, x: int, y: int, width: int) -> tuple[str, dict]:
    record = RECORDS[lockup_id]
    path = ROOT / record["canonical_file_path"]
    assert sha(path) == record["sha256"]
    raw = path.read_bytes()
    view = re.search(rb'<svg[^>]*viewBox="([^"]+)"', raw).group(1).decode()
    _, _, native_w, native_h = map(float, view.split())
    height = width * native_h / native_w
    embedded = base64.b64encode(raw).decode("ascii")
    image = (f'<image x="{x}" y="{y}" width="{width}" height="{height:.2f}" '
             f'preserveAspectRatio="xMidYMid meet" href="data:image/svg+xml;base64,{embedded}"/>')
    return image, {
        "id": lockup_id,
        "path": str(path.relative_to(ROOT)),
        "sha256": sha(path),
        "width_px": width,
        "height_px": round(height, 2),
    }


def header(width: int, height: int, title: str, description: str, mark: dict) -> str:
    meta = {
        "brand_id": "asyada-egitim",
        "status": "APPLICATION CANDIDATE — NOT A NEW CANONICAL TEMPLATE",
        "canonical_lockup_id": mark["id"],
        "canonical_lockup_sha256": mark["sha256"],
        "canonical_logo_sha256": SEAL_SHA,
        "canonical_seal_sha256": SEAL_SHA,
    }
    return f'''<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="0 0 {width} {height}" role="img" aria-labelledby="title desc">
<title id="title">{title}</title><desc id="desc">{description}</desc>
<metadata>{json.dumps(meta, ensure_ascii=False)}</metadata>
<defs><style>
@font-face{{font-family:Jost;src:url('Jost-VF.ttf')}}
.display{{font-family:Jost,'Arial',sans-serif;font-weight:600;letter-spacing:-.045em}}
.medium{{font-family:Jost,'Arial',sans-serif;font-weight:500;letter-spacing:-.02em}}
.label{{font-family:Jost,'Arial',sans-serif;font-weight:600;letter-spacing:.045em}}
.eyebrow{{font-family:Jost,'Arial',sans-serif;font-weight:650;letter-spacing:.13em}}
</style></defs>'''


def render(slug: str, dimensions: tuple[int, int], title: str, description: str,
           lockup_id: str, coords: tuple[int, int, int], artwork) -> dict:
    width, height = dimensions
    x, y, mark_width = coords
    mark_svg, mark = logo(lockup_id, x, y, mark_width)
    source = header(width, height, title, description, mark) + artwork(mark_svg) + "</svg>"
    svg_file = ASSETS / f"{slug}.svg"
    png_file = ASSETS / f"{slug}.png"
    svg_file.write_text(source, encoding="utf-8")
    subprocess.run(["rsvg-convert", "-w", str(width), "-h", str(height), str(svg_file), "-o", str(png_file)], check=True)
    min_width = 528 if lockup_id.startswith("H-02") else 200
    return {
        "platform": slug.split("-")[0].upper(),
        "id": slug,
        "dimensions_px": {"width": width, "height": height},
        "png": f"assets/{png_file.name}",
        "png_sha256": sha(png_file),
        "svg": f"assets/{svg_file.name}",
        "svg_sha256": sha(svg_file),
        "formats": ["PNG", "SVG (editable source)"],
        "canonical_lockup_id": mark["id"],
        "canonical_lockup_path": mark["path"],
        "canonical_lockup_sha256": mark["sha256"],
        "canonical_logo_sha256": SEAL_SHA,
        "canonical_seal_sha256": SEAL_SHA,
        "minimum_lockup_width_px": min_width,
        "lockup_width_px": mark_width,
        "status": "APPLICATION CANDIDATE — NOT A NEW CANONICAL TEMPLATE",
    }


def plain_countries(x: int, y1: int, y2: int, colour: str, size: int) -> str:
    return f'''<text x="{x}" y="{y1}" fill="{colour}" class="label" font-size="{size}">Çin <tspan fill="{RED}">·</tspan> Japonya <tspan fill="{RED}">·</tspan> Güney Kore</text>
<text x="{x}" y="{y2}" fill="{colour}" class="label" font-size="{size}">Singapur <tspan fill="{RED}">·</tspan> Hong Kong</text>'''


def x_art(mark: str) -> str:
    return f'''<rect width="1500" height="500" fill="{PAPER}"/>
<rect width="18" height="500" fill="{RED}"/>
<path d="M1010 72V428" stroke="{INK}" stroke-width="1" opacity=".2"/>
{mark}
<text x="1060" y="142" fill="{INK}" class="medium" font-size="37">Üniversite için</text>
<text x="1060" y="205" fill="{RED}" class="display" font-size="47">başka bir dünya</text>
<text x="1060" y="258" fill="{INK}" class="display" font-size="43">var.</text>
<path d="M1060 284H1435" stroke="{RED}" stroke-width="2"/>
{plain_countries(1060, 335, 371, INK, 17)}'''


def facebook_art(mark: str) -> str:
    return f'''<rect width="851" height="315" fill="{PAPER}"/>
<rect width="13" height="315" fill="{RED}"/>
<path d="M478 48V269" stroke="{INK}" stroke-width="1" opacity=".2"/>
{mark}
<text x="510" y="104" fill="{INK}" class="medium" font-size="25">Üniversite için</text>
<text x="510" y="151" fill="{RED}" class="display" font-size="32">başka bir dünya var.</text>
<path d="M510 172H813" stroke="{RED}" stroke-width="2"/>
{plain_countries(510, 215, 243, INK, 15)}'''


def main() -> None:
    original = json.loads((OUT / "manifest.json").read_text())
    linkedin = next(a for a in original["assets"] if a["id"] == "linkedin-page-cover-v2")
    font = ROOT / "docs/instagram/carousel-01/assets/Jost-VF.ttf"
    (ASSETS / "Jost-VF.ttf").write_bytes(font.read_bytes())
    x = render(
        "x-profile-header-v3", (1500, 500),
        "X cover — Ülke isimleri LinkedIn yönünde sadeleştirildi",
        "Açık zemin, kırmızı imza çizgisi ve düz tipografik ülke listesi. Sol-alt avatar alanı açık bırakılmıştır.",
        "H-02/light", (452, 151, 528), x_art,
    )
    facebook = render(
        "facebook-page-cover-v3", (851, 315),
        "Facebook Page cover — LinkedIn yönünde sadeleştirilmiş ülke listesi",
        "Açık zemin, kırmızı vurgu ve aynı renkli tipografik ülke listesi. Sol profil fotoğrafı alanı açık bırakılmıştır.",
        "D-04/light", (245, 109, 210), facebook_art,
    )
    original.update({
        "version": "03 — LinkedIn editorial style carried into X and Facebook",
        "slogan": SLOGAN,
        "countries": COUNTRIES,
        "country_treatment": "Uniform ink typography with small red separators; no country-specific colored backgrounds.",
        "assets": [x, linkedin, facebook],
    })
    (OUT / "manifest.json").write_text(json.dumps(original, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
