import { getCollection, type CollectionEntry } from 'astro:content';

export type TermEntry = CollectionEntry<'terms'>;
export type TopicEntry = CollectionEntry<'topics'>;

export const EXAM_SCOPE_LABELS = {
  statistics_grade_2: '統計検定2級'
} as const;

export const CONTENT_LEVEL_LABELS = {
  foundation: '基礎',
  standard: '標準',
  advanced: '発展'
} as const;

export const CONTENT_STATUS_LABELS = {
  draft: '下書き',
  published: '公開済み'
} as const;

export const TERM_CATEGORY_LABELS = {
  descriptive_statistics: '記述統計',
  probability: '確率',
  probability_distribution: '確率分布',
  sampling_distribution: '標本分布',
  estimation: '推定',
  hypothesis_testing: '仮説検定',
  correlation_regression: '相関・回帰',
  data_handling: 'データの扱い'
} as const;

export const TOPIC_TYPE_LABELS = {
  overview: '全体像',
  deep_dive: '深掘り'
} as const;

function bySortOrder<T extends TermEntry | TopicEntry>(a: T, b: T) {
  if (a.data.sort_order !== b.data.sort_order) {
    return a.data.sort_order - b.data.sort_order;
  }

  return a.data.title.localeCompare(b.data.title, 'ja');
}

export async function getPublishedTerms() {
  const terms = await getCollection('terms', ({ data }) => data.status === 'published');
  return terms.sort(bySortOrder);
}

export async function getPublishedTopics() {
  const topics = await getCollection('topics', ({ data }) => data.status === 'published');
  return topics.sort(bySortOrder);
}

export function getTermHref(term: TermEntry) {
  return `/terms/${term.data.slug}/`;
}

export function getTopicHref(topic: TopicEntry) {
  return `/topics/${topic.data.slug}/`;
}

export function getExamScopeLabel(scope: string) {
  return EXAM_SCOPE_LABELS[scope as keyof typeof EXAM_SCOPE_LABELS] ?? scope;
}

export function getExamScopeLabels(scopes: string[]) {
  return scopes.map(getExamScopeLabel);
}

export function getContentLevelLabel(level: string) {
  return CONTENT_LEVEL_LABELS[level as keyof typeof CONTENT_LEVEL_LABELS] ?? level;
}

export function getContentStatusLabel(status: string) {
  return CONTENT_STATUS_LABELS[status as keyof typeof CONTENT_STATUS_LABELS] ?? status;
}

export function getTermCategoryLabel(category: string) {
  return TERM_CATEGORY_LABELS[category as keyof typeof TERM_CATEGORY_LABELS] ?? category;
}

export function getTopicTypeLabel(topicType: string) {
  return TOPIC_TYPE_LABELS[topicType as keyof typeof TOPIC_TYPE_LABELS] ?? topicType;
}

export function getTermVisualVariant(slug: string) {
  const variants = {
    mean: 'balance',
    variance: 'spread',
    'standard-deviation': 'spread',
    'normal-distribution': 'distribution'
  } as const;

  return variants[slug as keyof typeof variants] ?? 'generic';
}
