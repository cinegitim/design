#!/usr/bin/env python3
"""Build/read a *public read-only* Brandstudio system hub snapshot.

Canonical sources: production routes, approved brand/lockup manifest, client
style registry and advisory model-family overlays. This tool cannot publish,
approve, run a model or create a GitHub PR.
"""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path


def load(root: Path, relative: str) -> dict:
    path = (root / relative).resolve()
    if not path.is_relative_to(root) or not path.is_file() or path.is_symlink():
        raise ValueError("Unsafe or missing catalog source: " + relative)
    data = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(data, dict):
        raise ValueError("Catalog source must be an object: " + relative)
    return data


def git_blob(content: bytes) -> str:
    return hashlib.sha1(b"blob " + str(len(content)).encode("ascii") + b"\0" + content).hexdigest()


def build_public_catalog(root: Path) -> dict:
    root = Path(root).resolve()
    routes = load(root, "studio/production/routes.json")
    registry = load(root, "docs/visual-editor/browser/style-registry.json")
    families = load(root, "studio/production/model-families.json")
    brand = load(root, "brands/asyada-egitim/brand.json")
    canonical = load(root, brand["canonicalLockups"]["manifest"])
    if routes.get("schema_version") != 1 or registry.get("schema") != 1 or families.get("schema_version") != 1:
        raise ValueError("Unsupported catalog schema")
    if brand.get("slug") != "asyada-egitim" or registry.get("brand") != brand["slug"]:
        raise ValueError("Brand scope drift")
    if canonical.get("status") != "APPROVED / CANONICAL":
        raise ValueError("Identity approval not grounded")
    if canonical["typography"]["turkish"]["family"] != "Jost":
        raise ValueError("Unexpected brand typography")

    categories = []
    cat_ids = set(routes["categories"])
    if {x["id"] for x in registry["categories"]} != cat_ids:
        raise ValueError("Editor categories and route categories disagree")
    styles = []
    ids = set()
    records = {r["canonical_lockup_id"]: r for r in canonical["records"]}
    for s in registry["styles"]:
        sid = (s["brand"], s["category"], s["style_id"])
        if sid in ids or sid[0] != brand["slug"] or sid[1] not in cat_ids:
            raise ValueError("Duplicate or unrelated style")
        ids.add(sid)
        path = s["source_path"]
        source = (root / path).resolve()
        if not source.is_relative_to(root) or not source.is_file():
            raise ValueError("Missing canonical style source")
        raw = source.read_bytes()
        if git_blob(raw) != s["source_blob_sha"]:
            raise ValueError("Stale style source blob SHA")
        origin = json.loads(raw)
        for k in ("brand", "category", "style_id", "version", "status", "presets", "variation_axes"):
            if origin.get(k) != s[k]:
                raise ValueError("Style registry drift: " + k)
        if origin["hard_locks"]["palette_tokens"] != s["palette"]:
            raise ValueError("Palette drift")
        if list(origin["hard_locks"]["lockup_options"]) != [x["id"] for x in s["lockups"]]:
            raise ValueError("Logo allowlist drift")
        if s["font_family"] != "Jost":
            raise ValueError("Typography drift")
        if s.get("seal_sha256") != canonical["canonical_seal_sha256"]:
            raise ValueError("Canonical seal digest drift")
        seal = (root / canonical["canonical_seal_path"]).resolve()
        if not seal.is_relative_to(root) or not seal.is_file() or hashlib.sha256(seal.read_bytes()).hexdigest() != s["seal_sha256"]:
            raise ValueError("Canonical seal bytes changed")
        for logo in s["lockups"]:
            record = records.get(logo["id"])
            if not record or record["sha256"] != logo["sha256"] or record["canonical_file_path"] != logo["path"]:
                raise ValueError("Noncanonical logo referenced")
            asset_path = (root / logo["path"]).resolve()
            if not asset_path.is_relative_to(root) or not asset_path.is_file():
                raise ValueError("Missing canonical logo bytes")
            if hashlib.sha256(asset_path.read_bytes()).hexdigest() != logo["sha256"]:
                raise ValueError("Approved logo file changed")
        styles.append({
            "id": s["style_id"], "name": s["name"], "category": s["category"], "brand": s["brand"],
            "version": s["version"], "status": s["status"],
            "production_approved": s["status"] == "approved" and origin["approval"].get("human_style_approval") is True,
            "description": s.get("description", ""),
            "source_path": path, "source_blob_sha": s["source_blob_sha"],
            "palette": s["palette"], "font": s["font_family"],
            "presets": [{"id": key, "label": value["label"]} for key, value in s["presets"].items()],
            "axes": list(s["variation_axes"]),
            "lockups": [x["id"] for x in s["lockups"]],
            "lockup_assets": [{"id": x["id"], "path": x["path"], "sha256": x["sha256"]} for x in s["lockups"]],
        })
    for category in registry["categories"]:
        count = sum(s["category"] == category["id"] for s in styles)
        if bool(category["registered"]) != (count > 0):
            raise ValueError("Style category activation drift")
        categories.append({"id": category["id"], "label": category["label"], "style_count": count,
                           "status": "registered" if count else "not-configured"})

    executors = []
    for p in routes["profiles"]:
        if not isinstance(p.get("id"), str) or not isinstance(p.get("requires"), list):
            raise ValueError("Invalid executor profile")
        executors.append({
            "id": p["id"], "executor": p["executor"], "strategy": p["strategy"],
            "required_capabilities": p["requires"], "categories": p["categories"],
            "references": p.get("references", []),
            "effort": p.get("effort"),
            "status": "configured-route-not-live-verified",
        })

    model_families = families["model_families"]
    if len(set(x["id"] for x in model_families)) != len(model_families):
        raise ValueError("Duplicate model family")
    for f in model_families:
        if f.get("status") != "advisory" or f.get("capabilities_verified") is not False:
            raise ValueError("Unverified LLM capability cannot become a fact")
        if not all(isinstance(f["emphasis"].get(x), str) for x in ("code", "image")):
            raise ValueError("Missing model-family advisory rules")

    return {
        "schema": 1,
        "brand": {"id": "asyada-egitim", "name": "Asya'da Eğitim"},
        "brand_identity": {
            "status": "approved-canonical", "seal_id": "V-01",
            "seal_sha256": canonical["canonical_seal_sha256"],
            "font": "Jost", "palette": styles[0]["palette"] if styles else {},
            "canonical_manifest": brand["canonicalLockups"]["manifest"],
            "logo_generation_allowed": False,
        },
        "categories": categories, "styles": styles, "executors": executors,
        "model_families": model_families,
        "workflow": {
            "style_selection": "canonical-github-registry",
            "visual_editor_versions": "cloud-drafts",
            "github_version": "pr-required",
            "social_proof": "platform-evidence-required",
            "creative_approval": "human-required",
            "automatic_agent_execution": False,
        },
    }


def render_json(catalog: dict) -> str:
    return json.dumps(catalog, ensure_ascii=False, indent=2) + "\n"


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=Path(__file__).resolve().parents[2])
    parser.add_argument("--check", action="store_true", help="Fail if checked-in public JSON is stale")
    parser.add_argument("--write", action="store_true", help="Update only public catalog snapshot")
    args = parser.parse_args()
    if args.write and args.check:
        parser.error("--check and --write are mutually exclusive")
    content = render_json(build_public_catalog(args.root))
    out = args.root / "docs/system/catalog.json"
    if args.check:
        if not out.exists() or out.read_text(encoding="utf-8") != content:
            parser.error("Stale docs/system/catalog.json; run public_catalog.py --write")
        print("Brandstudio public catalog current")
    elif args.write:
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_text(content, encoding="utf-8")
        print(str(out))
    else:
        print(content, end="")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
