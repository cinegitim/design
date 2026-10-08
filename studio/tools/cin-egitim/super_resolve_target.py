#!/usr/bin/env python3
"""Restore a separate raster candidate with local Real-ESRGAN inference.

Requires the official portable ncnn executable and matching x4plus model.
Never modifies the locked source or creates a vector logo.
"""
import argparse
import hashlib
import json
from pathlib import Path
import shutil
import subprocess

from PIL import Image, ImageDraw

ROOT = Path(__file__).resolve().parents[3]
REFERENCE = ROOT / "brands/cin-egitim/reference"
OUTPUT = ROOT / "brands/cin-egitim/enhancements"
PUBLIC = ROOT / "docs/cin-egitim/enhancements"
MODEL = "realesrgan-x4plus"


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def comparisons(source, restored):
    # Every panel has the same source crop coordinates and display size.
    original = Image.open(source).convert("RGB")
    previous = Image.open(OUTPUT / "target-symbol-6x.png").convert("RGB")
    enhanced = Image.open(restored).convert("RGB")
    items = [original, previous, enhanced]
    labels = ["ORIGINAL (enlarged for comparison)", "PREVIOUS: LANCZOS + SHARPEN", "REAL-ESRGAN SUPER RESOLUTION"]
    comparison = Image.new("RGB", (1422, 528), "#eeeae2")
    draw = ImageDraw.Draw(comparison)
    for i, (image, label) in enumerate(zip(items, labels)):
        x = 12 + i * 474
        draw.text((x, 10), label, fill="#222222")
        comparison.paste(image.resize((458, 462), Image.Resampling.LANCZOS), (x, 38))
    comparison.save(OUTPUT / "super-resolution-comparison.png")

    # A magnified roof detail makes noise/edge treatment visible without
    # changing the symbol's framing between the two methods.
    box = (110, 75, 188, 153)
    closeup = Image.new("RGB", (964, 510), "#eeeae2")
    draw = ImageDraw.Draw(closeup)
    for i, (image, scale, label) in enumerate([
        (previous, 6, "PREVIOUS: interpolation only"),
        (enhanced, 4, "NEW: model-based restoration"),
    ]):
        crop = image.crop(tuple(v * scale for v in box))
        crop = crop.resize((468, 468), Image.Resampling.LANCZOS)
        x = 8 + 482 * i
        draw.text((x, 8), label, fill="#222222")
        closeup.paste(crop, (x, 32))
    closeup.save(OUTPUT / "super-resolution-detail.png")


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--tool-dir", type=Path, required=True,
                        help="Directory containing official realesrgan-ncnn-vulkan and models/")
    args = parser.parse_args()
    tool_dir = args.tool_dir.resolve()
    executable = tool_dir / "realesrgan-ncnn-vulkan"
    models = tool_dir / "models"
    lock_path = REFERENCE / "target-lock.json"
    lock_hash = digest(lock_path)
    lock = json.loads(lock_path.read_text())
    source = REFERENCE / lock["target_image"]
    source_hash = digest(source)
    assert source_hash == lock["target_image_sha256"], "Locked target mismatch"
    OUTPUT.mkdir(parents=True, exist_ok=True)
    PUBLIC.mkdir(parents=True, exist_ok=True)
    restored = OUTPUT / "target-symbol-super-resolution-4x.png"
    command = [str(executable), "-i", str(source), "-o", str(restored),
               "-m", str(models), "-n", MODEL, "-s", "4", "-t", "256", "-f", "png"]
    subprocess.run(command, check=True, cwd=tool_dir)
    with Image.open(source) as image:
        original_size = image.size
    with Image.open(restored) as image:
        restored_size = image.size
    assert restored_size == tuple(v * 4 for v in original_size)
    assert digest(source) == source_hash and digest(lock_path) == lock_hash
    comparisons(source, restored)

    manifest = {
        "status": "SUPER_RESOLUTION_REVIEW_PENDING",
        "authorization": "User explicitly requested quality/detail improvement, not only a size increase.",
        "reference_lock_changed": False,
        "canonical_logo": False,
        "source": "../reference/target-symbol.png",
        "source_sha256": source_hash,
        "reference_lock_sha256": lock_hash,
        "source_dimensions": list(original_size),
        "output": restored.name,
        "output_sha256": digest(restored),
        "output_dimensions": list(restored_size),
        "method": "Local model-based Real-ESRGAN super-resolution + learned noise/artifact restoration",
        "model": MODEL,
        "scale": 4,
        "tile_size": 256,
        "tool_release": "v0.2.5.0 / ncnn-vulkan-20220424-macos",
        "official_download": "https://github.com/xinntao/Real-ESRGAN/releases/download/v0.2.5.0/realesrgan-ncnn-vulkan-20220424-macos.zip",
        "executable_sha256": digest(executable),
        "model_bin_sha256": digest(models / (MODEL + ".bin")),
        "model_param_sha256": digest(models / (MODEL + ".param")),
        "learned_detail_estimation": True,
        "text_to_image_generation": False,
        "svg_or_vectorization": False,
        "typography": False,
        "limitation": "The model estimates high-frequency detail, so fine brush texture and edges may change. Not a faithful-detail guarantee, new locked target, or approved production logo.",
        "comparisons": ["super-resolution-comparison.png", "super-resolution-detail.png"],
    }
    manifest_path = OUTPUT / "super-resolution-manifest.json"
    manifest_path.write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + "\n")
    for name in [restored.name, manifest_path.name] + manifest["comparisons"]:
        shutil.copyfile(OUTPUT / name, PUBLIC / name)
    print(json.dumps(manifest, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
