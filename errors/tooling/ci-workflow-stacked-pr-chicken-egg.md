---
title: "CI workflow が main 未マージ → stacked PR で CI がトリガーされない"
tags: [github-actions, stacked-pr, ci]
severity: medium
source: personal
date: "2026-07-16"
---

## 症状

PR#1（CI workflow 追加）→ PR#2（README）→ PR#3（テスト）のように stacked PR を作ると、
PR#2/#3 では CI チェックが一切実行されず "no checks" になる。

PR#1 の CI も fmt/clippy エラーが残ったまま failing になる。

## 原因

GitHub Actions は `.github/workflows/*.yml` が **default branch（main）** に存在する場合のみ
pull_request イベントでトリガーされる。

stacked PR#1 がマージされて初めて CI workflow が main に入る → それまで PR#2/#3 は CI 無し。

## 解決策

**全変更を1ブランチに集約して1つの PR にする。**

```bash
# stacked branchをrebaseして全コミットを1ブランチに持ってくる
git rebase origin/main
# 新ブランチ名で push（force push 代替）
git checkout -b feat/all-changes
git push origin feat/all-changes
gh pr create --base main --head feat/all-changes
```

squash merge 後に旧 PR（#1/#2/#3）を individually close する。

## 予防

CI workflow 自体を新規追加する際は必ずその branch に全変更を含めるか、
main に CI を先行マージしてから機能ブランチを作る。
stacked PR + CI 同時追加の組み合わせは避ける。
