import { defineCollection } from 'astro:content';
import { glob } from 'astro/loaders';
import { z } from 'astro/zod';

const pId = /^P(?:0[1-9]|[1-6]\d|7[0-2])$/;
const prerequisiteId = /^(?:[FG](?:0[1-9]|[1-3]\d|40)|P(?:0[1-9]|[1-6]\d|7[0-2]))$/;
export const pregrade1Lessons = defineCollection({
  loader: glob({ base: './src/content/pregrade1', pattern: '**/*.md' }),
  schema: z.object({
    lesson_id: z.string().regex(pId),
    slug: z.string().regex(/^[a-z0-9-]+$/),
    title: z.string().min(1),
    description: z.string().min(1),
    status: z.enum(['draft', 'published']),
    goals: z.array(z.string()).min(1).max(4),
    prerequisites: z.array(z.string().regex(prerequisiteId)).default([]),
    reading_minutes: z.number().int().positive(),
    practice_minutes: z.number().int().positive(),
    practice_count: z.number().int().min(4),
    revision_note: z.string().optional(),
    review_status: z.enum(['self_checked', 'independently_reviewed']),
    updated_at: z.coerce.date()
  })
});
