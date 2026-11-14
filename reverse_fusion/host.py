"""Portable host discovery with no global configuration writes."""
from __future__ import annotations

import platform
import shutil
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
