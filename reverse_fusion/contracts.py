from __future__ import annotations

import json
from pathlib import Path
from typing import Any


class ContractError(ValueError):
    pass


def read_json(path: Path) -> dict[str, Any]:
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise ContractError(f"cannot read JSON {path}: {exc}") from exc
    if not isinstance(value, dict):
        raise ContractError(f"JSON root must be object: {path}")
    return value


def _check_versioned_object(path: Path, required: set[str], allowed: set[str]) -> dict[str, Any]:
    value = read_json(path)
    missing = sorted(required - value.keys())
    unknown = sorted(set(value) - allowed)
    if missing:
        raise ContractError(f"{path}: missing keys {missing}")
    if unknown:
        raise ContractError(f"{path}: unknown keys {unknown}")
    if not isinstance(value.get("schema_version"), int) or value["schema_version"] != 1:
        raise ContractError(f"{path}: schema_version must be integer 1")
    return value


def check_contracts(root: Path) -> dict[str, Any]:
    checks: list[dict[str, Any]] = []
    try:
        manifest = _check_versioned_object(
            root / "components" / "official" / "manifest.json",
            {"schema_version", "project", "components"},
            {"schema_version", "project", "components"},
        )
        if manifest["project"] != "reverse-fusion" or not isinstance(manifest["components"], list):
            raise ContractError("official manifest has invalid project/components")
        checks.append({"id": "official-manifest", "status": "pass"})
        for rel in (
            "schemas/handoff-v1.schema.json",
            "schemas/external-baseline-v1.schema.json",
            "schemas/candidate-result-v1.schema.json",
            "schemas/source-manifest-v1.schema.json",
        ):
            schema = read_json(root / rel)
            if schema.get("$schema") is None or schema.get("$id") is None:
                raise ContractError(f"{rel}: missing $schema/$id")
            checks.append({"id": rel, "status": "pass"})
        for profile in ("normal-dev", "analysis", "reconstruction", "follow-up"):
            value = read_json(root / "profiles" / f"{profile}.json")
            if value.get("profile") != profile:
                raise ContractError(f"profile mismatch: {profile}")
            checks.append({"id": f"profile:{profile}", "status": "pass"})
    except ContractError as exc:
        checks.append({"id": "contracts", "status": "fail", "detail": str(exc)})
        return {"status": "fail", "checks": checks}
    return {"status": "pass", "checks": checks}
