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
from .adapters import CraftAdapter, LocalBoundedWorker, spec_pointer
from .builder import HostBuilder
from .case_bridge import build_case_pointer, dry_run_route, locate_reverse_root, record_case_pointer, resolve_case_root
from .contracts import ContractError, check_contracts, read_json, sha256_file
from .host import adapter_plan, detect_hosts, read_handshake_record
from .vertical import correct_candidate, evaluate_console, wrong_candidate
from .wasm_vertical import evaluate_wasm

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
        "host": {**adapter_plan(args.client), "python": platform.python_version(), "cwd": str(Path.cwd())},
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
        "host": {**detect_hosts(), "python": platform.python_version()},
        "receipt": str(ROOT / "state" / "install.json") if (ROOT / "state" / "install.json").is_file() else "not-installed",
        "reverse_root": str(locate_reverse_root()) if locate_reverse_root() else None,
        "loaded": "unverified",
        "running": "unverified",
        "accepted": "unverified",
        "handshakes": read_handshake_record(ROOT),
        "source_manifest_sha256": sha256_file(ROOT / "SOURCE-MANIFEST.json"),
        "provider_status": str(ROOT / "docs" / "PROVIDER-STATUS.md"),
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
        "host": {"client": args.client, **detect_hosts()},
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
    if args.fixture == "wasm":
        result = evaluate_wasm(ROOT, args.candidate, record_paths=args.record)
        result.update({"operation": "accept", "fixture": args.fixture})
        if args.record:
            _write_state("wasm-acceptance", result)
        _print(result, args.format)
        return 0 if result["status"] == "pass" else (2 if result["status"] == "unknown" else 1)
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
    route = dry_run_route(args.hint, source=args.source, primary=args.primary)
    routed = route.get("status") in {"local-route-pass", "external-route-pass"}
    owner = "reverse-fusion.local-router" if route.get("source") == "local" else "reverse.native-router"
    try:
        case_root = resolve_case_root(ROOT, args.case_root)
    except ValueError as exc:
        _print({"operation": "case-bridge", "status": "blocked", "reason": str(exc)}, args.format)
        return 2
    pointer = build_case_pointer(
        case_root.relative_to(ROOT),
        route.get("primary") or "unresolved",
        args.mode,
        delta=[f"route resolved by {route.get('source', 'unknown')} router"] if routed else ["route unresolved"],
        refs=[owner],
        route_owner=owner,
        route_source=route.get("source", "unknown"),
    )
    result = {"operation": "case-bridge", "route": route, "pointer": pointer.to_dict(), "recorded": False}
    if args.record and routed:
        result["case_file"] = str(record_case_pointer(ROOT, pointer))
        result["recorded"] = True
    _print(result, args.format)
    return 0 if routed else 2


def cmd_craft(args: argparse.Namespace) -> int:
    source = (ROOT / args.source).resolve()
    worker = LocalBoundedWorker(ROOT)
    result = worker.run(
        source=source,
        output_relative=args.output,
        tasks=args.tasks,
        research_ref=args.research_ref,
        model_id=args.model_id,
    )
    result.update({"operation": "craft", "source": str(source), "backend": "local-bounded-worker"})
    if args.record:
        _write_state("craft-candidate", result)
    _print(result, args.format)
    return 0 if result["disposition"] == "candidate" else 2


def cmd_build(args: argparse.Namespace) -> int:
    workspace = (ROOT / args.workspace).resolve()
    try:
        workspace.relative_to(ROOT)
    except ValueError:
        _print({"operation": "build", "status": "blocked", "reason": "workspace must stay inside this repository"}, args.format)
        return 2
    result = HostBuilder(workspace, host=args.host, timeout_seconds=args.timeout).run(
        baseline={"bundle_sha256": args.baseline_sha256},
        tasks=args.tasks,
        research_ref=args.research_ref,
        output_relative=args.output,
        prompt=args.prompt,
        allowed_outputs=args.allowed_output,
    )
    result.update({"operation": "build", "workspace": str(workspace), "model_selection": "host-owned"})
    if args.record:
        _write_state("host-builder", result)
    _print(result, args.format)
    return 0 if result["disposition"] == "candidate" else 2


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="reverse-fusion", description="Reverse Fusion evidence-driven reconstruction entry")
    sub = parser.add_subparsers(dest="command", required=True)
    for name, fn in (("contracts", cmd_contracts), ("doctor", cmd_doctor), ("plan", cmd_plan), ("handoff", cmd_handoff), ("install", cmd_install), ("uninstall", cmd_uninstall), ("update", cmd_update), ("accept", cmd_accept), ("bridge", cmd_bridge), ("craft", cmd_craft), ("build", cmd_build)):
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
            p.add_argument("--fixture", choices=("console", "wasm"), default="console")
            p.add_argument("--candidate", choices=("correct", "wrong", "missing"), default="correct")
            p.add_argument("--record", action="store_true")
            p.add_argument("argv", nargs="*")
        if name == "bridge":
            p.add_argument("--hint", required=True)
            p.add_argument("--case-root", default="work/current-case")
            p.add_argument("--mode", choices=("analysis", "reconstruction", "follow-up", "normal-dev"), default="reconstruction")
            p.add_argument("--source", choices=("local", "auto", "external"), default="local")
            p.add_argument("--primary", help="explicit local or upstream route id, for example R46")
            p.add_argument("--record", action="store_true", help="persist a repository-local case.json after route resolution")
        if name == "craft":
            p.add_argument("--source", required=True, help="repository-relative source fixture")
            p.add_argument("--output", required=True, help="repository-relative candidate output")
            p.add_argument("--tasks", nargs="+", default=["T-001"])
            p.add_argument("--research-ref", default="E-CONSOLE-001")
            p.add_argument("--model-id", default="deterministic-fixture-worker")
            p.add_argument("--record", action="store_true")
        if name == "build":
            p.add_argument("--host", choices=("auto", "codex", "pi", "claude"), default="auto")
            p.add_argument("--workspace", default="state/host-build")
            p.add_argument("--output", required=True, help="workspace-relative candidate output")
            p.add_argument("--allowed-output", action="append", default=[])
            p.add_argument("--tasks", nargs="+", required=True)
            p.add_argument("--research-ref", required=True)
            p.add_argument("--baseline-sha256", required=True)
            p.add_argument("--prompt", required=True)
            p.add_argument("--timeout", type=int, default=180)
            p.add_argument("--record", action="store_true")
        p.set_defaults(handler=fn)
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    return args.handler(args)


if __name__ == "__main__":
    raise SystemExit(main())

