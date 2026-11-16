"""Finite engineering-delivery checks, distinct from target acceptance."""
from __future__ import annotations

import json
import platform
import tomllib
from pathlib import Path

from . import __version__
from .component_status import component_status, core_deployment
from .contracts import check_contracts, is_safe_relative_path
from .global_adapter import adapter_paths, agents_block, skill_text
from .verification import verification_status
from .mcp_adapter import inspect_mcp
from .mcp_probe import connection_status


def check_release(root: Path, *, deployed: bool = False) -> dict:
    root = root.resolve()
    gates = []

    def gate(name, passed, detail):
        gates.append({'id': name, 'status': 'pass' if passed else 'fail', 'detail': detail})

    contract = check_contracts(root)
    gate('repository-contracts', contract['status'] == 'pass', contract['checks'])
    try:
        release = json.loads((root / 'release/manifest.json').read_text(encoding='utf-8'))
        package = tomllib.loads((root / 'pyproject.toml').read_text(encoding='utf-8'))
        gate('version', release['version'] == __version__ == package['project']['version'] ==
             (root / 'VERSION').read_text(encoding='utf-8').strip(), __version__)
        gate('edition', release['schema_version'] == 1 and release['edition'] == 'windows-x64-codex'
             and release['target_execution_required'] is False, release['edition'])
        requirements = release['requirements']
        valid = isinstance(requirements, list) and len(requirements) >= 8
        valid = valid and len({item['id'] for item in requirements}) == len(requirements)
        gate('delivery-contract', valid, 'finite code/document/installation scope; no target-equivalence claim')
        for item in requirements:
            paths = item['files']
            present = bool(paths) and all(is_safe_relative_path(name) and
                      (root / name).resolve().is_relative_to(root) and
                      (root / name).is_file() and (root / name).stat().st_size > 0 for name in paths)
            gate(item['id'], present, {'responsibility': item['responsibility'], 'files': paths})
        # Verify actual entry capabilities, not merely a list of command names in a document.
        from .cli import build_parser
        parser = build_parser()
        for argv in release['entry_contracts']:
            parsed = parser.parse_args(argv)
            if not callable(parsed.handler):
                raise ValueError('Missing CLI handler')
        gate('executable-handoffs', True, release['entry_contracts'])
    except (OSError, ValueError, KeyError, TypeError, SystemExit) as exc:
        gate('release-contract', False, str(exc))
    if deployed:
        verified = verification_status(root)
        gate('source-bound-regressions', verified['status'] == 'pass', verified)
        gate('supported-host', platform.system() == 'Windows' and
             platform.machine().lower() in {'amd64', 'x86_64'}, 'current release deployment is Windows x64 + Codex')
        components = component_status(root)
        deployment = core_deployment(components)
        gate('installed-core', deployment['status'] == 'installed', deployment)
        mcp = inspect_mcp(root)
        gate('deployed-mcp', mcp.get('enabled') is True, mcp)
        protocol = connection_status(root)
        gate('mcp-protocol-calls', protocol['status'] == 'pass', protocol)
        try:
            receipt = json.loads((root / 'state/install.json').read_text(encoding='utf-8'))
            gate('selected-host-install', receipt.get('installed') is True and receipt.get('version') == __version__
                 and receipt['host']['client'] == 'codex' and receipt['global_adapter']['enabled'] is True
                 and Path(receipt['global_adapter']['repository']).resolve() == root,
                 'current version, this checkout, selected Codex host and global adapter')
            paths = adapter_paths()
            installed_skill = paths['skill'].read_text(encoding='utf-8').replace('\r\n', '\n')
            installed_agents = paths['agents'].read_text(encoding='utf-8').replace('\r\n', '\n')
            gate('deployed-entry', installed_skill == skill_text(root).replace('\r\n', '\n')
                 and agents_block(root) in installed_agents, {key: str(value) for key, value in paths.items()})
        except (OSError, ValueError, KeyError, TypeError) as exc:
            gate('deployed-entry', False, str(exc))
    return {'operation': 'release-check', 'version': __version__,
            'edition': 'windows-x64-codex', 'status': 'ready' if all(g['status'] == 'pass' for g in gates) else 'blocked',
            'scope': 'engineering delivery and optional installed identities; no real-target execution',
            'target_acceptance': 'not-performed', 'checks': gates,
            'host_adaptation': {
                'clients': ['codex', 'pi', 'claude'],
                'acceptance': 'shared core representative runs plus per-host entry/tool/workflow contract checks',
                'full_model_run_required_per_host': False,
                'deployed_check_scope': 'Windows x64/Codex global entry; Pi/Claude require explicit outcome-project connection',
            },
            'future_hosts': ['additional host adapters', 'non-Windows Craft distributions']}
