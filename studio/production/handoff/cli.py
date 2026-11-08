#!/usr/bin/env python3
"""Offline P2 handoff validate/prepare/receive commands; no network or writes."""
from __future__ import annotations
import argparse
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from contracts_cli import _read
from handoff.protocol import prepare, verify, receive


def main(argv=None):
    parser=argparse.ArgumentParser(description=__doc__)
    sub=parser.add_subparsers(dest="command",required=True)
    p=sub.add_parser("prepare")
    p.add_argument("--task",required=True)
    p.add_argument("--source",required=True)
    p.add_argument("--target-executor",required=True)
    p.add_argument("--target-branch",required=True)
    p.add_argument("--receipt-ref",required=True)
    p.add_argument("--root",default=".")
    v=sub.add_parser("verify")
    v.add_argument("--envelope",required=True)
    v.add_argument("--observation",required=True)
    r=sub.add_parser("receive")
    r.add_argument("--envelope",required=True)
    r.add_argument("--observation",required=True)
    r.add_argument("--receipt",required=True)
    r.add_argument("--root",default=".")
    args=parser.parse_args(argv)
    try:
        if args.command=="prepare":
            out=prepare(_read(args.task),_read(args.source),
                target_executor=args.target_executor,target_branch=args.target_branch,
                receipt_ref=args.receipt_ref,root=Path(args.root).resolve())
        elif args.command=="verify":
            out=verify(_read(args.envelope),observation=_read(args.observation))
        elif args.command=="receive":
            out=receive(_read(args.envelope),target_observation=_read(args.observation),
                target_receipt=_read(args.receipt),root=Path(args.root).resolve())
        else:
            raise ValueError("Unknown command")
        print(json.dumps(out,ensure_ascii=False,allow_nan=False))
        return 0
    except (ValueError,KeyError,TypeError,OSError,RecursionError):
        print("P2_INVALID_INPUT: handoff validation blocked",file=sys.stderr)
        return 2


if __name__=="__main__":
    raise SystemExit(main())
