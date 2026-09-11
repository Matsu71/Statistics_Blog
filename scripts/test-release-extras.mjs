import assert from 'node:assert/strict';
import { readFile, writeFile } from 'node:fs/promises';
import path from 'node:path';
import { fileURLToPath } from 'node:url';
const root=fileURLToPath(new URL('../',import.meta.url));
const reportDir=path.join(root,'project-docs/learning-platform-design');
const report=JSON.parse(await readFile(path.join(reportDir,'10-foundation-validation.json'),'utf8'));
const coverage=JSON.parse(await readFile(path.join(root,'src/data/foundation-coverage.json'),'utf8'));
assert.equal(report.implemented_lessons,40);assert.equal(report.original_questions,130);
assert.equal(coverage.rows.length,20);assert.equal(new Set(coverage.rows.map(row=>row.id)).size,20);
const records=new Map(report.records.map(record=>[record.id,record]));
const questions=new Set(),sources={};
for(const record of report.records){
  const text=await readFile(path.join(root,'src/content/lessons',record.slug+'.md'),'utf8');sources[record.id]=text;
  for(const match of text.matchAll(/data-question="([^"]+)"/g))questions.add(match[1]);
}
for(const row of coverage.rows){
  assert.ok(row.focus&&row.source_locator&&row.question_ids.length);
  row.lesson_ids.forEach(id=>assert.ok(records.has(id),`missing lesson ${id}`));
  row.question_ids.forEach(id=>assert.ok(questions.has(id),`missing question ${id}`));
  row.source_ids.forEach(id=>assert.ok(coverage.sources.some(source=>source.id===id),`missing source ${id}`));
}
assert.ok(sources.F04.includes('f04-random-table')&&sources.F04.includes('F04-Q4'));
assert.ok(sources.F14.includes('M50 65H110')&&sources.F14.includes('<text x="50" y="122">1</text>'));
assert.ok(sources.F19.includes('M45 20V220H415'));
assert.ok(sources.F07.includes('f07-cumulative-figure'));assert.ok(sources.F20.includes('f20-regression-figure'));
assert.ok(sources.F39.includes('|S10|9|')&&!sources.F39.includes('|試料|S01|S02|'));
for(const id of ['F28','F31','F32','F35'])assert.ok(sources[id].includes('../../labs/#'));
const about=await readFile(path.join(root,'docs/about/index.html'),'utf8');for(const id of ['scope','review','sources','errata','privacy'])assert.ok(about.includes(`id="${id}"`)||about.includes(`id=${id}`));
const utility=await readFile(path.join(root,'src/components/LearningTools.astro'),'utf8');assert.ok(utility.includes('localStorage'));assert.ok(!utility.includes('fetch(')&&!utility.includes('sendBeacon')&&!utility.includes('XMLHttpRequest'),'memory/search must stay local');
const correctionChecks=['F04 random-number worked example and fourth problem','F07 cumulative graph','F14 boxplot linear scale','F19 scatterplot origin','F20 fitted line and vertical residuals','F39 legible vertical data table','Four links to interactive labs','Forty lessons and 130 original questions','Twenty coverage groups with resolvable lesson/question/source IDs','Editorial, corrections and privacy routes'];
await writeFile(path.join(reportDir,'19-release-structure-tests.json'),JSON.stringify({status:'passed',checked_at:new Date().toISOString(),source_commit:process.env.GITHUB_SHA??null,lessons:40,questions:130,coverage_groups:20,correction_checks:correctionChecks,scope:'Structural and specified source corrections only; does not prove all mathematical statements.'},null,2)+'\n');
console.log('Release structural checks passed: 40 lessons, 130 questions, 20 coverage groups.');
