---
title: "PR チェーンの最終ブランチが main に届かない"
tags: [git, github, pr, stacked-pr]
severity: medium
source: personal
date: "2026-08-16"
---

## 症状

issue ブランチ間で PR を順番にマージした（#6→feat/issue-1, #7→feat/issue-2, …）が、
main には最初の PR しか反映されておらず、`git log main` が短いままだった。

## 原因

`gh pr create --base <前のブランチ>` でブランチ同士を繋いだため、
最終ブランチ (feat/issue-N) を main にマージする手順が抜けていた。
中間ブランチへのマージは成功しているが、main には到達していない。

## 解決策

最終ブランチを main に直接マージする:

```bash
git merge origin/<最終ブランチ> --no-ff -m "chore: 全実装を main にマージ"
git push origin main
```

## 予防

- PR チェーンを使う場合は、最後の PR のベースを必ず `main` にする
- 全マージ後に `git log main --oneline` で反映を確認する
- 関連: `stacked-pr-base-merge-wrong-target.md`（base 未確認でマージした別パターン）
