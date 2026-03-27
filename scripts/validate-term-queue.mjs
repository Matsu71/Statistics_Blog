import { printIssues, validateWorkspace } from './lib/term-pipeline.mjs';

async function main() {
  const report = await validateWorkspace({ includeEditorialWarnings: false });

  if (report.errors.length > 0) {
    printIssues('term-queue validation failed:', report.errors);
    console.error("Look at: data/term-queue.json and src/content/terms/*.md.");
    console.error("Next step: align queue status, content_path, and content file presence before rerunning 'npm run validate:term-queue'.");
    process.exit(1);
  }

  console.log(`term-queue validation passed (${report.queue.items.length} items checked)`);
}

main().catch((error) => {
  console.error(`validate:term-queue failed: ${error.message}`);
  process.exit(1);
});
