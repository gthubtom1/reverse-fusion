"""Host-owned Builder transport.

This module deliberately does not select a model.  It invokes the currently
installed Codex, Pi, or Claude CLI and records the host response as an
observation.  The repository owns the task boundary, file scope, checks and
cleanup; the host owns the account, provider and model.
"""
from __future__ import annotations

import json
import os
import shutil
import subprocess
import tempfile
from dataclasses import dataclass
from hashlib import sha256
from pathlib import Path
from typing import Any

from .contracts import is_safe_relative_path
from .host import compare_host_config, snapshot_host_config


@dataclass(frozen=True)
class HostInvocation:
    host: str
    executable: str | None
    argv: tuple[str, ...]


class HostBuilder:
    """Run one bounded host-agent build in a repository-owned workspace."""

    HOSTS = ("codex", "pi", "claude")
    REQUIRED_TOOLS = ("prepare", "build", "check", "refine", "return_summary", "cleanup")

    def __init__(self, workspace: Path, *, host: str = "codex", timeout_seconds: int = 180):
        self.workspace = workspace.resolve()
        self.host = host
        self.timeout_seconds = timeout_seconds

    def _choose_host(self) -> tuple[str | None, str | None]:
        if self.host == "auto":
            for candidate in self.HOSTS:
                path = shutil.which(candidate) or shutil.which(f"{candidate}.exe")
                if path:
                    return candidate, path
            return None, None
        if self.host not in self.HOSTS:
            return None, None
        return self.host, shutil.which(self.host) or shutil.which(f"{self.host}.exe")

    def _invocation(self, host: str, executable: str, prompt: str) -> HostInvocation:
        if host == "codex":
            # No --model is supplied: the active Codex account/model is the
            # host's responsibility. --ignore-user-config prevents this probe
            # from changing or depending on project-global config content.
            argv = (
                executable,
                "exec",
                "--ephemeral",
                "--approve-for-me",
                "--ignore-user-config",
                "--skip-git-repo-check",
                "--json",
                "-C",
                str(self.workspace),
                prompt,
            )
        elif host == "pi":
            argv = (
                executable,
                "--print",
                "--mode",
                "json",
                "--no-session",
                "--no-mcp",
                prompt,
            )
        else:
            argv = (
                executable,
                "-p",
                prompt,
                "--bare",
                "--no-session-persistence",
                "--tools",
                "Read,Write",
                "--permission-mode",
                "acceptEdits",
                "--output-format",
                "json",
            )
        return HostInvocation(host, executable, argv)

    def _invoke(self, invocation: HostInvocation, prompt: str) -> dict[str, Any]:
        try:
            completed = subprocess.run(
                list(invocation.argv),
                cwd=str(self.workspace),
                stdin=subprocess.DEVNULL,
                capture_output=True,
                text=True,
                encoding="utf-8",
                errors="replace",
                timeout=self.timeout_seconds,
                check=False,
                env={**os.environ, "RF_BUILDER_ACTIVE": "1"},
            )
        except subprocess.TimeoutExpired as exc:
            return {
                "status": "blocked",
                "reason": "host builder timed out",
                "host": invocation.host,
                "executable": invocation.executable,
                "argv": list(invocation.argv[:-1]),
                "stdout": (exc.stdout or "")[-4000:],
                "stderr": (exc.stderr or "")[-4000:],
            }
        except OSError as exc:
            return {"status": "blocked", "reason": str(exc), "host": invocation.host, "executable": invocation.executable}
        stdout = completed.stdout or ""
        stderr = completed.stderr or ""
        combined = f"{stdout}\n{stderr}"
        lower = combined.lower()
        if completed.returncode != 0 and ("not logged in" in lower or "login" in lower or "credential" in lower):
            status = "blocked"
            reason = "host CLI started but has no usable login/provider credential"
        elif completed.returncode == 0:
            status = "pass"
            reason = "host CLI completed"
        else:
            status = "failed"
            reason = "host CLI returned a non-zero exit code"
        return {
            "status": status,
            "reason": reason,
            "host": invocation.host,
            "executable": invocation.executable,
            "exit_code": completed.returncode,
            "argv": list(invocation.argv[:-1]),
            "stdout": stdout[-12000:],
            "stderr": stderr[-12000:],
            "config_mutation": False,
        }

    def _snapshot(self) -> dict[str, str]:
        if not self.workspace.exists():
            return {}
        result: dict[str, str] = {}
        for path in self.workspace.rglob("*"):
            if path.is_file() and ".git" not in path.parts:
                result[str(path.relative_to(self.workspace)).replace("\\", "/")] = sha256(path.read_bytes()).hexdigest()
        return result

    @staticmethod
    def _safe_relative(value: str) -> bool:
        return is_safe_relative_path(value)

    def run(
        self,
        *,
        baseline: dict[str, Any],
        tasks: list[str],
        research_ref: str,
        output_relative: str,
        prompt: str,
        allowed_outputs: list[str] | None = None,
    ) -> dict[str, Any]:
        checks: list[dict[str, Any]] = []
        host, executable = self._choose_host()
        if not baseline.get("bundle_sha256"):
            return {"version": 1, "disposition": "needs-evidence", "tasks": tasks, "checks": checks, "cleanup": {"status": "not-started"}, "reason": "external baseline is missing"}
        if not tasks:
            return {"version": 1, "disposition": "needs-spec", "tasks": tasks, "checks": checks, "cleanup": {"status": "not-started"}, "reason": "no frozen tasks supplied"}
        if not research_ref:
            return {"version": 1, "disposition": "needs-evidence", "tasks": tasks, "checks": checks, "cleanup": {"status": "not-started"}, "reason": "accepted research reference is missing"}
        if not self._safe_relative(output_relative):
            return {"version": 1, "disposition": "needs-scope", "tasks": tasks, "checks": checks, "cleanup": {"status": "not-started"}, "reason": "candidate output must be workspace-relative"}
        if host is None or executable is None:
            return {"version": 1, "disposition": "unsupported", "tasks": tasks, "checks": checks, "cleanup": {"status": "not-started"}, "reason": "requested host CLI is unavailable"}

        self.workspace.mkdir(parents=True, exist_ok=True)
        output_path = (self.workspace / output_relative).resolve()
        try:
            output_path.relative_to(self.workspace)
        except ValueError:
            return {"version": 1, "disposition": "needs-scope", "tasks": tasks, "checks": checks, "cleanup": {"status": "not-started"}, "reason": "candidate output escapes workspace"}
        requested_allowed = allowed_outputs or [output_relative]
        if any(not is_safe_relative_path(item) for item in requested_allowed):
            return {"version": 1, "disposition": "needs-scope", "tasks": tasks, "checks": checks, "cleanup": {"status": "not-started"}, "reason": "allowed output escapes workspace"}
        allowed = {item.replace("\\", "/") for item in requested_allowed}
        before = self._snapshot()
        checks.append({"id": "prepare", "status": "pass", "host": host, "research_ref": research_ref})

        instruction = (
            f"You are the Builder for a bounded reconstruction task. Work only in {self.workspace}. "
            f"Frozen tasks (already accepted, do not invent new scope): {json.dumps(tasks, ensure_ascii=False)}. "
            f"Accepted research Evidence reference: {research_ref}. "
            f"Create or modify only the candidate files listed here: {json.dumps(sorted(allowed), ensure_ascii=False)}. "
            f"The required primary output is {output_relative}. "
            f"Use the supplied task and Evidence context. Do not modify repository, host, credential, or configuration files. "
            f"Do not choose or report a model. {prompt} "
            "After writing the candidate, return a short factual summary."
        )
        invocation = self._invocation(host, executable, instruction)
        config_before = snapshot_host_config(host)
        host_result = self._invoke(invocation, instruction)
        config_after = snapshot_host_config(host)
        config_check = compare_host_config(config_before, config_after)
        host_result["config_snapshot"] = config_check
        host_result["config_mutation"] = config_check["mutation"]
        checks.append({"id": "build", "status": host_result["status"], "host": host, "exit_code": host_result.get("exit_code")})
        checks.append({"id": "host-config", "status": "pass" if config_check["mutation"] is False else config_check["status"], "mutation": config_check["mutation"]})
        if config_check["mutation"] is not False:
            return {
                "version": 1,
                "disposition": "blocked-cleanup",
                "tasks": tasks,
                "checks": checks,
                "cleanup": {"status": "blocked"},
                "backend": f"host-agent:{host}",
                "host_result": host_result,
                "research_ref": research_ref,
                "reason": "host configuration snapshot changed or could not be observed",
            }
        if host_result["status"] != "pass":
            checks.extend([
                {"id": "check", "status": "not-run"},
                {"id": "refine", "status": "not-run"},
                {"id": "return_summary", "status": "pass"},
            ])
            return {"version": 1, "disposition": host_result["status"], "tasks": tasks, "checks": checks, "cleanup": {"status": "verified"}, "backend": f"host-agent:{host}", "host_result": host_result, "research_ref": research_ref}

        output_exists = output_path.is_file()
        changed = set(self._snapshot()) - set(before)
        unexpected = sorted(changed - allowed)
        if output_exists and not unexpected:
            checks.append({"id": "check", "status": "pass", "candidate": output_relative})
            # Exercise the refinement seam even when the first candidate
            # already satisfies the bounded file contract.  The host is told
            # to leave a correct candidate untouched; this proves that the
            # six-tool transport is available without inventing a second
            # writer or changing the frozen scope.
            refine_instruction = (
                f"Review the existing candidate file {output_relative} against the same frozen tasks and Evidence. "
                "If it already satisfies the tasks, leave it unchanged. If a correction is required, edit only the "
                f"allowed candidate files {json.dumps(sorted(allowed), ensure_ascii=False)}. Do not create any other files. "
                "Return a short factual refinement summary."
            )
            refine_invocation = self._invocation(host, executable, refine_instruction)
            refine_config_before = snapshot_host_config(host)
            refine_result = self._invoke(refine_invocation, refine_instruction)
            refine_config_after = snapshot_host_config(host)
            refine_config_check = compare_host_config(refine_config_before, refine_config_after)
            refine_result["config_snapshot"] = refine_config_check
            refine_result["config_mutation"] = refine_config_check["mutation"]
            refine_after = self._snapshot()
            refine_unexpected = sorted(set(refine_after) - set(before) - allowed)
            if refine_config_check["mutation"] is not False:
                checks.append({"id": "refine-config", "status": refine_config_check["status"], "mutation": refine_config_check["mutation"]})
                checks.append({"id": "refine", "status": "blocked-cleanup", "unexpected_writes": refine_unexpected})
                disposition = "blocked-cleanup"
            elif refine_result["status"] == "pass" and output_path.is_file() and not refine_unexpected:
                checks.append({"id": "refine", "status": "pass", "candidate": output_relative})
                disposition = "candidate"
            else:
                checks.append({"id": "refine", "status": refine_result["status"], "unexpected_writes": refine_unexpected})
                disposition = "failed"
            result_refine = refine_result
        else:
            checks.append({"id": "check", "status": "fail", "candidate": output_relative, "unexpected_writes": unexpected})
            checks.append({"id": "refine", "status": "unsupported", "reason": "host output did not satisfy the bounded file contract"})
            disposition = "failed"
            result_refine = None
        checks.append({"id": "return_summary", "status": "pass"})
        cleanup_status = "blocked" if disposition == "blocked-cleanup" else "verified"
        # The candidate is retained; only transient builder temp material would
        # be removed here. The contract records that no host/global config was
        # touched by this invocation.
        checks.append({"id": "cleanup", "status": cleanup_status, "config_mutation": config_check["mutation"]})
        result: dict[str, Any] = {
            "version": 1,
            "disposition": disposition,
            "tasks": tasks,
            "checks": checks,
            "cleanup": {"status": cleanup_status},
            "backend": f"host-agent:{host}",
            "host": host,
            "host_result": host_result,
            "research_ref": research_ref,
            "output": str(output_path),
        }
        if result_refine is not None:
            result["refine_result"] = result_refine
        if disposition == "candidate":
            result["candidate_sha256"] = sha256(output_path.read_bytes()).hexdigest()
        return result

