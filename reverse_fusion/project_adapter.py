"""Selected-host project pointers; no credentials, model settings or global writes."""
import json
from pathlib import Path

from .file_updates import atomic_write, file_transaction
from .global_adapter import MARKER_START, MARKER_END, SKILL_MARKER, _replace_agents_block, skill_text
from .session_builder import _inside


def connect_project(tool: Path, project: Path, *, client: str, apply: bool = False, remove: bool = False) -> dict:
    if client not in {'codex', 'pi', 'claude'}:
        raise ValueError('Select codex, pi or claude')
    project, tool = project.resolve(), tool.resolve()
    folder = {'codex': '.agents', 'pi': '.pi', 'claude': '.claude'}[client]
    skill = _inside(project, f'{folder}/skills/reverse-fusion/SKILL.md')
    instruction = _inside(project, 'CLAUDE.md' if client == 'claude' else 'AGENTS.md')
    receipt = _inside(project, f'.reverse-fusion/{client}.json')
    block = (f'{MARKER_START}\n'
             f'For plain analysis/recreation requests or specialist Reverse Fusion work, read '
             f'`{skill.relative_to(project).as_posix()}` and use its shared router before acting. '
             'Keep this project as the output root, preserve the original objective and use '
             'the current host for reasoning. Ordinary development stays host-native.\n'
             f'Shared checkout: `{tool.as_posix()}`.\n{MARKER_END}')
    existing = instruction.read_text(encoding='utf-8') if instruction.is_file() else ''
    updated = _replace_agents_block(existing, block)  # Validate markers before writes/removal.
    if skill.exists() and SKILL_MARKER not in skill.read_text(encoding='utf-8'):
        raise ValueError('Existing project skill is not owned by Reverse Fusion')
    if remove:
        if not receipt.is_file():
            return {'status': 'not-connected', 'writes': False, 'client': client}
        record = json.loads(receipt.read_text(encoding='utf-8'))
        if record.get('repository') != str(tool):
            raise ValueError('Another checkout owns this project pointer')
        start, end = existing.find(MARKER_START), existing.find(MARKER_END)
        if start >= 0 and existing[start:end + len(MARKER_END)] != block:
            raise ValueError('Project pointer was modified; preserve it for review')
        new_instruction = existing[:start] + existing[end + len(MARKER_END):] if start >= 0 else existing
        if apply:
            with file_transaction([skill, instruction, receipt]):
                if skill.is_file():
                    if skill.read_text(encoding='utf-8') != skill_text(tool):
                        raise ValueError('Project skill was modified; preserve it for review')
                    skill.unlink()
                if new_instruction.strip():
                    atomic_write(instruction, new_instruction.encode('utf-8'))
                elif instruction.exists():
                    instruction.unlink()
                receipt.unlink()
        return {'status': 'disconnected' if apply else 'ready-to-disconnect', 'client': client, 'writes': apply}
    result = {'status': 'connected' if apply else 'ready', 'client': client, 'project_root': str(project),
              'repository': str(tool), 'skill': str(skill), 'instructions': str(instruction),
              'writes': apply, 'global_writes': False, 'runtime_acceptance': 'not-performed'}
    if apply:
        with file_transaction([skill, instruction, receipt]):
            atomic_write(skill, skill_text(tool).encode('utf-8'))
            atomic_write(instruction, updated.encode('utf-8'))
            atomic_write(receipt, (json.dumps(result, indent=2) + '\n').encode('utf-8'))
    return result
