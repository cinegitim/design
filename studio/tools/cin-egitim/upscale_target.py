#!/usr/bin/env python3
"""Conservative raster enlargement only; never redraw the locked source."""
from pathlib import Path
import hashlib
import json
import shutil
from PIL import Image, ImageFilter

ROOT = Path(__file__).resolve().parents[3]
REFERENCE = ROOT / "brands/cin-egitim/reference"
OUTPUT = ROOT / "brands/cin-egitim/enhancements"
PUBLIC = ROOT / "docs/cin-egitim/enhancements"


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    lock = json.loads((REFERENCE / "target-lock.json").read_text())
    source = REFERENCE / lock["target_image"]
    original_digest = digest(source)
    assert original_digest == lock["target_image_sha256"], "Locked target mismatch"
    with Image.open(source) as image:
        image = image.convert("RGB")
        original_size = image.size
        enlarged = image.resize((image.width * 6, image.height * 6), Image.Resampling.LANCZOS)
        enlarged = enlarged.filter(ImageFilter.UnsharpMask(radius=1.2, percent=60, threshold=3))
    OUTPUT.mkdir(parents=True, exist_ok=True)
    PUBLIC.mkdir(parents=True, exist_ok=True)
    destination = OUTPUT / "target-symbol-6x.png"
    enlarged.save(destination, format="PNG", optimize=True)
    manifest = {
        "status": "RASTER_ENLARGEMENT_REVIEW_PENDING",
        "authorization": "User requested quality improvement only after confirming the locked symbol.",
        "canonical_logo": False,
        "reference_lock_changed": False,
        "source": "../reference/target-symbol.png",
        "source_sha256": original_digest,
        "source_dimensions": list(original_size),
        "output": destination.name,
        "output_sha256": digest(destination),
        "output_dimensions": list(enlarged.size),
        "scale": 6,
        "resampler": "Pillow LANCZOS",
        "sharpen": {"algorithm": "UnsharpMask", "radius": 1.2, "percent": 60, "threshold": 3},
        "generated_detail": False,
        "svg_or_redrawing": False,
        "typography": False,
        "limitation": "Interpolation and mild sharpening improve enlarged presentation, not recover missing source detail.",
    }
    (OUTPUT / "manifest.json").write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + "\n")
    for name in (destination.name, "manifest.json"):
        shutil.copyfile(OUTPUT / name, PUBLIC / name)
    assert digest(source) == original_digest
    print(json.dumps(manifest, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
