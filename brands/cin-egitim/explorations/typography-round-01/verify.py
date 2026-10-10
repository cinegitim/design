#!/usr/bin/env python3
"""Stdlib-only check: typography boards keep the locked logo and are distinct."""
from pathlib import Path
import hashlib
import json
import re

ROOT = Path(__file__).resolve().parents[4]
SOURCE = Path(__file__).resolve().parent
DOCS = ROOT / "docs/cin-egitim/typography-round-01"
EXPECTED = "1cc1808947d8f7f759ebb9956a715d535bb4fcc985d3f85194d4eaf1a85c7381"


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    metadata = json.loads((ROOT / "brands/cin-egitim/brand.json").read_text())
    manifest = json.loads((SOURCE / "manifest.json").read_text())
    logo = ROOT / metadata["canonicalLogo"]["path"]
    assert metadata["canonicalLogo"]["locked"] is True
    assert sha(logo) == EXPECTED == metadata["canonicalLogo"]["sha256"]
    assert manifest["canonical_logo_sha256"] == EXPECTED
    assert sha(ROOT / "docs/cin-egitim/assets/symbol.svg") == EXPECTED
    assert manifest["status"].startswith("EXPLORATION")
    assert len(manifest["directions"]) == 3
    classes = set()
    for item in manifest["directions"]:
        name = item["slug"] + ".html"
        src, web = SOURCE / name, DOCS / name
        assert src.is_file() and web.is_file()
        assert sha(src) == manifest["source_outputs"][name]
        assert sha(web) == manifest["docs_outputs"][name]
        html = src.read_text()
        assert "../../assets/symbol.svg" in html
        assert "image model" not in html.lower()
        assert item["arrangement"] not in classes
        classes.add(item["arrangement"])
        assert "Çin" in html or "ÇİN" in html
        assert "<script" not in html.lower()
    for name, digest in manifest["source_outputs"].items():
        assert sha(SOURCE / name) == digest and sha(DOCS / name) == manifest["docs_outputs"][name]
    assert (DOCS / "index.html").is_file()
    print(json.dumps({"status": "PASS", "directions": sorted(classes),
                      "canonical_logo_sha256": EXPECTED,
                      "note": "Structural/source hash verification only; human A/B/C and aesthetic approval pending."}, indent=2))


if __name__ == "__main__":
    main()
