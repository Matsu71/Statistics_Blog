# Deployment

## Overview

この repo では、GitHub Actions を使ってビルドやデプロイをしません。

- 静的サイトはローカルまたは Codex 実行でビルドします
- build 成果物は `docs/` に出力します
- `main` ブランチへ `docs/` を commit / push し、GitHub Pages は branch deploy で公開します

## GitHub Settings

GitHub 側では次を手動で設定します。

1. `Settings > Pages` を開く
2. `Source` で `Deploy from a branch` を選ぶ
3. `Branch` で `main` を選ぶ
4. `Folder` で `/docs` を選ぶ
5. 保存する

この変更は repo のファイル編集だけでは確実に反映できないため、必ず人手で確認してください。

## Build And Publish Flow

標準手順は次です。

```bash
npm install
npm run generate:index
npm run validate
npm run lint
npm run typecheck
npm run build
npm run validate:links
```

その後、source の変更と `docs/` を一緒に commit / push します。

```bash
git add src data scripts project-docs docs package.json astro.config.mjs site-build.config.mjs
git commit -m "Update content and rebuild site"
git push origin main
```

push 後は GitHub Pages が `main/docs` をそのまま配信します。

## Output Location

- build 出力先: `docs/`
- Pages のトップ: `docs/index.html`
- 用語一覧: `docs/terms/index.html`

`npm run build` 後に `docs/index.html` が無い場合は、公開処理に進みません。

## Stop Points

### `npm run validate`

- queue と content の不整合
- frontmatter の必須項目不足
- 旧キーや不正な関連語
- `src/generated/term-index.json` 未更新

最初に見る場所:

- `data/term-queue.json`
- `src/content/terms/<slug>.md`
- `src/generated/term-index.json`

### `npm run lint`

- `README.md`
- `project-docs/**/*.md`
- `src/content/**/*.md`

のリンク切れや未公開ページ向きリンクを止めます。

### `npm run typecheck`

- Astro / TypeScript の型エラー
- component props や template 上の不整合

### `npm run build`

- 静的ビルド失敗
- import / route / asset 破綻
- `docs/` 生成失敗

### `npm run validate:links`

- build 後の `docs/**/*.html` の内部リンク切れ
- `docs/terms/index.html` に published term が未反映の状態

最初に見る場所:

- `docs/**/*.html`
- `src/pages/**`
- `src/content/**`
- `src/generated/term-index.json`

### GitHub Pages で公開されないとき

最初に確認する項目:

1. `Settings > Pages` が `Deploy from a branch / main /docs` になっているか
2. `main` に `docs/index.html` が push されているか
3. `site-build.config.mjs` の `defaultSiteUrl` と `defaultBasePath` が repo の実態と合っているか

## URL Settings

- 通常の GitHub Pages は `site-build.config.mjs` の既定値で動かします
- カスタムドメイン利用時は `PUBLIC_SITE_URL` と `PUBLIC_BASE_PATH=/` を設定します
- 必要なら `public/CNAME` を追加します

## Notes For Automation

1時間ごとの自動実行では、少なくとも次を行います。

1. 用語ページを追加または更新する
2. `npm run generate:index`
3. `npm run validate`
4. `npm run lint`
5. `npm run typecheck`
6. `npm run build`
7. `npm run validate:links`
8. `docs/` を含めて commit / push する

Actions は介在しない前提です。
