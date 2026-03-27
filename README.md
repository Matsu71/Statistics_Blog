# 統計ことばノート

統計検定2級向けの「1用語1ページ」学習用語集サイトです。Astro + TypeScript で構築し、GitHub Pages へ静的デプロイできる構成にしています。

## 特徴

- `src/content/terms/` に用語原稿を置くコンテンツ分離構成
- `terms` と `topics` を分けた、将来拡張しやすいコレクション設計
- `data/term-queue.json` で、公開候補と優先度を機械的に管理
- `docs/editorial-style-guide.md` で、AI 生成時の表記ルールを固定
- GitHub Pages 向けの静的ビルド
- サイトマップ生成に対応
- 依存を最小限にしたシンプルな土台

## 動作環境

- Node.js 20 以上
- npm 10 以上を推奨

## ローカル起動

```bash
npm install
npm run dev
```

ブラウザで `http://localhost:4321` を開く。

## ビルド

```bash
npm run build
npm run preview
npm run validate:term-queue
```

出力先は `dist/`。

## GitHub Pages 公開

1. GitHub にリポジトリを push する
2. GitHub の `Settings > Pages` で `GitHub Actions` を選ぶ
3. `main` ブランチへ push すると `.github/workflows/deploy.yml` が自動デプロイする

### URL 設定

- 通常の GitHub Pages: `site` と `base` は `astro.config.mjs` で GitHub リポジトリ情報から自動計算
- カスタムドメイン利用時: `PUBLIC_SITE_URL` を設定し、必要なら `public/CNAME` を追加

## コンテンツ追加フロー

### 用語ページを追加する

1. `data/term-queue.json` の対象語を確認し、次に追加する slug を決める
2. `docs/editorial-style-guide.md` に従って `src/content/terms/` に Markdown を追加する
3. frontmatter に schema 必須項目を入れる
4. `status` を `draft` か `published` に設定する
5. `npm run validate:term-queue` と `npm run build` で確認する

例:

```md
---
title: 仮説検定
slug: hypothesis-testing
exam_scope:
  - statistics_grade_2
level: standard
status: draft
category: hypothesis_testing
short_definition: 母集団についての仮説をデータから検討する考え方です。
definition: 標本から得られた情報を使って、帰無仮説を棄却するかどうかを判断する手続きです。
intuition:
  - データを見て、最初の仮説をそのまま採用してよいか確かめる作業と考えます。
where_it_appears:
  - 推定のあとに、仮説が妥当かを検討するとき
exam_points:
  - 帰無仮説、対立仮説、p値、有意水準の関係を整理することが重要です。
related_terms:
  - p-value
  - significance-level
references: []
updated_at: 2026-03-27
---

...
```

### 分野解説ページを追加する

1. `src/content/topics/` に Markdown ファイルを追加する
2. `summary`, `learning_goals`, `related_terms`, `status` などを frontmatter に書く
3. 用語ページへの導線を `related_terms` と `sections` に入れる

## 主なディレクトリ

```text
src/pages/           画面ルーティング
src/layouts/         共通レイアウト
src/components/      UI 部品
src/content/terms/   用語ページ原稿
src/content/topics/  分野解説原稿
data/term-queue.json 用語の優先キュー
src/lib/             サイト設定・取得処理
scripts/             将来の自動生成スクリプト
docs/                設計メモ
public/              静的アセット
```

## 今後の想定

- `scripts/` に用語自動生成スクリプトを置く
- `data/term-queue.json` から未着手のものを 1 件ずつ追加する
- 表記ゆれチェック、リンク切れチェックを自動化する
