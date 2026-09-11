import assert from 'node:assert/strict';
import { readFile, stat, writeFile } from 'node:fs/promises';
import { createServer } from 'node:http';
import { once } from 'node:events';
import path from 'node:path';
import { fileURLToPath } from 'node:url';
import { chromium } from 'playwright';
import { resolveBasePath } from '../site-build.config.mjs';

const root = fileURLToPath(new URL('../', import.meta.url));
const output = path.join(root, 'docs');
const reportPath = path.join(root, 'project-docs/learning-platform-design/10-foundation-validation.json');
const report = JSON.parse(await readFile(reportPath, 'utf8'));
assert.equal(report.checks?.numeric_fixtures, 'passed', 'run validate-foundation.mjs first');
const prefix = resolveBasePath() === '/' ? '' : resolveBasePath();
const types = { '.html': 'text/html; charset=utf-8', '.css': 'text/css', '.js': 'application/javascript', '.svg': 'image/svg+xml', '.json': 'application/json', '.woff2': 'font/woff2', '.woff': 'font/woff', '.ttf': 'font/ttf' };
const server = createServer(async (request, response) => {
  try {
    const urlPath = decodeURIComponent(new URL(request.url, 'http://localhost').pathname);
    if (prefix && urlPath !== prefix && !urlPath.startsWith(`${prefix}/`)) {
      response.writeHead(404); response.end('Not found'); return;
    }
    let target = path.resolve(output, `.${urlPath.slice(prefix.length) || '/'}`);
    if (!target.startsWith(output + path.sep) && target !== output) {
      response.writeHead(403); response.end('Forbidden'); return;
    }
    if ((await stat(target)).isDirectory()) target = path.join(target, 'index.html');
    response.writeHead(200, { 'Content-Type': types[path.extname(target)] ?? 'application/octet-stream' });
    response.end(await readFile(target));
  } catch { response.writeHead(404); response.end('Not found'); }
});
server.listen(0, '127.0.0.1');
await once(server, 'listening');
const origin = `http://127.0.0.1:${server.address().port}`;
const urlFor = (route) => `${origin}${prefix}${route}`;
const browser = await chromium.launch({ headless: true });
const pageErrors = [];
let assertions = 0;
let viewChecks = 0;
try {
  const context = await browser.newContext();
  const page = await context.newPage();
  page.on('pageerror', (error) => pageErrors.push(error.message));
  for (const width of [375, 1280]) {
    await page.setViewportSize({ width, height: 900 });
    const courseResponse = await page.goto(urlFor('/courses/foundation/'), { waitUntil: 'networkidle' });
    assert.equal(courseResponse.status(), 200); assertions++;
    assert.equal(await page.locator('.course-contents a').count(), report.implemented_lessons); assertions++;
    assert.equal(await page.locator('.lesson-planned').count(), report.planned_not_implemented); assertions++;
    for (const record of report.records) {
      const response = await page.goto(urlFor(`/learn/${record.slug}/`), { waitUntil: 'networkidle' });
      assert.equal(response.status(), 200); assertions++;
      assert.equal(await page.locator('h1').textContent(), record.title); assertions++;
      assert.equal(await page.locator('.practice-question').count(), record.questions); assertions++;
      assert.equal(await page.locator('.lesson-body details[open]').count(), 0); assertions++;
      assert.equal(await page.locator('.katex-error').count(), 0); assertions++;
      assert.ok(await page.locator('.katex').count() > 0); assertions++;
      const geometry = await page.evaluate(() => ({ viewport: document.documentElement.clientWidth, document: document.documentElement.scrollWidth }));
      assert.ok(geometry.document <= geometry.viewport + 2, `${record.id} horizontal overflow at ${width}px: ${JSON.stringify(geometry)}`); assertions++;
      const ids = await page.locator('[id]').evaluateAll((elements) => elements.map((element) => element.id));
      assert.equal(new Set(ids).size, ids.length, `${record.id}: duplicate rendered IDs`); assertions++;
      const first = page.locator('.lesson-body details').first();
      await first.locator('summary').focus();
      await page.keyboard.press('Enter');
      assert.ok(await first.evaluate((element) => element.open)); assertions++;
      await page.locator('[data-collapse]').click();
      assert.equal(await page.locator('.lesson-body details[open]').count(), 0); assertions++;
      await page.locator('[data-expand]').click();
      assert.equal(await page.locator('.lesson-body details[open]').count(), record.disclosures); assertions++;
      await page.locator('[data-collapse]').click();
      viewChecks++;
    }
  }
  await page.goto(urlFor('/learn/ratios-and-percentages/#f06-bound'), { waitUntil: 'networkidle' });
  assert.ok(await page.locator('#f06-bound').evaluate((element) => element.open)); assertions++;
  assert.equal(await page.locator('.lesson-body details[open]').count(), 1); assertions++;
  await page.evaluate(() => window.dispatchEvent(new Event('beforeprint')));
  assert.equal(await page.locator('.lesson-body details[open]').count(), await page.locator('.lesson-body details').count()); assertions++;
  await page.evaluate(() => window.dispatchEvent(new Event('afterprint')));
  assert.equal(await page.locator('.lesson-body details[open]').count(), 1); assertions++;
  assert.ok(await page.locator('#f06-bound').evaluate((element) => element.open)); assertions++;
  await page.goto(urlFor('/learn/asking-statistical-questions/'), { waitUntil: 'networkidle' });
  assert.equal(await page.locator('a[rel="next"]').getAttribute('href'), `${prefix}/learn/reading-a-data-table/`); assertions++;
  await page.goto(urlFor('/learn/ratios-and-percentages/'), { waitUntil: 'networkidle' });
  assert.equal(await page.locator('a[rel="next"]').count(), report.implemented_lessons > 6 ? 1 : 0); assertions++;
  await page.goto(urlFor('/'), { waitUntil: 'networkidle' });
  assert.ok(await page.locator(`a[href="${prefix}/courses/foundation/"]`).count() > 0); assertions++;
  const noJs = await browser.newContext({ javaScriptEnabled: false, viewport: { width: 375, height: 900 } });
  const staticPage = await noJs.newPage();
  await staticPage.goto(urlFor('/learn/ratios-and-percentages/'));
  assert.ok((await staticPage.locator('.lesson-body').textContent()).includes('パーセントポイント')); assertions++;
  assert.ok(await staticPage.locator('.katex').count() > 0); assertions++;
  const nativeDisclosure = staticPage.locator('.lesson-body details').first();
  await nativeDisclosure.locator('summary').click();
  assert.ok(await nativeDisclosure.evaluate((element) => element.open)); assertions++;
  assert.equal(pageErrors.length, 0, pageErrors.join('\n')); assertions++;
  await noJs.close();
  await context.close();
  report.status = 'passed';
  report.checks.browser = 'passed';
  report.browser = {
    engine: 'Chromium', automated: true,
    viewports: [375, 1280], height: 900,
    lesson_view_checks: viewChecks, assertions,
    page_errors: pageErrors,
    deep_links: 'passed', keyboard_disclosures: 'passed',
    print_event_expansion_and_restore: 'passed',
    javascript_disabled_basic_reading: 'passed',
    horizontal_document_overflow: 'none in tested pages and widths',
    completed_at: new Date().toISOString(),
    note: 'This is browser automation, not a manual visual review or a screen-reader audit.'
  };
  await writeFile(reportPath, JSON.stringify(report, null, 2) + '\n');
  console.log(JSON.stringify(report.browser, null, 2));
  console.log('foundation browser tests passed');
} finally {
  await browser.close();
  await new Promise((resolve) => server.close(resolve));
}
