"""Identity of the full upstream Craft MCP launcher, distinct from the writer."""
from hashlib import sha256
import json
from pathlib import Path
import platform


def mcp_binary(root: Path) -> Path:
    manifest = json.loads((root / 'components/craft-mcp/manifest.json').read_text(encoding='utf-8'))
    system = {'Windows': 'windows', 'Linux': 'linux', 'Darwin': 'macos'}.get(platform.system(), 'unknown')
    machine = platform.machine().lower()
    architecture = 'x64' if machine in {'amd64', 'x86_64'} else 'arm64' if machine in {'arm64', 'aarch64'} else machine
    asset = manifest.get('platforms', {}).get(f'{system}-{architecture}')
    if not asset:
        raise ValueError(f'Craft MCP has no qualified distribution for {system}-{architecture}')
    binary = root / asset['local_path']
    if not binary.is_file():
        raise ValueError('Craft MCP binary missing; run scripts/bootstrap-craft-mcp.ps1')
    actual = sha256(binary.read_bytes()).hexdigest()
    names = {'components/craft-mcp/Cargo.toml', 'components/craft-mcp/Cargo.lock',
             *(path.relative_to(root).as_posix() for path in (root/'components/craft-mcp/src').rglob('*.rs'))}
    if 'components/craft-mcp/src/main.rs' not in names: raise ValueError('Craft MCP source entry missing')
    sources = manifest.get('adapter_source_sha256', {})
    matches = (set(sources) == names and all(
        sha256((root / name).read_bytes().replace(b'\r\n', b'\n')).hexdigest() == digest
        for name, digest in sources.items()))
    if actual == asset['binary_sha256'] and matches:
        return binary
    try:
        receipt = json.loads((root / 'state/craft-mcp-runtime.json').read_text(encoding='utf-8-sig'))
        expected = {*names, 'components/craft-mcp/manifest.json', *[item['path'] for item in manifest['patches']]}
        if (receipt.get('schema_version') != 1 or receipt.get('distribution') != 'source-build'
                or Path(receipt['repository_root']).resolve() != root.resolve()
                or receipt['binary_sha256'] != actual or set(receipt['source_inputs']) != expected
                or any(sha256((root / name).read_bytes()).hexdigest() != digest
                       for name, digest in receipt['source_inputs'].items())):
            raise ValueError('Craft MCP source receipt differs')
        return binary
    except (OSError, KeyError, TypeError, ValueError) as exc:
        raise ValueError('Craft MCP binary differs from source-bound installation') from exc
