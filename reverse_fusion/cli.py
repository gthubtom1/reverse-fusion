from __future__ import annotations

import argparse
import json
import os
import platform
import re
import shutil
import sys
from pathlib import Path
from typing import Any

from . import __version__
from .adapters import CraftAdapter, LocalBoundedWorker, spec_pointer
from .builder import HostBuilder
from .case_bridge import (
    _reverse_intent,
    build_case_pointer,
    dry_run_route,
    load_case_record,
    locate_reverse_root,
    record_case_pointer,
    resolve_case_root,
    workflow_contract,
    request_intent,
    discover_open_cases,
)
from .contracts import ContractError, check_contracts, read_json, sha256_file
from .host import adapter_plan, detect_hosts, read_handshake_record, probe_hosts
from .vertical import correct_candidate, evaluate_console, wrong_candidate
from .wasm_vertical import evaluate_wasm
from .session_builder import prepare_session, check_session
from .global_adapter import install_global_adapter, remove_global_adapter, adapter_paths
from .component_status import component_status, core_deployment
from .craft_native import prepare_native, invoke_native
from .workflow import component_entries, inspect_workflow
from .file_updates import atomic_write, file_transaction
from .project_adapter import connect_project
from .differential import compare_processes
from .rea_runner import run_rea

ROOT = Path(__file__).resolve().parents[1]
MANIFEST = ROOT / "components" / "official" / "manifest.json"
PROFILES = ROOT / "profiles"


def _print(value: Any, fmt: str) -> None:
    if fmt == "json":
        # JSON is also piped between Windows processes whose default code pages
        # can differ. Escapes preserve every Unicode path without requiring the
        # caller to set PYTHONIOENCODING or -X utf8.
        print(json.dumps(value, ensure_ascii=True, indent=2, sort_keys=True))
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


def cmd_workflow(args: argparse.Namespace) -> int:
    result = inspect_workflow(ROOT, _project_root(args), case_root=args.case_root, receipt=args.receipt)
    _print(result, args.format)
    return 0 if result['status'] == 'context-resolved' else 2


def cmd_connect(args: argparse.Namespace) -> int:
    result = connect_project(ROOT, _project_root(args), client=args.client, apply=args.apply, remove=args.remove)
    _print(result, args.format)
    return 0


def cmd_compare(args: argparse.Namespace) -> int:
    result = compare_processes(_project_root(args), args.plan, args.output)
    _print(result, args.format)
    return 0 if result['status'] == 'pass' else 1 if result['status'] == 'fail' else 2


def cmd_rea_run(args: argparse.Namespace) -> int:
    result = run_rea(ROOT, _project_root(args), operation=args.operation, arguments=args.args_file,
                     output=args.output, timeout=args.timeout, memory_mb=args.memory_mb)
    _print(result, args.format)
    return 0 if result['execution_status'] == 'returned' else 2


def cmd_release(args: argparse.Namespace) -> int:
    from .release import check_release
    result = check_release(ROOT, deployed=args.deployed)
    _print(result, args.format)
    return 0 if result['status'] == 'ready' else 2


def cmd_plan(args: argparse.Namespace) -> int:
    contract = check_contracts(ROOT)
    if contract["status"] != "pass":
        _print({"operation": "plan", "status": "blocked", "reason": "repository contracts failed", "checks": contract["checks"]}, args.format)
        return 2
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
    components = component_status(ROOT)
    result = {
        "schema_version": 1,
        "project": "reverse-fusion",
        "operation": "doctor",
        "status_scope": "repository-contracts-only; component presence and target acceptance are separate",
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
        "components": components,
        "core_deployment": core_deployment(components),
    }
    _print(result, args.format)
    return 0 if result["status"] == "pass" else 1


def cmd_handoff(args: argparse.Namespace) -> int:
    handoff = ROOT / "docs" / "CURRENT-STATE.md"
    required = ("Stage:", "Status:", "Next", "Acceptance")
    text = handoff.read_text(encoding="utf-8") if handoff.is_file() else ""
    missing = [marker for marker in required if marker.lower() not in text.lower()]
    for relative in ("docs/AGENT-BOOTSTRAP.md", "AGENTS.md", "SOURCE-MANIFEST.json", "components/official/manifest.json"):
        if not (ROOT / relative).is_file():
            missing.append(relative)
    contract = check_contracts(ROOT)
    result = {"operation": "handoff", "status": "pass" if handoff.is_file() and not missing and contract["status"] == "pass" else "fail", "file": str(handoff), "missing": missing, "contracts": contract["status"]}
    _print(result, args.format)
    return 0 if result["status"] == "pass" else 1


def _project_root(args: argparse.Namespace) -> Path:
    """Task output belongs to the caller's project, not the installed package."""
    root = Path(args.project_root).expanduser().resolve() if args.project_root else Path.cwd().resolve()
    if not root.is_dir():
        raise ValueError(f"Project root does not exist: {root}")
    return root


def _write_state(name: str, payload: dict[str, Any], *, root: Path | None = None) -> None:
    state = (root or ROOT) / "state"
    target = _state_path(name, root=root)
    state.mkdir(exist_ok=True)
    atomic_write(target, (json.dumps(payload, ensure_ascii=False, indent=2, sort_keys=True) + "\n").encode('utf-8'))


def _state_path(name: str, *, root: Path | None = None) -> Path:
    base = (root or ROOT).resolve()
    target = base / 'state' / f'{name}.json'
    if not target.resolve().is_relative_to(base):
        raise ValueError('State path escapes the repository or selected project')
    return target


def cmd_install(args: argparse.Namespace) -> int:
    contract = check_contracts(ROOT)
    if contract["status"] != "pass":
        _print({"operation": "install", "status": "blocked", "reason": "repository contracts failed", "checks": contract["checks"]}, args.format)
        return 2
    deployment = core_deployment(component_status(ROOT))
    if args.apply and deployment['status'] != 'installed':
        _print({'operation': 'install', 'status': 'blocked', 'core_deployment': deployment,
                'reason': 'Required components are missing; run scripts/bootstrap-core.ps1 before deploying the global adapter'}, args.format)
        return 2
    enable_global_adapter = args.global_adapter if args.global_adapter is not None else args.client == "codex"
    if enable_global_adapter and args.client != 'codex':
        raise ValueError('The global Codex adapter requires --client codex')
    adapter_preview = {
        "enabled": bool(enable_global_adapter),
        "skill": str(adapter_paths()["skill"]),
        "agents": str(adapter_paths()["agents"]),
        "repository": str(ROOT.resolve()),
    } if enable_global_adapter else {"enabled": False}
    plan = {
        "operation": "install",
        "mode": "apply" if args.apply else "dry-run",
        "project": "reverse-fusion",
        "host": {"client": args.client, **detect_hosts()},
        "effects": (["write repository state/install.json", "write user-level Codex adapter"] if args.apply and enable_global_adapter else ["write repository state/install.json"] if args.apply else ["read repository files only"]),
        "global_adapter": adapter_preview,
        "global_config_mutation": bool(args.apply and enable_global_adapter),
        "status": "ready",
        "core_deployment": deployment,
    }
    if args.apply:
        path = _state_path("install")  # Validate before any user-level writes.
        with file_transaction([*adapter_paths().values(), path]):
            if enable_global_adapter:
                plan["global_adapter"] = install_global_adapter(ROOT)
            elif path.is_file():
                previous = read_json(path)
                previous_adapter = previous.get('global_adapter')
                if isinstance(previous_adapter, dict) and previous_adapter.get('enabled'):
                    removal = remove_global_adapter(repo_root=ROOT)
                    plan['global_config_mutation'] = bool(removal.get('removed'))
                    plan['effects'].append('remove this checkout user-level adapter')
            plan["status"] = "installed"
            _write_state("install", {**plan, "installed": True, "version": __version__})
    _print(plan, args.format)
    return 0


def cmd_uninstall(args: argparse.Namespace) -> int:
    path = _state_path("install")
    adapter = {"enabled": False, "removed": []}
    if args.apply and path.exists():
        with file_transaction([*adapter_paths().values(), path]):
            prior = read_json(path)
            adapter_state = prior.get("global_adapter") if isinstance(prior, dict) else None
            if isinstance(adapter_state, dict) and adapter_state.get("enabled"):
                adapter = remove_global_adapter(repo_root=ROOT)
            path.unlink()
    result = {"operation": "uninstall", "mode": "apply" if args.apply else "dry-run", "status": "uninstalled" if args.apply else "ready", "state_file": str(path), "venv": str(ROOT / ".venv"), "vendor": "retained; remove explicitly if a provider asset is no longer wanted", "global_adapter": adapter, "global_config_mutation": bool(adapter.get("removed"))}
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
    result.update({"operation": "accept", "fixture": args.fixture, "candidate_kind": args.candidate,
                   "assessment_scope": "synthetic-console-fixture-only; no native REA or user target acceptance"})
    if args.record:
        _write_state("acceptance", result)
    _print(result, args.format)
    return 0 if result["status"] == "pass" else (2 if result["status"] == "unknown" else 1)


def cmd_bridge(args: argparse.Namespace) -> int:
    project = _project_root(args)
    explicit_case = args.case_root is not None
    args.case_root = args.case_root or 'work/current-case'
    # normal-dev is host-native by default.  Reverse is activated only by an
    # explicit reverse/analysis/reconstruction request, so a frontend or API
    # implementation task is not silently claimed by a security route.
    intent = request_intent(args.hint)
    original_intent = request_intent(args.user_request or args.hint)
    effective_mode = args.mode
    if args.mode == 'normal-dev':
        if intent == 'follow-up':
            cases = discover_open_cases(project)
            requested = resolve_case_root(project, args.case_root)
            if explicit_case and (requested / 'case.json').is_file():
                effective_mode = 'follow-up'
            elif len(cases) == 1:
                args.case_root = cases[0]
                effective_mode = 'follow-up'
            elif len(cases) > 1:
                _print({'operation': 'case-bridge', 'status': 'needs-case-selection',
                        'cases': cases, 'project_root': str(project),
                        'next_action': 'Read the project cases and recent conversation to identify the intended target; ask a plain target question only if it remains ambiguous.'}, args.format)
                return 2
        elif intent in {'analysis', 'reconstruction'} or original_intent in {'analysis', 'reconstruction'}:
            effective_mode = 'analysis'
    if effective_mode == "normal-dev":
        result = {
            "operation": "case-bridge",
            "status": "host-native",
            "source": "host",
            "mode": effective_mode,
            "workflow": workflow_contract({}, "normal-dev"),
            "activation_required": "use --mode analysis or --mode reconstruction when Reverse is requested",
            "recorded": False,
            "project_root": str(project),
            "repository_root": str(ROOT),
        }
        _print(result, args.format)
        return 0

    existing = None
    objective = 'reconstruction' if original_intent == 'reconstruction' or effective_mode == 'reconstruction' else 'analysis'
    if effective_mode != 'follow-up':
        try:
            candidate_case = resolve_case_root(project, args.case_root)
            if (candidate_case / 'case.json').is_file():
                existing = load_case_record(project, args.case_root)
        except ValueError as exc:
            _print({'operation': 'case-bridge', 'status': 'blocked', 'reason': str(exc)}, args.format)
            return 2
    if effective_mode == "follow-up":
        try:
            existing = load_case_record(project, args.case_root)
        except ValueError as exc:
            _print({"operation": "case-bridge", "status": "blocked", "reason": str(exc)}, args.format)
            return 2
        if existing is None:
            _print({"operation": "case-bridge", "status": "blocked", "reason": "follow-up requires an existing open case.json", "case_root": args.case_root}, args.format)
            return 2
        if args.primary is None:
            prior_primary = existing["pointer"]["primary"]
            match = re.search(r"(?:^|/)R\d+\.md$", prior_primary)
            if match:
                args.primary = match.group(0).split("/")[-1][:-3]

    route = dry_run_route(args.hint, source=args.source, primary=args.primary)
    routed = route.get("status") in {"local-route-pass", "external-route-pass"}
    owner = "reverse-fusion.local-router" if route.get("source") == "local" else "reverse.native-router"
    try:
        case_root = resolve_case_root(project, args.case_root)
    except ValueError as exc:
        _print({"operation": "case-bridge", "status": "blocked", "reason": str(exc)}, args.format)
        return 2
    prior_workflow = existing['pointer'].get('workflow', {}) if existing else {}
    if effective_mode != 'reconstruction' and original_intent != 'reconstruction':
        objective = prior_workflow.get('objective', 'reconstruction' if prior_workflow.get('stage') == 'reconstruction' else objective)
    original_request = prior_workflow.get('user_request', args.user_request or args.hint)
    if objective == 'reconstruction' and not route.get('next_stage') and route.get('primary_id') != 'R46':
        # Domain refinement changes the evidence question, not the final goal.
        next_stage = prior_workflow.get('next_stage') or dry_run_route('reconstruct target', source=args.source).get('next_stage')
        route = {**route, 'next_stage': next_stage}
    workflow = workflow_contract(route, effective_mode, follow_up=existing is not None,
                                 objective=objective, user_request=original_request)
    if effective_mode == 'follow-up' and prior_workflow:
        # Resuming a reconstruction must not discard its specification and
        # verification obligations just because this turn is called follow-up.
        workflow = {**prior_workflow, 'objective': objective, 'user_request': original_request, "mode": "follow-up"}
    from .session_builder import _inside
    project_refs = []
    for name in args.ref:
        path = _inside(project, name)
        if not path.is_file():
            raise ValueError(f'Carry-forward reference is not a file: {name}')
        project_refs.append('project:' + path.relative_to(project).as_posix())
    pointer = build_case_pointer(
        case_root.relative_to(project),
        route.get("primary") or "unresolved",
        effective_mode,
        delta=[f"route resolved by {route.get('source', 'unknown')} router" if routed else 'route unresolved', f'Current request: {args.hint}'],
        refs=list(dict.fromkeys([*(existing['pointer']['carry_forward_refs'] if existing else []), *project_refs, owner, *route.get("required_reads", []), *[str(item.get("skill")) for item in route.get("related_routes", []) if isinstance(item, dict) and item.get("skill")]])),
        route_owner=owner,
        route_source=route.get("source", "unknown"),
        workflow=workflow,
    )
    result = {
        "operation": "case-bridge",
        "repository_root": str(ROOT),
        "project_root": str(project),
        "route": route,
        "mode": effective_mode,
        "requested_mode": args.mode,
        "workflow": workflow,
        "resume": existing["pointer"] if existing is not None else None,
        "pointer": pointer.to_dict(),
        "recorded": False,
    }
    reference_root = locate_reverse_root() if route.get("source") == "external" else ROOT
    # Route refs are relative to the skill checkout, never to the caller's cwd.
    reads = list(route.get("required_reads", []))
    for related in route.get("related_routes", []):
        reads.extend(related.get("required_reads", []))
    if route.get("next_stage"):
        reads.extend(route["next_stage"].get("required_reads", []))
        if route["next_stage"].get("skill"):
            reads.append(route["next_stage"]["skill"])
    result["required_read_paths"] = [str((reference_root / name).resolve()) for name in dict.fromkeys(reads)] if reference_root else []
    result["execution_guide"] = str(ROOT / "docs" / "CROSS-PROJECT-WORKFLOW.md")
    result['agent_guide'] = str(ROOT / 'docs/AGENT-WORKFLOW.md')
    result['delivery_objective'] = objective
    result['required_read_paths'].append(result['agent_guide'])
    result['component_entries'] = component_entries(ROOT, project)
    result["business_acceptance"] = "not-performed"
    if workflow['stage'] == 'reconstruction':
        result['implementation_gate'] = {
            'status': 'not-assessed',
            'next_step': 'official Spec workflow, then native-craft prepare with frozen lease, --case-root, --handoff-manifest and --review-file; see docs/NATIVE-COMPONENTS.md',
            'boundary': 'reconstruction is the requested workflow, not a finding that analysis is complete',
        }
    result["next_action"] = (
        "Resume the recorded case, original user objective, evidence and unresolved work; retain the identified technology and investigate only what the next decision requires."
        if existing else
        "Identify the original target and actual technology, preserve the user's delivery objective, and collect evidence about behavior and dependencies before preparing implementation tasks. Read agent_guide; a reconstruction request starts with analysis, not candidate coding."
    )
    if args.record and routed:
        result["case_file"] = str(record_case_pointer(project, pointer))
        result["recorded"] = True
    _print(result, args.format)
    return 0 if routed else 2


def cmd_craft(args: argparse.Namespace) -> int:
    project = _project_root(args)
    source = (project / args.source).resolve()
    worker = LocalBoundedWorker(project)
    result = worker.run(
        source=source,
        output_relative=args.output,
        tasks=args.tasks,
        research_ref=args.research_ref,
        model_id=args.model_id,
    )
    result.update({"operation": "craft", "source": str(source), "backend": "local-bounded-worker"})
    if args.record:
        _write_state("craft-candidate", result, root=project)
    _print(result, args.format)
    return 0 if result["disposition"] == "candidate" else 2


def cmd_build(args: argparse.Namespace) -> int:
    project = _project_root(args)
    workspace = (project / args.workspace).resolve()
    try:
        workspace.relative_to(project)
    except ValueError:
        _print({"operation": "build", "status": "blocked", "reason": "workspace must stay inside the selected project"}, args.format)
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
        _write_state("host-builder", result, root=project)
    _print(result, args.format)
    return 0 if result["disposition"] == "candidate" else 2


def cmd_session(args: argparse.Namespace) -> int:
    try:
        project = _project_root(args)
        if args.phase == "prepare":
            result = prepare_session(project, workspace=args.workspace, receipt=args.receipt,
                                     tasks=args.tasks, task_files=args.task_file,
                                     research_files=args.research_file, allowed_outputs=args.allowed_output,
                                     case_root=args.case_root, handoff_manifest=args.handoff_manifest,
                                     review_file=args.review_file, requirements=args.requirement)
        else:
            result = check_session(project, receipt=args.receipt, phase=args.phase)
    except (ValueError, OSError, KeyError, TypeError) as exc:
        result = {"operation": "session", "status": "blocked", "reason": str(exc)}
    _print(result, args.format)
    return 2 if result["status"] == "blocked" else 0


def cmd_native_craft(args: argparse.Namespace) -> int:
    project = _project_root(args)
    if args.phase != 'capabilities' and not args.lease:
        raise ValueError('Native operation requires its frozen --lease')
    if args.phase == 'prepare':
        result = prepare_native(project, lease=args.lease, workspace=args.workspace, receipt=args.receipt,
                                tasks=args.tasks, task_files=args.task_file, research_files=args.research_file,
                                allowed_outputs=args.allowed_output, check_commands=args.check_command,
                                command_timeout_seconds=args.command_timeout, case_root=args.case_root,
                                handoff_manifest=args.handoff_manifest, review_file=args.review_file,
                                requirements=args.requirement)
    else:
        params = {}
        if args.params_file:
            from .session_builder import _inside
            params = json.loads(_inside(project, args.params_file).read_text(encoding='utf-8-sig'))
        result = invoke_native(project, lease=args.lease, operation=args.phase, params=params)
    _print(result, args.format)
    if args.phase == 'check' and result.get('data', {}).get('output', {}).get('result', {}).get('succeeded') is False:
        return 1
    return 0


def cmd_handshake(args: argparse.Namespace) -> int:
    result = probe_hosts(ROOT, client=args.client, timeout_seconds=args.timeout)
    if args.record:
        _write_state("host-handshakes", result)
    _print(result, args.format)
    if result.get("status") == "blocked":
        return 2
    statuses = [item.get("status") for item in result.get("probes", [])]
    if statuses == ["pass"]:
        return 0
    if any(status in {"failed", "unknown"} for status in statuses):
        return 1
    return 2


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="reverse-fusion", description="Reverse Fusion evidence-driven reconstruction entry")
    sub = parser.add_subparsers(dest="command", required=True)
    for name, fn in (("contracts", cmd_contracts), ("rea-run", cmd_rea_run), ("compare", cmd_compare), ("connect", cmd_connect), ("release-check", cmd_release), ("workflow", cmd_workflow), ("doctor", cmd_doctor), ("plan", cmd_plan), ("handoff", cmd_handoff), ("install", cmd_install), ("uninstall", cmd_uninstall), ("update", cmd_update), ("accept", cmd_accept), ("bridge", cmd_bridge), ("craft", cmd_craft), ("native-craft", cmd_native_craft), ("build", cmd_build), ("session", cmd_session), ("handshake", cmd_handshake)):
        p = sub.add_parser(name)
        p.add_argument("--format", choices=("json", "markdown"), default="json")
        if name in {"rea-run", "compare", "connect", "bridge", "workflow", "session", "build", "craft", "native-craft"}:
            p.add_argument("--project-root", help="task project directory; defaults to the current working directory, not the tool checkout")
        if name == 'connect':
            p.add_argument('--client', choices=('codex', 'pi', 'claude'), required=True)
            p.add_argument('--apply', action='store_true')
            p.add_argument('--remove', action='store_true', help='remove only this checkout project pointer, preserve other content')
        if name == 'compare':
            p.add_argument('--plan', required=True, help='reviewed project-relative JSON argv/stdin comparison plan')
            p.add_argument('--output', required=True, help='new project-relative directory for immutable observations')
        if name == 'rea-run':
            p.add_argument('--operation', required=True)
            p.add_argument('--args-file', required=True, help='project-relative JSON argument array for the actual official operation')
            p.add_argument('--output', required=True, help='new project-relative raw output/telemetry directory')
            p.add_argument('--timeout', type=int, default=180)
            p.add_argument('--memory-mb', type=int, default=2048)
        if name == 'release-check':
            p.add_argument('--deployed', action='store_true', help='also inspect installed core identities, receipt and managed Codex entry; never execute a target')
        if name == 'workflow':
            p.add_argument('--case-root', help='existing case; default the unique local open case')
            p.add_argument('--receipt', help='optional existing project-relative frozen session to inspect without changing it')
        if name == "handoff":
            p.add_argument("--check", action="store_true")
        if name == "plan":
            p.add_argument("--client", choices=("codex", "pi", "claude"), required=True)
            p.add_argument("--intent", choices=("normal-dev", "analysis", "reconstruction", "follow-up"), default="normal-dev")
            p.add_argument("--profile")
        if name in {"install", "uninstall", "update"}:
            p.add_argument("--apply", action="store_true", help="apply lifecycle changes; Codex install/uninstall also manages the user adapter")
        if name == "install":
            p.add_argument("--client", choices=("codex", "pi", "claude"), required=True)
            p.add_argument("--global-adapter", dest="global_adapter", action="store_true", default=None, help="install the user-level Codex adapter (default for codex)")
            p.add_argument("--no-global-adapter", dest="global_adapter", action="store_false", help="skip the user-level Codex adapter")
        if name == "accept":
            p.add_argument("--fixture", choices=("console", "wasm"), default="console")
            p.add_argument("--candidate", choices=("correct", "wrong", "missing"), default="correct")
            p.add_argument("--record", action="store_true")
            p.add_argument("argv", nargs="*")
        if name == "bridge":
            p.add_argument("--hint", required=True)
            p.add_argument("--case-root", help="project-relative case; default work/current-case, or the unique existing case for a continuation")
            p.add_argument('--user-request', help='original user request when first recording after a separate read-only technical route probe')
            p.add_argument('--ref', action='append', default=[], help='existing project-relative scope/workitems/evidence reference to carry forward without duplicating its content')
            p.add_argument("--mode", choices=("analysis", "reconstruction", "follow-up", "normal-dev"), default="normal-dev")
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
            p.add_argument("--host", choices=("codex", "pi", "claude"), required=True)
            p.add_argument("--workspace", default="state/host-build")
            p.add_argument("--output", required=True, help="workspace-relative candidate output")
            p.add_argument("--allowed-output", action="append", default=[])
            p.add_argument("--tasks", nargs="+", required=True)
            p.add_argument("--research-ref", required=True)
            p.add_argument("--baseline-sha256", required=True)
            p.add_argument("--prompt", required=True)
            p.add_argument("--timeout", type=int, default=180)
            p.add_argument("--record", action="store_true")
        if name == "session":
            p.add_argument('--requirement', action='append', default=[], help='explicit reviewed batch FR subset; selected task lines must map exactly; full spec and deferred work retained')
            p.add_argument("phase", choices=("prepare", "check", "refine", "finish"))
            p.add_argument("--receipt", default="state/current-builder-session.json")
            p.add_argument("--workspace", default="state/current-candidate")
            p.add_argument("--tasks", nargs="+", default=[])
            p.add_argument("--task-file", action="append", default=[])
            p.add_argument("--research-file", action="append", default=[])
            p.add_argument("--allowed-output", action="append", default=[])
            p.add_argument("--case-root", help="bind reconstruction prepare to its recorded case and checked handoff")
            p.add_argument("--handoff-manifest", help="project-relative existing reconstruction handoff manifest")
            p.add_argument("--review-file", help="project-relative independent semantic review record; not machine proof")
        if name == 'native-craft':
            p.add_argument('--requirement', action='append', default=[], help='explicit reviewed batch FR subset; full spec and deferred work retained')
            p.add_argument('phase', choices=('capabilities', 'prepare', 'build', 'check', 'refine', 'return_summary', 'cleanup', 'abort'))
            p.add_argument('--lease')
            p.add_argument('--params-file', help='project-relative JSON for the real native tool')
            p.add_argument('--workspace', default='work/native-craft')
            p.add_argument('--receipt', default='work/native-craft-session.json')
            p.add_argument('--tasks', nargs='+', default=[])
            p.add_argument('--task-file', action='append', default=[])
            p.add_argument('--research-file', action='append', default=[])
            p.add_argument('--allowed-output', action='append', default=[])
            p.add_argument('--check-command', action='append', default=[])
            p.add_argument('--command-timeout', type=int, default=60)
            p.add_argument('--case-root')
            p.add_argument('--handoff-manifest')
            p.add_argument('--review-file')
        if name == "handshake":
            p.add_argument("--client", choices=("codex", "pi", "claude"), required=True)
            p.add_argument("--timeout", type=int, default=45)
            p.add_argument("--record", action="store_true")
        p.set_defaults(handler=fn)
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    try:
        return args.handler(args)
    except (ValueError, OSError) as exc:
        _print({'operation': args.command, 'status': 'blocked', 'reason': str(exc)}, args.format)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())

