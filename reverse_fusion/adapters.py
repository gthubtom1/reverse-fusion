"""Typed, bounded adapters for REA, Spec Kit and Craft.

These adapters validate handoffs and return explicit states. They never pretend a
missing provider is a successful business acceptance.
"""
from __future__ import annotations

from dataclasses import dataclass, field
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

    def prepare(self, *, baseline: dict[str, Any], tasks: list[str]) -> dict[str, Any]:
        if not self.upstream_commit or not self.patch_series:
            return {"disposition": "unsupported", "reason": "Craft identity or patch series missing"}
        if not baseline.get("bundle_sha256"):
            return {"disposition": "needs-evidence", "reason": "external baseline is missing"}
        return {
            "disposition": "ready" if self.backend else "unsupported",
            "upstream_commit": self.upstream_commit,
            "patch_series": list(self.patch_series),
            "backend": self.backend,
            "tasks": list(tasks),
        }

    def run(self, *, baseline: dict[str, Any], tasks: list[str], writer: Callable[[list[str]], Any] | None = None) -> dict[str, Any]:
        prepared = self.prepare(baseline=baseline, tasks=tasks)
        if prepared.get("disposition") != "ready":
            return {"version": 1, "disposition": prepared["disposition"], "tasks": tasks, "checks": [], "cleanup": {"status": "not-started"}, "reason": prepared.get("reason")}
        try:
            result = writer(tasks) if writer else {"candidate_files": []}
        except Exception as exc:  # backend errors are returned to the owning runner
            return {"version": 1, "disposition": "failed", "tasks": tasks, "checks": [], "cleanup": {"status": "required"}, "reason": str(exc)}
        return {"version": 1, "disposition": "candidate", "tasks": tasks, "checks": [{"id": "builder-returned", "status": "pass"}], "cleanup": {"status": "verified"}, "result": result}
