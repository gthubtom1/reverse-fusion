"""Portable host discovery with no global configuration writes."""
from __future__ import annotations

import json
import platform
import shutil
import subprocess
from datetime import datetime, timezone
from hashlib import sha256
import os
from pathlib import Path
from typing import Any


def assistant_texts(stdout: str, host: str) -> list[str]:
    """Read final assistant payloads only; echoed prompts are not handshakes."""
    texts: list[str] = []
    for line in stdout.splitlines():
        try:
            value = json.loads(line)
        except (ValueError, TypeError):
            continue
        if not isinstance(value, dict):
            continue
        if host == "codex" and value.get("type") == "item.completed":
            item = value.get("item", {})
            if item.get("type") == "agent_message" and isinstance(item.get("text"), str):
                texts.append(item["text"])
        elif host == "pi":
            messages = [value.get("message")] if value.get("type") == "message_end" else value.get("messages", []) if value.get("type") == "agent_end" else []
            for message in messages:
                if isinstance(message, dict) and message.get("role") == "assistant":
                    texts.extend(item["text"] for item in message.get("content", [])
                                 if isinstance(item, dict) and item.get("type") == "text" and isinstance(item.get("text"), str))
        elif host == "claude" and value.get("type") == "result" and value.get("is_error") is not True:
            if isinstance(value.get("result"), str):
                texts.append(value["result"])
    return texts


def probe_hosts(root: Path, *, client: str = "auto", timeout_seconds: int = 45) -> dict[str, Any]:
    """Run one finite, read-only transport probe per explicitly selected host."""
    clients = ["codex", "pi", "claude"] if client == "auto" else [client]
    probes = []
    for host in clients:
        if host not in {"codex", "pi", "claude"}:
            raise ValueError("Unknown host")
        names = [f"{host}.exe", f"{host}.ps1", f"{host}.cmd"] if os.name == "nt" else [host]
        executable = next((found for name in names if (found := shutil.which(name))), None)
        sentinel = f"RF_HOST_HANDSHAKE_{host.upper()}"
        prompt = f"Reply with exactly {sentinel} and nothing else. Do not call tools or modify files."
        before = snapshot_host_config(host)
        version = None
        status, reason, code, observed = "unavailable", "executable not found", None, False
        stdout, stderr = "", ""
        timed_out = False
        if executable:
            command = [executable]
            if executable.lower().endswith(".ps1"):
                command = [shutil.which("powershell") or "pwsh", "-NoProfile", "-File", executable]
            args = (["exec", "--ephemeral", "--sandbox", "read-only", "--ignore-user-config", "--json", "--skip-git-repo-check", "-"] if host == "codex"
                    else ["--print", "--mode", "json", "--no-session", "--no-tools", "--no-mcp", prompt] if host == "pi"
                    else ["-p", prompt, "--bare", "--no-session-persistence", "--tools", "", "--permission-mode", "plan", "--output-format", "json"])
            try:
                banner = subprocess.run(command + ["--version"], capture_output=True, text=True, encoding="utf-8", errors="replace", timeout=10, cwd=root)
                version = (banner.stdout or banner.stderr).strip()[:200]
                result = subprocess.run(command + args, input=prompt if host == "codex" else "", capture_output=True, text=True, encoding="utf-8", errors="replace", timeout=timeout_seconds, cwd=root)
                stdout, stderr, code = result.stdout, result.stderr, result.returncode
                observed = any(text.strip() == sentinel for text in assistant_texts(stdout, host))
                combined = f"{stdout}\n{stderr}".lower()
                if code == 0 and observed:
                    status, reason = "pass", "exact assistant sentinel observed"
                elif any(token in combined for token in ("not logged in", "please run /login", "credential", "out of credits", "quota", "service temporarily unavailable", "503", "not recognized", "command not found")):
                    status, reason = "blocked", "host login, quota, runtime or provider availability blocked the probe"
                else:
                    status, reason = "unknown" if code == 0 else "failed", "exact assistant sentinel was not observed"
            except subprocess.TimeoutExpired:
                status, reason, timed_out = "blocked", "host probe deadline exceeded; descendant cleanup unverified", True
            except OSError as exc:
                status, reason = "blocked", str(exc)
        check = compare_host_config(before, snapshot_host_config(host))
        if check["mutation"] is not False:
            status, reason = "blocked", "host configuration changed or snapshot was not observed"
        probes.append({"id": host, "status": status, "reason": reason, "version": version,
                       "executable": executable, "exit_code": code, "sentinel": sentinel, "observed": observed,
                       "config_mutation": check["mutation"], "config_snapshot": check,
                       "cleanup": "unknown" if timed_out else "root invocation returned; no descendant claim",
                       "output_excerpt": (stdout + "\n" + stderr)[-1800:]})
    return {"schema_version": 1, "operation": "host-handshakes", "generated_at": datetime.now(timezone.utc).isoformat(),
            "config_mutation": any(item["config_mutation"] is True for item in probes), "probes": probes}


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
