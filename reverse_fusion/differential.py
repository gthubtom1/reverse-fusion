"""Project-local finite process comparison with explicit source identity.

This adapter executes reviewed argv, keeps raw byte observations and never
promotes its result to native REA proof or whole-product equivalence.
"""
import base64
from hashlib import sha256
import json
from pathlib import Path

from .file_updates import atomic_write
from .session_builder import _inside
from .owned_process import run_owned


def compare_processes(project: Path, plan_name: str, output: str) -> dict:
    project = project.resolve()
    plan_path, destination = _inside(project, plan_name), _inside(project, output)
    plan_bytes = plan_path.read_bytes()
    plan = json.loads(plan_bytes.decode('utf-8-sig'))
    if set(plan) != {'version', 'scope', 'original', 'candidate', 'cases', 'timeout_seconds'} or plan['version'] != 1:
        raise ValueError('Comparison plan must declare version/scope/original/candidate/cases/timeout_seconds')
    if not isinstance(plan['scope'], str) or not plan['scope'].strip():
        raise ValueError('Finite behavior scope is required')
    if type(plan['timeout_seconds']) not in {int, float} or not 0 < plan['timeout_seconds'] <= 60:
        raise ValueError('Comparison deadline must be in (0,60] seconds')
    if not isinstance(plan['cases'], list) or not plan['cases']:
        raise ValueError('Explicit nonempty finite cases are required')
    cases = plan['cases']
    if (any(not isinstance(c, dict) or set(c) != {'id', 'stdin'} or not isinstance(c['id'], str)
            or not c['id'].strip() or not isinstance(c['stdin'], str) for c in cases)
            or len({c['id'] for c in cases}) != len(cases)):
        raise ValueError('Case IDs must be unique and stdin must be explicit text')
    sources, sides = {}, {}
    for side in ('original', 'candidate'):
        config = plan[side]
        if (not isinstance(config, dict) or set(config) != {'argv', 'cwd', 'sources'}
                or not isinstance(config['argv'], list) or not config['argv']
                or any(not isinstance(arg, str) or '\0' in arg for arg in config['argv'])
                or not isinstance(config['sources'], list) or not config['sources']):
            raise ValueError('Each side needs argv, project-relative cwd and explicit source files')
        cwd = _inside(project, config['cwd'])
        if not cwd.is_dir():
            raise ValueError('Comparison cwd is missing')
        refs = {_inside(project, name): sha256(_inside(project, name).read_bytes()).hexdigest()
                for name in config['sources']}
        sources.update(refs)
        sides[side] = (config, cwd, refs)
    if (set(sides['original'][2]) & set(sides['candidate'][2]) or
            set(sides['original'][2].values()) == set(sides['candidate'][2].values())):
        raise ValueError('Original and candidate must have distinct source paths and identities')
    if destination.exists():
        raise ValueError('Comparison output already exists; preserve it and use a new run path')
    # Keep this comparison independent of candidate implementation. The bounded
    # runner owns its child tree; argv are reviewed executable effects, not an OS sandbox.
    destination.mkdir(parents=True)
    observations = []
    for case in cases:
        pair = {'id': case['id']}
        for side, (config, cwd, _) in sides.items():
            try:
                run = run_owned(config['argv'], cwd=cwd, stdin=case['stdin'].encode('utf-8'), timeout=plan['timeout_seconds'])
                pair[side] = {key: value for key, value in run.items() if key not in {'stdout', 'stderr'}}
                pair[side].update(stdout_base64=base64.b64encode(run['stdout']).decode('ascii'),
                                  stderr_base64=base64.b64encode(run['stderr']).decode('ascii'))
            except OSError as exc:
                pair[side] = {'status': 'unknown', 'reason': str(exc), 'cleanup': 'no child invocation started'}
        left, right = pair['original'], pair['candidate']
        pair['status'] = ('unknown' if left['status'] != 'observed' or right['status'] != 'observed' else
                          'pass' if all(left[key] == right[key] for key in ('exit_code', 'stdout_base64', 'stderr_base64')) else 'fail')
        observations.append(pair)
        # Fail closed on timeout before another process is started.
        if any(v.get('cleanup', '').startswith('unknown') for v in (left, right)):
            break
    changed = [path.relative_to(project).as_posix() for path, digest in sources.items()
               if not path.is_file() or sha256(path.read_bytes()).hexdigest() != digest]
    if sha256(plan_path.read_bytes()).hexdigest() != sha256(plan_bytes).hexdigest():
        changed.append(plan_name)
    status = ('unknown' if changed or len(observations) != len(cases) or any(c['status'] == 'unknown' for c in observations)
              else 'fail' if any(c['status'] == 'fail' for c in observations) else 'pass')
    result = {'version': 1, 'operation': 'finite-process-comparison', 'status': status,
              'scope': plan['scope'], 'plan_sha256': sha256(plan_bytes).hexdigest(),
              'sources': {path.relative_to(project).as_posix(): digest for path, digest in sources.items()},
              'changed_inputs': changed, 'cases': observations,
              'rea_native_proof': 'not-performed', 'whole_product_acceptance': 'not-established',
              'limitations': ['Finite argv/stdin/exit/stdout/stderr comparison only.',
                              'Filesystem, UI, network and other effects need their own reviewed observations.',
                              'No shell expansion; executable arguments still have their actual effects.']}
    atomic_write(destination / 'comparison.json', (json.dumps(result, indent=2) + '\n').encode('utf-8'))
    return result
