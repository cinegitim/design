#!/usr/bin/env python3
"""Verify and package the Tsinghua V2 carousel; does not render or call APIs."""

from __future__ import annotations

import argparse
import hashlib
import json
import sys
import zipfile
from pathlib import Path, PurePosixPath
import xml.etree.ElementTree as ET

from PIL import Image, ImageCms

ROOT = Path(__file__).resolve().parent
REPO = ROOT.parents[3]
SEAL_SHA = "8f5d46f0302c4cc7e3765d3bfce9445f842dbd92f1e0f8fbe99f9f509c77e11a"
IDS = [
    "01-cover", "02-subject-rankings", "03-global-rankings", "04-english-hsk",
    "05-deadlines", "06-tuition-scholarships", "07-cta",
]
LOCKUPS = {
    "P-01/light": ("p-01-light.svg", "cdc4394d9fe69e2c2f44b6aedd4fc651ed19b3c3e021b10f46a8e0fe41b768b2", 352),
    "P-01/dark": ("p-01-dark.svg", "16fc8c66e338a72515dd1fe9c43d5fe4394317039db4a00ec2a2c93358b5577f", 352),
    "D-04/light": ("d-04-light.svg", "2ff2263dcdab496e81cda01601f4abb746890c3478d05a2ff6b9278c71f9b59e", 200),
    "D-04/dark": ("d-04-dark.svg", "e77d5607426ce7764d4f5fdf2c7d4fb1f2779beaaabfc1e1644460133e55b335", 200),
}
PLACEMENTS = [
    ("P-01/light", 72, 956, 376, 369.6658132676),
    ("D-04/light", 72, 1235, 220, 84.2212131892),
    ("D-04/dark", 72, 1235, 220, 84.2212131892),
    ("D-04/light", 438, 1238, 220, 84.2212131892),
    ("D-04/dark", 72, 1238, 220, 84.2212131892),
    ("D-04/light", 72, 1239, 220, 84.2212131892),
    ("P-01/dark", 72, 70, 360, 353.9353531285),
]
PHOTO_EXPECTED = {
    "01-cover": ["main-building.jpg"],
    "02-subject-rankings": ["chemistry-building.jpg"],
    "03-global-rankings": ["grand-auditorium.jpg"],
    "04-english-hsk": ["old-library.jpg"],
    "05-deadlines": ["quantum-information-center.jpg"],
    "06-tuition-scholarships": [],
    "07-cta": ["campus-sport.jpg"],
}


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def require(condition: bool, message: str) -> None:
    if not condition:
        raise ValueError(message)


def relative(path: Path) -> str:
    return path.relative_to(ROOT).as_posix()


def srgb_profile() -> bytes:
    path = ROOT / "assets/sRGB.icc"
    if path.is_file():
        return path.read_bytes()
    profile = ImageCms.ImageCmsProfile(ImageCms.createProfile("sRGB")).tobytes()
    path.write_bytes(profile)
    return profile


def embed_srgb(profile: bytes) -> None:
    candidates = list(ROOT.rglob("*.png"))
    for path in candidates:
        with Image.open(path) as image:
            require(image.mode in {"RGB", "RGBA"}, f"unexpected PNG mode: {relative(path)}")
            pixels = image.copy()
            pixels.save(path, format="PNG", optimize=True, icc_profile=profile)


def canonical_records() -> dict[str, dict]:
    path = REPO / "brands/asyada-egitim/assets/lockups/canonical-lockups.json"
    manifest = json.loads(path.read_text(encoding="utf-8"))
    return {item["canonical_lockup_id"]: item for item in manifest["records"]}


def validate_lockup_copies(canonical: dict[str, dict]) -> None:
    for key, (filename, expected_sha, minimum) in LOCKUPS.items():
        local = ROOT / "assets" / filename
        source = REPO / canonical[key]["canonical_file_path"]
        require(sha(local) == expected_sha, f"local lockup hash mismatch: {key}")
        require(sha(source) == expected_sha, f"canonical lockup hash mismatch: {key}")
        require(canonical[key]["sha256"] == expected_sha, f"canonical manifest mismatch: {key}")
        require(canonical[key]["minimum_supported_display_size"]["screen_width_px"] == minimum,
                f"canonical minimum mismatch: {key}")


def validate_png(path: Path, expected: tuple[int, int], profile: bytes) -> None:
    with Image.open(path) as image:
        require(image.size == expected, f"wrong PNG dimensions: {relative(path)} {image.size}")
        require(image.mode == "RGB", f"not RGB: {relative(path)}")
        require(image.info.get("icc_profile") == profile, f"missing/mismatched embedded sRGB profile: {relative(path)}")


def source_copy(svg: Path) -> tuple[list[str], ET.Element, ET.Element]:
    tree = ET.parse(svg).getroot()
    group = next((element for element in tree.iter() if element.get("id") == "editable-campaign-copy"), None)
    mark = next((element for element in tree.iter() if element.get("id") == "canonical-lockup"), None)
    require(group is not None and mark is not None, f"missing editable copy or lockup: {relative(svg)}")
    copy = json.loads(group.get("data-exact-copy-json", "[]"))
    text = [element.text or "" for element in group.iter() if element.tag.endswith("text")]
    require(text == copy, f"SVG visible text differs from exact copy list: {relative(svg)}")
    return copy, group, mark


def build_manifest(profile: bytes) -> dict:
    canonical = canonical_records()
    validate_lockup_copies(canonical)
    exact_copy = json.loads((ROOT / "exact-copy.json").read_text(encoding="utf-8"))
    render_report = json.loads((ROOT / "render-validation.json").read_text(encoding="utf-8"))
    require(list(exact_copy) == IDS, "exact-copy slide order mismatch")
    require(list(render_report) == IDS, "render report slide order mismatch")
    slides = []
    all_photos = set()
    for index, (slide_id, placement) in enumerate(zip(IDS, PLACEMENTS), 1):
        n = f"{index:02d}"
        final = ROOT / "png" / f"{n}.png"
        original = ROOT / "originals" / f"{n}.png"
        source = ROOT / "source" / f"{n}.svg"
        editable = ROOT / "source" / f"{n}.html"
        require(final.is_file() and original.is_file() and source.is_file() and editable.is_file(),
                f"missing slide deliverable: {n}")
        validate_png(final, (1080, 1350), profile)
        validate_png(original, (1080, 1350), profile)
        copy, _group, mark = source_copy(source)
        require(copy == exact_copy[slide_id], f"copy record mismatch: {slide_id}")
        require(source.read_text(encoding="utf-8") in editable.read_text(encoding="utf-8"),
                f"HTML does not contain its editable SVG: {slide_id}")
        lockup_id, x, y, width, height = placement
        filename, lockup_sha, minimum = LOCKUPS[lockup_id]
        require(mark.get("href") == f"../assets/{filename}", f"unexpected complete lockup: {slide_id}")
        values = [float(mark.get(k)) for k in ("x", "y", "width", "height")]
        require(values == [float(x), float(y), float(width), float(height)], f"lockup placement mismatch: {slide_id}")
        logo_tree = ET.parse(ROOT / "assets" / filename).getroot()
        vx, vy, vw, vh = map(float, logo_tree.get("viewBox").split())
        require(abs(width / height - vw / vh) < 1e-6, f"lockup aspect ratio changed: {slide_id}")
        require(width >= minimum and x >= 0 and y >= 0 and x + width <= 1080 and y + height <= 1350,
                f"lockup size/position invalid: {slide_id}")
        metrics = render_report[slide_id]
        require(metrics["jostLoaded"] is True and metrics["issues"] == [], f"render issue: {slide_id}")
        require(metrics["textOverflows"] == [], f"text overflow: {slide_id}")
        require(metrics.get("dateOverlaps") == [], f"date text overlaps: {slide_id}")
        photos = sorted({PurePosixPath(element.get("href", "")).name for element in ET.parse(source).getroot().iter()
                         if element.tag.endswith("image") and element.get("id") != "canonical-lockup"
                         and element.get("href", "").lower().endswith((".jpg", ".jpeg", ".png", ".webp"))})
        require(photos == PHOTO_EXPECTED[slide_id], f"photo assignment mismatch: {slide_id} {photos}")
        all_photos.update(photos)
        slides.append({
            "id": slide_id,
            "final_file": f"png/{n}.png",
            "final_sha256": sha(final),
            "original_file": f"originals/{n}.png",
            "original_sha256": sha(original),
            "source_file": f"source/{n}.svg",
            "source_sha256": sha(source),
            "editable_html_file": f"source/{n}.html",
            "dimensions": [1080, 1350],
            "copy": copy,
            "canonical_lockup_id": lockup_id,
            "canonical_lockup_sha256": lockup_sha,
            "canonical_lockup_file": f"assets/{filename}",
            "canonical_logo_sha256": SEAL_SHA,
            "canonical_seal_sha256": SEAL_SHA,
            "logo_x_y_px": [x, y],
            "logo_width_px": width,
            "logo_height_px": height,
            "minimum_supported_display_width_px": minimum,
            "photo_files": photos,
            "render_validation": metrics,
        })
    require(len(all_photos) >= 5, "fewer than five distinct campaign photos")
    photo_slides = [slide for slide in slides if slide["photo_files"]]
    require(len(photo_slides) >= 4, "photos appear on fewer than four slides")
    for path in (ROOT / "mobile-324").glob("*.png"):
        validate_png(path, (324, 405), profile)
    mobile_375 = [f"mobile-375/{i:02d}.png" for i in range(1, 8)]
    for rel in mobile_375:
        validate_png(ROOT / rel, (375, 469), profile)
    assets = {}
    for path in sorted((ROOT / "assets").rglob("*")):
        if path.is_file():
            assets[relative(path)] = {"sha256": sha(path), "bytes": path.stat().st_size}
    font_path = ROOT / "assets/Jost-VF.ttf"
    return {
        "title": "Tsinghua Üniversitesi — 2027 lisans başvuru carousel — V2",
        "status": "HUMAN CREATIVE REVIEW PENDING",
        "checked_on": "2026-10-10",
        "dimensions": [1080, 1350],
        "color_space": "sRGB (embedded ICC profile)",
        "brand": "asyada-egitim",
        "brand_system_note": "Approved identity metadata and exact lockups used; no full brand-system approval inferred.",
        "canonical_seal_sha256": SEAL_SHA,
        "font": {"file": "assets/Jost-VF.ttf", "sha256": sha(font_path), "license": "SIL Open Font License 1.1"},
        "canonical_lockups": {
            key: {"file": f"assets/{value[0]}", "sha256": value[1], "minimum_display_width_px": value[2]}
            for key, value in LOCKUPS.items()
        },
        "slides": slides,
        "exact_copy": exact_copy,
        "assets": assets,
        "photograph_count": len(all_photos),
        "photo_slide_count": len(photo_slides),
        "mobile_preview_files": mobile_375,
        "mobile_preview_324_files": [f"mobile-324/{i:02d}.png" for i in range(1, 8)],
        "contact_sheet_file": "contact-sheet.png",
        "mobile_324_contact_sheet_file": "mobile-324-contact-sheet.png",
        "source_vs_final_contact_sheet_file": "source-vs-final-contact-sheet.png",
        "revision_comparison_file": "revision-comparison.png",
        "feed_cover_preview_file": "feed-cover-preview.png",
        "caption_and_credits_file": "caption-and-credits.md",
        "factual_source_report_file": "factual-source-report.md",
        "quality_review_file": "quality-review.md",
        "package_file": "package/tsinghua-atlas-2027-v2.zip",
    }


def make_package(manifest: dict) -> Path:
    path = ROOT / manifest["package_file"]
    path.parent.mkdir(parents=True, exist_ok=True)
    members = sorted(
        p for p in ROOT.rglob("*")
        if p.is_file() and not p.is_relative_to(path.parent)
        and "__pycache__" not in p.parts and p.suffix != ".pyc"
    )
    with zipfile.ZipFile(path, "w", compression=zipfile.ZIP_DEFLATED, compresslevel=9) as archive:
        for item in members:
            archive.write(item, relative(item))
        for slide in manifest["slides"]:
            source = ROOT / slide["final_file"]
            archive.write(source, Path(slide["final_file"]).name)
    return path


def verify_package(path: Path, manifest: dict) -> None:
    with zipfile.ZipFile(path) as archive:
        names = archive.namelist()
        require(len(names) == len(set(names)), "duplicate archive member")
        require(archive.testzip() is None, "ZIP CRC error")
        for slide in manifest["slides"]:
            for filename in (slide["final_file"], Path(slide["final_file"]).name,
                             slide["original_file"], slide["source_file"], slide["editable_html_file"],
                             slide["canonical_lockup_file"]):
                require(filename in names, f"package missing {filename}")
        for required in ("manifest.json", "quality-review.md", "generation-notes.md", "caption-and-credits.md",
                         "factual-source-report.md", "contact-sheet.png", "mobile-324-contact-sheet.png", "revision-comparison.png",
                         "mobile-preview.html", "feed-cover-preview.html"):
            require(required in names, f"package missing {required}")
        require(archive.read("manifest.json") == (ROOT / "manifest.json").read_bytes(),
                "packaged manifest differs from source")
        for member in names:
            p = PurePosixPath(member)
            require(not p.is_absolute() and ".." not in p.parts and "\\" not in member,
                    f"unsafe archive path: {member}")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check-only", action="store_true", help="verify current outputs without rebuilding manifest/ZIP")
    args = parser.parse_args()
    try:
        require((ROOT / "assets/sRGB.icc").is_file() or not args.check_only,
                "sRGB profile asset missing; run without --check-only")
        profile = srgb_profile()
        if not args.check_only:
            embed_srgb(profile)
        manifest = build_manifest(profile)
        if args.check_only:
            saved = json.loads((ROOT / "manifest.json").read_text(encoding="utf-8"))
            require(saved == manifest, "manifest is stale; run without --check-only")
            package = ROOT / manifest["package_file"]
        else:
            (ROOT / "manifest.json").write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
            package = make_package(manifest)
        verify_package(package, manifest)
        print(json.dumps({
            "status": "PASS",
            "slides": len(manifest["slides"]),
            "distinct_photos": manifest["photograph_count"],
            "photo_slides": manifest["photo_slide_count"],
            "embedded_srgb": True,
            "package": str(package.relative_to(ROOT)),
            "package_sha256": sha(package),
        }, ensure_ascii=False, indent=2))
        return 0
    except (OSError, ValueError, KeyError, StopIteration, zipfile.BadZipFile, ET.ParseError) as exc:
        print(f"FAIL: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
