#!/usr/bin/env python3
"""Export byte-preserving public Pages assets for Cloudflare.

Oversized ZIPs cannot be uploaded to Cloudflare Pages; retain explicit 302
redirects to GitHub Pages until they are migrated to R2 with checked hashes.
"""
from __future__ import annotations
import argparse
import hashlib
import json
from pathlib import Path
import shutil

MAX_BYTES = 25 * 1024 * 1024
MAX_FILES = 19_000
MAX_OUTPUT_BYTES = 1_400_000_000
ORIGIN = "https://cinegitim.github.io/design"

def build(source: Path, dest: Path, dry_run=False):
    source, dest = source.resolve(), dest.resolve()
    if not source.is_dir() or not (source / "index.html").is_file():
        raise ValueError("Source must be public docs directory")
    if source == dest or source in dest.parents:
        raise ValueError("Destination cannot be within source")
    if dest.exists() and any(dest.iterdir()):
        raise ValueError("Destination must be empty")
    kept, omitted, size_total = 0, [], 0
    for p in sorted(source.rglob("*")):
        if not p.is_file(): continue
        if p.is_symlink(): raise ValueError(f"Symlink: {p}")
        rel = p.relative_to(source).as_posix()
        if any(x.startswith(".") for x in rel.split("/")): continue
        size = p.stat().st_size
        if size > MAX_BYTES:
            if not rel.lower().endswith(".zip"):
                raise ValueError(f"Oversized non-ZIP asset: {rel}")
            omitted.append(dict(path=rel, bytes=size, fallback=f"{ORIGIN}/{rel}"))
            continue
        kept += 1
        size_total += size
        if kept + 1 > MAX_FILES:
            raise ValueError('Free-only Pages file count quota exceeded')
        if size_total > MAX_OUTPUT_BYTES:
            raise ValueError('Free-only Pages total output byte budget exceeded')
        if not dry_run:
            out = dest / rel
            out.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(p, out)
            if hashlib.sha256(out.read_bytes()).digest() != hashlib.sha256(p.read_bytes()).digest():
                raise RuntimeError(f"Copy mismatch: {rel}")
    if not dry_run:
        redirects = dest / "_redirects"
        if redirects.exists(): raise ValueError("Existing _redirects requires manual merge")
        redirects.write_text(
            "\n".join(f"/{x['path']} {x['fallback']} 302" for x in omitted) + "\n",
            encoding="utf-8")
    return dict(
        schema_version=1, source=ORIGIN, files_on_cloudflare=kept,
        bytes_on_cloudflare=size_total, external_archives=omitted,
        fully_independent=len(omitted) == 0, dry_run=dry_run)

def main():
    root = Path(__file__).resolve().parents[2]
    p = argparse.ArgumentParser()
    p.add_argument("--source", type=Path, default=root / "docs")
    p.add_argument("--dest", type=Path, default=Path(__file__).resolve().parent / "dist")
    p.add_argument("--dry-run", action="store_true")
    args = p.parse_args()
    print(json.dumps(build(args.source,args.dest,args.dry_run),indent=2,ensure_ascii=False))

if __name__ == "__main__": main()
