import assert from 'node:assert/strict';
import { readFile, writeFile, stat, mkdir } from 'node:fs/promises';
import { createServer } from 'node:http';
import { once } from 'node:events';
import { fileURLToPath } from 'node:url';
import path from 'node:path';
import { createHash } from 'node:crypto';
import { chromium } from 'playwright';
import AxeBuilder from '@axe-core/playwright';
import { resolveBasePath } from '../site-build.config.mjs';
import { normalTailModel, bernoulliExperiment, coverageExperiment } from '../src/lib/foundation-labs.mjs';

const root = fileURLToPath(new URL('../', import.meta.url));
const docs = path.join(root, 'docs');
const review = path.join(root, 'review-assets/foundation-final');
await mkdir(review, { recursive: true });
const course = JSON.parse(await readFile(path.join(root,'src/data/foundation-course.json'),'utf8'));
const lessons = course.modules.flatMap(module=>module.lessons);
assert.equal(lessons.length,40);
const near=(actual,expected,tolerance=1e-11)=>assert.ok(Math.abs(actual-expected)<=tolerance,`${actual} != ${expected}`);
near(normalTailModel({mean:0,sd:1,z:1.96,mode:'upper'}).probability,0.024997895148220435);
near(normalTailModel({mean:50,sd:10,z:1.96,mode:'upper'}).boundary,69.6);
near(normalTailModel({mean:50,sd:10,z:1.96,mode:'upper'}).probability,0.024997895148220435);
near(normalTailModel({mean:0,sd:1,z:0,mode:'upper'}).probability,.5);
near(normalTailModel({mean:0,sd:1,z:1.96,mode:'central'}).probability,.9500042097035591);
assert.throws(()=>normalTailModel({mean:0,sd:0,z:1.96,mode:'upper'}));
assert.throws(()=>normalTailModel({mean:0,sd:1,z:5,mode:'upper'}));
const b100=bernoulliExperiment({p:.5,n:100,seed:12345});
const b1000=bernoulliExperiment({p:.5,n:1000,seed:12345});
assert.deepEqual(b100.history,b1000.history.slice(0,100));
assert.deepEqual(b100,bernoulliExperiment({p:.5,n:100,seed:12345}));
assert.equal(bernoulliExperiment({p:0,n:100,seed:12345}).successes,0);
assert.equal(bernoulliExperiment({p:1,n:100,seed:12345}).successes,100);
assert.throws(()=>bernoulliExperiment({p:.5,n:0,seed:12345}));
assert.throws(()=>bernoulliExperiment({p:.5,n:100,seed:0}));
const settings={mean:50,sd:10,n:100,repetitions:100,level:95,seed:12345};
const c95=coverageExperiment(settings);
const c90=coverageExperiment({...settings,level:90});
const c99=coverageExperiment({...settings,level:99});
assert.deepEqual(c95,coverageExperiment(settings));
near(c95.se,1);
near(c95.halfWidth,1.959963984540054);
assert.ok(c90.covered<=c95.covered&&c95.covered<=c99.covered);
for(let i=0;i<c95.intervals.length;i++){
  const row=c95.intervals[i];
  near(row.upper-row.lower,2*c95.halfWidth);
  near(row.estimate,c90.intervals[i].estimate);
  assert.equal(row.contains,row.lower<=settings.mean&&settings.mean<=row.upper);
}
near(coverageExperiment({...settings,n:400}).halfWidth,c95.halfWidth/2);

const sourceRecords=[];
let questions=0;
const sourceIds=new Set();
for(const lesson of lessons){
  const raw=await readFile(path.join(root,'src/content/lessons',`${lesson.slug}.md`),'utf8');
  const ids=[...raw.matchAll(/data-question=["']([^"']+)["']/g)].map(match=>match[1]);
  for(const id of ids){assert.ok(!sourceIds.has(id),`duplicate question ${id}`);sourceIds.add(id);}
  questions+=ids.length;
  assert.ok(ids.length>=3);
  assert.ok(!/TODO:|保留:/.test(raw));
  const html=await readFile(path.join(docs,'learn',lesson.slug,'index.html'),'utf8');
  assert.ok(!html.includes('katex-error'),`rendering error ${lesson.id}`);
  sourceRecords.push({id:lesson.id,slug:lesson.slug,sha256:createHash('sha256').update(raw).digest('hex'),questions:ids.length});
}
assert.equal(questions,129);
const variance=await readFile(path.join(root,'src/content/lessons/variance-and-standard-deviation.md'),'utf8');
assert.ok(!variance.includes('標準偏差の平方根を取った量まで自動的に不偏'));
const box=await readFile(path.join(root,'src/content/lessons/quartiles-and-boxplots.md'),'utf8');
assert.ok(box.includes('f14-release-box-title'));
for(const [value,coordinate] of [[1,80],[2.5,140],[4.5,220],[6.5,300],[12,520]]) near(40+40*value,coordinate);

const prefix=resolveBasePath()==='/'?'':resolveBasePath();
const mime={'.html':'text/html; charset=utf-8','.js':'application/javascript','.css':'text/css','.svg':'image/svg+xml','.json':'application/json','.woff2':'font/woff2','.woff':'font/woff','.ttf':'font/ttf','.csv':'text/csv; charset=utf-8'};
const server=createServer(async(request,response)=>{
  try{
    const urlPath=decodeURIComponent(new URL(request.url,'http://localhost').pathname);
    if(prefix&&urlPath!==prefix&&!urlPath.startsWith(prefix+'/')){response.writeHead(404);response.end();return;}
    let target=path.resolve(docs,'.'+(urlPath.slice(prefix.length)||'/'));
    if(target!==docs&&!target.startsWith(docs+path.sep)){response.writeHead(403);response.end();return;}
    if((await stat(target)).isDirectory())target=path.join(target,'index.html');
    response.writeHead(200,{'Content-Type':mime[path.extname(target)]??'application/octet-stream'});
    response.end(await readFile(target));
  }catch{response.writeHead(404);response.end('Not found');}
});
server.listen(0,'127.0.0.1');
await once(server,'listening');
const origin=`http://127.0.0.1:${server.address().port}${prefix}`;
const browser=await chromium.launch({headless:true});
const errors=[];
const missingResources=[];
const accessibility=[];
const browserChecks=[];
const screenshotLessons=new Set(['F04','F07','F09','F11','F14','F15','F22','F31','F35','F40']);
try{
  const context=await browser.newContext({viewport:{width:320,height:900},reducedMotion:'reduce'});
  const page=await context.newPage();
  page.on('pageerror',error=>errors.push(error.message));
  page.on('response',response=>{if(response.url().startsWith(origin)&&response.status()>=400)missingResources.push({url:response.url(),status:response.status()});});
  for(const lesson of lessons){
    const response=await page.goto(`${origin}/learn/${lesson.slug}/`,{waitUntil:'networkidle'});
    assert.equal(response.status(),200);
    const geometry=await page.evaluate(()=>({viewport:document.documentElement.clientWidth,document:document.documentElement.scrollWidth}));
    assert.ok(geometry.document<=geometry.viewport+2,`${lesson.id}: document overflow at 320px ${JSON.stringify(geometry)}`);
    assert.equal(await page.locator('.lesson-body .practice-question').count(),sourceRecords.find(row=>row.id===lesson.id).questions);
    const axe=await new AxeBuilder({page}).withTags(['wcag2a','wcag2aa','wcag21a','wcag21aa','wcag22aa']).analyze();
    accessibility.push({route:`/learn/${lesson.slug}/`,violations:axe.violations.map(issue=>({id:issue.id,impact:issue.impact,description:issue.description,help:issue.help,nodes:issue.nodes.map(node=>({target:node.target,failureSummary:node.failureSummary}))})),incomplete_checks:axe.incomplete.length});
    browserChecks.push({id:lesson.id,width:320,status:'passed'});
    if(screenshotLessons.has(lesson.id))await page.screenshot({path:path.join(review,`${lesson.id}-320.png`),fullPage:true});
  }
  for(const width of [375,1280]){
    await page.setViewportSize({width,height:900});
    for(const route of ['/labs/normal-area/','/labs/probability-frequency/','/labs/confidence-coverage/','/search/','/courses/foundation/coverage/','/about/','/privacy/','/errata/','/contact/']){
      const response=await page.goto(origin+route,{waitUntil:'networkidle'});
      assert.equal(response.status(),200,route);
      const geometry=await page.evaluate(()=>({viewport:document.documentElement.clientWidth,document:document.documentElement.scrollWidth}));
      assert.ok(geometry.document<=geometry.viewport+2,`${route}: overflow at ${width}`);
      if(route.startsWith('/labs/')&&route!=='/labs/'){
        assert.equal(await page.locator('[data-foundation-lab]').getAttribute('data-ready'),'true');
        assert.equal(await page.locator('[data-lab-error]').textContent(),'');
      }
      if(width===375){
        const axe=await new AxeBuilder({page}).withTags(['wcag2a','wcag2aa','wcag21a','wcag21aa','wcag22aa']).analyze();
        accessibility.push({route,violations:axe.violations.map(issue=>({id:issue.id,impact:issue.impact,description:issue.description,nodes:issue.nodes.map(node=>({target:node.target,failureSummary:node.failureSummary}))})),incomplete_checks:axe.incomplete.length});
      }
      await page.screenshot({path:path.join(review,route.replaceAll('/','_')+width+'.png'),fullPage:true});
      browserChecks.push({route,width,status:'passed'});
    }
  }
  await page.goto(origin+'/labs/normal-area/',{waitUntil:'networkidle'});
  await page.locator('#normal-z').fill('0');
  await page.locator('[data-lab-form] button').click();
  near(Number(await page.locator('[data-lab-result]').getAttribute('data-probability')),.5);
  await page.locator('#normal-z').fill('1.96');
  await page.locator('#normal-mode').selectOption('central');
  await page.locator('[data-lab-form] button').click();
  near(Number(await page.locator('[data-lab-result]').getAttribute('data-probability')),.9500042097035591);
  await page.goto(origin+'/labs/probability-frequency/',{waitUntil:'networkidle'});
  await page.locator('#frequency-p').fill('0');
  await page.locator('[data-lab-form] button').click();
  assert.equal(await page.locator('[data-lab-result]').getAttribute('data-successes'),'0');
  await page.locator('#frequency-p').fill('1');
  await page.locator('[data-lab-form] button').click();
  assert.equal(await page.locator('[data-lab-result]').getAttribute('data-successes'),'100');
  await page.goto(origin+'/labs/confidence-coverage/',{waitUntil:'networkidle'});
  assert.equal(Number(await page.locator('[data-lab-result]').getAttribute('data-covered')),c95.covered);
  await page.locator('#coverage-level').selectOption('99');
  await page.locator('[data-lab-form] button').click();
  assert.equal(Number(await page.locator('[data-lab-result]').getAttribute('data-covered')),c99.covered);
  await page.goto(origin+'/search/',{waitUntil:'networkidle'});
  assert.equal(await page.locator('[data-search-results] li').count(),40);
  await page.locator('#course-search-query').fill('不偏分散');
  assert.ok(await page.locator('[data-search-results] li').count()>0);
  await page.locator('#course-search-query').fill('zzzz-nonexistent-lesson-999');
  assert.equal(await page.locator('[data-search-results] li').count(),0);
  await page.locator('#course-search-query').fill('<img src=x onerror=alert(1)>');
  assert.equal(await page.locator('[data-search-results] img').count(),0);
  const nojs=await browser.newContext({javaScriptEnabled:false,viewport:{width:375,height:900}});
  const staticPage=await nojs.newPage();
  await staticPage.goto(origin+'/search/');
  assert.equal(await staticPage.locator('[data-search-results] li').count(),40);
  await staticPage.goto(origin+'/labs/confidence-coverage/');
  assert.ok((await staticPage.locator('main').textContent()).includes('既知の母標準偏差'));
  await nojs.close();
  assert.equal(errors.length,0,errors.join('\n'));
  assert.equal(missingResources.length,0,JSON.stringify(missingResources));
  const blockers=accessibility.flatMap(page=>page.violations.filter(issue=>['serious','critical'].includes(issue.impact)).map(issue=>({route:page.route,...issue})));
  const report={status:blockers.length?'blocked':'passed',checked_at:new Date().toISOString(),scope:'foundation_40_lessons',lessons:40,questions,source_records:sourceRecords,numerical_labs:'passed',browser_checks:browserChecks,console_errors:errors,missing_resources:missingResources,accessibility:{engine:'axe-core',tags:['wcag2a','wcag2aa','wcag21a','wcag21aa','wcag22aa'],pages:accessibility,serious_or_critical_violations:blockers.length,limitations:'Automated checks are not a complete WCAG conformity assessment, manual screenshot review, or screen-reader study.'},manual_review_status:'Targeted findings from preceding editorial review corrected; no independent human peer review claimed.'};
  await writeFile(path.join(root,'project-docs/learning-platform-design/19-final-release-audit.json'),JSON.stringify(report,null,2)+'\n');
  await writeFile(path.join(review,'audit.json'),JSON.stringify(report,null,2)+'\n');
  assert.equal(blockers.length,0,JSON.stringify(blockers,null,2));
  console.log(JSON.stringify({status:report.status,lessons:40,questions,browser_checks:browserChecks.length,accessibility_pages:accessibility.length,serious_or_critical_violations:blockers.length},null,2));
  await context.close();
}finally{await browser.close();await new Promise(resolve=>server.close(resolve));}
