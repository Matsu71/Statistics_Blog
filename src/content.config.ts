import { defineCollection } from 'astro:content';
import { glob } from 'astro/loaders';
import { z } from 'astro/zod';

const examScopeEnum = z.enum(['statistics_grade_2']);
const contentLevelEnum = z.enum(['foundation', 'standard', 'advanced']);
const contentStatusEnum = z.enum(['draft', 'published']);
const termCategoryEnum = z.enum([
  'descriptive_statistics',
  'probability',
  'probability_distribution',
  'sampling_distribution',
  'estimation',
  'hypothesis_testing',
  'correlation_regression',
  'data_handling'
]);
const topicTypeEnum = z.enum(['overview', 'deep_dive']);
const referenceTypeEnum = z.enum(['official', 'textbook', 'web']);

const exampleSchema = z.object({
  title: z.string(),
  description: z.string()
});

const formulaSchema = z.object({
  name: z.string(),
  latex: z.string(),
  description: z.string(),
  conditions: z.array(z.string()).default([])
});

const proofSchema = z.object({
  summary: z.string(),
  outline_steps: z.array(z.string()).default([])
});

const referenceSchema = z.object({
  title: z.string(),
  type: referenceTypeEnum,
  author: z.string().optional(),
  year: z.number().int().optional(),
  url: z.string().url().optional(),
  note: z.string().optional()
});

const terms = defineCollection({
  loader: glob({ base: './src/content/terms', pattern: '**/*.md' }),
  schema: z.object({
    title: z.string(),
    slug: z.string().regex(/^[a-z0-9-]+$/),
    exam_scope: z.array(examScopeEnum).min(1),
    level: contentLevelEnum,
    status: contentStatusEnum,
    category: termCategoryEnum,
    short_definition: z.string(),
    definition: z.string(),
    intuition: z.array(z.string()).min(1),
    visual_explanation: z.array(z.string()).default([]),
    where_it_appears: z.array(z.string()).min(1),
    practical_examples: z.array(exampleSchema).default([]),
    exam_points: z.array(z.string()).min(1),
    formulas: z.array(formulaSchema).default([]),
    rigorous_explanation: z.array(z.string()).default([]),
    proof: proofSchema.optional(),
    common_mistakes: z.array(z.string()).default([]),
    references: z.array(referenceSchema).default([]),
    aliases: z.array(z.string()).default([]),
    tags: z.array(z.string()).default([]),
    related_terms: z.array(z.string()).default([]),
    sort_order: z.number().int().default(999),
    updated_at: z.coerce.date()
  })
});

const topics = defineCollection({
  loader: glob({ base: './src/content/topics', pattern: '**/*.md' }),
  schema: z.object({
    title: z.string(),
    slug: z.string().regex(/^[a-z0-9-]+$/),
    exam_scope: z.array(examScopeEnum).min(1),
    level: contentLevelEnum,
    topic_type: topicTypeEnum,
    summary: z.string(),
    learning_goals: z.array(z.string()).min(1),
    related_terms: z.array(z.string()).default([]),
    sections: z
      .array(
        z.object({
          title: z.string(),
          objective: z.string(),
          related_terms: z.array(z.string()).default([])
        })
      )
      .default([]),
    references: z.array(referenceSchema).default([]),
    status: contentStatusEnum,
    sort_order: z.number().int().default(999),
    updated_at: z.coerce.date()
  })
});

export const collections = { terms, topics };
