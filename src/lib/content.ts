import { getCollection, type CollectionEntry } from 'astro:content';

export type TermEntry = CollectionEntry<'terms'>;
export type TopicEntry = CollectionEntry<'topics'>;

function bySortOrder<T extends TermEntry | TopicEntry>(a: T, b: T) {
  if (a.data.sortOrder !== b.data.sortOrder) {
    return a.data.sortOrder - b.data.sortOrder;
  }

  return a.data.title.localeCompare(b.data.title, 'ja');
}

export async function getPublishedTerms() {
  const terms = await getCollection('terms', ({ data }) => !data.draft);
  return terms.sort(bySortOrder);
}

export async function getPublishedTopics() {
  const topics = await getCollection('topics', ({ data }) => !data.draft);
  return topics.sort(bySortOrder);
}

export function getTermHref(term: TermEntry) {
  return `/terms/${term.id}/`;
}

export function getTopicHref(topic: TopicEntry) {
  return `/topics/${topic.id}/`;
}
