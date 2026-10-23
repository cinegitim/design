#!/usr/bin/env python3
"""Optional post-production bridge to the user's local Visual Editor companion.

The prompt renderer remains authoritative. No network calls, remote writes,
publishing, or uploads are performed by this script.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
from pathlib import Path
import re
import subprocess
import sys

SLUG = re.compile(r"^[a-z0-9]+(?:-[a-z0-9]+)*$")
MANIFEST = "brands/asyada-egitim/assets/lockups/canonical-lockups.json"


class BridgeError(ValueError):
    pass


def slug(value: str) -> str:
    if not isinstance(value, str) or not SLUG.fullmatch(value):
        raise BridgeError(f"Invalid slug: {value!r}")
    return value


def approved_logo(repo: Path, brand: str, logo_id: str) -> tuple[Path, str]:
    if brand != "asyada-egitim":
        raise BridgeError("Only asyada-egitim has a verified adapter in v1")
    entries = json.loads((repo / MANIFEST).read_text(encoding="utf-8"))["records"]
    record = next((x for x in entries if (x.get("id") or x.get("canonical_lockup_id")) == logo_id), None)
    if record is None:
        raise BridgeError(f"Unknown canonical lockup: {logo_id}")
    path = (repo / record["path"]).resolve()
    if not path.is_relative_to(repo.resolve()) or not path.is_file():
        raise BridgeError("Canonical lockup missing")
    expected = record.get("hash") or record.get("sha256")
    if not re.fullmatch(r"[a-f0-9]{64}", expected or ""):
        raise BridgeError("Invalid canonical lockup hash")
    actual = hashlib.sha256(path.read_bytes()).hexdigest()
    if actual != expected:
        raise BridgeError("Canonical SVG SHA-256 mismatch")
    return path, expected


def validate_output(output: Path) -> None:
    if not output.is_dir():
        raise BridgeError("Prompt output folder missing")
    source = output / "source"
    if not (source / "style.css").is_file():
        raise BridgeError("Source CSS missing")
    pages = sorted(p for p in source.glob("*.html") if p.stem.isdecimal())
    if not pages:
        raise BridgeError("No editable numbered source HTML files")
    if not (output / "slides").is_dir() or not any((output / "slides").glob("*.png")):
        raise BridgeError("Missing actual rendered PNGs; registration is post-production only")
    if len(pages) > 25:
        raise BridgeError("Too many slides")
    for p in pages:
        if p.is_symlink() or p.stat().st_size > 2_000_000:
            raise BridgeError("Unsupported or unsafe source HTML")


def run(
    *, repo: Path, editor_home: Path, output: Path, product: str,
    brand: str, category: str, style: str, logo_id: str,
    dry_run: bool = False,
) -> dict:
    brand, product, category, style = map(slug, (brand, product, category, style))
    repo = repo.resolve()
    editor_home = editor_home.resolve()
    output = output.resolve()
    validate_output(output)
    logo_path, sha = approved_logo(repo, brand, logo_id)
    if logo_id != "P-01/light":
        raise BridgeError("Local MVP currently renders only P-01/light; other canonical variants are not interchangeable")
    if not (editor_home / "app" / "manage.py").is_file():
        raise BridgeError("Install the local editor MVP first; no runtime is bundled into public Pages")
    destination = editor_home / "products" / category / product
    if destination.exists():
        raise BridgeError("Product already registered; registration cannot overwrite a source")
    command = [
        sys.executable, "-m", "app.manage", "register-output",
        "--output", str(output), "--category", category, "--product", product,
        "--brand", brand, "--style", style,
        "--logo-file", str(logo_path), "--logo-sha256", sha,
    ]
    result = {
        "product": product, "category": category, "brand": brand,
        "style_id": style, "logo_id": logo_id, "logo_sha256": sha,
        "destination": str(destination), "source_output": str(output),
        "visual_editor": f"http://127.0.0.1:8765/editor/{category}/{product}/",
        "dry_run": dry_run,
    }
    if dry_run:
        return result
    completed = subprocess.run(command, cwd=editor_home, check=False, text=True, capture_output=True, timeout=90)
    if completed.returncode:
        raise BridgeError(f"Local companion registration failed: {completed.stderr[-900:]}")
    if not (destination / "product.json").is_file() or not (destination / "versions" / "v1" / "state.json").is_file():
        raise BridgeError("Companion returned without verified v1 product files")
    result["registered"] = True
    return result


def main() -> int:
    ap = argparse.ArgumentParser(description="Register verified prompt outputs in the optional local Visual Editor")
    ap.add_argument("--repo", type=Path, default=Path(__file__).resolve().parents[2])
    ap.add_argument("--editor-home", type=Path, required=True)
    ap.add_argument("--output", type=Path, required=True)
    ap.add_argument("--product", required=True)
    ap.add_argument("--category", default="instagram-carousel")
    ap.add_argument("--brand", default="asyada-egitim")
    ap.add_argument("--style", default="editorial-campaign")
    ap.add_argument("--logo-id", default="P-01/light")
    ap.add_argument("--dry-run", action="store_true")
    args = ap.parse_args()
    try:
        result = run(**vars(args))
        print(json.dumps(result, ensure_ascii=False, indent=2))
        return 0
    except (BridgeError, OSError, json.JSONDecodeError, subprocess.TimeoutExpired) as exc:
        print(f"Visual Editor bridge: {exc}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
