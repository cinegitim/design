#!/usr/bin/env python3
"""Read-only, stdlib-only, delta-scoped validation for Brandstudio finalization PRs.

The GitHub job invokes this checker from the trusted base commit, not from the
incoming PR. No APIs, LLMs, package installs, uploads, or continuous polling.
A single Chrome cover smoke render is optional; it is NOT an aesthetic approval.
"""
from __future__ import annotations

import argparse
import json
import re
import shutil
import struct
import subprocess
import sys
import tempfile
import time
from pathlib import Path, PurePosixPath

PREFIX = "studio/production/finalized/"
SLUG = re.compile(r"^[a-z0-9]+(?:-[a-z0-9]+)*$")
HEX40 = re.compile(r"^[a-f0-9]{40}$")
REV = re.compile(r"^[a-f0-9]{12}$")
UUID = re.compile(r"^[a-f0-9]{8}-[a-f0-9]{4}-[a-f0-9]{4}-[a-f0-9]{4}-[a-f0-9]{12}$")
MAX_FILE = 250_000
MAX_PACKAGE = 6_000_000
MAX_VERSIONS = 26
MAX_SLIDES = 25
MAX_HISTORY = 240

class Reject(ValueError):
    pass

def require(valid: bool, reason: str):
    if not valid:
        raise Reject(reason)

def read_bytes(root: Path, rel: str) -> bytes:
    path = root / rel
    require(path.resolve().is_relative_to(root.resolve()), "path escapes checkout")
    require(path.is_file() and not path.is_symlink(), f"missing or symlink: {rel}")
    require(path.stat().st_size <= MAX_FILE, f"oversized file: {rel}")
    return path.read_bytes()

def read_json(root: Path, rel: str):
    try:
        return json.loads(read_bytes(root, rel))
    except (UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise Reject(f"invalid JSON: {rel}") from exc

def group_changes(paths: list[str]) -> dict[str, str]:
    """Only changed package roots; no recursive inspection of unrelated products."""
    changed = {}
    for filename in paths:
        if not filename.startswith(PREFIX):
            continue
        parts = PurePosixPath(filename).parts
        require(len(parts) >= 6 and parts[0:3] == ("studio", "production", "finalized"),
                f"invalid finalized path: {filename}")
        product, revision = parts[3:5]
        require(len(product) <= 130 and SLUG.fullmatch(product) and REV.fullmatch(revision),
                f"invalid package identity: {filename}")
        key = f"{product}/{revision}"
        changed[key] = f"{PREFIX}{key}/"
    require(len(changed) <= 5, "too many product bundles per PR")
    return changed

def check_package(root: Path, prefix: str, check_source: bool = True) -> dict:
    product, rev = prefix.removeprefix(PREFIX).strip("/").split("/")
    manifest = read_json(root, prefix + "manifest.json")
    versions = manifest.get("versions")
    selected = manifest.get("selectedVersion")
    require(manifest.get("schema") == 1 and manifest.get("kind") == "brandstudio-product-finalization",
            "invalid finalization manifest")
    require(manifest.get("product") == product and isinstance(manifest.get("revision"), str) and
            UUID.fullmatch(manifest["revision"]) and
            manifest["revision"].replace("-", "").startswith(rev),
            "product/revision mismatch")
    require(isinstance(versions, list) and 1 <= len(versions) <= MAX_VERSIONS and
            all(type(v) is int and 1 <= v <= MAX_VERSIONS for v in versions) and
            versions == sorted(set(versions)) and selected in versions,
            "invalid version list / selected version")
    require(manifest.get("review") == {"creative": "pending", "socialPublished": False,
                                     "sourceAuditRequired": True},
            "finalization cannot grant approval or publish")
    source = manifest.get("source", {})
    paths = source.get("paths")
    require(source.get("repository") == "cinegitim/design" and HEX40.fullmatch(source.get("baseCommit", "")),
            "unverified source commitment")
    require(isinstance(paths, list) and 1 <= len(paths) <= MAX_SLIDES and
            all(isinstance(p, str) and p.startswith("docs/") and
                ".." not in PurePosixPath(p).parts and
                re.fullmatch(r"docs/[a-zA-Z0-9_./-]+\.html?", p) for p in paths) and
            len(set(paths)) == len(paths), "invalid source inventory")
    slide_count = len(paths)
    require(manifest.get("files", {}).get("renderedSlides") == 2 * slide_count * len(versions) and
            manifest.get("files", {}).get("versionStates") == len(versions) and
            manifest.get("files", {}).get("history") == "history.json",
            "declared file inventory mismatch")
    if check_source and (root / ".git").exists():
        for source_path in paths:
            found = subprocess.run(["git", "-C", str(root), "cat-file", "-e", f"HEAD:{source_path}"],
                                   stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, timeout=5)
            require(found.returncode == 0, f"missing original source: {source_path}")
    history = read_json(root, prefix + "history.json")
    require(history.get("schema") == 1 and history.get("product") == product and
            isinstance(history.get("history"), list) and len(history["history"]) <= MAX_HISTORY,
            "invalid version history")
    expected = {"manifest.json", "history.json"}
    for v in versions:
        ver = f"versions/v{v:02d}/"
        meta = read_json(root, prefix + ver + "editor-state.json")
        require(meta.get("schema") == 1 and meta.get("kind") == "brandstudio-saved-editor-version" and
                meta.get("product") == product and meta.get("version") == v, "version state mismatch")
        state = meta.get("state", {})
        require(isinstance(state, dict) and isinstance(state.get("colors"), dict) and
                isinstance(state.get("edits"), dict) and isinstance(state.get("groups"), dict),
                "invalid saved state")
        require(all(re.fullmatch(r"#[0-9A-Fa-f]{6}", x)
                    for x in state["colors"].values() if isinstance(x, str)),
                "invalid palette color")
        expected.add(ver + "editor-state.json")
        for slide in range(1, slide_count + 1):
            base = ver + f"slides/{slide:02d}"
            html = read_bytes(root, prefix + base + ".html")
            css = read_bytes(root, prefix + base + ".css")
            require(html[:100].lower().lstrip().startswith(b"<!doctype html>") and
                    b"<html" in html.lower() and b"</html>" in html.lower() and
                    b"class=\"slide\"" in html.lower(), "invalid exported HTML")
            require(css.strip() and b"{" in css and b"}" in css, "invalid exported CSS")
            expected.update({base + ".html", base + ".css"})
    # Detect partial or unexpected files. Do not follow symlinks.
    folder = root / prefix
    require(folder.is_dir() and not folder.is_symlink(), "package directory missing")
    actual = set()
    total = 0
    for path in folder.rglob("*"):
        require(not path.is_symlink(), "symlink inside finalization package")
        if not path.is_file():
            continue
        rel = path.relative_to(folder).as_posix()
        actual.add(rel)
        total += path.stat().st_size
        require(total <= MAX_PACKAGE, "package larger than allowed")
    require(actual == expected, f"package inventory mismatch: missing={len(expected - actual)} extra={len(actual - expected)}")
    return {"product": product, "revision": rev, "versions": len(versions),
            "candidate": selected, "slides": slide_count, "files": len(actual), "bytes": total,
            "cover": str(folder / f"versions/v{selected:02d}/slides/01.html")}

def render_cover(cover: str, timeout: int = 25):
    chrome = shutil.which("google-chrome") or shutil.which("chromium")
    require(chrome is not None, "system Chrome missing, cannot perform cover smoke test")
    with tempfile.TemporaryDirectory(prefix="brandstudio-cover-") as output:
        screenshot = Path(output) / "cover.png"
        args = [chrome, "--headless", "--no-sandbox", "--disable-gpu", "--disable-dev-shm-usage",
                "--disable-background-networking", "--no-first-run",
                "--hide-scrollbars", "--window-size=1080,1350",
                "--virtual-time-budget=1500", f"--screenshot={screenshot}",
                Path(cover).resolve().as_uri()]
        proc = subprocess.run(args, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL,
                              timeout=timeout, check=False)
        require(proc.returncode == 0 and screenshot.is_file() and screenshot.stat().st_size > 1000,
                "headless cover smoke render failed")
        header = screenshot.read_bytes()[:24]
        require(header[:8] == b"\x89PNG\r\n\x1a\n", "cover smoke image invalid PNG")
        w, h = struct.unpack(">II", header[16:24])
        require(w >= 600 and h >= 600, "cover screenshot dimensions invalid")

def audit(root: Path, changed_paths: list[str], check_source=True, cover=False):
    t0 = time.perf_counter()
    groups = group_changes(changed_paths)
    rows = []
    for prefix in groups.values():
        record = check_package(root, prefix, check_source=check_source)
        if cover:
            render_cover(record["cover"])
        record.pop("cover", None)
        rows.append(record)
    return {"packages": len(rows), "results": rows,
            "coverRenders": len(rows) if cover else 0,
            "seconds": round(time.perf_counter() - t0, 3)}

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", required=True)
    parser.add_argument("--changed", required=True)
    parser.add_argument("--render-cover", action="store_true")
    args = parser.parse_args()
    try:
        paths = Path(args.changed).read_text(encoding="utf-8").splitlines()
        result = audit(Path(args.root), paths, cover=args.render_cover)
        print(json.dumps(result, ensure_ascii=False, sort_keys=True))
        summary = __import__("os").environ.get("GITHUB_STEP_SUMMARY")
        if summary:
            with open(summary, "a", encoding="utf-8") as handle:
                handle.write(f"\n### Brandstudio lightweight handoff audit\n")
                handle.write(f"Products: {result['packages']} · cover renders: {result['coverRenders']} · elapsed: {result['seconds']} s\n")
                for record in result["results"]:
                    handle.write(f"- {record['product']}: {record['versions']} versions, {record['slides']} slides, {record['bytes']} bytes\n")
    except (Reject, OSError, subprocess.TimeoutExpired) as exc:
        print(f"FAIL CLOSED: {exc}", file=sys.stderr)
        sys.exit(1)

if __name__ == "__main__":
    main()
