#!/usr/bin/env python3
"""Verify the 12 exploration pages, output hashes and unchanged canonical symbol."""
from pathlib import Path
import hashlib
import json

ROOT = Path(__file__).resolve().parents[4]
SOURCE = Path(__file__).resolve().parent
DOCS = ROOT / "docs/cin-egitim/typography-round-01"
EXPECTED_LOGO = "1cc1808947d8f7f759ebb9956a715d535bb4fcc985d3f85194d4eaf1a85c7381"
EXPECTED_IDS = list("ABCDEFGHIJKL")


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    metadata = json.loads((ROOT / "brands/cin-egitim/brand.json").read_text())
    manifest = json.loads((SOURCE / "manifest.json").read_text())
    directions = manifest["directions"]
    logo = ROOT / metadata["canonicalLogo"]["path"]

    assert metadata["canonicalLogo"]["locked"] is True
    assert sha(logo) == EXPECTED_LOGO == metadata["canonicalLogo"]["sha256"]
    assert manifest["canonical_logo_sha256"] == EXPECTED_LOGO
    assert sha(ROOT / "docs/cin-egitim/assets/symbol.svg") == EXPECTED_LOGO
    assert len(directions) == 12 and [d["id"] for d in directions] == EXPECTED_IDS
    assert len({d["font_display"] for d in directions}) == 12
    assert manifest["status"].startswith("EXPLORATION")

    for direction in directions:
        name = direction["slug"] + ".html"
        src, web = SOURCE / name, DOCS / name
        assert src.is_file() and web.is_file()
        assert sha(src) == manifest["source_outputs"][name]
        assert sha(web) == manifest["docs_outputs"][name]
        source_html, web_html = src.read_text(), web.read_text()
        assert "../../assets/symbol.svg" in source_html
        assert "../assets/symbol.svg" in web_html
        assert "Kilitli Çin Eğitim sembolü" in source_html
        assert direction["name"] in source_html
        assert "<script" not in source_html.lower()

    for name, digest in manifest["source_outputs"].items():
        assert sha(SOURCE / name) == digest
        assert sha(DOCS / name) == manifest["docs_outputs"][name]
    for name, digest in manifest["published_support_files"].items():
        assert sha(DOCS / name) == digest

    index = (DOCS / "index.html").read_text()
    assert index.count('class="option"') == 12
    assert all(f'href="{d["slug"]}.html"' in index for d in directions)
    print(json.dumps({"status": "PASS", "directions": len(directions),
                      "unique_font_families": len({d['font_display'] for d in directions}),
                      "canonical_logo_sha256": EXPECTED_LOGO,
                      "note": "Structural/hash verification only; no wordmark or aesthetic approval."},
                     ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
