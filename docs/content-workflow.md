# Content Workflow

## 目的

この文書は、この repo で新しい用語ページを 1 件追加し、一覧データと validation を通したうえで公開候補にするまでの標準手順をまとめたものです。

対象は次の人です。

- 新しく参加した人
- Codex Automation を組む人
- queue と content の整合を壊さずに更新したい人

## 最初に見るファイル

1. `README.md`
2. `data/term-queue.json`
3. `src/content.config.ts`
4. `docs/editorial-style-guide.md`
5. `AGENTS.md`

この順で見ると、「何を作る repo か」「queue が何を正とするか」「schema は何か」「文体と禁止事項は何か」が短時間で分かります。

## 前提環境

- Node.js 20 以上
- npm 10 以上
- 依存インストール済み

```bash
npm install
```

この repo の `build` と `check` は、Automation や sandbox で失敗しにくいように `ASTRO_TELEMETRY_DISABLED=1` を付けています。

## コマンド早見表

```bash
npm run pick:next-term
npm run scaffold:term -- --slug=<slug>
npm run generate:index
npm run validate:term-queue
npm run validate:content
npm run build
```

### 1. `npm run pick:next-term`

- 次に着手すべき未着手用語を 1 件だけ選びます。
- `priority` と `prerequisites` を見て、今扱ってよい候補だけを返します。
- queue や content に破綻がある場合は、選定せずに止まります。

### 2. `npm run scaffold:term -- --slug=<slug>`

- queue 項目から `src/content/terms/<slug>.md` の雛形を作ります。
- 生成されるページは必ず `status: draft` です。
- schema 必須項目は `TODO:` 付きの安全文で埋めます。
- 既存ファイルは上書きしません。

例:

```bash
npm run scaffold:term -- --slug=population
```

### 3. `npm run generate:index`

- `src/generated/term-index.json` を再生成します。
- ホームと用語一覧はこの生成物を読むため、新規ページ追加後は必ず実行します。
- source of truth は queue と content であり、生成物はキャッシュ兼表示用スナップショットです。

### 4. `npm run validate:term-queue`

- queue の語彙、重複 slug、`content_path`、`status` と実ファイルの最低限の同期を確認します。
- まず軽量に整合を見たいときの入口です。

### 5. `npm run validate:content`

- queue と content の cross-check をまとめて行います。
- 必須 frontmatter、`slug` 一致、`status` 一致、`related_terms`、構造化配列、編集ガイド由来 warning まで見ます。
- 公開前の主検査はこれです。

### 6. `npm run build`

- 最終確認です。
- `generate:index` と validation を通過したあとに実行します。

## 標準フロー

### Step 1. 次の用語を決める

```bash
npm run pick:next-term
```

このコマンドは queue を更新しません。選定だけを行います。

### Step 2. 雛形を作る

```bash
npm run scaffold:term -- --slug=<slug>
```

成功すると次が起きます。

- `src/content/terms/<slug>.md` が作られる
- queue の対象項目が `draft` になる
- queue の `content_path` が設定される

### Step 3. 下書きを埋める

生成された Markdown を開き、`TODO:` を実内容に置き換えます。

特に次は必須です。

- `short_definition`
- `definition`
- `intuition`
- `where_it_appears`
- `exam_points`

必要に応じて次を足します。

- `visual_explanation`
- `practical_examples`
- `formulas`
- `rigorous_explanation`
- `common_mistakes`
- `references`

### Step 4. 一覧データを再生成する

```bash
npm run generate:index
```

### Step 5. 検査する

```bash
npm run validate:term-queue
npm run validate:content
```

### Step 6. ビルド確認する

```bash
npm run build
```

## エラー時の見方

エラーメッセージは次の形を基本にしています。

- 何が壊れたか
- どの slug / file か
- 何を期待していたか
- どう直すか

例:

```text
src/content/terms/median.md: status mismatch for "median". queue="published", content="draft".
Next step: align the queue status or the frontmatter status before building.
```

### よくある失敗と直し方

`Queue entry missing for content file ...`
- content file はあるが queue に slug が無い状態です。
- `data/term-queue.json` に項目を追加するか、不要ファイルなら削除します。

`Content file missing for queue item ...`
- queue では `draft` または `published` なのに Markdown が無い状態です。
- scaffold し直すか、queue の status を見直します。

`Slug mismatch ...`
- ファイル名、frontmatter、queue の slug が一致していません。
- canonical ID は queue の slug です。そこへ揃えます。

`related_terms includes ... but that slug is not in the queue`
- 関連語が queue 未登録です。
- queue へ追加するか、誤記なら修正します。

`published content must not contain TODO/保留 markers`
- 公開状態のページに未確定事項が残っています。
- TODO を解消するか、`status: draft` に戻します。

## Automation で使うときのルール

- 1 回の実行で扱う用語は 1 件だけにする
- `pick:next-term` の結果をそのまま `scaffold:term` に渡す
- `generate:index` を content 追加後に必ず実行する
- `validate:content` が落ちたら公開処理に進まない
- `main` 直 push ではなく branch + Draft PR を前提にする
- 既存ファイルを上書きしない

推奨順:

```bash
npm run pick:next-term
npm run scaffold:term -- --slug=<slug>
npm run generate:index
npm run validate:term-queue
npm run validate:content
npm run build
```

## Done の定義

新しい用語追加が完了扱いになる最低条件は次です。

- queue と content の slug / status / path が整合している
- `src/generated/term-index.json` が再生成済み
- `npm run validate:term-queue` が通る
- `npm run validate:content` が通る
- `npm run build` が通る
