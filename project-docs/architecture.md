# Architecture

## 目的

このサイトは、統計検定2級を主対象にした「1用語1ページ」の学習用語集を GitHub Pages で継続公開するための土台です。

## 設計方針

- 静的サイトとしてビルドし、`docs/` を GitHub Pages に公開する
- Astro + TypeScript を使い、表示ロジックは単純に保つ
- コンテンツは `src/content/` 以下に置き、表示ロジックと分離する
- repo 内の運用文書は `project-docs/` に置き、公開物とは分ける
- build と validation はローカルまたは Codex 実行で行う

## ディレクトリ構成

```text
.
├── project-docs/          # 設計・運用ドキュメント
├── docs/                  # GitHub Pages 公開物
├── data/                  # 用語生成キュー
├── public/                # 静的アセット
├── scripts/               # 生成・検証スクリプト
├── src/
│   ├── components/        # 再利用 UI
│   ├── content/
│   │   ├── terms/         # 用語ページ原稿
│   │   └── topics/        # 分野解説ページ原稿
│   ├── layouts/           # 共通レイアウト
│   ├── lib/               # サイト設定・コンテンツ取得処理
│   ├── pages/             # ルーティング
│   └── styles/            # グローバル CSS
├── src/content.config.ts  # コンテンツコレクション定義
├── astro.config.mjs       # Astro 設定
└── site-build.config.mjs  # GitHub Pages 向けの site/base/build 出力設定
```

## 画面構成

- `/`: 最小限の導線
- `/terms/`: 用語一覧
- `/terms/[...slug]/`: 用語詳細
- `/topics/`: 分野解説一覧
- `/topics/[...slug]/`: 分野解説詳細

ホームや一覧はシンプルに保ち、内容の厚みは詳細ページへ寄せます。

## 数式表示

- 数式は画像化せず、KaTeX によるテキストベースの静的レンダリングを標準にする
- Markdown 本文の数式は `astro.config.mjs` の `remark-math` / `rehype-katex` で処理する
- frontmatter の `formulas[].latex` は `src/lib/math.ts` と `FormulaCard` で HTML+MathML にレンダリングする
- frontmatter の説明文中の短い記号や式は `MathText` で inline math として表示する
- display 数式は `global.css` の `.formula-block` / `.katex-display` のカード風スタイルを維持する
- 長い式は数式ブロック内だけ横スクロールさせ、ページ全体を横に広げない
- 数式 UI を変更した回は、`normal-distribution`、`random-sampling`、`variance`、`sample-mean`、`range` を代表ページとして確認する

## GitHub Pages 対応

- Astro は `output: 'static'` でビルドする
- build 出力先は `docs/`
- GitHub Pages は `Deploy from a branch / main /docs` を使う
- `site` と `base` は `site-build.config.mjs` で管理する
- カスタムドメインを使う場合は `PUBLIC_SITE_URL` と `PUBLIC_BASE_PATH=/` を追加する

## 将来の拡張方針

- `data/term-queue.json` から未着手用語を 1 件ずつ追加する
- `scripts/` の CLI を Codex Automation から呼びやすく保つ
- 追加後は `docs/` まで更新して commit / push する
