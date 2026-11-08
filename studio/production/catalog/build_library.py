#!/usr/bin/env python3
"""Build/check public Brandstudio library from the canonical catalog, offline.

Canonical associations: studio/production/catalog/navigation.json.
Canonical product/version list: docs/visual-editor/browser/product-groups.json.
Canonical style definitions: brands/<brand>/styles/<format>/<style>/style.json,
with verified browser style registry as their static discoverability projection.

The new static site and existing editor read snapshots of these sources.
No auth, API, worker, GitHub operation, database write, or approval is performed.
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path
import re
import sys

ROOT = Path(__file__).resolve().parents[3]
SOURCE = "studio/production/catalog/navigation.json"
EDITOR = "docs/visual-editor/browser/navigation-classification.json"
OUTPUT = "docs/library/catalog.json"
IDENTIFIER = re.compile(r"^[a-z0-9]+(?:-[a-z0-9]+)*$")
EVIDENCE = re.compile(r"^https://github\.com/cinegitim/design/(?:pull/[1-9]\d*|commit/[0-9a-fA-F]{40})/?$")
FORMAT = {
    "Karuseller": "instagram-carousel",
    "Tekil Paylaşımlar": "social-post",
    "Profil ve Kapaklar": "identity-application",
    "Roll-up": "print-catalog",
}


def load(root: Path, relative: str) -> dict:
    file = (root / relative).resolve()
    if not file.is_relative_to(root) or not file.is_file() or file.is_symlink():
        raise ValueError("Missing or unsafe catalog source: " + relative)
    obj = json.loads(file.read_text(encoding="utf-8"))
    if not isinstance(obj, dict):
        raise ValueError("Expected a JSON object: " + relative)
    return obj


def require(ok: bool, error: str) -> None:
    if not ok:
        raise ValueError(error)


def build(root: Path = ROOT) -> dict:
    root = Path(root).resolve()
    nav = load(root, SOURCE)
    groups = load(root, "docs/visual-editor/browser/product-groups.json")
    registry = load(root, "docs/visual-editor/browser/style-registry.json")
    require(nav.get("schema") == groups.get("schema") == registry.get("schema") == 1,
            "Incompatible library schema")
    require(nav.get("repository") == "cinegitim/design" and
            nav.get("scope") == "navigation-proposals-only", "Untrusted taxonomy source")
    products = groups.get("groups")
    styles = registry.get("styles")
    require(isinstance(products, list) and isinstance(styles, list), "Missing product or style array")
    require(isinstance(nav.get("items"), list) and isinstance(nav.get("confirmedVersions"), list),
            "Invalid associations")
    by_group = {}
    style_map = {}
    for s in styles:
        key = (s.get("brand"), s.get("category"), s.get("style_id"))
        require(key not in style_map and all(isinstance(x, str) and IDENTIFIER.fullmatch(x) for x in key),
                "Duplicate/unsafe style key")
        require(isinstance(s.get("presets"), dict) and s["presets"], "Missing style presets")
        style_map[key] = s
    for group in products:
        gid = group.get("id")
        require(isinstance(gid, str) and IDENTIFIER.fullmatch(gid) and gid not in by_group,
                "Invalid/duplicate product ID")
        versions = group.get("versions")
        require(isinstance(versions, list) and len(versions) > 0, "Product without source versions")
        vids = [v["id"] for v in versions]
        require(len(set(vids)) == len(vids) and all(IDENTIFIER.fullmatch(x) for x in vids),
                "Duplicate or invalid source version")
        require(group["currentId"] in vids and group["defaultId"] in vids,
                "Broken source version selector")
        if group.get("publishedVersionId") is not None:
            require(group["publishedVersionId"] in vids, "Published version not in product family")
        by_group[gid] = group

    classification = {}
    for item in nav["items"]:
        gid = item.get("groupId")
        require(gid in by_group and gid not in classification, "Missing or duplicate category assignment")
        main, sub = item.get("mainCategory"), item.get("subCategory")
        require(main in FORMAT and isinstance(sub, str) and 0 < len(sub) <= 90,
                "Invalid main/content category")
        group = by_group[gid]
        old = group.get("categoryPath") or []
        old_main = (old[1] if len(old) > 1 and old[0] == "Sosyal Medya" else
                    "Roll-up" if old[:1] == ["Baskı"] else None)
        require(old_main in (main, "Kimlik Uygulamaları") or old_main is None,
                "Category is incompatible with product format")
        if old_main == "Kimlik Uygulamaları":
            require(main == "Profil ve Kapaklar", "Identity application format mismatch")
        suggestion = item.get("suggestion")
        if suggestion is not None:
            require(isinstance(suggestion, dict) and suggestion.get("status") == "proposed"
                    and suggestion.get("scope") == "future-design",
                    "Unreviewed proposals cannot claim historic or creative approval")
            s = style_map.get((group["brand"], FORMAT[main], suggestion.get("styleId")))
            require(s is not None and suggestion.get("presetId") in s["presets"],
                    "Proposed style does not belong to the product's brand/format")
        classification[gid] = item
    require(set(classification) == set(by_group),
            "Every active family requires exactly one content category")

    confirmed = {}
    for link in nav["confirmedVersions"]:
        gid,vid = link.get("groupId"),link.get("versionId")
        require(gid in by_group and vid in [v["id"] for v in by_group[gid]["versions"]],
                "Verified style link is not an existing source version")
        require(vid not in confirmed and link.get("status") == "verified" and
                isinstance(link.get("evidence"), str) and EVIDENCE.fullmatch(link["evidence"]),
                "Verified link requires unique version and source-review evidence")
        group = by_group[gid]
        main = classification[gid]["mainCategory"]
        s = style_map.get((group["brand"], FORMAT[main], link.get("styleId")))
        require(s is not None and link.get("presetId") in s["presets"],
                "Verified link brand/category/preset mismatch")
        confirmed[vid] = link

    records = []
    for gid,group in by_group.items():
        entry = classification[gid]
        links = []
        for v in group["versions"]:
            if v["id"] in confirmed:
                match = confirmed[v["id"]]
                links.append({
                    "styleId": match["styleId"], "presetId": match["presetId"],
                    "status": "verified", "versionId": v["id"], "evidence": match["evidence"]
                })
        if "suggestion" in entry:
            s=entry["suggestion"]
            links.append({
                "styleId": s["styleId"], "presetId": s["presetId"],
                "status": "proposed", "scope": "future-design", "versionId": None
            })
        records.append({
            "groupId": gid, "title": group["title"], "brand": group["brand"],
            "mainCategory": entry["mainCategory"], "subCategory": entry["subCategory"],
            "versions": [{"id":v["id"],"label":v["label"]} for v in group["versions"]],
            "defaultId": group["defaultId"], "currentId": group["currentId"],
            "publishedVersionId": group.get("publishedVersionId"), "styleLinks": links
        })

    definitions = [{
        "id": s["style_id"], "name": s["name"], "brand": s["brand"],
        "category": s["category"], "description": s["description"],
        "status": s["status"], "sourcePath": s["source_path"],
        "sourceBlobSha": s["source_blob_sha"],
        "presets": [{"id": pid, "label": p["label"]}
                    for pid,p in s["presets"].items()]
    } for s in styles]
    categories = []
    for brand in dict.fromkeys(p["brand"] for p in records):
        mains = []
        for main in FORMAT:
            subcats = list(dict.fromkeys(p["subCategory"] for p in records
                     if p["brand"] == brand and p["mainCategory"] == main))
            if subcats:
                mains.append({"id":main,"subcategories":subcats})
        categories.append({"brand":brand,"mains":mains})

    return {
        "schema": 1,
        "source": {
            "repository": "cinegitim/design",
            "taxonomy": SOURCE,
            "productVersions": "docs/visual-editor/browser/product-groups.json",
            "styleRegistry": "docs/visual-editor/browser/style-registry.json"
        },
        "rules": {
            "hierarchy": ["Ana kategori","İçerik alt kategorisi","Ortak tarz",
                          "Tarz çeşitlemesi","Tekil ürün"],
            "verified": "Source-version evidence is required; these links do not claim creative approval.",
            "proposed": "Future design suggestion; does not describe the existing artwork.",
            "noStyle": "No registered or verified style association."
        },
        "categories": categories,
        "styles": definitions,
        "products": records,
        "retiredCount": len(groups.get("retired",[]))
    }


def output_text(data: dict) -> str:
    return json.dumps(data, ensure_ascii=False, indent=2) + "\n"


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=ROOT)
    group = parser.add_mutually_exclusive_group()
    group.add_argument("--check", action="store_true")
    group.add_argument("--write", action="store_true")
    args = parser.parse_args()
    root = args.root.resolve()
    try:
        canonical = load(root, SOURCE)
        catalog = build(root)
        targets = [
            (EDITOR, output_text(canonical)),
            (OUTPUT, output_text(catalog)),
        ]
        stale = [path for path,expected in targets if
                 not (root / path).is_file() or
                 (root / path).read_text(encoding="utf-8") != expected]
        if stale and not args.write:
            raise ValueError("Stale projections: " + ", ".join(stale) +
                             " (run --write only when intentionally editing the catalog)")
        if args.write:
            for path,content in targets:
                file=root/path
                file.parent.mkdir(parents=True, exist_ok=True)
                file.write_text(content, encoding="utf-8")
        print(json.dumps({"status": "updated" if stale else "verified",
                          "products": len(catalog["products"]),
                          "source_versions": sum(len(p["versions"]) for p in catalog["products"]),
                          "styles":len(catalog["styles"]),
                          "proposed":sum(any(l["status"]=="proposed" for l in p["styleLinks"])
                                         for p in catalog["products"]),
                          "verified":sum(l["status"]=="verified" for p in catalog["products"]
                                         for l in p["styleLinks"]),
                          "stale":stale},ensure_ascii=False))
        return 0
    except (ValueError, OSError, KeyError, TypeError) as exc:
        parser.error(str(exc))


if __name__ == "__main__":
    raise SystemExit(main())
