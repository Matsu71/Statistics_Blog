import { parseCliArgs, pickNextTerm, printIssues, validateWorkspace } from './lib/term-pipeline.mjs';

async function main() {
  const args = parseCliArgs();
  const report = await validateWorkspace({ includeEditorialWarnings: false });

  if (report.errors.length > 0) {
    printIssues('pick:next-term failed because queue/content validation found errors:', report.errors);
    console.error("Next step: run 'npm run validate:content' and fix the reported items first.");
    process.exit(1);
  }

  const selection = pickNextTerm(report.queue, report.contentBySlug);

  if (!selection.item) {
    const blockedExample = selection.blocked[0];
    const blockedCount = selection.blocked.length;
    console.error(
      blockedExample
        ? `No eligible unstarted term found. ${blockedCount} item(s) are blocked by prerequisites. Example: ${blockedExample.slug} -> ${blockedExample.reasons.join(', ')}.`
        : 'No eligible unstarted term found.'
    );
    process.exit(2);
  }

  if (args.json) {
    console.log(
      JSON.stringify(
        {
          slug: selection.item.slug,
          title: selection.item.title,
          category: selection.item.category,
          level: selection.item.level,
          priority: selection.item.priority,
          prerequisites: selection.item.prerequisites
        },
        null,
        2
      )
    );
    return;
  }

  console.log(`next slug: ${selection.item.slug}`);
  console.log(`title: ${selection.item.title}`);
  console.log(`category: ${selection.item.category}`);
  console.log(`level: ${selection.item.level}`);
  console.log(`priority: ${selection.item.priority}`);
  console.log(
    `prerequisites: ${
      selection.item.prerequisites.length > 0 ? selection.item.prerequisites.join(', ') : 'none'
    }`
  );
  console.log(`command: npm run scaffold:term -- --slug=${selection.item.slug}`);
}

main().catch((error) => {
  console.error(`pick:next-term failed: ${error.message}`);
  process.exit(1);
});
