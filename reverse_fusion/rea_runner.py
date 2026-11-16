"""Run installed official REA with bounded ownership and unmodified output."""
from hashlib import sha256
import json
from pathlib import Path

from .file_updates import atomic_write
from .owned_process import run_owned
from .runtime import node_runtime
from .provider_runtime import launch_environment
from .session_builder import _inside


def run_rea(tool: Path, project: Path, *, operation: str, arguments: str,
            output: str, timeout: int = 180, memory_mb: int = 2048) -> dict:
    project = project.resolve()
    if not operation or not operation.replace('-', '').replace('_', '').isalnum():
        raise ValueError('Expected an actual installed REA operation name')
    if type(timeout) is not int or not 1 <= timeout <= 600 or type(memory_mb) is not int or not 128 <= memory_mb <= 8192:
        raise ValueError('REA execution requires1..600seconds and128..8192MiB budget')
    arg_path, dest = _inside(project, arguments), _inside(project, output)
    raw_args = arg_path.read_bytes()
    args = json.loads(raw_args.decode('utf-8-sig'))
    if not isinstance(args, list) or any(not isinstance(arg, str) or '\0' in arg for arg in args):
        raise ValueError('REA arguments file must contain an argv string array')
    if dest.exists():
        raise ValueError('Preserve existing REA output; choose a new run directory')
    node, source = node_runtime(tool)
    entry = tool / 'vendor/rea/package/scripts/rea.mjs'
    if not node or not entry.is_file():
        raise ValueError('Required official REA installation is missing')
    dest.mkdir(parents=True)
    run = run_owned([node, str(entry), operation, *args], cwd=project, stdin=b'', timeout=timeout, memory_mb=memory_mb,
                    env=launch_environment(tool))
    stdout, stderr = run.pop('stdout'), run.pop('stderr')
    atomic_write(dest/'stdout.json', stdout)
    atomic_write(dest/'stderr.txt', stderr)
    resource_messages = []
    structured = None
    if not run['output_truncated']:
        try:
            structured = json.loads(stdout.decode('utf-8-sig'))
        except (ValueError, UnicodeError):
            pass
    def visit(value):
        if isinstance(value, dict):
            for child in value.values(): visit(child)
        elif isinstance(value, list):
            for child in value: visit(child)
        elif isinstance(value, str) and any(token in value.lower() for token in
                ('resource constraint', 'exhausted', 'heap out of memory', 'timed out', 'provider deadline', 'budget exceeded')):
            resource_messages.append(value[:1200])
    visit(structured)
    status = ('unknown' if run['status'] != 'observed' or structured is None else
              'partial' if resource_messages else
              'failed' if run['exit_code'] != 0 or isinstance(structured,dict) and (
                  structured.get('ok') is False or structured.get('isError') is True
                  or structured.get('error') is not None) else
              'returned')
    report = {'operation': 'owned-official-rea-run', 'execution_status': status, 'requested_operation': operation,
              'runtime_source': source, 'argv': [node, str(entry), operation, *args], 'process': run,
              'argument_sha256': sha256(raw_args).hexdigest(), 'arguments_changed': arg_path.read_bytes() != raw_args,
              'stdout_sha256': sha256(stdout).hexdigest(), 'stderr_sha256': sha256(stderr).hexdigest(),
              'resource_messages': sorted(set(resource_messages)),
              'semantic_acceptance': 'not-assessed; inspect native coverage/limitations even when execution_status=returned',
              'next_action': ('Read retained partial result, identify the affected source/feature and choose a smaller provenance-backed observation or another available method; keep independent tasks moving.' if resource_messages else
                              'Inspect actual official result/coverage before promoting facts; raw output remains unmodified.')}
    if report['arguments_changed']:
        report['execution_status'] = 'unknown'
    atomic_write(dest/'execution.json',(json.dumps(report,indent=2)+'\n').encode('utf-8'))
    return report
