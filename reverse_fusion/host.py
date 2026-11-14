"""Portable host discovery with no global configuration writes."""
from __future__ import annotations

import json
import platform
import shutil
from pathlib import Path
from typing import Any


def detect_hosts() -> dict[str, Any]:
    candidates = {
        "codex": ("codex", "codex.exe"),
        "pi": ("pi", "pi.exe"),
        "claude": ("claude", "claude.exe"),
    }
    found: dict[str, str | None] = {}
    for name, commands in candidates.items():
        found[name] = next((path for command in commands if (path := shutil.which(command))), None)
    return {
        "os": platform.system().lower(),
        "arch": platform.machine().lower(),
        "hosts": found,
        "available": sorted(name for name, path in found.items() if path),
        "global_config_mutation": False,
    }


def adapter_plan(client: str) -> dict[str, Any]:
    hosts = detect_hosts()
    selected = hosts["available"] if client == "auto" else [client] if client in hosts["hosts"] else []
    return {
        "requested": client,
        "selected": selected,
        "host": hosts,
        "actions": [
            "read repository instructions",
            "run reverse_fusion plan and doctor",
            "preserve host-global configuration unless explicitly selected by the installer",
        ],
    }


def read_handshake_record(root: Path) -> dict[str, Any]:
    """Read the repository-local host probe without treating absence as success."""
    path = root / "state" / "host-handshakes.json"
    if not path.is_file():
        return {"status": "unrecorded", "config_mutation": False, "probes": []}
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return {"status": "invalid", "config_mutation": False, "probes": []}
    probes = value.get("probes") if isinstance(value, dict) else None
    if not isinstance(probes, list):
        return {"status": "invalid", "config_mutation": False, "probes": []}
    summary = []
    for item in probes:
        if not isinstance(item, dict) or not isinstance(item.get("id"), str):
            continue
        summary.append({
            "id": item["id"],
            "status": item.get("status", "unknown"),
            "version": item.get("version"),
            "exit_code": item.get("exit_code"),
            "reason": item.get("reason"),
        })
    return {
        "status": "recorded",
        "config_mutation": value.get("config_mutation") is True,
        "probes": summary,
    }
