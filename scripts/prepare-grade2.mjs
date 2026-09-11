import { readFile, readdir, mkdir, writeFile } from 'node:fs/promises';
import assert from 'node:assert/strict';
import { createHash } from 'node:crypto';
import { parse } from 'yaml';

const manifest = JSON.parse(await readFile('src/data/grade2-course.json', 'utf8'));
const release = JSON.parse(await readFile('src/data/grade2-release.json', 'utf8'));
const planned = manifest.modules.flatMap((module) => module.lessons);
const records = [];
for (const file of (await readdir('src/content/grade2')).filter((file) => file.endsWith('.md'))) {
  const body = await readFile(`src/content/grade2/${file}`, 'utf8');
  const match = body.match(/^---\n([\s\S]*?)\n---\n/);
  assert.ok(match, `${file}: frontmatter missing`);
  const data = parse(match[1]);
  if (data.status === 'published') records.push({ id: data.lesson_id, questions: data.practice_count, sha256: createHash('sha256').update(body).digest('hex') });
}
records.sort((a, b) => a.id.localeCompare(b.id));
assert.equal(new Set(records.map((record) => record.id)).size, records.length);
if (release.stage === 'release_candidate') assert.equal(records.length, planned.length, 'A release candidate must contain all planned lessons');
const marker = {
  release: 'grade2-1.0', source_commit: process.env.GITHUB_SHA ?? 'local',
  workflow_run_id: process.env.GITHUB_RUN_ID ?? null, stage: release.stage,
  lesson_count: records.length, question_count: records.reduce((sum, record) => sum + record.questions, 0),
  built_at: new Date().toISOString(), lesson_sources: records
};
await mkdir('public', { recursive: true });
await writeFile('public/grade2-build.json', JSON.stringify(marker, null, 2) + '\n');
console.log(`Prepared ${marker.lesson_count} grade2 lessons / ${marker.question_count} questions; stage=${release.stage}`);
