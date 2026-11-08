#!/usr/bin/env python3
"""Offline Brandstudio P1 contract validation and advisory routing CLI."""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from advisory import propose
from contracts.states import next_state
from contracts.validation import validate_document

_MAX_BYTES = 256 * 1024
_MAX_DEPTH = 32


def _no_duplicates(pairs):
    result = {}
    for key, value in pairs:
        if key in result:
            raise ValueError("duplicate JSON keys")
        result[key] = value
    return result


def _bad_constant(_value):
    raise ValueError("nonfinite JSON number")


def _depth(item, n=0):
    if n > _MAX_DEPTH:
        raise ValueError("JSON nesting limit")
    if isinstance(item, dict):
        for value in item.values():
            _depth(value, n + 1)
    elif isinstance(item, list):
        for value in item:
            _depth(value, n + 1)


def _read(path):
    target = Path(path)
    if target.is_symlink() or any(parent.is_symlink() for parent in target.parents):
        raise ValueError("Input path uses symlink")
    with target.open("rb") as stream:
        data = stream.read(_MAX_BYTES + 1)
    if len(data) > _MAX_BYTES:
        raise ValueError("Input too large")
    try:
        document = json.loads(
            data.decode("utf-8"),
            object_pairs_hook=_no_duplicates,
            parse_constant=_bad_constant,
        )
    except (UnicodeError, ValueError, RecursionError):
        raise ValueError("Invalid JSON") from None
    _depth(document)
    return document


def run(args) -> dict:
    root = Path(args.root).resolve() if hasattr(args, "root") else Path(".").resolve()
    if args.command == "validate":
        validate_document(args.kind, _read(args.file), root=root)
        return {"mode": "v3-advisory", "kind": args.kind, "valid": True}
    if args.command == "route":
        task = _read(args.task)
        report = _read(args.report)
        config = json.loads((root / "studio" / "production" / "routes.json").read_text(encoding="utf-8"))
        return propose(task=task, report=report, root=root, config=config)
    if args.command == "transition":
        return {"mode": "v3-advisory", "state": next_state(
            args.old_state, requested=args.new_state, actor_role=args.actor,
            evidence_ref=args.evidence_ref)}
    raise ValueError("Unknown command")


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest="command", required=True)
    validate = sub.add_parser("validate")
    validate.add_argument("--kind", required=True, choices=["task","capability-report","task-receipt","output-manifest"])
    validate.add_argument("--file", required=True)
    validate.add_argument("--root", default=".")
    route = sub.add_parser("route")
    route.add_argument("--task", required=True)
    route.add_argument("--report", required=True)
    route.add_argument("--root", default=".")
    transition = sub.add_parser("transition")
    transition.add_argument("--from", dest="old_state", required=True)
    transition.add_argument("--to", dest="new_state", required=True)
    transition.add_argument("--actor", required=True)
    transition.add_argument("--evidence-ref", required=True)
    args = parser.parse_args(argv)
    try:
        print(json.dumps(run(args), ensure_ascii=False, allow_nan=False))
        return 0
    except (ValueError, OSError, TypeError, KeyError, RecursionError):
        print("P1_INVALID_INPUT: validation or advisory request blocked", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
