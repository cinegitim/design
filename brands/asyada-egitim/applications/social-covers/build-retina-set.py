#!/usr/bin/env python3
"""Export high-density v04 social covers from approved vector sources."""
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
PAPER, INK, RED = "#F7F3E9", "#1D2027", "#BD2120"
SEAL_SHA = "8f5d46f0302c4cc7e3765d3bfce9445f842dbd92f1e0f8fbe99f9f509c77e11a"
COUNTRIES = ["Çin", "Japonya", "Güney Kore", "Singapur", "Hong Kong"]


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def render(svg: str, svg_path: Path, png_path: Path, width: int, height: int) -> None:
    svg_path.write_text(svg, encoding="utf-8")
    subprocess.run(["rsvg-convert", "-w", str(width), "-h", str(height),
                    str(svg_path), "-o", str(png_path)], check=True)


def upscale_source(source: Path, dest: Path, png: Path, w: int, h: int) -> dict:
    svg = source.read_text(encoding="utf-8")
    svg, count = re.subn(r'(<svg\b[^>]*\bwidth=")[^"]+("[^>]*\bheight=")[^"]+',
                         rf'\g<1>{w}\g<2>{h}', svg, count=1)
    if count != 1:
        raise ValueError(f"Could not update SVG dimensions: {source}")
    render(svg, dest, png, w, h)
    return {"png": f"assets/{png.name}", "png_sha256": sha(png),
            "svg": f"assets/{dest.name}", "svg_sha256": sha(dest)}


def logo_element(lockup_id: str, x: int, y: int, width: int) -> tuple[str, dict]:
    record = RECORDS[lockup_id]
    path = ROOT / record["canonical_file_path"]
    if sha(path) != record["sha256"]:
        raise ValueError(f"Canonical lockup hash mismatch: {path}")
    raw = path.read_bytes()
    vb = re.search(rb'<svg[^>]*viewBox="([^"]+)"', raw).group(1).decode()
    _, _, native_w, native_h = map(float, vb.split())
    height = width * native_h / native_w
    href = base64.b64encode(raw).decode("ascii")
    tag = (f'<image x="{x}" y="{y}" width="{width}" height="{height:.2f}" '
           f'preserveAspectRatio="xMidYMid meet" href="data:image/svg+xml;base64,{href}"/>')
    return tag, {"id": lockup_id, "path": str(path.relative_to(ROOT)),
                 "sha256": sha(path), "design_width_px": width,
                 "design_height_px": round(height, 2)}


def fb_svg(title: str, logical_w: int, logical_h: int, pixel_w: int,
           pixel_h: int, dy: int, lockup: str) -> tuple[str, dict]:
    mark, mark_record = logo_element("D-04/light", 245, 109 + dy, 210)
    meta = {
        "brand_id": "asyada-egitim",
        "status": "APPLICATION CANDIDATE — NOT A NEW CANONICAL TEMPLATE",
        "facebook_crop": title,
        "canonical_lockup_id": mark_record["id"],
        "canonical_lockup_sha256": mark_record["sha256"],
        "canonical_logo_sha256": SEAL_SHA,
        "canonical_seal_sha256": SEAL_SHA,
    }
    body = f'''<rect width="{logical_w}" height="{logical_h}" fill="{PAPER}"/>
+<rect width="13" height="{logical_h}" fill="{RED}"/>
+<path d="M478 {48 + dy}V{logical_h - 46}" stroke="{INK}" stroke-width="1" opacity=".2"/>
+{mark}
+<text x="510" y="{104 + dy}" fill="{INK}" class="medium" font-size="25">Üniversite için</text>
+<text x="510" y="{151 + dy}" fill="{RED}" class="display" font-size="32">başka bir dünya var.</text>
+<path d="M510 {172 + dy}H813" stroke="{RED}" stroke-width="2"/>
+<text x="510" y="{215 + dy}" fill="{INK}" class="label" font-size="15">Çin <tspan fill="{RED}">·</tspan> Japonya <tspan fill="{RED}">·</tspan> Güney Kore</text>
+<text x="510" y="{243 + dy}" fill="{INK}" class="label" font-size="15">Singapur <tspan fill="{RED}">·</tspan> Hong Kong</text>'''.replace("\n+", "\n")
    svg = f'''<svg xmlns="http://www.w3.org/2000/svg" width="{pixel_w}" height="{pixel_h}" viewBox="0 0 {logical_w} {logical_h}" role="img" aria-labelledby="title desc">
+<title id="title">{title}</title><desc id="desc">Asya'da Eğitim sayfa kapağı. Masaüstü ve mobil için ayrı kırpım; profil fotoğrafı örtüşme alanı boş bırakılmıştır.</desc>
+<metadata>{json.dumps(meta, ensure_ascii=False)}</metadata>
+<defs><style>@font-face{{font-family:Jost;src:url('Jost-VF.ttf')}}.display{{font-family:Jost,'Arial',sans-serif;font-weight:600;letter-spacing:-.045em}}.medium{{font-family:Jost,'Arial',sans-serif;font-weight:500;letter-spacing:-.02em}}.label{{font-family:Jost,'Arial',sans-serif;font-weight:600;letter-spacing:.045em}}</style></defs>
+{body}</svg>'''.replace("\n+", "\n")
    return svg, mark_record


def make_facebook(slug: str, title: str, logical_w: int, logical_h: int,
                  pixel_w: int, pixel_h: int, dy: int) -> dict:
    dest, png = ASSETS / f"{slug}.svg", ASSETS / f"{slug}.png"
    svg, mark = fb_svg(title, logical_w, logical_h, pixel_w, pixel_h, dy, "D-04/light")
    render(svg, dest, png, pixel_w, pixel_h)
    return {
        "platform": "Facebook Page", "id": slug,
        "crop": title, "dimensions_px": {"width": pixel_w, "height": pixel_h},
        "design_viewbox_px": {"width": logical_w, "height": logical_h},
        "png": f"assets/{png.name}", "png_sha256": sha(png),
        "svg": f"assets/{dest.name}", "svg_sha256": sha(dest),
        "formats": ["PNG 2×", "SVG editable source"],
        "canonical_lockup_id": mark["id"],
        "canonical_lockup_path": mark["path"],
        "canonical_lockup_sha256": mark["sha256"],
        "canonical_logo_sha256": SEAL_SHA, "canonical_seal_sha256": SEAL_SHA,
        "minimum_lockup_width_px": 200, "lockup_width_design_px": mark["design_width_px"],
        "status": "APPLICATION CANDIDATE — NOT A NEW CANONICAL TEMPLATE",
    }


def main() -> None:
    ASSETS.mkdir(parents=True, exist_ok=True)
    (ASSETS / "Jost-VF.ttf").write_bytes(
        (ROOT / "docs/instagram/carousel-01/assets/Jost-VF.ttf").read_bytes())
    old = json.loads((OUT / "manifest.json").read_text(encoding="utf-8"))
    archived = OUT / "manifest-v03.json"
    if not archived.exists():
        archived.write_text(json.dumps(old, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    outputs = []
    for platform, stem, source_name, w, h in [
        ("X", "x-profile-header-v4-2x", "x-profile-header-v3.svg", 3000, 1000),
        ("LinkedIn Page", "linkedin-page-cover-v4-2x", "linkedin-page-cover-v2.svg", 3024, 512),
    ]:
        source = ASSETS / source_name
        dest, png = ASSETS / f"{stem}.svg", ASSETS / f"{stem}.png"
        hashes = upscale_source(source, dest, png, w, h)
        base = next(a for a in old["assets"] if a["platform"].lower().startswith(platform.split()[0].lower()))
        output = dict(base)
        output.update({"id": stem, "dimensions_px": {"width": w, "height": h},
                       **hashes, "formats": ["PNG 2×", "SVG editable source"],
                       "design_viewbox_px": base["dimensions_px"],
                       "supersedes": base["id"], "render_scale": 2})
        outputs.append(output)

    outputs.extend([
        make_facebook("facebook-page-cover-desktop-v4-2x", "Facebook desktop cover — 16:9",
                      851, 479, 1702, 958, 82),
        make_facebook("facebook-page-cover-mobile-v4-2x", "Facebook mobile cover — 2.4:1",
                      852, 355, 1704, 710, 20),
    ])
    result = {
        "brand_id": "asyada-egitim",
        "version": "04 — Retina exports + Facebook device crops",
        "slogan": "Üniversite için başka bir dünya var.",
        "countries": COUNTRIES,
        "status": "APPLICATION CANDIDATES — NOT NEW CANONICAL TEMPLATES",
        "country_treatment": "Uniform ink typography with small red separators; no country-specific colored backgrounds.",
        "source_assets": [
            "assets/x-profile-header-v3.svg (re-exported 2×)",
            "assets/linkedin-page-cover-v2.svg (re-exported 2×; composition retained)",
            "brands/asyada-egitim/assets/lockups/d-04-small-use-digital-light.svg",
        ],
        "dimensions_researched": {
            "X": {"platform_design_px": [1500, 500], "provided_export_px": [3000, 1000],
                  "source": "https://help.x.com/en/managing-your-account/how-to-customize-your-profile",
                  "note": "2× raster export; scalable vector source included."},
            "LinkedIn Page": {"platform_design_px": [1512, 256], "provided_export_px": [3024, 512],
                              "source": "https://www.linkedin.com/help/linkedin/answer/a563309/image-specifications-for-your-linkedin-pages-and-career-pages",
                              "note": "2× raster export; composition retained; scalable vector source included."},
            "Facebook Page": {"desktop_ratio": "16:9", "desktop_export_px": [1702, 958],
                               "mobile_ratio": "2.4:1", "mobile_export_px": [1704, 710],
                               "source": "https://www.facebook.com/help/125379114252045",
                               "note": "Separate 2× crops. Meta also lists 851×315 sRGB JPG under 100KB as a fastest-loading example; that 2.7:1 example does not match its separately listed desktop/mobile aspect ratios. These text/logo PNGs prioritize sharpness and use crop-specific compositions."},
        },
        "assets": outputs,
        "superseded_manifest": "manifest-v03.json",
    }
    (OUT / "manifest.json").write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
