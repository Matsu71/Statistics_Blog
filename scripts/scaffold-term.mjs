import path from 'node:path';
import {
  buildMarkdownDocument,
  buildScaffold,
  contentDir,
  fileExists,
  parseCliArgs,
  printIssues,
  updateQueueForScaffold,
  validateWorkspace,
  writeJsonAtomic,
  writeTextAtomic,
  queuePath
} from './lib/term-pipeline.mjs';

async function main() {
  const args = parseCliArgs();
  const slug = typeof args.slug === 'string' ? args.slug.trim() : '';
  const dryRun = Boolean(args['dry-run']);

  if (!slug) {
    console.error('scaffold:term failed: --slug is required. Use --slug=<term-slug> or run npm run pick:next-term first.');
    process.exit(1);
  }

  const report = await validateWorkspace({ includeEditorialWarnings: false });

  if (report.errors.length > 0) {
    printIssues('scaffold:term failed because queue/content validation found errors:', report.errors);
    console.error("Next step: run 'npm run validate:content' and fix the reported items first.");
    process.exit(1);
  }

  const queueItem = report.queue.items.find((item) => item.slug === slug);

  if (!queueItem) {
    console.error(`scaffold:term failed: queue item "${slug}" was not found in data/term-queue.json.`);
    process.exit(1);
  }

  if (queueItem.status === 'published') {
    console.error(
      `scaffold:term failed: queue item "${slug}" is already published. Refusing to scaffold over an existing published page.`
    );
    process.exit(3);
  }

  const targetPath = path.join(contentDir, `${slug}.md`);

  if (await fileExists(targetPath)) {
    console.error(`scaffold:term failed: ${path.relative(process.cwd(), targetPath)} already exists. Remove it or choose another slug.`);
    process.exit(3);
  }

  for (const relatedTerm of queueItem.related_terms) {
    if (!report.queueItemBySlug.has(relatedTerm)) {
      console.error(
        `scaffold:term failed: queue item "${slug}" references unknown related term "${relatedTerm}". Fix data/term-queue.json first.`
      );
      process.exit(1);
    }
  }

  const scaffold = buildScaffold(report.queue, queueItem);
  const markdown = buildMarkdownDocument(scaffold.frontmatter, scaffold.body);

  if (dryRun) {
    console.log(`scaffold:term dry-run succeeded for ${slug}`);
    console.log(`target file: ${path.relative(process.cwd(), targetPath)}`);
    console.log(markdown);
    return;
  }

  await writeTextAtomic(targetPath, markdown);
  const updatedQueue = updateQueueForScaffold(report.queue, slug);
  await writeJsonAtomic(queuePath, updatedQueue);

  console.log(
    `scaffold:term created ${path.relative(process.cwd(), targetPath)} and updated queue status to draft.`
  );
}

main().catch((error) => {
  console.error(`scaffold:term failed: ${error.message}`);
  process.exit(1);
});
