import { defineCollection } from 'astro:content';
import { glob } from 'astro/loaders';
import { z } from 'astro/zod';

const terms = defineCollection({
  loader: glob({ base: './src/content/terms', pattern: '**/*.md' }),
  schema: z.object({
    title: z.string(),
    description: z.string(),
    category: z.string(),
    examLevel: z.string().default('統計検定2級'),
    aliases: z.array(z.string()).default([]),
    tags: z.array(z.string()).default([]),
    relatedTerms: z.array(z.string()).default([]),
    sortOrder: z.number().default(999),
    draft: z.boolean().default(false),
    updatedAt: z.coerce.date().optional()
  })
});

const topics = defineCollection({
  loader: glob({ base: './src/content/topics', pattern: '**/*.md' }),
  schema: z.object({
    title: z.string(),
    description: z.string(),
    status: z.enum(['planned', 'draft', 'published']).default('planned'),
    relatedTerms: z.array(z.string()).default([]),
    sortOrder: z.number().default(999),
    draft: z.boolean().default(false),
    updatedAt: z.coerce.date().optional()
  })
});

export const collections = { terms, topics };
