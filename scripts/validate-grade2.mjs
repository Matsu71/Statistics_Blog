import assert from 'node:assert/strict';
import { readFile, readdir, mkdir, writeFile } from 'node:fs/promises';
import { createHash } from 'node:crypto';
import { parse } from 'yaml';

const manifest = JSON.parse(await readFile('src/data/grade2-course.json', 'utf8'));
const release = JSON.parse(await readFile('src/data/grade2-release.json', 'utf8'));
const coverage = JSON.parse(await readFile('src/data/grade2-coverage.json', 'utf8'));
const planned = manifest.modules.flatMap((module) => module.lessons);
assert.equal(manifest.modules.length, 10);
assert.equal(planned.length, 40);
assert.equal(new Set(planned.map((item) => item.slug)).size, 40);
planned.forEach((item, index) => assert.equal(item.id, `G${String(index + 1).padStart(2, '0')}`));
const hash = (text) => createHash('sha256').update(text).digest('hex');
async function readLessons(dir) {
  const result = [];
  for (const file of (await readdir(dir)).filter((file) => file.endsWith('.md'))) {
    const raw = await readFile(`${dir}/${file}`, 'utf8');
    const match = raw.match(/^---\n([\s\S]*?)\n---\n([\s\S]*)$/);
    assert.ok(match, `${file}: missing frontmatter`);
    result.push({ file, raw, meta: parse(match[1]), body: match[2] });
  }
  return result;
}
const foundation = await readLessons('src/content/lessons');
const authored = (await readLessons('src/content/grade2')).filter((entry) => entry.meta.status === 'published').sort((a, b) => a.meta.lesson_id.localeCompare(b.meta.lesson_id));
const all = [...foundation, ...authored];
const lookup = new Map(all.map((entry) => [entry.meta.lesson_id, entry]));
assert.equal(lookup.size, all.length, 'duplicate lesson ID');
const questions = new Set();
const allQuestions = new Set(all.flatMap((entry) => [...entry.body.matchAll(/data-question="([^"]+)"/g)].map((match) => match[1])));
const records = [];
const plain = (text) => text.replace(/```[\s\S]*?```/g, '').replace(/\$\$[\s\S]*?\$\$/g, '').replace(/\$[^$\n]+\$/g, '').replace(/\[([^\]]+)\]\([^)]+\)/g, '$1').replace(/<[^>]*>/g, '').replace(/[#*`|\s]/g, '');
for (const [index, entry] of authored.entries()) {
  const { meta, body, raw } = entry;
  const id = meta.lesson_id;
  const plan = planned[index];
  assert.equal(id, plan.id, 'published sequence has a gap');
  assert.equal(meta.slug, plan.slug);
  assert.equal(meta.title, plan.title);
  assert.equal(entry.file, meta.slug + '.md');
  assert.ok(meta.goals.length >= 1 && meta.goals.length <= 4);
  assert.equal(meta.review_status, 'self_checked', `${id}: do not infer independent review`);
  for (const p of meta.prerequisites ?? []) {
    assert.ok(lookup.has(p), `${id}: missing prerequisite ${p}`);
    assert.ok(p.startsWith('F') || p < id, `${id}: circular or future prerequisite ${p}`);
  }
  for (const required of ['## 確認問題', '## 詳しく確かめる', '## まとめと次の一歩', '## 出典・関連資料']) assert.ok(body.includes(required), `${id}: ${required}`);
  assert.ok(!/TODO:|保留:/.test(body), `${id}: unfinished statement`);
  assert.ok(!/<details\b[^>]*\sopen(?:\s|=|>)/.test(body), `${id}: answers should start collapsed`);
  const q = [...body.matchAll(/data-question="([^"]+)"/g)].map((match) => match[1]);
  assert.equal(q.length, meta.practice_count, `${id}: count mismatch`);
  assert.ok(q.length >= 4, `${id}: too few varied exercises`);
  q.forEach((question, i) => {
    assert.equal(question, `${id}-Q${i + 1}`);
    assert.ok(!questions.has(question), `duplicate ${question}`); questions.add(question);
    assert.ok(body.includes(`id="${question.toLowerCase()}-answer"`), `${question}: missing solution`);
  });
  const summaries = [...body.matchAll(/<summary>([^<]+)<\/summary>/g)];
  assert.ok(summaries.length > q.length, `${id}: no deeper explanation`);
  const references = [...body.matchAll(/\]\((https:\/\/[^)]+)\)/g)].map((match) => match[1]);
  assert.ok(references.length >= 2, `${id}: insufficient precise references`);
  const html = await readFile(`docs/learn/grade2/${meta.slug}/index.html`, 'utf8');
  assert.equal(html.match(/data-lesson-id\s*=\s*["']?([A-Z0-9-]+)/)?.[1], id, `${id}: missing body`);
  assert.equal((html.match(/data-question\s*=/g) ?? []).length, q.length, `${id}: questions not rendered`);
  assert.ok(!html.includes('katex-error'), `${id}: formula syntax error`);
  assert.ok(html.includes('katex'), `${id}: missing typeset mathematics`);
  records.push({ id, slug: meta.slug, title: meta.title, questions: q.length, question_ids: q,
    source_sha256: hash(raw), html_sha256: hash(html), prerequisites: meta.prerequisites,
    main_characters_approx: plain(body.split('## 確認問題')[0]).length,
    total_characters_approx: plain(body.split('## 出典・関連資料')[0]).length,
    references, review_status: meta.review_status });
}
const coverageResults = coverage.groups.map((group) => {
  for (const id of group.lessons) assert.ok(lookup.has(id) || planned.some((lesson) => lesson.id === id), `unknown coverage lesson: ${id}`);
  const missing = [...group.lessons.filter((id) => !lookup.has(id)), ...group.questions.filter((id) => !allQuestions.has(id))];
  return { id: group.id, status: missing.length ? 'planned' : 'implemented', missing };
});
assert.equal(coverageResults.length, 27);
if (release.stage === 'release_candidate') {
  assert.equal(authored.length, 40);
  assert.ok(coverageResults.every((row) => row.status === 'implemented'), 'uncovered syllabus rows');
  assert.equal(questions.size, 172, '39 lessons × 4 + final 16 original questions');
}
const report = { status: 'structure_passed', source_commit: process.env.GITHUB_SHA ?? null, checked_at: new Date().toISOString(),
  stage: release.stage, planned_lessons: 40, authored_lessons: authored.length, original_questions: questions.size,
  complete_course: authored.length === 40, records, coverage: coverageResults,
  limitations: ['Structural checks do not prove mathematical or pedagogical correctness.', 'Character counts omit markup, formulas and references.', 'Independent numerical and browser tests are recorded separately.'] };
await mkdir('project-docs/grade2', { recursive: true });
await writeFile('project-docs/grade2/content-validation.json', JSON.stringify(report, null, 2) + '\n');
console.log(JSON.stringify({ ...report, records: records.map(({ id, questions, main_characters_approx, total_characters_approx }) => ({ id, questions, main_characters_approx, total_characters_approx })) }, null, 2));
