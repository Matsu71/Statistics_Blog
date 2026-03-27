import {
  buildTermIndex,
  generatedTermIndexPath,
  printIssues,
  validateWorkspace,
  writeJsonAtomic
} from './lib/term-pipeline.mjs';

async function main() {
  const report = await validateWorkspace({ includeEditorialWarnings: false });

  if (report.errors.length > 0) {
    printIssues('generate:index failed because validation found errors:', report.errors);
    process.exit(1);
  }

  const termIndex = buildTermIndex(report.queue, report.contentBySlug);
  await writeJsonAtomic(generatedTermIndexPath, termIndex);

  console.log(
    `generate:index wrote ${generatedTermIndexPath.replace(`${process.cwd()}/`, '')} (${termIndex.publishedTerms.length} published term(s))`
  );
}

main().catch((error) => {
  console.error(`generate:index failed: ${error.message}`);
  process.exit(1);
});
