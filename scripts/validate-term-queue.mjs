import { printIssues, validateWorkspace } from './lib/term-pipeline.mjs';

async function main() {
  const report = await validateWorkspace({ includeEditorialWarnings: false });

  if (report.errors.length > 0) {
    printIssues('term-queue validation failed:', report.errors);
    process.exit(1);
  }

  console.log(`term-queue validation passed (${report.queue.items.length} items checked)`);
}

main().catch((error) => {
  console.error(`validate:term-queue failed: ${error.message}`);
  process.exit(1);
});
