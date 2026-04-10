import { defineConfig } from 'astro/config';
import sitemap from '@astrojs/sitemap';
import rehypeKatex from 'rehype-katex';
import remarkMath from 'remark-math';
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
    remarkPlugins: [remarkMath],
    rehypePlugins: [[rehypeKatex, { output: 'htmlAndMathml', throwOnError: false }]],
    shikiConfig: {
      theme: 'github-light'
    }
  }
});
