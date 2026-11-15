"""Drive actual Craft engine operations, with the host as the single writer."""
from __future__ import annotations

from hashlib import sha256
import json
from pathlib import Path
import platform
import subprocess
import time
import os

from .session_builder import _inside, prepare_session


TOOL_ROOT = Path(__file__).resolve().parents[1]


def _spec_implementation_refs(project: Path, task_files: list[str]) -> list[str]:
    """Run actual official prerequisites; never infer semantic workflow completion."""
    pin = json.loads((TOOL_ROOT / 'vendor/spec-kit/manifest.json').read_text(encoding='utf-8'))
    runtime = json.loads((TOOL_ROOT / 'state/spec-runtime.json').read_text(encoding='utf-8-sig'))
    if (runtime.get('source_commit') != pin['commit'] or runtime.get('version') != pin['version']
            or Path(runtime['repository_root']).resolve() != TOOL_ROOT.resolve()):
        raise ValueError('Install the pinned official Spec Kit before native reconstruction')
    integration = json.loads(_inside(project, '.specify/integration.json').read_text(encoding='utf-8-sig'))
    feature = json.loads(_inside(project, '.specify/feature.json').read_text(encoding='utf-8-sig'))['feature_directory']
    if integration.get('version') != pin['version'] or f'{feature}/tasks.md' not in task_files:
        raise ValueError('Native reconstruction must use the current official Spec feature and its tasks')
    source = TOOL_ROOT / 'vendor/spec-kit/upstream'
    for name, expected in pin['prerequisite_scripts'].items():
        if sha256((source / name).read_bytes().replace(b'\r\n', b'\n')).hexdigest() != expected:
            raise ValueError('Official Spec prerequisite source changed')
    environment = {**os.environ, 'SPECIFY_INIT_DIR': str(project)}
    shell = 'pwsh' if os.name != 'nt' else 'powershell'
    run = subprocess.run([shell, '-NoProfile', '-File', str(source / 'scripts/powershell/check-prerequisites.ps1'),
                          '-Json', '-RequireSpec', '-RequireTasks', '-IncludeTasks'], cwd=project, env=environment,
                         capture_output=True, timeout=30)
    if run.returncode != 0:
        raise ValueError('Official Spec implementation prerequisites failed: ' + run.stderr.decode('utf-8', errors='replace'))
    # The official command can persist feature.json; freeze its final state below.
    refs = ['.specify/integration.json', '.specify/feature.json', '.specify/memory/constitution.md',
            f'{feature}/spec.md', f'{feature}/plan.md', f'{feature}/tasks.md']
    refs += [path.relative_to(project).as_posix() for path in (project / '.agents/skills').glob('speckit-*/SKILL.md')]
    if not refs[6:]:
        raise ValueError('Official generated Spec skills are missing; initialize the outcome project')
    for name in refs:
        if not _inside(project, name).read_bytes().strip():
            raise ValueError(f'Official Spec input is empty: {name}')
    return refs


def native_binary(root: Path = TOOL_ROOT) -> Path:
    manifest = json.loads((root / 'components/craft-native/manifest.json').read_text(encoding='utf-8'))
    key = {'Windows': 'windows', 'Linux': 'linux', 'Darwin': 'macos'}.get(platform.system(), 'unknown')
    machine = platform.machine().lower()
    arch = 'x64' if machine in {'amd64', 'x86_64'} else 'arm64' if machine in {'arm64', 'aarch64'} else machine
    asset = manifest.get('platforms', {}).get(f'{key}-{arch}')
    if not asset:
        raise ValueError(f'Craft native adapter needs a qualified build for {key}-{arch}')
    binary = root / asset['local_path']
    if not binary.is_file():
        raise ValueError('Craft native binary is missing; run the component bootstrap')
    actual = sha256(binary.read_bytes()).hexdigest()
    if actual != asset['binary_sha256']:
        try:
            receipt = json.loads((root / 'state/craft-runtime.json').read_text(encoding='utf-8-sig'))
            expected = {'components/craft-native/src/main.rs', 'components/craft-native/Cargo.toml',
                        'components/craft-native/Cargo.lock', 'components/craft-native/manifest.json',
                        *[p['path'] for p in manifest['patches']]}
            if (receipt.get('schema_version') != 1 or receipt.get('distribution') != 'source-build'
                    or Path(receipt['repository_root']).resolve() != root.resolve()
                    or receipt['binary_sha256'] != actual or set(receipt['source_inputs']) != expected
                    or any(sha256((root / name).read_bytes()).hexdigest() != digest
                           for name, digest in receipt['source_inputs'].items())):
                raise ValueError('Source-built Craft receipt or source identity changed')
        except (OSError, KeyError, TypeError, ValueError) as exc:
            raise ValueError('Craft native binary differs from its source-bound installation; run the component bootstrap') from exc
    return binary


def invoke_native(project: Path, *, lease: str | None = None, operation: str,
                  params: dict | None = None) -> dict:
    project = project.resolve()
    binary = native_binary()
    request = {'op': operation, 'params': params or {}}
    deadline = 15
    lease_path = None
    if lease:
        lease_path = _inside(project, lease)
        request['lease'] = str(lease_path)
        configuration = json.loads(lease_path.read_text(encoding='utf-8'))
        deadline += configuration['command_timeout_seconds']
    started = time.time()
    try:
        run = subprocess.run([str(binary)], input=json.dumps(request, ensure_ascii=True).encode('ascii'),
                             cwd=project, capture_output=True, timeout=deadline,
                             creationflags=getattr(subprocess, 'CREATE_NO_WINDOW', 0))
    except subprocess.TimeoutExpired as exc:
        raise ValueError('Native adapter exceeded its outer deadline; cleanup requires inspection') from exc
    try:
        result = json.loads(run.stdout.decode('utf-8'))
    except (UnicodeError, ValueError) as exc:
        raise ValueError('Craft native adapter returned no complete structured result') from exc
    if lease_path:
        event = {'operation': operation, 'started_at': started, 'returncode': run.returncode,
                 'native_binary_sha256': sha256(binary.read_bytes()).hexdigest(),
                 'result': result, 'parameter_sha256': sha256(json.dumps(request['params'], sort_keys=True).encode()).hexdigest()}
        with lease_path.with_suffix('.events.jsonl').open('a', encoding='utf-8') as stream:
            stream.write(json.dumps(event, ensure_ascii=True) + '\n')
    if run.returncode != 0 or result.get('ok') is not True:
        raise ValueError(f"Craft native operation blocked: {result.get('error', 'unsuccessful native call')}")
    return result


def prepare_native(project: Path, *, lease: str, workspace: str, receipt: str,
                   tasks: list[str], task_files: list[str], research_files: list[str],
                   allowed_outputs: list[str], check_commands: list[str],
                   command_timeout_seconds: int = 60, case_root: str | None = None,
                   handoff_manifest: str | None = None, review_file: str | None = None) -> dict:
    project = project.resolve()
    native_binary()  # Fail before creating task state when the component is absent.
    if not check_commands or not 1 <= command_timeout_seconds <= 600:
        raise ValueError('A frozen check-command list and a 1..600 second deadline are required')
    if any(not name.startswith('app/') for name in allowed_outputs):
        raise ValueError('Native candidate outputs must be under app/ in the Craft workspace')
    inferred_case = case_root
    if not inferred_case:
        for parent in _inside(project, receipt).parents:
            if parent == project:
                break
            if (parent / 'case.json').is_file():
                inferred_case = parent.relative_to(project).as_posix()
                break
    spec_refs = _spec_implementation_refs(project, task_files) if inferred_case else []
    lease_path = _inside(project, lease)
    if lease_path.is_relative_to(_inside(project, workspace)) or lease_path == _inside(project, receipt):
        raise ValueError('Native lease and observer receipt must stay outside the candidate workspace and differ')
    configuration = {'version': 1, 'project_root': str(project), 'receipt': receipt.replace('\\', '/'),
                     'workspace': workspace.replace('\\', '/'), 'check_commands': check_commands,
                     'command_timeout_seconds': command_timeout_seconds}
    lease_path.parent.mkdir(parents=True, exist_ok=True)
    with lease_path.open('x', encoding='utf-8') as stream:
        stream.write(json.dumps(configuration, ensure_ascii=True, indent=2) + '\n')
    try:
        observer = prepare_session(project, workspace=configuration['workspace'], receipt=configuration['receipt'],
                                   tasks=tasks, task_files=task_files, research_files=[*research_files, *spec_refs, lease],
                                   allowed_outputs=['craft.json', *allowed_outputs], case_root=case_root,
                                   handoff_manifest=handoff_manifest, review_file=review_file)
    except (ValueError, OSError):
        lease_path.unlink()  # Only the new file owned by this failed prepare.
        raise
    native = invoke_native(project, lease=lease, operation='prepare')
    return {'status': 'prepared', 'backend': 'craft-anything-native-engine', 'observer': observer,
            'native': native, 'lease': lease, 'business_acceptance': 'not-performed'}
