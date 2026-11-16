// Held independent UI checks for the repository-owned desk qualification app.
// Maintainer fixture verifier, not a generic target-equivalence oracle.
const fs = require('node:fs'), path = require('node:path'), http = require('node:http');
const {createHash} = require('node:crypto');
const modules = process.env.RF_NODE_MODULES;
if (!modules) throw Error('Set RF_NODE_MODULES to the reviewed Playwright/pngjs package root');
const {chromium} = require(require.resolve('playwright', {paths: [modules]}));
const {PNG} = require(require.resolve('pngjs', {paths: [modules]}));
const [originalArg, candidateArg, outputArg] = process.argv.slice(2);
if (!outputArg) throw Error('Expected original-directory candidate-directory NEW-output-directory');
const original = fs.realpathSync(originalArg), candidate = fs.realpathSync(candidateArg);
if (original === candidate) throw Error('Original and candidate directories must differ');
const output = path.resolve(outputArg);
if (fs.existsSync(output)) throw Error('Output already exists; preserve old comparison');
fs.mkdirSync(output, {recursive: true});
const hash = data => createHash('sha256').update(data).digest('hex');
const inventory = root => fs.readdirSync(root, {recursive: true, withFileTypes: true})
  .filter(entry => entry.isFile() && /\.(html|mjs|js|css)$/.test(entry.name))
  .map(entry => {const p=path.join(entry.parentPath ?? entry.path,entry.name);return {path:path.relative(root,p),sha256:hash(fs.readFileSync(p))};});
const before = {original:inventory(original),candidate:inventory(candidate)};
const server = http.createServer((req,res) => {
  const parts = decodeURIComponent(new URL(req.url, 'http://local').pathname).split('/').filter(Boolean);
  const side = parts.shift();
  const base = side === 'original' ? original : side === 'candidate' ? candidate : null;
  if (!base || parts.some(part => part === '..')) {res.writeHead(404).end();return;}
  const file = path.resolve(base,...parts, ...(parts.length ? [] : ['index.html']));
  if (!file.startsWith(base + path.sep) || !fs.existsSync(file) || !fs.statSync(file).isFile()) {res.writeHead(404).end();return;}
  res.setHeader('Content-Type', file.endsWith('.html') ? 'text/html;charset=utf-8' : file.endsWith('.css') ? 'text/css' : 'text/javascript');
  res.end(fs.readFileSync(file));
});
async function exercise(browser, side, viewport) {
  const context = await browser.newContext({viewport,locale:'zh-CN',reducedMotion:'reduce'});
  const page = await context.newPage(), errors=[];
  page.on('pageerror',error => errors.push(error.message));
  const url = `http://127.0.0.1:${server.address().port}/${side}/`;
  await page.goto(url); const states=[];
  async function record(name) {
    states.push({name, rows:await page.locator('tbody tr').allTextContents(),
      alerts:await page.getByRole('alert').allTextContents(),
      body:await page.locator('main').innerText(),
      horizontalOverflow:await page.evaluate(() => document.documentElement.scrollWidth > innerWidth)});
  }
  async function add(name,tag,quantity) {
    await page.getByLabel('名称',{exact:true}).fill(name);
    await page.getByLabel('分类',{exact:true}).fill(tag);
    await page.getByLabel('数量',{exact:true}).fill(quantity);
    // Use form submission so native number input validity does not mask app rules.
    await page.locator('form').evaluate(form => form.dispatchEvent(new Event('submit',{bubbles:true,cancelable:true})));
  }
  await record('empty');
  const emptyImage = await page.screenshot({fullPage:true,animations:'disabled'});
  fs.writeFileSync(path.join(output,`${side}-${viewport.width}-empty.png`),emptyImage);
  await add('  灯具  ','  办公  ','3');await record('trimmed-name');
  await add('Screw','工具','2');await add('screw','工具','1');await record('case-insensitive-duplicate');
  await add('Screw','备件','4');await add('<img src=x onerror=window.bad=1>','','1');await record('literal-html');
  await add('','','1');await record('blank-error');
  await add('无效数量','','100');await record('out-of-range-error');
  await page.getByLabel('搜索名称或分类').fill(' screw ');await record('filtered-summary');
  await page.getByLabel('搜索名称或分类').fill('不存在');await record('no-matches');
  await page.getByLabel('搜索名称或分类').fill('');
  await page.getByRole('combobox',{name:/^排序/}).selectOption('name');await record('name-order');
  await page.reload();await record('persisted-on-reload');
  await page.getByRole('button',{name:'删除',exact:true}).first().click();await record('delete-one');
  page.once('dialog',dialog => dialog.dismiss());await page.getByRole('button',{name:'清空全部',exact:true}).click();
  await record('cancel-clear');
  page.once('dialog',dialog => dialog.accept());await page.getByRole('button',{name:'清空全部',exact:true}).click();
  await record('confirm-clear');await page.reload();await record('persisted-clear');
  await page.evaluate(() => {for(const key of Object.keys(localStorage))localStorage.setItem(key,'{damaged');});
  await page.reload();await record('damaged-storage-recovery');
  const finalImage = await page.screenshot({fullPage:true,animations:'disabled'});
  fs.writeFileSync(path.join(output,`${side}-${viewport.width}-final.png`),finalImage);
  const bad = await page.evaluate(() => Boolean(window.bad));
  await context.close();
  return {states,errors,scriptExecutedFromItemName:bad,emptyImage,finalImage};
}
function pixels(left,right) {
  const a=PNG.sync.read(left),b=PNG.sync.read(right);
  if (a.width!==b.width || a.height!==b.height) return {status:'fail',reason:'image dimensions differ',left:[a.width,a.height],right:[b.width,b.height]};
  let differing=0;
  for(let i=0;i<a.data.length;i+=4)if(a.data[i]!==b.data[i]||a.data[i+1]!==b.data[i+1]||a.data[i+2]!==b.data[i+2]||a.data[i+3]!==b.data[i+3])differing++;
  return {status:differing===0?'pass':'fail',differingPixels:differing,pixels:a.width*a.height};
}
(async()=>{
  await new Promise(resolve=>server.listen(0,'127.0.0.1',resolve));
  let browser;
  try {
    browser=await chromium.launch({headless:true,...(process.env.RF_BROWSER ? {executablePath:process.env.RF_BROWSER} : {})});const measurements=[];
    for(const viewport of [{width:1100,height:850},{width:390,height:844}]){
      const start=performance.now();const left=await exercise(browser,'original',viewport),right=await exercise(browser,'candidate',viewport);
      const behavior=JSON.stringify(left.states)===JSON.stringify(right.states)&&left.errors.length===0&&right.errors.length===0&&!left.scriptExecutedFromItemName&&!right.scriptExecutedFromItemName;
      const empty=pixels(left.emptyImage,right.emptyImage),final=pixels(left.finalImage,right.finalImage);
      delete left.emptyImage;delete left.finalImage;delete right.emptyImage;delete right.finalImage;
      measurements.push({viewport,behavior:behavior?'pass':'fail',emptyVisual:empty,finalVisual:final,left,right,elapsedMs:Math.round(performance.now()-start)});
    }
    const unchanged=JSON.stringify(before)===JSON.stringify({original:inventory(original),candidate:inventory(candidate)});
    const result={scope:'owned desk app finite UI behavior and exact screenshot comparison; no arbitrary target claim',verifierSha256:hash(fs.readFileSync(__filename)),sources:before,inputFixity:unchanged,
      status:unchanged&&measurements.every(x=>x.behavior==='pass'&&x.emptyVisual.status==='pass'&&x.finalVisual.status==='pass')?'pass':'fail',measurements};
    fs.writeFileSync(path.join(output,'comparison.json'),JSON.stringify(result,null,2));console.log(JSON.stringify({status:result.status,output,checks:measurements.map(x=>({viewport:x.viewport,behavior:x.behavior,empty:x.emptyVisual,final:x.finalVisual,elapsedMs:x.elapsedMs}))}));
    process.exitCode=result.status==='pass'?0:1;
  } finally {if(browser)await browser.close();await new Promise(resolve=>server.close(resolve));}
})().catch(error=>{console.error(error);process.exitCode=2;server.close();});
