import assert from 'node:assert/strict';
import { readFile, readdir, mkdir, writeFile } from 'node:fs/promises';
import { createHash } from 'node:crypto';
import { parse } from 'yaml';

const phase = process.argv[2] ?? 'validate';
assert.ok(['prepare','validate'].includes(phase));
const hash = (text) => createHash('sha256').update(text).digest('hex');
const course = JSON.parse(await readFile('src/data/pregrade1-course.json','utf8'));
const release = JSON.parse(await readFile('src/data/pregrade1-release.json','utf8'));
const planned = course.modules.flatMap((module) => module.lessons);
assert.equal(planned.length, course.planned_lessons);
assert.equal(planned.length, 72);
assert.equal(new Set(planned.map((item) => item.slug)).size, 72);
planned.forEach((item, i) => assert.equal(item.id, `P${String(i+1).padStart(2,'0')}`));
const courses = [['lessons','F'],['grade2','G'],['pregrade1','P']];
const all = [];
for (const [directory,prefix] of courses) {
  for (const name of (await readdir(`src/content/${directory}`)).filter((name) => name.endsWith('.md'))) {
    const path = `src/content/${directory}/${name}`;
    const raw = await readFile(path,'utf8');
    const match = raw.match(/^---\r?\n([\s\S]*?)\r?\n---\r?\n([\s\S]*)$/);
    assert.ok(match, path);
    const meta = parse(match[1]);
    if (meta.status === 'published') all.push({path,name,meta,body:match[2],raw,prefix});
  }
}
const lookup = new Map(all.map((entry) => [entry.meta.lesson_id,entry]));
assert.equal(lookup.size,all.length,'duplicate ID across courses');
const authored = all.filter((entry) => entry.prefix === 'P').sort((a,b) => a.meta.lesson_id.localeCompare(b.meta.lesson_id));
assert.equal(authored.length,release.candidate_lessons);
assert.equal(all.filter((entry) => entry.prefix === 'F').length,40);
assert.equal(all.filter((entry) => entry.prefix === 'G').length,40);
const questions = new Set();
const records = [];
const plain = (text) => text.replace(/\$\$[\s\S]*?\$\$/g,'').replace(/\$[^$\n]+\$/g,'').replace(/<\/?(?:section|summary|details|figure|figcaption|svg|path|g|text|title|desc|p)\b[^>]*>/g,'').replace(/\[([^\]]+)\]\([^)]+\)/g,'$1').replace(/[#*`|\s]/g,'');
for (const [i,entry] of authored.entries()) {
  const { meta,body,raw,path,name } = entry;
  const id = meta.lesson_id;
  assert.equal(id,planned[i].id,'published sequence has a gap');
  assert.equal(meta.title,planned[i].title);
  assert.equal(meta.slug,planned[i].slug);
  assert.equal(name,`${meta.slug}.md`);
  assert.equal(meta.review_status,'self_checked','external review needs separately supplied evidence');
  for (const predecessor of meta.prerequisites ?? []) {
    assert.ok(lookup.has(predecessor),`${id}: missing prerequisite ${predecessor}`);
    assert.ok(!predecessor.startsWith('P') || predecessor < id,`${id}: forward prerequisite ${predecessor}`);
  }
  for (const heading of ['## 確認問題','## 詳しく確かめる','## まとめと次の一歩','## 出典・関連資料']) assert.ok(body.includes(heading),`${id}: ${heading}`);
  assert.ok(!/<details\b[^>]*\sopen(?:[\s=>])/.test(body),`${id}: answers not initially closed`);
  assert.ok(!/TODO:|保留:/.test(body));
  const ids = [...body.matchAll(/data-question="([^"]+)"/g)].map((match) => match[1]);
  assert.equal(ids.length,meta.practice_count);
  assert.ok(ids.length>=4);
  ids.forEach((q,j) => {
    assert.equal(q,`${id}-Q${j+1}`);assert.ok(!questions.has(q));questions.add(q);
    assert.ok(body.includes(`id="${q.toLowerCase()}"`));
    assert.ok(body.includes(`id="${q.toLowerCase()}-answer"`));
  });
  const details = [...body.matchAll(/<details\s+id="([^"]+)"/g)].map((m) => m[1]);
  assert.ok(details.length>ids.length,'an appropriate optional derivation is required');
  assert.equal(new Set(details).size,details.length);
  assert.equal((body.match(/<summary>/g)??[]).length,details.length);
  assert.equal((body.match(/<\/details>/g)??[]).length,details.length);
  const urls = [...body.matchAll(/\]\((https:\/\/[^)]+)\)/g)].map((m) => m[1]);
  assert.ok(urls.length>=2,`${id}: precise source links required`);
  const record = {id,slug:meta.slug,title:meta.title,path,source_sha256:hash(raw),questions:ids.length,
    question_ids:ids,disclosures:details.length,detail_ids:details,prerequisites:meta.prerequisites,
    main_text_characters_approx:plain(body.split('## 確認問題')[0]).length,
    total_text_characters_approx:plain(body.split('## 出典・関連資料')[0]).length,
    source_urls:urls,review_status:meta.review_status};
  if (phase === 'validate') {
    const html = await readFile(`docs/learn/pregrade1/${meta.slug}/index.html`,'utf8');
    assert.equal(html.match(/data-lesson-id\s*=\s*["']?([A-Z0-9]+)/)?.[1],id,`${id}: rendered article missing`);
    assert.equal((html.match(/data-question\s*=/g)??[]).length,ids.length);
    assert.ok(!html.includes('katex-error'));
    assert.ok(/class=(?:"[^"]*\bkatex\b|'[^']*\bkatex\b|katex[\s>])/.test(html),`${id}: no rendered formula`);
    record.html_sha256=hash(html);
  }
  records.push(record);
}
assert.equal(questions.size,release.candidate_questions);
const marker = {release:'pregrade1-initial',source_commit:process.env.GITHUB_SHA??'local',
  workflow_run_id:process.env.GITHUB_RUN_ID??null,lesson_count:records.length,question_count:questions.size,
  planned_lessons:72,existing_courses:{foundation:{lessons:40,questions:130},grade2:{lessons:40,questions:172}},
  lesson_source_sha256:Object.fromEntries(records.map((r)=>[r.path,r.source_sha256]))};
await mkdir('project-docs/pregrade1/checks',{recursive:true});
if (phase==='prepare') {
  await mkdir('public',{recursive:true});
  await writeFile('public/pregrade1-build.json',JSON.stringify(marker,null,2)+'\n');
  console.log(`Prepared marker for ${records.length} pre-grade1 lessons; no manuscripts were rewritten.`);
} else {
  assert.deepEqual(JSON.parse(await readFile('docs/pregrade1-build.json','utf8')),marker,'source changed after build preparation');
  const report={status:'passed',source_commit:marker.source_commit,checked_at:new Date().toISOString(),
    lesson_count:records.length,question_count:questions.size,planned_lessons:72,records,
    limitations:['Structure does not prove mathematical correctness.','Character counts exclude formulas, markup and references and are approximate.','Only authored lessons count as implemented.']};
  await writeFile('project-docs/pregrade1/checks/content.json',JSON.stringify(report,null,2)+'\n');
  console.log(JSON.stringify({...report,records:records.map(({id,questions,main_text_characters_approx,total_text_characters_approx})=>({id,questions,main_text_characters_approx,total_text_characters_approx}))},null,2));
}
