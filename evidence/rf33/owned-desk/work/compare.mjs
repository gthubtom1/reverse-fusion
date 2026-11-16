import fs from 'node:fs';
import path from 'node:path';
import http from 'node:http';
import {pathToFileURL,fileURLToPath} from 'node:url';
import assert from 'node:assert/strict';
import {createHash} from 'node:crypto';
import {createRequire} from 'node:module';
const require=createRequire(import.meta.url),{observe}=require('./observe.cjs');
const root=path.resolve(path.dirname(fileURLToPath(import.meta.url)),'..');
const candidateDir=path.resolve(process.argv[2]||'.');
const output=path.resolve(process.argv[3]||path.join(root,'work/current-case/evidence/differential'));
const originalDir=path.join(root,'desk-original');
fs.mkdirSync(output,{recursive:true});
const digest=p=>createHash('sha256').update(fs.readFileSync(p)).digest('hex');
const original=await import(pathToFileURL(path.join(originalDir,'core.mjs')));
const candidate=await import(pathToFileURL(path.join(candidateDir,'core.mjs')));
let checks=0;const details=[];
const call=(m,fn,args)=>{try{return {returned:m[fn](...structuredClone(args))};}catch(e){return {error:e.message}}};
function equal(fn,args,label){const a=call(original,fn,args),b=call(candidate,fn,args);assert.deepEqual(b,a,label);checks++;return a.returned;}
function core(m,seed,count){
 let s=m.initial();const results=[];
 const rnd=()=>{seed=(Math.imul(seed,1664525)+1013904223)>>>0;return seed/4294967296;};
 for(let i=0;i<count;i++){
  const before=JSON.stringify(s);let action;
  if(rnd()<.7)action={type:'add',name:[' 笔 ','cable','CABLE','', 'a'.repeat(32),'😀'.repeat(17),'纸巾','<b>文本</b>'][Math.floor(rnd()*8)],tag:['','A','a','电子'][Math.floor(rnd()*4)],quantity:[1,99,0,100,'2','1.5','',null][Math.floor(rnd()*8)]};
  else if(rnd()<.8)action={type:'remove',id:Math.floor(rnd()*(s.next+1))};
  else action={type:'clear'};
  let result;try{result={returned:m.change(s,action)}}catch(e){result={error:e.message}}
  assert.equal(JSON.stringify(s),before,'transition mutated input');
  if('returned'in result)s=result.returned;
  results.push({action,result,view:m.view(s,['','A',' 电 ','<b>'][i%4],i%2?'name':'newest')});
 }
 return results;
}
const serve=async(dir)=>{
 const server=http.createServer((req,res)=>{
  let pathname=decodeURIComponent(new URL(req.url,'http://localhost').pathname);if(pathname==='/')pathname='/index.html';
  const target=path.resolve(dir,'.'+pathname);if(!target.startsWith(dir+path.sep)){res.writeHead(403);return res.end();}
  try{res.setHeader('Content-Type',target.endsWith('.html')?'text/html; charset=utf-8':target.endsWith('.mjs')?'text/javascript; charset=utf-8':'text/plain; charset=utf-8');res.end(fs.readFileSync(target));}catch{res.writeHead(404);res.end();}
 });
 await new Promise((ok,no)=>{server.once('error',no);server.listen(0,'127.0.0.1',ok)});
 return {server,url:`http://127.0.0.1:${server.address().port}`};
};
const servers=[];
try{
 equal('initial',[],'initial');
 const base=original.initial();
 for(const name of ['', '  ', 'a'.repeat(32),'a'.repeat(33),'😀'.repeat(16),'😀'.repeat(17),null,42,'<script>text</script>'])
 for(const quantity of [1,99,0,100,-1,1.5,'2','1e1',null,undefined,'',true])equal('change',[base,{type:'add',name,tag:' ',quantity}],'add bounds');
 const a=equal('change',[base,{type:'add',name:' Cable ',tag:'电子',quantity:'2'}],'first add');
 for(const tag of ['电子','电子 ','电子x','电子'.toUpperCase(),''])equal('change',[a,{type:'add',name:'cAbLe',tag,quantity:1}],'duplicate normalization');
 for(const id of [1,2,'1',null])equal('change',[a,{type:'remove',id}],'remove');
 equal('change',[a,{type:'clear'}],'clear');equal('change',[a,{type:'other'}],'unknown');
 const states=[null,'','{','null','1','[]',JSON.stringify(a),JSON.stringify({...a,version:2}),JSON.stringify({...a,next:1}),JSON.stringify({...a,next:1.5}),JSON.stringify({...a,next:Number.MAX_SAFE_INTEGER+1}),JSON.stringify({...a,entries:[a.entries[0],a.entries[0]]}),JSON.stringify({...a,extra:'retained',entries:[{...a.entries[0],extra:4}]}),JSON.stringify({...a,entries:[{...a.entries[0],name:'a'.repeat(50),tag:''}]})];
 for(const field of ['id','name','tag','quantity'])for(const value of [null,-1,0,1.5,100,'bad',{},[]])states.push(JSON.stringify({...a,entries:[{...a.entries[0],[field]:value}]}));
 for(const text of states)equal('restore',[text],'restore schema');
 let many=original.initial();for(const [name,tag,quantity] of [['中文','电子',4],['a','',1],['A','其它',99],['abc','A',2],['é','B',1]])many=original.change(many,{type:'add',name,tag,quantity});
 for(const query of ['',' A ','电','文\n电',null,42,'xyz','é'])for(const order of ['newest','name','other'])equal('view',[many,query,order],'view collation/filter');
 for(const seed of [20261116,4138721]){const left=core(original,seed,600),right=core(candidate,seed,600);assert.deepEqual(right,left,'seeded operation traces');checks+=left.length;details.push({seed,operations:left.length,traceSha256:createHash('sha256').update(JSON.stringify(left)).digest('hex')});}
 const mutant={...candidate,view:(...args)=>({...candidate.view(...args),quantity:0})};
 let rejected=false;try{assert.deepEqual(core(mutant,20261116,600),core(original,20261116,600))}catch{rejected=true;}
 assert.ok(rejected,'wrong candidate must fail');checks++;
 const leftServer=await serve(originalDir);servers.push(leftServer.server);
 const rightServer=await serve(candidateDir);servers.push(rightServer.server);
 const left=await observe(leftServer.url,path.join(output,'original'));
 const right=await observe(rightServer.url,path.join(output,'candidate'));
 assert.deepEqual(right,left,'all browser state, focus, failure and layout checkpoints');checks+=left.trace.length;
 const screenshots=[];
 for(const name of ['empty','populated','mobile']){
  const l=digest(path.join(output,'original',name+'.png')),r=digest(path.join(output,'candidate',name+'.png'));
  assert.equal(r,l,`${name} exact PNG equality`);screenshots.push({name,sha256:l,equal:true});checks++;
 }
 for(const file of ['core.mjs','page.mjs','index.html','launch.py','启动.cmd','使用说明.txt'])assert.ok(fs.existsSync(path.join(candidateDir,file)),`required deliverable ${file}`);
 assert.notEqual(digest(path.join(candidateDir,'core.mjs')),digest(path.join(originalDir,'core.mjs')),'independent core');
 assert.notEqual(digest(path.join(candidateDir,'page.mjs')),digest(path.join(originalDir,'page.mjs')),'independent controller');
 for(const file of ['core.mjs','page.mjs','index.html','launch.py','启动.cmd']){
  const text=fs.readFileSync(path.join(candidateDir,file),'utf8');assert.ok(!/desk-original|Project[\\/]reverse|reverse_fusion/.test(text),'no original/tools runtime dependency');
 }
 const report={status:'pass',checks,coreTraces:details,browserCheckpoints:left.trace.length,screenshots,wrongCandidateRejected:rejected,files:Object.fromEntries(['core.mjs','page.mjs','index.html','launch.py','启动.cmd','使用说明.txt'].map(n=>[n,digest(path.join(candidateDir,n))])),limitations:['Finite declared input/operation coverage; not a universal equivalence proof.','Same-machine installed Chrome visual comparison.'],cleanup:'Both owned browser contexts and browsers closed; loopback servers closed in finally.'};
 fs.writeFileSync(path.join(output,'result.json'),JSON.stringify(report,null,2));console.log(JSON.stringify(report));
}catch(e){fs.writeFileSync(path.join(output,'failure.json'),JSON.stringify({status:'fail',checks,error:e.stack},null,2));throw e;}
finally{await Promise.all(servers.map(s=>new Promise(ok=>s.close(ok))));}
