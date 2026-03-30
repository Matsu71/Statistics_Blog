# Automation Plan

## Goal

このリポジトリでは、将来的に 1 時間ごとに 1 用語ページを安定して追加または拡充できる自動運用を目指します。ただし、最優先は更新頻度ではなく品質です。

## Current Canonical Inputs

- 用語 schema: `src/content.config.ts`
- 用語キュー: `data/term-queue.json`
- 作成 Skill: `.agents/skills/term-page-generator/SKILL.md`
- 運用フロー: `project-docs/content-workflow.md`

## Hourly Run Workflow

1. `AGENTS.md`、Skill、schema、queue、近い既存ページを読む
2. `npm run pick:next-term` で次の 1 件を選ぶ
3. `npm run scaffold:term -- --slug=<slug>` で安全な下書きを作る
4. 親 agent が必要な役割の subagent を立てて内容を統合する
5. `npm run generate:index` を実行する
6. `npm run validate` を実行する
7. `npm run lint` と `npm run typecheck` を実行する
8. `npm run build` を実行し、`docs/` を更新する
9. `npm run validate:links` を実行する
10. source と `docs/` を一緒に commit / push する

## Quality Gates

自動実行で push に進める条件は次です。

- frontmatter が `src/content.config.ts` と整合している
- 必須 content block が揃っている
- 少なくとも 1 つの具体例がある
- `related_terms` が既存 slug のみで構成されている
- `TODO:` / `保留:` が publishable 内容に残っていない
- `npm run validate` が通る
- `npm run lint` が通る
- `npm run typecheck` が通る
- `npm run build` が通る
- `npm run validate:links` が通る
- `docs/index.html` が生成されている

## Failure Handling

次のどれかに当てはまる場合は、その回を失敗扱いにします。

- subagent を必要数だけ立てられなかった
- `pick:next-term` が候補を返せなかった
- validation または build が通らない
- `docs/` を安全に更新できなかった
- 公開品質に届かない内容が残った

失敗時の原則:

- 無理に push しない
- 必要なら `status: draft` のまま止める
- queue に別 status を書き足さない
- 再実行時に原因を追えるよう、ログや commit message の下書きに理由を残す

## Publish Model

- GitHub Pages は `main` ブランチの `/docs` を配信する
- GitHub Actions はビルドにもデプロイにも使わない
- 公開は `docs/` を含む commit が `main` に push された時点で反映される

## Open Questions

- `status: draft` の term をどこまで automation が自動更新してよいか
- direct push を常用するか、別 branch で build してから `main` へ反映するか
- 数学的裏取りメモの保存場所をどこにするか
- repo-local の `.codex/config.toml` を安全に使えるか
