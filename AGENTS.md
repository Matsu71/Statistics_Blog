# AGENTS.md

## Site Mission

このリポジトリは、統計検定2級を主対象にした「1用語1ページ」の学習用統計サイトを、継続的かつ安全に拡充するためのものです。

- 最優先は、GitHub Pages で安定公開できる高品質な用語ページ資産を積み上げることです。
- 各ページは単なる辞書項目ではなく、初学者が上から読んで理解できる短い解説記事として作成します。
- 現在の主対象は `src/content/terms/` です。`topics` は将来拡張用であり、通常運用では `terms` を優先します。
- ホームや一覧ページは導線としてシンプルに保ちます。情報の厚みは各 term / topic の詳細ページに寄せます。
- サイト全体の表示方針は、シンプルで洗練され、利用者が一目で構造を理解できることを優先します。
- 文字による補足説明は最小限にし、画面構成、余白、見出し、カードの役割で自然に伝えることを優先します。
- 公開済み件数、追加予定、次の候補、おすすめ入口などの運用情報は内部データとして保持してよいですが、利用者に必要な場合を除きホームに表示しません。
- この表示方針は制作・編集のための指針であり、サイト本文にはコンセプト文として掲載しません。

## Target Readers

- 主対象読者は、統計検定2級を学ぶ文系の初学者です。
- 数式に苦手意識がある学習者、実務で基礎を学び直したい人、理系の基礎整理をしたい人も想定します。
- 方針は「入口はやさしく、内容は浅くしすぎない」です。

## Source Of Truth

この repo では、次を正本として扱います。

- 用語 schema: `src/content.config.ts`
- 用語キュー: `data/term-queue.json`
- 用語ページ生成 Skill: `.agents/skills/term-page-generator/SKILL.md`

これらと他の文書が矛盾した場合は、`src/content.config.ts` と `data/term-queue.json` を優先します。

## Scope And Content Model

- 主な編集対象は `src/content/terms/*.md` です。
- `src/pages/index.astro`、`src/pages/terms/index.astro`、`src/pages/topics/index.astro` は導線ページであり、長い説明や運用状況の表示を増やしすぎません。
- frontmatter は必ず `src/content.config.ts` の `terms` schema に従います。
- 必須 frontmatter は少なくとも次です。
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
- 任意だが強く推奨する frontmatter は次です。
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
- `status` は `draft` または `published` を使います。不確かな内容や `TODO:` / `保留:` が残る場合は `status: draft` にします。
- `related_terms` には、実在する term slug のみを入れます。
- queue で管理されている slug については、`title`、`category`、`level`、`exam_scope`、`related_terms`、`content_path` を queue と矛盾させません。
- Markdown 本文は補足ノートです。主要な導線は frontmatter から描画されるため、本文だけで必須情報を持たせません。

この repo では次の旧キーを使いません。

- `description`
- `examLevel`
- `relatedTerms`
- `sortOrder`
- `updatedAt`
- `draft: true`

代わりに、次の現行キーを使います。

- `short_definition`
- `exam_scope`
- `related_terms`
- `sort_order`
- `updated_at`
- `status: draft`

## Required Content Blocks

publishable / safe draft を問わず、用語ページでは少なくとも次の情報が frontmatter または補足本文から読める状態にします。

1. `short_definition`
2. `intuition`
3. `definition`
4. `where_it_appears`
5. `exam_points`
6. `related_terms`

加えて、少なくとも 1 つの具体例を入れます。具体例は次のどちらかです。

- `practical_examples` に入った具体例
- `intuition` または Markdown 本文中の、小さな数値例や現実の場面に結びついた具体例

比喩だけで終わる説明は、具体例として数えません。

既存公開ページを改稿するときは、上の必須項目に加えて、次の観点を監査します。全てを同じ長さで入れる必要はありませんが、不足が大きいページから優先して補強します。

- 初学者向けの入口説明があるか
- 直感的な説明と視覚的な説明が定義と矛盾していないか
- その概念が「何を表すか」と「何を表さないか」が分かるか
- 小さな数値例、現実例、または確認問題があるか
- 類似概念との違いや、試験での見分け方があるか
- 数式がある場合、記号の意味だけでなく式が言っていることを説明しているか
- 証明や厳密説明がある場合、結論だけでなく途中の意味を追えるか
- 関連用語への導線が、次に読む理由と一緒に分かるか

## Optional Content Blocks

用語に応じて、次を追加します。

- `visual_explanation`
- `practical_examples`
- `formulas`
- `rigorous_explanation`
- `proof`
- `common_mistakes`
- `references`

説明順は `直感 -> 定義 -> 現れる場面 -> 試験で重要なポイント -> 数式 / 厳密説明` を基本にします。`rigorous_explanation` と `proof` は後半に置きます。

## Writing And Notation Rules

- 文体は説明中心で、威圧的にしません。
- 過度にくだけた口調にはしません。
- 1ページ1概念を原則とし、別概念を混ぜる場合は区別を明示します。
- ホームや一覧の見出しは短く保ちます。
- ホームや一覧には、必要以上のメタ説明、運用説明、件数表示、追加予定、サンプル配置の説明を置きません。
- 説明を足す必要がある場合は、まず詳細ページ側の `definition`、`intuition`、`exam_points`、`practical_examples` などを充実させることを優先します。
- `short_definition` は 1 文で、その用語の役割がすぐ分かる要約にします。
- 記号は初出で意味を説明します。
- 数式は KaTeX でレンダリングされる前提で、`formulas[].latex` には正規の LaTeX を入れます。`√`、`Σ`、`1 / n` のようなプレーン表記ではなく、`\sqrt{}`、`\sum`、`\frac{}{}` を優先します。
- frontmatter の文章中で記号や短い式を書く場合は、`$x_i$`、`$\bar{x}$`、`$\sigma^2$` のように inline math として明示します。
- display 数式は、式の直前に短い説明、式の直後に記号の見方や解釈を置き、式だけが孤立しない構成にします。
- 長い式はモバイルで横スクロールできる前提ですが、1つの式に詰め込みすぎず、必要なら説明を分割します。
- 数式表示の標準は、KaTeX によるテキストベースの静的レンダリング、`FormulaCard` の「説明 -> 式 -> 記号の見方」、`MathText` による inline math 表示です。この読みやすさを下げる実装へ戻しません。
- 数式 UI を変更するときは、少なくとも `normal-distribution`、`random-sampling`、`variance`、`sample-mean`、`range` の詳細ページで、長い式、分数、根号、添字、総和、証明折りたたみ、例題ブロックの見え方を確認します。
- 母集団 / 標本、不偏 / 標本、確率変数 / 観測値など、誤読しやすい前提は明示します。
- 既存ページとの表記ゆれを避けます。
- 関連用語は単に列挙するだけでなく、本文または補足ノートでも「なぜ関連するか」に触れます。
- Markdown 見出しは補助的に使ってよいですが、frontmatter で持つべき必須情報の代替にはしません。
- 数学的に「確か」とみなしてよいのは、少なくとも次のどちらかを満たす内容だけです。
  - 入力の `source_notes`、既存ページ、repo 内ルールから直接確認できる
  - このページ内で定義・式・計算として明示し、自分で記号と前提を説明できる
- 上の条件を満たせない主張は未確認扱いとし、`TODO:` / `保留:` に回します。

## Multi-Agent Rules

用語ページ作成時は、必ず複数の subagent を立てて並列で進めます。コストより品質を優先します。

最低限、次の固定役割を使います。

- 基本説明担当
- 直感・イメージ担当
- 実例担当
- 数学的厳密説明担当
- 編集統合担当
- 品質チェック担当

運用ルールは次のとおりです。

- 親 agent は全 subagent の結果が揃うまで統合しません。
- 親 agent が最終的な統合責任を持ちます。
- 品質チェック担当は合否判定と差し戻し理由の明文化を担います。
- 品質チェック担当の出力は、少なくとも `pass` / `fail`、不足項目、差し戻し理由を含めます。
- 必要に応じて、試験対策担当、関連語導線担当、図解発想担当を追加してよいです。

## Term Page Workflow

1. `AGENTS.md`、`.agents/skills/term-page-generator/SKILL.md`、`src/content.config.ts`、`data/term-queue.json`、近い既存用語ページを確認します。
2. 対象 slug が queue 管理下にある場合は、queue の `title`、`category`、`level`、`exam_scope`、`related_terms` を canonical 値として採用します。
3. 固定役割の subagent を並列起動します。
4. 親 agent は全 subagent の結果を待ってから、1 本の Markdown に統合します。
5. frontmatter が schema と一致しているか、`related_terms` が既存 slug のみで構成されているか確認します。
6. publishable にできない不確定事項が残る場合は `TODO:` / `保留:` を残し、`status: draft` にします。
7. repo に保存する変更では、少なくとも `npm run generate:index`、`npm run validate:term-queue`、`npm run validate:content`、`npm run build` を通してから完了扱いにします。
8. schema、型、UI コンポーネントも変更した場合は `npm run check` も実行します。

### Existing Page Improvement Workflow

既存公開ページをまとめて底上げする場合は、次の順に進めます。

1. 既存の `src/content/terms/*.md` を全て監査し、ページごとに不足観点を短く整理します。
2. 監査では、概念説明、直感・図解、例題・比較、数式・証明、関連導線、よくある勘違いを分けて見ます。
3. 共通テンプレートや Skill の方針が不足していれば、先に制作ルールとして追記します。
4. 改稿では URL、slug、queue の canonical 値を壊さず、frontmatter の既存 block を厚くすることを優先します。
5. 関連用語は `data/term-queue.json` と矛盾させません。未公開 slug へ導線を張る場合は本文内の比較に留めます。
6. 全ページを同じ分量にそろえるのではなく、基礎概念や後続ページの土台になるページから深くします。
7. 最後に `npm run generate:index`、`npm run validate:term-queue`、`npm run validate:content`、`npm run lint`、`npm run check`、`npm run build`、`npm run validate:links` を実行します。

## Git Operation Rule

- この repo では、変更を加えたら原則としてそのターン内で commit と push まで行います。
- build 成果物を伴う変更では、source 変更だけでなく `docs/` も含めて commit / push します。
- push 前には、変更内容に応じた validation / build を実行してから進めます。
- 例外は、ユーザーが明示的に「まだ commit / push しない」と指定した場合だけです。

## Done Criteria

### Publishable

以下を満たしたときだけ公開可能扱いにします。

- frontmatter が `src/content.config.ts` と整合している。
- 必須 content block が揃っている。
- 具体例が少なくとも 1 つある。
- 数式を出す場合、記号の意味を説明している。
- 数学的に不確かな断定がない。
- `related_terms` が既存 slug のみで構成されている。
- 関連用語について、本文または補足ノートで「なぜ関連するか」に触れている。
- `TODO:` / `保留:` が残っていない。
- `status` は `published` である。
- `src/generated/term-index.json` が再生成済みである。
- `npm run validate:term-queue`、`npm run validate:content`、`npm run build` が通る。
- schema / UI 変更を伴う場合は `npm run check` も通る。

### Safe Draft

公開はしないが、安全に保留できる状態は次です。

- frontmatter と必須 content block は揃っている。
- 必須 block は空欄ではなく、最低 1-2 文の安全な説明または理由つき `TODO:` / `保留:` がある。
- 不確かな箇所が `TODO:` / `保留:` で理由つきに分離されている。
- 不確かな内容を断定で書いていない。
- `status` は `draft` である。
- repo に保存するなら `npm run generate:index`、`npm run validate:term-queue`、`npm run validate:content`、`npm run build` が通る。

## Prohibited Actions

- 推測で数学的事実を埋めないこと。
- 根拠が弱いまま定理、条件、一般則、同値関係を断定しないこと。
- 不確かな内容をもっともらしい文章で隠さないこと。
- 詳細ページで不足している説明を、ホームや一覧の長文で補わないこと。
- ホームや一覧に、公開中件数、追加予定、サンプル説明などの運用メタ情報を常設しないこと。
- 存在しない slug を `related_terms` に入れないこと。
- queue の canonical 値と矛盾する frontmatter を作らないこと。
- 旧 frontmatter キーを新規に導入しないこと。
- Markdown 本文だけで必須情報を持たせ、frontmatter を空にしないこと。
- 1ページに複数の中心概念を詰め込みすぎないこと。
- 1時間ごとの運用を理由に品質基準を下げないこと。

## When Uncertain

- 不確かな内容は `TODO:` または `保留:` として残します。
- 数学的に確信がない式、性質、証明は本文で断定しません。
- 重要な前提が未確認なら、その block は省略するか保留に回します。
- 未確定事項が公開品質に影響する場合は `status: draft` にし、publishable 完了扱いにしません。
