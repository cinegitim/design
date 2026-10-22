#!/usr/bin/env python3
"""Read-only, brand/category-scoped Brandstudio style family registry.

A style is a proposal for visual grammar, not a brand/identity approval or
proof that the output will meet a visual standard. No filesystem writes.
"""
from __future__ import annotations

import json
import re
from pathlib import Path

SLUG = re.compile(r"^[a-z0-9]+(?:-[a-z0-9]+)*$")


def _valid_slug(value: str, kind: str) -> str:
    if not isinstance(value, str) or not SLUG.fullmatch(value):
        raise ValueError(f"Invalid {kind} identifier")
    return value


def style_path(root: Path, brand: str, category: str, style_id: str) -> Path:
    return (
        Path(root) / "brands" / _valid_slug(brand, "brand")
        / "styles" / _valid_slug(category, "category")
        / _valid_slug(style_id, "style") / "style.json"
    )


def _read_style(root: Path, brand: str, category: str, style_id: str) -> tuple[Path, dict]:
    path = style_path(root, brand, category, style_id)
    if not path.is_file():
        raise ValueError(f"Unknown style for brand/category: {style_id}")
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise ValueError(f"Invalid style manifest: {style_id}") from exc
    if not isinstance(data, dict) or (
        data.get("style_id"), data.get("brand"), data.get("category")
    ) != (style_id, brand, category):
        raise ValueError("Style manifest scope mismatch")
    if data.get("status") not in ("review-only", "approved", "locked"):
        raise ValueError("Unknown style approval status")
    if not isinstance(data.get("variation_axes"), dict) or not isinstance(data.get("presets"), dict):
        raise ValueError("Incomplete variation spec")
    for axis, spec in data["variation_axes"].items():
        if (not isinstance(spec, dict) or not isinstance(spec.get("options"), list)
                or spec.get("default") not in spec["options"]):
            raise ValueError(f"Invalid variation axis: {axis}")
    return path, data


def list_styles(*, root: Path, brand: str, category: str) -> list[dict]:
    """Enumerate only styles registered for this exact brand and category."""
    base = style_path(root, brand, category, "placeholder").parent.parent
    if not base.is_dir():
        return []
    items = []
    for candidate in sorted(base.iterdir()):
        if not candidate.is_dir() or not SLUG.fullmatch(candidate.name):
            continue
        if not (candidate / "style.json").is_file():
            continue
        _, spec = _read_style(root, brand, category, candidate.name)
        items.append({
            "style_id": spec["style_id"],
            "name": spec["name"],
            "version": spec["version"],
            "status": spec["status"],
            "default_preset": spec["default_preset"],
            "preset_ids": sorted(spec["presets"]),
        })
    return items


def resolve_style(
    *, root: Path, brand: str, category: str,
    style_id: str | None = None, preset_id: str | None = None,
    variation_overrides: dict[str, str] | None = None,
) -> dict | None:
    """Resolve a user-chosen family, optional preset and validated axis overrides.

    No style selection is inferred. Presets compose into a family, not into
    separate style IDs; user overrides take precedence and remain recorded.
    """
    if style_id is None:
        if preset_id is not None or variation_overrides:
            raise ValueError("Select a style before specifying a preset or variation")
        return None
    path, spec = _read_style(root, brand, category, style_id)
    preset_id = preset_id or spec.get("default_preset")
    presets = spec["presets"]
    if not isinstance(preset_id, str) or preset_id not in presets:
        raise ValueError(f"Unknown preset: {preset_id}")
    chosen = presets[preset_id].get("variants", {})
    if not isinstance(chosen, dict):
        raise ValueError("Invalid preset variants")
    overrides = variation_overrides or {}
    if not isinstance(overrides, dict):
        raise ValueError("Variation overrides must be a mapping")
    axes = spec["variation_axes"]
    choices = {axis: value["default"] for axis, value in axes.items()}
    for provided in (chosen, overrides):
        for axis, value in provided.items():
            if axis not in axes or not isinstance(value, str) or value not in axes[axis]["options"]:
                raise ValueError(f"Unsupported variation: {axis}={value}")
            choices[axis] = value
    relative = path.relative_to(root).as_posix()
    return {
        "style_id": style_id,
        "version": spec["version"],
        "name": spec["name"],
        "status": spec["status"],
        "approved": spec["status"] in ("approved", "locked"),
        "preset_id": preset_id,
        "variation": choices,
        "overrides": dict(overrides),
        "definition_path": relative,
        "source_of_truth": spec["source_of_truth"],
        "references": [r["id"] for r in spec["references"]],
    }
