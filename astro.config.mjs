import { defineConfig } from 'astro/config';
import sitemap from '@astrojs/sitemap';
import {
  defaultBuildDir,
  resolveBasePath,
  resolveSiteUrl
} from './site-build.config.mjs';

export default defineConfig({
  site: resolveSiteUrl(),
  base: resolveBasePath(),
  outDir: defaultBuildDir,
  output: 'static',
  trailingSlash: 'always',
  integrations: [sitemap()],
  markdown: {
    shikiConfig: {
      theme: 'github-light'
    }
  }
});
