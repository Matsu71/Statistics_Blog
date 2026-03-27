import { defineConfig } from 'astro/config';
import sitemap from '@astrojs/sitemap';

const repository = process.env.GITHUB_REPOSITORY?.split('/')[1] ?? '';
const owner =
  process.env.GITHUB_REPOSITORY_OWNER ??
  process.env.GITHUB_REPOSITORY?.split('/')[0] ??
  '';
const isUserOrOrgPagesSite = owner !== '' && repository === `${owner}.github.io`;

const site =
  process.env.PUBLIC_SITE_URL ??
  (owner ? `https://${owner}.github.io` : 'https://example.com');
const base =
  process.env.PUBLIC_BASE_PATH ??
  (repository && !isUserOrOrgPagesSite ? `/${repository}` : '/');

export default defineConfig({
  site,
  base,
  output: 'static',
  trailingSlash: 'always',
  integrations: [sitemap()],
  markdown: {
    shikiConfig: {
      theme: 'github-light'
    }
  }
});
