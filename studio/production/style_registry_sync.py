#!/usr/bin/env python3
"""On-demand, stdlib-only sync/check of category→style registry projections.

Canonical source: brands/<brand>/styles/<category>/<style>/style.json.
Browser and system catalogs are read-only projections; no APIs, LLMs or cron.
Default is --check (no writes); --write is an explicit authoring operation.
"""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
import re

ROOT = Path(__file__).resolve().parents[2]
BRAND = "asyada-egitim"
SAFE = re.compile(r"^[a-z0-9]+(?:-[a-z0-9]+)*$")


def checked(condition: bool, reason: str) -> None:
    if not condition:
        raise ValueError(reason)


def read_json(root: Path, relative: str) -> dict:
    path = (root / relative).resolve()
    checked(path.is_relative_to(root.resolve()) and path.is_file() and not path.is_symlink(),
            f"Missing or unsafe source: {relative}")
    return json.loads(path.read_text(encoding="utf-8"))


def style_sources(root: Path, categories: list[str]) -> dict[tuple[str, str], dict]:
    found = {}
    for category in categories:
        checked(bool(SAFE.fullmatch(category)), "Invalid style category")
        directory = root / "brands" / BRAND / "styles" / category
        if not directory.exists():
            continue
        for candidate in sorted(directory.iterdir()):
            if not candidate.is_dir() or not SAFE.fullmatch(candidate.name):
                continue
            relative = f"brands/{BRAND}/styles/{category}/{candidate.name}/style.json"
            if not (root / relative).is_file():
                continue
            raw = (root / relative).read_bytes()
            spec = read_json(root, relative)
            checked(spec.get("schema_version") == 1 and
                    (spec.get("brand"), spec.get("category"), spec.get("style_id")) ==
                    (BRAND, category, candidate.name), "Style scope mismatch: " + relative)
            checked(spec.get("status") in {"review-only", "approved", "locked"},
                    "Invalid style status")
            checked(spec.get("approval", {}).get("human_style_approval") is
                    (spec["status"] in {"approved", "locked"}), "Style approval mismatch")
            checked(spec.get("hard_locks", {}).get("palette_tokens") ==
                    {"paper": "#F7F3E9", "red": "#BD2120", "ink": "#1D2027"},
                    "Unexpected brand palette")
            checked(str(spec["hard_locks"]["typeface"]).startswith("Jost"), "Unexpected font")
            axes = spec.get("variation_axes", {})
            presets = spec.get("presets", {})
            checked(isinstance(axes, dict) and isinstance(presets, dict) and bool(presets),
                    "Missing style variations")
            for key, preset in presets.items():
                checked(bool(SAFE.fullmatch(key)) and isinstance(preset, dict) and
                        isinstance(preset.get("variants"), dict), "Invalid preset: " + key)
                for axis, choice in preset["variants"].items():
                    checked(axis in axes and choice in axes[axis]["options"],
                            "Preset contains an unsupported variation")
            for axis, values in axes.items():
                checked(values.get("default") in values.get("options", []),
                        "Variation axis has invalid default: " + axis)
            checked(spec["default_preset"] in presets, "Missing default preset")
            sha = hashlib.sha1(b"blob " + str(len(raw)).encode() + b"\0" + raw).hexdigest()
            found[(category, candidate.name)] = {"spec": spec, "sha": sha, "path": relative}
    return found


def project(root: Path) -> tuple[dict, dict]:
    registry = read_json(root, "docs/visual-editor/browser/style-registry.json")
    system = read_json(root, "docs/system/catalog.json")
    checked(registry.get("schema") == system.get("schema") == 1 and
            registry.get("brand") == system.get("brand", {}).get("id") == BRAND,
            "Brand registry scope mismatch")
    cats = [c["id"] for c in registry["categories"]]
    checked(cats == [c["id"] for c in system["categories"]], "Category taxonomy drift")
    sources = style_sources(root, cats)
    # Preserve existing editorial ordering; append new styles deterministically.
    current = [(s["category"], s["style_id"]) for s in registry["styles"]]
    checked(len(current) == len(set(current)), "Duplicate style in browser catalog")
    order = [x for x in current if x in sources] + sorted(set(sources) - set(current))
    manifest = read_json(root, "brands/asyada-egitim/assets/lockups/canonical-lockups.json")
    records = {r["canonical_lockup_id"]: r for r in manifest["records"]}
    result_browser, result_system = [], []
    for category, style_id in order:
        x = sources[(category, style_id)]
        s, sha, definition = x["spec"], x["sha"], x["path"]
        ids = s["hard_locks"]["lockup_options"]
        checked(len(ids) == len(set(ids)) and ids, "Duplicate/missing lockup options")
        lockups = []
        for lid in ids:
            checked(lid in records and records[lid].get("status") == "APPROVED / CANONICAL",
                    "Unknown canonical lockup: " + lid)
            rec = records[lid]
            asset = root / rec["canonical_file_path"]
            checked(asset.is_file() and not asset.is_symlink() and
                    hashlib.sha256(asset.read_bytes()).hexdigest() == rec["sha256"],
                    "Canonical logo SHA-256 mismatch: " + lid)
            lockups.append({"id": lid, "path": rec["canonical_file_path"],
                            "sha256": rec["sha256"]})
        common = {"brand": BRAND, "category": category,
                  "version": s["version"], "status": s["status"],
                  "source_path": definition, "source_blob_sha": sha,
                  "description": s["description"]}
        result_browser.append({
            "style_id": style_id, "name": s["name"], **common,
            "default_preset": s["default_preset"], "presets": s["presets"],
            "variation_axes": s["variation_axes"],
            "palette": s["hard_locks"]["palette_tokens"], "font_family": "Jost",
            "lockups": lockups, "seal_sha256": manifest["canonical_seal_sha256"]
        })
        result_system.append({
            "id": style_id, "name": s["name"],
            "category": category, "brand": BRAND,
            "version": s["version"], "status": s["status"],
            "production_approved": s["status"] == "approved" and
                                   s["approval"]["human_style_approval"] is True,
            "description": s["description"],
            "source_path": definition, "source_blob_sha": sha,
            "palette": s["hard_locks"]["palette_tokens"], "font": "Jost",
            "presets": [{"id": pid, "label": p["label"]}
                        for pid, p in s["presets"].items()],
            "axes": list(s["variation_axes"]), "lockups": ids,
            "lockup_assets": lockups
        })
    for c in registry["categories"]:
        c["registered"] = any(x["category"] == c["id"] for x in result_browser)
    for c in system["categories"]:
        n = sum(x["category"] == c["id"] for x in result_system)
        c["style_count"] = n
        c["status"] = "registered" if n else "not-configured"
    registry["styles"] = result_browser
    system["styles"] = result_system
    return registry, system


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=ROOT)
    group = parser.add_mutually_exclusive_group()
    group.add_argument("--check", action="store_true", help="Verify projections; default")
    group.add_argument("--write", action="store_true", help="Explicitly update both derived catalogs")
    args = parser.parse_args()
    root = args.root.resolve()
    browser, system = project(root)
    pairs = [
        ("docs/visual-editor/browser/style-registry.json", browser),
        ("docs/system/catalog.json", system),
    ]
    changes = []
    for rel, expected in pairs:
        old = read_json(root, rel)
        if old != expected:
            changes.append(rel)
            if args.write:
                (root / rel).write_text(json.dumps(expected, ensure_ascii=False, indent=2) + "\n",
                                        encoding="utf-8")
    if changes and not args.write:
        parser.error("Outdated derived catalogs: " + ", ".join(changes) + " (run --write explicitly)")
    print(json.dumps({"status": "updated" if changes and args.write else "verified",
                      "registered_styles": len(browser["styles"]),
                      "categories": len(browser["categories"]),
                      "changed": changes}, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
