# Deployment

## Overview

この repo では、GitHub Pages 公開と CI 品質ゲートを分けて運用します。

- `.github/workflows/ci.yml`
  - PR と `main` 以外の branch push で実行
  - 公開はしない
  - quality gate 専用
- `.github/workflows/deploy.yml`
  - `main` push と `workflow_dispatch` で実行
  - quality gate を再実行したうえで Pages artifact を作り、GitHub Pages へデプロイする

公開前に止まる場所を明確にするため、workflow は stage を分けています。

## CI Flow

CI は次の順で止まります。

1. `01-content-validation`
2. `02-site-quality`
3. `03-build-site`

各 stage の中身は次です。

### 1. `01-content-validation`

```bash
npm run validate:term-queue
npm run validate:content -- --strict
```

ここで止まる例:

- タイトル未設定
- slug 重複
- 必須項目不足
- frontmatter と queue の不整合
- 関連用語が queue に存在しない
- `published` なのに `TODO:` / `保留:` が残っている
- `src/generated/term-index.json` が未更新で、一覧に反映されていない
- warning 扱いの内容品質問題が `--strict` により fail になる

### 2. `02-site-quality`

```bash
npm run lint
npm run typecheck
```

`npm run lint` は `scripts/lint-repo.mjs` を実行し、次を確認します。

- `README.md` と `docs/**/*.md` の相対リンク切れ
- `src/content/**/*.md` 本文中の内部リンク切れ
- `/terms/<slug>/` や `/topics/<slug>/` が未公開ページを向いていないか
- `public/` 配下に存在しない静的 asset を参照していないか

`npm run typecheck` は Astro / TypeScript の型エラーとテンプレート上の不整合を止めます。

### 3. `03-build-site`

```bash
npm run build
npm run validate:links
```

ここでは次を止めます。

- 静的ビルド失敗
- build 後 HTML の内部リンク切れ
- asset 参照切れ
- `dist/terms/index.html` に published term が反映されていない状態

## Deploy Flow

`deploy.yml` は次の流れです。

1. `01-content-validation`
2. `02-site-quality`
3. `03-build-site`
4. `04-deploy-pages`

`04-deploy-pages` は `03-build-site` が作った `dist/` artifact を `actions/deploy-pages` で公開します。content 起因の失敗は deploy job に持ち込まず、その前段で止める構成です。

## GitHub Settings

最低限、GitHub 側で次を確認します。

1. `Settings > Pages` を開く
2. Source を `GitHub Actions` にする
3. Actions が Pages へ deploy できる権限を持っていることを確認する

repo の `astro.config.mjs` は、`GITHUB_REPOSITORY` と `GITHUB_REPOSITORY_OWNER` から `site` と `base` を計算します。通常の GitHub Pages では追加設定なしで動きます。

カスタムドメインを使う場合:

- `PUBLIC_SITE_URL` を設定する
- 必要なら `public/CNAME` を追加する

## Local Reproduction

CI と同じ順でローカル確認する場合は次です。

```bash
npm install
npm run generate:index
npm run validate:term-queue
npm run validate:content -- --strict
npm run lint
npm run typecheck
npm run build
npm run validate:links
```

一括なら次でもよいです。

```bash
npm run generate:index
npm run ci
```

## Stop Points And Where To Look

### `lint` で止まったとき

- まず `scripts/lint-repo.mjs` のメッセージを見る
- 対象が `README.md` / `docs/` か `src/content/` かを確認する
- 未公開 slug へのリンクや相対パスの打ち間違いを直す

### `typecheck` で止まったとき

- `astro check` の対象ファイルと行番号を見る
- Astro component の props、JSON import、`undefined` の扱いを確認する

### `content-validation` で止まったとき

- `data/term-queue.json`
- `src/content/terms/<slug>.md`
- `src/generated/term-index.json`

この 3 つの整合を最初に見ると早いです。

### `build-site` で止まったとき

- Astro page と component の render 破綻を疑う
- 直前の `typecheck` と `content-validation` を再確認する
- `dist/` を作る前提の asset や import が壊れていないかを見る
- `npm run validate:links` の出力に出た `dist/...` と `src/generated/term-index.json` を見る

### `deploy-pages` で止まったとき

- GitHub Pages の Source 設定
- workflow permissions
- `actions/deploy-pages` の job log

を確認します。

## Auto-Generated Pages Notes

1時間ごとの追加実行前に、最低限次を通る状態にします。

- `npm run generate:index`
- `npm run validate:term-queue`
- `npm run validate:content -- --strict`
- `npm run lint`
- `npm run typecheck`
- `npm run build`
- `npm run validate:links`

`validate:content` は generated index の鮮度も見ているため、一覧未反映のまま `main` に入るのを防げます。
