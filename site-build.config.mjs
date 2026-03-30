export const githubPagesOwner = 'Matsu71';
export const githubPagesRepository = 'Statistics_Blog';
export const defaultSiteUrl = `https://${githubPagesOwner}.github.io`;
export const defaultBasePath = `/${githubPagesRepository}`;
export const defaultBuildDir = 'docs';

export function resolveSiteUrl() {
  return process.env.PUBLIC_SITE_URL ?? defaultSiteUrl;
}

export function resolveBasePath() {
  const raw = process.env.PUBLIC_BASE_PATH ?? defaultBasePath;

  if (raw === '/' || raw === '') {
    return '/';
  }

  return `/${raw.replace(/^\/+|\/+$/g, '')}`;
}

export function resolveNormalizedBasePath() {
  return resolveBasePath().replace(/^\/+|\/+$/g, '');
}
