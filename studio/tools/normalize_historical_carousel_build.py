#!/usr/bin/env python3
"""Normalize historic carousel render exports to byte-identical shared PNGs.

Dry-run unless --apply is supplied. Used by three legacy builders only after
all slide PNGs, crops, contact sheets, manifest, and source pages are rendered.
Stops before mutation if any expected input, image hash, or HTML link differs.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import posixpath
import shutil
import tempfile
from pathlib import Path

from audit_asset_dedup_pilot import (
    ADDITIONAL_CLUSTERS, EXPECTED_SHARED_BYTES, EXPECTED_SHARED_SHA256,
    HISTORICAL_SOURCE_PAGES, SHARED, TARGETS, digest,
)

VALID_SLUGS = ("carousel-01-v2", "carousel-01-v3", "carousel-02", "discovery-01")
FIRST_GROUP = {
    "name": "study-worlds",
    "shared": SHARED,
    "sha256": EXPECTED_SHARED_SHA256,
    "bytes": EXPECTED_SHARED_BYTES,
    "old": TARGETS,
    "pages": HISTORICAL_SOURCE_PAGES,
}
ALL_GROUPS = (FIRST_GROUP,) + ADDITIONAL_CLUSTERS


def normalize(root: Path, slug: str, *, groups=ALL_GROUPS, apply: bool = False) -> dict:
    if slug not in VALID_SLUGS:
        raise ValueError(f"Unsupported historical builder slug: {slug}")
    docs = root / "docs"
    prefix = f"instagram/{slug}/"
    copies = []
    source_edits = []
    shared_to_copy = {}
    for group in groups:
        olds = [old for old in group["old"] if old.startswith(prefix)]
        pages = [p for p in group["pages"] if p.startswith(prefix)]
        if not olds and not pages:
            continue
        dst = docs / group["shared"]
        if dst.exists() or dst.is_symlink():
            if not dst.is_file() or dst.is_symlink() or dst.stat().st_size != group["bytes"] or digest(dst) != group["sha256"]:
                raise ValueError(f"Unexpected bytes in shared original: {group['shared']}")
        else:
            dst = None
        verified = []
        for old in olds:
            src = docs / old
            if src.exists() or src.is_symlink():
                if not src.is_file() or src.is_symlink() or src.stat().st_size != group["bytes"] or digest(src) != group["sha256"]:
                    raise ValueError(f"Unexpected bytes in generated original: {old}")
                verified.append(src)
                copies.append(src)
        if dst is None:
            if not verified:
                raise ValueError(f"No valid original available for shared image: {group['shared']}")
            shared_to_copy[group["shared"]] = verified[0]
        for page in pages:
            html_file = docs / page
            if not html_file.is_file() or html_file.is_symlink():
                raise ValueError(f"Missing historical source HTML: {page}")
            value = html_file.read_text(encoding="utf-8")
            old_options = [
                "src=\"" + posixpath.relpath(old, posixpath.dirname(page)) + "\""
                for old in olds
            ]
            desired = "src=\"" + posixpath.relpath(group["shared"], posixpath.dirname(page)) + "\""
            found_old = sum(value.count(token) for token in old_options)
            found_new = value.count(desired)
            if found_old + found_new != 1:
                raise ValueError(f"Wrong image references in generated HTML: {page}")
            if found_old:
                before = next(token for token in old_options if token in value)
                source_edits.append((html_file, value.replace(before, desired)))
    # Preflight is complete before any file is changed.
    if apply:
        for dest, src in shared_to_copy.items():
            target = docs / dest
            target.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(src, target)  # byte-identical; preserve PNG ancillary chunks
        for path, value in source_edits:
            # Keep existing metadata and replace within the same filesystem.
            with tempfile.NamedTemporaryFile("w", dir=path.parent, prefix=".brandstudio-", suffix=".tmp",
                                             encoding="utf-8", delete=False) as fh:
                tmp = Path(fh.name)
                fh.write(value)
            try:
                os.chmod(tmp, path.stat().st_mode & 0o777)
                os.replace(tmp, path)
            finally:
                if tmp.exists():
                    tmp.unlink()
        for path in copies:
            path.unlink()
    return {
        "status": "APPLIED" if apply else "DRY_RUN",
        "slug": slug,
        "original_paths_to_unpublish": len(copies),
        "html_pages_to_update": len(source_edits),
        "shared_images_to_create": len(shared_to_copy),
        "changed_anything": apply and bool(copies or source_edits or shared_to_copy),
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=Path(__file__).resolve().parents[2])
    parser.add_argument("--slug", choices=VALID_SLUGS, required=True)
    parser.add_argument("--apply", action="store_true")
    args = parser.parse_args()
    try:
        report = normalize(args.root.resolve(), args.slug, apply=args.apply)
    except (ValueError, OSError) as exc:
        parser.exit(2, f"Historical image normalization STOP: {exc}\n")
    print(json.dumps(report, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
