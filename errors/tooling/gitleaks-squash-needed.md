---
title: "gitleaks が修正済みコミットの旧 API キーを検出する — squash が必要"
tags: [gitleaks, git, security, ci]
severity: medium
source: personal
date: "2026-08-08"
---

## 症状

PR に「①キーをハードコード」「②env var に修正」の 2 コミットが含まれると、
gitleaks が ① の diff を検出して fail する（② で修正済みでも）。

```
Finding: EMBED_KEY = "REDACTED"
RuleID:  generic-api-key
Commit:  f7bd204...
```

## 原因

gitleaks は PR 範囲の全コミット diff をスキャンする。
最終的なファイルにキーが残っていなくても、git 履歴の diff に含まれていれば検出される。

## 解決策

2 コミットを squash して force push（feature ブランチのみ）:

```bash
git reset HEAD~2          # soft reset（変更は unstaged に残る）
git add <files>
git commit -m "feat: ..." # キーが入っていない最終状態で 1 コミット
git push --force-with-lease origin <branch>
```

`git push --force*` は settings.json deny 設定のため Claude Code から直接実行不可。
ユーザーがターミナルで手動実行する必要がある。

## 予防

- 初回コミット時点で env var を使う（後から修正しない）
- `EMBEDDING_API_KEY = os.environ.get("EMBEDDING_API_KEY", "")` を最初から書く
