#!/usr/bin/env python3
"""Read-only pilot: verify exact image duplication and references in Pages sources.

No network requests, build/render operations, deletion, or file mutations.
Run (migrated tree): python3 studio/tools/audit_asset_dedup_pilot.py --mode after --root . --json
Run (historical baseline): python3 studio/tools/audit_asset_dedup_pilot.py --mode before --root . --json
"""
from __future__ import annotations

import argparse
import hashlib
import html
import json
import posixpath
import re
from pathlib import Path
from urllib.parse import unquote, urlsplit

TARGETS = (
    "instagram/carousel-01-v2/assets/photo-3.png",
    "instagram/carousel-01-v3/assets/photo-3.png",
    "instagram/carousel-02/assets/photo-3.png",
    "instagram/discovery-01/assets/study-worlds.png",
)
TEXT_EXTENSIONS = {".html", ".htm", ".css", ".js", ".mjs", ".json", ".md", ".py", ".txt"}
HTML_ATTRIBUTE = re.compile(r"""(?:src|href)\s*=\s*["']([^"']+)["']""", re.IGNORECASE)
CSS_URL = re.compile(r"""url\(\s*["']?([^"')\s]+)""", re.IGNORECASE)
MAX_TEXT_BYTES = 2_000_000


def digest(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as src:
        for chunk in iter(lambda: src.read(128 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def resolve_site_url(source: str, value: str) -> str | None:
    """Resolve a reference within /design/ without following symlinks/redirects."""
    value = html.unescape(value.strip())
    if not value or value.startswith(("#", "data:", "javascript:", "mailto:")):
        return None
    url = urlsplit(value)
    if url.scheme or url.netloc:
        return None
    path = unquote(url.path)
    if not path:
        return None
    if path.startswith("/"):
        if not path.startswith("/design/"):
            return None
        return posixpath.normpath(path[len("/design/"):])
    return posixpath.normpath(posixpath.join(posixpath.dirname(source), path))


def inspect(root: Path, targets: tuple[str, ...] = TARGETS) -> dict:
    docs = root / "docs"
    if not docs.is_dir():
        raise ValueError("docs directory is missing")
    records = []
    for rel in targets:
        candidate = docs / rel
        if not candidate.is_file() or candidate.is_symlink():
            raise ValueError(f"Missing or symlinked original file: {rel}")
        records.append({"path": rel, "bytes": candidate.stat().st_size, "sha256": digest(candidate)})

    if len({r["sha256"] for r in records}) != 1 or len({r["bytes"] for r in records}) != 1:
        raise ValueError("Pilot images are no longer byte-identical; stop migration")

    chosen = set(targets)
    exact_references = []
    ambiguous_mentions = []
    scanned = 0
    for source in docs.rglob("*"):
        if not source.is_file() or source.suffix.lower() not in TEXT_EXTENSIONS:
            continue
        if source.stat().st_size > MAX_TEXT_BYTES:
            continue
        rel = source.relative_to(docs).as_posix()
        content = source.read_text(encoding="utf-8", errors="replace")
        scanned += 1
        refs = HTML_ATTRIBUTE.findall(content) + CSS_URL.findall(content)
        for url in refs:
            target = resolve_site_url(rel, url)
            if target in chosen:
                exact_references.append({"source": rel, "target": target, "reference": url})
        # A filename mention is NOT necessarily a URL dependency; report separately.
        basenames = sorted({posixpath.basename(t) for t in targets if posixpath.basename(t) in content})
        if basenames and not any(ref["source"] == rel for ref in exact_references):
            ambiguous_mentions.append({"source": rel, "filenames": basenames})

    size = records[0]["bytes"]
    return {
        "status": "READ_ONLY",
        "files": records,
        "bytes_current": size * len(records),
        "bytes_one_copy": size,
        "theoretical_bytes_saved_if_three_urls_removed": size * (len(records) - 1),
        "text_files_scanned": scanned,
        "exact_site_references": sorted(exact_references, key=lambda r: (r["target"], r["source"])),
        "ambiguous_text_mentions": sorted(ambiguous_mentions, key=lambda r: r["source"]),
        "may_delete_original_paths": False,
        "reason": (
            "GitHub Pages static hosting cannot retain byte-identical responses "
            "at all existing PNG URLs if the corresponding published files are deleted. "
            "Rewriting HTML alone yields zero Pages-size reduction."
        ),
    }



# Exact, pre-existing Git blob reused without PNG re-encoding (caBX preserved).
SHARED = "instagram/_shared/assets/study-worlds-22dde98f.png"
EXPECTED_SHARED_SHA256 = "c9e22040515021cfa5014b51426cf63ba3ded488370ae347edba77632c4e63ed"
EXPECTED_SHARED_BYTES = 3281287
HISTORICAL_SOURCE_PAGES = (
    "instagram/carousel-01-v2/source/03.html",
    "instagram/carousel-01-v3/source/03.html",
    "instagram/carousel-02/source/03.html",
    "instagram/discovery-01/source/02.html",
)


def verify_migrated(root: Path, *, expected_sha256: str = EXPECTED_SHARED_SHA256,
                    expected_bytes: int = EXPECTED_SHARED_BYTES) -> dict:
    """Read-only, fail-closed check for the finished 4-path -> 1-path migration."""
    docs = root / "docs"
    shared = docs / SHARED
    if not shared.is_file() or shared.is_symlink():
        raise ValueError(f"Shared source missing or symlinked: {SHARED}")
    if shared.stat().st_size != expected_bytes or digest(shared) != expected_sha256:
        raise ValueError("Shared image byte count or SHA256 differs from unchanged source")

    for old in TARGETS:
        if (docs / old).exists() or (docs / old).is_symlink():
            raise ValueError(f"Original duplicate still published: {old}")

    required = set(HISTORICAL_SOURCE_PAGES)
    confirmed = []
    scanned = 0
    for source in docs.rglob("*"):
        if not source.is_file() or source.is_symlink() or source.suffix.lower() not in TEXT_EXTENSIONS:
            continue
        if source.stat().st_size > MAX_TEXT_BYTES:
            continue
        rel = source.relative_to(docs).as_posix()
        content = source.read_text(encoding="utf-8", errors="replace")
        scanned += 1
        refs = HTML_ATTRIBUTE.findall(content) + CSS_URL.findall(content)
        for value in refs:
            target = resolve_site_url(rel, value)
            if target in TARGETS:
                raise ValueError(f"Stale HTML/CSS image reference: {rel} -> {target}")
            if target == SHARED and rel in required:
                confirmed.append({"page": rel, "reference": value, "target": SHARED})

    counts = {page: sum(x["page"] == page for x in confirmed) for page in required}
    if any(n != 1 for n in counts.values()):
        raise ValueError(f"Expected one shared image reference in every source page: {counts}")

    return {
        "status": "PASS_AFTER_MIGRATION",
        "shared_path": SHARED,
        "shared_sha256": expected_sha256,
        "source_file_bytes": expected_bytes,
        "removed_duplicate_paths": list(TARGETS),
        "net_published_bytes_saved": (len(TARGETS) - 1) * expected_bytes,
        "source_pages": sorted(confirmed, key=lambda x: x["page"]),
        "text_files_scanned": scanned,
        "old_image_deep_links_intentionally_retired": True,
        "modifies_files": False,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=Path(__file__).resolve().parents[2])
    parser.add_argument("--json", action="store_true", help="Emit machine-readable findings")
    parser.add_argument("--mode", choices=("before", "after"), default="after", help="Verify baseline before or migration after")
    args = parser.parse_args()
    try:
        result = inspect(args.root.resolve()) if args.mode == "before" else verify_migrated(args.root.resolve())
    except (ValueError, OSError) as exc:
        parser.exit(2, f"Asset pilot STOP: {exc}\n")
    if args.json:
        print(json.dumps(result, indent=2, ensure_ascii=False))
    else:
        if args.mode == "before":
            print(f"PASS: {len(result['files'])} identical files")
            print(f"Theoretical reduction: {result['theoretical_bytes_saved_if_three_urls_removed']:,} bytes")
        else:
            print(f"PASS: {len(result['source_pages'])} migrated layout references")
            print(f"Published asset reduction: {result['net_published_bytes_saved']:,} bytes")
        print("Read-only verification; no files modified.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
