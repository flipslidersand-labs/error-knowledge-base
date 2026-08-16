---
title: "worktree で push 失敗 — リモートブランチに前セッションの別実装が存在"
tags: [git, worktree, rebase]
severity: medium
source: personal
date: "2026-07-15"
---

## 症状

```
! [rejected] feat/renovate -> feat/renovate (non-fast-forward)
```

リベース試行で add/add コンフリクト（両側が同じファイルを新規追加）。

## 原因

別セッションが同名ブランチ `feat/renovate` で異なる内容をすでに push 済み。
ローカルは `origin/main` から新規作成した同名ブランチだったため、リモートの履歴と分岐していた。

## 解決策

```bash
# リモートブランチの状態にリセット（ワーキングツリーは保持）
git reset --mixed origin/feat/renovate

# ワーキングツリーに残った正しいバージョンでコミット
git add <files>
git commit -m "fix: ..."

# 通常 push（fast-forward 可能になっている）
git push origin HEAD
```

## 予防

セッション開始時に `git ls-remote origin | grep <branch>` でリモートの同名ブランチ存在を確認する。
存在する場合は `git worktree add .claude/worktrees/<name> origin/<branch>` でリモートを追跡してから作業開始する。
