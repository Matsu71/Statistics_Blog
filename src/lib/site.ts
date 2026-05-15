export const siteMeta = {
  name: '統計ラボ',
  shortName: '統計ラボ',
  description:
    '統計の用語、考え方、数式、試験ポイントを整理する学習サイトです。'
};

export const navigation = [
  { label: 'ホーム', href: '/' },
  { label: '用語一覧', href: '/terms/' },
  { label: '分野解説', href: '/topics/' }
];

export function withBase(path: string) {
  const normalizedPath = path.startsWith('/') ? path : `/${path}`;
  const base = import.meta.env.BASE_URL === '/' ? '' : import.meta.env.BASE_URL.replace(/\/$/, '');
  return `${base}${normalizedPath}`;
}

export function formatDate(value?: Date) {
  if (!value) {
    return '';
  }

  return new Intl.DateTimeFormat('ja-JP', {
    year: 'numeric',
    month: 'long',
    day: 'numeric'
  }).format(value);
}
