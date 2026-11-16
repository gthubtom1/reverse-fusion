"""Select existing tool paths once and restore them for both MCP and CLI.

Only tool paths are persisted. Credentials, arbitrary environment variables and
unrelated client registrations are never imported. Presence is not execution.
"""
from __future__ import annotations

from hashlib import sha256
import json
import os
from pathlib import Path
import shutil

from .file_updates import atomic_write


PATH_KEYS = {
    'GHIDRA_INSTALL_DIR': 'directory', 'JAVA_HOME': 'directory',
    'REA_WABT_BIN_DIRECTORY': 'directory', 'REA_JADX_MCP_JAR': 'file',
    'REA_BROWSER_EXECUTABLE': 'file', 'REA_ADB_PATH': 'file',
    'REA_APKTOOL_COMMAND': 'file', 'REA_ILSPY_CMD_PATH': 'file',
    'REA_KUNA_COMMAND': 'file', 'REA_GDB_COMMAND': 'file',
    'REA_OBJDUMP_COMMAND': 'file', 'REA_TSHARK_COMMAND': 'file',
    'REA_MITMDUMP_COMMAND': 'file', 'REA_BINWALK_COMMAND': 'file',
    'REA_UNBLOB_COMMAND': 'file', 'REA_WAKARU_COMMAND': 'file',
    'REA_IDA_MCP_CONFIG': 'file',
    'HOPPER_LAUNCHER_PATH':'file','REA_RIZIN_COMMAND':'file','REA_CAPINFOS_COMMAND':'file',
    'REA_CUTTER_BRIDGE_DIR':'directory','REA_TSHARK_PRLIMIT_COMMAND':'file',
    'REA_JAVASCRIPT_PRLIMIT_COMMAND':'file','REA_FIRMWARE_PRLIMIT_COMMAND':'file',
    'REA_EVM_PRLIMIT_COMMAND':'file','REA_SIGROK_COMMAND':'file','REA_SIGROK_PRLIMIT_COMMAND':'file',
    'REA_PWNTOOLS_PYTHON':'file','REA_PWNDBG_GDB':'file','REA_PWNDBG_GDBINIT':'file',
    'REA_PWNDBG_VENV_PATH':'directory','REA_DARWIN_SWIFTC_PATH':'file',
    'REA_GHIDRA_NATIVEAOT_JAR':'file','SDKROOT':'directory',
}
CRAFT_COMMANDS = ('adb', 'jadx', 'apktool', 'chromium', 'frida', 'gdb', 'lldb',
                  'mitmdump', 'binwalk', 'unblob', 'ilspy', 'java', 'tshark',
                  'objdump', 'rizin', 'rtl433', 'vineflower')
CRAFT_PREFIX = 'REVERSE_FUSION_CRAFT_TOOL_'
CRAFT_FROM_REA = {'adb': 'REA_ADB_PATH', 'apktool': 'REA_APKTOOL_COMMAND',
    'chromium': 'REA_BROWSER_EXECUTABLE', 'gdb': 'REA_GDB_COMMAND',
    'ilspy': 'REA_ILSPY_CMD_PATH', 'tshark': 'REA_TSHARK_COMMAND',
    'objdump': 'REA_OBJDUMP_COMMAND', 'mitmdump': 'REA_MITMDUMP_COMMAND',
    'binwalk': 'REA_BINWALK_COMMAND', 'unblob': 'REA_UNBLOB_COMMAND','rizin':'REA_RIZIN_COMMAND'}
ALL_KEYS = {*PATH_KEYS, *(CRAFT_PREFIX + name.upper() for name in CRAFT_COMMANDS)}


def _existing(key: str, value: str) -> Path:
    path = Path(value).expanduser()
    if not path.is_absolute(): raise ValueError(f'{key} must be an absolute tool path')
    path = path.resolve()
    kind = PATH_KEYS.get(key, 'file')
    if not (path.is_dir() if kind == 'directory' else path.is_file()):
        raise ValueError(f'{key} selected path is missing: {path}')
    if key == 'GHIDRA_INSTALL_DIR' and not (path/'Ghidra/application.properties').is_file():
        raise ValueError('Selected Ghidra has no application.properties')
    if key == 'JAVA_HOME' and not (path/'bin'/('java.exe' if os.name=='nt' else 'java')).is_file():
        raise ValueError('Selected Java home has no Java executable')
    return path


def _receipt(root: Path) -> dict:
    path = root/'state/provider-runtime.json'
    if not path.is_file(): return {}
    value = json.loads(path.read_text(encoding='utf-8-sig'))
    if (not isinstance(value,dict) or value.get('schema_version') != 1 or not isinstance(value.get('repository_root'),str)
            or not Path(value['repository_root']).is_absolute() or Path(value['repository_root']).resolve() != root.resolve()
            or not isinstance(value.get('paths'), dict) or set(value['paths'])-ALL_KEYS
            or any(not isinstance(item, str) for item in value['paths'].values())):
        raise ValueError('Provider runtime receipt is not bound to this checkout')
    sources=value.get('sources',{})
    if not isinstance(sources,dict) or any(key not in value['paths'] or not isinstance(source,str) for key,source in sources.items()):
        raise ValueError('Provider runtime receipt contains invalid path origins')
    return value


def _read(root: Path) -> dict:
    return _receipt(root).get('paths',{})


def _repository_tools(root: Path) -> dict:
    result = {}
    manifest = root/'vendor/wabt/1.0.42/manifest.json'
    if manifest.is_file():
        pin = json.loads(manifest.read_text(encoding='utf-8'))
        directory = root/'vendor/wabt/1.0.42/windows-x64/wabt-1.0.42/bin'
        if all((directory/name).is_file() and sha256((directory/name).read_bytes()).hexdigest()==pin['bin_sha256'][name]
               for name in pin['required_tools']):
            result['REA_WABT_BIN_DIRECTORY'] = str(directory.resolve())
    manifest = root/'vendor/jadx-headless-mcp/0.7.1/manifest.json'
    if manifest.is_file():
        pin = json.loads(manifest.read_text(encoding='utf-8'))
        jar = manifest.parent/pin['artifact']
        if jar.is_file() and sha256(jar.read_bytes()).hexdigest()==pin['sha256']:
            result['REA_JADX_MCP_JAR'] = str(jar.resolve())
    return result


def discover_providers(root: Path, *, persist=False, overrides: dict | None=None) -> dict:
    """Refresh discovery during deployment; explicit invalid selections fail closed."""
    root=root.resolve();receipt=_receipt(root);selected=dict(receipt.get('paths',{}))
    sources={key:receipt.get('sources',{}).get(key,'saved-tool-path') for key in selected};removed={}
    repository=_repository_tools(root)
    for key,value in list(selected.items()):
        try:
            path=_existing(key,value)
            if key in {'REA_WABT_BIN_DIRECTORY','REA_JADX_MCP_JAR'} and path.is_relative_to(root) and repository.get(key)!=str(path):
                raise ValueError('Managed provider integrity changed')
        except (OSError,ValueError) as error:
            removed[key]=str(error);selected.pop(key);sources.pop(key)
    for key,value in repository.items():
        if key not in selected: selected[key]=value;sources[key]='verified-repository-provider'
    for key in ALL_KEYS:
        if os.environ.get(key): selected[key]=os.environ[key];sources[key]='deployment-environment'
    for key,value in (overrides or {}).items():
        if key not in ALL_KEYS: raise ValueError(f'Unsupported provider path key: {key}')
        selected[key]=value;sources[key]='explicit-tool-path'
    which = {'REA_ADB_PATH':'adb','REA_APKTOOL_COMMAND':'apktool','REA_ILSPY_CMD_PATH':'ilspycmd',
             'REA_KUNA_COMMAND':'kuna','REA_GDB_COMMAND':'gdb','REA_OBJDUMP_COMMAND':'objdump',
             'REA_TSHARK_COMMAND':'tshark','REA_MITMDUMP_COMMAND':'mitmdump',
             'REA_RIZIN_COMMAND':'rizin','REA_CAPINFOS_COMMAND':'capinfos'}
    for key,command in which.items():
        found=shutil.which(command)
        if key not in selected and found: selected[key]=found;sources[key]='deployment-path'
    java=shutil.which('java')
    if 'JAVA_HOME' not in selected and java:
        selected['JAVA_HOME']=str(Path(java).resolve().parent.parent);sources['JAVA_HOME']='deployment-path'
    if 'REA_BROWSER_EXECUTABLE' not in selected:
        for base in ('PROGRAMFILES','PROGRAMFILES(X86)','LOCALAPPDATA'):
            for suffix in ('Google/Chrome/Application/chrome.exe','Microsoft/Edge/Application/msedge.exe'):
                if os.environ.get(base):
                    browser=Path(os.environ[base])/suffix
                    if browser.is_file(): selected['REA_BROWSER_EXECUTABLE']=str(browser);sources['REA_BROWSER_EXECUTABLE']='installed-browser';break
            if 'REA_BROWSER_EXECUTABLE' in selected: break
    for name in CRAFT_COMMANDS:
        key=CRAFT_PREFIX+name.upper()
        mapped=selected.get(CRAFT_FROM_REA.get(name,''))
        if name=='java' and 'JAVA_HOME' in selected:
            mapped=str(Path(selected['JAVA_HOME'])/'bin'/('java.exe' if os.name=='nt' else 'java'))
        found=mapped or shutil.which({'chromium':'chrome','ilspy':'ilspycmd'}.get(name,name))
        if (key not in selected or sources.get(key)=='shared-provider-path') and found:
            selected[key]=found;sources[key]='shared-provider-path' if mapped else 'deployment-path'
    paths={key:str(_existing(key,value)) for key,value in sorted(selected.items())}
    report={'schema_version':1,'repository_root':str(root),'paths':paths,'sources':sources,
            'removed_unavailable_paths':removed,
            'status':'configured' if paths else 'no-external-providers',
            'scope':'existing tool paths; actual provider compatibility and operations require native observations'}
    if persist: atomic_write(root/'state/provider-runtime.json',(json.dumps(report,ensure_ascii=True,indent=2)+'\n').encode('ascii'))
    return report


def provider_status(root: Path) -> dict:
    paths=_read(root)
    if not paths: paths=_repository_tools(root)
    available,unavailable={},{}
    repository=_repository_tools(root)
    for key,value in paths.items():
        try:
            path=_existing(key,value)
            if (key in {'REA_WABT_BIN_DIRECTORY','REA_JADX_MCP_JAR'} and path.is_relative_to(root.resolve())
                    and repository.get(key)!=str(path)):
                raise ValueError('Repository-managed provider integrity differs from its fixed manifest')
            available[key]=str(path)
        except (OSError,ValueError) as error: unavailable[key]=str(error)
    return {'status':'configured' if available else 'no-external-providers','paths':available,
            'unavailable':unavailable,'receipt_present':(root/'state/provider-runtime.json').is_file(),
            'scope':'configured existing paths; individual native operations establish provider readiness'}


def provider_environment(root: Path) -> dict[str,str]:
    """Restore saved deployment paths, independent of the app's old environment."""
    return provider_status(root)['paths']


def launch_environment(root: Path, base: dict | None=None) -> dict[str,str]:
    environment={key:value for key,value in (os.environ if base is None else base).items() if key not in ALL_KEYS}
    environment.update(provider_environment(root))
    return environment


def provider_identities(root: Path) -> dict:
    """Bind selected executable/JAR and directory entry identities, not whole SDKs."""
    report=provider_status(root);identities={}
    for key,value in report['paths'].items():
        path=Path(value)
        if path.is_file(): files=[path]
        elif key=='GHIDRA_INSTALL_DIR':
            files=[path/'Ghidra/application.properties',path/'support'/('analyzeHeadless.bat' if os.name=='nt' else 'analyzeHeadless')]
            files += [p for p in (path/'Ghidra/Features/Decompiler/os').glob('*/decompile*') if p.is_file()]
        elif key=='JAVA_HOME':files=[path/'release',path/'bin'/('java.exe' if os.name=='nt' else 'java')]
        elif key=='REA_WABT_BIN_DIRECTORY':
            pin=json.loads((root/'vendor/wabt/1.0.42/manifest.json').read_text(encoding='utf-8'))
            files=[path/name for name in pin['required_tools']]
        else: files=[p for p in (path/'VERSION',path/'version',path/'SDKSettings.plist') if p.is_file()]
        identities[key]={'path':value,'files':{str(p):sha256(p.read_bytes()).hexdigest() if p.is_file() else 'missing' for p in files}}
    return identities
