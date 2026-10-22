#!/usr/bin/env python3
"""Brandstudio read-only route planner; no model calls, writes, or side effects."""
from __future__ import annotations

import argparse
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
CONFIG = Path(__file__).with_name("routes.json")
SLUG = re.compile(r"^[a-z0-9]+(?:-[a-z0-9]+)*$")


def plan(*, root: Path, config: dict, executor: str, brand: str,
         category: str, capabilities: set[str],
         model_id: str | None = None, model_verified: bool = False,
         requested_effort: str | None = None) -> dict:
    """Select a candidate strategy using explicitly observed runtime capabilities."""
    if category not in config["categories"]:
        raise ValueError(f"Unknown category: {category}")
    if not SLUG.fullmatch(brand):
        raise ValueError("Brand must be an exact safe slug")
    metadata = root / "brands" / brand / "brand.json"
    registered = metadata.is_file()
    if not registered and category != "new-identity":
        raise ValueError(f"Brand metadata not found: brands/{brand}/brand.json")
    if requested_effort not in (None, "instant", "medium", "high", "extra-high", "pro"):
        raise ValueError("Unsupported effort label")
    if requested_effort and executor != "chatgpt-chat":
        raise ValueError("ChatGPT thinking effort is only valid for chatgpt-chat")
    if model_verified and not model_id:
        raise ValueError("Verified model flag requires --model-id")
    supported_executors = {"codex", "opencode", "antigravity", "chatgpt-work", "chatgpt-chat"}
    if executor not in supported_executors:
        raise ValueError(f"Unknown executor: {executor}")
    selected = None
    for profile in config["profiles"]:
        if profile["executor"] not in (executor, "*"):
            continue
        if category not in profile["categories"] and "*" not in profile["categories"]:
            continue
        if profile.get("effort") and profile["effort"] != requested_effort:
            continue
        if not set(profile["requires"]).issubset(capabilities):
            continue
        selected = profile
        break
    if selected is None:
        raise ValueError("Missing fallback profile")
    production_policy = config.get("production_policies", {}).get(category, {})
    return {
        "schema_version": config["schema_version"],
        "mode": "read-only-dry-run",
        "runtime": {
            "executor": executor,
            "model_reported": model_id,
            "model_verified": model_id if model_verified else None,
            "verified_capabilities": sorted(capabilities),
            "effort_requested": requested_effort,
            "effort_verified": False,
        },
        "task": {"brand": brand, "category": category},
        "production_policy": dict(production_policy),
        "route": {
            "id": selected["id"],
            "strategy": selected["strategy"],
            "status": "candidate-not-benchmarked",
        },
        "load": [
            "AGENTS.md",
            "studio/production/BOOTSTRAP.md",
            *([f"brands/{brand}/brand.json"] if registered else []),
            ".agents/skills/brand-studio/SKILL.md",
            *config["categories"][category],
            *selected.get("references", []),
            "studio/workflow/PUBLISHING.md",
        ],
        "telemetry": {"collected": False, "run_id": None},
        "warnings": (
            ["New brand: follow identity intake/scaffolding before applications; no brand metadata exists."]
            if not registered else []
        ) + (
            ["No verified model identity; a specific model version cannot be asserted."]
            if not model_verified else []
        ) + (
            ["Limited route: some required capabilities were not verified."]
            if selected["id"] == "generic-limited-v1" else []
        ) + (
            ["Image-only access supports raster layers, not a complete editable/rendered branded carousel."]
            if selected["id"] == "chat-image-v1" and category == "instagram-carousel" else []
        ),
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--executor", required=True)
    parser.add_argument("--brand", required=True)
    parser.add_argument("--category", required=True)
    parser.add_argument("--capability", action="append", default=[])
    parser.add_argument("--model-id")
    parser.add_argument("--model-verified", action="store_true")
    parser.add_argument("--requested-effort", choices=["instant", "medium", "high", "extra-high", "pro"])
    parser.add_argument("--root", type=Path, default=ROOT)
    args = parser.parse_args()
    try:
        config = json.loads(CONFIG.read_text(encoding="utf-8"))
        result = plan(
            root=args.root, config=config, executor=args.executor,
            brand=args.brand, category=args.category,
            capabilities=set(args.capability), model_id=args.model_id,
            model_verified=args.model_verified,
            requested_effort=args.requested_effort,
        )
    except (ValueError, KeyError, OSError, json.JSONDecodeError) as exc:
        parser.error(str(exc))
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
