---
title: "gh pr edit が Projects (classic) 警告で exit 1 になる"
tags: [go]
severity: medium
source: personal
---

# gh pr edit が Projects (classic) 警告で exit 1 になる

## 症状

```
gh pr edit 198 --repo ... --title "..." --body "..."
GraphQL: Projects (classic) is being deprecated in favor of the new Projects experience
exit: 1
```

タイトル・本文は実際には更新されていない（API呼び出し自体が失敗している）。

## 原因

`gh pr edit` が Projects (classic) フィールドを取得する GraphQL クエリを内部で投げており、
deprecation エラーが返ってくると exit 1 になる。

## 回避策

REST API を直接叩く:

```bash
gh api --method PATCH repos/<owner>/<repo>/pulls/<number> \
  --field title="..." \
  --field body="..." \
  --jq '.number,.title'
```

## 確認環境

- gh version: 2.x
- 発生リポ: flipslidersand-labs/mesh-drop
- 日付: 2026-08-16
