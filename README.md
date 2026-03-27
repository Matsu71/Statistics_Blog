# 統計ことばノート

統計検定2級向けの「1用語1ページ」学習用語集サイトです。Astro + TypeScript で構築し、GitHub Pages へ静的デプロイできる構成にしています。

## 特徴

- `src/content/terms/` に用語原稿を置くコンテンツ分離構成
- `terms` と `topics` を分けた、将来拡張しやすいコレクション設計
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

1. `src/content/terms/` に Markdown ファイルを追加する
2. frontmatter に `title`, `description`, `category` を入れる
3. 必要に応じて `aliases`, `tags`, `relatedTerms`, `sortOrder` を設定する
4. `npm run build` で確認する

例:

```md
---
title: 仮説検定
description: 母集団についての仮説をデータから検証する考え方。
category: 推測統計
tags:
  - 検定
  - 推測統計
relatedTerms:
  - p-value
sortOrder: 120
---

## この用語は何か

...
```

### 分野解説ページを追加する

1. `src/content/topics/` に Markdown ファイルを追加する
2. `title`, `description`, `status` などを frontmatter に書く
3. 用語ページへの導線を本文や `relatedTerms` に入れる

## 主なディレクトリ

```text
src/pages/           画面ルーティング
src/layouts/         共通レイアウト
src/components/      UI 部品
src/content/terms/   用語ページ原稿
src/content/topics/  分野解説原稿
src/lib/             サイト設定・取得処理
scripts/             将来の自動生成スクリプト
docs/                設計メモ
public/              静的アセット
```

## 今後の想定

- `scripts/` に用語自動生成スクリプトを置く
- 用語候補リストから未作成のものを 1 件ずつ追加する
- 表記ゆれチェック、リンク切れチェックを自動化する
