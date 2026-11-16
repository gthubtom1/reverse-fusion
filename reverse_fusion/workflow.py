"""Read-only host handoff; existing cases and native records remain authoritative.

This module resolves entry points and recovery state. It does not select a
reverse method, execute target text, invent Evidence or certify semantic readiness.
"""
from __future__ import annotations

import json
import os
from hashlib import sha256
from pathlib import Path

from .case_bridge import discover_open_cases, load_case_record
from .runtime import node_runtime
from .session_builder import _inside
from .spec_support import generated_workflow


def component_entries(tool: Path, project: Path) -> dict:
    scripts = tool / '.venv' / ('Scripts' if os.name == 'nt' else 'bin')
    python = str(scripts / ('python.exe' if os.name == 'nt' else 'python'))
    node, source = node_runtime(tool)
    prefix = [python, '-m', 'reverse_fusion']
    return {
        'cwd': str(project.resolve()),
        'argument_policy': 'argv arrays; append reviewed arguments without shell interpolation; preserve original UTF-8 provider output',
        'rea': {'argv': [node, str(tool / 'vendor/rea/package/scripts/rea.mjs')] if node else None,
                'bounded_argv': [*prefix, 'rea-run', '--project-root', str(project.resolve())],
                'runtime_source': source, 'usage': 'append the installed official command and its arguments; inspect its help/schema before using a new operation'},
        'spec': {'argv': [str(scripts / ('specify.exe' if os.name == 'nt' else 'specify'))],
                 'generated_workflow': generated_workflow(project),
                 'usage': 'initialize in the outcome project, then read and execute its generated speckit skills; init alone is not the workflow'},
        'native_craft': {'argv': [*prefix, 'native-craft', '<phase>', '--project-root', str(project.resolve())],
                         'usage': 'prepare/build/check/refine/return_summary/cleanup with the same frozen lease; abort retains failed/interrupted work without acceptance'},
        'observer': {'argv': [*prefix, 'session', '<phase>', '--project-root', str(project.resolve())],
                     'usage': 'additional check/refine/finish on the native prepare receipt, after native checks and cleanup'},
        'comparison': {'argv': [*prefix, 'compare', '--project-root', str(project.resolve())],
                       'usage': 'reviewed --plan and new --output; independent finite argv/stdin observations with owned process cleanup; not native REA proof'},
        'guides': [str(tool / 'docs' / name) for name in
                   ('AGENT-WORKFLOW.md', 'NATIVE-COMPONENTS.md', 'CROSS-PROJECT-WORKFLOW.md', 'RECOVERY.md', 'PROCESS-COMPARISON.md')],
    }


def inspect_workflow(tool: Path, project: Path, *, case_root: str | None = None,
                     receipt: str | None = None) -> dict:
    project = project.resolve()
    entries = component_entries(tool, project)
    if not case_root:
        cases = discover_open_cases(project)
        if len(cases) != 1:
            return {'operation': 'workflow', 'status': 'needs-case-selection' if cases else 'no-open-case',
                    'cases': cases, 'entries': entries, 'writes': False,
                    'next_action': 'Identify the intended existing case; do not silently replace it. For a new task, record the original request through bridge.'}
        case_root = cases[0]
    record = load_case_record(project, case_root)
    if not record:
        raise ValueError('Workflow recovery requires an existing open case')
    pointer = record['pointer']
    workflow = pointer.get('workflow', {})
    refs = []
    for ref in pointer['carry_forward_refs']:
        if ref.startswith('project:'):
            path = _inside(project, ref[len('project:'):])
            refs.append({'path': str(path), 'present': path.is_file()})
    result = {'operation': 'workflow', 'status': 'context-resolved', 'writes': False,
              'project_root': str(project), 'case_root': pointer['case_root'],
              'revision': record['revision'], 'workflow': workflow,
              'carry_forward_refs': pointer['carry_forward_refs'], 'project_refs': refs,
              'entries': entries, 'business_acceptance': 'not-performed',
              'next_action': 'Read the original objective and case workitems; choose the next evidence-supported action. A missing dependency blocks only dependent tasks; continue independent work before asking for help.',
              'readiness': 'not-assessed; current stage and presence of documents do not establish semantic readiness'}
    if any(not ref['present'] for ref in refs):
        result.update(status='missing-context', next_action='Restore or locate the missing referenced material before work that depends on it; retain the original goal and continue independent tasks.')
    if receipt:
        path = _inside(project, receipt)
        session = json.loads(path.read_text(encoding='utf-8-sig'))
        if (not isinstance(session, dict) or session.get('version') != 1
                or session.get('backend') != 'current-session'
                or not isinstance(session.get('project_root'), str)
                or not Path(session['project_root']).is_absolute()
                or Path(session['project_root']).resolve() != project):
            raise ValueError('Session is not a supported record bound to this project')
        refs_map = session.get('frozen_refs')
        if (not isinstance(refs_map, dict)
                or any(not isinstance(name, str) or not isinstance(digest, str) or len(digest) != 64
                       for name, digest in refs_map.items())):
            raise ValueError('Session frozen references are malformed')
        case_path = _inside(project, f'{case_root}/case.json')
        if case_path not in {_inside(project, name) for name in refs_map}:
            raise ValueError('Session is not bound to the selected case')
        changed = []
        for name, expected in refs_map.items():
            target = _inside(project, name)
            if not target.is_file() or sha256(target.read_bytes()).hexdigest() != expected:
                changed.append(name)
        result['session'] = {'receipt': receipt, 'phase': session.get('phase'),
                             'changed_frozen_refs': changed,
                             'workspace': session.get('workspace'),
                             'cleanup': 'not-inferred; inspect actual native events and owned processes',
                             'next_action': ('Keep old records; inspect/clean the old writer and prepare a new reviewed batch. Do not refresh hashes to hide changes.' if changed else
                                             'Aborted batch: retain outputs and failure records; revise analysis/spec as needed and prepare a new reviewed workspace.' if session.get('phase') == 'aborted' else
                                             'Finished batch: compare independently and update Spec tasks/converge; new edits need a new batch.' if session.get('phase') == 'finished' else
                                             'Inspect native events and last check; continue the same valid lease only when cleanup and ownership are known. Failed checks return to correction; missing facts return to analysis.')}
        if changed:
            result['status'] = 'frozen-input-changed'
    return result
