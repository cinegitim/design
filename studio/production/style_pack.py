#!/usr/bin/env python3
"""Deterministic, agent-neutral Brandstudio visual-language contract.

Uses only repository files; does not render, call models, approve creative
work, write files or post on social media.
"""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path

from style_catalog import resolve_style


def _read_json(root: Path, relative: str) -> dict:
    path = (root / relative).resolve()
    if not path.is_relative_to(root.resolve()) or not path.is_file():
        raise ValueError("Unsafe or missing design-system source: " + relative)
    data = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(data, dict):
        raise ValueError("Invalid design-system JSON object: " + relative)
    return data


def _verify_hash(root: Path, relative: str, expected: str) -> None:
    path = (root / relative).resolve()
    if not path.is_relative_to(root.resolve()) or not path.is_file() or path.is_symlink():
        raise ValueError("Missing approved brand asset: " + relative)
    actual = hashlib.sha256(path.read_bytes()).hexdigest()
    if actual != expected:
        raise ValueError("Approved brand asset digest mismatch: " + relative)


def build_style_pack(*, root: Path, brand: str, category: str,
                     style_id: str, preset_id: str | None = None,
                     variation_overrides: dict[str, str] | None = None,
                     lockup_id: str | None = None,
                     executor: str | None = None) -> dict:
    """Resolve a selected style into the same immutable rules for every agent.

    The executor argument is explicitly ignored: production runtime is a
    separate provenance record and must not change visual rules.
    """
    root = Path(root).resolve()
    if not isinstance(style_id, str):
        raise ValueError("Explicit style selection required")
    selected = resolve_style(root=root, brand=brand, category=category,
                             style_id=style_id, preset_id=preset_id,
                             variation_overrides=variation_overrides)
    if selected is None:
        raise ValueError("Explicit style selection required")
    brand_path = f"brands/{brand}/brand.json"
    canonical_brand = _read_json(root, brand_path)
    if canonical_brand.get("slug") != brand or not canonical_brand.get("canonicalIdentity"):
        raise ValueError("Brand identity not canonically approved")
    metadata = canonical_brand["canonicalLockups"]
    manifest_path = metadata["manifest"]
    canonical = _read_json(root, manifest_path)
    if canonical.get("brand_id") != brand or canonical.get("status") != "APPROVED / CANONICAL":
        raise ValueError("Canonical brand manifest mismatch")
    if not metadata.get("locked") or metadata.get("status") != canonical["status"]:
        raise ValueError("Canonical lockups not locked")

    style = _read_json(root, selected["definition_path"])
    identity = style["hard_locks"]
    allowed = identity["lockup_options"]
    preview = style["preview_quality_contract"]["identity_gate"]["allowed_approved_lockups"]
    if not isinstance(allowed, list) or len(allowed) != len(set(allowed)) or not allowed:
        raise ValueError("Invalid style lockup options")
    if allowed != preview:
        raise ValueError("Preview and source lockup allowlists disagree")
    retired = set(metadata.get("retiredVariants", [])) | set(metadata.get("retired", []))
    manifest_ids = {r["canonical_lockup_id"] for r in canonical["records"]}
    if any(x.split("/")[0] in retired or x not in manifest_ids for x in allowed):
        raise ValueError("Style requests retired or unapproved canonical lockup")
    if not str(identity.get("typeface", "")).startswith("Jost"):
        raise ValueError("Style text must use Jost")

    palette = identity["palette_tokens"]
    approved_palette = {"paper": "#F7F3E9", "red": "#BD2120", "ink": "#1D2027"}
    if palette != approved_palette:
        raise ValueError("Unapproved institutional color tokens")
    chosen_id = lockup_id or "H-02/dark"
    if chosen_id not in allowed:
        raise ValueError("Selected lockup not permitted by style")
    record = next(x for x in canonical["records"] if x["canonical_lockup_id"] == chosen_id)
    seal_path = canonical["canonical_seal_path"]
    seal_hash = canonical["canonical_seal_sha256"]
    if seal_hash != canonical_brand["canonicalLogo"]["sha256"]:
        raise ValueError("Brand seal identity drift")
    if record["canonical_seal_sha256"] != seal_hash:
        raise ValueError("Lockup points to a different seal")
    if record.get("status") != "APPROVED / CANONICAL":
        raise ValueError("Lockup record not approved")
    _verify_hash(root, record["canonical_file_path"], record["sha256"])
    _verify_hash(root, seal_path, seal_hash)
    type_spec = canonical["typography"]
    if type_spec["turkish"]["family"] != "Jost" or type_spec["english"]["family"] != "Jost":
        raise ValueError("Unexpected brand typography")

    return {
        "contract_version": 1,
        "brand": brand,
        "category": category,
        "status": selected["status"],
        "style": {
            "id": selected["style_id"],
            "version": selected["version"],
            "status": selected["status"],
            "production_approved": selected["approved"],
            "preset_id": selected["preset_id"],
            "variation": selected["variation"],
            "overrides": selected["overrides"],
            "definition_path": selected["definition_path"],
            "canvas_px": identity["output_size_px"],
        },
        "identity": {
            "canonical_approved": True,
            "seal_id": "V-01",
            "seal_path": seal_path,
            "seal_sha256": seal_hash,
            "lockup_id": chosen_id,
            "lockup_path": record["canonical_file_path"],
            "lockup_sha256": record["sha256"],
            "minimum_screen_width_px": record["minimum_supported_display_size"]["screen_width_px"],
            "allowed_lockup_ids": allowed,
            "allowed_operations": canonical["allowed_operations"],
            "forbidden_operations": canonical["forbidden_operations"],
        },
        "palette": dict(palette),
        "typography": {
            "body_family": "Jost",
            "turkish_weight": type_spec["turkish"]["weight"],
            "english_weight": type_spec["english"]["weight"],
            "logo_runtime_font_dependency": False,
        },
        "sources": {
            "brand_path": brand_path,
            "lockup_manifest": manifest_path,
            "style_definition": selected["definition_path"],
        },
        "review": {
            "human_style_approval": style["approval"]["human_style_approval"],
            "creative_approval_required": True,
            "social_publish_approved": False,
        },
    }


def verify_style_pack(pack: dict, *, root: Path) -> bool:
    """Rebuild from repository truth and reject every changed field, including unknowns."""
    if not isinstance(pack, dict):
        raise ValueError("Invalid style pack")
    try:
        style = pack["style"]
        identity = pack["identity"]
        rebuilt = build_style_pack(
            root=root, brand=pack["brand"], category=pack["category"],
            style_id=style["id"], preset_id=style["preset_id"],
            variation_overrides=style["overrides"],
            lockup_id=identity["lockup_id"],
        )
    except (KeyError, TypeError, IndexError) as exc:
        raise ValueError("Malformed style contract") from exc
    if rebuilt != pack:
        raise ValueError("Style pack differs from verified repository rules")
    return True


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=Path(__file__).resolve().parents[2])
    parser.add_argument("--brand", required=True)
    parser.add_argument("--category", required=True)
    parser.add_argument("--style", required=True)
    parser.add_argument("--preset")
    parser.add_argument("--lockup", default="H-02/dark")
    parser.add_argument("--variation", action="append", default=[])
    args = parser.parse_args()
    try:
        overrides = {}
        for value in args.variation:
            if "=" not in value:
                raise ValueError("Variation must be AXIS=VALUE")
            axis, variant = value.split("=", 1)
            if axis in overrides:
                raise ValueError("Duplicate variation axis")
            overrides[axis] = variant
        pack = build_style_pack(
            root=args.root, brand=args.brand, category=args.category,
            style_id=args.style, preset_id=args.preset,
            lockup_id=args.lockup, variation_overrides=overrides,
        )
        verify_style_pack(pack, root=args.root)
    except (ValueError, OSError, KeyError, json.JSONDecodeError) as exc:
        parser.error(str(exc))
    print(json.dumps(pack, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
