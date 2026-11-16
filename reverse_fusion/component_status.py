"""Local component discovery. Presence is never reported as a live tool handshake."""
from __future__ import annotations

import json
import re
import subprocess
import os
from hashlib import sha256

from .runtime import node_runtime
from pathlib import Path
from .craft_native import native_binary
from .craft_mcp import mcp_binary
from .contracts import is_safe_relative_path


def core_deployment(components: dict) -> dict:
    missing = []
    if components['rea']['status'] != 'present-unverified' or components['rea']['node_engine_status'] != 'satisfied':
        missing.append('rea')
    if components['spec']['cli_status'] != 'installed':
        missing.append('spec-kit')
    if components['craft']['native_backend'] != 'installed-identity-verified':
        missing.append('craft-native')
    if components['craft'].get('mcp_backend') != 'installed-identity-verified':
        missing.append('craft-mcp')
    return {'status': 'installed' if not missing else 'incomplete', 'missing': missing,
            'scope': 'required runtime installation; generated workflow and target acceptance remain separate'}


def _spec_status(root: Path) -> dict:
    scripts = root / '.venv' / ('Scripts' if os.name == 'nt' else 'bin')
    cli = scripts / ('specify.exe' if os.name == 'nt' else 'specify')
    python = scripts / ('python.exe' if os.name == 'nt' else 'python')
    result = {'cli': str(cli), 'cli_status': 'not-installed', 'version': None,
              'workflow_acceptance': 'not-performed',
              'boundary': 'installed CLI is required; execute its generated project skills/scripts for actual Spec workflow'}
    if cli.is_file() and python.is_file():
        try:
            pin = json.loads((root / 'vendor/spec-kit/manifest.json').read_text(encoding='utf-8'))
            probe = subprocess.run([str(python), '-c', 'import importlib.metadata; print(importlib.metadata.version("specify-cli"))'],
                                   capture_output=True, text=True, timeout=10)
            version = probe.stdout.strip()
            receipt = json.loads((root / 'state/spec-runtime.json').read_text(encoding='utf-8-sig'))
            result['version'] = version
            result['cli_status'] = 'installed' if (probe.returncode == 0 and version == pin['version']
                and receipt['source_commit'] == pin['commit'] and Path(receipt['repository_root']).resolve() == root.resolve()) else 'identity-mismatch'
        except (OSError, ValueError, KeyError, subprocess.SubprocessError):
            result['cli_status'] = 'identity-unverified'
    return result


def _craft_status(root: Path) -> dict:
    result = {'distribution': 'pinned-native-engine-adapter', 'native_backend': 'not-installed',
              'handshake': 'unverified', 'business_acceptance': 'not-performed',
              'boundary': 'native-craft drives actual Craft engine; the legacy craft copy command is not this backend'}
    try:
        binary = native_binary(root)
        result.update({'native_backend': 'installed-identity-verified', 'binary': str(binary)})
    except (OSError, ValueError, KeyError) as exc:
        result['reason'] = str(exc)
    try:
        binary = mcp_binary(root)
        result.update(mcp_backend='installed-identity-verified', mcp_binary=str(binary))
    except (OSError, ValueError, KeyError) as exc:
        result.update(mcp_backend='not-installed', mcp_reason=str(exc))
    return result


def component_status(root: Path) -> dict:
    manifest = json.loads((root / 'vendor/rea/manifest.json').read_text(encoding='utf-8'))
    entry = root / 'vendor/rea' / manifest['entry']
    package_file = root / 'vendor/rea/package/package.json'
    rea_status = 'not-installed'
    methods_status = 'not-installed'
    if entry.is_file() and package_file.is_file():
        try:
            package = json.loads(package_file.read_text(encoding='utf-8'))
            matches = (package.get('name') == manifest['package']
                       and package.get('version') == manifest['version']
                       and package.get('engines', {}).get('node') == manifest['node_engine'])
            rea_status = 'present-unverified' if matches else 'identity-mismatch'
        except (OSError, ValueError, AttributeError):
            rea_status = 'identity-mismatch'
    methods = manifest.get('method_files_sha256', {})
    if methods and isinstance(methods, dict):
        valid = all(is_safe_relative_path(name) and (root/'vendor/rea'/name).resolve().is_relative_to((root/'vendor/rea').resolve())
                    and (root/'vendor/rea'/name).is_file()
                    and sha256((root/'vendor/rea'/name).read_bytes()).hexdigest() == digest
                    for name,digest in methods.items())
        methods_status = 'installed-identity-verified' if valid else 'missing-or-changed'
    if rea_status == 'present-unverified' and methods_status != 'installed-identity-verified':
        rea_status = 'methods-incomplete'
    node, node_source = node_runtime(root)
    node_version, engine_status = None, 'missing'
    if node:
        try:
            probe = subprocess.run([node, '--version'], capture_output=True, text=True,
                                   encoding='utf-8', errors='replace', timeout=5, check=False)
            match = re.fullmatch(r'v?(\d+)\.(\d+)\.(\d+)', probe.stdout.strip())
            engine_status = 'unknown'
            if probe.returncode == 0 and match:
                version = tuple(map(int, match.groups()))
                node_version = probe.stdout.strip()
                supported = ((version[0] == 22 and version >= (22, 23, 4))
                             or (version[0] == 24 and version >= (24, 22, 1))
                             or version >= (26, 12, 1))
                engine_status = 'satisfied' if supported else 'blocked'
        except (OSError, subprocess.SubprocessError):
            engine_status = 'unknown'
    craft = _craft_status(root)
    return {
        'reverse': {'status': 'repository-local', 'router': str(root / 'components/reverse-core/router.py'),
                    'boundary': 'route availability is checked by contracts; target analysis is separate'},
        'rea': {'status': rea_status, 'entry': str(entry), 'version_pin': manifest['version'],
                'methods_status':methods_status,
                'official_skill':str(root/'vendor/rea/package/skills/reverse-engineer-anything/SKILL.md'),
                'node_engine': manifest['node_engine'], 'node': node,
                'node_source': node_source,
                'node_version': node_version, 'node_engine_status': engine_status,
                'handshake': 'unverified', 'provider_health': 'unverified',
                'next_action': 'Use scripts/bootstrap-rea.ps1 on Windows when REA is needed; check the pinned Node engine and then the actual REA catalog/provider before use. A source manifest is not an installed runtime.'},
        'spec': _spec_status(root),
        'builder': {'backend': 'host-reasoning-with-native-craft', 'status': craft['native_backend'],
                    'boundary': 'review analysis and execute official Spec workflow before native-craft prepare/build/check/refine/return_summary/cleanup; session is an auxiliary boundary observer, not the implementation engine'},
        'craft': craft,
    }
