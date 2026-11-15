"""Reverse route and case bridge.

The repository-owned router is the default and works in a fresh clone.  An
installed reverse-skill router remains an optional read-only external source;
the two outcomes are kept distinct in the returned contract.
"""
from __future__ import annotations

import json
import os
import platform
import re
import subprocess
import sys
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any

from importlib.util import module_from_spec, spec_from_file_location

from .contracts import is_safe_relative_path


@dataclass(frozen=True)
class CasePointer:
    case_root: str
    route_owner: str
    primary: str
    mode: str
    decision_delta: list[str]
    carry_forward_refs: list[str]
    route_source: str = "local"
    workflow: dict[str, Any] | None = None

    def to_dict(self) -> dict[str, Any]:
        value = asdict(self)
        if self.workflow is None:
            value.pop("workflow", None)
        return value


def resolve_case_root(repo_root: Path, case_root: str) -> Path:
    candidate = (repo_root / case_root).resolve()
    try:
        candidate.relative_to(repo_root.resolve())
    except ValueError as exc:
        raise ValueError("case root must stay inside the repository") from exc
    return candidate


def record_case_pointer(repo_root: Path, pointer: CasePointer) -> Path:
    case_root = resolve_case_root(repo_root, pointer.case_root)
    case_root.mkdir(parents=True, exist_ok=True)
    path = case_root / "case.json"
    if not path.resolve().is_relative_to(repo_root.resolve()):
        raise ValueError('Case record path escapes the repository')
    history: list[dict[str, Any]] = []
    revision = 1
    if path.is_file():
        try:
            previous = json.loads(path.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError) as exc:
            raise ValueError(f"existing case record is unreadable: {exc}") from exc
        if not isinstance(previous, dict) or set(previous) - {"schema_version", "status", "revision", "history", "pointer"}:
            raise ValueError("existing case record is malformed")
        if type(previous.get("schema_version")) is not int or previous.get("schema_version") != 1 or previous.get("status") != "open":
            raise ValueError("existing case record has an invalid schema or status")
        prior_pointer = previous.get("pointer")
        _validate_pointer(prior_pointer, "existing case pointer")
        if resolve_case_root(repo_root, prior_pointer["case_root"]) != case_root:
            raise ValueError("existing case pointer belongs to another case root")
        prior_revision = previous.get("revision", 1)
        if isinstance(prior_revision, bool) or not isinstance(prior_revision, int) or prior_revision < 1:
            raise ValueError("existing case record has an invalid revision")
        prior_history = previous.get("history", [])
        if not isinstance(prior_history, list):
            raise ValueError("existing case record has invalid history")
        for index, item in enumerate(prior_history):
            if not isinstance(item, dict) or set(item) != {"revision", "pointer"}:
                raise ValueError(f"existing case history[{index}] is malformed")
            item_revision = item.get("revision")
            if isinstance(item_revision, bool) or not isinstance(item_revision, int) or item_revision < 1:
                raise ValueError(f"existing case history[{index}] has an invalid revision")
            _validate_pointer(item.get("pointer"), f"existing case history[{index}] pointer")
            if resolve_case_root(repo_root, item["pointer"]["case_root"]) != case_root:
                raise ValueError(f"existing case history[{index}] belongs to another case root")
        if [item["revision"] for item in prior_history] != list(range(1, prior_revision)):
            raise ValueError("existing case history revisions are not contiguous")
        history = list(prior_history)
        history.append({"revision": prior_revision, "pointer": prior_pointer})
        revision = prior_revision + 1
    record = {
        "schema_version": 1,
        "status": "open",
        "revision": revision,
        "history": history,
        "pointer": pointer.to_dict(),
    }
    path.write_text(json.dumps(record, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return path


def _validate_pointer(value: Any, label: str) -> None:
    required = {"case_root", "route_owner", "primary", "mode", "decision_delta", "carry_forward_refs", "route_source"}
    if not isinstance(value, dict) or set(value) not in (required, required | {"workflow"}):
        raise ValueError(f"{label} is malformed")
    for key in required - {"decision_delta", "carry_forward_refs"}:
        if not isinstance(value.get(key), str):
            raise ValueError(f"{label}.{key} must be a string")
    if value["mode"] not in {"analysis", "reconstruction", "follow-up", "normal-dev"}:
        raise ValueError(f"{label}.mode is invalid")
    for key in ("decision_delta", "carry_forward_refs"):
        items = value.get(key)
        if not isinstance(items, list) or any(not isinstance(item, str) for item in items):
            raise ValueError(f"{label}.{key} must be a string list")
    if "workflow" in value:
        _validate_workflow(value["workflow"], f"{label}.workflow")


def _validate_workflow(value: Any, label: str = "workflow") -> None:
    """Validate the small, machine-readable stage handoff saved with a case.

    This contract deliberately describes boundaries and references.  It does
    not force a fixed tool order or start providers on behalf of the host.
    """
    required = {
        "schema_version", "mode", "stage", "primary_route", "related_routes",
        "next_stage", "required_artifacts", "activation_required",
        "business_acceptance_boundary",
    }
    if not isinstance(value, dict) or set(value) != required:
        raise ValueError(f"{label} is malformed")
    if value["schema_version"] != 1 or value["mode"] not in {"analysis", "reconstruction", "follow-up", "normal-dev"}:
        raise ValueError(f"{label} has an invalid schema or mode")
    if value["stage"] not in {"host-native", "analysis", "reconstruction", "follow-up"}:
        raise ValueError(f"{label}.stage is invalid")
    if not isinstance(value["primary_route"], (str, type(None))):
        raise ValueError(f"{label}.primary_route must be a string or null")
    for key in ("related_routes", "required_artifacts", "activation_required", "business_acceptance_boundary"):
        if not isinstance(value[key], list) or any(not isinstance(item, (str, dict)) for item in value[key]):
            raise ValueError(f"{label}.{key} must be a list")
    if not isinstance(value["next_stage"], (dict, type(None))):
        raise ValueError(f"{label}.next_stage must be an object or null")


def workflow_contract(route: dict[str, Any], mode: str, *, follow_up: bool = False) -> dict[str, Any]:
    """Build the explicit handoff without eagerly loading downstream tools."""
    if mode == "normal-dev":
        stage = "host-native"
        artifacts = []
        activation = ["reverse only when the user explicitly requests analysis or reconstruction"]
        boundary = ["host-native development remains the owner", "no REA/Spec/Builder activation"]
    elif mode == "analysis":
        stage = "analysis"
        artifacts = ["original-evidence", "observations", "unknowns", "limitations", "conclusion"]
        activation = ["REA original Evidence", "selected domain skill"]
        boundary = ["analysis conclusions require Evidence links", "no candidate equivalence claim"]
    elif mode == "reconstruction":
        stage = "reconstruction"
        artifacts = ["original-evidence", "frozen-spec-tasks", "candidate", "build-run", "comparison", "proof", "obligation-ledger", "cleanup"]
        activation = ["REA original Evidence", "Spec tasks", "current-session Builder", "independent acceptance"]
        boundary = ["candidate is bounded by frozen tasks", "pass/fail/unknown/blocked/unsupported remain distinct"]
    else:
        stage = "follow-up"
        artifacts = ["existing-case", "prior-stage-refs", "new-observations", "updated-conclusion"]
        activation = ["load existing case.json", "resume only from recorded refs"]
        boundary = ["missing case is blocked", "do not recreate a new route silently"]
    primary = route.get("primary") or route.get("primary_id")
    return {
        "schema_version": 1,
        "mode": mode,
        "stage": stage,
        "primary_route": primary,
        "related_routes": route.get("related_routes", []),
        "next_stage": route.get("next_stage"),
        "required_artifacts": artifacts,
        "activation_required": activation,
        "business_acceptance_boundary": boundary,
    }


def _reverse_intent(hint: str) -> bool:
    return bool(re.search(
        r"逆向|反编译|脱壳|复刻|重构目标|reverse|decompil|reconstruct|replica|reimplement|re-?implement|clone.?behavior|implementation.?equivalence|obfuscat|anti[- ]?(debug|analysis|vm|hook)|packed|protected|binary analysis|apk analysis|\.exe|\.apk",
        hint or "", flags=re.IGNORECASE,
    ))


def load_case_record(repo_root: Path, case_root: str) -> dict[str, Any] | None:
    """Read and validate an existing open case for an explicit follow-up."""
    root = resolve_case_root(repo_root, case_root)
    path = root / "case.json"
    if not path.is_file():
        return None
    try:
        record = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise ValueError(f"existing case record is unreadable: {exc}") from exc
    if not isinstance(record, dict) or record.get("status") != "open":
        raise ValueError("existing case record is not open")
    pointer = record.get("pointer")
    _validate_pointer(pointer, "existing case pointer")
    return record


def locate_reverse_root() -> Path | None:
    """Locate an installed enhanced reverse-skill without writing to it."""
    explicit = os.environ.get("REVERSE_SKILL_ROOT")
    if explicit:
        candidate = Path(explicit).expanduser()
        if (candidate / "RULES.md").is_file():
            return candidate
    receipt_value = os.environ.get("REVERSE_WORKFLOW_RECEIPT")
    candidates = [Path(receipt_value)] if receipt_value else []
    root_override = os.environ.get("REVERSE_WORKFLOW_HOME")
    if root_override:
        candidates.append(Path(root_override) / ".installer" / "receipt.json")
    home = Path.home()
    if platform.system().lower() == "windows":
        candidates.append(home / "AppData" / "Local" / "reverse-workflow" / ".installer" / "receipt.json")
    else:
        candidates.extend([
            home / ".local" / "share" / "reverse-workflow" / ".installer" / "receipt.json",
            home / ".config" / "reverse-workflow" / ".installer" / "receipt.json",
        ])
    for receipt in candidates:
        if not receipt or not receipt.is_file():
            continue
        try:
            data = json.loads(receipt.read_text(encoding="utf-8"))
            candidate = Path(data["reverse"]["root"])
            if (candidate / "RULES.md").is_file():
                return candidate
        except (OSError, KeyError, TypeError, json.JSONDecodeError):
            continue
    return None


def _local_route(hint: str, primary: str | None = None) -> dict[str, Any]:
    module_path = Path(__file__).resolve().parents[1] / "components" / "reverse-core" / "router.py"
    spec = spec_from_file_location("reverse_fusion_local_router", module_path)
    if spec is None or spec.loader is None:
        return {"status": "unavailable", "source": "local", "reason": "local router module missing", "hint": hint}
    module = module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    try:
        return module.route(hint, primary=primary).to_dict()
    except (OSError, ValueError, json.JSONDecodeError) as exc:
        return {"status": "unavailable", "source": "local", "reason": str(exc), "hint": hint}


def _external_route(hint: str, reverse_root: Path | None, primary: str | None = None) -> dict[str, Any]:
    root = reverse_root or locate_reverse_root()
    if root is None:
        return {"status": "unavailable", "source": "external", "reason": "reverse-skill root not located", "hint": hint}
    ps_script = root / "skills" / "scripts" / "master-route.ps1"
    sh_script = root / "skills" / "scripts" / "master-route.sh"
    requested_primary = primary
    if ps_script.is_file() and (platform.system().lower() == "windows" or not sh_script.is_file()):
        command = ["powershell", "-NoProfile", "-File", str(ps_script), "-DryRun", "-Hint", hint]
        if requested_primary:
            command.extend(["-Primary", requested_primary])
        script = ps_script
    elif sh_script.is_file():
        command = ["bash", str(sh_script), "--dry-run", "--hint", hint]
        if requested_primary:
            command.extend(["--primary", requested_primary])
        script = sh_script
    else:
        return {"status": "unavailable", "source": "external", "reason": "native router missing", "path": str(ps_script), "hint": hint}
    try:
        completed = subprocess.run(
            command,
            cwd=str(root),
            capture_output=True,
            text=True,
            timeout=20,
            check=False,
        )
    except (OSError, subprocess.SubprocessError) as exc:
        return {"status": "unavailable", "source": "external", "reason": str(exc), "hint": hint}
    output = (completed.stdout or completed.stderr).strip()
    selected = next((line.split("->", 1)[1].strip() for line in output.splitlines() if line.startswith("PRIMARY ->")), None)
    selected_id = requested_primary
    skill = selected if isinstance(selected, str) and selected.startswith("skills/") else ""
    config_path = root / "components" / "reverse-core" / "routing.json"
    if not config_path.is_file():
        config_path = root / "skills" / "config" / "routing.json"
    try:
        routing = json.loads(config_path.read_text(encoding="utf-8-sig"))
        routes = routing.get("routes", {}) if isinstance(routing, dict) else {}
        derived_id = next(
            (route_id for route_id, route in routes.items()
             if isinstance(route, dict) and f"skills/{route.get('skill', '')}" == skill),
            None,
        )
    except (OSError, json.JSONDecodeError):
        derived_id = None
    if derived_id:
        selected_id = derived_id
    skill_available = False
    missing_support: list[str] = []
    required_reads = ["RULES.md"]
    if skill:
        required_reads.append(skill)
    for name in required_reads:
        if not is_safe_relative_path(name):
            missing_support.append(name)
            continue
        candidate = (root / name).resolve()
        try:
            candidate.relative_to(root.resolve())
        except ValueError:
            missing_support.append(name)
            continue
        if not candidate.is_file():
            missing_support.append(name)
    if skill:
        skill_available = skill not in missing_support

    # The external compatibility router predates Reverse Fusion's runtime
    # manifest. Reapply the product's hard-target context to the external
    # selected skill and check those resources in the external root; otherwise
    # an explicit fallback would silently lose anti-analysis/dynamic-Dex reads.
    hard_target = False
    runtime_path = Path(__file__).resolve().parents[1] / "components" / "reverse-core" / "runtime.json"
    try:
        runtime = json.loads(runtime_path.read_text(encoding="utf-8"))
        hard = runtime["hard_target"]
        hard_target = bool(re.search(hard["pattern"], hint, flags=re.IGNORECASE))
        groups = [runtime["route_reads"].get(selected_id, [])]
        if hard_target:
            groups.extend([hard["common_reads"], hard["route_reads"].get(selected_id, [])])
        for group in groups:
            for name in group:
                if name not in required_reads:
                    required_reads.append(name)
    except (OSError, KeyError, TypeError, json.JSONDecodeError, re.error):
        hard_target = False
    for name in required_reads:
        if name in missing_support:
            continue
        if not is_safe_relative_path(name) or not (root / name).resolve().is_relative_to(root.resolve()) or not (root / name).is_file():
            missing_support.append(name)
    skill_available = bool(skill) and skill not in missing_support

    primary_mismatch = bool(requested_primary and derived_id and requested_primary != derived_id)
    routed = completed.returncode == 0 and bool(selected) and skill_available and not missing_support and not primary_mismatch
    return {
        "status": "external-route-pass" if routed else "unavailable",
        "source": "external",
        "primary": selected,
        "primary_id": selected_id,
        "skill": skill,
        "skill_available": skill_available,
        "hard_target": hard_target,
        "required_reads": required_reads,
        "missing_support": missing_support,
        "output": output,
        "returncode": completed.returncode,
        "router": str(script),
        "reason": "external router did not honor the requested primary" if primary_mismatch else None,
    }


def dry_run_route(
    hint: str,
    reverse_root: Path | None = None,
    *,
    source: str = "local",
    primary: str | None = None,
) -> dict[str, Any]:
    """Resolve a route from the requested source without creating case files.

    ``local`` is the portable default.  ``external`` is an explicit, read-only
    compatibility path for an installed reverse-skill.  ``auto`` prefers the
    repository route and never makes an external receipt a prerequisite.
    """
    if source not in {"local", "external", "auto"}:
        return {"status": "blocked", "source": source, "reason": "unsupported route source", "hint": hint}
    if source == "external":
        return _external_route(hint, reverse_root, primary=primary)
    local = _local_route(hint, primary=primary)
    if source == "auto" and local.get("status") != "local-route-pass":
        external = _external_route(hint, reverse_root, primary=primary)
        if external.get("status") == "external-route-pass":
            return external
    return local


def build_case_pointer(
    case_root: Path,
    primary: str,
    mode: str,
    *,
    delta: list[str] | None = None,
    refs: list[str] | None = None,
    route_owner: str | None = None,
    route_source: str | None = None,
    workflow: dict[str, Any] | None = None,
) -> CasePointer:
    if mode not in {"analysis", "reconstruction", "follow-up", "normal-dev"}:
        raise ValueError(f"unsupported mode: {mode}")
    inferred_source = route_source or ("external" if primary.startswith("skills/") else "local")
    inferred_owner = route_owner or ("reverse.native-router" if inferred_source == "external" else "reverse-fusion.local-router")
    if workflow is not None:
        _validate_workflow(workflow)
    return CasePointer(
        case_root=str(case_root),
        route_owner=inferred_owner,
        primary=primary,
        mode=mode,
        decision_delta=delta or [],
        carry_forward_refs=refs or [],
        route_source=inferred_source,
        workflow=workflow,
    )
