import { access, mkdir, readFile, readdir, rename, writeFile } from 'node:fs/promises';
import path from 'node:path';
import { parse as parseYaml, stringify as stringifyYaml } from 'yaml';

export const rootDir = process.cwd();
export const queuePath = path.join(rootDir, 'data', 'term-queue.json');
export const contentDir = path.join(rootDir, 'src', 'content', 'terms');
export const generatedDir = path.join(rootDir, 'src', 'generated');
export const generatedTermIndexPath = path.join(generatedDir, 'term-index.json');

const frontmatterPattern = /^---\s*\n([\s\S]*?)\n---\s*(?:\n([\s\S]*))?$/;
const slugPattern = /^[a-z0-9-]+$/;
const queueStatusValues = ['unstarted', 'draft', 'published'];
const contentStatusValues = ['draft', 'published'];
const levelValues = ['foundation', 'standard', 'advanced'];
const categoryValues = [
  'descriptive_statistics',
  'probability',
  'probability_distribution',
  'sampling_distribution',
  'estimation',
  'hypothesis_testing',
  'correlation_regression',
  'data_handling'
];
const examScopeValues = ['statistics_grade_2'];
const referenceTypeValues = ['official', 'textbook', 'web'];
const knownTermFrontmatterKeys = new Set([
  'title',
  'slug',
  'exam_scope',
  'level',
  'status',
  'category',
  'short_definition',
  'definition',
  'intuition',
  'visual_explanation',
  'where_it_appears',
  'practical_examples',
  'exam_points',
  'formulas',
  'rigorous_explanation',
  'proof',
  'common_mistakes',
  'references',
  'aliases',
  'tags',
  'related_terms',
  'sort_order',
  'updated_at'
]);
const legacyTermFrontmatterKeys = {
  description: 'short_definition',
  examLevel: 'exam_scope',
  relatedTerms: 'related_terms',
  sortOrder: 'sort_order',
  updatedAt: 'updated_at',
  draft: 'status'
};
const requiredQueueKeys = [
  'slug',
  'title',
  'category',
  'priority',
  'status',
  'level',
  'exam_scope',
  'prerequisites',
  'related_terms'
];
const discouragedTextRules = [
  { token: '超重要', message: 'Avoid exaggerated phrasing like "超重要".' },
  { token: 'めちゃくちゃ簡単', message: 'Avoid casual phrasing like "めちゃくちゃ簡単".' },
  { token: 'とにかく覚えましょう', message: 'Avoid telling readers to memorize without explanation.' },
  { token: 'P値', message: 'Use "p値" instead of "P値".' }
];
const collator = new Intl.Collator('ja');

function addIssue(issues, message, severity = 'error') {
  issues.push({ severity, message });
}

function isPlainObject(value) {
  return Boolean(value) && typeof value === 'object' && !Array.isArray(value);
}

function isNonEmptyString(value) {
  return typeof value === 'string' && value.trim().length > 0;
}

function normalizeDate(value) {
  if (value instanceof Date && !Number.isNaN(value.getTime())) {
    return value.toISOString().slice(0, 10);
  }

  if (isNonEmptyString(value)) {
    return value.trim();
  }

  return '';
}

function getLocalIsoDate(date = new Date()) {
  const year = String(date.getFullYear());
  const month = String(date.getMonth() + 1).padStart(2, '0');
  const day = String(date.getDate()).padStart(2, '0');
  return `${year}-${month}-${day}`;
}

function isIsoDate(value) {
  if (!isNonEmptyString(value)) {
    return false;
  }

  const date = new Date(value);
  return !Number.isNaN(date.getTime()) && date.toISOString().startsWith(value.trim());
}

function toRelativePath(targetPath) {
  return path.relative(rootDir, targetPath).split(path.sep).join('/');
}

function expectedContentPath(slug) {
  return `src/content/terms/${slug}.md`;
}

function formatValue(value) {
  if (Array.isArray(value)) {
    return value.join(', ');
  }

  return String(value);
}

function sortedCopy(values) {
  return [...values].sort((a, b) => collator.compare(a, b));
}

function uniqueStrings(values = []) {
  return [...new Set(values)];
}

function arraysEqualAsSets(left = [], right = []) {
  const leftSorted = sortedCopy(uniqueStrings(left));
  const rightSorted = sortedCopy(uniqueStrings(right));

  return leftSorted.length === rightSorted.length && leftSorted.every((value, index) => value === rightSorted[index]);
}

function checkStringArray(value, fieldPath, issues, { minLength = 0, allowUndefined = false } = {}) {
  if (value === undefined && allowUndefined) {
    return;
  }

  if (!Array.isArray(value)) {
    addIssue(issues, `${fieldPath} must be an array of strings.`);
    return;
  }

  if (value.length < minLength) {
    addIssue(issues, `${fieldPath} must contain at least ${minLength} item(s).`);
  }

  value.forEach((item, index) => {
    if (!isNonEmptyString(item)) {
      addIssue(issues, `${fieldPath}[${index}] must be a non-empty string.`);
    }
  });
}

function checkDuplicateStrings(values, fieldPath, issues) {
  if (!Array.isArray(values)) {
    return;
  }

  const seen = new Set();

  for (const value of values) {
    if (!isNonEmptyString(value)) {
      continue;
    }

    if (seen.has(value)) {
      addIssue(issues, `${fieldPath} contains a duplicate entry: "${value}".`);
      return;
    }

    seen.add(value);
  }
}

function extractTextChunks(value, chunks = []) {
  if (typeof value === 'string') {
    chunks.push(value);
    return chunks;
  }

  if (Array.isArray(value)) {
    value.forEach((item) => extractTextChunks(item, chunks));
    return chunks;
  }

  if (isPlainObject(value)) {
    Object.values(value).forEach((item) => extractTextChunks(item, chunks));
  }

  return chunks;
}

function detectTodoMarkers(record) {
  const haystack = extractTextChunks(record.data, [record.body]).join('\n');
  return /\bTODO:|\b保留:|このページは雛形です|前提用語とのつながりを確認する/.test(haystack);
}

function detectEditorialWarnings(record) {
  const warnings = [];
  const haystack = extractTextChunks(record.data, [record.body]).join('\n');

  for (const rule of discouragedTextRules) {
    if (haystack.includes(rule.token)) {
      warnings.push(`${record.relativePath}: editorial warning: ${rule.message}`);
    }
  }

  if (
    haystack.includes('標本分散') &&
    haystack.includes('不偏分散') &&
    !haystack.includes('区別') &&
    !haystack.includes('違い')
  ) {
    warnings.push(
      `${record.relativePath}: editorial warning: possible ambiguity between 標本分散 and 不偏分散.`
    );
  }

  return warnings;
}

export function parseCliArgs(argv = process.argv.slice(2)) {
  const args = { _: [] };

  for (const arg of argv) {
    if (!arg.startsWith('--')) {
      args._.push(arg);
      continue;
    }

    const trimmed = arg.slice(2);
    const equalsIndex = trimmed.indexOf('=');

    if (equalsIndex === -1) {
      args[trimmed] = true;
      continue;
    }

    const key = trimmed.slice(0, equalsIndex);
    const value = trimmed.slice(equalsIndex + 1);
    args[key] = value;
  }

  return args;
}

export async function fileExists(targetPath) {
  try {
    await access(targetPath);
    return true;
  } catch {
    return false;
  }
}

export async function readQueue() {
  const raw = await readFile(queuePath, 'utf8');
  return JSON.parse(raw);
}

export async function writeJsonAtomic(targetPath, value) {
  await mkdir(path.dirname(targetPath), { recursive: true });
  const tempPath = `${targetPath}.tmp-${process.pid}-${Date.now()}`;
  await writeFile(tempPath, `${JSON.stringify(value, null, 2)}\n`, 'utf8');
  await rename(tempPath, targetPath);
}

export async function writeTextAtomic(targetPath, value) {
  await mkdir(path.dirname(targetPath), { recursive: true });
  const tempPath = `${targetPath}.tmp-${process.pid}-${Date.now()}`;
  await writeFile(tempPath, value, 'utf8');
  await rename(tempPath, targetPath);
}

export function buildMarkdownDocument(frontmatter, body) {
  const frontmatterYaml = stringifyYaml(frontmatter, {
    lineWidth: 0,
    minContentWidth: 0
  }).trimEnd();

  const normalizedBody = body.trim();
  return `---\n${frontmatterYaml}\n---\n\n${normalizedBody}\n`;
}

async function walkMarkdownFiles(directory) {
  const entries = await readdir(directory, { withFileTypes: true });
  const results = [];

  for (const entry of entries) {
    const absolutePath = path.join(directory, entry.name);

    if (entry.isDirectory()) {
      results.push(...(await walkMarkdownFiles(absolutePath)));
      continue;
    }

    if (entry.isFile() && entry.name.endsWith('.md')) {
      results.push(absolutePath);
    }
  }

  return results;
}

export async function readMarkdownRecord(filePath) {
  const raw = await readFile(filePath, 'utf8');
  const match = raw.match(frontmatterPattern);

  if (!match) {
    throw new Error('missing frontmatter block');
  }

  let data;

  try {
    data = parseYaml(match[1]) ?? {};
  } catch (error) {
    throw new Error(`invalid YAML frontmatter (${error.message})`);
  }

  if (!isPlainObject(data)) {
    throw new Error('frontmatter must parse to an object');
  }

  return {
    absolutePath: filePath,
    relativePath: toRelativePath(filePath),
    raw,
    frontmatterRaw: match[1],
    body: match[2] ?? '',
    data
  };
}

export async function loadMarkdownRecords() {
  const files = await walkMarkdownFiles(contentDir);
  const records = [];
  const issues = [];

  for (const filePath of files) {
    try {
      records.push(await readMarkdownRecord(filePath));
    } catch (error) {
      addIssue(issues, `${toRelativePath(filePath)}: ${error.message}`);
    }
  }

  return { records, issues };
}

function validateQueueStructure(queue) {
  const errors = [];
  const warnings = [];
  const itemBySlug = new Map();

  if (!isPlainObject(queue)) {
    addIssue(errors, `${toRelativePath(queuePath)} must contain an object.`);
    return { errors, warnings, itemBySlug };
  }

  if (!Array.isArray(queue.items)) {
    addIssue(errors, `${toRelativePath(queuePath)} is missing an "items" array.`);
    return { errors, warnings, itemBySlug };
  }

  queue.items.forEach((item, index) => {
    const label = `queue.items[${index}]`;

    if (!isPlainObject(item)) {
      addIssue(errors, `${label} must be an object.`);
      return;
    }

    for (const key of requiredQueueKeys) {
      if (!(key in item)) {
        addIssue(errors, `Missing required queue field "${key}" for item at index ${index}.`);
      }
    }

    if (!isNonEmptyString(item.slug)) {
      addIssue(errors, `${label}.slug must be a non-empty string.`);
      return;
    }

    if (!slugPattern.test(item.slug)) {
      addIssue(errors, `Invalid queue slug "${item.slug}". Slugs must match ${slugPattern}.`);
    }

    if (itemBySlug.has(item.slug)) {
      addIssue(errors, `Duplicate queue slug: "${item.slug}".`);
    } else {
      itemBySlug.set(item.slug, item);
    }

    if (!isNonEmptyString(item.title)) {
      addIssue(errors, `Missing required queue field "title" for slug "${item.slug}".`);
    }

    if (!queueStatusValues.includes(item.status)) {
      addIssue(
        errors,
        `Invalid queue status for "${item.slug}": expected one of [${queueStatusValues.join(
          ', '
        )}], got "${formatValue(item.status)}".`
      );
    }

    if (!levelValues.includes(item.level)) {
      addIssue(
        errors,
        `Invalid queue level for "${item.slug}": expected one of [${levelValues.join(
          ', '
        )}], got "${formatValue(item.level)}".`
      );
    }

    if (!categoryValues.includes(item.category)) {
      addIssue(
        errors,
        `Invalid queue category for "${item.slug}": expected one of [${categoryValues.join(
          ', '
        )}], got "${formatValue(item.category)}".`
      );
    }

    if (![1, 2, 3, 4].includes(item.priority)) {
      addIssue(errors, `Invalid queue priority for "${item.slug}": expected one of [1, 2, 3, 4], got "${formatValue(item.priority)}".`);
    }

    checkStringArray(item.exam_scope, `queue item "${item.slug}".exam_scope`, errors, { minLength: 1 });
    checkStringArray(item.prerequisites, `queue item "${item.slug}".prerequisites`, errors);
    checkStringArray(item.related_terms, `queue item "${item.slug}".related_terms`, errors);
    checkDuplicateStrings(item.prerequisites, `queue item "${item.slug}".prerequisites`, errors);
    checkDuplicateStrings(item.related_terms, `queue item "${item.slug}".related_terms`, errors);

    if (Array.isArray(item.exam_scope)) {
      for (const scope of item.exam_scope) {
        if (isNonEmptyString(scope) && !examScopeValues.includes(scope)) {
          addIssue(
            errors,
            `Invalid exam_scope for "${item.slug}": expected one of [${examScopeValues.join(
              ', '
            )}], got "${scope}".`
          );
        }
      }
    }

    const shouldHaveContentPath = item.status === 'draft' || item.status === 'published';

    if (shouldHaveContentPath) {
      if (!isNonEmptyString(item.content_path)) {
        addIssue(errors, `${item.status} queue item "${item.slug}" is missing content_path.`);
      } else if (item.content_path !== expectedContentPath(item.slug)) {
        addIssue(
          errors,
          `Queue/content path mismatch for "${item.slug}": expected "${expectedContentPath(
            item.slug
          )}", got "${item.content_path}".`
        );
      }
    } else if (item.content_path && item.content_path !== expectedContentPath(item.slug)) {
      addIssue(
        warnings,
        `Unstarted queue item "${item.slug}" has an unexpected content_path "${item.content_path}".`
      );
    }
  });

  for (const item of queue.items) {
    if (!isPlainObject(item) || !isNonEmptyString(item.slug)) {
      continue;
    }

    for (const prerequisite of item.prerequisites ?? []) {
      if (!itemBySlug.has(prerequisite)) {
        addIssue(errors, `Unknown prerequisite for "${item.slug}": "${prerequisite}".`);
      }
    }

    for (const relatedTerm of item.related_terms ?? []) {
      if (!itemBySlug.has(relatedTerm)) {
        addIssue(errors, `Unknown related_terms slug for "${item.slug}": "${relatedTerm}".`);
      }
    }
  }

  const visiting = new Set();
  const visited = new Set();

  function dfs(slug, trail = []) {
    if (visited.has(slug) || !itemBySlug.has(slug)) {
      return;
    }

    if (visiting.has(slug)) {
      addIssue(errors, `Prerequisite cycle detected: ${[...trail, slug].join(' -> ')}.`);
      return;
    }

    visiting.add(slug);
    const item = itemBySlug.get(slug);
    for (const prerequisite of item.prerequisites ?? []) {
      dfs(prerequisite, [...trail, slug]);
    }
    visiting.delete(slug);
    visited.add(slug);
  }

  for (const slug of itemBySlug.keys()) {
    dfs(slug);
  }

  return { errors, warnings, itemBySlug };
}

function validateReference(reference, fieldPath, errors) {
  if (!isPlainObject(reference)) {
    addIssue(errors, `${fieldPath} must be an object.`);
    return;
  }

  if (!isNonEmptyString(reference.title)) {
    addIssue(errors, `${fieldPath}.title is required.`);
  }

  if (!referenceTypeValues.includes(reference.type)) {
    addIssue(
      errors,
      `${fieldPath}.type must be one of [${referenceTypeValues.join(', ')}].`
    );
  }

  if ('author' in reference && !isNonEmptyString(reference.author)) {
    addIssue(errors, `${fieldPath}.author must be a non-empty string when present.`);
  }

  if ('year' in reference && !(Number.isInteger(reference.year) && reference.year > 0)) {
    addIssue(errors, `${fieldPath}.year must be a positive integer when present.`);
  }

  if ('url' in reference) {
    if (!isNonEmptyString(reference.url)) {
      addIssue(errors, `${fieldPath}.url must be a non-empty string when present.`);
    } else {
      try {
        new URL(reference.url);
      } catch {
        addIssue(errors, `${fieldPath}.url must be a valid URL.`);
      }
    }
  }

  if ('note' in reference && !isNonEmptyString(reference.note)) {
    addIssue(errors, `${fieldPath}.note must be a non-empty string when present.`);
  }
}

function validateMarkdownRecord(record, queueItemBySlug, issues, warnings) {
  const { data } = record;
  const termFrontmatterKeys = Object.keys(data);

  for (const key of termFrontmatterKeys) {
    if (knownTermFrontmatterKeys.has(key)) {
      continue;
    }

    if (key in legacyTermFrontmatterKeys) {
      addIssue(
        issues,
        `${record.relativePath}: legacy frontmatter field "${key}" is not allowed. Use "${legacyTermFrontmatterKeys[key]}" instead.`
      );
      continue;
    }

    addIssue(
      issues,
      `${record.relativePath}: unknown frontmatter field "${key}". Remove it or add support in src/content.config.ts.`
    );
  }

  if (!isNonEmptyString(data.slug)) {
    addIssue(issues, `${record.relativePath}: missing required field "slug".`);
    return;
  }

  if (!slugPattern.test(data.slug)) {
    addIssue(issues, `${record.relativePath}: invalid slug "${data.slug}".`);
  }

  const expectedFilename = `${data.slug}.md`;

  if (path.basename(record.absolutePath) !== expectedFilename) {
    addIssue(
      issues,
      `${record.relativePath}: slug mismatch. Expected filename "${expectedFilename}", got "${path.basename(
        record.absolutePath
      )}".`
    );
  }

  const queueItem = queueItemBySlug.get(data.slug);

  if (!queueItem) {
    addIssue(issues, `Queue entry missing for content file ${record.relativePath} (slug: "${data.slug}").`);
    return;
  }

  if (!isNonEmptyString(data.title)) {
    addIssue(issues, `${record.relativePath}: missing required field "title".`);
  } else if (data.title !== queueItem.title) {
    addIssue(
      issues,
      `${record.relativePath}: title mismatch for "${data.slug}". queue="${queueItem.title}", content="${data.title}".`
    );
  }

  if (!Array.isArray(data.exam_scope) || data.exam_scope.length === 0) {
    addIssue(issues, `${record.relativePath}: exam_scope must contain at least one entry.`);
  } else {
    for (const scope of data.exam_scope) {
      if (!examScopeValues.includes(scope)) {
        addIssue(
          issues,
          `${record.relativePath}: invalid exam_scope "${scope}". Expected one of [${examScopeValues.join(
            ', '
          )}].`
        );
      }
    }
  }

  if (!levelValues.includes(data.level)) {
    addIssue(issues, `${record.relativePath}: invalid level "${formatValue(data.level)}".`);
  } else if (data.level !== queueItem.level) {
    addIssue(
      issues,
      `${record.relativePath}: level mismatch for "${data.slug}". queue="${queueItem.level}", content="${data.level}".`
    );
  }

  if (!contentStatusValues.includes(data.status)) {
    addIssue(
      issues,
      `${record.relativePath}: invalid status "${formatValue(data.status)}". Expected one of [${contentStatusValues.join(
        ', '
      )}].`
    );
  } else if (queueItem.status !== data.status) {
    addIssue(
      issues,
      `${record.relativePath}: status mismatch for "${data.slug}". queue="${queueItem.status}", content="${data.status}".`
    );
  }

  if (!categoryValues.includes(data.category)) {
    addIssue(issues, `${record.relativePath}: invalid category "${formatValue(data.category)}".`);
  } else if (data.category !== queueItem.category) {
    addIssue(
      issues,
      `${record.relativePath}: category mismatch for "${data.slug}". queue="${queueItem.category}", content="${data.category}".`
    );
  }

  if (!isNonEmptyString(data.short_definition)) {
    addIssue(issues, `${record.relativePath}: short_definition is required.`);
  }

  if (!isNonEmptyString(data.definition)) {
    addIssue(issues, `${record.relativePath}: definition is required.`);
  }

  checkStringArray(data.intuition, `${record.relativePath}: intuition`, issues, { minLength: 1 });
  checkStringArray(data.visual_explanation, `${record.relativePath}: visual_explanation`, issues, {
    allowUndefined: true
  });
  checkStringArray(data.where_it_appears, `${record.relativePath}: where_it_appears`, issues, {
    minLength: 1
  });
  checkStringArray(data.exam_points, `${record.relativePath}: exam_points`, issues, { minLength: 1 });
  checkStringArray(data.rigorous_explanation, `${record.relativePath}: rigorous_explanation`, issues, {
    allowUndefined: true
  });
  checkStringArray(data.common_mistakes, `${record.relativePath}: common_mistakes`, issues, {
    allowUndefined: true
  });
  checkStringArray(data.aliases, `${record.relativePath}: aliases`, issues, {
    allowUndefined: true
  });
  checkStringArray(data.tags, `${record.relativePath}: tags`, issues, { allowUndefined: true });

  if (!('related_terms' in data)) {
    addIssue(issues, `${record.relativePath}: related_terms is required.`);
  }

  checkStringArray(data.related_terms, `${record.relativePath}: related_terms`, issues, {
    minLength: 1
  });
  checkDuplicateStrings(data.related_terms, `${record.relativePath}: related_terms`, issues);

  if (Array.isArray(data.related_terms)) {
    for (const relatedTerm of data.related_terms) {
      if (!queueItemBySlug.has(relatedTerm)) {
        addIssue(
          issues,
          `${record.relativePath}: related_terms includes "${relatedTerm}", but that slug is not in the queue.`
        );
      }

      if (relatedTerm === data.slug) {
        addIssue(issues, `${record.relativePath}: self reference is not allowed in related_terms.`);
      }
    }

    if (!arraysEqualAsSets(data.related_terms ?? [], queueItem.related_terms ?? [])) {
      addIssue(
        issues,
        `${record.relativePath}: related_terms mismatch for "${data.slug}". queue="${formatValue(
          queueItem.related_terms ?? []
        )}", content="${formatValue(data.related_terms ?? [])}".`
      );
    }
  }

  if (data.sort_order !== undefined && !Number.isInteger(data.sort_order)) {
    addIssue(issues, `${record.relativePath}: sort_order must be an integer.`);
  }

  const normalizedUpdatedAt = normalizeDate(data.updated_at);

  if (!isIsoDate(normalizedUpdatedAt)) {
    addIssue(
      issues,
      `${record.relativePath}: invalid updated_at "${formatValue(data.updated_at)}". Expected YYYY-MM-DD.`
    );
  } else if (normalizedUpdatedAt > getLocalIsoDate()) {
    addIssue(
      warnings,
      `${record.relativePath}: updated_at "${normalizedUpdatedAt}" is in the future.`,
      'warning'
    );
  }

  if (data.practical_examples !== undefined && !Array.isArray(data.practical_examples)) {
    addIssue(issues, `${record.relativePath}: practical_examples must be an array.`);
  } else if (Array.isArray(data.practical_examples)) {
    data.practical_examples.forEach((example, index) => {
      const fieldPath = `${record.relativePath}: practical_examples[${index}]`;

      if (!isPlainObject(example)) {
        addIssue(issues, `${fieldPath} must be an object.`);
        return;
      }

      if (!isNonEmptyString(example.title)) {
        addIssue(issues, `${fieldPath}.title is required.`);
      }

      if (!isNonEmptyString(example.description)) {
        addIssue(issues, `${fieldPath}.description is required.`);
      }
    });
  }

  if (data.status === 'published' && (!Array.isArray(data.practical_examples) || data.practical_examples.length === 0)) {
    addIssue(issues, `${record.relativePath}: published content must include at least one practical_examples entry.`);
  }

  if (data.formulas !== undefined && !Array.isArray(data.formulas)) {
    addIssue(issues, `${record.relativePath}: formulas must be an array.`);
  } else if (Array.isArray(data.formulas)) {
    data.formulas.forEach((formula, index) => {
      const fieldPath = `${record.relativePath}: formulas[${index}]`;

      if (!isPlainObject(formula)) {
        addIssue(issues, `${fieldPath} must be an object.`);
        return;
      }

      if (!isNonEmptyString(formula.name)) {
        addIssue(issues, `${fieldPath}.name is required.`);
      }

      if (!isNonEmptyString(formula.latex)) {
        addIssue(issues, `${fieldPath}.latex is required.`);
      }

      if (!isNonEmptyString(formula.description)) {
        addIssue(issues, `${fieldPath}.description is required.`);
      }

      checkStringArray(formula.conditions, `${fieldPath}.conditions`, issues, {
        allowUndefined: true
      });
    });
  }

  if ('proof' in data && data.proof !== undefined) {
    if (!isPlainObject(data.proof)) {
      addIssue(issues, `${record.relativePath}: proof must be an object when present.`);
    } else {
      if (!isNonEmptyString(data.proof.summary)) {
        addIssue(issues, `${record.relativePath}: proof.summary is required when proof exists.`);
      }

      if ('outline_steps' in data.proof) {
        checkStringArray(data.proof.outline_steps, `${record.relativePath}: proof.outline_steps`, issues, {
          allowUndefined: true
        });
      }
    }
  }

  if (data.references !== undefined && !Array.isArray(data.references)) {
    addIssue(issues, `${record.relativePath}: references must be an array.`);
  } else if (Array.isArray(data.references)) {
    data.references.forEach((reference, index) => {
      validateReference(reference, `${record.relativePath}: references[${index}]`, issues);
    });
  }

  if (!arraysEqualAsSets(data.exam_scope ?? [], queueItem.exam_scope ?? [])) {
    addIssue(
      issues,
      `${record.relativePath}: exam_scope mismatch for "${data.slug}". queue="${formatValue(
        queueItem.exam_scope
      )}", content="${formatValue(data.exam_scope)}".`
    );
  }

  if (detectTodoMarkers(record) && data.status === 'published') {
    addIssue(issues, `${record.relativePath}: published content must not contain TODO/保留 markers.`);
  }

  for (const warning of detectEditorialWarnings(record)) {
    addIssue(warnings, warning, 'warning');
  }
}

export async function validateWorkspace({ includeEditorialWarnings = true } = {}) {
  const errors = [];
  const warnings = [];

  let queue;

  try {
    queue = await readQueue();
  } catch (error) {
    addIssue(errors, `Queue file is not valid JSON: ${toRelativePath(queuePath)}`);
    return {
      errors,
      warnings,
      queue: null,
      queueItemBySlug: new Map(),
      contentBySlug: new Map(),
      records: []
    };
  }

  const queueValidation = validateQueueStructure(queue);
  errors.push(...queueValidation.errors);
  warnings.push(...queueValidation.warnings);

  const markdownLoad = await loadMarkdownRecords();
  errors.push(...markdownLoad.issues);

  const contentBySlug = new Map();
  const recordsByTitle = new Map();

  for (const record of markdownLoad.records) {
    if (!isNonEmptyString(record.data.slug)) {
      continue;
    }

    if (contentBySlug.has(record.data.slug)) {
      addIssue(
        errors,
        `Duplicate content slug "${record.data.slug}" in ${contentBySlug.get(record.data.slug).relativePath} and ${record.relativePath}.`
      );
      continue;
    }

    contentBySlug.set(record.data.slug, record);

    if (isNonEmptyString(record.data.title)) {
      if (!recordsByTitle.has(record.data.title)) {
        recordsByTitle.set(record.data.title, []);
      }

      recordsByTitle.get(record.data.title).push(record.relativePath);
    }
  }

  for (const item of queue?.items ?? []) {
    if (!isNonEmptyString(item.slug)) {
      continue;
    }

    const hasFile = contentBySlug.has(item.slug);

    if ((item.status === 'published' || item.status === 'draft') && !hasFile) {
      addIssue(
        errors,
        `Content file missing for queue item "${item.slug}": expected ${expectedContentPath(item.slug)}.`
      );
    }

    if (item.status === 'unstarted' && hasFile) {
      addIssue(
        errors,
        `Queue status is "unstarted" but content file already exists: ${expectedContentPath(item.slug)}.`
      );
    }
  }

  for (const record of markdownLoad.records) {
    validateMarkdownRecord(record, queueValidation.itemBySlug, errors, warnings);
  }

  for (const [title, relativePaths] of recordsByTitle.entries()) {
    if (relativePaths.length > 1) {
      addIssue(
        warnings,
        `Duplicate content title "${title}" in ${relativePaths.join(', ')}.`,
        'warning'
      );
    }
  }

  if (!includeEditorialWarnings) {
    return {
      errors,
      warnings: [],
      queue,
      queueItemBySlug: queueValidation.itemBySlug,
      contentBySlug,
      records: markdownLoad.records
    };
  }

  return {
    errors,
    warnings,
    queue,
    queueItemBySlug: queueValidation.itemBySlug,
    contentBySlug,
    records: markdownLoad.records
  };
}

export function printIssues(heading, issues) {
  if (issues.length === 0) {
    return;
  }

  console.error(heading);
  for (const issue of issues) {
    console.error(`- ${issue.message}`);
  }
}

export function printWarnings(heading, warnings) {
  if (warnings.length === 0) {
    return;
  }

  console.warn(heading);
  for (const warning of warnings) {
    console.warn(`- ${warning.message}`);
  }
}

export function pickNextTerm(queue, contentBySlug = new Map()) {
  const queueItemBySlug = new Map(queue.items.map((item) => [item.slug, item]));
  const blocked = [];
  const candidates = queue.items
    .map((item, index) => ({ item, index }))
    .filter(({ item }) => item.status === 'unstarted')
    .sort((left, right) => left.item.priority - right.item.priority || left.index - right.index);

  for (const candidate of candidates) {
    const reasons = [];

    if (contentBySlug.has(candidate.item.slug)) {
      reasons.push('content file already exists');
    }

    for (const prerequisite of candidate.item.prerequisites) {
      const prerequisiteItem = queueItemBySlug.get(prerequisite);

      if (!prerequisiteItem) {
        reasons.push(`unknown prerequisite "${prerequisite}"`);
        continue;
      }

      if (prerequisiteItem.status !== 'published') {
        reasons.push(`${prerequisite} (${prerequisiteItem.status})`);
      }
    }

    if (reasons.length === 0) {
      return { item: candidate.item, blocked };
    }

    blocked.push({ slug: candidate.item.slug, reasons });
  }

  return { item: null, blocked };
}

export function buildScaffold(queue, queueItem) {
  const today = getLocalIsoDate();
  const queueIndex = queue.items.findIndex((item) => item.slug === queueItem.slug);
  const relatedTerms = Array.isArray(queueItem.related_terms) ? queueItem.related_terms : [];
  const prerequisites = Array.isArray(queueItem.prerequisites) ? queueItem.prerequisites : [];
  const frontmatter = {
    title: queueItem.title,
    slug: queueItem.slug,
    exam_scope: Array.isArray(queueItem.exam_scope) && queueItem.exam_scope.length > 0 ? queueItem.exam_scope : ['statistics_grade_2'],
    level: queueItem.level,
    status: 'draft',
    category: queueItem.category,
    short_definition: `TODO: ${queueItem.title} の短い定義を1文で書く。`,
    definition: `TODO: ${queueItem.title} の定義を1文で書く。`,
    intuition: [`TODO: ${queueItem.title} の直感を1文で書く。`],
    visual_explanation: [],
    where_it_appears: [`TODO: ${queueItem.title} が現れる場面を1つ書く。`],
    practical_examples: [],
    exam_points: ['TODO: 試験で重要なポイントを1つ書く。'],
    formulas: [],
    rigorous_explanation: [],
    common_mistakes: [],
    related_terms: relatedTerms,
    references: [],
    updated_at: today,
    aliases: [],
    tags: [],
    sort_order: (queueIndex + 1) * 10
  };

  const notes = [
    'このページは雛形です。公開前に `short_definition`、`definition`、`intuition`、`where_it_appears`、`exam_points` を確定してください。',
    '',
    '- TODO: 前提用語とのつながりを確認する。',
    '- TODO: 必要なら `visual_explanation` を追加する。',
    '- TODO: 必要なら `practical_examples` を追加する。',
    '- TODO: 必要なら `formulas` と記号説明を追加する。',
    '- TODO: `common_mistakes` をその用語固有の内容にする。'
  ];

  if (prerequisites.length > 0) {
    notes.push(`- queue の前提用語: ${prerequisites.map((slug) => `\`${slug}\``).join(', ')}`);
  }

  return {
    frontmatter,
    body: notes.join('\n')
  };
}

export function updateQueueForScaffold(queue, slug) {
  const updatedQueue = JSON.parse(JSON.stringify(queue));
  const item = updatedQueue.items.find((entry) => entry.slug === slug);

  if (!item) {
    throw new Error(`queue item "${slug}" was not found`);
  }

  item.status = 'draft';
  item.content_path = expectedContentPath(slug);
  updatedQueue.updated_at = getLocalIsoDate();

  return updatedQueue;
}

export function buildTermIndex(queue, contentBySlug) {
  const stats = {
    publishedCount: 0,
    draftCount: 0,
    unstartedCount: 0
  };

  const queueSummaryByCategory = Object.fromEntries(
    categoryValues.map((category) => [
      category,
      { published: 0, draft: 0, unstarted: 0 }
    ])
  );

  for (const item of queue.items) {
    if (item.status === 'published') {
      stats.publishedCount += 1;
    } else if (item.status === 'draft') {
      stats.draftCount += 1;
    } else if (item.status === 'unstarted') {
      stats.unstartedCount += 1;
    }

    queueSummaryByCategory[item.category][item.status] += 1;
  }

  const publishedTerms = [...contentBySlug.values()]
    .filter((record) => record.data.status === 'published')
    .sort((left, right) => {
      const leftSortOrder = Number.isInteger(left.data.sort_order) ? left.data.sort_order : 999;
      const rightSortOrder = Number.isInteger(right.data.sort_order) ? right.data.sort_order : 999;

      if (leftSortOrder !== rightSortOrder) {
        return leftSortOrder - rightSortOrder;
      }

      return collator.compare(left.data.title, right.data.title);
    })
    .map((record) => ({
      slug: record.data.slug,
      title: record.data.title,
      shortDefinition: record.data.short_definition,
      category: record.data.category,
      level: record.data.level,
      examScope: record.data.exam_scope,
      aliases: record.data.aliases ?? [],
      tags: record.data.tags ?? [],
      sortOrder: Number.isInteger(record.data.sort_order) ? record.data.sort_order : 999,
      updatedAt: normalizeDate(record.data.updated_at),
      href: `/terms/${record.data.slug}/`,
      searchText: [
        record.data.title,
        record.data.short_definition,
        record.data.category,
        ...(record.data.exam_scope ?? []),
        ...(record.data.aliases ?? []),
        ...(record.data.tags ?? [])
      ].join(' '),
      relatedPublishedSlugs: (record.data.related_terms ?? []).filter((slug) => {
        const relatedRecord = contentBySlug.get(slug);
        return relatedRecord?.data.status === 'published';
      })
    }));

  const nextTermSelection = pickNextTerm(queue, contentBySlug);
  const nextTerm = nextTermSelection.item
    ? {
        slug: nextTermSelection.item.slug,
        title: nextTermSelection.item.title,
        category: nextTermSelection.item.category,
        level: nextTermSelection.item.level,
        priority: nextTermSelection.item.priority,
        prerequisites: nextTermSelection.item.prerequisites,
        relatedTerms: nextTermSelection.item.related_terms
      }
    : null;

  return {
    generatedAt: new Date().toISOString(),
    stats,
    nextTerm,
    publishedTerms,
    featuredTermSlugs: publishedTerms.slice(0, 3).map((term) => term.slug),
    queueSummaryByCategory
  };
}

function normalizeGeneratedIndex(index) {
  if (!isPlainObject(index)) {
    return index;
  }

  const { generatedAt: _generatedAt, ...rest } = index;
  return rest;
}

export async function validateGeneratedIndexSnapshot(queue, contentBySlug) {
  const errors = [];
  const expected = buildTermIndex(queue, contentBySlug);

  if (!(await fileExists(generatedTermIndexPath))) {
    addIssue(
      errors,
      `Generated index is missing: expected ${toRelativePath(generatedTermIndexPath)}. Run 'npm run generate:index'.`
    );
    return { errors, expected, actual: null };
  }

  let actual;

  try {
    actual = JSON.parse(await readFile(generatedTermIndexPath, 'utf8'));
  } catch (error) {
    addIssue(
      errors,
      `Generated index is not valid JSON: ${toRelativePath(generatedTermIndexPath)} (${error.message}). Run 'npm run generate:index'.`
    );
    return { errors, expected, actual: null };
  }

  if (JSON.stringify(normalizeGeneratedIndex(actual)) !== JSON.stringify(normalizeGeneratedIndex(expected))) {
    addIssue(
      errors,
      `Generated index is stale: ${toRelativePath(generatedTermIndexPath)} does not match queue/content. Run 'npm run generate:index'.`
    );
  }

  return { errors, expected, actual };
}
