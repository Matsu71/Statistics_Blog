import { access, readFile, readdir } from 'node:fs/promises';
import path from 'node:path';
import { defaultBuildDir, resolveNormalizedBasePath } from '../site-build.config.mjs';

const rootDir = process.cwd();
const buildDir = path.join(rootDir, defaultBuildDir);
const generatedTermIndexPath = path.join(rootDir, 'src', 'generated', 'term-index.json');
const ignoredSchemes = /^(https?:|mailto:|tel:|javascript:|data:)/i;
const publicBasePath = resolveNormalizedBasePath();

async function fileExists(targetPath) {
  try {
    await access(targetPath);
    return true;
  } catch {
    return false;
  }
}

async function walkHtmlFiles(directory) {
  const entries = await readdir(directory, { withFileTypes: true });
  const results = [];

  for (const entry of entries) {
    const absolutePath = path.join(directory, entry.name);

    if (entry.isDirectory()) {
      results.push(...(await walkHtmlFiles(absolutePath)));
      continue;
    }

    if (entry.isFile() && entry.name.endsWith('.html')) {
      results.push(absolutePath);
    }
  }

  return results;
}

function toBuildRelativePath(targetPath) {
  return path.relative(buildDir, targetPath).split(path.sep).join('/');
}

function extractTargetsByAttribute(content, attributeName) {
  const targets = [];
  const pattern = new RegExp(`\\s${attributeName}=(["'])(.*?)\\1`, 'g');

  for (const match of content.matchAll(pattern)) {
    targets.push(match[2]);
  }

  return targets;
}

function extractAssetTargets(content) {
  const targets = [
    ...extractTargetsByAttribute(content, 'href'),
    ...extractTargetsByAttribute(content, 'src')
  ];

  for (const srcset of extractTargetsByAttribute(content, 'srcset')) {
    for (const candidate of srcset.split(',')) {
      const [target] = candidate.trim().split(/\s+/, 1);

      if (target) {
        targets.push(target);
      }
    }
  }

  return targets;
}

function stripQueryAndHash(target) {
  return target.split('#')[0].split('?')[0];
}

function getCandidatePaths(relativeTarget) {
  const normalized = relativeTarget.replace(/^\/+/, '').replace(/\/+$/, '');

  if (normalized === '') {
    return ['index.html'];
  }

  if (path.posix.extname(normalized) !== '') {
    return [normalized];
  }

  return [normalized, `${normalized}.html`, path.posix.join(normalized, 'index.html')];
}

async function targetExists(relativeTarget) {
  const candidates = getCandidatePaths(relativeTarget);

  for (const candidate of candidates) {
    if (await fileExists(path.join(buildDir, candidate))) {
      return true;
    }
  }

  return false;
}

async function absoluteTargetExists(cleanTarget) {
  const normalized = cleanTarget.replace(/^\/+/, '');

  if (await targetExists(normalized)) {
    return true;
  }

  if (publicBasePath !== '' && normalized.startsWith(`${publicBasePath}/`)) {
    return targetExists(normalized.slice(publicBasePath.length + 1));
  }
  return false;
}

async function relativeTargetExists(cleanTarget, sourceRelativePath) {
  const sourceDirectory = path.posix.dirname(sourceRelativePath);
  const normalized = path.posix.normalize(path.posix.join(sourceDirectory, cleanTarget));
  return targetExists(normalized);
}

function getEffectiveBasePath() {
  if (publicBasePath !== '') {
    return `/${publicBasePath}`;
  }

  return '';
}

function withBasePath(sitePath) {
  const basePath = getEffectiveBasePath();
  return basePath === '' ? sitePath : `${basePath}${sitePath}`;
}

async function validateTermsIndexCoverage(errors) {
  if (!(await fileExists(generatedTermIndexPath))) {
    errors.push('src/generated/term-index.json is missing. Run npm run generate:index before validating built links.');
    return;
  }

  const termsIndexPath = path.join(buildDir, 'terms', 'index.html');

  if (!(await fileExists(termsIndexPath))) {
    errors.push(`${defaultBuildDir}/terms/index.html is missing. Run npm run build before validating built links.`);
    return;
  }

  const termIndex = JSON.parse(await readFile(generatedTermIndexPath, 'utf8'));
  const termsIndexHtml = await readFile(termsIndexPath, 'utf8');

  for (const term of termIndex.publishedTerms ?? []) {
    const expectedHref = withBasePath(term.href);

    if (!termsIndexHtml.includes(`href="${expectedHref}"`) && !termsIndexHtml.includes(`href='${expectedHref}'`)) {
      errors.push(
        `${defaultBuildDir}/terms/index.html: published term "${term.slug}" is missing from the built terms index (${expectedHref}).`
      );
    }
  }
}

async function main() {
  if (!(await fileExists(buildDir))) {
    console.error(`validate:links failed: ${defaultBuildDir}/ does not exist. Run npm run build first.`);
    process.exit(1);
  }

  const htmlFiles = await walkHtmlFiles(buildDir);
  const errors = [];

  for (const filePath of htmlFiles) {
    const content = await readFile(filePath, 'utf8');
    const sourceRelativePath = toBuildRelativePath(filePath);

    for (const target of extractAssetTargets(content)) {
      if (target === '' || target.startsWith('#') || ignoredSchemes.test(target)) {
        continue;
      }

      const cleanTarget = stripQueryAndHash(target);

      if (cleanTarget === '') {
        continue;
      }

      const exists = cleanTarget.startsWith('/')
        ? await absoluteTargetExists(cleanTarget)
        : await relativeTargetExists(cleanTarget, sourceRelativePath);

      if (!exists) {
        errors.push(`${defaultBuildDir}/${sourceRelativePath}: broken internal asset or link target "${target}"`);
      }
    }
  }

  await validateTermsIndexCoverage(errors);

  if (errors.length > 0) {
    console.error('validate:links failed:');
    for (const error of errors) {
      console.error(`- ${error}`);
    }
    console.error(`Look at: ${defaultBuildDir}/**/*.html, src/pages/**, src/content/**, and src/generated/term-index.json.`);
    console.error('Next step: inspect the reported built page and fix the missing route or link source before deploying.');
    process.exit(1);
  }

  console.log(`validate:links passed (${htmlFiles.length} HTML file(s) checked)`);
}

main().catch((error) => {
  console.error(`validate:links failed: ${error.message}`);
  process.exit(1);
});
