# Automation Plan

## Goal

このリポジトリでは、将来的に 1 時間ごとに 1 用語ページを安定して追加または拡充できる自動運用を目指します。ただし、最優先は更新頻度ではなく品質です。

この設計の前提は次です。

- 1 回の自動実行で扱う用語は 1 件だけ
- 多エージェント分担は必須
- 数学的事実を推測で埋めない
- publishable 品質に届かない回は公開しない

## Current Canonical Inputs

automation は、次を正本として扱います。

- 用語 schema: `src/content.config.ts`
- 用語キュー: `data/term-queue.json`
- 作成 Skill: `.agents/skills/term-page-generator/SKILL.md`
- 運用フロー: `docs/content-workflow.md`

将来の automation でも、別の queue file や独自 status vocab を増やさず、まずはこの repo の現行 CLI と同じ前提を使います。

## Queue Model

現在の canonical queue は `data/term-queue.json` です。

主なフィールド:

- `slug`
- `title`
- `category`
- `priority`
- `status`
- `level`
- `exam_scope`
- `prerequisites`
- `related_terms`
- `content_path`

status 語彙:

- `unstarted`
- `draft`
- `published`

automation は `pending`、`in_progress`、`blocked`、`done` のような別語彙を queue に書き込みません。block 理由や実行メモは、automation のログ、inbox、PR 説明、または将来の別ファイルで管理します。

## Hourly Run Workflow

1. `AGENTS.md`、`.agents/skills/term-page-generator/SKILL.md`、`src/content.config.ts`、`data/term-queue.json`、近い既存ページを読む。
2. `npm run pick:next-term` で、`status = unstarted` の中から前提条件を満たす用語を 1 件だけ選ぶ。
3. `npm run scaffold:term -- --slug=<slug>` で、queue 項目から `src/content/terms/<slug>.md` の安全な下書きを作る。
4. 親 agent が固定 6 役割の subagent を並列起動する。
5. 親 agent は全 subagent の結果を待ってから 1 本の Markdown に統合する。
6. 用語ページを `AGENTS.md` と Skill の基準に合わせて仕上げる。publishable に届かない場合は `status: draft` を維持する。
7. `npm run generate:index` で一覧データを再生成する。
8. `npm run validate:term-queue` と `npm run validate:content` を実行する。
9. `npm run build` を実行する。schema、型、UI を触った回は `npm run check` も実行する。
10. build / validation を通過したら、`codex/term-<slug>` ブランチで Draft PR を作る。
11. 人手レビューまたは将来の昇格フローで publishable と判断された場合のみ、`status: published` へ進める。

## Required Multi-Agent Roles

自動実行でも、次の役割を省略しません。

- 基本説明担当
- 直感・イメージ担当
- 実例担当
- 数学的厳密説明担当
- 編集統合担当
- 品質チェック担当

ルール:

- 親 agent は全 subagent の結果が揃う前に統合しない
- subagent を十分に立てられない実行は成功扱いにしない
- 品質チェック担当が不合格とした場合、その回は公開しない

## Quality Gates

自動実行で publishable に進める条件は次です。

- frontmatter が `src/content.config.ts` と整合している
- 必須 content block が揃っている
- 少なくとも 1 つの具体例がある
- 数式を使う場合、記号の意味が説明されている
- 数学的に不確かな断定がない
- `related_terms` が既存 slug のみで構成されている
- `TODO:` / `保留:` が残っていない
- `status` は `published` である
- `src/generated/term-index.json` が再生成済みである
- `npm run validate:term-queue`、`npm run validate:content`、`npm run build` が通る
- schema / UI 変更を伴う場合は `npm run check` も通る

publishable に届かないが安全に保存できる条件は次です。

- frontmatter と必須 content block が揃っている
- 不確かな箇所が `TODO:` / `保留:` で理由つきに分離されている
- 不確かな内容を断定していない
- `status` は `draft` である
- repo に保存するなら `npm run generate:index`、`npm run validate:term-queue`、`npm run validate:content`、`npm run build` が通る

## Failure Handling

次のどれかに当てはまる場合は、その回を失敗扱いにします。

- subagent を必要数だけ立てられなかった
- `pick:next-term` が候補を返せなかった
- 同じ slug の既存ファイルがあり、scaffold できなかった
- validation または build が通らない
- `related_terms` が未作成 slug を含む
- 数学的に不確かな内容が publishable 本文に残る
- 重要な block が安全に書けない

失敗時の原則:

- 無理に公開しない
- 内容が未確定なら `status: draft` のまま止める
- queue に別 status を書き足さない
- 再実行時に原因を追えるよう、automation のログか PR に理由を残す

## Re-Run Safety

再実行で重複生成や衝突を起こさないため、次を守ります。

- 1 回の実行で 1 用語だけ扱う
- `pick:next-term` の決定規則を変えない
- `scaffold:term` は既存ファイルを上書きしない
- `generate:index` は queue / content から再計算する
- `validate:content` で queue / content / generated index の不整合を止める
- 同一 slug のブランチや PR があれば新規作成より再利用を優先する

## Review And Publish Policy

初期運用では、automation が直接 `main` を更新しない方針にします。

- Phase 1: `pick`、`scaffold`、原稿更新、validation、Draft PR まで
- Phase 2: 人手レビュー後に merge
- Phase 3: publish 昇格を自動化するなら、専用の status 更新フローを追加してから再検討

理由:

- 現在の GitHub Pages デプロイは `main` push で即公開される
- この repo では数学的正確性の事故コストが高い
- 現時点の CLI は下書き生成と検証までは揃っているが、公開昇格は慎重に扱うべきである

## Open Questions

- `status: draft` の term をどこまで automation が自動更新してよいか
- `published` への昇格を手動レビュー後に行うか、将来スクリプト化するか
- block 理由の保存先を repo 内ファイルにするか、PR 側に寄せるか
- 数学的裏取りメモの保存場所をどこにするか
- repo-local の `.codex/config.toml` を安全に使えるか
