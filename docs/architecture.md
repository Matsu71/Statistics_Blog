# Architecture

## 目的

このサイトは、統計検定2級を主対象にした「1用語1ページ」の学習用語集を GitHub Pages で継続公開するための土台である。

最初の主役は `terms` であり、各ページは単なる辞書ではなく、理解重視の短い解説記事として扱う。将来は、複数の用語ページを束ねた `topics` を追加し、重要分野の解説ページへ発展させる。

## 設計方針

- 静的サイトとしてビルドし、GitHub Pages へデプロイできる構成にする
- Astro + TypeScript を使い、ルーティングとコンテンツ表示は単純に保つ
- コンテンツは `src/content/` 以下に置き、表示ロジックと分離する
- `terms` と `topics` を別コレクションとして扱い、将来の再利用と自動生成に備える
- 依存は Astro 本体、TypeScript、サイトマップ生成に絞る

## ディレクトリ構成

```text
.
├── .github/workflows/     # GitHub Pages デプロイ
├── docs/                  # 設計・運用ドキュメント
├── data/                  # 用語生成キュー
├── public/                # 静的アセット
├── scripts/               # 将来の自動生成スクリプト置き場
├── src/
│   ├── components/        # ヘッダー、カードなどの再利用 UI
│   ├── content/
│   │   ├── terms/         # 用語ページ原稿
│   │   └── topics/        # 分野解説ページ原稿
│   ├── layouts/           # 共通レイアウト
│   ├── lib/               # サイト設定・コンテンツ取得処理
│   ├── pages/             # ルーティング
│   └── styles/            # グローバル CSS
├── src/content.config.ts  # コンテンツコレクション定義
└── astro.config.mjs       # Astro / GitHub Pages 設定
```

## コンテンツモデル

### `terms`

1用語1ページの主コレクション。各 Markdown は、AI が量産しやすいように構造化 frontmatter を持つ。

- `slug`: canonical ID。ファイル名と queue の両方で一致させる
- `exam_scope`: 対象試験範囲
- `level`: 基礎 / 標準 / 発展
- `status`: `draft` または `published`
- `category`: 用語領域
- `short_definition`: 一覧・SEO 向けの短い定義
- `definition`: 本文用の定義
- `intuition`: 直感的説明
- `visual_explanation`: 視覚的説明
- `where_it_appears`: どのような場面で現れるか
- `practical_examples`: 現実の例・実務の例
- `exam_points`: 試験で重要なポイント
- `formulas`: 数式と記号
- `rigorous_explanation`: 厳密な説明
- `proof`: 証明の要約
- `common_mistakes`: 間違えやすい点
- `related_terms`: 関連用語の slug
- `references`: 参考文献
- `sort_order`: 一覧順制御

### `topics`

将来の分野解説コレクション。`summary`, `learning_goals`, `sections`, `related_terms` を中心に、複数の用語ページを束ねる。

### `data/term-queue.json`

用語の追加順を管理するキュー。少なくとも次を持つ。

- `slug`
- `title`
- `category`
- `priority`
- `status`: `unstarted`, `draft`, `published`
- `level`
- `exam_scope`
- `prerequisites`
- `related_terms`
- `content_path`

## 画面構成

- `/`: サイトの目的、使い方、公開中コンテンツ数、代表的な用語への導線
- `/terms/`: 用語一覧。主導線
- `/terms/[...slug]/`: 用語詳細。Markdown をレンダリング
- `/topics/`: 分野解説一覧。初期は空ページ
- `/topics/[...slug]/`: 将来の分野解説詳細

## GitHub Pages 対応

- Astro は `output: 'static'` でビルドする
- GitHub Actions は公式 `withastro/action` を使用する
- `site` と `base` は GitHub Pages の URL 形態を前提に設定する
- カスタムドメインを使う場合は `PUBLIC_SITE_URL` と `public/CNAME` を追加する

## 将来の拡張方針

### 1. 用語の自動追加

1時間ごとに 1 用語ずつ追加する運用を想定する。実装方針は以下の通り。

- 原稿生成ロジックは `scripts/` に分離する
- 生成対象の選定は `data/term-queue.json` から行う
- 生成結果は `src/content/terms/` に Markdown として保存する
- 一覧ページはコレクションを読むだけにし、ページ追加時のコード変更を不要にする
- `scripts/validate-term-queue.mjs` で slug と公開状態の最低限の整合性を確認する

### 2. 分野解説の追加

`topics` は、複数の `terms` を束ねた学習導線として使う。たとえば「記述統計の全体像」「確率分布の基本」などを想定する。

### 3. 品質管理

将来は次のチェックをスクリプト化しやすい。

- frontmatter の必須項目チェック
- queue と content の slug 同期チェック
- 用語重複チェック
- 関連用語リンク切れチェック
- 文章テンプレート準拠チェック

## この初期版で意図的にやっていないこと

- CMS 導入
- 重い検索 SaaS 導入
- UI の過度な作り込み
- 複雑なビルドパイプライン

最優先は、保守しやすく、あとから自動追加しやすい土台を先に確定することである。
