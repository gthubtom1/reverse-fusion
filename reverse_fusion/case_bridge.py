"""Thin bridge to the installed reverse-skill router and its case authority.

The bridge deliberately stores pointers and decision deltas; it does not copy a
second routing table or create a competing evidence ledger.
"""
from __future__ import annotations

import json
import os
import subprocess
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any


@dataclass(frozen=True)
class CasePointer:
    case_root: str
    route_owner: str
    primary: str
    mode: str
    decision_delta: list[str]
    carry_forward_refs: list[str]

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


def locate_reverse_root() -> Path | None:
    """Locate the installed enhanced reverse-skill without vendoring it."""
    explicit = os.environ.get("REVERSE_SKILL_ROOT")
    if explicit:
        candidate = Path(explicit).expanduser()
        if (candidate / "RULES.md").is_file():
            return candidate
    receipt_value = os.environ.get("REVERSE_WORKFLOW_RECEIPT")
    receipt = Path(receipt_value) if receipt_value else Path.home() / "AppData" / "Local" / "reverse-workflow" / ".installer" / "receipt.json"
    if receipt.is_file():
        try:
            data = json.loads(receipt.read_text(encoding="utf-8"))
            candidate = Path(data["reverse"]["root"])
            if (candidate / "RULES.md").is_file():
                return candidate
        except (OSError, KeyError, TypeError, json.JSONDecodeError):
            return None
    return None


def dry_run_route(hint: str, reverse_root: Path | None = None) -> dict[str, Any]:
    """Ask the native router for a route, preserving its output as support data."""
    root = reverse_root or locate_reverse_root()
    if root is None:
        return {"status": "unavailable", "reason": "reverse-skill root not located", "hint": hint}
    script = root / "skills" / "scripts" / "master-route.ps1"
    if not script.is_file():
        return {"status": "unavailable", "reason": "native router missing", "path": str(script)}
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
        return {"status": "unavailable", "reason": str(exc)}
    output = (completed.stdout or completed.stderr).strip()
    primary = next((line.split("->", 1)[1].strip() for line in output.splitlines() if line.startswith("PRIMARY ->")), None)
    return {
        "status": "routed" if completed.returncode == 0 and primary else "unavailable",
        "primary": primary,
        "output": output,
        "returncode": completed.returncode,
        "router": str(script),
    }


def build_case_pointer(case_root: Path, primary: str, mode: str, *, delta: list[str] | None = None, refs: list[str] | None = None) -> CasePointer:
    if mode not in {"analysis", "reconstruction", "follow-up", "normal-dev"}:
        raise ValueError(f"unsupported mode: {mode}")
    return CasePointer(
        case_root=str(case_root),
        route_owner="reverse.native-router",
        primary=primary,
        mode=mode,
        decision_delta=delta or [],
        carry_forward_refs=refs or [],
    )
