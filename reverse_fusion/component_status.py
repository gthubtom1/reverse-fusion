"""Local component discovery. Presence is never reported as a live tool handshake."""
from __future__ import annotations

import json
import os
import re
import shutil
import subprocess
from pathlib import Path


def component_status(root: Path) -> dict:
    manifest = json.loads((root / 'vendor/rea/manifest.json').read_text(encoding='utf-8'))
    entry = root / 'vendor/rea' / manifest['entry']
    package_file = root / 'vendor/rea/package/package.json'
    rea_status = 'not-installed'
    if entry.is_file() and package_file.is_file():
        try:
            package = json.loads(package_file.read_text(encoding='utf-8'))
            matches = (package.get('name') == manifest['package']
                       and package.get('version') == manifest['version']
                       and package.get('engines', {}).get('node') == manifest['node_engine'])
            rea_status = 'present-unverified' if matches else 'identity-mismatch'
        except (OSError, ValueError, AttributeError):
            rea_status = 'identity-mismatch'
    specify = shutil.which('specify')
    node = os.environ.get('REVERSE_FUSION_NODE') or shutil.which('node')
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
    return {
        'reverse': {'status': 'repository-local', 'router': str(root / 'components/reverse-core/router.py'),
                    'boundary': 'route availability is checked by contracts; target analysis is separate'},
        'rea': {'status': rea_status, 'entry': str(entry), 'version_pin': manifest['version'],
                'node_engine': manifest['node_engine'], 'node': node,
                'node_version': node_version, 'node_engine_status': engine_status,
                'handshake': 'unverified', 'provider_health': 'unverified',
                'next_action': 'Use scripts/bootstrap-rea.ps1 on Windows when REA is needed; check the pinned Node engine and then the actual REA catalog/provider before use. A source manifest is not an installed runtime.'},
        'spec': {'cli': specify, 'cli_status': 'present-unverified' if specify else 'not-installed',
                 'task_files': 'authorable-by-current-host',
                 'boundary': 'tasks must be evidence-linked and frozen before implementation; local files do not prove official Spec CLI execution'},
        'builder': {'backend': 'current-session', 'status': 'available-interface',
                    'boundary': 'run session prepare/check/refine/finish in the selected project; direct host edits alone are not an observed Builder session'},
        'craft': {'distribution': 'repository-interface-only', 'native_backend': 'unsupported',
                  'boundary': 'the craft command copies a fixture; it does not start native Craft or implement an application'},
    }
