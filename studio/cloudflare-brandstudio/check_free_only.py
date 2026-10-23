#!/usr/bin/env python3
"""Fail closed if Brandstudio infrastructure attempts to use billable services.

Not an account-level billing cap. Cloudflare dashboards/other services remain
outside the control of the repository policy.
"""
from __future__ import annotations
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent
BANNED_BINDINGS = {
    "r2_buckets", "ai", "browser", "queues", "durable_objects",
    "vectorize", "images", "hyperdrive", "analytics_engine_datasets",
    "logpush", "pipelines", "containers", "workflows", "send_email",
}


class FreeOnlyViolation(ValueError):
    pass


def check(root: Path = ROOT) -> dict:
    policy = json.loads((root / "free-only-policy.json").read_text(encoding="utf-8"))
    cfg = json.loads((root / "wrangler.jsonc").read_text(encoding="utf-8"))
    worker = (root / "src/worker.mjs").read_text(encoding="utf-8")
    build = (root / "build_pages.py").read_text(encoding="utf-8")
    errors = []

    if policy.get("policy") != "zero-cost-or-stop":
        errors.append("Zero-cost policy disabled")
    if policy.get("storage", {}).get("r2_uploads_allowed") is not False:
        errors.append("R2 uploads must remain disabled")
    if policy.get("storage", {}).get("r2_bucket_creations_allowed") is not False:
        errors.append("R2 bucket creation must remain disabled")
    if policy.get("editor", {}).get("write_api_enabled") is not False:
        errors.append("Editor write routes cannot be enabled without authenticated free-tier review")
    if policy.get("hosting", {}).get("automatic_paid_upgrade") is not False:
        errors.append("Paid upgrade forbidden")
    if policy.get("deployment", {}).get("max_asset_bytes") != 25 * 1024 * 1024:
        errors.append("Pages max asset must be 25 MiB")
    if policy.get("deployment", {}).get("max_asset_count", 0) > 19_000:
        errors.append("Pages max asset count should have margin below 20,000")
    if policy.get("deployment", {}).get("max_output_bytes", 0) > 1_400_000_000:
        errors.append("Pages self-imposed output cap lifted")
    if policy.get("deployment", {}).get("autodeploy") != "off-until-quota-verified":
        errors.append("Enable autodeploy only after manual build quota review")

    bad = sorted(BANNED_BINDINGS.intersection(cfg.keys()))
    if bad:
        errors.append(f"Cloudflare paid/variable-cost bindings configured: {bad}")
    if "d1_databases" not in cfg or len(cfg["d1_databases"]) != 1:
        errors.append("Only the existing free D1 binding is allowed")
    if cfg.get("name") != "brandstudio-stage":
        errors.append("Unexpected Worker deployment target")
    if cfg.get("env", {}).get("production"):
        errors.append("Implicit production environment forbidden in zero-cost staging")
    if "env.R2" in worker or "env.BROWSER" in worker or "env.AI" in worker:
        errors.append("Paid service usage discovered in worker")
    if any(s in worker for s in (
        ".put(", "INSERT INTO", "UPDATE products", "DELETE FROM", "CREATE BUCKET"
    )):
        errors.append("Worker has a write primitive; manual audit required")
    if "mutations_enabled: false" not in worker or "read_only_staging" not in worker:
        errors.append("Worker no longer fail-closed read-only")
    if "MAX_BYTES = 25 * 1024 * 1024" not in build:
        errors.append("Free Pages single-file size guard removed")
    if "MAX_FILES = 19_000" not in build or "MAX_OUTPUT_BYTES = 1_400_000_000" not in build:
        errors.append("Free Pages total-size/count caps removed")
    if errors:
        raise FreeOnlyViolation("; ".join(errors))
    return {"result": "PASS", "policy": "zero-cost-or-stop",
            "paid_bindings": 0, "r2_in_use": False, "worker_writes": False,
            "note": "This is a code/deploy gate, not a Cloudflare billing guarantee."}


if __name__ == "__main__":
    print(json.dumps(check(), indent=2, ensure_ascii=False))
