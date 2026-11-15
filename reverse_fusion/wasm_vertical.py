"""End-to-end local WASM acceptance using retained REA Evidence and WABT."""
from __future__ import annotations

import json
import os
import re
import subprocess
from hashlib import sha256
from pathlib import Path
from typing import Any

from .adapters import comparison
from .runtime import node_runtime


def _read_record(path: Path) -> dict[str, Any] | None:
    try:
        value = json.loads(path.read_text(encoding="utf-8-sig"))
        return value.get("data") if isinstance(value, dict) and value.get('ok') is True and isinstance(value.get("data"), dict) else None
    except (OSError, json.JSONDecodeError):
        return None


def _interp_path(root: Path) -> Path | None:
    explicit = os.environ.get("REVERSE_FUSION_WABT_BIN")
    if explicit:
        candidate = Path(explicit) / "wasm-interp.exe"
        if candidate.is_file():
            return candidate
    candidates = sorted(root.glob("vendor/wabt/*/windows-x64/wabt-*/bin/wasm-interp.exe"))
    return candidates[0] if candidates else None


def _run_interpreter(executable: Path, module: Path) -> dict[str, Any]:
    try:
        completed = subprocess.run(
            [str(executable), str(module), "--run-all-exports"],
            capture_output=True,
            text=True,
            timeout=10,
            check=False,
        )
    except (OSError, subprocess.SubprocessError) as exc:
        return {"status": "unknown", "reason": str(exc)}
    output = (completed.stdout or completed.stderr).strip()
    match = re.search(r"answer\(\) => i32:(-?\d+)", output)
    if completed.returncode != 0 or match is None:
        return {"status": "unknown", "returncode": completed.returncode, "output": output}
    return {"status": "observed", "returncode": 0, "output": output, "value": int(match.group(1))}


def evaluate_wasm(root: Path, candidate_kind: str, *, record_paths: bool = False) -> dict[str, Any]:
    original_path = root / "fixtures" / "answer.wasm"
    candidate_path = {
        "correct": root / "fixtures" / "answer-candidate.wasm",
        "wrong": root / "fixtures" / "answer-wrong.wasm",
        "missing": None,
    }[candidate_kind]
    original = _read_record(root / "state" / "rea-wasm-evidence.json")
    evidence_name = {"correct": "candidate", "wrong": "wrong"}.get(candidate_kind)
    candidate = _read_record(root / "state" / f"rea-wasm-{evidence_name}-evidence.json") if evidence_name else None
    evidence_ids = [item["evidence_id"] for item in (original, candidate) if item and isinstance(item.get("evidence_id"), str)]
    if original is None or candidate_kind == "missing" or candidate is None:
        result = {"status": "unknown", "reason": "complete original and candidate REA Evidence are required", "evidence_ids": evidence_ids}
        return result
    # The official codec owns content identity. A subject digest alone does
    # not authenticate edited interface observations inside an Evidence record.
    verifier = root / 'scripts' / 'verify-evidence.mjs'
    node, _ = node_runtime(root)
    if not node or not verifier.is_file():
        return {'status': 'unknown', 'reason': 'Official REA Evidence authentication is unavailable', 'evidence_ids': evidence_ids}
    try:
        admitted = subprocess.run([node, str(verifier), '--records', str(root / 'state/rea-wasm-evidence.json'),
                                   str(root / 'state' / f'rea-wasm-{evidence_name}-evidence.json')],
                                  capture_output=True, text=True, encoding='utf-8', errors='replace', timeout=30)
        if admitted.returncode != 0:
            return {'status': 'unknown', 'reason': 'Official REA Evidence authentication failed', 'evidence_ids': evidence_ids}
    except (OSError, subprocess.SubprocessError):
        return {'status': 'unknown', 'reason': 'Official REA Evidence authentication did not complete', 'evidence_ids': evidence_ids}
    for record, artifact in ((original, original_path), (candidate, candidate_path)):
        if (not artifact.is_file() or record.get("subject", {}).get("digest", {}).get("sha256")
                != sha256(artifact.read_bytes()).hexdigest()):
            return {"status": "unknown", "reason": "artifact differs from its retained REA Evidence", "evidence_ids": evidence_ids}
    left_entries = original.get("normalized_result", {}).get("interface", {}).get("entries", [])
    right_entries = candidate.get("normalized_result", {}).get("interface", {}).get("entries", [])
    interface = comparison(left_entries, right_entries, evidence_ids=evidence_ids)
    interpreter = _interp_path(root)
    if interpreter is None:
        return {"status": "unknown", "reason": "WABT wasm-interp is unavailable", "evidence_ids": evidence_ids, "interface": interface}
    manifest_path = root / "vendor" / "wabt" / "1.0.42" / "manifest.json"
    try:
        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
        if sha256(interpreter.read_bytes()).hexdigest() != manifest["bin_sha256"]["wasm-interp.exe"]:
            return {"status": "unknown", "reason": "WABT interpreter differs from its manifest", "evidence_ids": evidence_ids}
    except (OSError, ValueError, KeyError):
        return {"status": "unknown", "reason": "WABT interpreter identity unavailable", "evidence_ids": evidence_ids}
    left_run = _run_interpreter(interpreter, original_path)
    right_run = _run_interpreter(interpreter, candidate_path)
    runtime = comparison(left_run.get("value"), right_run.get("value"), evidence_ids=evidence_ids) if left_run.get("status") == "observed" and right_run.get("status") == "observed" else {"status": "unknown", "reason": "runtime observation incomplete", "left": left_run, "right": right_run, "evidence_ids": evidence_ids}
    status = "pass" if interface.get("status") == "pass" and runtime.get("status") == "pass" else "fail" if interface.get("status") == "fail" or runtime.get("status") == "fail" else "unknown"
    result = {"status": status, "candidate_kind": candidate_kind, "evidence_ids": evidence_ids, "interface": interface, "runtime": runtime, "left_run": left_run, "right_run": right_run}
    if record_paths:
        result["original_path"] = str(original_path)
        result["candidate_path"] = str(candidate_path)
    return result
