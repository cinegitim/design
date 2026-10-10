#!/usr/bin/env python3
"""Stdlib-only review-bundle checks. No render, producer import or approval."""
from pathlib import Path
import hashlib
import json
import re
import struct
import xml.etree.ElementTree as ET
import zipfile

ROOT = Path(__file__).resolve().parents[4]
BUNDLE = Path(__file__).resolve().parent
PUBLIC = ROOT / "docs/cin-egitim/svg-round-01"
NS = "{http://www.w3.org/2000/svg}"


def need(condition, message):
    if not condition:
        raise ValueError(message)


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def bundle_file(name):
    path = (BUNDLE / name).resolve()
    need(path.is_relative_to(BUNDLE.resolve()) and path.is_file(), "Missing/unsafe file")
    return path


def svg_check(path, record):
    root = ET.parse(path).getroot()
    need(root.tag == NS + "svg", "SVG root required")
    need(root.get("viewBox") == record["viewBox"] == "0 0 916 924", "SVG bounds")
    need(root.get("width") == "916" and root.get("height") == "924", "SVG dimensions")
    allowed = {NS + tag for tag in ("svg", "g", "path", "title", "desc")}
    groups = {e.get("id"): e for e in root.iter(NS + "g")}
    for expected in ("brush-ring", "pagoda-and-ink-ground"):
        need(expected in groups, "Missing symbol group")
        need(groups[expected].get("fill-rule") == "evenodd", "Preserve holes")
    paths = list(root.iter(NS + "path"))
    need(len(paths) == record["paths"] and len(paths) >= 2, "Missing vector paths")
    for e in root.iter():
        need(e.tag in allowed, "Only vector paths/groups and accessibility metadata permitted")
        for key, value in e.attrib.items():
            need(not key.lower().startswith("on") and "href" not in key.lower(), "Active/external content")
            need("url(" not in value and "data:" not in value, "Embedded/external dependency")
        if e.tag == NS + "path":
            d = e.get("d", "")
            need(bool(d) and re.fullmatch(r"[MmZzLlHhVvCcSsQqTtAaEe0-9+.,\s-]+", d), "Invalid path data")
            need("c" in d.lower(), "Cubic Bezier contours expected")
    return len(paths)


def main():
    m = json.loads(bundle_file("manifest.json").read_text())
    need(m["brand"] == "cin-egitim" and m["canonical"] is False, "Review status/brand")
    need(m["embedded_raster"] is False and m["typography"] is False, "Symbol-only scope")
    for path, key in [
        ("brands/cin-egitim/enhancements/target-symbol-super-resolution-4x.png", "source_sha256"),
        ("brands/cin-egitim/reference/target-symbol.png", "locked_target_sha256"),
        ("brands/cin-egitim/reference/target-lock.json", "reference_lock_sha256"),
    ]:
        need(digest(ROOT / path) == m[key], "Changed source/reference")
    count = 0
    for name, record in m["files"].items():
        path = bundle_file(name)
        need(digest(path) == record["sha256"], "Stale hash: " + name)
        need((PUBLIC / name).read_bytes() == path.read_bytes(), "Public mirror: " + name)
        if path.suffix == ".svg":
            count += svg_check(path, record)
        elif path.suffix == ".png":
            data = path.read_bytes()
            need(data[:8] == b"\x89PNG\r\n\x1a\n", "Invalid PNG")
            need(list(struct.unpack(">II", data[16:24])) == record["dimensions"], "PNG dimensions")
    need((PUBLIC / "manifest.json").read_bytes() == bundle_file("manifest.json").read_bytes(), "Manifest mirror")
    if (PUBLIC / "svg-round-01.zip").is_file():
        with zipfile.ZipFile(PUBLIC / "svg-round-01.zip") as z:
            need(len(z.namelist()) == len(set(z.namelist())), "Duplicate ZIP entries")
            need(z.testzip() is None, "ZIP CRC failure")
            delivery = json.loads(bundle_file("delivery.json").read_text())
            need(digest(PUBLIC / "svg-round-01.zip") == delivery["sha256"], "ZIP hash")
            need((PUBLIC / "delivery.json").read_bytes() == bundle_file("delivery.json").read_bytes(), "Delivery mirror")
            need(sorted(z.namelist()) == sorted(delivery["members"]), "Unexpected ZIP members")
            for name in list(m["files"]) + ["manifest.json", "build.py", "verify.py", "package.py", "README.md", "quality-review.md", "handoff.md", "index.html"]:
                need(z.read(name) == bundle_file(name).read_bytes(), "ZIP member: " + name)
                need((PUBLIC / name).read_bytes() == bundle_file(name).read_bytes(), "Public recipe mirror: " + name)
    print(json.dumps({"status": "PASS", "brand": "cin-egitim", "vector_paths": count,
                      "checks": "source/reference hashes, path-only SVG/no bitmap/no text, dimensions, mirrors, ZIP",
                      "limits": "Local file validation only; not visual approval or SVG-format production CI coverage"}, indent=2))


if __name__ == "__main__":
    main()
