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
import re

MAX_BYTES = 25 * 1024 * 1024
MAX_FILES = 19_000
MAX_OUTPUT_BYTES = 1_400_000_000
ORIGIN = "https://cinegitim.github.io/design"

def design_catalog(paths):
    """Discover authored product sources and final media only, not comparison pages or build assets."""
    grouped, images, single = {}, {}, []
    def slug(value):
        return re.sub(r"^-+|-+$", "", re.sub(r"[^a-z0-9]+", "-", value.lower()))[:125]
    def label(value):
        return re.sub(r"[-_]+", " ", value).title()
    paths = sorted(set(paths))
    for p in paths:
        if not p.startswith("docs/") or any(x in ("..", "") or x.startswith(".") for x in p.split("/")):
            continue
        m = re.fullmatch(r"docs/(.+?)/(source|editable)/([^/]+\.html)", p, re.I)
        if m:
            project, name = m.group(1), m.group(3)
            if name.lower().endswith("-plate.html") or re.search(r"(?:^|/)(history|drafts|review|previews?)/", project,re.I):
                continue
            entry = grouped.setdefault(project, dict(
                id="carousel-01-v3" if project=="instagram/carousel-01-v3" else slug(project),
                title=label(project.split("/")[-1]),family=project.split("/")[0],kind="html",pages=[]))
            entry["pages"].append(p[5:])
            continue
        if re.fullmatch(r"docs/[^/]+/(rollup|poster|flyer|banner|banners)/[^/]+\.html",p,re.I) and not re.search(r"/(index|review)\.html$",p,re.I):
            single.append(p[5:])
    for p in paths:
        if not p.startswith("docs/") or not re.search(r"\.(png|jpe?g|webp|svg)$",p,re.I):
            continue
        m = re.fullmatch(r"docs/instagram/([^/]+)/(.+)",p,re.I)
        if m:
            project,tail = "instagram/"+m.group(1),m.group(2)
            if project in grouped:
                continue
            if re.fullmatch(r"(?:\d\d[-_][^/]+\.(png|jpe?g|webp|svg)|(?:export|png|final|renders|composited)/[^/]+\.(png|jpe?g|webp|svg))",tail,re.I):
                images.setdefault(project,[]).append(p[5:])
                continue
            if re.fullmatch(r"profile-photo/(?:[^/]+\.(png|svg)|variants/[^/]+\.(png|svg))",m.group(1)+"/"+tail,re.I):
                images.setdefault("instagram/profile-photo",[]).append(p[5:])
                continue
        covers=re.fullmatch(r"docs/social-covers/(assets|[a-z0-9-]+)/([^/]+\.(png|jpe?g|webp|svg))",p,re.I)
        if covers and (covers.group(1)!="assets" or re.match(r"(facebook|instagram|linkedin|x-profile|youtube)",covers.group(2),re.I)):
            images.setdefault("social-covers/cover-graphics",[]).append(p[5:])
    out = list(grouped.values())
    for p in single:
        out.append(dict(id=slug(re.sub(r"\.html$","",p,flags=re.I)),
            title=label(re.sub(r"\.html$","",p.split("/")[-1],flags=re.I)),
            family=p.split("/")[0],kind="html",pages=[p]))
    for folder,files in images.items():
        variants={}
        for p in files:
            stem=re.sub(r"\.(png|jpe?g|webp|svg)$","",p,flags=re.I)
            if stem not in variants or p.lower().endswith(".svg"):
                variants[stem]=p
        sorted_files=sorted(variants.values())
        for j in range(0,len(sorted_files),25):
            number=j//25+1
            out.append(dict(id="asset-"+slug(folder)+(f"-{number}" if j else ""),
                title=label(folder.split("/")[-1])+(f" · {number}" if j else "")+" (görsel)",
                family=folder.split("/")[0],kind="image",pages=sorted_files[j:j+25]))
    seen=set()
    clean=[]
    for x in out:
        x["pages"].sort()
        if x["id"] not in seen and x["pages"]:
            seen.add(x["id"]);clean.append(x)
    clean.sort(key=lambda x:(0 if x["kind"]=="html" else 1,x["family"],x["title"]))
    return clean

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
    if not dry_run and (source / "visual-editor/browser/catalog.json").is_file():
        live = design_catalog(["docs/"+p.relative_to(source).as_posix() for p in source.rglob("*") if p.is_file()])
        catalog = dest / "visual-editor/browser/catalog.json"
        before = catalog.stat().st_size
        catalog.write_text(json.dumps(live,ensure_ascii=False,separators=(",",":")),encoding="utf-8")
        size_total += catalog.stat().st_size-before
        if size_total>MAX_OUTPUT_BYTES: raise ValueError("Updated catalog exceeds free Pages size budget")
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
