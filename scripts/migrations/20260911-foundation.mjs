import { readFile, writeFile, readdir } from 'node:fs/promises';
import { fileURLToPath } from 'node:url';
import path from 'node:path';

// One-time, idempotent policy migration. Preserve the earlier design as a dated snapshot.
const root = fileURLToPath(new URL('../../', import.meta.url));
async function prependOnce(relativePath, marker, lines) {
  const absolutePath = path.join(root, relativePath);
  const old = await readFile(absolutePath, 'utf8');
  if (old.includes(marker)) return;
  await writeFile(absolutePath, lines.join('\n') + '\n\n' + old, 'utf8');
  console.log(`policy updated: ${relativePath}`);
}

await prependOnce('AGENTS.md', 'FOUNDATION_POLICY_20260911', [
  '<!-- FOUNDATION_POLICY_20260911 -->',
  '## 現行の学習コース方針（2026-09-11・この節を優先）',
  '',
  '公開する学習順序は **基礎 → 2級 → 準1級 → 1級** です。基礎は4級・3級の内容を統合し、初心者の入口とします。独立した4級コースは設けません。以下の旧来の「2級中心・用語ページ優先」は既存用語辞典の運用説明であり、サイト全体の対象や制作優先順位を制限しません。',
  '',
  '現行の基礎コース仕様は [09-foundation-course.md](project-docs/learning-platform-design/09-foundation-course.md) を参照してください。順序教材は `src/content/lessons/`、構成は `src/data/foundation-course.json`、教材schemaは `src/lib/foundation-schema.ts`、公開ルートは `src/pages/learn/[slug].astro` です。旧termsとtopicsのschema・キューは、それらの既存記事に引き続き適用します。新しいlessons原稿には旧termsのfrontmatterや生成Skillを機械的に適用しません。',
  '',
  '各講座には、目標、基本の説明、条件、具体例、3問以上の確認問題と解答・誤答理由、適切な詳しい説明、特定できる出典を用意します。重要な使用条件は隠さず、導出・発展は折りたたみます。下書きや予定講座を公開済み・全範囲対応済みとして数えません。比較対象より高品質を目指しますが、実証のない優越性を表示しません。',
  '',
  '確認は数学・初学者向け説明・範囲/出典・UIの観点を分けます。自己点検を独立監修と表示しません。実施していない複数担当者・subagentの確認を記録してはいけません。新しいlessonsの公開前には、既存の `npm run verify` と `node scripts/validate-foundation.mjs` を実行し、UI変更時は `node scripts/test-foundation-browser.mjs` も実行してください。後者はPlaywrightとChromiumが必要です。',
  '',
  '原稿とUIを変更したときは、検証した生成物 `docs/` も含めて保存します。公開前の検証はstagingブランチで行い、成功した内容だけをmainへ反映します。',
  '',
  '---'
]);

await prependOnce('README.md', 'FOUNDATION_RELEASE_20260911', [
  '<!-- FOUNDATION_RELEASE_20260911 -->',
  '## 統計の基礎コース（2026-09-11）',
  '',
  '4級・3級の内容を統合した **基礎 → 2級 → 準1級 → 1級** の学習構成へ拡張しています。基礎コースの初期構成は8章・40講座。最初の6講座・確認問題18問を実装し、残りの講座は準備中として区別しています。',
  '',
  '[基礎コース](https://Matsu71.github.io/Statistics_Blog/courses/foundation/) · [講座の構成・品質基準](project-docs/learning-platform-design/09-foundation-course.md) · [講座原稿](src/content/lessons/)',
  '',
  '基本説明は常時表示し、詳しい説明と解答は開閉できます。講座の前後移動、目次、証明等への直接リンク、印刷時の展開に対応します。確認問題は自分で考えて解答を開く形式で、自動採点や学習履歴保存はまだ実装していません。',
  '',
  '検証は `npm run generate:index && npm run verify && node scripts/validate-foundation.mjs` で行います。ブラウザ検証はPlaywright/Chromiumを用い、staging用ワークフローで実行します。検証結果は [初期リリースの検証記録](project-docs/learning-platform-design/10-foundation-validation.json) を参照してください。',
  '',
  '以下の「次期設計・未実装」は初期設計時点の記録です。現在の実装範囲は上記と09の仕様を優先します。既存の用語ページ・URLは維持しています。',
  '',
  '---'
]);

const directory = 'project-docs/learning-platform-design';
const files = await readdir(path.join(root, directory));
for (const filename of files.filter((name) => /^(0[1-8]-.+|README)\.md$/.test(name))) {
  await prependOnce(`${directory}/${filename}`, 'FOUNDATION_SUPERSEDES_20260911', [
    '<!-- FOUNDATION_SUPERSEDES_20260911 -->',
    '> **2026-09-11の更新**：本書は初期設計の記録です。現在の公開学習順序は「基礎（4級・3級統合）→2級→準1級→1級」に変更し、独立した4級コースは設けません。基礎の8章・40講座構成、最初の6講座の実装、教材分量と品質基準は [09 基礎コースの現行仕様](09-foundation-course.md) を優先してください。以下の「未実装」は初期設計時点の状態です。とけたろうブログ本体は後続調査で確認できたため、その追記も09を参照してください。'
  ]);
}
const specificationPath = path.join(root, directory, '09-foundation-course.md');
const specification = await readFile(specificationPath, 'utf8');
const cleaned = specification.replace(/^全40講座は設計上の予定枠で.*$/m,
  '全40講座は設計上の予定枠で、40講座の本文が完成したという意味ではない。正本の構成データは [foundation-course.json](../../src/data/foundation-course.json) に置く。');
if (cleaned !== specification) await writeFile(specificationPath, cleaned, 'utf8');
console.log('foundation policy migration completed');
