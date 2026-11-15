"""Resolve a repository-owned runtime without changing the host's PATH."""
from __future__ import annotations

import json
import os
from pathlib import Path
import shutil


def node_runtime(root: Path) -> tuple[str | None, str]:
    explicit = os.environ.get('REVERSE_FUSION_NODE')
    if explicit:
        return explicit, 'environment'
    try:
        receipt = json.loads((root / 'state/rea-runtime.json').read_text(encoding='utf-8-sig'))
        candidate = Path(receipt['node'])
        if (receipt.get('schema_version') == 1
                and Path(receipt['repository_root']).is_absolute()
                and Path(receipt['repository_root']).resolve() == root.resolve()
                and candidate.is_absolute() and candidate.is_file()):
            return str(candidate), 'repository-receipt'
    except (OSError, ValueError, TypeError, KeyError):
        pass
    return shutil.which('node'), 'path'
