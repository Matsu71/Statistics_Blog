import assert from 'node:assert/strict';
import { readFile, readdir, writeFile } from 'node:fs/promises';
import path from 'node:path';
import { fileURLToPath } from 'node:url';
import { parse } from 'yaml';

const root = fileURLToPath(new URL('../', import.meta.url));
const reportPath = path.join(root, 'project-docs/learning-platform-design/10-foundation-validation.json');
const course = JSON.parse(await readFile(path.join(root, 'src/data/foundation-course.json'), 'utf8'));
const planned = course.modules.flatMap((module) => module.lessons);
assert.equal(course.modules.length, 8, 'foundation must have eight modules');
assert.equal(planned.length, 40, 'update the agreed curriculum and this assertion together if the plan changes');
assert.equal(new Set(planned.map((lesson) => lesson.id)).size, planned.length, 'duplicate curriculum ID');
assert.equal(new Set(planned.map((lesson) => lesson.slug)).size, planned.length, 'duplicate curriculum slug');
for (const [index, lesson] of planned.entries()) {
  assert.equal(lesson.id, `F${String(index + 1).padStart(2, '0')}`, 'lesson order is not contiguous');
  assert.ok(lesson.title && lesson.objective && lesson.catalog_ids.length, `incomplete plan: ${lesson.id}`);
}

const directory = path.join(root, 'src/content/lessons');
const records = [];
const questionIds = new Set();
const sourceUrls = new Set();
const plainText = (text) => text
  .replace(/```[\s\S]*?```/g, '')
  .replace(/\$\$[\s\S]*?\$\$/g, '')
  .replace(/\$[^$\n]+\$/g, '')
  .replace(/\[([^\]]+)\]\([^)]+\)/g, '$1')
  .replace(/<[^>]*>/g, '')
  .replace(/[#*`|\s]/g, '');

for (const name of (await readdir(directory)).filter((file) => file.endsWith('.md')).sort()) {
  const raw = await readFile(path.join(directory, name), 'utf8');
  const matched = raw.match(/^---\r?\n([\s\S]*?)\r?\n---\r?\n([\s\S]*)$/);
  assert.ok(matched, `missing frontmatter: ${name}`);
  const meta = parse(matched[1]);
  const body = matched[2];
  const plan = planned.find((lesson) => lesson.id === meta.lesson_id);
  assert.ok(plan, `unknown lesson ID: ${name}`);
  assert.equal(meta.slug, plan.slug, `slug mismatch: ${name}`);
  assert.equal(meta.title, plan.title, `title mismatch: ${name}`);
  assert.equal(name, `${meta.slug}.md`, `filename mismatch: ${name}`);
  if (meta.status !== 'published') continue;
  assert.ok(!/TODO:|保留:/.test(body), `unfinished published content: ${name}`);
  for (const heading of ['## 確認問題', '## 詳しく確かめる', '## まとめと次の一歩', '## 出典・関連資料']) {
    assert.ok(body.includes(heading), `missing section ${heading}: ${name}`);
  }
  assert.ok(!/<details\b[^>]*\sopen(?:\s|=|>)/.test(body), `answers must start collapsed: ${name}`);
  const questions = [...body.matchAll(/data-question="([^"]+)"/g)].map((match) => match[1]);
  assert.ok(questions.length >= 3, `too few questions: ${name}`);
  assert.equal(questions.length, meta.practice_count, `question count mismatch: ${name}`);
  for (const id of questions) {
    assert.ok(!questionIds.has(id), `duplicate question ID: ${id}`);
    assert.ok(id.startsWith(`${meta.lesson_id}-Q`), `invalid question ID: ${id}`);
    questionIds.add(id);
  }
  const details = [...body.matchAll(/<details\s+id="([^"]+)"/g)].map((match) => match[1]);
  assert.ok(details.length > questions.length, `no deeper explanation: ${name}`);
  assert.equal(new Set(details).size, details.length, `duplicate disclosure ID: ${name}`);
  assert.equal((body.match(/<summary>/g) ?? []).length, details.length, `missing summary: ${name}`);
  assert.equal((body.match(/<\/details>/g) ?? []).length, details.length, `unclosed details: ${name}`);
  const urls = [...body.matchAll(/\]\((https:\/\/[^)]+)\)/g)].map((match) => match[1]);
  assert.ok(urls.length, `no references: ${name}`);
  urls.forEach((url) => sourceUrls.add(url));
  const html = await readFile(path.join(root, 'docs/learn', meta.slug, 'index.html'), 'utf8');
  assert.ok(html.includes(`data-lesson-id="${meta.lesson_id}"`), `not rendered: ${name}`);
  assert.ok(!html.includes('katex-error'), `math rendering error: ${name}`);
  assert.equal((html.match(/data-question=/g) ?? []).length, questions.length, `rendered questions missing: ${name}`);
  assert.ok(html.includes('class="katex'), `expected rendered mathematics: ${name}`);
  const main = body.split('## 確認問題')[0];
  const withoutReferences = body.split('## 出典・関連資料')[0];
  records.push({
    id: meta.lesson_id, slug: meta.slug, title: meta.title,
    status: meta.status, prerequisites: meta.prerequisites ?? [],
    questions: questions.length, disclosures: details.length,
    main_text_characters_approx: plainText(main).length,
    all_text_characters_approx: plainText(withoutReferences).length,
    reading_minutes_editorial: meta.reading_minutes,
    practice_minutes_editorial: meta.practice_minutes,
    review_status: meta.review_status
  });
}
records.sort((a, b) => a.id.localeCompare(b.id));
assert.ok(records.length >= 6, 'initial six lessons are required');
assert.equal(new Set(records.map((record) => record.id)).size, records.length, 'duplicate published lesson');
for (const record of records) {
  for (const prerequisite of record.prerequisites) {
    assert.ok(records.some((other) => other.id === prerequisite), `${record.id}: missing published prerequisite ${prerequisite}`);
    assert.ok(prerequisite < record.id, `${record.id}: prerequisite must precede the lesson`);
  }
}
for (let i = 0; i < records.length; i++) assert.equal(records[i].id, planned[i].id, 'published sequence has a gap');

// Independent arithmetic fixtures. These verify numerical examples, not all pedagogical claims.
const close = (actual, expected) => assert.ok(Math.abs(actual - expected) < 1e-10, `${actual} != ${expected}`);
close([2, 4, 4, 6, 8, 12].reduce((a, b) => a + b, 0) / 6, 6);
close(36 / 10, 3.6); close((36 + 4 * 20) / 10, 11.6);
close((4 + 0 + 8) / 3, 4); close(12 / 4, 3); close(12 / 2, 6);
close((2 + 10 + 10 + 10) / 4, 8); close((2 + 10) / 2, 6);
close((1.8 * 30 + 32) / (1.8 * 20 + 32), 86 / 68);
const population = [2, 4, 8, 10];
const means = population.flatMap((a, i) => population.slice(i + 1).map((b) => (a + b) / 2));
assert.deepEqual(means, [3, 5, 6, 6, 7, 9]); close(means.reduce((a, b) => a + b, 0) / means.length, 6);
close(15 / 20, 0.75); close(6 / 15, 0.4); close(6 / 20, 0.3);
close((0.4 - 0.3) / 0.3, 1 / 3); close((0.25 - 0.2) / 0.2, 0.25);
close((6 + 5) / 20, 0.55); close(100 * 1.2 * 0.8, 96);

const report = {
  status: 'content_passed_browser_pending',
  checked_at: new Date().toISOString(),
  source_commit: process.env.GITHUB_SHA ?? null,
  workflow_run_id: process.env.GITHUB_RUN_ID ?? null,
  modules: course.modules.length, planned_lessons: planned.length,
  implemented_lessons: records.length, planned_not_implemented: planned.length - records.length,
  original_questions: questionIds.size,
  records,
  source_urls: [...sourceUrls].sort(),
  checks: {
    manifest_and_ids: 'passed', published_prerequisites: 'passed',
    original_question_structure: 'passed', rendered_pages_and_math: 'passed',
    numeric_fixtures: 'passed', browser: 'pending'
  },
  limitations: [
    'Not an independent mathematical peer review.',
    'Character counts strip markup, formulas and references and are approximate.',
    'Reading time is an editorial estimate, not measured learner performance.',
    'Planned lessons do not count as implemented syllabus coverage.',
    'Automated tests do not establish superiority to benchmark materials.'
  ]
};
await writeFile(reportPath, JSON.stringify(report, null, 2) + '\n');
console.log(JSON.stringify(report, null, 2));
console.log('foundation content validation passed');
