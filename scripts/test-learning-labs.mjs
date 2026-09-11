import assert from 'node:assert/strict';
import { readFile, stat, writeFile, mkdir } from 'node:fs/promises';
import { createServer } from 'node:http';
import { once } from 'node:events';
import path from 'node:path';
import { fileURLToPath } from 'node:url';
import { chromium, webkit } from 'playwright';
import { resolveBasePath } from '../site-build.config.mjs';
import { coverageSimulation } from '../src/lib/learning-math.mjs';
const root=fileURLToPath(new URL('../',import.meta.url)),out=path.join(root,'docs');
const reportDir=path.join(root,'project-docs/learning-platform-design');
const content=JSON.parse(await readFile(path.join(reportDir,'10-foundation-validation.json'),'utf8'));
const prefix=resolveBasePath()==='/'?'':resolveBasePath();
const mime={'.html':'text/html; charset=utf-8','.css':'text/css','.js':'application/javascript','.svg':'image/svg+xml','.woff2':'font/woff2','.woff':'font/woff','.ttf':'font/ttf','.json':'application/json','.csv':'text/csv'};
const server=createServer(async(req,res)=>{try{const pathname=decodeURIComponent(new URL(req.url,'http://local').pathname);if(prefix&&pathname!==prefix&&!pathname.startsWith(prefix+'/'))throw Error();let target=path.resolve(out,'.'+(pathname.slice(prefix.length)||'/'));if(target!==out&&!target.startsWith(out+path.sep))throw Error();if((await stat(target)).isDirectory())target=path.join(target,'index.html');res.writeHead(200,{'Content-Type':mime[path.extname(target)]??'application/octet-stream'});res.end(await readFile(target));}catch{res.writeHead(404);res.end('Not found');}});
server.listen(0,'127.0.0.1');await once(server,'listening');
const base=`http://127.0.0.1:${server.address().port}${prefix}`,results=[],screens=path.join(root,'review-assets/screenshots');await mkdir(screens,{recursive:true});
let checks=0;function ok(value,label){assert.ok(value,label);checks++;}function equal(actual,expected,label){assert.equal(actual,expected,label);checks++;}function near(actual,expected,tolerance,label){ok(Number.isFinite(actual)&&Math.abs(actual-expected)<=tolerance,`${label}: ${actual} vs ${expected}`);}
async function geometry(page,label){const d=await page.evaluate(()=>({viewport:document.documentElement.clientWidth,width:document.documentElement.scrollWidth}));ok(d.width<=d.viewport+2,`${label}: document overflow ${JSON.stringify(d)}`);}
async function submit(page,id){await page.locator(`#${id} button[type=submit]`).click();}
try{
  for(const [engine,type] of [['Chromium',chromium],['WebKit',webkit]]){
    const browser=await type.launch({headless:true});
    try{
      const context=await browser.newContext({viewport:{width:375,height:900}}),page=await context.newPage(),errors=[];
      page.on('pageerror',error=>errors.push(error.message));
      const start=checks;
      for(const record of content.records){
        const response=await page.goto(`${base}/learn/${record.slug}/`,{waitUntil:'networkidle'});equal(response.status(),200,`${engine} ${record.id} response`);
        equal(await page.locator('.practice-question').count(),record.questions,`${record.id} questions`);
        equal(await page.locator('.lesson-body details[open]').count(),0,`${record.id} answers collapsed`);
        equal(await page.locator('.katex-error').count(),0,`${record.id} math errors`);
        await geometry(page,`${engine} ${record.id}`);
      }
      await page.goto(`${base}/courses/foundation/`,{waitUntil:'networkidle'});
      const search=page.locator('#foundation-search');await search.fill('乱数表');
      ok(await page.locator('.course-contents li:not([hidden])').count()>0,'search content');
      ok((await page.locator('.course-contents li:not([hidden])').allTextContents()).some(text=>text.includes('F04')),'search finds new example');
      await search.fill('ガウス積分');ok((await page.locator('.course-contents li:not([hidden])').allTextContents()).some(text=>text.includes('F31')),'search includes collapsed proof');
      await search.fill('zzznomatch987');equal(await page.locator('.course-contents li:not([hidden])').count(),0,'no results');
      await search.fill('');equal(await page.locator('.course-contents li:not([hidden])').count(),40,'clear results');
      await page.screenshot({path:path.join(screens,`${engine}-course-mobile.png`),fullPage:true});
      await page.goto(`${base}/learn/ratios-and-percentages/`,{waitUntil:'networkidle'});
      await page.locator('[data-mark-reviewed]').check();await page.locator('[data-save-place]').click();await page.reload({waitUntil:'networkidle'});
      ok(await page.locator('[data-mark-reviewed]').isChecked(),'mark persists');
      await page.goto(`${base}/courses/foundation/`,{waitUntil:'networkidle'});ok((await page.locator('[data-resume]').textContent()).includes('F06'),'resume persists');
      equal(await page.evaluate(()=>JSON.parse(localStorage.getItem('statistics-lab:foundation:memory:v1')).reviewed.length),1,'one reviewed lesson');
      page.once('dialog',dialog=>dialog.accept());await page.locator('[data-clear-memory]').click();equal(await page.evaluate(()=>localStorage.getItem('statistics-lab:foundation:memory:v1')),null,'only course memory deleted');
      await page.goto(`${base}/labs/`,{waitUntil:'networkidle'});
      equal(await page.locator('form:not([hidden])').count(),3,'three labs ready');await geometry(page,`${engine} labs mobile`);
      near(Number(await page.locator('#normal [data-lab-result]').getAttribute('data-probability')),.024997895148220435,1e-11,'normal upper');
      await page.locator('#normal-form select[name=mode]').selectOption('two');await submit(page,'normal-form');near(Number(await page.locator('#normal [data-lab-result]').getAttribute('data-probability')),.04999579029644087,1e-11,'normal two-sided');
      await page.locator('#normal-form select[name=mode]').selectOption('upper');await page.locator('#normal-form input[name=z]').fill('8');await submit(page,'normal-form');near(Number(await page.locator('#normal [data-lab-result]').getAttribute('data-probability'))/6.22096057427174e-16,1,2e-10,'normal extreme tail');
      await page.locator('#normal-form input[name=sigma]').fill('0');await submit(page,'normal-form');ok(!(await page.locator('#normal-form').evaluate(form=>form.checkValidity())),'zero sigma rejected');
      await page.locator('#normal-form input[name=sigma]').fill('10');await page.locator('#normal-form input[name=z]').fill('1.96');await submit(page,'normal-form');
      const frequency=await page.locator('#frequency [data-lab-result]').textContent();await submit(page,'frequency-form');equal(await page.locator('#frequency [data-lab-result]').textContent(),frequency,'frequency reproducible');
      await page.locator('#frequency-form input[name=p]').fill('0');await submit(page,'frequency-form');equal(await page.locator('#frequency [data-lab-result]').getAttribute('data-successes'),'0','p=0');
      await page.locator('#frequency-form input[name=p]').fill('1');await submit(page,'frequency-form');equal(await page.locator('#frequency [data-lab-result]').getAttribute('data-successes'),'100','p=1');
      await page.locator('#frequency-form input[name=p]').fill('0.5');await submit(page,'frequency-form');
      const expected=coverageSimulation({mu:50,sigma:10,n:25,repetitions:100,level:95,seed:12345});
      equal(Number(await page.locator('#confidence [data-lab-result]').getAttribute('data-covered')),expected.covered,'coverage same oracle input');
      near(Number(await page.locator('#confidence [data-lab-result]').getAttribute('data-half')),expected.half,1e-12,'confidence width');
      await page.locator('#confidence-form input[name=n]').fill('100');await submit(page,'confidence-form');near(Number(await page.locator('#confidence [data-lab-result]').getAttribute('data-half')),expected.half/2,1e-12,'n quadrupling halves width');
      await page.locator('#confidence-form input[name=n]').fill('25');await submit(page,'confidence-form');
      equal(await page.locator('#confidence tbody tr').count(),10,'accessible interval table');
      await page.screenshot({path:path.join(screens,`${engine}-labs-mobile.png`),fullPage:true});
      for(const [slug,extra] of [['quartiles-and-boxplots',''],['reporting-statistical-results',''],['normal-density-basics',''],['population-and-sampling','#f04-random-table'],['regression-line-and-prediction','#f20-regression-figure']]){
        await page.goto(`${base}/learn/${slug}/${extra}`,{waitUntil:'networkidle'});await geometry(page,`${engine} ${slug} corrected`);await page.screenshot({path:path.join(screens,`${engine}-${slug}-mobile.png`),fullPage:true});
      }
      await page.setViewportSize({width:1280,height:900});await page.goto(`${base}/labs/`,{waitUntil:'networkidle'});await geometry(page,`${engine} labs desktop`);await page.screenshot({path:path.join(screens,`${engine}-labs-desktop.png`),fullPage:true});
      await page.goto(`${base}/coverage/foundation/`,{waitUntil:'networkidle'});equal(await page.locator('.course-module').count(),20,'coverage groups');
      await page.goto(`${base}/about/`,{waitUntil:'networkidle'});ok((await page.locator('#privacy').textContent()).includes('プライバシー'),'privacy page');
      const blocked=await browser.newContext({viewport:{width:375,height:900}});await blocked.addInitScript(()=>{Object.defineProperty(window,'localStorage',{get(){throw new DOMException('Blocked','SecurityError');}});});const restricted=await blocked.newPage();
      await restricted.goto(`${base}/learn/ratios-and-percentages/`,{waitUntil:'networkidle'});ok((await restricted.locator('.lesson-body').textContent()).includes('パーセントポイント'),'blocked storage keeps content');await restricted.locator('[data-mark-reviewed]').check();ok((await restricted.locator('[data-memory-status]').textContent()).includes('保存できません'),'blocked write reported');
      const noJs=await browser.newContext({javaScriptEnabled:false,viewport:{width:375,height:900}});const staticPage=await noJs.newPage();await staticPage.goto(`${base}/labs/`);ok((await staticPage.locator('#normal [data-lab-result]').textContent()).includes('69.6'),'static numeric example');equal(await staticPage.locator('form:not([hidden])').count(),0,'JS-only controls hidden');
      equal(errors.length,0,errors.join('\n'));results.push({engine,assertions:checks-start,lesson_mobile_checks:40,features:['content and proof search','explicit local memory save/delete','storage denied','normal tails and domain validation','seed replay','p=0/p=1','CI width scaling','interval table','no-JS fallback','mobile/desktop geometry'],page_errors:errors});
      await noJs.close();await blocked.close();await context.close();
    }finally{await browser.close();}
  }
  const report={status:'passed',checked_at:new Date().toISOString(),source_commit:process.env.GITHUB_SHA??null,assertions:checks,engines:results,screenshots:'review-assets/screenshots',limitations:['Automated browser checks are not human usability testing or full accessibility certification.','Screenshot images require visual review.','Independent numerical function checks are recorded separately.']};
  await writeFile(path.join(reportDir,'18-learning-experience-tests.json'),JSON.stringify(report,null,2)+'\n');console.log(JSON.stringify(report,null,2));
}finally{await new Promise(resolve=>server.close(resolve));}
