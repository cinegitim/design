#!/usr/bin/env python3
"""Verify Asya'da Eğitim approved canonical lockup integrity.

This is a production gate. Any failure means stop publishing and restore from
git or the approved canonical manifest. This verifier does not approve new art.
"""
from pathlib import Path
import hashlib
import json
import subprocess
import tempfile
import xml.etree.ElementTree as ET

from PIL import Image

ROOT = Path(__file__).resolve().parents[2]
MANIFEST = ROOT / "brands/asyada-egitim/assets/lockups/canonical-lockups.json"
SEAL = ROOT / "brands/asyada-egitim/assets/v01-canonical.svg"
RESULT = ROOT / "brands/asyada-egitim/assets/lockups/verification-result.json"
NS = "http://www.w3.org/2000/svg"
SEAL_SHA = "8f5d46f0302c4cc7e3765d3bfce9445f842dbd92f1e0f8fbe99f9f509c77e11a"
FULL_GLYPHS = "ASYA’DAEĞİTİMEDUCATIONINASIA"
TURKISH_GLYPHS = "ASYA’DAEĞİTİM"

def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()

def fail(msg: str):
    raise SystemExit(f"CANONICAL LOCKUP VERIFICATION FAILED: {msg}")

def render_ok(path: Path, min_width: int) -> dict:
    with tempfile.TemporaryDirectory(prefix="asyada-lockup-verify-", dir=Path.home()/".cache/brand-studio") as td:
        out = Path(td) / "render.png"
        subprocess.run(["rsvg-convert", "-w", str(min_width), str(path), "-o", str(out)], check=True, capture_output=True)
        im = Image.open(out).convert("RGBA")
        alpha = im.getchannel("A")
        bbox = alpha.getbbox()
        if not bbox:
            fail(f"{path}: renders empty")
        x0, y0, x1, y1 = bbox
        if x0 <= 0 or y0 <= 0 or x1 >= im.width or y1 >= im.height:
            fail(f"{path}: rendered ink touches canvas edge / clipping risk {bbox} in {im.size}")
        return {"render_width_px": im.width, "render_height_px": im.height, "alpha_bbox": [x0, y0, x1, y1]}

def root_paths(root: ET.Element):
    return list(root.iter(f"{{{NS}}}path"))

def main() -> None:
    if sha(SEAL) != SEAL_SHA:
        fail("canonical seal SHA-256 changed")
    manifest = json.loads(MANIFEST.read_text())
    if manifest.get("status") != "APPROVED / CANONICAL":
        fail("manifest status is not APPROVED / CANONICAL")
    if manifest.get("canonical_seal_sha256") != SEAL_SHA:
        fail("manifest seal SHA mismatch")
    records = manifest.get("records", [])
    expected_ids = {f"{v}/{c}" for v in ["P-01", "H-02", "C-03", "D-04", "F-05"] for c in ["light", "dark", "monochrome"]}
    seen = {r.get("canonical_lockup_id") for r in records}
    if seen != expected_ids or len(records) != 15:
        fail(f"approved combination set mismatch: {sorted(seen)}")
    checked = []
    for rec in records:
        path = ROOT / rec["canonical_file_path"]
        if not str(path).startswith(str(ROOT / "brands/asyada-egitim/assets/lockups")):
            fail(f"{path}: canonical asset outside approved lockup directory")
        if sha(path) != rec["sha256"]:
            fail(f"{path}: SHA mismatch")
        if any(part in path.as_posix() for part in ["explorations", "wordmark-ref", "final-lockups", "typography-weights"]):
            fail(f"{path}: experimental/review asset used as production canonical")
        root = ET.fromstring(path.read_bytes())
        if list(root.iter(f"{{{NS}}}text")):
            fail(f"{path}: contains SVG <text>")
        if list(root.iter(f"{{{NS}}}image")):
            fail(f"{path}: contains SVG <image>")
        glyphs = "".join(p.get("data-glyph", "") for p in root_paths(root) if p.get("data-glyph"))
        expected = TURKISH_GLYPHS if rec["variant_id"] == "D-04" else FULL_GLYPHS
        if glyphs != expected:
            fail(f"{path}: glyph/diacritic sequence mismatch: {glyphs!r}")
        if rec["variant_id"] == "D-04" and "EDUCATION" in glyphs:
            fail(f"{path}: D-04 incorrectly contains English")
        # Seal must be embedded as a nested original 400:370 SVG with the manifest SHA.
        nested = [e for e in root.iter(f"{{{NS}}}svg") if e.get("data-canonical-logo-sha256")]
        if len(nested) != 1 or nested[0].get("data-canonical-logo-sha256") != SEAL_SHA:
            fail(f"{path}: missing embedded canonical seal marker")
        if nested[0].get("viewBox") != "0 0 400 370":
            fail(f"{path}: embedded seal viewBox changed")
        if abs(float(nested[0].get("width")) / float(nested[0].get("height")) - 400/370) > 1e-9:
            fail(f"{path}: embedded seal aspect changed")
        min_width = rec["minimum_supported_display_size"]["screen_width_px"]
        render = render_ok(path, min_width)
        checked.append({"canonical_lockup_id": rec["canonical_lockup_id"], "path": rec["canonical_file_path"], "sha256": rec["sha256"], **render})
    production_dirs = [ROOT/"brands/asyada-egitim/applications", ROOT/"docs/asyada-seal/canonical-lockups"]
    bad_refs = []
    # Manifest/verification JSON legitimately records historical provenance strings;
    # only artwork-bearing production files (HTML/SVG) can pull experimental art.
    skip_names = {"canonical-lockups.json", "verification-result.json"}
    for base in production_dirs:
        if not base.exists():
            continue
        for f in base.rglob("*"):
            if f.is_file() and f.suffix.lower() in {".html", ".svg"} and f.name not in skip_names:
                txt = f.read_text(errors="ignore")
                for bad in ["wordmark-ref/lockups", "wordmark-ref/alignment", "vector-review/assets/W", "smooth/", "typography-weights/assets/tr", "final-lockups/assets/"]:
                    if bad in txt:
                        bad_refs.append(f"{f.relative_to(ROOT)} -> {bad}")
    if bad_refs:
        fail("experimental assets referenced in production: " + "; ".join(bad_refs))
    result = {
        "status": "PASS",
        "canonical_status": "APPROVED / CANONICAL",
        "checked_records": len(checked),
        "canonical_seal_sha256": SEAL_SHA,
        "manifest_sha256": sha(MANIFEST),
        "minimum_size_and_contrast_caveats_recorded": True,
        "experimental_assets_in_production": False,
        "records": checked,
    }
    RESULT.write_text(json.dumps(result, indent=2, ensure_ascii=False) + "\n")
    print(json.dumps({k: v for k, v in result.items() if k != "records"}, indent=2, ensure_ascii=False))

if __name__ == "__main__":
    main()
