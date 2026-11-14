from __future__ import annotations

import argparse
import json
import os
import platform
import shutil
import sys
from pathlib import Path
from typing import Any

from . import __version__
from .adapters import CraftAdapter, spec_pointer
from .case_bridge import build_case_pointer, dry_run_route, locate_reverse_root
from .contracts import ContractError, check_contracts, read_json, sha256_file
from .vertical import correct_candidate, evaluate_console, wrong_candidate

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
        "receipt": str(ROOT / "state" / "install.json") if (ROOT / "state" / "install.json").is_file() else "not-installed",
        "reverse_root": str(locate_reverse_root()) if locate_reverse_root() else None,
        "loaded": "unverified",
        "running": "unverified",
        "accepted": "unverified",
        "source_manifest_sha256": sha256_file(ROOT / "SOURCE-MANIFEST.json"),
    }
    _print(result, args.format)
    return 0 if result["status"] == "pass" else 1


def cmd_handoff(args: argparse.Namespace) -> int:
    handoff = ROOT / "docs" / "CURRENT-STATE.md"
    required = ("Stage:", "Status:", "Next", "Acceptance")
    text = handoff.read_text(encoding="utf-8") if handoff.is_file() else ""
    missing = [marker for marker in required if marker.lower() not in text.lower()]
    result = {"operation": "handoff", "status": "pass" if handoff.is_file() and not missing else "fail", "file": str(handoff), "missing": missing}
    _print(result, args.format)
    return 0 if result["status"] == "pass" else 1


def _write_state(name: str, payload: dict[str, Any]) -> None:
    state = ROOT / "state"
    state.mkdir(exist_ok=True)
    (state / f"{name}.json").write_text(json.dumps(payload, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def cmd_install(args: argparse.Namespace) -> int:
    plan = {
        "operation": "install",
        "mode": "apply" if args.apply else "dry-run",
        "project": "reverse-fusion",
        "host": {"client": args.client, "os": platform.system().lower(), "arch": platform.machine().lower()},
        "effects": ["write repository state/install.json"] if args.apply else ["read repository files only"],
        "status": "ready",
    }
    if args.apply:
        _write_state("install", {**plan, "installed": True, "version": __version__})
        plan["status"] = "installed"
    _print(plan, args.format)
    return 0


def cmd_uninstall(args: argparse.Namespace) -> int:
    path = ROOT / "state" / "install.json"
    if args.apply and path.exists():
        path.unlink()
    result = {"operation": "uninstall", "mode": "apply" if args.apply else "dry-run", "status": "uninstalled" if args.apply else "ready", "state_file": str(path)}
    _print(result, args.format)
    return 0


def cmd_update(args: argparse.Namespace) -> int:
    result = {"operation": "update", "mode": "read-only", "status": "review-required", "source_manifest": str(ROOT / "SOURCE-MANIFEST.json"), "action": "compare upstream identities before changing any component"}
    if args.apply:
        result["mode"] = "apply"
        _write_state("update", {**result, "status": "recorded"})
        result["status"] = "recorded"
    _print(result, args.format)
    return 0


def cmd_accept(args: argparse.Namespace) -> int:
    if args.fixture != "console":
        _print({"operation": "accept", "status": "unsupported", "fixture": args.fixture}, args.format)
        return 2
    candidate = {"correct": correct_candidate, "wrong": wrong_candidate, "missing": None}[args.candidate]
    result = evaluate_console(candidate, args.argv, evidence=args.candidate != "missing").to_dict()
    result.update({"operation": "accept", "fixture": args.fixture, "candidate_kind": args.candidate})
    if args.record:
        _write_state("acceptance", result)
    _print(result, args.format)
    return 0 if result["status"] == "pass" else (2 if result["status"] == "unknown" else 1)


def cmd_bridge(args: argparse.Namespace) -> int:
    route = dry_run_route(args.hint)
    pointer = build_case_pointer(Path(args.case_root), route.get("primary") or "unresolved", args.mode, delta=["route resolved by native reverse router"] if route.get("primary") else ["route unresolved"], refs=["reverse.native-router"])
    _print({"operation": "case-bridge", "route": route, "pointer": pointer.to_dict()}, args.format)
    return 0 if route.get("status") == "routed" else 2


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="reverse-fusion", description="Reverse Fusion evidence-driven reconstruction entry")
    sub = parser.add_subparsers(dest="command", required=True)
    for name, fn in (("contracts", cmd_contracts), ("doctor", cmd_doctor), ("plan", cmd_plan), ("handoff", cmd_handoff), ("install", cmd_install), ("uninstall", cmd_uninstall), ("update", cmd_update), ("accept", cmd_accept), ("bridge", cmd_bridge)):
        p = sub.add_parser(name)
        p.add_argument("--format", choices=("json", "markdown"), default="json")
        if name == "handoff":
            p.add_argument("--check", action="store_true")
        if name == "plan":
            p.add_argument("--client", default="auto")
            p.add_argument("--intent", choices=("normal-dev", "analysis", "reconstruction", "follow-up"), default="analysis")
            p.add_argument("--profile")
        if name in {"install", "uninstall", "update"}:
            p.add_argument("--apply", action="store_true", help="write only this repository's state")
        if name == "install":
            p.add_argument("--client", default="auto")
        if name == "accept":
            p.add_argument("--fixture", choices=("console",), default="console")
            p.add_argument("--candidate", choices=("correct", "wrong", "missing"), default="correct")
            p.add_argument("--record", action="store_true")
            p.add_argument("argv", nargs="*")
        if name == "bridge":
            p.add_argument("--hint", required=True)
            p.add_argument("--case-root", default="work/current-case")
            p.add_argument("--mode", choices=("analysis", "reconstruction", "follow-up", "normal-dev"), default="reconstruction")
        p.set_defaults(handler=fn)
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    return args.handler(args)


if __name__ == "__main__":
    raise SystemExit(main())

