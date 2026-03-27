import {
  parseCliArgs,
  printIssues,
  printWarnings,
  validateGeneratedIndexSnapshot,
  validateWorkspace
} from './lib/term-pipeline.mjs';

async function main() {
  const args = parseCliArgs();
  const strict = Boolean(args.strict);
  const report = await validateWorkspace({ includeEditorialWarnings: true });

  if (report.errors.length > 0) {
    printIssues('content validation failed:', report.errors);
    if (report.warnings.length > 0) {
      printWarnings('warnings:', report.warnings);
    }
    process.exit(1);
  }

  const generatedIndexReport = await validateGeneratedIndexSnapshot(report.queue, report.contentBySlug);

  if (generatedIndexReport.errors.length > 0) {
    printIssues('content validation failed:', generatedIndexReport.errors);
    if (report.warnings.length > 0) {
      printWarnings('warnings:', report.warnings);
    }
    process.exit(1);
  }

  if (report.warnings.length > 0) {
    printWarnings('content validation warnings:', report.warnings);

    if (strict) {
      console.error('validate:content failed because --strict treats warnings as errors.');
      process.exit(1);
    }
  }

  console.log(
    `content validation passed (${report.queue.items.length} queue item(s), ${report.records.length} content file(s) checked)${
      report.warnings.length > 0 ? ` with ${report.warnings.length} warning(s)` : ''
    }`
  );
}

main().catch((error) => {
  console.error(`validate:content failed: ${error.message}`);
  process.exit(1);
});
