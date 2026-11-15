"""Package a qualified local Craft build with dependency license texts.

Maintainer operation, after build/tests. Does not publish or claim acceptance.
"""
from pathlib import Path
import hashlib
import json
import os
import subprocess
import zipfile

root = Path(__file__).resolve().parents[1]
manifest_path = root / 'components/craft-native/manifest.json'
manifest = json.loads(manifest_path.read_text())
asset = manifest['platforms']['windows-x64']
binary = root / asset['local_path']
metadata = json.loads(subprocess.check_output([
    os.environ.get('RF_CARGO', 'cargo'), 'metadata', '--locked', '--format-version', '1',
    '--filter-platform', 'x86_64-pc-windows-gnu', '--manifest-path', str(root / 'components/craft-native/Cargo.toml')]))
notices = ['Reverse Fusion Craft native adapter. Upstream Craft: MIT OR Apache-2.0.\n'
           'Source, pinned patch and build instructions: https://github.com/gthubtom1/reverse-fusion\n'
           'The adapter is supplied under MIT. Dependency notices follow.\n']
inventory = []
extra_licenses = json.loads((root / 'components/craft-native/licenses/manifest.json').read_text())
for package in sorted(metadata['packages'], key=lambda p: (p['name'], p['version'])):
    source = Path(package['manifest_path']).parent
    files = sorted({p for p in source.iterdir() if p.is_file()
                    and p.name.lower().startswith(('license', 'licence', 'copying', 'notice'))})
    if package['name'].startswith('craft-anything-') and not files:
        files = sorted((root / 'vendor/craft/upstream').glob('LICENSE-*'))
    if package['name'] == 'reverse-fusion-craft-native':
        files = [root / 'vendor/craft/upstream/LICENSE-MIT']
    if not files:
        # Some packages keep text in a nested licenses directory.
        files = sorted(p for p in source.rglob('*') if p.is_file() and
                       p.name.lower().startswith(('license', 'licence', 'copying', 'notice')))
    if not files:
        for record in extra_licenses:
            if package['name'] in record['packages']:
                path = root / record['path']
                if hashlib.sha256(path.read_bytes()).hexdigest() != record['sha256']:
                    raise SystemExit('Supplemental license identity changed')
                files.append(path)
    if not files:
        raise SystemExit(f'Missing license text for {package["name"]} {package["version"]}')
    header = f'\n=== {package["name"]} {package["version"]}: {package.get("license")} ===\n'
    notices.append(header)
    for path in files:
        notices.append(path.name + '\n' + path.read_text(encoding='utf-8', errors='replace') + '\n')
    inventory.append({'name': package['name'], 'version': package['version'],
                      'license': package.get('license'), 'source': package.get('source')})
runtime_licenses = Path(os.environ.get('RF_MINGW_LICENSES', ''))
if not runtime_licenses.is_dir():
    raise SystemExit('Set RF_MINGW_LICENSES to the build toolchain licenses directory')
for directory in ('gcc', 'mingw-w64'):
    paths = sorted(p for p in (runtime_licenses / directory).rglob('*') if p.is_file())
    if not paths:
        raise SystemExit(f'Missing {directory} runtime license texts')
    for path in paths:
        notices.append(f'\n=== {directory}/{path.name} ===\n' + path.read_text(encoding='utf-8', errors='replace'))
notice = root / 'vendor/craft/native/THIRD-PARTY-NOTICES.txt'
notice.write_text('\n'.join(notices), encoding='utf-8')
archive = root / 'vendor/craft/native/craft-native-windows-x64.zip'
with zipfile.ZipFile(archive, 'w', compression=zipfile.ZIP_DEFLATED, compresslevel=9) as bundle:
    bundle.write(binary, binary.name)
    bundle.write(notice, notice.name)
asset.update(binary_sha256=hashlib.sha256(binary.read_bytes()).hexdigest(),
             archive_sha256=hashlib.sha256(archive.read_bytes()).hexdigest(),
             notices_sha256=hashlib.sha256(notice.read_bytes()).hexdigest())
manifest_path.write_text(json.dumps(manifest, indent=2) + '\n', encoding='utf-8')
(root / 'components/craft-native/dependency-notices.json').write_text(json.dumps(inventory, indent=2) + '\n')
print(json.dumps({'archive': str(archive), 'sha256': asset['archive_sha256'], 'packages': len(inventory)}))
