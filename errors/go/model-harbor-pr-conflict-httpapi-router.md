---
title: "model-harbor: feat/auth-middleware が httpapi パッケージ導入後にマージコンフリクト"
tags: [go, git, merge-conflict, model-harbor]
severity: medium
source: personal
date: "2026-08-08"
---

## 症状

PR #4 (`feat/auth-middleware` → `feat/phase1-proxy`) と PR #5 (`feat/chat-completions-auth-3` → `master`) が同一機能（Bearer 認証）を別アーキテクチャで実装。PR #5 を master にマージ後、PR #4 をリベースすると `cmd/modelharbor/main.go` でコンフリクト。

## 原因

- PR #4: `internal/router` に `BearerAuth()` を追加、`main.go` で `provider.NewOpenAI/Anthropic` + `router.New` を使用
- PR #5: `internal/httpapi` パッケージを新設、`main.go` を `serveCmd()` スタイルに全面刷新
- 両者が `main.go` の `runServe` / `serveCmd` 定義を競合

## 解決策

PR #5 の実装（httpapi パッケージ、fail-closed、カンマ区切り複数キー）が上位互換のため採用。PR #4 の `main.go` を PR #5 版に差し替えてリベース完了後、古い PR をクローズ。

```bash
git rebase origin/master  # conflict on main.go
# PR #5 の serveCmd() 版を取る
git add cmd/modelharbor/main.go
git rebase --continue
git push --force-with-lease origin feat/chat-completions-auth-3
gh pr merge 5 --squash --delete-branch
gh pr close 4 --comment "PR #5 でより完全な実装がマージされたためクローズ"
```

## 予防

- 同一リポジトリで複数セッションが同機能を実装しないよう Issue アサイン確認。
- スタック PR（feat/A → feat/B → master）は後続 PR が先に master 入りすると必ずコンフリクト。直接 master をベースにするか worktree で分離する。
