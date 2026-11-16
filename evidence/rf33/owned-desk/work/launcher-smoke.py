from pathlib import Path
import subprocess,sys,time,json,urllib.request,hashlib,socket,os
root=Path(__file__).resolve().parent.parent
app=Path(sys.argv[1]).resolve() if len(sys.argv)>1 else root/'outputs/标签收纳盒'
log=root/'work/current-case/evidence/launcher-output.txt'
result={'status':'fail'}
def port_open():
 with socket.socket() as s:
  s.settimeout(.3);return s.connect_ex(('127.0.0.1',8877))==0
assert not port_open(),'test port already occupied'
proc=None
try:
 with log.open('w',encoding='utf-8') as output:
  desk_env=dict(os.environ,PYTHONIOENCODING='utf-8')
  proc=subprocess.Popen([sys.executable,str(app/'launch.py'),'--no-browser'],cwd=app,stdout=output,stderr=subprocess.STDOUT,env=desk_env,creationflags=getattr(subprocess,'CREATE_NO_WINDOW',0))
  for _ in range(40):
   if port_open():break
   if proc.poll() is not None:raise RuntimeError('launcher exited early')
   time.sleep(.1)
  assert port_open(),'server did not become ready'
  body=urllib.request.urlopen('http://127.0.0.1:8877/',timeout=3).read()
  assert hashlib.sha256(body).digest()==hashlib.sha256((app/'index.html').read_bytes()).digest()
  for filename in ['core.mjs','page.mjs']:
   assert urllib.request.urlopen('http://127.0.0.1:8877/'+filename,timeout=3).read()==(app/filename).read_bytes()
  collision=subprocess.run([sys.executable,str(app/'launch.py'),'--no-browser'],capture_output=True,timeout=5,env=desk_env,creationflags=getattr(subprocess,'CREATE_NO_WINDOW',0))
  assert collision.returncode==1,'occupied port must fail explicitly'
  result.update(status='pass',server_ready=True,served_exact_delivered_files=True,port_conflict_rejected=True,launch_mode='delivered launch.py --no-browser; CMD wrapper separately inspected',python=sys.version.split()[0])
finally:
 if proc is not None and proc.poll() is None:
  proc.terminate();proc.wait(timeout=5)
 result['process_exited']=proc is None or proc.poll() is not None
 for _ in range(20):
  if not port_open():break
  time.sleep(.1)
 result['port_closed']=not port_open()
 (root/'work/current-case/evidence/launcher-smoke.json').write_text(json.dumps(result,ensure_ascii=False,indent=2),encoding='utf-8')
assert result['port_closed']
print(json.dumps(result,ensure_ascii=False))
