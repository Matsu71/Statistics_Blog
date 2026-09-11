<!-- FOUNDATION_RELEASE_20260911 -->
## 統計の基礎コース（2026-09-11）

4級・3級の内容を統合した **基礎 → 2級 → 準1級 → 1級** の学習構成へ拡張しています。基礎コースの初期構成は8章・40講座。最初の6講座・確認問題18問を実装し、残りの講座は準備中として区別しています。

[基礎コース](https://Matsu71.github.io/Statistics_Blog/courses/foundation/) · [講座の構成・品質基準](project-docs/learning-platform-design/09-foundation-course.md) · [講座原稿](src/content/lessons/)

基本説明は常時表示し、詳しい説明と解答は開閉できます。講座の前後移動、目次、証明等への直接リンク、印刷時の展開に対応します。確認問題は自分で考えて解答を開く形式で、自動採点や学習履歴保存はまだ実装していません。

検証は `npm run generate:index && npm run verify && node scripts/validate-foundation.mjs` で行います。ブラウザ検証はPlaywright/Chromiumを用い、staging用ワークフローで実行します。検証結果は [初期リリースの検証記録](project-docs/learning-platform-design/10-foundation-validation.json) を参照してください。

以下の「次期設計・未実装」は初期設計時点の記録です。現在の実装範囲は上記と09の仕様を優先します。既存の用語ページ・URLは維持しています。

---

# 統計ラボ

統計の用語、考え方、数式、試験ポイントを整理する学習サイトです。Astro + TypeScript で構築し、静的サイトを `docs/` にビルドして GitHub Pages で公開します。

## 次期学習サイトの設計（2026-09-11）

初学者から上級者まで、統計検定4級〜1級を軸に学べるサイトへの拡張設計を [project-docs/learning-platform-design/README.md](project-docs/learning-platform-design/README.md) にまとめています。

既存サービス調査、級別ロードマップ、24分野・307学習単位の候補、基本と証明を分けたページ仕様、正規分布の具体的な見本、実装・品質管理の計画を含みます。設計資料であり、新UIや全教材の実装・公開が完了したものではありません。以下は現在の実装・運用方法です。

## 特徴

- `src/content/terms/` に用語原稿を置くコンテンツ分離構成
- `terms` と `topics` を分けた、将来拡張しやすいコレクション設計
- `data/term-queue.json` で、公開候補と優先度を機械的に管理
- `project-docs/editorial-style-guide.md` で、AI 生成時の表記ルールを固定
- build 成果物を `docs/` に置き、`main` ブランチの `/docs` を GitHub Pages 公開元にする運用
- content validation、repo lint、typecheck、build、内部リンク検証をローカルまたは Codex 実行で回せる構成
- サイトマップ生成に対応

## 動作環境

- Node.js 20 以上
- npm 10 以上を推奨

## ローカル起動

```bash
npm install
npm run dev
```

ブラウザで `http://localhost:4321` を開きます。

## 検証とビルド

```bash
npm run generate:index
npm run validate
npm run lint
npm run typecheck
npm run build
npm run validate:links
npm run preview
```

- `npm run build` の出力先は `docs/` です。
- `src/content/terms/` や `data/term-queue.json` を触った回は、先に `npm run generate:index` を実行します。
- 一括確認は `npm run verify` を使います。

## GitHub Pages 公開

1. ローカルまたは Codex 実行で `npm run build` を実行して `docs/` を更新する
2. 生成された `docs/` を source 変更と一緒に commit / push する
3. GitHub Pages は `main` ブランチの `/docs` をそのまま公開する

GitHub 側で必要な設定と停止箇所は [project-docs/deployment.md](project-docs/deployment.md) を参照してください。

### URL 設定

- 通常の GitHub Pages: `site-build.config.mjs` の既定値を使う
- カスタムドメイン利用時: `PUBLIC_SITE_URL` と `PUBLIC_BASE_PATH=/` を設定し、必要なら `public/CNAME` を追加する

## コンテンツ追加フロー

### 用語ページを追加する

1. `npm run pick:next-term` で候補を確認する
2. `npm run scaffold:term -- --slug=<slug>` で安全な下書きを作る
3. `project-docs/editorial-style-guide.md` に従って `src/content/terms/` の内容を埋める
4. `npm run generate:index` を実行する
5. `npm run verify` を実行する
6. `docs/` を含めて commit / push する

詳細な標準手順は [project-docs/content-workflow.md](project-docs/content-workflow.md) を参照してください。

### 分野解説ページを追加する

1. `src/content/topics/` に Markdown ファイルを追加する
2. `summary`, `learning_goals`, `related_terms`, `status` などを frontmatter に書く
3. 用語ページへの導線を `related_terms` と `sections` に入れる
4. `npm run build` で `docs/` を更新する

## 主なディレクトリ

```text
src/pages/              画面ルーティング
src/layouts/            共通レイアウト
src/components/         UI 部品
src/content/terms/      用語ページ原稿
src/content/topics/     分野解説原稿
data/term-queue.json    用語の優先キュー
src/lib/                サイト設定・取得処理
scripts/                生成・検証・lint 用の CLI
project-docs/           設計・運用ドキュメント
docs/                   GitHub Pages 公開物
public/                 静的アセット
```
