"""Resolve the actual official Spec project integration without assuming Codex."""
import json
from pathlib import Path

from .session_builder import _inside


PHASES = ('constitution', 'specify', 'clarify', 'plan', 'tasks', 'analyze', 'implement', 'converge')


def generated_workflow(project: Path) -> dict:
    record_path = _inside(project, '.specify/integration.json')
    if not record_path.is_file():
        return {'status': 'not-initialized', 'client': None, 'refs': [], 'missing_phases': list(PHASES)}
    record = json.loads(record_path.read_text(encoding='utf-8-sig'))
    client = record.get('default_integration') or record.get('integration')
    if client not in {'codex', 'pi', 'claude'} or client not in record.get('installed_integrations', [client]):
        raise ValueError('Unsupported or inconsistent official Spec project integration')
    if client == 'pi':
        refs = {phase: f'.pi/prompts/speckit.{phase}.md' for phase in PHASES}
    else:
        base = '.agents' if client == 'codex' else '.claude'
        refs = {phase: f'{base}/skills/speckit-{phase}/SKILL.md' for phase in PHASES}
    missing = [phase for phase, name in refs.items() if not _inside(project, name).is_file()
               or not _inside(project, name).read_bytes().strip()]
    return {'status': 'available' if not missing else 'incomplete', 'client': client,
            'version': record.get('version'), 'refs': list(refs.values()),
            'phases': refs, 'missing_phases': missing,
            'scope': 'official generated workflow discovery, not semantic phase completion'}
