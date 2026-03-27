# scripts ディレクトリ

Codex Automation や手動運用から呼べるように、用語追加パイプライン用の CLI を置いています。

## 主なコマンド

- `npm run pick:next-term`
  - queue から次に着手すべき未着手用語を 1 件選びます。
- `npm run scaffold:term -- --slug=<slug>`
  - queue 項目から `src/content/terms/<slug>.md` の安全な draft 雛形を作ります。
- `npm run validate:term-queue`
  - queue の語彙・path・status と実ファイルの最低限の整合を検査します。
- `npm run validate:content`
  - queue と content の cross-check、必須 frontmatter、関連語、編集ガイド由来 warning を検査します。
- `npm run generate:index`
  - `src/generated/term-index.json` を再生成し、ホームと用語一覧の導線データを更新します。

## 実装方針

- queue の正本は `data/term-queue.json`
- content の正本は `src/content/terms/*.md`
- 生成物の正本は `src/generated/term-index.json` ではなく、常に queue と content
- 共通ロジックは `scripts/lib/term-pipeline.mjs` に寄せ、コマンドごとの判定差を避けます
