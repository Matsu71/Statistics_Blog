import assert from 'node:assert/strict';
import { readFile, stat, writeFile, mkdir } from 'node:fs/promises';
import { createServer } from 'node:http';
import { once } from 'node:events';
import path from 'node:path';
import { chromium, webkit } from 'playwright';
import { resolveBasePath } from '../site-build.config.mjs';

const output=path.resolve('docs');
const report=JSON.parse(await readFile('project-docs/pregrade1/checks/content.json','utf8'));
const prefix=resolveBasePath()==='/'?'':resolveBasePath();
const types={'.html':'text/html; charset=utf-8','.css':'text/css','.js':'application/javascript','.json':'application/json','.svg':'image/svg+xml','.woff2':'font/woff2','.woff':'font/woff','.ttf':'font/ttf','.csv':'text/csv'};
const server=createServer(async(req,res)=>{
  try{
    const p=decodeURIComponent(new URL(req.url,'http://localhost').pathname);
    if(prefix&&p!==prefix&&!p.startsWith(prefix+'/'))throw Error('Invalid base');
    let file=path.resolve(output,'.'+(p.slice(prefix.length)||'/'));
    if(file!==output&&!file.startsWith(output+path.sep))throw Error('Outside build');
    if((await stat(file)).isDirectory())file=path.join(file,'index.html');
    res.writeHead(200,{'Content-Type':types[path.extname(file)]??'application/octet-stream'});res.end(await readFile(file));
  }catch{res.writeHead(404);res.end('Not found');}
});
server.listen(0,'127.0.0.1');await once(server,'listening');
const origin=`http://127.0.0.1:${server.address().port}`;
const url=(route)=>`${origin}${prefix}${route}`;
const errors=[];const views=[];let assertions=0;
function equal(actual,expected,message){assert.equal(actual,expected,message);assertions++;}
function ok(condition,message){assert.ok(condition,message);assertions++;}
const key='statistics-lab:pregrade1:memory:v1';
await mkdir('review-assets/pregrade1/screens',{recursive:true});
try{
  for(const [engineName,engine]of[['Chromium',chromium],['WebKit',webkit]]){
    const browser=await engine.launch({headless:true});
    try{
      const context=await browser.newContext({viewport:{width:375,height:900},acceptDownloads:true});
      const page=await context.newPage();page.setDefaultTimeout(12000);
      page.on('pageerror',e=>errors.push(`${engineName}: ${e.message}`));
      for(const width of engineName==='Chromium'?[375,1280]:[375]){
        await page.setViewportSize({width,height:900});
        for(const record of report.records){
          const response=await page.goto(url(`/learn/pregrade1/${record.slug}/`),{waitUntil:'networkidle'});
          equal(response?.status(),200);equal(await page.locator('h1').textContent(),record.title);
          equal(await page.locator('[data-lesson-id]').getAttribute('data-lesson-id'),record.id);
          equal(await page.locator('.practice-question').count(),record.questions);
          equal(await page.locator('.lesson-body details[open]').count(),0);
          equal(await page.locator('.katex-error').count(),0);ok(await page.locator('.katex').count()>0);
          const ids=await page.locator('[id]').evaluateAll(items=>items.map(item=>item.id));equal(ids.length,new Set(ids).size,'duplicate IDs');
          const links=await page.locator('.lesson-toc a').evaluateAll(items=>items.map(item=>decodeURIComponent(new URL(item.href).hash.slice(1))));
          ok(await page.evaluate(ids=>ids.every(id=>Boolean(document.getElementById(id))),links),'TOC anchors');
          for(const phase of ['closed','open']){
            if(phase==='open')await page.locator('[data-p-expand]').click();
            const geometry=await page.evaluate(()=>[document.documentElement.clientWidth,document.documentElement.scrollWidth]);
            ok(geometry[1]<=geometry[0]+2,`${engineName} ${record.id} ${width} ${phase}: overflow ${geometry}`);
            const broken=await page.locator('.lesson-body td[align="right"]').evaluateAll(cells=>cells.flatMap(cell=>{
              if(!cell.getClientRects().length)return [];
              const text=(cell.textContent??'').trim();if(!/^[+\-−]?[0-9]+(?:\.[0-9]+)?%?$/.test(text))return [];
              const range=document.createRange();range.selectNodeContents(cell);
              return new Set(Array.from(range.getClientRects()).map(rect=>Math.round(rect.top))).size>1?[text]:[];
            }));equal(broken.length,0,`${record.id}: numbers wrapped ${broken}`);
          }
          equal(await page.locator('.lesson-body details[open]').count(),record.disclosures);
          await page.locator('[data-p-collapse]').click();equal(await page.locator('.lesson-body details[open]').count(),0);
          const first=page.locator('.lesson-body details').first();await first.locator('summary').focus();await page.keyboard.press('Enter');ok(await first.evaluate(e=>e.open));
          await page.locator('[data-p-collapse]').click();
          if(engineName==='Chromium'&&width===375)await page.screenshot({path:`review-assets/pregrade1/screens/${record.id}-375.png`,fullPage:true});
          const next=report.records[report.records.indexOf(record)+1];
          equal(await page.locator('a[rel="next"]').count(),next?1:0);
          if(next)equal(await page.locator('a[rel="next"]').getAttribute('href'),`${prefix}/learn/pregrade1/${next.slug}/`);
          views.push({engine:engineName,width,id:record.id,states:['closed','open'],status:'passed'});
        }
      }
      await page.goto(url('/courses/pregrade1/'),{waitUntil:'networkidle'});
      equal(await page.locator('.course-contents a').count(),report.lesson_count);
      equal(await page.locator('.lesson-planned').count(),72-report.lesson_count);
      equal(await page.locator('#syllabus-versions a[href$=".pdf"]').count(),2);
      await page.locator('#pregrade1-search').fill('ヤコビアン');ok(await page.locator('[data-p-id="P05"]').isVisible());
      await page.locator('#pregrade1-search').fill('存在しない検索xyz987');equal(await page.locator('.course-module:visible').count(),0);
      await page.locator('#pregrade1-search').fill('');equal(await page.locator('[data-p-id]:visible').count(),72);
      await page.goto(url('/learn/pregrade1/conditional-expectation/#p01-tower-proof'),{waitUntil:'networkidle'});
      ok(await page.locator('#p01-tower-proof').evaluate(e=>e.open));equal(await page.locator('.lesson-body details[open]').count(),1);
      await page.evaluate(()=>dispatchEvent(new Event('beforeprint')));equal(await page.locator('.lesson-body details[open]').count(),await page.locator('.lesson-body details').count());
      await page.evaluate(()=>dispatchEvent(new Event('afterprint')));equal(await page.locator('.lesson-body details[open]').count(),1);
      await page.locator('[data-p-reviewed]').check();await page.locator('[data-p-save]').click();await page.reload({waitUntil:'networkidle'});ok(await page.locator('[data-p-reviewed]').isChecked());
      const downloadPromise=page.waitForEvent('download');await page.locator('[data-p-export]').click();const download=await downloadPromise;
      const exported=JSON.parse(await readFile(await download.path(),'utf8'));equal(exported.last,'P01');ok(exported.reviewed.includes('P01'));
      await page.evaluate(()=>{localStorage.setItem('statistics-lab:foundation:memory:v1','preserve-F');localStorage.setItem('statistics-lab:grade2:memory:v1','preserve-G');});
      page.once('dialog',dialog=>dialog.accept());await page.locator('[data-p-clear]').click();
      equal(await page.evaluate(key=>localStorage.getItem(key),key),null);
      equal(await page.evaluate(()=>localStorage.getItem('statistics-lab:foundation:memory:v1')),'preserve-F');
      equal(await page.evaluate(()=>localStorage.getItem('statistics-lab:grade2:memory:v1')),'preserve-G');
      await page.evaluate(key=>localStorage.setItem(key,'broken-json'),key);await page.reload({waitUntil:'networkidle'});
      ok((await page.locator('[data-p-memory-status]').textContent()).includes('形式'));equal(await page.evaluate(key=>localStorage.getItem(key),key),'broken-json');
      const firstRecord=report.records[0];
      const noJs=await browser.newContext({javaScriptEnabled:false,viewport:{width:375,height:900}});const staticPage=await noJs.newPage();
      await staticPage.goto(url(`/learn/pregrade1/${firstRecord.slug}/`));ok((await staticPage.locator('.lesson-body').textContent()).includes('条件付き期待値'));
      const native=staticPage.locator('.lesson-body details').first();await native.locator('summary').click();ok(await native.evaluate(e=>e.open));await noJs.close();
      const blocked=await browser.newContext();await blocked.addInitScript(()=>Object.defineProperty(window,'localStorage',{get(){throw new Error('Storage blocked for test');}}));
      const blockedPage=await blocked.newPage();await blockedPage.goto(url(`/learn/pregrade1/${firstRecord.slug}/`),{waitUntil:'networkidle'});
      ok((await blockedPage.locator('[data-p-memory-status]').textContent()).includes('利用できません'));ok(await blockedPage.locator('.katex').count()>0);
      await blockedPage.locator('[data-p-save]').click();ok((await blockedPage.locator('[data-p-memory-status]').textContent()).includes('保存できません'));await blocked.close();
      await context.close();
    }finally{await browser.close();}
  }
  equal(errors.length,0,errors.join('\n'));
  const evidence={status:'passed',checked_at:new Date().toISOString(),source_commit:process.env.GITHUB_SHA??null,
    assertions,lesson_views:views.length,views,page_errors:errors,
    checks:['mobile and desktop','all solutions expanded','number legibility','TOC and next links','native disclosure keyboard','deep link','print restore','search','export and isolated clear','malformed storage','blocked storage','JavaScript disabled'],
    limitations:['Screenshots are stored separately for visual review.','Automated browsers do not establish learner outcomes or substitute for an independent accessibility audit.']};
  await writeFile('project-docs/pregrade1/checks/browser.json',JSON.stringify(evidence,null,2)+'\n');
  console.log(JSON.stringify({...evidence,views:undefined},null,2));
}finally{await new Promise(resolve=>server.close(resolve));}
