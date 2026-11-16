"""Manage only Reverse Fusion's two Codex stdio MCP registrations.

Unrelated TOML bytes remain unchanged. Registration is distinct from a live
client connection or target acceptance; the Codex client may need reloading.
"""
from __future__ import annotations

from dataclasses import dataclass
import json
from pathlib import Path
import re
import shutil
import tomllib

from .file_updates import atomic_write, file_transaction
from .global_adapter import adapter_paths
from .runtime import node_runtime


BEGIN = b'# reverse-fusion:mcp:begin'
END = b'# reverse-fusion:mcp:end'
SERVERS = ('reverse-fusion-rea', 'reverse-fusion-craft')
REA_ENV = {
    'REA_MCP_INPUT_SCHEMA_PROFILE': 'compact',
    'REA_MCP_OUTPUT_SCHEMA_PROFILE': 'compact',
}


def mcp_paths(home: Path | None = None) -> dict[str, Path]:
    return {'config': adapter_paths(home)['agents'].parent / 'config.toml'}


def _toml(payload: bytes) -> dict:
    try:
        return tomllib.loads(payload.decode('utf-8-sig'))
    except (UnicodeError, tomllib.TOMLDecodeError) as exc:
        raise ValueError('Codex config.toml is not valid UTF-8 TOML; nothing changed') from exc


def _registrations(root: Path, *, require_files: bool = False) -> dict:
    root = root.resolve()
    selected, _ = node_runtime(root)
    if not selected:
        raise ValueError('Required verified REA Node runtime is unavailable')
    executable = selected if Path(selected).is_absolute() else shutil.which(selected)
    if not executable:
        raise ValueError('Required selected REA Node executable is unavailable')
    node = Path(executable).resolve()
    rea = (root / 'vendor/rea/package/scripts/rea.mjs').resolve()
    craft = (root / 'vendor/craft/mcp/windows-x64/reverse-fusion-craft-mcp.exe').resolve()
    state = (root / 'state/craft-mcp').resolve()
    if any(not path.is_relative_to(root) for path in (rea, craft, state)):
        raise ValueError('MCP launch or state path leaves the shared checkout')
    if require_files and any(not path.is_file() for path in (node, rea, craft)):
        raise ValueError('Required selected Node, official REA or Craft MCP launcher is missing')
    return {
        SERVERS[0]: {'command': str(node), 'args': [str(rea), 'mcp'], 'cwd': str(root),
                     'startup_timeout_sec': 60, 'tool_timeout_sec': 600, 'env': dict(REA_ENV)},
        SERVERS[1]: {'command': str(craft), 'args': ['--all-tools', '--deep-mode', '--allow-run', '--state-dir', str(state)],
                     'cwd': str(root), 'startup_timeout_sec': 60, 'tool_timeout_sec': 600},
    }


@dataclass(frozen=True)
class Managed:
    start: int
    end: int
    repository: Path
    separator: int
    original_existed: bool
    registrations: dict


def _metadata(block: bytes, name: str):
    prefix = ('# reverse-fusion:mcp:' + name + ' = ').encode('ascii')
    lines = [line[len(prefix):] for line in block.splitlines() if line.startswith(prefix)]
    if len(lines) != 1:
        raise ValueError('Malformed Reverse Fusion MCP ownership metadata')
    try:
        return json.loads(lines[0].decode('utf-8'))
    except (UnicodeError, ValueError) as exc:
        raise ValueError('Malformed Reverse Fusion MCP ownership metadata') from exc


def _managed(payload: bytes, parsed: dict) -> Managed | None:
    counts = payload.count(BEGIN), payload.count(END)
    if counts == (0, 0):
        return None
    if counts != (1, 1):
        raise ValueError('Malformed or duplicate Reverse Fusion MCP markers')
    first = re.search(rb'^' + re.escape(BEGIN) + rb'\r?\n', payload, re.M)
    last = re.search(rb'^' + re.escape(END) + rb'(?:\r?\n|$)', payload, re.M)
    if not first or not last or first.end() >= last.start():
        raise ValueError('Malformed or reversed Reverse Fusion MCP markers')
    block = payload[first.start():last.end()]
    owner = _metadata(block, 'repository')
    separator = _metadata(block, 'added-separator')
    original_existed = _metadata(block, 'original-config-existed')
    if (not isinstance(owner, str) or not Path(owner).is_absolute()
            or type(separator) is not int or separator not in (0, 1)
            or type(original_existed) is not bool):
        raise ValueError('Invalid Reverse Fusion MCP ownership metadata')
    start = first.start() - separator
    if start < 0 or separator and payload[start:first.start()] != b'\n':
        raise ValueError('Reverse Fusion MCP separator changed; preserve configuration for review')
    owned = _toml(block)
    if set(owned) != {'mcp_servers'} or set(owned['mcp_servers']) != set(SERVERS):
        raise ValueError('Managed MCP block contains unrelated configuration; preserve it for review')
    full_servers = parsed.get('mcp_servers', {})
    if not isinstance(full_servers, dict) or any(full_servers.get(name) != owned['mcp_servers'][name] for name in SERVERS):
        raise ValueError('Managed MCP entries were extended outside their block; preserve them for review')
    # Refuse hidden unrelated fields on removal; installation owns these exact
    # server entries, never adjacent provider tables or credentials.
    for name, value in owned['mcp_servers'].items():
        expected = {'command', 'args', 'cwd', 'startup_timeout_sec', 'tool_timeout_sec'}
        if name == SERVERS[0]:
            expected.add('env')
        if not isinstance(value, dict) or set(value) != expected:
            raise ValueError('Managed MCP entry fields changed; preserve them for review')
        if (not isinstance(value['command'], str) or not isinstance(value['args'], list)
                or any(not isinstance(arg, str) for arg in value['args'])
                or value['cwd'] != owner):
            raise ValueError('Managed MCP entry identity is malformed')
        if name == SERVERS[0] and value['env'] != REA_ENV:
            raise ValueError('Managed REA environment changed; preserve it for review')
    return Managed(start, last.end(), Path(owner).resolve(), separator, original_existed, owned['mcp_servers'])


def _read(path: Path) -> tuple[bytes, dict, Managed | None]:
    if path.exists() and not path.is_file():
        raise ValueError('Expected a Codex config.toml file')
    payload = path.read_bytes() if path.is_file() else b''
    parsed = _toml(payload)
    return payload, parsed, _managed(payload, parsed)


def _render(root: Path, registrations: dict, *, separator: int, original_existed: bool) -> bytes:
    quote = lambda value: json.dumps(value, ensure_ascii=False)
    lines = [BEGIN.decode(), '# reverse-fusion:mcp:repository = ' + quote(str(root.resolve())),
             '# reverse-fusion:mcp:added-separator = ' + str(separator),
             '# reverse-fusion:mcp:original-config-existed = ' + str(original_existed).lower()]
    for name, entry in registrations.items():
        lines += ['', f'[mcp_servers.{name}]', 'command = ' + quote(entry['command']),
                  'args = ' + quote(entry['args']), 'cwd = ' + quote(entry['cwd']),
                  'startup_timeout_sec = 60', 'tool_timeout_sec = 600']
        if 'env' in entry:
            lines += [f'[mcp_servers.{name}.env]']
            lines += [key + ' = ' + quote(value) for key, value in entry['env'].items()]
    lines += [END.decode(), '']
    return b'\n' * separator + '\n'.join(lines).encode('utf-8')


def install_mcp(root: Path, home: Path | None = None) -> dict:
    root = root.resolve()
    path = mcp_paths(home)['config']
    payload, parsed, managed = _read(path)
    servers = parsed.get('mcp_servers', {})
    if not isinstance(servers, dict):
        raise ValueError('Codex mcp_servers must be a TOML table')
    if managed is None and any(name in servers for name in SERVERS):
        raise ValueError('Existing same-name MCP server is not owned by Reverse Fusion')
    registrations = _registrations(root, require_files=True)
    separator = managed.separator if managed else int(bool(payload) and not payload.endswith(b'\n'))
    original_existed = managed.original_existed if managed else path.is_file()
    block = _render(root, registrations, separator=separator, original_existed=original_existed)
    updated = payload[:managed.start] + block + payload[managed.end:] if managed else payload + block
    _toml(updated)
    with file_transaction([path]):
        if updated != payload or not path.is_file():
            atomic_write(path, updated)
    return {'enabled': True, 'status': 'registered', 'config': str(path), 'repository': str(root),
            'servers': list(SERVERS), 'changed': updated != payload,
            'reload_required': True, 'runtime_acceptance': 'not-performed'}


def remove_mcp(root: Path, home: Path | None = None) -> dict:
    root = root.resolve()
    path = mcp_paths(home)['config']
    payload, _, managed = _read(path)
    result = {'enabled': False, 'config': str(path), 'removed': [], 'changed': False}
    if managed is None:
        return {**result, 'status': 'not-registered'}
    if managed.repository != root:
        return {**result, 'status': 'retained', 'retained': 'another checkout owns the MCP pointer'}
    updated = payload[:managed.start] + payload[managed.end:]
    _toml(updated)
    with file_transaction([path]):
        if not updated and not managed.original_existed:
            path.unlink()
        else:
            atomic_write(path, updated)
    return {**result, 'status': 'removed', 'removed': list(SERVERS), 'changed': True,
            'reload_required': True}


def inspect_mcp(root: Path, home: Path | None = None) -> dict:
    root = root.resolve()
    path = mcp_paths(home)['config']
    try:
        _, parsed, managed = _read(path)
        if managed is None:
            servers = parsed.get('mcp_servers', {})
            collision = isinstance(servers, dict) and any(name in servers for name in SERVERS)
            return {'status': 'unmanaged-conflict' if collision else 'not-registered',
                    'enabled': False, 'config': str(path), 'servers': []}
        same_owner = managed.repository == root
        exact = same_owner and managed.registrations == _registrations(root)
        return {'status': 'registered' if exact else 'stale' if same_owner else 'other-checkout',
                'enabled': exact, 'config': str(path), 'repository': str(managed.repository),
                'servers': list(SERVERS), 'reload_required': True,
                'runtime_acceptance': 'not-performed'}
    except (OSError, ValueError, KeyError, TypeError) as exc:
        return {'status': 'invalid', 'enabled': False, 'config': str(path), 'reason': str(exc)}
