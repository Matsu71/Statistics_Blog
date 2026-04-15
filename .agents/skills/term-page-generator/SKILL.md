# term-page-generator

## What This Skill Does

この Skill は、統計検定2級を主対象にした「1用語1ページ」の term 原稿を、固定役割の多エージェント分担で新規作成または改稿するためのものです。

- 主出力は `src/content/terms/<slug>.md` です。
- 目的は、文系初学者にも読みやすく、かつ数学的にごまかさない解説を安定して再現することです。
- 実行前に、必ず repo 直下の `AGENTS.md`、`src/content.config.ts`、`data/term-queue.json`、近い既存用語ページを確認します。
- この Skill は、ホームや一覧を説明過多にせず、内容の厚みを各 term 詳細ページへ集める前提で使います。

## When To Use

- 新しい用語ページを追加するとき
- 既存の用語ページを同じ品質基準で拡充するとき
- ページ構成、表記、品質基準を repo 標準に合わせて整えるとき

## When Not To Use

- `src/content/topics/` の分野解説ページを作るとき
- 数学的裏取りなしでは書けない高度な事項を、根拠なしで埋めようとしているとき
- UI 実装や Astro コンポーネントだけを変更するとき

## Required Inputs

最低限、次のどちらかを受け取ります。

- `queue_item`
- または `term`, `slug`, `category`, `level`, `exam_scope`

あると望ましい入力は次です。

- `aliases`
- `tags`
- `related_terms_candidates`
- `must_cover`
- `reader_level`
- `existing_file`
- `sort_order_hint`
- `uncertain_points`
- `source_notes`
- `publish_intent`

入力不足時のルール:

- 推測で埋めません。
- queue 管理下の slug では、queue の値を canonical とします。
- 不足が致命的でない場合は `TODO:` / `保留:` として明示します。
- 不足が公開品質に直結する場合は `status: draft` にします。

## Expected Outputs

### Output Files

- 主出力: `src/content/terms/<slug>.md`
- repo に保存する変更では、必要に応じて `src/generated/term-index.json` も更新対象になります。

### Frontmatter Rules

frontmatter は `src/content.config.ts` の `terms` schema に従います。

必須:

- `title`
- `slug`
- `exam_scope`
- `level`
- `status`
- `category`
- `short_definition`
- `definition`
- `intuition`
- `where_it_appears`
- `exam_points`
- `updated_at`

任意だが推奨:

- `visual_explanation`
- `practical_examples`
- `formulas`
- `rigorous_explanation`
- `proof`
- `common_mistakes`
- `references`
- `aliases`
- `tags`
- `related_terms`
- `sort_order`

ルール:

- `status` は `draft` または `published` のみを使います。
- `related_terms` には、確認できた既存 slug だけを入れます。
- queue 管理下の slug では、`title`、`category`、`level`、`exam_scope`、`related_terms` を queue と矛盾させません。
- この repo は `description`、`examLevel`、`relatedTerms`、`sortOrder`、`updatedAt`、`draft: true` を使いません。

## Page Structure Rules

この repo の term 詳細ページは、Markdown 本文の見出しからではなく frontmatter から主要 sections を描画します。

ホームや一覧は導線に徹し、長い説明や運用メタ情報を持たせない前提です。そのため、読者理解に必要な説明は term 詳細ページ内で完結するように作ります。

そのため、最低限の中身は次の block に入れます。

- `short_definition`
- `intuition`
- `definition`
- `where_it_appears`
- `exam_points`
- `related_terms`

必要に応じて次を追加します。

- `visual_explanation`
- `practical_examples`
- `formulas`
- `rigorous_explanation`
- `proof`
- `common_mistakes`
- `references`

Markdown 本文は補足ノートです。本文の見出しは補助的に使ってよいですが、必須情報を本文だけに置きません。

### Existing Page Improvement Mode

既存の公開済み用語ページを改稿するときは、次の監査を先に行います。

- 初学者向け導入が足りないページ
- 直感・視覚説明が抽象的すぎるページ
- 現実例、例題、確認問題が少ないページ
- 試験での見分け方や類似概念との違いが弱いページ
- よくある勘違いが一般論に寄りすぎているページ
- 数式の意味説明や記号説明が短すぎるページ
- 証明や厳密説明が結論だけで終わっているページ
- 関連用語の「なぜ次に読むか」が本文でつながっていないページ

改稿では、URL、slug、queue の canonical 値を壊さず、既存の frontmatter block を厚くすることを優先します。全ページを同じ長さにそろえる必要はありません。基礎概念や後続ページの土台になる用語を優先して深くします。

### Math Writing Rules

- 数式は KaTeX でレンダリングされる前提で書きます。
- `formulas[].latex` には、`√`、`Σ`、`1 / n` ではなく、`\sqrt{}`、`\sum`、`\frac{}{}` などの正規 LaTeX を入れます。
- `description`、`conditions`、`rigorous_explanation`、`proof.outline_steps` などの文章中で記号や短い式を書く場合は、`$x_i$` や `$\bar{x}$` のように inline math で明示します。
- display 数式は、式の直前に短い説明、式の直後に記号の見方や解釈が続くようにします。
- 長い式は本文に埋め込まず、数式カードまたは display math として独立させます。
- 現在の数式表示スタイルは維持対象です。`FormulaCard` の「説明 -> 式 -> 記号の見方」、`MathText` の inline math、`.formula-block` の穏やかなカード表示を前提に原稿を作ります。
- 数式 UI の変更や、長い式を含む原稿を作った場合は、`normal-distribution`、`random-sampling`、`variance`、`sample-mean`、`range` を代表ページとして確認します。

具体例は少なくとも 1 つ必要です。具体例は次のどちらかです。

- `practical_examples` に入った具体例
- `intuition` または本文中の、小さな数値例や現実の場面に結びついた具体例

## Fixed Multi-Agent Roles

親 agent は、最低でも次の 6 役割を並列起動し、全結果を待ってから統合します。

- `基本説明担当`
  - 用語の核心、初学者向けの入口、試験上の位置づけを整理する。
- `直感・イメージ担当`
  - たとえ、視覚的な捉え方、小さな数値例で直感を作る。
- `実例担当`
  - 現実世界の例、実務例、試験での出題文脈を出す。
- `数学的厳密説明担当`
  - 定義、記号の意味、数式、前提条件、母集団 / 標本などの区別を書く。
- `編集統合担当`
  - 全担当の結果を 1 本の Markdown に統合し、構成、文体、重複、表記を整える。
- `品質チェック担当`
  - MUST / SHOULD 基準で合否判定し、`TODO:` / `保留:` と `status: draft` の要否を判断する。
  - 出力には `pass` / `fail`、不足項目、差し戻し理由を含める。

既存ページをまとめて改善する場合は、上記に加えて次の観点を担当に含めます。

- `テンプレート・情報設計担当`
  - 共通構成、Skill、AGENTS、編集ガイドの不足を確認する。
- `監査担当`
  - 全既存ページをページ別に評価し、優先順位と不足観点を明文化する。

親 agent の責務:

- 全 subagent の結果が揃うまで本文を確定しないこと
- 最終統合責任を持つこと
- 品質チェック担当の指摘を反映すること

## Quality Standards

### MUST

- 数学的事実を推測で補わない。
- 必須 frontmatter を満たす。
- 必須 content block を満たす。
- 1ページ1概念を守る。
- 記号は初出で説明する。
- 誤読しやすい前提条件を明示する。
- `related_terms` は既存 slug のみを使う。
- 関連用語は本文または補足ノートでも「なぜ関連するか」に触れる。
- 具体例を少なくとも 1 つ入れる。
- 不確かな内容は `TODO:` / `保留:` で隔離し、必要なら `status: draft` にする。
- 数学的に「確か」とみなせるのは、次のどちらかを満たす内容だけにする。
  - `source_notes`、既存ページ、repo 内ルールから直接確認できる
  - このページ内で定義・式・計算として明示し、記号と前提を説明できる
- 上の条件を満たせない主張は未確認扱いとし、`TODO:` / `保留:` に回す。

### SHOULD

- `aliases`、`tags`、`sort_order`、`updated_at` を可能な限り入れる。
- `visual_explanation` または `practical_examples` のどちらかを入れる。
- 数式の意味を言葉でも説明する。
- その用語が「何を表すか」と「何を表さないか」を説明する。
- 類似概念との違いが重要な用語では、比較説明や短い確認問題を入れる。
- 発展内容は後半に分離する。
- 既存ページと同程度のトーンと block 粒度を保つ。
- ホームや一覧の補助説明に頼らず、このページ単体で読んで理解できる密度を目指す。

## Execution Procedure

1. `AGENTS.md`、`src/content.config.ts`、`data/term-queue.json`、近い既存ページを読む。
2. 入力から canonical な `title`、`slug`、`category`、`level`、`exam_scope`、未確定事項、関連語候補を整理する。
3. 親 agent が固定 6 役割の subagent を並列起動する。
4. 親 agent は全 subagent の結果を待つ。
5. `編集統合担当` の視点で frontmatter と本文を 1 本に統合する。
6. `品質チェック担当` の視点で MUST / SHOULD を照合する。
7. queue 管理下の slug では queue と frontmatter の整合を再確認する。
8. repo に保存する変更では `npm run generate:index`、`npm run validate:term-queue`、`npm run validate:content`、`npm run build` を通す。
9. schema、型、UI を触った場合は `npm run check` も実行する。
10. 公開可能なら `status: published` にする。未確定事項が残るなら `TODO:` / `保留:` と `status: draft` で安全な下書きにする。

既存ページをまとめて改稿した場合は、`npm run lint`、`npm run check`、`npm run validate:links` も実行し、生成済み `docs/` に反映します。

subagent を十分に起動できない環境では、この Skill は成功扱いにしません。

## Failure Handling And Draft Policy

- 数学的裏取りが弱い内容は断定で書きません。
- optional block は安全に書けないなら省略します。
- 必須 block は省略せず、最低 1-2 文の安全な説明と理由つき `TODO:` / `保留:` を残します。
- 未確定事項は `TODO:` または `保留:` を理由つきで残します。
- 公開品質に届かない場合は `status: draft` を設定します。
- `related_terms` や例を安全に確定できない場合は、無理に埋めません。

## Definition Of Done

### Publishable Done

以下をすべて満たします。

- `src/content/terms/<slug>.md` が作成または更新されている。
- frontmatter が `src/content.config.ts` と整合している。
- 必須 content block が揃っている。
- 少なくとも 1 つの具体例がある。
- 数式を使う場合、記号の意味が説明されている。
- `rigorous_explanation` または `proof` を入れる場合は、直感説明と文脈の両方で区別されている。
- 数学的に不確かな断定がない。
- `related_terms` は既存 slug のみで構成されている。
- 関連用語について、本文または補足ノートで「なぜ関連するか」に触れている。
- `TODO:` / `保留:` が残っていない。
- `status` は `published` である。
- `src/generated/term-index.json` が再生成済みである。
- `npm run validate:term-queue`、`npm run validate:content`、`npm run build` が通る。
- schema / UI 変更を伴う場合は `npm run check` も通る。

### Safe Draft Done

公開しない前提で、次を満たします。

- frontmatter と必須 content block は揃っている。
- 必須 block は空欄ではなく、最低 1-2 文の安全な説明または理由つき `TODO:` / `保留:` がある。
- 不確かな箇所が `TODO:` / `保留:` で理由つきに明示されている。
- 不確かな内容を断定で書いていない。
- `status` は `draft` である。
- repo に保存するなら `npm run generate:index`、`npm run validate:term-queue`、`npm run validate:content`、`npm run build` が通る。

## Sample Input

```yaml
task: create_term_page
queue_item:
  slug: sample-variance
  title: 標本分散
  category: descriptive_statistics
  level: standard
  exam_scope:
    - statistics_grade_2
  related_terms:
    - mean
    - variance
    - standard-deviation
term: 標本分散
slug: sample-variance
category: descriptive_statistics
level: standard
exam_scope:
  - statistics_grade_2
aliases:
  - 標本の分散
tags:
  - 散布度
  - 標本
must_cover:
  - 平均からのずれの二乗平均という考え方
  - 母分散との違い
  - 不偏分散との違い
related_terms_candidates:
  - mean
  - variance
  - standard-deviation
reader_level: 統計検定2級の文系初学者
existing_file: null
sort_order_hint: 40
uncertain_points:
  - 標本分散と不偏分散の説明順
source_notes:
  - 既存ページの文体に合わせる
  - 数式は必要最小限だが意味説明を省かない
publish_intent: draft_allowed
```

## Output Template

optional block は、必要なものだけ残します。不要な optional block は削除してかまいません。

```md
---
title: <表示名>
slug: <slug>
exam_scope:
  - statistics_grade_2
level: <foundation|standard|advanced>
status: <draft|published>
category: <term-category>
short_definition: <1文要約>
definition: <定義文>
intuition:
  - <直感説明>
visual_explanation: []
where_it_appears:
  - <現れる場面>
practical_examples: []
exam_points:
  - <試験上の要点>
formulas: []
rigorous_explanation: []
common_mistakes: []
references: []
aliases: []
tags: []
related_terms:
  - <existing-slug>
sort_order: <number>
updated_at: <YYYY-MM-DD>
---

この本文は補足ノートです。frontmatter で表現しきれない背景、関連用語とのつながり、例外事項だけを補います。
```
