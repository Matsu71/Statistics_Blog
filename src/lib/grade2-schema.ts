import { defineCollection } from 'astro:content';
import { glob } from 'astro/loaders';
import { z } from 'astro/zod';

export const grade2Lessons = defineCollection({
  loader: glob({ base: './src/content/grade2', pattern: '**/*.md' }),
  schema: z.object({
    lesson_id: z.string().regex(/^G(?:0[1-9]|[1-3]\d|40)$/),
    slug: z.string().regex(/^[a-z0-9-]+$/),
    title: z.string().min(1),
    description: z.string().min(1),
    status: z.enum(['draft', 'published']),
    goals: z.array(z.string()).min(1).max(4),
    prerequisites: z.array(z.string().regex(/^[FG](?:0[1-9]|[1-3]\d|40)$/)).default([]),
    reading_minutes: z.number().int().positive(),
    practice_minutes: z.number().int().positive(),
    practice_count: z.number().int().min(4),
    review_status: z.enum(['self_checked', 'independently_reviewed']),
    updated_at: z.coerce.date()
  })
});
