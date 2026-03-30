# Codex Config Proposal

## Decision

2026-03-27 時点では、repo-local の `.codex/config.toml` は作成していません。

## Why It Was Not Created

- 現在この環境で確認できた Codex CLI の help は、設定ファイルとして `~/.codex/config.toml` を明示しています。
- 手元のグローバル設定ファイルから、有効な TOML のキー構文自体は確認できました。
- ただし、repo 直下の `.codex/config.toml` が正式に読み込まれるかは、この環境だけでは確認できませんでした。
- この repo では「構文や挙動に確信が持てない場合は推測で書かない」ことを優先するため、未確認の repo-local 設定は追加していません。

## Confirmed Valid Syntax Observed In Global Config

次のようなキー構文は、少なくともグローバル設定では有効な形として確認できました。

```toml
model = "gpt-5.4"
model_reasoning_effort = "xhigh"

[features]
multi_agent = true
```

## Candidate Repo-Local Config

もし将来、repo-local の `.codex/config.toml` が正式サポートされていることを確認できた場合は、まずは次の最小構成から始めるのが安全です。

```toml
model_reasoning_effort = "high"

[features]
multi_agent = true
```

## Why This Candidate

- `multi_agent = true` は、この repo の最重要ルールである「複数 subagent を必ず立てる」方針と一致します。
- `model_reasoning_effort = "high"` は、コストより品質を優先する方針と整合します。
- それ以外のキーは、repo-local 読み込み可否が確認できてから追加した方が安全です。

## Next Step

repo-local config の正式サポートが確認できたら、`.codex/config.toml` を追加し、まずは Skill 作成や用語ページ作成のワークフローで挙動を burn-in します。
