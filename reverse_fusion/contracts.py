from __future__ import annotations

import json
from hashlib import sha256
from pathlib import Path
from typing import Any, Iterable


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


def sha256_file(path: Path) -> str:
    """Return a stable digest used by source and acceptance manifests."""
    digest = sha256()
    try:
        with path.open("rb") as handle:
            for chunk in iter(lambda: handle.read(1024 * 1024), b""):
                digest.update(chunk)
    except OSError as exc:
        raise ContractError(f"cannot hash {path}: {exc}") from exc
    return digest.hexdigest()


def _is_relative_safe(value: str) -> bool:
    path = Path(value)
    return bool(value) and not path.is_absolute() and ".." not in path.parts


def _check_unique_ids(items: Iterable[dict[str, Any]], label: str) -> None:
    seen: set[str] = set()
    for index, item in enumerate(items):
        item_id = item.get("id")
        if not isinstance(item_id, str) or not item_id:
            raise ContractError(f"{label}[{index}].id must be a non-empty string")
        if item_id in seen:
            raise ContractError(f"{label}: duplicate id {item_id!r}")
        seen.add(item_id)


def validate_external_baseline(value: dict[str, Any]) -> dict[str, Any]:
    allowed = {"version", "root", "bundle_sha256", "artifacts"}
    missing = sorted({"version", "root", "bundle_sha256", "artifacts"} - value.keys())
    unknown = sorted(set(value) - allowed)
    if missing or unknown:
        raise ContractError(f"external baseline contract missing={missing} unknown={unknown}")
    if value["version"] != 1 or not isinstance(value["root"], str) or not isinstance(value["artifacts"], list):
        raise ContractError("external baseline has invalid version/root/artifacts")
    digest = value["bundle_sha256"]
    if not isinstance(digest, str) or len(digest) != 64 or any(char not in "0123456789abcdef" for char in digest):
        raise ContractError("external baseline bundle_sha256 must be lowercase SHA-256")
    return value


def validate_candidate_result(value: dict[str, Any]) -> dict[str, Any]:
    required = {"version", "disposition", "tasks", "checks", "cleanup"}
    missing = sorted(required - value.keys())
    if missing or value.get("version") != 1:
        raise ContractError(f"candidate result missing={missing} or version is not 1")
    if value["disposition"] not in {"candidate", "needs-evidence", "needs-spec", "needs-scope", "unsupported", "failed", "blocked-cleanup"}:
        raise ContractError("candidate result has invalid disposition")
    if not isinstance(value["tasks"], list) or not isinstance(value["checks"], list) or not isinstance(value["cleanup"], dict):
        raise ContractError("candidate result tasks/checks/cleanup have invalid types")
    return value


def validate_handoff(value: dict[str, Any]) -> dict[str, Any]:
    required = {"version", "case", "original", "implementation", "baseline", "checks", "builder", "owner"}
    missing = sorted(required - value.keys())
    if missing or value.get("version") != 1:
        raise ContractError(f"handoff missing={missing} or version is not 1")
    if any(not isinstance(value[key], dict) for key in required - {"version"}):
        raise ContractError("handoff sections must be objects")
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
        _check_unique_ids(manifest["components"], "official manifest components")
        for component in manifest["components"]:
            for key in ("id", "kind", "source", "policy"):
                if not isinstance(component.get(key), str) or not component[key]:
                    raise ContractError(f"official manifest component {component.get('id')!r} missing {key}")
            if "path" in component and not _is_relative_safe(component["path"]):
                raise ContractError(f"official manifest component {component['id']!r} has unsafe path")
        checks.append({"id": "official-manifest", "status": "pass"})
        source_manifest = _check_versioned_object(
            root / "SOURCE-MANIFEST.json",
            {"schema_version", "project", "components"},
            {"schema_version", "project", "components"},
        )
        if source_manifest["project"] != "reverse-fusion" or not isinstance(source_manifest["components"], list):
            raise ContractError("SOURCE-MANIFEST.json has invalid project/components")
        _check_unique_ids(source_manifest["components"], "source manifest components")
        if {item.get("id") for item in source_manifest["components"]} != {item.get("id") for item in manifest["components"]}:
            raise ContractError("source manifest component ids drift from official manifest")
        checks.append({"id": "source-manifest", "status": "pass"})
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
            if not isinstance(value.get("components"), list) or not value["components"]:
                raise ContractError(f"profile {profile} must select at least one component")
            checks.append({"id": f"profile:{profile}", "status": "pass"})
    except ContractError as exc:
        checks.append({"id": "contracts", "status": "fail", "detail": str(exc)})
        return {"status": "fail", "checks": checks}
    return {"status": "pass", "checks": checks}
