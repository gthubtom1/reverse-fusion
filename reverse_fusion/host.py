"""Portable host discovery with no global configuration writes."""
from __future__ import annotations

import json
import platform
import shutil
from hashlib import sha256
import os
from pathlib import Path
from typing import Any


def _known_config_paths(host: str) -> list[Path]:
    home = Path.home()
    if host == "codex":
        root = Path(os.environ.get("CODEX_HOME", home / ".codex"))
        return [root / "config.toml", root / "AGENTS.md"]
    if host == "pi":
        root = Path(os.environ.get("PI_CODING_AGENT_DIR", home / ".pi" / "agent"))
        return [root / "settings.json", root / "mcp.json", root / "AGENTS.md"]
    if host == "claude":
        root = Path(os.environ.get("CLAUDE_CONFIG_DIR", home / ".claude"))
        return [root / "settings.json", root / "config.json", home / ".claude.json"]
    return []


def snapshot_host_config(host: str) -> dict[str, Any]:
    """Hash known host config files without reading or storing their contents."""
    files: dict[str, str] = {}
    for path in _known_config_paths(host):
        try:
            if path.is_file():
                files[str(path)] = sha256(path.read_bytes()).hexdigest()
        except OSError:
            return {"status": "unobserved", "files": files, "reason": f"cannot hash {path}"}
    return {"status": "observed", "files": files, "known_paths": [str(path) for path in _known_config_paths(host)]}


def compare_host_config(before: dict[str, Any], after: dict[str, Any]) -> dict[str, Any]:
    if before.get("status") != "observed" or after.get("status") != "observed":
        return {"status": "unknown", "mutation": None, "before": before, "after": after}
    return {
        "status": "observed",
        "mutation": before.get("files", {}) != after.get("files", {}),
        "before": before,
        "after": after,
    }


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
    selected = hosts["available"] if client == "auto" else [client] if client in hosts["available"] else []
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
        # Windows PowerShell 5's `Out-File -Encoding utf8` emits a UTF-8 BOM.
        # Accept both BOM and BOM-less records so a real host probe is readable
        # on every supported Windows shell without weakening the schema checks.
        value = json.loads(path.read_text(encoding="utf-8-sig"))
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
