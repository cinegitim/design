#!/usr/bin/env python3
"""Verify a Visual Editor style handoff against GitHub canonical files, offline.

Works for OpenCode, Codex, Work, Antigravity, or any code-capable agent with
a checkout. This is not a production run, user approval, or GitHub delivery.
"""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
import re
import sys

from style_pack import build_style_pack, verify_style_pack

ROOT = Path(__file__).resolve().parents[2]
PRODUCT = re.compile(r"^[a-z0-9]+(?:-[a-z0-9]+)*$")
VERSION = re.compile(r"^v(?:[1-9]|1[0-9]|2[0-6])$")

class HandoffError(ValueError):
    pass

def required(condition, message):
    if not condition:
        raise HandoffError(message)

def blob_hash(raw: bytes) -> str:
    return hashlib.sha1(b"blob " + str(len(raw)).encode("ascii") + b"\x00" + raw).hexdigest()

def verify_brief(brief: dict, root: Path = ROOT) -> dict:
    """Fail closed on altered fields, forged approval, brand drift, or bad files.

    Returns only a validated, brand-locked production pack and review flags.
    A review-only style stays review-only even if every hash matches.
    """
    required(type(brief) is dict, "Handoff must be an object")
    required(set(brief) == {"schema", "origin", "repository", "product",
                           "editor_cloud_version", "selection", "github",
                           "approval", "instruction"}, "Unexpected handoff fields")
    required(brief["schema"] == 1 and brief["origin"] == "brandstudio-visual-editor"
             and brief["repository"] == "cinegitim/design", "Unrecognized handoff source")
    required(isinstance(brief["product"], str) and PRODUCT.fullmatch(brief["product"])
             and isinstance(brief["editor_cloud_version"], str)
             and VERSION.fullmatch(brief["editor_cloud_version"]), "Invalid product/version")
    required(brief["github"] == {"status": "not-submitted",
                                 "branch": None, "commit": None, "pr": None},
             "A copied brief cannot claim a GitHub delivery")
    required(brief["approval"] == {"creative": "pending", "social_published": False},
             "An agent handoff cannot approve creativity or publication")
    required(isinstance(brief["instruction"], str)
             and brief["instruction"].startswith("Use the exact canonical style pack"),
             "Invalid instruction provenance")
    selection = brief["selection"]
    required(type(selection) is dict and set(selection) == {
        "schema", "brand", "category", "style_id", "style_version",
        "style_source_blob_sha", "preset_id", "lockup_id", "lockup_sha256",
        "seal_sha256", "approval_status", "font_family", "palette",
        "variation", "overrides", "source_path"}, "Invalid style selection fields")
    required(selection["schema"] == 1 and type(selection["overrides"]) is dict,
             "Invalid style selection")
    root = Path(root).resolve()
    pack = build_style_pack(root=root, brand=selection["brand"],
                            category=selection["category"],
                            style_id=selection["style_id"],
                            preset_id=selection["preset_id"],
                            variation_overrides=selection["overrides"],
                            lockup_id=selection["lockup_id"])
    verify_style_pack(pack, root=root)
    source = (root / pack["sources"]["style_definition"]).resolve()
    required(source.is_relative_to(root) and source.is_file() and not source.is_symlink(),
             "Style definition missing")
    expected = {
        "schema": 1,
        "brand": pack["brand"],
        "category": pack["category"],
        "style_id": pack["style"]["id"],
        "style_version": pack["style"]["version"],
        "style_source_blob_sha": blob_hash(source.read_bytes()),
        "preset_id": pack["style"]["preset_id"],
        "lockup_id": pack["identity"]["lockup_id"],
        "lockup_sha256": pack["identity"]["lockup_sha256"],
        "seal_sha256": pack["identity"]["seal_sha256"],
        "approval_status": pack["style"]["status"],
        "font_family": pack["typography"]["body_family"],
        "palette": pack["palette"],
        "variation": pack["style"]["variation"],
        "overrides": pack["style"]["overrides"],
        "source_path": pack["sources"]["style_definition"],
    }
    required(selection == expected, "Style or canonical identity differs from repository")
    return {
        "schema": 1, "result": "verified-style-contract",
        "product": brief["product"],
        "editor_cloud_version": brief["editor_cloud_version"],
        "style_pack": pack,
        "review": {
            "creative": "pending",
            "style_approved": pack["style"]["production_approved"],
            "social_published": False,
        },
        "github": {"status": "not-submitted"},
        "instructions": [
            "Read AGENTS.md, studio/production/BOOTSTRAP.md, and the exact style/brand/lockup sources.",
            "Keep the original user brief and copy verbatim; this handoff contains no original copy.",
            "Create editable HTML/CSS/SVG with canonical logo bytes, not a raster recreation.",
            "Validate and visually review actual rendered artwork before a separate GitHub PR.",
            "Do not claim any creative, social-publication, or source-version approval."
        ]
    }

def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--brief", required=True, help="JSON production brief path, or - for stdin")
    parser.add_argument("--root", type=Path, default=ROOT)
    args = parser.parse_args()
    try:
        raw = (sys.stdin.read(250_001) if args.brief == "-"
               else Path(args.brief).read_text(encoding="utf-8"))
        required(len(raw.encode("utf-8")) <= 250_000, "Brief exceeds 250 KB")
        result = verify_brief(json.loads(raw), args.root)
    except (ValueError, OSError, KeyError, TypeError, json.JSONDecodeError) as error:
        parser.error(str(error))
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
