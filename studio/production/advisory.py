"""Read-only P1 advisory: honest capability filtering around legacy router."""
from __future__ import annotations

from pathlib import Path

from contracts.validation import validate_document
from router import plan


def propose(*, task: dict, report: dict, root: Path, config: dict) -> dict:
    """Propose a candidate route without mutating inputs or starting agents."""
    validate_document("task", task, root=root)
    validate_document("capability-report", report, root=root)
    executor = report["executor"]
    blockers = []
    if executor not in task["allowed_executors"]:
        blockers.append("executor-not-allowed")
    observed = {
        name for name, entry in report["capabilities"].items()
        if entry["status"] == "observed" and isinstance(entry["evidence_source"], str)
        and bool(entry["evidence_source"].strip())
    }
    for required in task["required_capabilities"]:
        if required not in observed:
            blockers.append("missing-observed-capability:" + required)
    candidate = None
    if not blockers:
        candidate = plan(
            root=root, config=config, executor=executor,
            brand=task["brand_slug"], category=task["category"], capabilities=observed,
            style_id=task["style_id"],
        )
        if candidate["route"]["id"] == "generic-limited-v1":
            blockers.append("route-is-capability-limited")
        if candidate["route"]["status"] != "candidate-not-benchmarked":
            blockers.append("route-has-unexpected-status")
    return {
        "mode": "v3-advisory",
        "task_id": task["task_id"],
        "eligible": not blockers,
        "blockers": blockers,
        "candidate": candidate,
    }
