from __future__ import annotations

import json
import re
from hashlib import sha256
from pathlib import Path
from pathlib import PurePosixPath, PureWindowsPath
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


def is_safe_relative_path(value: str) -> bool:
    """Reject POSIX and Windows absolute/traversal paths on every host."""
    if not isinstance(value, str) or not value.strip():
        return False
    if not PurePosixPath(value).parts or PureWindowsPath(value).drive or PureWindowsPath(value).root:
        return False
    for path_type in (PurePosixPath, PureWindowsPath):
        path = path_type(value)
        if path.is_absolute() or any(part in {"", ".", ".."} for part in path.parts):
            return False
    return True


def _is_relative_safe(value: str) -> bool:
    return is_safe_relative_path(value)


def _check_unique_ids(items: Iterable[dict[str, Any]], label: str) -> None:
    seen: set[str] = set()
    for index, item in enumerate(items):
        if not isinstance(item, dict):
            raise ContractError(f"{label}[{index}] must be an object")
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
    if (type(value["version"]) is not int or value["version"] != 1
            or not isinstance(value["root"], str) or not value["root"]
            or not isinstance(value["artifacts"], list)
            or any(not isinstance(artifact, dict) for artifact in value["artifacts"])):
        raise ContractError("external baseline has invalid version/root/artifacts")
    digest = value["bundle_sha256"]
    if not isinstance(digest, str) or len(digest) != 64 or any(char not in "0123456789abcdef" for char in digest):
        raise ContractError("external baseline bundle_sha256 must be lowercase SHA-256")
    return value


def validate_candidate_result(value: dict[str, Any]) -> dict[str, Any]:
    required = {"version", "disposition", "tasks", "checks", "cleanup"}
    allowed = required | {
        "reason", "result", "task_digest", "model_id", "research_ref", "backend", "host",
        "host_result", "output", "candidate_sha256", "source_sha256", "refine_result",
        "operation", "source", "workspace", "model_selection",
    }
    missing = sorted(required - value.keys())
    unknown = sorted(set(value) - allowed)
    if missing or unknown or type(value.get("version")) is not int or value.get("version") != 1:
        raise ContractError(f"candidate result missing={missing} unknown={unknown} or version is not 1")
    if value["disposition"] not in {"candidate", "needs-evidence", "needs-spec", "needs-scope", "unsupported", "failed", "blocked", "blocked-cleanup"}:
        raise ContractError("candidate result has invalid disposition")
    if not isinstance(value["tasks"], list) or not isinstance(value["checks"], list) or not isinstance(value["cleanup"], dict):
        raise ContractError("candidate result tasks/checks/cleanup have invalid types")
    if any(not isinstance(task, str) for task in value["tasks"]):
        raise ContractError("candidate result tasks must contain strings")
    for check in value["checks"]:
        if not isinstance(check, dict) or not isinstance(check.get("id"), str) or not isinstance(check.get("status"), str):
            raise ContractError("candidate result checks must contain id and status strings")
    if not isinstance(value["cleanup"].get("status"), str):
        raise ContractError("candidate result cleanup must contain a status string")
    string_fields = {
        "task_digest", "model_id", "research_ref", "backend", "host", "output",
        "operation", "source", "workspace", "model_selection",
    }
    for key in string_fields & value.keys():
        if not isinstance(value[key], str):
            raise ContractError(f"candidate result {key} must be a string")
    if "reason" in value and value["reason"] is not None and not isinstance(value["reason"], str):
        raise ContractError("candidate result reason must be a string or null")
    for key in {"host_result", "refine_result"} & value.keys():
        if not isinstance(value[key], dict):
            raise ContractError(f"candidate result {key} must be an object")
    for key in {"candidate_sha256", "source_sha256"} & value.keys():
        digest = value[key]
        if not isinstance(digest, str) or not re.fullmatch(r"[0-9a-f]{64}", digest):
            raise ContractError(f"candidate result {key} must be lowercase SHA-256")
    return value


def validate_handoff(value: dict[str, Any]) -> dict[str, Any]:
    required = {"version", "case", "original", "implementation", "baseline", "checks", "builder", "owner"}
    allowed = required
    missing = sorted(required - value.keys())
    unknown = sorted(set(value) - allowed)
    if missing or unknown or type(value.get("version")) is not int or value.get("version") != 1:
        raise ContractError(f"handoff missing={missing} unknown={unknown} or version is not 1")
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


def _check_reverse_support(root: Path, route_ids: set[str]) -> dict[str, Any]:
    """Check inherited content and runtime dependencies in the existing doctor.

    Digests describe content preservation, never successful target execution.
    Text line endings are normalized; the Gradle wrapper JAR is hashed as bytes.
    """
    base = root / "components" / "reverse-core"
    runtime = read_json(base / "runtime.json")
    try:
        if runtime["schema_version"] != 1:
            raise ContractError("reverse runtime version mismatch")
        hard = runtime["hard_target"]
        re.compile(hard["pattern"])
        groups = [runtime["base_reads"], hard["common_reads"]]
        for mapping in (runtime["route_reads"], hard["route_reads"]):
            if not isinstance(mapping, dict) or set(mapping) - route_ids:
                raise ContractError("reverse runtime references an unknown route")
            groups.extend(mapping.values())
        for paths in groups:
            if not isinstance(paths, list):
                raise ContractError("reverse runtime reads must be lists")
            for name in paths:
                if (not is_safe_relative_path(name)
                        or not (root / name).resolve().is_relative_to(root.resolve())
                        or not (root / name).is_file()):
                    raise ContractError(f"reverse runtime resource missing or unsafe: {name}")
    except (KeyError, TypeError, re.error) as exc:
        raise ContractError(f"invalid reverse runtime context: {exc}") from exc
    preserved = read_json(base / "preservation.json")
    files = preserved.get("files")
    if preserved.get("schema_version") != 1 or not isinstance(files, dict) or not files:
        raise ContractError("reverse preservation manifest is invalid")
    expected_groups = preserved.get("groups")
    if not isinstance(expected_groups, dict) or set(expected_groups) != {"skills", "CTF-Sandbox-Orchestrator", "burp-mcp-full"}:
        raise ContractError("reverse preservation groups are invalid")
    actual_groups = {
        "skills": sum(name.startswith("skills/") for name in files),
        "CTF-Sandbox-Orchestrator": sum(name.startswith("CTF-Sandbox-Orchestrator/") for name in files),
        "burp-mcp-full": sum(name.startswith("burp-mcp-full/") for name in files),
    }
    if actual_groups != expected_groups or sum(expected_groups.values()) != len(files):
        raise ContractError(f"reverse preservation group counts drift: expected={expected_groups} actual={actual_groups}")
    sources = read_json(root / "SOURCE-MANIFEST.json")["components"]
    origin = next((item for item in sources if item.get("id") == "reverse-domain-skills"), {})
    if preserved.get("source") != origin.get("source") or preserved.get("commit") != origin.get("commit"):
        raise ContractError("reverse preservation source identity differs from SOURCE-MANIFEST")
    for name, record in files.items():
        if not is_safe_relative_path(name) or not isinstance(record, dict):
            raise ContractError(f"invalid preserved Reverse resource: {name}")
        path = root / name
        if not path.resolve().is_relative_to(root.resolve()) or not path.is_file():
            raise ContractError(f"preserved Reverse resource missing: {name}")
        payload = path.read_bytes()
        if path.suffix != ".jar":
            payload = payload.replace(b"\r\n", b"\n")
        if sha256(payload).hexdigest() != record.get("sha256"):
            raise ContractError(f"preserved Reverse resource hash mismatch: {name}")
        if "upstream_sha256" in record and not record.get("patch_reason"):
            raise ContractError(f"preserved Reverse patch has no reason: {name}")
    return {"id": "reverse-support-preservation", "status": "pass", "files": len(files)}


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
            if not isinstance(component, dict):
                raise ContractError("official manifest components must be objects")
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
        if any(not isinstance(component, dict) for component in source_manifest["components"]):
            raise ContractError("source manifest components must be objects")
        if {item.get("id") for item in source_manifest["components"]} != {item.get("id") for item in manifest["components"]}:
            raise ContractError("source manifest component ids drift from official manifest")
        checks.append({"id": "source-manifest", "status": "pass"})
        routing_path = root / "components" / "reverse-core" / "routing.json"
        routing = read_json(routing_path)
        routes = routing.get("routes")
        priority = routing.get("priority")
        if not isinstance(routes, dict) or not isinstance(priority, list) or set(routes) != set(priority):
            raise ContractError("reverse routing manifest routes and priority diverge")
        for route_id, route in routes.items():
            if not isinstance(route, dict) or not isinstance(route.get("skill"), str):
                raise ContractError(f"reverse route {route_id} is missing a local skill reference")
            descriptor_path = root / "components" / "reverse-core" / "routes" / f"{route_id}.md"
            if not descriptor_path.is_file():
                raise ContractError(f"reverse route descriptor missing: {route_id}")
            if not (root / "skills" / route["skill"]).is_file():
                raise ContractError(f"reverse domain skill missing: {route['skill']}")
            try:
                descriptor = descriptor_path.read_text(encoding="utf-8")
            except (OSError, UnicodeError) as exc:
                raise ContractError(f"reverse route descriptor unreadable: {route_id}: {exc}") from exc
            expected_heading = f"# {route_id}: {route.get('label', '')}"
            if expected_heading not in descriptor:
                raise ContractError(f"reverse route descriptor identity drift: {route_id}")
            expected_route_id = f"- Route id: `{route_id}`"
            if expected_route_id not in descriptor:
                raise ContractError(f"reverse route descriptor id drift: {route_id}")
            expected_skill = f"- Local skill: `skills/{route['skill']}`"
            if expected_skill not in descriptor:
                raise ContractError(f"reverse route descriptor skill drift: {route_id}")
        checks.append({"id": "reverse-routing-and-skills", "status": "pass", "routes": len(routes)})
        checks.append(_check_reverse_support(root, set(routes)))
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
        craft = read_json(root / "components" / "craft-bounded" / "bundle-manifest.json")
        required_capabilities = ["prepare", "build", "check", "refine", "return_summary", "cleanup"]
        if craft.get("version") != 1 or craft.get("required_capabilities") != required_capabilities:
            raise ContractError("Craft bundle manifest does not contain the exact six-tool gate")
        if craft.get("distribution") != "pinned-native-engine-adapter" or not craft.get("patch_series"):
            raise ContractError("Craft must declare its actual engine adapter and replayable patches")
        native = read_json(root / 'components/craft-native/manifest.json')
        if native.get('upstream', {}).get('commit') != craft['upstream']['commit']:
            raise ContractError('Craft adapter and upstream pins differ')
        for patch in native.get('patches', []):
            name = patch['path']
            if not is_safe_relative_path(name) or sha256_file(root / name) != patch['sha256']:
                raise ContractError('Craft replayable patch identity mismatch')
        if [patch['path'] for patch in native.get('patches', [])] != craft['patch_series']:
            raise ContractError('Craft patch series differs from native source manifest')
        for asset in native.get('platforms', {}).values():
            for field in ('binary_sha256', 'archive_sha256', 'notices_sha256'):
                if not re.fullmatch('[a-f0-9]{64}', asset.get(field, '')):
                    raise ContractError(f'Craft distribution digest missing: {field}')
        for name in ('scripts/bootstrap-craft.ps1', 'scripts/bootstrap-spec.ps1', 'scripts/bootstrap-core.ps1',
                     'components/craft-native/src/main.rs', 'components/craft-native/Cargo.lock'):
            if not (root / name).is_file():
                raise ContractError(f'Required native component distribution file missing: {name}')
        if len(craft.get("historical_patch_series", [])) != 4:
            raise ContractError("Craft adapter must preserve the four historical patch references")
        checks.append({"id": "craft-bundle-manifest", "status": "pass"})
        wabt = read_json(root / "vendor" / "wabt" / "1.0.42" / "manifest.json")
        if wabt.get("version") != "1.0.42" or wabt.get("platform") != "windows-x64":
            raise ContractError("WABT manifest identity mismatch")
        if not isinstance(wabt.get("archive_sha256"), str) or len(wabt["archive_sha256"]) != 64:
            raise ContractError("WABT manifest archive hash is malformed")
        if wabt.get("required_tools") != ["wasm-validate.exe", "wasm-objdump.exe", "wasm2wat.exe", "wasm-interp.exe"]:
            raise ContractError("WABT manifest required tool set drifted")
        for rel in ("scripts/bootstrap-wabt.ps1", "scripts/bootstrap-rea.ps1", "scripts/bootstrap-jadx.ps1", "scripts/run-rea-doctor.ps1", "scripts/run-rea-wasm.ps1", "scripts/run-wasm-vertical.ps1", "scripts/run-rea-ledger.ps1", "scripts/run-rea-ledger.mjs", "scripts/run-web-proof.mjs", "scripts/run-web-vertical.ps1", "scripts/run-dotnet-proof.mjs", "scripts/run-dotnet-vertical.ps1", "scripts/run-apk-proof.mjs", "scripts/run-apk-vertical.ps1", "scripts/run-host-handshakes.ps1", "scripts/install.ps1", "scripts/install.sh", "scripts/uninstall.ps1"):
            if not (root / rel).is_file():
                raise ContractError(f"WABT/REA reproducibility script missing: {rel}")
        checks.append({"id": "wabt-reproducibility", "status": "pass"})
        jadx = read_json(root / "vendor" / "jadx-headless-mcp" / "0.7.1" / "manifest.json")
        if jadx.get("provider") != "jadx-headless-mcp" or jadx.get("version") != "0.7.1":
            raise ContractError("JADX headless MCP manifest identity mismatch")
        if not isinstance(jadx.get("sha256"), str) or len(jadx["sha256"]) != 64:
            raise ContractError("JADX headless MCP manifest hash is malformed")
        if not isinstance(jadx.get("required_classes"), list) or len(jadx["required_classes"]) < 3:
            raise ContractError("JADX headless MCP manifest required classes are incomplete")
        if not (root / "scripts" / "bootstrap-jadx.ps1").is_file():
            raise ContractError("JADX provider bootstrap script missing")
        checks.append({"id": "jadx-reproducibility", "status": "pass"})
        rea_manifest = read_json(root / "vendor" / "rea" / "manifest.json")
        if rea_manifest.get("package") != "rea-agents" or rea_manifest.get("version") != "6.9.0":
            raise ContractError("REA local manifest identity mismatch")
        if not isinstance(rea_manifest.get("integrity"), str) or not rea_manifest["integrity"].startswith("sha512-"):
            raise ContractError("REA local manifest integrity missing")
        if rea_manifest.get("node_engine") != "^22.23.4 || ^24.22.1 || >=26.12.1":
            raise ContractError("REA Node engine differs from the official pinned package")
        checks.append({"id": "rea-reproducibility", "status": "pass"})
        for rel in ("docs/TARGET-CAPABILITY-MATRIX.md", "docs/FINAL-COMPLETION-SPEC.md", "docs/FINAL-RELEASE-ACCEPTANCE.md", "docs/DEPLOYMENT-GUIDE.md", "docs/AGENT-WORKFLOW.md", "docs/BEGINNER-GUIDE.md"):
            if not (root / rel).is_file():
                raise ContractError(f"final v1 document missing: {rel}")
        checks.append({"id": "final-v1-documents", "status": "pass"})
        evidence_manifest = read_json(root / "evidence" / "rf22" / "manifest.json")
        targets = evidence_manifest.get("targets")
        if evidence_manifest.get("schema_version") != 1 or not isinstance(targets, dict) or set(targets) != {"wasm", "web", "dotnet", "apk"}:
            raise ContractError("RF-22 evidence manifest must contain all four representative targets")
        for target, record in targets.items():
            files = record.get("files") if isinstance(record, dict) else None
            if not isinstance(files, dict) or not files:
                raise ContractError(f"RF-22 evidence manifest has no files for {target}")
            for name, metadata in files.items():
                path = root / "evidence" / "rf22" / target / name
                if (not is_safe_relative_path(name) or not path.resolve().is_relative_to(root.resolve())
                        or not path.is_file() or not isinstance(metadata, dict) or metadata.get("sha256") != sha256_file(path)):
                    raise ContractError(f"RF-22 evidence hash mismatch: {target}/{name}")
        checks.append({"id": "rf22-evidence-manifest", "status": "pass"})
        for rel in (
            "specs/console-project/.specify/integration.json",
            "specs/console-project/specs/001-console-contract/spec.md",
            "specs/console-project/specs/001-console-contract/plan.md",
            "specs/console-project/specs/001-console-contract/tasks.md",
            "specs/console-project/specs/001-console-contract/converge.md",
        ):
            if not (root / rel).is_file():
                raise ContractError(f"Spec Kit project artifact missing: {rel}")
        checks.append({"id": "spec-kit-project", "status": "pass"})
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
