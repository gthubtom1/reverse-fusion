"""Compile owned PE variants and observe a real OS debugger on the owned process.

No third-party sample, service, credential or licensing bypass. This is finite
Windows PE/anti-analysis method qualification, not all-protector support.
"""
import ctypes
from ctypes import wintypes as w
from hashlib import sha256
import json
from pathlib import Path
import shutil
import subprocess
import sys
import time

root = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(root))
from reverse_fusion.differential import compare_processes
from reverse_fusion.rea_runner import run_rea

project = root / 'state/rf33-owned-native'
if project.exists():
    raise SystemExit('Preserve existing native qualification; select a new named run before retry')
project.mkdir(parents=True)
gcc = shutil.which('gcc')
if not gcc:
    raise SystemExit('A local GCC Windows compiler is required for this owned fixture')
for name in ('guarded', 'candidate'):
    side = project / name
    side.mkdir()
    source = root / f'fixtures/owned-native/{name}.c'
    shutil.copyfile(source, side / 'main.c')
    built = subprocess.run([gcc, '-O1', str(side/'main.c'), '-o', str(side/'main.exe')],capture_output=True,timeout=30)
    (side/'build.stdout').write_bytes(built.stdout)
    (side/'build.stderr').write_bytes(built.stderr)
    if built.returncode:
        raise SystemExit('Owned fixture compilation failed; retained build output')
plan = {'version':1,'scope':'owned native integer operation, input validation and exit behavior',
    'original':{'argv':[str(project/'guarded/main.exe')],'cwd':'guarded','sources':['guarded/main.c','guarded/main.exe']},
    'candidate':{'argv':[str(project/'candidate/main.exe')],'cwd':'candidate','sources':['candidate/main.c','candidate/main.exe']},
    'cases':[{'id':f'case-{index}','stdin':text} for index,text in enumerate(['0\n','2\n','-1000\n','1000\n','1001\n','abc\n','+19\n','  33 \n','3x\n',''])],
    'timeout_seconds':3}
(project/'plan.json').write_text(json.dumps(plan),encoding='utf-8')
compared = compare_processes(project,'plan.json','comparison')
kernel=ctypes.WinDLL('kernel32',use_last_error=True)
kernel.DebugActiveProcess.argtypes=[w.DWORD];kernel.DebugActiveProcess.restype=w.BOOL
kernel.DebugActiveProcessStop.argtypes=[w.DWORD];kernel.DebugActiveProcessStop.restype=w.BOOL
kernel.ContinueDebugEvent.argtypes=[w.DWORD,w.DWORD,w.DWORD];kernel.ContinueDebugEvent.restype=w.BOOL
kernel.DebugSetProcessKillOnExit.argtypes=[w.BOOL]
kernel.CloseHandle.argtypes=[w.HANDLE]
# DEBUG_EVENT union maximum is176bytes on Win64 (EXCEPTION_DEBUG_INFO).
class Event(ctypes.Structure):
    _fields_=[('code',w.DWORD),('pid',w.DWORD),('tid',w.DWORD),('payload',ctypes.c_ulonglong * 20)]
kernel.WaitForDebugEvent.argtypes=[ctypes.POINTER(Event),w.DWORD];kernel.WaitForDebugEvent.restype=w.BOOL
debugger=[]
for name in ('guarded','candidate'):
    process=subprocess.Popen([str(project/name/'main.exe')],stdin=subprocess.PIPE,stdout=subprocess.PIPE,stderr=subprocess.PIPE,
                             creationflags=subprocess.CREATE_NO_WINDOW,cwd=project/name)
    attached=False
    try:
        if not kernel.DebugActiveProcess(process.pid):
            raise ctypes.WinError(ctypes.get_last_error())
        attached=True; kernel.DebugSetProcessKillOnExit(False)
        process.stdin.write(b'2\n');process.stdin.flush();process.stdin.close();process.stdin=None
        deadline=time.monotonic()+8; events=[]
        while time.monotonic()<deadline:
            event=Event()
            if not kernel.WaitForDebugEvent(ctypes.byref(event),100):
                continue
            events.append(event.code)
            for index in ([0,1,2] if event.code==3 else [0] if event.code in (2,6) else []):
                if event.payload[index]:kernel.CloseHandle(event.payload[index])
            kernel.ContinueDebugEvent(event.pid,event.tid,0x00010002)
            if event.code==5:
                attached=False;break
        else:
            raise TimeoutError('Owned debugger observation did not exit within its budget')
        stdout,stderr=process.communicate(timeout=3)
        debugger.append({'side':name,'actual_os_debugger_attached':True,'events':events,'exit_code':process.returncode,
                         'stdout':stdout.decode('utf-8',errors='replace'),'stderr':stderr.decode('utf-8',errors='replace')})
    finally:
        if attached:kernel.DebugActiveProcessStop(process.pid)
        if process.poll() is None:process.kill();process.communicate(timeout=3)
(project/'rea-args.json').write_text(json.dumps(['guarded/main.exe','--format','json','--full-output']),encoding='utf-8')
rea=run_rea(root,project,operation='inspect-artifact',arguments='rea-args.json',output='rea-pe',timeout=30,memory_mb=768)
report={'scope':'owned Windows PE/debugger-effect finite qualification only','normal_comparison':compared['status'],
        'actual_debugger_observations':debugger,'rea_execution':rea['execution_status'],
        'status':'pass' if compared['status']=='pass' and all(r['exit_code']==9 and r['stdout'].strip()=='observer-blocked' for r in debugger) and rea['execution_status']=='returned' else 'fail',
        'next_method':'Record observer influence and use static/unobserved facts; do not mistake debug-triggered early exit for absent behavior.',
        'not_claimed':['unpacking arbitrary protectors','all anti-debug bypass','full arbitrary native source recovery']}
(project/'qualification.json').write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8')
print(json.dumps(report));raise SystemExit(0 if report['status']=='pass' else 1)
