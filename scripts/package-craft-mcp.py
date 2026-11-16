"""Package the pinned full Craft MCP launcher with complete dependency notices.

Maintainer operation only. Does not publish, start a model or claim acceptance.
Existing native adapter packaging remains unchanged.
"""
from pathlib import Path
import hashlib
import json
import os
import subprocess
import zipfile


root = Path(__file__).resolve().parents[1]
manifest_path = root / 'components/craft-mcp/manifest.json'
manifest = json.loads(manifest_path.read_text(encoding='utf-8'))
asset = manifest['platforms']['windows-x64']
binary = root / asset['local_path']
if not binary.is_file():
    raise SystemExit('Build and qualify the Craft MCP executable before packaging')
metadata = json.loads(subprocess.check_output([
    os.environ.get('RF_CARGO', 'cargo'), 'metadata', '--locked', '--format-version', '1',
    '--filter-platform', 'x86_64-pc-windows-gnu', '--manifest-path',
    str(root / 'components/craft-mcp/Cargo.toml')]))
notices = [
    'Reverse Fusion Craft MCP launcher (MIT). Upstream Craft: MIT OR Apache-2.0.\n'
    'Source, pinned patch and build instructions: https://github.com/gthubtom1/reverse-fusion\n'
    'Original Craft MCP protocol and tools; dependency license texts follow.\n'
]
inventory = []
extra_licenses = json.loads((root / 'components/craft-native/licenses/manifest.json').read_text(encoding='utf-8'))
for package in sorted(metadata['packages'], key=lambda item: (item['name'], item['version'])):
    source = Path(package['manifest_path']).parent
    files = sorted({path for path in source.iterdir() if path.is_file()
                    and path.name.lower().startswith(('license', 'licence', 'copying', 'notice'))})
    if package['name'].startswith('craft-anything-') and not files:
        files = sorted((root / 'vendor/craft/upstream').glob('LICENSE-*'))
    if package['name'] == 'reverse-fusion-craft-mcp':
        files = [root / 'vendor/craft/upstream/LICENSE-MIT']
    if not files:
        files = sorted(path for path in source.rglob('*') if path.is_file()
                       and path.name.lower().startswith(('license', 'licence', 'copying', 'notice')))
    if not files:
        for record in extra_licenses:
            if package['name'] in record['packages']:
                path = root / record['path']
                if hashlib.sha256(path.read_bytes()).hexdigest() != record['sha256']:
                    raise SystemExit('Supplemental license identity changed')
                files.append(path)
    if not files:
        raise SystemExit(f'Missing license text for {package["name"]} {package["version"]}')
    notices.append(f'\n=== {package["name"]} {package["version"]}: {package.get("license")} ===\n')
    license_files = []
    for path in files:
        data = path.read_bytes()
        notices.append(path.name + '\n' + data.decode('utf-8', errors='replace') + '\n')
        license_files.append({'name': path.name, 'sha256': hashlib.sha256(data).hexdigest()})
    inventory.append({'name': package['name'], 'version': package['version'],
                      'license': package.get('license'), 'source': package.get('source'),
                      'license_files': license_files})
runtime_licenses = Path(os.environ.get('RF_MINGW_LICENSES', ''))
if not runtime_licenses.is_dir():
    raise SystemExit('Set RF_MINGW_LICENSES to the build toolchain licenses directory')
for directory in ('gcc', 'mingw-w64'):
    paths = sorted(path for path in (runtime_licenses / directory).rglob('*') if path.is_file())
    if not paths:
        raise SystemExit(f'Missing {directory} runtime license texts')
    for path in paths:
        notices.append(f'\n=== {directory}/{path.name} ===\n'
                       + path.read_text(encoding='utf-8', errors='replace'))
package_dir = root / 'vendor/craft/mcp'
package_dir.mkdir(parents=True, exist_ok=True)
notice = package_dir / 'THIRD-PARTY-NOTICES.txt'
notice.write_bytes('\n'.join(notices).encode('utf-8'))
inventory_path = root / 'components/craft-mcp/dependency-notices.json'
inventory_path.write_bytes((json.dumps(inventory, indent=2) + '\n').encode('utf-8'))
archive = package_dir / 'craft-mcp-windows-x64.zip'
with zipfile.ZipFile(archive, 'w', compression=zipfile.ZIP_DEFLATED, compresslevel=9) as bundle:
    for file in (binary, notice, inventory_path):
        entry = zipfile.ZipInfo(file.name, date_time=(1980, 1, 1, 0, 0, 0))
        entry.compress_type = zipfile.ZIP_DEFLATED
        bundle.writestr(entry, file.read_bytes())
asset.update(binary_sha256=hashlib.sha256(binary.read_bytes()).hexdigest(),
             archive_sha256=hashlib.sha256(archive.read_bytes()).hexdigest(),
             notices_sha256=hashlib.sha256(notice.read_bytes()).hexdigest(),
             dependency_notices_sha256=hashlib.sha256(inventory_path.read_bytes()).hexdigest())
manifest['adapter_source_sha256'] = {
    name: hashlib.sha256((root / name).read_bytes().replace(b'\r\n', b'\n')).hexdigest()
    for name in ('components/craft-mcp/src/main.rs', 'components/craft-mcp/Cargo.toml',
                 'components/craft-mcp/Cargo.lock')}
manifest_path.write_bytes((json.dumps(manifest, indent=2) + '\n').encode('utf-8'))
print(json.dumps({'archive': str(archive), 'sha256': asset['archive_sha256'],
                  'binary_sha256': asset['binary_sha256'], 'packages': len(inventory)}))
