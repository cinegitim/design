#!/usr/bin/env python3
"""Brandstudio Recorder v1: local private evidence -> allowlisted public summary.

No provider API calls, no GitHub writes, no automated usage measurement.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import tempfile
import uuid
from datetime import datetime, timezone
from pathlib import Path

COMMIT = re.compile(r"^[0-9a-f]{40}$")
SLUG = re.compile(r"^[a-z0-9]+(?:-[a-z0-9]+)*$")
ROUTE = re.compile(r"^[a-z0-9][a-z0-9.-]{0,79}$")
CATEGORIES = {"instagram-carousel", "social-post", "identity-application",
              "print-catalog", "web-design", "new-identity"}
EXECUTORS = {"chatgpt-chat", "chatgpt-work", "codex", "opencode", "antigravity"}
EFFORTS = {"instant", "medium", "high", "extra-high", "pro"}
EVENTS = {"repo-read", "skill-loaded", "route-selected", "tool-called",
          "source-created", "render-created", "artifact-verified",
          "pr-opened", "ci-checked", "delivery-verified", "blocked"}
STATUSES = {"planned", "blocked", "failed", "finished"}
SOURCES = {"provider-usage", "host-telemetry", "visible-ui"}
SAFE_ROOTS = {"docs", "brands", "studio"}
SCHEMA_VERSION = 1


def utcnow():
    return datetime.now(timezone.utc).isoformat(timespec="seconds")


def check_private_path(path: Path):
    if ".brandstudio-private" not in path.parts:
        raise ValueError("Private run files must be within .brandstudio-private/")
    if path.is_symlink():
        raise ValueError("Refusing a symlink run file")


def atomic_json(path: Path, document: dict, *, exclusive=False):
    path.parent.mkdir(parents=True, exist_ok=True)
    check_private_path(path) if ".brandstudio-private" in path.parts else None
    if exclusive and path.exists():
        raise ValueError("Run already exists; refusing overwrite")
    fd, tmp = tempfile.mkstemp(prefix=".recorder-", dir=str(path.parent))
    try:
        os.fchmod(fd, 0o600)
        with os.fdopen(fd, "w", encoding="utf-8") as out:
            json.dump(document, out, ensure_ascii=False, indent=2)
            out.write("\n")
            out.flush()
            os.fsync(out.fileno())
        os.replace(tmp, path)
    finally:
        if os.path.exists(tmp):
            os.unlink(tmp)


def validate(doc: dict):
    if not isinstance(doc, dict) or doc.get("schema_version") != SCHEMA_VERSION:
        raise ValueError("Unsupported recorder schema")
    if not re.fullmatch(r"bs_[a-f0-9]{32}", doc.get("run_id", "")):
        raise ValueError("Invalid run_id")
    task, origin, runtime = doc["task"], doc["origin"], doc["runtime"]
    if not SLUG.fullmatch(task["brand"]) or task["category"] not in CATEGORIES:
        raise ValueError("Invalid brand or category")
    if not COMMIT.fullmatch(origin["source_commit"]):
        raise ValueError("Missing exact source commit")
    if runtime["executor"] not in EXECUTORS:
        raise ValueError("Unsupported executor")
    if doc["status"] not in {"in_progress", *STATUSES}:
        raise ValueError("Unknown run status")
    if not ROUTE.fullmatch(doc["route"]["id"]):
        raise ValueError("Invalid route id")
    if doc["metrics"]["input_tokens"] is not None or doc["metrics"]["output_tokens"] is not None:
        if doc["metrics"]["source"] not in SOURCES:
            raise ValueError("Usage figures require a declared observation source")
    for key in ("input_tokens", "output_tokens", "cache_tokens"):
        value = doc["metrics"][key]
        if value is not None and (type(value) is not int or value < 0):
            raise ValueError("Token usage must be an observed nonnegative integer or null")
    if doc["runtime"]["model_observed_id"] is not None:
        if not doc["runtime"]["model_evidence"] or not isinstance(doc["runtime"]["model_observed_id"], str):
            raise ValueError("Observed model requires source attestation")
    delivery = doc["delivery"]
    if delivery["ci_status"] == "success" and delivery.get("checked_head_sha") != delivery["head_sha"]:
        raise ValueError("CI success must match the recorded PR head")
    for key in ("head_sha", "checked_head_sha", "merged_commit"):
        sha = delivery.get(key)
        if sha is not None and not COMMIT.fullmatch(sha):
            raise ValueError("Invalid delivery SHA")
    for artifact in doc["artifacts"]:
        safe_relative(artifact["path"])
        if not re.fullmatch(r"[a-f0-9]{64}", artifact["sha256"]):
            raise ValueError("Artifact must have a real SHA-256")
    return doc


def read_private(path: Path):
    check_private_path(path)
    with path.open(encoding="utf-8") as src:
        return validate(json.load(src))


def safe_relative(s: str):
    if not isinstance(s, str):
        raise ValueError("Invalid artifact path")
    path = Path(s)
    if path.is_absolute() or not path.parts or path.parts[0] not in SAFE_ROOTS:
        raise ValueError("Artifact must be under docs/, brands/, or studio/")
    if any(x.startswith(".") or x == ".." for x in path.parts):
        raise ValueError("Hidden or traversal paths cannot become public artifacts")
    return path


def sha256_file(path: Path):
    h = hashlib.sha256()
    with path.open("rb") as f:
        for block in iter(lambda: f.read(1024 * 1024), b""):
            h.update(block)
    return h.hexdigest()


def init(args):
    path = Path(args.file)
    check_private_path(path)
    if path.exists():
        raise ValueError("Run already exists; refusing overwrite")
    if not SLUG.fullmatch(args.brand) or args.category not in CATEGORIES:
        raise ValueError("Invalid brand/category")
    if args.executor not in EXECUTORS or not ROUTE.fullmatch(args.route):
        raise ValueError("Invalid executor/route")
    if not COMMIT.fullmatch(args.source_commit):
        raise ValueError("A verified 40-character source commit is required")
    if args.effort and args.effort not in EFFORTS:
        raise ValueError("Unknown thinking effort")
    if args.effort and args.executor != "chatgpt-chat":
        raise ValueError("Thinking effort only applies to standard ChatGPT chat")
    digest = sha256_file(Path(args.brief_file)) if args.brief_file else None
    record = {
        "schema_version": SCHEMA_VERSION,
        "run_id": "bs_" + uuid.uuid4().hex,
        "status": "in_progress",
        "origin": {"repository": "cinegitim/design", "source_commit": args.source_commit},
        "task": {"brand": args.brand, "category": args.category, "brief_sha256": digest},
        "runtime": {"executor": args.executor, "effort_requested": args.effort,
                    "model_observed_id": None, "model_evidence": None},
        "route": {"id": args.route, "strategy_version": args.strategy_version},
        "time": {"started_at": utcnow(), "ended_at": None, "wall_seconds": None},
        "metrics": {"input_tokens": None, "output_tokens": None,
                    "cache_tokens": None, "source": None},
        "events": [],
        "artifacts": [],
        "delivery": {"pr_number": None, "head_sha": None,
                     "checked_head_sha": None, "ci_status": "unverified",
                     "merged_commit": None, "attestation": None},
    }
    atomic_json(path, validate(record), exclusive=True)
    return record


def event(args):
    record = read_private(Path(args.file))
    if record["status"] != "in_progress":
        raise ValueError("Closed runs are immutable")
    record["events"].append({"kind": args.kind, "at": utcnow()})
    atomic_json(Path(args.file), validate(record))
    return record


def metrics(args):
    record = read_private(Path(args.file))
    if record["status"] != "in_progress":
        raise ValueError("Closed runs are immutable")
    figures = {k: getattr(args, k) for k in ("input_tokens", "output_tokens", "cache_tokens")}
    if all(v is None for v in figures.values()):
        raise ValueError("At least one observed metric is required")
    for k, v in figures.items():
        if v is not None:
            if v < 0:
                raise ValueError("Negative usage not permitted")
            record["metrics"][k] = v
    record["metrics"]["source"] = args.source
    atomic_json(Path(args.file), validate(record))
    return record


def model(args):
    record = read_private(Path(args.file))
    if record["status"] != "in_progress":
        raise ValueError("Closed runs are immutable")
    if not re.fullmatch(r"[A-Za-z0-9][A-Za-z0-9._:/ -]{0,119}", args.model_id):
        raise ValueError("Invalid model ID label")
    record["runtime"]["model_observed_id"] = args.model_id
    record["runtime"]["model_evidence"] = args.source
    atomic_json(Path(args.file), validate(record))
    return record


def delivery(args):
    record = read_private(Path(args.file))
    if record["status"] != "in_progress":
        raise ValueError("Closed runs are immutable")
    if args.pr_number < 1 or not COMMIT.fullmatch(args.head_sha):
        raise ValueError("Valid PR and exact head commit required")
    if args.ci_status == "success" and args.checked_head_sha != args.head_sha:
        raise ValueError("Cannot report successful CI on a different/unchecked head")
    if args.merged_commit and not COMMIT.fullmatch(args.merged_commit):
        raise ValueError("Merged commit must be a full SHA")
    record["delivery"] = {
        "pr_number": args.pr_number, "head_sha": args.head_sha,
        "checked_head_sha": args.checked_head_sha,
        "ci_status": args.ci_status, "merged_commit": args.merged_commit,
        "attestation": "reported-from-github-by-caller-not-independently-verified"
    }
    atomic_json(Path(args.file), validate(record))
    return record


def artifact(args):
    record = read_private(Path(args.file))
    if record["status"] != "in_progress":
        raise ValueError("Closed runs are immutable")
    rel = safe_relative(args.path)
    root = Path(args.root).resolve(strict=True)
    path = root / rel
    if path.is_symlink() or not path.is_file() or not path.resolve().is_relative_to(root):
        raise ValueError("No verified in-repository regular file at that path")
    if any(a["path"] == rel.as_posix() for a in record["artifacts"]):
        raise ValueError("Duplicate artifact path")
    record["artifacts"].append({"path": rel.as_posix(),
                                "sha256": sha256_file(path),
                                "evidence": "locally-hashed-file"})
    record["events"].append({"kind": "artifact-verified", "at": utcnow()})
    atomic_json(Path(args.file), validate(record))
    return record


def finish(args):
    record = read_private(Path(args.file))
    if record["status"] != "in_progress":
        raise ValueError("Closed runs are immutable")
    if args.status == "finished" and not record["artifacts"]:
        raise ValueError("Cannot finish a production run without verified artifacts")
    now = datetime.now(timezone.utc)
    first = datetime.fromisoformat(record["time"]["started_at"])
    record["time"]["ended_at"] = now.isoformat(timespec="seconds")
    record["time"]["wall_seconds"] = max(0, round((now - first).total_seconds()))
    record["status"] = args.status
    atomic_json(Path(args.file), validate(record))
    return record


def public_summary(doc):
    """Explicit allowlist: original brief, freeform logs and secrets never exported."""
    validate(doc)
    return {
        "schema_version": SCHEMA_VERSION,
        "run_id": doc["run_id"],
        "status": doc["status"],
        "source": {"repository": doc["origin"]["repository"],
                   "commit": doc["origin"]["source_commit"]},
        "task": {"brand": doc["task"]["brand"], "category": doc["task"]["category"]},
        "runtime": {"executor": doc["runtime"]["executor"],
                    "effort_requested": doc["runtime"]["effort_requested"],
                    "model_id": doc["runtime"]["model_observed_id"],
                    "model_verification": (
                        "reported-with-" + doc["runtime"]["model_evidence"]
                        if doc["runtime"]["model_evidence"] else "unavailable")},
        "route": {"id": doc["route"]["id"],
                  "strategy_version": doc["route"]["strategy_version"]},
        "timing": {"started_at": doc["time"]["started_at"],
                   "ended_at": doc["time"]["ended_at"],
                   "elapsed_wall_seconds": doc["time"]["wall_seconds"],
                   "elapsed_kind": "calendar-wall-clock-not-model-runtime"},
        "usage": dict(doc["metrics"]),
        "event_counts": {kind: sum(e["kind"] == kind for e in doc["events"])
                         for kind in sorted({e["kind"] for e in doc["events"]})},
        "artifacts": [dict(x) for x in doc["artifacts"]],
        "delivery": dict(doc["delivery"]),
    }


def main():
    p = argparse.ArgumentParser(description=__doc__)
    subs = p.add_subparsers(dest="command", required=True)
    a = subs.add_parser("init")
    a.add_argument("--file", required=True)
    a.add_argument("--brand", required=True)
    a.add_argument("--category", required=True, choices=sorted(CATEGORIES))
    a.add_argument("--executor", required=True, choices=sorted(EXECUTORS))
    a.add_argument("--route", required=True)
    a.add_argument("--strategy-version", default="v1")
    a.add_argument("--source-commit", required=True)
    a.add_argument("--effort", choices=sorted(EFFORTS))
    a.add_argument("--brief-file")
    a = subs.add_parser("event")
    a.add_argument("--file", required=True)
    a.add_argument("--kind", required=True, choices=sorted(EVENTS))
    a = subs.add_parser("metrics")
    a.add_argument("--file", required=True)
    a.add_argument("--source", required=True, choices=sorted(SOURCES))
    for name in ("input_tokens", "output_tokens", "cache_tokens"):
        a.add_argument("--" + name.replace("_", "-"), type=int)
    a = subs.add_parser("model")
    a.add_argument("--file", required=True)
    a.add_argument("--model-id", required=True)
    a.add_argument("--source", choices=["provider-metadata", "host-metadata"], required=True)
    a = subs.add_parser("delivery")
    a.add_argument("--file", required=True)
    a.add_argument("--pr-number", type=int, required=True)
    a.add_argument("--head-sha", required=True)
    a.add_argument("--checked-head-sha")
    a.add_argument("--ci-status", choices=["unverified", "pending", "failed", "success"], default="unverified")
    a.add_argument("--merged-commit")
    a = subs.add_parser("artifact")
    a.add_argument("--file", required=True)
    a.add_argument("--root", required=True)
    a.add_argument("--path", required=True)
    a = subs.add_parser("finish")
    a.add_argument("--file", required=True)
    a.add_argument("--status", required=True, choices=sorted(STATUSES))
    a = subs.add_parser("export")
    a.add_argument("--file", required=True)
    a.add_argument("--output", required=True)
    a = subs.add_parser("validate")
    a.add_argument("--file", required=True)
    args = p.parse_args()
    try:
        if args.command == "init":
            doc = init(args)
        elif args.command == "event":
            doc = event(args)
        elif args.command == "metrics":
            doc = metrics(args)
        elif args.command == "model":
            doc = model(args)
        elif args.command == "delivery":
            doc = delivery(args)
        elif args.command == "artifact":
            doc = artifact(args)
        elif args.command == "finish":
            doc = finish(args)
        else:
            doc = read_private(Path(args.file))
        if args.command == "export":
            out = Path(args.output)
            if ".brandstudio-private" in out.parts:
                raise ValueError("Public export must not overwrite a private run")
            atomic_json(out, public_summary(doc), exclusive=True)
        print(json.dumps({"ok": True, "run_id": doc["run_id"],
                          "status": doc["status"], "command": args.command},
                         ensure_ascii=False))
        return 0
    except (ValueError, OSError, KeyError, TypeError, json.JSONDecodeError) as exc:
        p.exit(2, f"Recorder error: {exc}\n")


if __name__ == "__main__":
    raise SystemExit(main())
