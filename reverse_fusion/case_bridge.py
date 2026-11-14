"""Reverse route and case bridge.

The repository-owned router is the default and works in a fresh clone.  An
installed reverse-skill router remains an optional read-only external source;
the two outcomes are kept distinct in the returned contract.
"""
from __future__ import annotations

import json
import os
import platform
import subprocess
import sys
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any

from importlib.util import module_from_spec, spec_from_file_location


@dataclass(frozen=True)
class CasePointer:
    case_root: str
    route_owner: str
    primary: str
    mode: str
    decision_delta: list[str]
    carry_forward_refs: list[str]
    route_source: str = "local"

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


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
    record = {
        "schema_version": 1,
        "status": "open",
        "pointer": pointer.to_dict(),
    }
    path = case_root / "case.json"
    path.write_text(json.dumps(record, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return path


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


def _external_route(hint: str, reverse_root: Path | None) -> dict[str, Any]:
    root = reverse_root or locate_reverse_root()
    if root is None:
        return {"status": "unavailable", "source": "external", "reason": "reverse-skill root not located", "hint": hint}
    script = root / "skills" / "scripts" / "master-route.ps1"
    if not script.is_file():
        return {"status": "unavailable", "source": "external", "reason": "native router missing", "path": str(script), "hint": hint}
    try:
        completed = subprocess.run(
            ["powershell", "-NoProfile", "-File", str(script), "-DryRun", "-Hint", hint],
            cwd=str(root),
            capture_output=True,
            text=True,
            timeout=20,
            check=False,
        )
    except (OSError, subprocess.SubprocessError) as exc:
        return {"status": "unavailable", "source": "external", "reason": str(exc), "hint": hint}
    output = (completed.stdout or completed.stderr).strip()
    primary = next((line.split("->", 1)[1].strip() for line in output.splitlines() if line.startswith("PRIMARY ->")), None)
    return {
        "status": "external-route-pass" if completed.returncode == 0 and primary else "unavailable",
        "source": "external",
        "primary": primary,
        "output": output,
        "returncode": completed.returncode,
        "router": str(script),
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
        return _external_route(hint, reverse_root)
    local = _local_route(hint, primary=primary)
    if source == "auto" and local.get("status") != "local-route-pass":
        external = _external_route(hint, reverse_root)
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
) -> CasePointer:
    if mode not in {"analysis", "reconstruction", "follow-up", "normal-dev"}:
        raise ValueError(f"unsupported mode: {mode}")
    inferred_source = route_source or ("external" if primary.startswith("skills/") else "local")
    inferred_owner = route_owner or ("reverse.native-router" if inferred_source == "external" else "reverse-fusion.local-router")
    return CasePointer(
        case_root=str(case_root),
        route_owner=inferred_owner,
        primary=primary,
        mode=mode,
        decision_delta=delta or [],
        carry_forward_refs=refs or [],
        route_source=inferred_source,
    )
