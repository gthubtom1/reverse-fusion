"""A bounded handoff for the agent already running the current conversation.

No child CLI, account, provider or model is started. The active host writes the
candidate with its existing tools; this module observes file boundaries only.
Business acceptance remains the independent build/comparison/ledger's job.
"""
from __future__ import annotations

import json
from hashlib import sha256
from pathlib import Path
from typing import Any

from .builder import HostBuilder
from .contracts import is_safe_relative_path


def _inside(root: Path, relative: str) -> Path:
    if not is_safe_relative_path(relative):
        raise ValueError(f"Expected a repository-relative path: {relative}")
    path = (root / relative).resolve()
    if not path.is_relative_to(root):
        raise ValueError(f"Path escapes the repository: {relative}")
    return path


def _digest(path: Path) -> str:
    return sha256(path.read_bytes()).hexdigest()


def prepare_session(
    root: Path, *, workspace: str, receipt: str, tasks: list[str],
    task_files: list[str], research_files: list[str], allowed_outputs: list[str],
) -> dict[str, Any]:
    root = root.resolve()
    area = _inside(root, workspace)
    record_path = _inside(root, receipt)
    if record_path.is_relative_to(area):
        raise ValueError("Session receipt must stay outside the candidate workspace")
    if record_path.exists():
        raise ValueError("Session receipt already exists; resume it or choose a new run")
    if not tasks or not task_files or not research_files or not allowed_outputs:
        raise ValueError("Frozen tasks, task documents, research and candidate outputs are required")
    for relative in allowed_outputs:
        _inside(area, relative)
    refs = {name: _digest(_inside(root, name)) for name in dict.fromkeys(task_files + research_files)}
    task_text = "\n".join(_inside(root, name).read_text(encoding="utf-8-sig") for name in task_files)
    if any(task not in task_text for task in tasks):
        raise ValueError("A selected task ID is absent from the frozen task documents")
    area.mkdir(parents=True, exist_ok=True)
    observer = HostBuilder(area)
    before = observer._snapshot()
    if observer._unsafe_entries(before):
        raise ValueError("Candidate workspace contains a symbolic link or junction")
    record = {
        "version": 1, "backend": "current-session", "workspace": workspace,
        "tasks": tasks, "frozen_refs": refs, "allowed_outputs": allowed_outputs,
        "before": before, "phase": "prepared", "events": [],
        "model_selection": "current-host-owned", "business_acceptance": "not-performed",
    }
    record_path.parent.mkdir(parents=True, exist_ok=True)
    record_path.write_text(json.dumps(record, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return {"status": "prepared", "receipt": receipt, "workspace": workspace,
            "read": list(refs), "tasks": tasks, "allowed_outputs": allowed_outputs,
            "action": "The current host reads the frozen files, writes only allowed candidate outputs, then records check/refine/finish.",
            "model_selection": "current-host-owned", "business_acceptance": "not-performed"}


def check_session(root: Path, *, receipt: str, phase: str) -> dict[str, Any]:
    root = root.resolve()
    record_path = _inside(root, receipt)
    record = json.loads(record_path.read_text(encoding="utf-8"))
    if record.get("backend") != "current-session" or record.get("version") != 1:
        raise ValueError("Unsupported session record")
    if record.get("phase") == "finished":
        raise ValueError("Session already finished; new work requires a new frozen run")
    area = _inside(root, record["workspace"])
    if record_path.is_relative_to(area):
        raise ValueError("Session receipt is inside the candidate workspace")
    for relative, expected in record["frozen_refs"].items():
        if _digest(_inside(root, relative)) != expected:
            raise ValueError(f"Frozen task or research changed: {relative}")
    observer = HostBuilder(area)
    after = observer._snapshot()
    delta = observer._snapshot_delta(record["before"], after)
    allowed = {name.replace("\\", "/") for name in record["allowed_outputs"]}
    changed = set(delta["added"]) | set(delta["changed"])
    unexpected = sorted((changed | set(delta["deleted"])) - allowed)
    missing = sorted(name for name in allowed if name not in after)
    stale = sorted(name for name in allowed if name not in changed)
    unsafe = observer._unsafe_entries(after)
    if unexpected or missing or stale or unsafe:
        return {"status": "blocked", "phase": phase, "unexpected_writes": unexpected,
                "missing_outputs": missing, "stale_outputs": stale, "unsafe_entries": unsafe,
                "business_acceptance": "not-performed"}
    if phase not in {"check", "refine", "finish"}:
        raise ValueError("Session phase must be check, refine or finish")
    phases = [event["phase"] for event in record["events"]]
    if phase == "refine" and "check" not in phases:
        raise ValueError("Check the built candidate before the host's refinement step")
    if phase == "finish" and ("check" not in phases or "refine" not in phases):
        raise ValueError("Observe check and refine before finishing the handoff")
    outputs = {name: after[name] for name in sorted(allowed)}
    record["events"].append({"phase": phase, "outputs": outputs, "snapshot_delta": delta})
    record["phase"] = "finished" if phase == "finish" else phase
    record_path.write_text(json.dumps(record, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return {"version": 1, "status": "candidate" if phase == "finish" else "observed",
            "backend": "current-session", "tasks": record["tasks"], "phase": phase,
            "outputs": outputs, "business_acceptance": "not-performed",
            "cleanup": {"status": "observed", "child_processes_started": 0,
                        "reason": "Current host tools own execution; this adapter starts no helper processes."}}
