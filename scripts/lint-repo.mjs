import { readFile, readdir } from 'node:fs/promises';
import path from 'node:path';
import { fileExists, readMarkdownRecord, rootDir } from './lib/term-pipeline.mjs';

const repoDocsDir = path.join(rootDir, 'project-docs');
const agentsPath = path.join(rootDir, 'AGENTS.md');
const skillsDir = path.join(rootDir, '.agents', 'skills');
const termsDir = path.join(rootDir, 'src', 'content', 'terms');
const topicsDir = path.join(rootDir, 'src', 'content', 'topics');
const publicDir = path.join(rootDir, 'public');
const markdownLinkPattern = /\[[^\]]+\]\(([^)\s]+(?:#[^)]+)?)\)/g;
const htmlHrefPattern = /href=["']([^"']+)["']/g;
const codeFencePattern = /```[\s\S]*?```/g;
const inlineCodePattern = /`[^`]*`/g;

function toRelativePath(targetPath) {
  return path.relative(rootDir, targetPath).split(path.sep).join('/');
}

function addIssue(issues, message) {
  issues.push(message);
}

function stripCode(text) {
  return text.replace(codeFencePattern, '').replace(inlineCodePattern, '');
}

function extractLinks(text) {
  const cleanText = stripCode(text);
  const links = [];

  for (const pattern of [markdownLinkPattern, htmlHrefPattern]) {
    pattern.lastIndex = 0;
    let match;

    while ((match = pattern.exec(cleanText)) !== null) {
      links.push(match[1]);
    }
  }

  return [...new Set(links)];
}

function normalizeTarget(target) {
  return target.trim().replace(/^<|>$/g, '');
}

function stripHashAndQuery(target) {
  return target.split('#')[0].split('?')[0];
}

async function walkMarkdownFiles(directory) {
  const entries = await readdir(directory, { withFileTypes: true });
  const files = [];

  for (const entry of entries) {
    const absolutePath = path.join(directory, entry.name);

    if (entry.isDirectory()) {
      files.push(...(await walkMarkdownFiles(absolutePath)));
      continue;
    }

    if (entry.isFile() && entry.name.endsWith('.md')) {
      files.push(absolutePath);
    }
  }

  return files;
}

async function loadPublishedSlugs(directory, issues) {
  const files = await walkMarkdownFiles(directory);
  const publishedSlugs = new Set();

  for (const filePath of files) {
    let record;

    try {
      record = await readMarkdownRecord(filePath);
    } catch (error) {
      addIssue(
        issues,
        `${toRelativePath(filePath)}: unable to parse frontmatter for lint (${error.message}).`
      );
      continue;
    }

    if (record.data.status === 'published' && typeof record.data.slug === 'string') {
      publishedSlugs.add(record.data.slug);
    }
  }

  return publishedSlugs;
}

async function validateDocsLinks(filePath, issues, { publishedTermSlugs, publishedTopicSlugs }) {
  const relativePath = toRelativePath(filePath);
  const raw = await readFile(filePath, 'utf8');

  for (const originalTarget of extractLinks(raw)) {
    const target = normalizeTarget(originalTarget);
    const targetPath = stripHashAndQuery(target);

    if (target === '' || target.startsWith('#')) {
      continue;
    }

    if (
      target.startsWith('http://') ||
      target.startsWith('https://') ||
      target.startsWith('mailto:') ||
      target.startsWith('tel:')
    ) {
      continue;
    }

    if (target.startsWith('/')) {
      if (targetPath === '/' || targetPath === '/terms/' || targetPath === '/topics/') {
        continue;
      }

      if (targetPath.startsWith('/terms/')) {
        const slug = targetPath.replace(/^\/terms\//, '').replace(/\/$/, '');

        if (!publishedTermSlugs.has(slug)) {
          addIssue(
            issues,
            `${relativePath}: broken site link "${target}" points to a missing or unpublished term page.`
          );
        }

        continue;
      }

      if (targetPath.startsWith('/topics/')) {
        const slug = targetPath.replace(/^\/topics\//, '').replace(/\/$/, '');

        if (slug !== '' && !publishedTopicSlugs.has(slug)) {
          addIssue(
            issues,
            `${relativePath}: broken site link "${target}" points to a missing or unpublished topic page.`
          );
        }

        continue;
      }

      const publicTarget = path.join(publicDir, targetPath.slice(1));

      if (!(await fileExists(publicTarget))) {
        addIssue(issues, `${relativePath}: broken public asset link "${target}".`);
      }

      continue;
    }

    const resolvedTarget = path.resolve(path.dirname(filePath), targetPath);

    if (!(await fileExists(resolvedTarget))) {
      addIssue(
        issues,
        `${relativePath}: broken relative link "${target}" -> "${toRelativePath(resolvedTarget)}".`
      );
    }
  }
}

async function validateContentBodyLinks(filePath, issues, { publishedTermSlugs, publishedTopicSlugs }) {
  let record;

  try {
    record = await readMarkdownRecord(filePath);
  } catch (error) {
    addIssue(
      issues,
      `${toRelativePath(filePath)}: unable to parse frontmatter for lint (${error.message}).`
    );
    return;
  }

  for (const originalTarget of extractLinks(record.body)) {
    const target = normalizeTarget(originalTarget);
    const targetPath = stripHashAndQuery(target);

    if (target === '' || target.startsWith('#')) {
      continue;
    }

    if (
      target.startsWith('http://') ||
      target.startsWith('https://') ||
      target.startsWith('mailto:') ||
      target.startsWith('tel:')
    ) {
      continue;
    }

    if (target.startsWith('/terms/')) {
      const slug = targetPath.replace(/^\/terms\//, '').replace(/\/$/, '');

      if (!publishedTermSlugs.has(slug)) {
        addIssue(
          issues,
          `${record.relativePath}: body link "${target}" points to a missing or unpublished term page.`
        );
      }

      continue;
    }

    if (target.startsWith('/topics/')) {
      const slug = targetPath.replace(/^\/topics\//, '').replace(/\/$/, '');

      if (slug !== '' && !publishedTopicSlugs.has(slug)) {
        addIssue(
          issues,
          `${record.relativePath}: body link "${target}" points to a missing or unpublished topic page.`
        );
      }

      continue;
    }

    if (target.startsWith('/')) {
      const publicTarget = path.join(publicDir, targetPath.slice(1));

      if (!(await fileExists(publicTarget))) {
        addIssue(issues, `${record.relativePath}: body link "${target}" points to a missing public asset.`);
      }

      continue;
    }

    const resolvedTarget = path.resolve(path.dirname(filePath), targetPath);

    if (!(await fileExists(resolvedTarget))) {
      addIssue(
        issues,
        `${record.relativePath}: body link "${target}" resolves to missing path "${toRelativePath(resolvedTarget)}".`
      );
    }
  }
}

async function main() {
  const issues = [];
  const docsFiles = [
    path.join(rootDir, 'README.md'),
    agentsPath,
    ...(await walkMarkdownFiles(repoDocsDir)),
    ...(await walkMarkdownFiles(skillsDir))
  ];
  const contentFiles = [
    ...(await walkMarkdownFiles(termsDir)),
    ...(await walkMarkdownFiles(topicsDir))
  ];
  const publishedTermSlugs = await loadPublishedSlugs(termsDir, issues);
  const publishedTopicSlugs = await loadPublishedSlugs(topicsDir, issues);

  for (const filePath of docsFiles) {
    await validateDocsLinks(filePath, issues, { publishedTermSlugs, publishedTopicSlugs });
  }

  for (const filePath of contentFiles) {
    await validateContentBodyLinks(filePath, issues, { publishedTermSlugs, publishedTopicSlugs });
  }

  if (issues.length > 0) {
    console.error('lint failed:');
    for (const issue of issues) {
      console.error(`- ${issue}`);
    }
    console.error('Next step: fix the broken doc or content links listed above before running build or deploy.');
    process.exit(1);
  }

  console.log(
    `lint passed (${docsFiles.length} docs file(s), ${contentFiles.length} content file(s) checked)`
  );
}

main().catch((error) => {
  console.error(`lint failed: ${error.message}`);
  process.exit(1);
});
