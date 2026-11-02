"""Brandstudio P2 source→target portable handoff, pure and fail-closed.

The caller is responsible for independently collecting actual GitHub/gitrepo
observations; this module validates *supplied evidence* and never contacts an
agent, obtains secrets, creates branches or grants creative approval.
"""
from __future__ import annotations

import json
import re
from pathlib import Path
from jsonschema import Draft202012Validator, ValidationError
from contracts.validation import validate_bundle, validate_document

_SCHEMA = Path(__file__).with_name("schema.json")
_SHA = re.compile(r"^[a-f0-9]{40}$")
_COMPONENT = re.compile(r"^[A-Za-z0-9][A-Za-z0-9._-]*$")
_SOURCES = {"github-connector", "git-remote"}


def _valid_branch(branch: str) -> bool:
    if not isinstance(branch, str) or len(branch) > 181 or ".." in branch or "//" in branch:
        return False
    return bool(all(_COMPONENT.fullmatch(p) and not p.endswith((".", ".lock"))
                    for p in branch.split("/")))


def _valid_receipt_path(path: str, output_ref: str) -> bool:
    if not isinstance(path, str) or not path.startswith(output_ref.rstrip("/") + "/"):
        return False
    if len(path) > 400 or not path.endswith(".json"):
        return False
    return bool(all(_COMPONENT.fullmatch(p) and p not in (".", "..")
                    for p in path.split("/")))


def _envelope(e: dict) -> None:
    try:
        schema = json.loads(_SCHEMA.read_text(encoding="utf-8"))
        Draft202012Validator(schema).validate(e)
    except (OSError, ValueError, ValidationError, TypeError):
        raise ValueError("Invalid handoff envelope") from None
    if not _valid_branch(e["source_branch"]) or not _valid_branch(e["target_branch"]):
        raise ValueError("Unsafe handoff branch")
    if e["source_branch"] == e["target_branch"] or e["source_executor"] == e["target_executor"]:
        raise ValueError("Separate executor and branch required")
    if not _valid_receipt_path(e["receipt_ref"], e["output_ref"]):
        raise ValueError("Unsafe handoff receipt reference")
    if e["status"] == "prepared" and (e["observed_via"] != "none" or e["target_observed_via"] != "none"):
        raise ValueError("Prepared receipt must have no claimed observation")
    if e["status"] == "source_verified" and (e["observed_via"] not in _SOURCES or e["target_observed_via"] != "none"):
        raise ValueError("Source verification evidence inconsistent")
    if e["status"] == "received" and (e["observed_via"] not in _SOURCES or e["target_observed_via"] not in _SOURCES):
        raise ValueError("Received handoff requires two observations")


def prepare(task: dict, source: dict, *, target_executor: str, target_branch: str,
            receipt_ref: str, root: Path) -> dict:
    """Validate a task and actual source receipt, then create a PENDING handoff."""
    validate_bundle(task, None, source, None, root=root)
    head = source["head_sha"]
    if not isinstance(head, str) or not _SHA.fullmatch(head):
        raise ValueError("Source handoff requires an observed commit ID")
    if target_executor not in task["allowed_executors"] or target_executor == source["executor"]:
        raise ValueError("Target executor not allowed or not distinct")
    if not _valid_branch(target_branch) or not _valid_branch(source["branch"] or ""):
        raise ValueError("Handoff branch invalid")
    if target_branch == source["branch"]:
        raise ValueError("Cannot share source writer branch")
    if not _valid_receipt_path(receipt_ref, task["output_ref"]):
        raise ValueError("Handoff receipt must be inside task output")
    e = {
        "schema_version": 1,
        "task_id": task["task_id"],
        "source_executor": source["executor"],
        "target_executor": target_executor,
        "source_branch": source["branch"],
        "source_head_sha": head,
        "original_base_sha": task["base_sha"],
        "target_branch": target_branch,
        "output_ref": task["output_ref"],
        "receipt_ref": receipt_ref,
        "observed_via": "none",
        "target_observed_via": "none",
        "status": "prepared",
    }
    _envelope(e)
    return e


def verify(envelope: dict, *, observation: dict) -> dict:
    """Check a caller-supplied remote source HEAD observation; no GitHub requests."""
    _envelope(envelope)
    if envelope["status"] != "prepared" or not isinstance(observation, dict):
        raise ValueError("Handoff is not prepared or evidence missing")
    if (observation.get("observed_from") not in _SOURCES or
        observation.get("branch") != envelope["source_branch"] or
        observation.get("head_sha") != envelope["source_head_sha"]):
        raise ValueError("Source branch observation mismatch or stale HEAD")
    result = dict(envelope)
    result.update(status="source_verified", observed_via=observation["observed_from"])
    _envelope(result)
    return result


def receive(envelope: dict, *, target_observation: dict, target_receipt: dict, root: Path) -> dict:
    """Validate target ancestry and receipt; received != executed/rendered/approved."""
    _envelope(envelope)
    if envelope["status"] != "source_verified" or not isinstance(target_observation, dict):
        raise ValueError("Source verification missing")
    validate_document("task-receipt", target_receipt, root=root)
    if (target_receipt["task_id"] != envelope["task_id"] or
        target_receipt["base_sha"] != envelope["original_base_sha"] or
        target_receipt["executor"] != envelope["target_executor"] or
        target_receipt["branch"] != envelope["target_branch"] or
        target_receipt["head_sha"] is None):
        raise ValueError("Target receipt mismatch")
    if (target_observation.get("observed_from") not in _SOURCES or
        target_observation.get("branch") != envelope["target_branch"] or
        target_observation.get("base_sha") != envelope["source_head_sha"] or
        target_observation.get("head_sha") != target_receipt["head_sha"]):
        raise ValueError("Target branch or ancestry observation mismatch")
    result = dict(envelope)
    result.update(status="received", target_observed_via=target_observation["observed_from"])
    _envelope(result)
    return result
