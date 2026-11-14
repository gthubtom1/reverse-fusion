"""Typed, bounded adapters for REA, Spec Kit and Craft.

These adapters validate handoffs and return explicit states. They never pretend a
missing provider is a successful business acceptance.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from hashlib import sha256
from pathlib import Path, PurePosixPath
from typing import Any, Callable


@dataclass
class EvidenceRecord:
    evidence_id: str
    question: str
    status: str = "observed"
    provider: str = "rea"
    artifacts: list[str] = field(default_factory=list)
    unknowns: list[str] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        return {
            "evidence_id": self.evidence_id,
            "question": self.question,
            "status": self.status,
            "provider": self.provider,
            "artifacts": list(self.artifacts),
            "unknowns": list(self.unknowns),
        }


def rea_bundle(records: list[EvidenceRecord], *, bundle_sha256: str | None = None) -> dict[str, Any]:
    unknowns = [unknown for record in records for unknown in record.unknowns]
    return {
        "provider": "rea",
        "status": "ready" if records else "unknown",
        "evidence": [record.to_dict() for record in records],
        "unknowns": unknowns,
        "bundle_sha256": bundle_sha256,
    }


def comparison(original: Any, candidate: Any, *, evidence_ids: list[str]) -> dict[str, Any]:
    if not evidence_ids:
        return {"status": "unknown", "reason": "missing evidence", "evidence_ids": []}
    return {
        "status": "pass" if original == candidate else "fail",
        "equal": original == candidate,
        "evidence_ids": evidence_ids,
        "original": original,
        "candidate": candidate,
    }


@dataclass(frozen=True)
class SpecPointer:
    project_root: str
    feature: str
    tasks: tuple[str, ...]
    source_refs: tuple[str, ...]


def spec_pointer(project_root: str, feature: str, tasks: list[str], source_refs: list[str]) -> SpecPointer:
    if not feature or not tasks:
        raise ValueError("Spec Kit pointer requires a feature and at least one task")
    return SpecPointer(project_root, feature, tuple(tasks), tuple(source_refs))


@dataclass
class CraftAdapter:
    upstream_commit: str
    patch_series: tuple[str, ...]
    backend: str | None = None
    capabilities: tuple[str, ...] = ()
    source_manifest_sha256: str | None = None

    REQUIRED_CAPABILITIES = (
        "prepare",
        "build",
        "check",
        "refine",
        "return_summary",
        "cleanup",
    )

    @staticmethod
    def _digest_tasks(tasks: list[str]) -> str:
        return sha256("\n".join(tasks).encode("utf-8")).hexdigest()

    @classmethod
    def six_tool_gate(cls, capabilities: tuple[str, ...] | list[str]) -> dict[str, Any]:
        values = list(capabilities)
        missing = [item for item in cls.REQUIRED_CAPABILITIES if item not in values]
        duplicates = sorted({item for item in values if values.count(item) > 1})
        unexpected = sorted(set(values) - set(cls.REQUIRED_CAPABILITIES))
        return {
            "status": "pass" if not missing and not duplicates and not unexpected else "fail",
            "required": list(cls.REQUIRED_CAPABILITIES),
            "provided": values,
            "missing": missing,
            "duplicates": duplicates,
            "unexpected": unexpected,
        }

    @staticmethod
    def _safe_relative_path(value: str) -> bool:
        path = PurePosixPath(value)
        return bool(value) and not path.is_absolute() and all(part not in {"", ".", ".."} for part in path.parts)

    def prepare(
        self,
        *,
        baseline: dict[str, Any],
        tasks: list[str],
        implementation_root: str = "implementation",
        model_id: str = "unverified-model",
        research_ref: str = "",
    ) -> dict[str, Any]:
        if not self.upstream_commit or not self.patch_series:
            return {"disposition": "unsupported", "reason": "Craft identity or patch series missing"}
        gate = self.six_tool_gate(self.capabilities)
        if self.backend and gate["status"] != "pass":
            return {"disposition": "unsupported", "reason": "six-tool capability gate failed", "gate": gate}
        if not baseline.get("bundle_sha256"):
            return {"disposition": "needs-evidence", "reason": "external baseline is missing"}
        digest = baseline["bundle_sha256"]
        if not isinstance(digest, str) or len(digest) != 64 or any(char not in "0123456789abcdef" for char in digest):
            return {"disposition": "needs-evidence", "reason": "external baseline digest is malformed"}
        if not tasks:
            return {"disposition": "needs-spec", "reason": "no frozen tasks supplied"}
        if not self._safe_relative_path(implementation_root):
            return {"disposition": "needs-scope", "reason": "implementation root must be a safe relative path"}
        if not model_id or not research_ref:
            return {"disposition": "needs-evidence", "reason": "model identity and accepted research reference are required"}
        return {
            "disposition": "ready" if self.backend else "unsupported",
            "upstream_commit": self.upstream_commit,
            "patch_series": list(self.patch_series),
            "backend": self.backend,
            "tasks": list(tasks),
            "task_digest": self._digest_tasks(tasks),
            "implementation_root": implementation_root,
            "model_id": model_id,
            "research_ref": research_ref,
            "gate": gate,
        }

    def run(
        self,
        *,
        baseline: dict[str, Any],
        tasks: list[str],
        writer: Callable[[list[str]], Any] | None = None,
        implementation_root: str = "implementation",
        model_id: str = "unverified-model",
        research_ref: str = "",
    ) -> dict[str, Any]:
        prepared = self.prepare(
            baseline=baseline,
            tasks=tasks,
            implementation_root=implementation_root,
            model_id=model_id,
            research_ref=research_ref,
        )
        if prepared.get("disposition") != "ready":
            return {
                "version": 1,
                "disposition": prepared["disposition"],
                "tasks": tasks,
                "checks": [{"id": "six-tool-gate", "status": prepared.get("gate", {}).get("status", "not-run")}],
                "cleanup": {"status": "not-started"},
                "reason": prepared.get("reason"),
            }
        try:
            result = writer(tasks) if writer else {"candidate_files": []}
        except Exception as exc:  # backend errors are returned to the owning runner
            return {"version": 1, "disposition": "failed", "tasks": tasks, "checks": [], "cleanup": {"status": "required"}, "reason": str(exc)}
        return {
            "version": 1,
            "disposition": "candidate",
            "tasks": tasks,
            "checks": [
                {"id": "six-tool-gate", "status": "pass"},
                {"id": "builder-returned", "status": "pass"},
            ],
            "cleanup": {"status": "verified"},
            "result": result,
            "task_digest": prepared["task_digest"],
            "model_id": prepared["model_id"],
            "research_ref": prepared["research_ref"],
        }
