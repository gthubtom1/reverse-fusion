from __future__ import annotations

import argparse
import json
import os
import platform
import sys
from pathlib import Path
from typing import Any

from . import __version__
from .contracts import check_contracts, read_json

ROOT = Path(__file__).resolve().parents[1]
MANIFEST = ROOT / "components" / "official" / "manifest.json"
PROFILES = ROOT / "profiles"


def _print(value: Any, fmt: str) -> None:
    if fmt == "json":
        print(json.dumps(value, ensure_ascii=False, indent=2, sort_keys=True))
        return
    if isinstance(value, dict):
        for key, item in value.items():
            if isinstance(item, (dict, list)):
                print(f"{key}: {json.dumps(item, ensure_ascii=False, sort_keys=True)}")
            else:
                print(f"{key}: {item}")
    else:
        print(value)


def cmd_contracts(args: argparse.Namespace) -> int:
    result = check_contracts(ROOT)
    _print(result, args.format)
    return 0 if result["status"] == "pass" else 1


def cmd_plan(args: argparse.Namespace) -> int:
    manifest = read_json(MANIFEST)
    profile = args.profile or ("normal-dev" if args.intent == "normal-dev" else args.intent)
    profile_path = PROFILES / f"{profile}.json"
    selected = read_json(profile_path)
    result = {
        "schema_version": 1,
        "project": "reverse-fusion",
        "version": __version__,
        "operation": "plan",
        "mode": "read-only",
        "client_requested": args.client,
        "intent": args.intent,
        "profile": profile,
        "host": {
            "os": platform.system().lower(),
            "arch": platform.machine().lower(),
            "python": platform.python_version(),
            "cwd": str(Path.cwd()),
        },
        "components": manifest["components"],
        "profile_settings": selected,
        "effects": ["reads repository files", "does not start provider", "does not modify host config"],
        "status": "plan-ready",
        "unverified": ["host loading", "REA MCP handshake", "Craft bounded runtime", "real target acceptance"],
    }
    _print(result, args.format)
    return 0


def cmd_doctor(args: argparse.Namespace) -> int:
    contract = check_contracts(ROOT)
    result = {
        "schema_version": 1,
        "project": "reverse-fusion",
        "operation": "doctor",
        "status": "pass" if contract["status"] == "pass" else "fail",
        "checks": contract["checks"],
        "host": {"os": platform.system().lower(), "arch": platform.machine().lower(), "python": platform.python_version()},
        "receipt": "not-installed-in-this-skeleton",
        "loaded": "unverified",
        "running": "unverified",
        "accepted": "unverified",
    }
    _print(result, args.format)
    return 0 if result["status"] == "pass" else 1


def cmd_handoff(args: argparse.Namespace) -> int:
    handoff = ROOT / "docs" / "CURRENT-STATE.md"
    result = {"operation": "handoff", "status": "pass" if handoff.is_file() else "fail", "file": str(handoff)}
    _print(result, args.format)
    return 0 if result["status"] == "pass" else 1


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="reverse-fusion", description="Reverse Fusion RF-01 static project entry")
    sub = parser.add_subparsers(dest="command", required=True)
    for name, fn in (("contracts", cmd_contracts), ("doctor", cmd_doctor), ("plan", cmd_plan), ("handoff", cmd_handoff)):
        p = sub.add_parser(name)
        p.add_argument("--format", choices=("json", "markdown"), default="json")
        if name == "handoff":
            p.add_argument("--check", action="store_true")
        if name == "plan":
            p.add_argument("--client", default="auto")
            p.add_argument("--intent", choices=("normal-dev", "analysis", "reconstruction", "follow-up"), default="analysis")
            p.add_argument("--profile")
        p.set_defaults(handler=fn)
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    return args.handler(args)


if __name__ == "__main__":
    raise SystemExit(main())

