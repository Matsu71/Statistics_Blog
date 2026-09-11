import assert from 'node:assert/strict';
import { readFile, stat, writeFile, mkdir } from 'node:fs/promises';
import { createServer } from 'node:http';
import { once } from 'node:events';
import path from 'node:path';
import { chromium, webkit } from 'playwright';
import { resolveBasePath } from '../site-build.config.mjs';

const out = path.resolve('docs');
const report = JSON.parse(await readFile('project-docs/grade2/content-validation.json','utf8'));
const prefix = resolveBasePath() === '/' ? '' : resolveBasePath();
const mime = {'.html':'text/html; charset=utf-8','.js':'application/javascript','.css':'text/css','.json':'application/json','.svg':'image/svg+xml','.woff2':'font/woff2','.woff':'font/woff','.ttf':'font/ttf','.csv':'text/csv'};
const server = createServer(async(req,res)=>{
  try {
    const url = decodeURIComponent(new URL(req.url,'http://localhost').pathname);
    if(prefix && url !== prefix && !url.startsWith(prefix+'/')) throw new Error('Outside base');
    let file = path.resolve(out, '.'+(url.slice(prefix.length)||'/'));
    if(file !== out && !file.startsWith(out+path.sep)) throw new Error('Outside root');
    if((await stat(file)).isDirectory()) file=path.join(file,'index.html');
    res.writeHead(200,{'Content-Type':mime[path.extname(file)]??'application/octet-stream'});res.end(await readFile(file));
  } catch {res.writeHead(404);res.end('Not found');}
});
server.listen(0,'127.0.0.1');await once(server,'listening');
const origin=`http://127.0.0.1:${server.address().port}`;
const url=(p)=>origin+prefix+p;
const results=[]; const errors=[]; let assertions=0;
await mkdir('review-assets/grade2/screens',{recursive:true});
try {
  for(const [name,engine] of [['Chromium',chromium],['WebKit',webkit]]) {
    const browser=await engine.launch({headless:true});
    try {
      const context=await browser.newContext({viewport:{width:375,height:900},acceptDownloads:true});
      const page=await context.newPage();page.on('pageerror',e=>errors.push(`${name}: ${e.message}`));
      page.setDefaultTimeout(12000);
      for(const width of [375,1280]) {
        if(name==='WebKit' && width===1280)continue;
        await page.setViewportSize({width,height:900});
        for(const lesson of report.records) {
          const response=await page.goto(url(`/learn/grade2/${lesson.slug}/`),{waitUntil:'networkidle'});
          assert.equal(response.status(),200);assertions++;
          assert.equal(await page.locator('h1').textContent(),lesson.title);assertions++;
          assert.equal(await page.locator('[data-lesson-id]').getAttribute('data-lesson-id'),lesson.id);assertions++;
          assert.equal(await page.locator('.practice-question').count(),lesson.questions);assertions++;
          assert.equal(await page.locator('.lesson-body details[open]').count(),0);assertions++;
          assert.equal(await page.locator('.katex-error').count(),0);assertions++;
          assert.ok(await page.locator('.katex').count()>0);assertions++;
          const geometry=await page.evaluate(()=>[document.documentElement.clientWidth,document.documentElement.scrollWidth]);
          assert.ok(geometry[1]<=geometry[0]+2,`${name} ${lesson.id} ${width} overflow ${geometry}`);assertions++;
          const brokenNumbers=await page.locator('.lesson-body td[align="right"]').evaluateAll(cells=>cells.flatMap(cell=>{
            const text=(cell.textContent??'').trim();
            if(!/^[+\-−]?[0-9]+(?:\.[0-9]+)?(?:e[+\-]?[0-9]+)?%?$/i.test(text))return [];
            const range=document.createRange();range.selectNodeContents(cell);
            const lines=new Set(Array.from(range.getClientRects()).map(rect=>Math.round(rect.top)));
            return lines.size>1?[text]:[];
          }));
          assert.deepEqual(brokenNumbers,[],`${name} ${lesson.id}: number split across lines`);assertions++;
          const ids=await page.locator('[id]').evaluateAll(items=>items.map(item=>item.id));
          assert.equal(ids.length,new Set(ids).size,`${lesson.id}: duplicate IDs`);assertions++;
          const first=page.locator('.lesson-body details').first();await first.locator('summary').focus();await page.keyboard.press('Enter');
          assert.ok(await first.evaluate(e=>e.open));assertions++;
          await page.locator('[data-g2-collapse]').click();
          assert.equal(await page.locator('.lesson-body details[open]').count(),0);assertions++;
          if(['G03','G18','G23','G25','G26','G33','G35','G38','G39','G40'].includes(lesson.id)&&width===375&&name==='Chromium') await page.screenshot({path:`review-assets/grade2/screens/${lesson.id}-${width}.png`,fullPage:true});
          results.push({engine:name,width,lesson:lesson.id,status:'passed'});
        }
      }
      await page.goto(url('/courses/grade2/'),{waitUntil:'networkidle'});
      assert.equal(await page.locator('.course-contents a').count(),report.authored_lessons);assertions++;
      await page.locator('#grade2-search').fill('有限母集団');
      assert.ok(await page.locator('li[data-grade2-id="G05"]').isVisible());assertions++;
      await page.locator('#grade2-search').fill('ない語句abcdefxyz');
      assert.equal(await page.locator('.course-module:visible').count(),0);assertions++;
      await page.locator('#grade2-search').fill('');
      assert.equal(await page.locator('li[data-grade2-id]:visible').count(),40);assertions++;
      const first=report.records[0];await page.goto(url(`/learn/grade2/${first.slug}/#g01-sum-proof`),{waitUntil:'networkidle'});
      assert.ok(await page.locator('#g01-sum-proof').evaluate(e=>e.open));assertions++;
      await page.evaluate(()=>dispatchEvent(new Event('beforeprint')));
      assert.equal(await page.locator('.lesson-body details[open]').count(),await page.locator('.lesson-body details').count());assertions++;
      await page.evaluate(()=>dispatchEvent(new Event('afterprint')));
      assert.equal(await page.locator('.lesson-body details[open]').count(),1);assertions++;
      await page.locator('[data-g2-reviewed]').check();await page.locator('[data-g2-save]').click();
      await page.reload({waitUntil:'networkidle'});assert.ok(await page.locator('[data-g2-reviewed]').isChecked());assertions++;
      await page.evaluate(()=>localStorage.setItem('statistics-lab:foundation:memory:v1','foundation-preservation-sentinel'));
      page.once('dialog',dialog=>dialog.accept());await page.locator('[data-g2-clear]').click();
      assert.equal(await page.evaluate(()=>localStorage.getItem('statistics-lab:foundation:memory:v1')),'foundation-preservation-sentinel');assertions++;
      assert.equal(await page.evaluate(()=>localStorage.getItem('statistics-lab:grade2:memory:v1')),null);assertions++;
      await page.goto(url('/coverage/grade2/'),{waitUntil:'networkidle'});
      assert.equal(await page.locator('.course-module').count(),27);assertions++;
      const links=await page.locator('[data-grade2-coverage] a[href*="#"]').evaluateAll(items=>items.map(item=>item.href));
      for(const target of [...new Set(links)]) {
        const documentUrl=new URL(target);documentUrl.hash='';
        const http=await page.request.get(documentUrl.href);assert.equal(http.status(),200);assertions++;
        await page.goto(target,{waitUntil:'domcontentloaded'});
        assert.equal(new URL(page.url()).pathname,documentUrl.pathname);assertions++;
        const id=decodeURIComponent(new URL(target).hash.slice(1));
        assert.ok(await page.evaluate(id=>Boolean(document.getElementById(id)),id),`missing coverage anchor: ${target}`);assertions++;
      }
      const noJs=await browser.newContext({javaScriptEnabled:false,viewport:{width:375,height:900}});
      const staticPage=await noJs.newPage();await staticPage.goto(url(`/learn/grade2/${first.slug}/`));
      assert.ok((await staticPage.locator('.lesson-body').textContent()).includes('母数'));assertions++;
      const detail=staticPage.locator('.lesson-body details').first();await detail.locator('summary').click();assert.ok(await detail.evaluate(e=>e.open));assertions++;
      await noJs.close();
      await context.close();
    } finally {await browser.close();}
  }
  assert.deepEqual(errors,[]);
  const evidence={status:'passed',checked_at:new Date().toISOString(),source_commit:process.env.GITHUB_SHA??null,
    assertions,views:results.length,results,page_errors:errors,
    tested:['all authored grade2 pages','mobile and desktop layout','keyboard details','deep links','print expand/restore','full-text search','isolated local memory','syllabus links','JavaScript-disabled basic reading'],
    limits:['Automated browsers are not user studies or a screen-reader audit.','Screenshots require separate visual review.']};
  await writeFile('project-docs/grade2/browser-validation.json',JSON.stringify(evidence,null,2)+'\n');
  console.log(JSON.stringify({...evidence,results:undefined},null,2));
} finally {await new Promise(resolve=>server.close(resolve));}
