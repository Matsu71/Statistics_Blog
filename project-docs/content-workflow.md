# Content Workflow

## 目的

この文書は、新しい用語ページを 1 件追加し、`docs/` まで更新して公開できる状態にする標準手順をまとめたものです。

## 最初に見るファイル

1. `README.md`
2. `data/term-queue.json`
3. `src/content.config.ts`
4. `project-docs/editorial-style-guide.md`
5. `AGENTS.md`

## 前提環境

- Node.js 20 以上
- npm 10 以上
- 依存インストール済み

```bash
npm install
```

## コマンド早見表

```bash
npm run pick:next-term
npm run scaffold:term -- --slug=<slug>
npm run generate:index
npm run validate
npm run lint
npm run typecheck
npm run build
npm run validate:links
```

## 標準フロー

### Step 1. 次の用語を決める

```bash
npm run pick:next-term
```

### Step 2. 雛形を作る

```bash
npm run scaffold:term -- --slug=<slug>
```

成功すると次が起きます。

- `src/content/terms/<slug>.md` が作られる
- queue の対象項目が `draft` になる
- queue の `content_path` が設定される

### Step 3. 下書きを埋める

- `project-docs/editorial-style-guide.md`
- `AGENTS.md`
- `.agents/skills/term-page-generator/SKILL.md`

に従って内容を埋めます。

### Step 4. 一覧データを再生成する

```bash
npm run generate:index
```

### Step 5. content を検査する

```bash
npm run validate
```

### Step 6. UI 側も含めて確認する

```bash
npm run lint
npm run typecheck
```

### Step 7. 公開物を更新する

```bash
npm run build
npm run validate:links
```

`npm run build` の出力先は `docs/` です。`docs/index.html` が生成されることを確認します。

### Step 8. commit / push する

```bash
git add src data project-docs docs
git commit -m "Add <slug> term page"
git push origin main
```

## エラー時の見方

`npm run validate`
- queue / content / generated index の不整合を直します

`npm run lint`
- `README.md`、`project-docs/`、`src/content/` のリンクを直します

`npm run typecheck`
- Astro / TypeScript のエラー位置を直します

`npm run build`
- `docs/` 出力が壊れる原因を直します

`npm run validate:links`
- `docs/**/*.html` の壊れたリンクや一覧未反映を直します

## Done の定義

新しい用語追加が完了扱いになる最低条件は次です。

- queue と content の slug / status / path が整合している
- `src/generated/term-index.json` が再生成済み
- `npm run validate` が通る
- `npm run lint` が通る
- `npm run typecheck` が通る
- `npm run build` が通る
- `npm run validate:links` が通る
- `docs/index.html` と `docs/terms/index.html` が更新されている
- commit と push が完了している

## Git 運用ルール

- この repo では、変更を加えたら原則としてそのターン内で commit / push まで行います。
- 用語追加だけでなく、設定変更、UI 変更、運用文書変更でも同じです。
- `docs/` が更新された回は、source と `docs/` を分けずに一緒に commit / push します。
- ユーザーが明示的に止めた場合だけ、未 push のまま終えてよいものとします。
