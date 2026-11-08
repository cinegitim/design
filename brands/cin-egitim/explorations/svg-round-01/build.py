#!/usr/bin/env python3
"""Trace the existing SR symbol with Potrace into genuine SVG paths.

No image model calls, typographic elements, new logo design or canonicalization.
Dependencies: Pillow and Potrace 1.16; rsvg-convert for review raster exports.
"""
import argparse
from copy import deepcopy
import hashlib
import json
from pathlib import Path
import platform
import shutil
from statistics import median
import subprocess
import tempfile
import xml.etree.ElementTree as ET

from PIL import Image, ImageDraw
import PIL

ROOT = Path(__file__).resolve().parents[4]
BUNDLE = Path(__file__).resolve().parent
PUBLIC = ROOT / "docs/cin-egitim/svg-round-01"
INPUT = ROOT / "brands/cin-egitim/enhancements/target-symbol-super-resolution-4x.png"
LOCK = ROOT / "brands/cin-egitim/reference/target-lock.json"
NS = "http://www.w3.org/2000/svg"
ET.register_namespace("", NS)
EXPECTED_INPUT = "56ad9bc59a50a53f44db2c91800a5470868002b70fb692107c4e8e115582bdc7"
PARAMETERS = {"turdsize": 2, "alphamax": 1.0, "opttolerance": 0.12, "unit": 100}


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def classify(rgb):
    r, g, b = rgb
    if r - g > 70 and r - b > 45 and r > 90:
        return "red"
    if max(rgb) < 140 and max(rgb) - min(rgb) < 40:
        return "ink"
    return None


def sample_palette(image):
    channels = {"red": [[], [], []], "ink": [[], [], []]}
    for rgb in image.getdata():
        kind = classify(rgb)
        # Avoid white-background antialias fringe when sampling pigment.
        if kind == "red" and rgb[1] < 60 or kind == "ink" and max(rgb) < 80:
            for i, value in enumerate(rgb):
                channels[kind][i].append(value)
    return {kind: "#" + "".join(f"{int(median(c)):02X}" for c in data)
            for kind, data in channels.items()}


def write_pbm(path, image, kind):
    width, height = image.size
    px = image.load()
    # PBM uses 1 for foreground/black. Rows are padded to full bytes.
    data = bytearray()
    for y in range(height):
        for start in range(0, width, 8):
            value = 0
            for bit in range(8):
                x = start + bit
                if x < width and classify(px[x, y]) == kind:
                    value |= 1 << (7 - bit)
            data.append(value)
    path.write_bytes(f"P4\n{width} {height}\n".encode() + data)


def trace(potrace, pbm, result):
    subprocess.run([potrace, str(pbm), "--svg", "--flat", "--output", str(result),
                    "--turdsize", str(PARAMETERS["turdsize"]),
                    "--alphamax", str(PARAMETERS["alphamax"]),
                    "--opttolerance", str(PARAMETERS["opttolerance"]),
                    "--unit", str(PARAMETERS["unit"])], check=True)
    tree = ET.parse(result).getroot()
    group = next(tree.iter(f"{{{NS}}}g"))
    result_group = deepcopy(group)
    for attribute in ("fill", "stroke"):
        result_group.attrib.pop(attribute, None)
    return result_group


def write_svg(width, height, groups, palette, path):
    root = ET.Element(f"{{{NS}}}svg", {"viewBox": f"0 0 {width} {height}",
                                     "width": str(width), "height": str(height),
                                     "role": "img", "aria-labelledby": "title desc"})
    ET.SubElement(root, f"{{{NS}}}title", {"id": "title"}).text = "Çin Eğitim — SVG sembol adayı"
    ET.SubElement(root, f"{{{NS}}}desc", {"id": "desc"}).text = (
        "Son süper çözünürlük PNG'sinden izlenen kırmızı fırça halkası, siyah pagoda "
        "ve mürekkep zemini. Yalnız vektör yolları; tipografi yok. İnsan onayı bekliyor.")
    for kind in ("red", "ink"):
        group = deepcopy(groups[kind])
        group.set("id", "brush-ring" if kind == "red" else "pagoda-and-ink-ground")
        group.set("fill", palette[kind])
        group.set("stroke", "none")
        # Potrace subpaths include interior holes; do not fill their gaps.
        group.set("fill-rule", "evenodd")
        root.append(group)
    ET.indent(root, space="  ")
    path.write_bytes(ET.tostring(root, encoding="utf-8", xml_declaration=True))


def render(svg, png, width):
    subprocess.run(["rsvg-convert", "-w", str(width), "-o", str(png), str(svg)], check=True)


def comparison_and_metrics():
    source = Image.open(BUNDLE / "source-sr.png").convert("RGB")
    rgba = Image.open(BUNDLE / "symbol-preview.png").convert("RGBA")
    rendered = Image.alpha_composite(Image.new("RGBA", rgba.size, "white"), rgba).convert("RGB")
    canvas = Image.new("RGB", (1872, 988), "#F0ECE4")
    draw = ImageDraw.Draw(canvas)
    for image, x, label in [(source, 12, "SOURCE: existing super-resolution PNG"),
                            (rendered, 944, "SVG: traced paths / two solid colours")]:
        draw.text((x, 10), label, fill="#202020")
        canvas.paste(image, (x, 36))
    canvas.save(BUNDLE / "source-vs-svg.png")

    # Full resolution regional crops: original coordinates for both panels.
    for filename, box in [
        ("detail-brush.png", (90, 680, 750, 882)),
        ("detail-pagoda.png", (416, 342, 794, 688)),
    ]:
        a, b = source.crop(box), rendered.crop(box)
        review = Image.new("RGB", (a.width * 2 + 36, a.height + 52), "#F0ECE4")
        d = ImageDraw.Draw(review)
        d.text((10, 8), "SOURCE", fill="#202020")
        d.text((a.width + 26, 8), "SVG", fill="#202020")
        review.paste(a, (10, 32))
        review.paste(b, (a.width + 26, 32))
        review.save(BUNDLE / filename)

    # Mask overlap is a shape/coverage check only, not aesthetic approval.
    metrics = {}
    src, dst = source.load(), rendered.load()
    for kind in ("red", "ink"):
        intersection = union = 0
        for y in range(source.height):
            for x in range(source.width):
                a, b = classify(src[x, y]) == kind, classify(dst[x, y]) == kind
                intersection += a and b
                union += a or b
        metrics[kind + "_mask_iou"] = round(intersection / union, 6)
    metrics["limits"] = "Masks measure flat-colour outline coverage, not shading, source detail authenticity or human approval."
    return metrics


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--potrace", default="potrace", help="Potrace 1.16 executable")
    args = parser.parse_args()
    metadata = json.loads((ROOT / "brands/cin-egitim/brand.json").read_text())
    if metadata.get("canonicalLogo", {}).get("locked"):
        raise RuntimeError("This round's SVG is human-approved and locked; create a new round for any regeneration.")
    assert digest(INPUT) == EXPECTED_INPUT, "Unexpected raster source; stop"
    lock_before = digest(LOCK)
    locked = json.loads(LOCK.read_text())
    reference = LOCK.parent / locked["target_image"]
    assert digest(reference) == locked["target_image_sha256"]
    potrace_version = subprocess.check_output([args.potrace, "--version"], text=True).splitlines()[0]
    assert potrace_version.startswith("potrace 1.16"), "Use pinned Potrace 1.16"
    image = Image.open(INPUT).convert("RGB")
    palette = sample_palette(image)
    shutil.copyfile(INPUT, BUNDLE / "source-sr.png")
    with tempfile.TemporaryDirectory(prefix="cin-svg-trace-") as temporary:
        temp = Path(temporary)
        groups = {}
        for kind in ("red", "ink"):
            mask, result = temp / (kind + ".pbm"), temp / (kind + ".svg")
            write_pbm(mask, image, kind)
            groups[kind] = trace(args.potrace, mask, result)
        write_svg(*image.size, groups, palette, BUNDLE / "symbol.svg")
        write_svg(*image.size, groups, {"red": palette["ink"], "ink": palette["ink"]},
                  BUNDLE / "symbol-mono.svg")
    render(BUNDLE / "symbol.svg", BUNDLE / "symbol-preview.png", image.width)
    render(BUNDLE / "symbol.svg", BUNDLE / "symbol-2x.png", image.width * 2)
    metrics = comparison_and_metrics()
    assert digest(LOCK) == lock_before and digest(INPUT) == EXPECTED_INPUT
    manifest = {
        "brand": "cin-egitim", "round": "svg-round-01", "executor": "OpenCode",
        "status": "REVIEW_ONLY / HUMAN_ACCEPTANCE_PENDING", "canonical": False,
        "typography": False, "embedded_raster": False,
        "source": "source-sr.png", "source_sha256": EXPECTED_INPUT,
        "locked_target_sha256": locked["target_image_sha256"],
        "reference_lock_sha256": lock_before,
        "input_dimensions": list(image.size),
        "method": "Separate pigment masks, Potrace cubic Bezier tracing, evenodd holes, sampled median pigment colours",
        "parameters": PARAMETERS, "palette": palette,
        "tools": {"potrace": potrace_version, "pillow": PIL.__version__,
                  "python": platform.python_version(),
                  "rsvg": subprocess.check_output(["rsvg-convert", "--version"], text=True).strip()},
        "metrics": metrics,
        "compromise": "Raster tonal shading is flattened to two sampled solid colours; outlines/holes traced from the SR candidate. No claim of pixel-identical recreation or new human approval.",
        "files": {},
    }
    for name in ["symbol.svg", "symbol-mono.svg", "source-sr.png", "symbol-preview.png",
                 "symbol-2x.png", "source-vs-svg.png", "detail-brush.png", "detail-pagoda.png"]:
        path = BUNDLE / name
        entry = {"sha256": digest(path)}
        if path.suffix == ".png":
            with Image.open(path) as img:
                entry["dimensions"] = list(img.size)
        else:
            entry["viewBox"] = "0 0 916 924"
            entry["paths"] = len(list(ET.parse(path).getroot().iter(f"{{{NS}}}path")))
        manifest["files"][name] = entry
    (BUNDLE / "manifest.json").write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + "\n")
    PUBLIC.mkdir(parents=True, exist_ok=True)
    for name in ["manifest.json"] + list(manifest["files"]):
        shutil.copyfile(BUNDLE / name, PUBLIC / name)
    print(json.dumps({"palette": palette, "metrics": metrics,
                      "svg_bytes": (BUNDLE / "symbol.svg").stat().st_size}, indent=2))


if __name__ == "__main__":
    main()
