export const siteMeta = {
  name: '統計ことばノート',
  shortName: '統計ことば',
  description:
    '統計検定2級を学ぶ人のための、1用語1ページ型の学習用語集サイトです。'
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
