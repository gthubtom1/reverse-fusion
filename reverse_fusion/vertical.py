"""Small deterministic console slice used to prove the acceptance plane."""
from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Callable

from .adapters import EvidenceRecord, comparison, rea_bundle


def reference_console(args: list[str]) -> dict[str, Any]:
    # The fixture models a stable, observable contract rather than a real target.
    return {"argv": list(args), "count": len(args), "joined": " ".join(args)}


@dataclass(frozen=True)
class VerticalResult:
    status: str
    evidence: dict[str, Any]
    comparison: dict[str, Any]
    candidate: Any

    def to_dict(self) -> dict[str, Any]:
        return {"status": self.status, "evidence": self.evidence, "comparison": self.comparison, "candidate": self.candidate}


def evaluate_console(candidate: Callable[[list[str]], Any] | None, args: list[str], *, evidence: bool = True) -> VerticalResult:
    original = reference_console(args)
    records = [EvidenceRecord("E-CONSOLE-001", "What console contract is observable?", artifacts=["reference-console"])] if evidence else []
    bundle = rea_bundle(records)
    if candidate is None:
        return VerticalResult("unknown", bundle, comparison({}, {}, evidence_ids=[]), None)
    actual = candidate(args)
    diff = comparison(original, actual, evidence_ids=[record.evidence_id for record in records])
    return VerticalResult("pass" if diff["status"] == "pass" else "fail", bundle, diff, actual)


def correct_candidate(args: list[str]) -> dict[str, Any]:
    return reference_console(args)


def wrong_candidate(args: list[str]) -> dict[str, Any]:
    return {"argv": list(reversed(args)), "count": len(args) + 1, "joined": ",".join(args)}
